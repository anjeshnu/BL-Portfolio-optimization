"""
Portfolio Optimization

Functions for portfolio optimization including mean-variance,
risk parity, and various constraint formulations.
"""

from typing import Optional, Dict, Tuple
import pandas as pd
import numpy as np
import cvxpy as cp


def mean_variance_optimization(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_aversion: float = 1.0,
    constraints: Optional[Dict] = None
) -> pd.Series:
    """
    Mean-variance portfolio optimization.
    
    Maximizes: μ'w - (λ/2) w'Σw
    
    Parameters
    ----------
    expected_returns : pd.Series
        Expected returns for each asset
    cov_matrix : pd.DataFrame
        Covariance matrix
    risk_aversion : float, optional
        Risk aversion parameter (λ), by default 1.0
    constraints : Optional[Dict], optional
        Dictionary of constraints:
        - long_only: bool, default True
        - max_weight: float, default 1.0 (no individual limit)
        - min_weight: float, default 0.0
        - target_weights: Dict[str, float] or None
        - leverage: float, default 1.0
        
    Returns
    -------
    pd.Series
        Optimal portfolio weights
    """
    # Default constraints
    if constraints is None:
        constraints = {}
    
    long_only = constraints.get("long_only", True)
    max_weight = constraints.get("max_weight", 1.0)
    min_weight = constraints.get("min_weight", 0.0)
    leverage = constraints.get("leverage", 1.0)
    target_weights = constraints.get("target_weights", None)
    
    # Align data
    common_assets = expected_returns.index.intersection(cov_matrix.index)
    mu = expected_returns.loc[common_assets].values
    Sigma = cov_matrix.loc[common_assets, common_assets].values
    n = len(common_assets)
    
    # Define optimization variables
    w = cp.Variable(n)
    
    # Objective: maximize utility = returns - risk_aversion * variance
    returns = mu @ w
    risk = cp.quad_form(w, Sigma)
    objective = cp.Maximize(returns - (risk_aversion / 2) * risk)
    
    # Constraints
    constraints_list = []
    
    # Budget constraint
    constraints_list.append(cp.sum(w) == leverage)
    
    # Long-only
    if long_only:
        constraints_list.append(w >= 0)
    
    # Individual weight limits
    if max_weight < 1.0:
        constraints_list.append(w <= max_weight)
    
    if min_weight > 0:
        constraints_list.append(w >= min_weight)
    
    # Target weight constraints
    if target_weights is not None:
        for asset, target in target_weights.items():
            if asset in common_assets:
                idx = list(common_assets).index(asset)
                constraints_list.append(w[idx] == target)
    
    # Solve
    problem = cp.Problem(objective, constraints_list)
    problem.solve()
    
    if problem.status not in ["optimal", "optimal_inaccurate"]:
        raise ValueError(f"Optimization failed: {problem.status}")
    
    weights = pd.Series(w.value, index=common_assets)
    return weights


def minimum_variance_portfolio(
    cov_matrix: pd.DataFrame,
    constraints: Optional[Dict] = None
) -> pd.Series:
    """
    Minimum variance portfolio optimization.
    
    Minimizes: w'Σw
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix
    constraints : Optional[Dict], optional
        Same as mean_variance_optimization, by default None
        
    Returns
    -------
    pd.Series
        Minimum variance portfolio weights
    """
    if constraints is None:
        constraints = {}
    
    long_only = constraints.get("long_only", True)
    max_weight = constraints.get("max_weight", 1.0)
    leverage = constraints.get("leverage", 1.0)
    
    n = len(cov_matrix)
    Sigma = cov_matrix.values
    
    # Define optimization variables
    w = cp.Variable(n)
    
    # Objective: minimize variance
    risk = cp.quad_form(w, Sigma)
    objective = cp.Minimize(risk)
    
    # Constraints
    constraints_list = [cp.sum(w) == leverage]
    
    if long_only:
        constraints_list.append(w >= 0)
    
    if max_weight < 1.0:
        constraints_list.append(w <= max_weight)
    
    # Solve
    problem = cp.Problem(objective, constraints_list)
    problem.solve()
    
    if problem.status not in ["optimal", "optimal_inaccurate"]:
        raise ValueError(f"Optimization failed: {problem.status}")
    
    weights = pd.Series(w.value, index=cov_matrix.index)
    return weights


def risk_parity_portfolio(
    cov_matrix: pd.DataFrame,
    target_risk_contributions: Optional[pd.Series] = None
) -> pd.Series:
    """
    Risk parity portfolio optimization.
    
    Allocates capital such that each asset contributes equally to portfolio risk.
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix
    target_risk_contributions : Optional[pd.Series], optional
        Target risk contribution for each asset (should sum to 1),
        by default None (equal risk contribution)
        
    Returns
    -------
    pd.Series
        Risk parity portfolio weights
    """
    n = len(cov_matrix)
    Sigma = cov_matrix.values
    
    if target_risk_contributions is None:
        # Equal risk contribution
        target_rc = np.ones(n) / n
    else:
        target_rc = target_risk_contributions.values
    
    # Use iterative algorithm for risk parity
    # Start with equal weights
    w = np.ones(n) / n
    
    for _ in range(100):  # Max iterations
        # Portfolio volatility
        portfolio_var = w @ Sigma @ w
        portfolio_vol = np.sqrt(portfolio_var)
        
        # Marginal risk contribution
        mrc = (Sigma @ w) / portfolio_vol
        
        # Risk contribution
        rc = w * mrc
        
        # Update weights
        # w_new = w * (target_rc / rc)
        w_new = w * np.sqrt(target_rc / (rc + 1e-10))
        w_new = w_new / w_new.sum()  # Normalize
        
        # Check convergence
        if np.max(np.abs(w_new - w)) < 1e-6:
            break
        
        w = w_new
    
    weights = pd.Series(w, index=cov_matrix.index)
    return weights


def max_sharpe_ratio(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0,
    constraints: Optional[Dict] = None
) -> pd.Series:
    """
    Maximum Sharpe ratio portfolio.
    
    Maximizes: (μ - rf) / σ
    
    Parameters
    ----------
    expected_returns : pd.Series
        Expected returns
    cov_matrix : pd.DataFrame
        Covariance matrix
    risk_free_rate : float, optional
        Risk-free rate, by default 0.0
    constraints : Optional[Dict], optional
        Constraints dictionary, by default None
        
    Returns
    -------
    pd.Series
        Maximum Sharpe ratio portfolio weights
    """
    if constraints is None:
        constraints = {}
    
    long_only = constraints.get("long_only", True)
    max_weight = constraints.get("max_weight", 1.0)
    
    # Align data
    common_assets = expected_returns.index.intersection(cov_matrix.index)
    mu = expected_returns.loc[common_assets].values - risk_free_rate
    Sigma = cov_matrix.loc[common_assets, common_assets].values
    n = len(common_assets)
    
    # Reformulate as convex problem
    # Maximize: (μ'y) subject to: y'Σy ≤ 1, sum(y) = κ
    # Then w = y / κ
    
    y = cp.Variable(n)
    kappa = cp.Variable()
    
    # Objective
    objective = cp.Maximize(mu @ y)
    
    # Constraints
    constraints_list = [
        cp.quad_form(y, Sigma) <= 1,
        cp.sum(y) == kappa
    ]
    
    if long_only:
        constraints_list.append(y >= 0)
    
    # Solve
    problem = cp.Problem(objective, constraints_list)
    problem.solve()
    
    if problem.status not in ["optimal", "optimal_inaccurate"]:
        raise ValueError(f"Optimization failed: {problem.status}")
    
    # Convert to weights
    w = y.value / kappa.value
    
    # Apply max weight constraint if needed
    if max_weight < 1.0:
        w = np.clip(w, 0, max_weight)
        w = w / w.sum()
    
    weights = pd.Series(w, index=common_assets)
    return weights


def efficient_frontier(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    n_points: int = 50,
    constraints: Optional[Dict] = None
) -> Tuple[np.ndarray, np.ndarray, list]:
    """
    Compute the efficient frontier.
    
    Parameters
    ----------
    expected_returns : pd.Series
        Expected returns
    cov_matrix : pd.DataFrame
        Covariance matrix
    n_points : int, optional
        Number of points on the frontier, by default 50
    constraints : Optional[Dict], optional
        Constraints dictionary, by default None
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray, list]
        - Array of returns
        - Array of volatilities
        - List of weight vectors
    """
    # Get minimum and maximum return portfolios
    min_var_weights = minimum_variance_portfolio(cov_matrix, constraints)
    min_return = expected_returns @ min_var_weights
    
    # Maximum return (all in highest return asset if long-only)
    if constraints is None or constraints.get("long_only", True):
        max_return = expected_returns.max()
    else:
        # If short-selling allowed, use max Sharpe
        max_sr_weights = max_sharpe_ratio(expected_returns, cov_matrix, 0.0, constraints)
        max_return = expected_returns @ max_sr_weights
    
    # Target returns
    target_returns = np.linspace(min_return, max_return, n_points)
    
    # Optimize for each target
    returns_list = []
    vols_list = []
    weights_list = []
    
    for target in target_returns:
        try:
            # Add target return constraint
            if constraints is None:
                cons = {}
            else:
                cons = constraints.copy()
            
            # Optimize for minimum variance given target return
            common_assets = expected_returns.index.intersection(cov_matrix.index)
            n = len(common_assets)
            Sigma = cov_matrix.loc[common_assets, common_assets].values
            mu = expected_returns.loc[common_assets].values
            
            w = cp.Variable(n)
            risk = cp.quad_form(w, Sigma)
            objective = cp.Minimize(risk)
            
            constraints_list = [
                cp.sum(w) == 1,
                mu @ w == target
            ]
            
            if cons.get("long_only", True):
                constraints_list.append(w >= 0)
            
            problem = cp.Problem(objective, constraints_list)
            problem.solve()
            
            if problem.status in ["optimal", "optimal_inaccurate"]:
                weights = w.value
                ret = mu @ weights
                vol = np.sqrt(weights @ Sigma @ weights)
                
                returns_list.append(ret)
                vols_list.append(vol)
                weights_list.append(pd.Series(weights, index=common_assets))
        
        except:
            continue
    
    return np.array(returns_list), np.array(vols_list), weights_list


def portfolio_statistics(
    weights: pd.Series,
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0
) -> Dict:
    """
    Calculate portfolio statistics.
    
    Parameters
    ----------
    weights : pd.Series
        Portfolio weights
    expected_returns : pd.Series
        Expected returns
    cov_matrix : pd.DataFrame
        Covariance matrix
    risk_free_rate : float, optional
        Risk-free rate, by default 0.0
        
    Returns
    -------
    Dict
        Dictionary of portfolio statistics
    """
    # Align data
    common_assets = weights.index.intersection(expected_returns.index).intersection(cov_matrix.index)
    w = weights.loc[common_assets].values
    mu = expected_returns.loc[common_assets].values
    Sigma = cov_matrix.loc[common_assets, common_assets].values
    
    # Calculate statistics
    portfolio_return = w @ mu
    portfolio_variance = w @ Sigma @ w
    portfolio_vol = np.sqrt(portfolio_variance)
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
    
    # Annualize (assuming monthly data)
    annual_return = portfolio_return * 12
    annual_vol = portfolio_vol * np.sqrt(12)
    annual_sharpe = sharpe_ratio * np.sqrt(12)
    
    stats = {
        "return": portfolio_return,
        "volatility": portfolio_vol,
        "sharpe_ratio": sharpe_ratio,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "annual_sharpe": annual_sharpe,
        "weights_sum": weights.sum(),
        "n_positions": (weights.abs() > 1e-4).sum(),
    }
    
    return stats
