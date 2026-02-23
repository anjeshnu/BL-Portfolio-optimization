"""
Data Loading Utilities

Functions for loading and preprocessing ETF prices, factor data,
risk-free rates, and Capital Market Assumptions.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np


class DataConfig:
    """Configuration for data file paths and asset universe."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.file_etf = self.data_dir / "Raw_data_ETFs.xlsx"
        self.file_rates = self.data_dir / "Rates.xlsx"
        self.file_ff = self.data_dir / "Factor_Data.xlsx"
        self.file_cma = self.data_dir / "blackrock-capital-market-assumptions.xlsx"
        
        # Asset universe
        self.assets = [
            "SPY",   # US Large Cap
            "VGK",   # European Stocks
            "VWO",   # Emerging Markets
            "IEF",   # US 7-10Y Treasuries
            "TLT",   # US 20+ Year Treasuries
            "LQD",   # Investment Grade Corporate Bonds
            "HYG",   # High Yield Corporate Bonds
            "TIP",   # TIPS
            "DBC",   # Commodities
        ]


def clean_ffill_series(s: pd.Series) -> pd.Series:
    """
    Convert 0/invalid values to NaN, then forward-fill.
    
    Parameters
    ----------
    s : pd.Series
        Input series to clean
        
    Returns
    -------
    pd.Series
        Cleaned and forward-filled series
    """
    s = pd.to_numeric(s, errors="coerce")
    s = s.replace(0, np.nan)
    return s.ffill()


def reindex_business_days(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reindex DataFrame to business-day calendar and forward-fill.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with datetime index
        
    Returns
    -------
    pd.DataFrame
        Reindexed DataFrame with business days
    """
    idx = pd.bdate_range(df.index.min(), df.index.max())
    return df.reindex(idx).ffill()


def load_yahoo_sheet_as_close(excel_path: Path, sheet_name: str) -> pd.Series:
    """
    Load Yahoo Finance style Excel sheet and extract adjusted close prices.
    
    Parameters
    ----------
    excel_path : Path
        Path to Excel file
    sheet_name : str
        Name of the sheet to load
        
    Returns
    -------
    pd.Series
        Time series of adjusted close prices
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    # Find date column
    date_col = None
    for col in df.columns:
        if "date" in str(col).lower():
            date_col = col
            break
    if date_col is None:
        date_col = df.columns[0]
    
    # Set datetime index
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    
    # Extract Adj Close
    if "Adj Close" in df.columns:
        series = df["Adj Close"]
    elif "Close" in df.columns:
        series = df["Close"]
    else:
        raise ValueError(f"No Close price column in {sheet_name}")
    
    return clean_ffill_series(series)


def eom_prices(daily_px: pd.DataFrame) -> pd.DataFrame:
    """
    Convert daily prices to end-of-month prices.
    
    Parameters
    ----------
    daily_px : pd.DataFrame
        DataFrame of daily prices
        
    Returns
    -------
    pd.DataFrame
        End-of-month prices
    """
    return daily_px.resample("ME").last()


def monthly_returns(px_m: pd.DataFrame, kind: str = "log") -> pd.DataFrame:
    """
    Calculate monthly returns from monthly prices.
    
    Parameters
    ----------
    px_m : pd.DataFrame
        Monthly prices
    kind : str, optional
        Return type: "log" or "simple", by default "log"
        
    Returns
    -------
    pd.DataFrame
        Monthly returns
    """
    if kind == "log":
        return np.log(px_m).diff().dropna()
    else:
        return px_m.pct_change().dropna()


def load_etf_prices(config: DataConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load ETF prices from Excel sheets and compute monthly returns.
    
    Parameters
    ----------
    config : DataConfig
        Data configuration object
        
    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        Monthly prices and monthly returns
    """
    xls = pd.ExcelFile(config.file_etf)
    
    px = {}
    for ticker in config.assets:
        sheet_name = f"{ticker}"
        if sheet_name not in xls.sheet_names:
            raise ValueError(f"Missing sheet {sheet_name} in {config.file_etf.name}")
        px[ticker] = load_yahoo_sheet_as_close(config.file_etf, sheet_name)
    
    # Combine into DataFrame
    px_df = pd.concat(px, axis=1)
    px_df.columns = px_df.columns.get_level_values(0)
    
    # Reindex to business days and forward-fill
    px_df = reindex_business_days(px_df)
    
    # Convert to monthly
    px_monthly = eom_prices(px_df)
    ret_monthly = monthly_returns(px_monthly, kind="log")
    
    return px_monthly, ret_monthly


def load_risk_free_rate(config: DataConfig) -> pd.Series:
    """
    Load risk-free rate data and convert to monthly.
    
    Parameters
    ----------
    config : DataConfig
        Data configuration object
        
    Returns
    -------
    pd.Series
        Monthly risk-free rate returns
    """
    df = pd.read_excel(config.file_rates, sheet_name="US-3M")
    
    # Set datetime index
    date_col = None
    for col in df.columns:
        if "date" in str(col).lower():
            date_col = col
            break
    if date_col is None:
        date_col = df.columns[0]
    
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    
    # Get yield column (in percent)
    rf_daily = df.iloc[:, 0] / 100  # Convert to decimal
    
    # Convert to monthly
    rf_monthly = rf_daily.resample("ME").last()
    rf_monthly = rf_monthly / 12  # Convert annual to monthly
    
    return rf_monthly


def load_ff_factors(config: DataConfig) -> Dict[str, pd.DataFrame]:
    """
    Load Fama-French factor data from Excel file.
    
    Parameters
    ----------
    config : DataConfig
        Data configuration object
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary containing factor DataFrames
    """
    def load_ff_sheet(sheet_name: str) -> pd.DataFrame:
        df = pd.read_excel(config.file_ff, sheet_name=sheet_name)
        
        # Build datetime index from yyyymm
        df["Date"] = pd.to_datetime(
            df["yyyymm"].astype(int).astype(str), 
            format="%Y%m"
        ) + pd.offsets.MonthEnd(0)
        df = df.set_index("Date").sort_index()
        
        # Keep only factor columns (convert from percent to decimal)
        factor_cols = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "MOM", "RF"]
        available_cols = [c for c in factor_cols if c in df.columns]
        
        df = df[available_cols] / 100  # Convert to decimal
        return df
    
    factors = {
        "FF5": load_ff_sheet("FF5"),
        "MOM": load_ff_sheet("MOM") if "MOM" in pd.ExcelFile(config.file_ff).sheet_names else None,
    }
    
    return factors


def load_cma_priors(config: DataConfig) -> pd.Series:
    """
    Load BlackRock Capital Market Assumptions as prior expected returns.
    
    Parameters
    ----------
    config : DataConfig
        Data configuration object
        
    Returns
    -------
    pd.Series
        Prior expected returns for each asset (annualized)
    """
    df = pd.read_excel(config.file_cma, sheet_name="CMA")
    
    # Mapping from assets to CMA labels
    asset_to_cma = {
        "SPY": "US Large Cap",
        "VGK": "European Equities",
        "VWO": "EM Equities",
        "IEF": "US Govt 7-10Y",
        "TLT": "US Govt 20+Y",
        "LQD": "US IG Corporate",
        "HYG": "US High Yield",
        "TIP": "US TIPS",
        "DBC": "Commodities",
    }
    
    priors = {}
    for asset, cma_label in asset_to_cma.items():
        # Find row matching CMA label
        row = df[df["Asset Class"] == cma_label]
        if len(row) > 0:
            # Expected return in percent, convert to decimal
            priors[asset] = row["Expected Return (%)"].values[0] / 100
        else:
            # Default if not found
            priors[asset] = 0.05
    
    return pd.Series(priors)


def load_all_data(data_dir: str = "./data") -> Dict[str, pd.DataFrame]:
    """
    Load all data required for Black-Litterman analysis.
    
    Parameters
    ----------
    data_dir : str, optional
        Path to data directory, by default "./data"
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary containing all loaded data:
        - prices_monthly: Monthly ETF prices
        - returns_monthly: Monthly ETF returns
        - rf_monthly: Monthly risk-free rate
        - ff_factors: Fama-French factors
        - cma_priors: CMA prior expected returns
    """
    config = DataConfig(data_dir)
    
    # Load prices and returns
    prices_monthly, returns_monthly = load_etf_prices(config)
    
    # Load risk-free rate
    rf_monthly = load_risk_free_rate(config)
    
    # Load factors
    ff_factors = load_ff_factors(config)
    
    # Load CMA priors
    cma_priors = load_cma_priors(config)
    
    # Compute excess returns
    # Align dates
    common_dates = returns_monthly.index.intersection(rf_monthly.index)
    excess_returns = returns_monthly.loc[common_dates].sub(
        rf_monthly.loc[common_dates], axis=0
    )
    
    return {
        "prices_monthly": prices_monthly,
        "returns_monthly": returns_monthly,
        "excess_returns": excess_returns,
        "rf_monthly": rf_monthly,
        "ff_factors": ff_factors,
        "cma_priors": cma_priors,
        "config": config,
    }
