"""
Factor Model Construction

Functions for building factor exposures, custom factors,
and factor-based covariance matrices.
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
import statsmodels.api as sm


def estimate_factor_exposures(
    excess_returns: pd.DataFrame,
    factors: pd.DataFrame,
    min_periods: int = 36
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Estimate factor exposures via time-series regression.
    
    For each asset, run regression:
        R_i,t - R_f,t = alpha_i + beta_i' * F_t + epsilon_i,t
    
    Parameters
    ----------
    excess_returns : pd.DataFrame
        Asset excess returns (assets × time)
    factors : pd.DataFrame
        Factor returns (factors × time)
    min_periods : int, optional
        Minimum periods required for regression, by default 36
        
    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        - betas: Factor exposures (assets × factors)
        - alphas: Regression alphas (assets)
        - residuals: Regression residuals (assets × time)
    """
    # Align dates
    common_dates = excess_returns.index.intersection(factors.index)
    y = excess_returns.loc[common_dates]
    X = factors.loc[common_dates]
    
    if len(common_dates) < min_periods:
        raise ValueError(f"Insufficient data: {len(common_dates)} < {min_periods}")
    
    # Add constant for alpha
    X_with_const = sm.add_constant(X)
    
    betas = pd.DataFrame(index=y.columns, columns=X.columns)
    alphas = pd.Series(index=y.columns, dtype=float)
    residuals = pd.DataFrame(index=y.index, columns=y.columns)
    
    for asset in y.columns:
        # Run OLS regression
        model = sm.OLS(y[asset].dropna(), X_with_const.loc[y[asset].dropna().index])
        results = model.fit()
        
        # Store results
        alphas[asset] = results.params["const"]
        betas.loc[asset] = results.params.drop("const").values
        
        # Store residuals
        residuals[asset] = results.resid
    
    betas = betas.astype(float)
    residuals = residuals.astype(float)
    
    return betas, alphas, residuals


def build_term_factor(
    bond_returns: pd.DataFrame,
    short_bond: str = "IEF",
    long_bond: str = "TLT"
) -> pd.Series:
    """
    Build term structure factor (duration exposure).
    
    Term Factor = Long Treasury - Short Treasury
    
    Parameters
    ----------
    bond_returns : pd.DataFrame
        Bond ETF returns
    short_bond : str, optional
        Short duration bond ticker, by default "IEF"
    long_bond : str, optional
        Long duration bond ticker, by default "TLT"
        
    Returns
    -------
    pd.Series
        Term factor returns
    """
    if short_bond not in bond_returns.columns or long_bond not in bond_returns.columns:
        raise ValueError(f"Missing bonds: need {short_bond} and {long_bond}")
    
    term_factor = bond_returns[long_bond] - bond_returns[short_bond]
    term_factor.name = "TERM"
    
    return term_factor


def build_credit_factor(
    bond_returns: pd.DataFrame,
    high_yield: str = "HYG",
    investment_grade: str = "LQD"
) -> pd.Series:
    """
    Build credit spread factor.
    
    Credit Factor = High Yield - Investment Grade
    
    Parameters
    ----------
    bond_returns : pd.DataFrame
        Bond ETF returns
    high_yield : str, optional
        High yield bond ticker, by default "HYG"
    investment_grade : str, optional
        Investment grade bond ticker, by default "LQD"
        
    Returns
    -------
    pd.Series
        Credit factor returns
    """
    if high_yield not in bond_returns.columns or investment_grade not in bond_returns.columns:
        raise ValueError(f"Missing bonds: need {high_yield} and {investment_grade}")
    
    credit_factor = bond_returns[high_yield] - bond_returns[investment_grade]
    credit_factor.name = "CREDIT"
    
    return credit_factor


def build_commodity_factor(
    commodity_returns: pd.DataFrame,
    commodity_ticker: str = "DBC"
) -> pd.Series:
    """
    Build commodity factor.
    
    Parameters
    ----------
    commodity_returns : pd.DataFrame
        Commodity ETF returns
    commodity_ticker : str, optional
        Commodity ETF ticker, by default "DBC"
        
    Returns
    -------
    pd.Series
        Commodity factor returns
    """
    if commodity_ticker not in commodity_returns.columns:
        raise ValueError(f"Missing commodity: need {commodity_ticker}")
    
    commodity_factor = commodity_returns[commodity_ticker].copy()
    commodity_factor.name = "COMMODITY"
    
    return commodity_factor


def build_custom_factors(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Build all custom factors (Term, Credit, Commodity).
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns
        
    Returns
    -------
    pd.DataFrame
        Custom factors
    """
    factors = {}
    
    # Term factor
    try:
        factors["TERM"] = build_term_factor(returns)
    except ValueError as e:
        print(f"Warning: Could not build TERM factor: {e}")
    
    # Credit factor
    try:
        factors["CREDIT"] = build_credit_factor(returns)
    except ValueError as e:
        print(f"Warning: Could not build CREDIT factor: {e}")
    
    # Commodity factor
    try:
        factors["COMMODITY"] = build_commodity_factor(returns)
    except ValueError as e:
        print(f"Warning: Could not build COMMODITY factor: {e}")
    
    return pd.DataFrame(factors)


def combine_factors(
    ff_factors: pd.DataFrame,
    custom_factors: pd.DataFrame
) -> pd.DataFrame:
    """
    Combine Fama-French and custom factors.
    
    Parameters
    ----------
    ff_factors : pd.DataFrame
        Fama-French factors
    custom_factors : pd.DataFrame
        Custom factors
        
    Returns
    -------
    pd.DataFrame
        Combined factor set
    """
    # Align dates
    common_dates = ff_factors.index.intersection(custom_factors.index)
    
    all_factors = pd.concat([
        ff_factors.loc[common_dates],
        custom_factors.loc[common_dates]
    ], axis=1)
    
    return all_factors


def build_factor_covariance(
    betas: pd.DataFrame,
    factor_returns: pd.DataFrame,
    residuals: pd.DataFrame
) -> pd.DataFrame:
    """
    Build factor model covariance matrix.
    
    Σ = B * F * B' + D
    
    Where:
    - B: Factor exposures (betas)
    - F: Factor covariance matrix
    - D: Diagonal matrix of idiosyncratic variances
    
    Parameters
    ----------
    betas : pd.DataFrame
        Factor exposures (assets × factors)
    factor_returns : pd.DataFrame
        Factor returns (time × factors)
    residuals : pd.DataFrame
        Regression residuals (time × assets)
        
    Returns
    -------
    pd.DataFrame
        Covariance matrix (assets × assets)
    """
    # Factor covariance matrix
    F = factor_returns.cov()
    
    # Align betas with factor covariance
    common_factors = betas.columns.intersection(F.index)
    B = betas[common_factors]
    F_aligned = F.loc[common_factors, common_factors]
    
    # Systematic covariance: B * F * B'
    systematic_cov = B @ F_aligned @ B.T
    
    # Idiosyncratic variance (diagonal)
    idio_var = residuals.var()
    D = np.diag(idio_var)
    
    # Total covariance
    total_cov = systematic_cov + D
    
    return pd.DataFrame(
        total_cov,
        index=betas.index,
        columns=betas.index
    )


def factor_model_analysis(
    excess_returns: pd.DataFrame,
    ff_factors: pd.DataFrame,
    custom_factors: pd.DataFrame = None,
    min_periods: int = 36
) -> Dict:
    """
    Complete factor model analysis.
    
    Parameters
    ----------
    excess_returns : pd.DataFrame
        Asset excess returns
    ff_factors : pd.DataFrame
        Fama-French factors
    custom_factors : pd.DataFrame, optional
        Custom factors, by default None
    min_periods : int, optional
        Minimum periods for regression, by default 36
        
    Returns
    -------
    Dict
        Dictionary containing:
        - betas: Factor exposures
        - alphas: Regression alphas
        - residuals: Residuals
        - factor_cov: Factor covariance matrix
        - cov_matrix: Asset covariance matrix
        - r_squared: R-squared values
    """
    # Combine factors
    if custom_factors is not None:
        all_factors = combine_factors(ff_factors, custom_factors)
    else:
        all_factors = ff_factors
    
    # Estimate exposures
    betas, alphas, residuals = estimate_factor_exposures(
        excess_returns, all_factors, min_periods
    )
    
    # Build covariance matrix
    cov_matrix = build_factor_covariance(betas, all_factors, residuals)
    
    # Calculate R-squared
    common_dates = excess_returns.index.intersection(all_factors.index)
    y = excess_returns.loc[common_dates]
    
    r_squared = {}
    for asset in y.columns:
        ss_tot = ((y[asset] - y[asset].mean()) ** 2).sum()
        ss_res = (residuals[asset].dropna() ** 2).sum()
        r_squared[asset] = 1 - (ss_res / ss_tot)
    
    r_squared = pd.Series(r_squared)
    
    return {
        "betas": betas,
        "alphas": alphas,
        "residuals": residuals,
        "factors": all_factors,
        "factor_cov": all_factors.cov(),
        "cov_matrix": cov_matrix,
        "r_squared": r_squared,
    }
