"""
Covariance Estimation

Functions for robust covariance matrix estimation including
Ledoit-Wolf shrinkage and factor-based approaches.
"""

from typing import Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.covariance import LedoitWolf


def sample_covariance(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Compute sample covariance matrix.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (time × assets)
        
    Returns
    -------
    pd.DataFrame
        Sample covariance matrix (assets × assets)
    """
    return returns.cov()


def ledoit_wolf_shrinkage(returns: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
    """
    Compute Ledoit-Wolf shrinkage covariance estimator.
    
    This method shrinks the sample covariance towards a structured
    target (constant correlation model) to reduce estimation error.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (time × assets)
        
    Returns
    -------
    Tuple[pd.DataFrame, float]
        - Shrinkage covariance matrix (assets × assets)
        - Shrinkage intensity (0-1)
    """
    # Remove any NaN values
    clean_returns = returns.dropna()
    
    if len(clean_returns) < 2:
        raise ValueError("Insufficient data for covariance estimation")
    
    # Fit Ledoit-Wolf estimator
    lw = LedoitWolf()
    lw.fit(clean_returns)
    
    # Get shrinkage covariance and shrinkage intensity
    cov_shrunk = lw.covariance_
    shrinkage = lw.shrinkage_
    
    # Convert to DataFrame
    cov_df = pd.DataFrame(
        cov_shrunk,
        index=returns.columns,
        columns=returns.columns
    )
    
    return cov_df, shrinkage


def exponentially_weighted_covariance(
    returns: pd.DataFrame,
    halflife: int = 60
) -> pd.DataFrame:
    """
    Compute exponentially weighted covariance matrix.
    
    More recent observations receive higher weight, useful for
    capturing time-varying volatility and correlations.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (time × assets)
    halflife : int, optional
        Halflife for exponential weighting in periods, by default 60
        
    Returns
    -------
    pd.DataFrame
        Exponentially weighted covariance matrix (assets × assets)
    """
    clean_returns = returns.dropna()
    
    if len(clean_returns) < 2:
        raise ValueError("Insufficient data for covariance estimation")
    
    # Compute EWMA covariance
    cov_ew = clean_returns.ewm(halflife=halflife).cov()
    
    # Extract the last (most recent) covariance matrix
    last_date = cov_ew.index.get_level_values(0)[-1]
    cov_matrix = cov_ew.loc[last_date]
    
    return cov_matrix


def correlation_matrix(cov_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Convert covariance matrix to correlation matrix.
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix (assets × assets)
        
    Returns
    -------
    pd.DataFrame
        Correlation matrix (assets × assets)
    """
    # Extract standard deviations
    std = np.sqrt(np.diag(cov_matrix))
    
    # Compute correlation
    corr = cov_matrix / np.outer(std, std)
    
    return pd.DataFrame(
        corr,
        index=cov_matrix.index,
        columns=cov_matrix.columns
    )


def volatility_vector(cov_matrix: pd.DataFrame, annualize: bool = True) -> pd.Series:
    """
    Extract volatility (standard deviation) from covariance matrix.
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix (assets × assets)
    annualize : bool, optional
        Whether to annualize volatilities (assumes monthly data), by default True
        
    Returns
    -------
    pd.Series
        Asset volatilities
    """
    vol = np.sqrt(np.diag(cov_matrix))
    
    if annualize:
        vol = vol * np.sqrt(12)  # Assuming monthly data
    
    return pd.Series(vol, index=cov_matrix.index)


def nearest_psd(cov_matrix: pd.DataFrame, epsilon: float = 1e-8) -> pd.DataFrame:
    """
    Find the nearest positive semi-definite matrix.
    
    Useful for ensuring numerical stability when a covariance matrix
    is not positive definite due to numerical errors.
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Input covariance matrix
    epsilon : float, optional
        Small positive value to add to eigenvalues, by default 1e-8
        
    Returns
    -------
    pd.DataFrame
        Nearest PSD matrix
    """
    # Eigenvalue decomposition
    eigvals, eigvecs = np.linalg.eigh(cov_matrix.values)
    
    # Set negative eigenvalues to small positive value
    eigvals[eigvals < epsilon] = epsilon
    
    # Reconstruct matrix
    psd_matrix = eigvecs @ np.diag(eigvals) @ eigvecs.T
    
    return pd.DataFrame(
        psd_matrix,
        index=cov_matrix.index,
        columns=cov_matrix.columns
    )


def robust_covariance(
    returns: pd.DataFrame,
    method: str = "ledoit_wolf",
    **kwargs
) -> pd.DataFrame:
    """
    Compute robust covariance estimate using specified method.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (time × assets)
    method : str, optional
        Estimation method: "sample", "ledoit_wolf", or "ewma", by default "ledoit_wolf"
    **kwargs
        Additional arguments for the chosen method
        
    Returns
    -------
    pd.DataFrame
        Covariance matrix (assets × assets)
        
    Raises
    ------
    ValueError
        If method is not recognized
    """
    if method == "sample":
        return sample_covariance(returns)
    
    elif method == "ledoit_wolf":
        cov, _ = ledoit_wolf_shrinkage(returns)
        return cov
    
    elif method == "ewma":
        halflife = kwargs.get("halflife", 60)
        return exponentially_weighted_covariance(returns, halflife)
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'sample', 'ledoit_wolf', or 'ewma'.")


def compare_covariance_methods(
    returns: pd.DataFrame
) -> dict:
    """
    Compare different covariance estimation methods.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns (time × assets)
        
    Returns
    -------
    dict
        Dictionary containing covariance matrices from different methods
    """
    results = {
        "sample": sample_covariance(returns),
        "ledoit_wolf": ledoit_wolf_shrinkage(returns)[0],
        "ewma_30": exponentially_weighted_covariance(returns, halflife=30),
        "ewma_60": exponentially_weighted_covariance(returns, halflife=60),
    }
    
    # Add summary statistics
    for method, cov in results.items():
        print(f"\n{method.upper()}:")
        print(f"  Condition number: {np.linalg.cond(cov):.2f}")
        print(f"  Min eigenvalue: {np.linalg.eigvals(cov).min():.6f}")
        print(f"  Avg volatility: {volatility_vector(cov, annualize=True).mean():.2%}")
    
    return results


def covariance_diagnostics(cov_matrix: pd.DataFrame) -> dict:
    """
    Compute diagnostic statistics for a covariance matrix.
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix (assets × assets)
        
    Returns
    -------
    dict
        Dictionary of diagnostic statistics
    """
    eigvals = np.linalg.eigvals(cov_matrix.values)
    
    diagnostics = {
        "min_eigenvalue": eigvals.min(),
        "max_eigenvalue": eigvals.max(),
        "condition_number": np.linalg.cond(cov_matrix),
        "is_positive_definite": (eigvals > 0).all(),
        "trace": np.trace(cov_matrix),
        "determinant": np.linalg.det(cov_matrix),
        "avg_volatility": volatility_vector(cov_matrix, annualize=True).mean(),
        "avg_correlation": correlation_matrix(cov_matrix).values[np.triu_indices_from(cov_matrix, k=1)].mean(),
    }
    
    return diagnostics


def annualize_covariance(cov_matrix: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
    """
    Annualize a covariance matrix.
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix (assets × assets)
    periods : int, optional
        Number of periods per year, by default 12 (for monthly data)
        
    Returns
    -------
    pd.DataFrame
        Annualized covariance matrix
    """
    return cov_matrix * periods
