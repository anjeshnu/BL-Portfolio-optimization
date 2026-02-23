"""
Black-Litterman Model Implementation

Functions for computing posterior expected returns using the
Black-Litterman model, incorporating market equilibrium and views.
"""

from typing import Optional, Dict, Tuple
import pandas as pd
import numpy as np


class BlackLittermanModel:
    """
    Black-Litterman portfolio optimization model.
    
    Combines market equilibrium (prior) with investor views to produce
    posterior expected returns that can be used in mean-variance optimization.
    """
    
    def __init__(
        self,
        prior_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_aversion: float = 2.5,
        tau: float = 0.025
    ):
        """
        Initialize Black-Litterman model.
        
        Parameters
        ----------
        prior_returns : pd.Series
            Prior (equilibrium) expected returns
        cov_matrix : pd.DataFrame
            Covariance matrix of returns
        risk_aversion : float, optional
            Market risk aversion coefficient (δ), by default 2.5
        tau : float, optional
            Uncertainty in prior (typically 0.01-0.05), by default 0.025
        """
        self.prior_returns = prior_returns
        self.cov_matrix = cov_matrix
        self.risk_aversion = risk_aversion
        self.tau = tau
        
        # Ensure alignment
        common_assets = prior_returns.index.intersection(cov_matrix.index)
        self.prior_returns = prior_returns.loc[common_assets]
        self.cov_matrix = cov_matrix.loc[common_assets, common_assets]
        
        self.views = None
        self.view_confidences = None
        self.posterior_returns = None
        self.posterior_cov = None
    
    def add_absolute_views(
        self,
        views: Dict[str, float],
        confidences: Optional[Dict[str, float]] = None
    ):
        """
        Add absolute views on asset returns.
        
        Absolute view: Asset A will return X%
        
        Parameters
        ----------
        views : Dict[str, float]
            Dictionary mapping asset names to expected returns
        confidences : Optional[Dict[str, float]], optional
            Dictionary mapping asset names to confidence levels (0-1),
            by default None (uses equal confidence for all views)
        """
        n_assets = len(self.prior_returns)
        n_views = len(views)
        
        # Pick matrix P: maps views to assets
        P = np.zeros((n_views, n_assets))
        q = np.zeros(n_views)
        
        for i, (asset, view_return) in enumerate(views.items()):
            if asset not in self.prior_returns.index:
                raise ValueError(f"Asset {asset} not in universe")
            
            asset_idx = self.prior_returns.index.get_loc(asset)
            P[i, asset_idx] = 1.0
            q[i] = view_return
        
        # Omega matrix: uncertainty in views
        if confidences is None:
            # Default: equal confidence
            confidences = {asset: 0.5 for asset in views.keys()}
        
        omega_diag = []
        for i, asset in enumerate(views.keys()):
            conf = confidences[asset]
            # Convert confidence to variance
            # Higher confidence → lower variance
            variance = self.tau * P[i] @ self.cov_matrix.values @ P[i].T / conf
            omega_diag.append(variance)
        
        Omega = np.diag(omega_diag)
        
        self.views = {"P": P, "q": q, "Omega": Omega}
        return self
    
    def add_relative_views(
        self,
        views: Dict[Tuple[str, str], float],
        confidences: Optional[Dict[Tuple[str, str], float]] = None
    ):
        """
        Add relative views between pairs of assets.
        
        Relative view: Asset A will outperform Asset B by X%
        
        Parameters
        ----------
        views : Dict[Tuple[str, str], float]
            Dictionary mapping (asset_A, asset_B) to expected outperformance
        confidences : Optional[Dict[Tuple[str, str], float]], optional
            Dictionary mapping asset pairs to confidence levels (0-1),
            by default None
        """
        n_assets = len(self.prior_returns)
        n_views = len(views)
        
        P = np.zeros((n_views, n_assets))
        q = np.zeros(n_views)
        
        for i, ((asset_a, asset_b), outperformance) in enumerate(views.items()):
            if asset_a not in self.prior_returns.index:
                raise ValueError(f"Asset {asset_a} not in universe")
            if asset_b not in self.prior_returns.index:
                raise ValueError(f"Asset {asset_b} not in universe")
            
            idx_a = self.prior_returns.index.get_loc(asset_a)
            idx_b = self.prior_returns.index.get_loc(asset_b)
            
            P[i, idx_a] = 1.0
            P[i, idx_b] = -1.0
            q[i] = outperformance
        
        # Omega matrix
        if confidences is None:
            confidences = {pair: 0.5 for pair in views.keys()}
        
        omega_diag = []
        for i, pair in enumerate(views.keys()):
            conf = confidences[pair]
            variance = self.tau * P[i] @ self.cov_matrix.values @ P[i].T / conf
            omega_diag.append(variance)
        
        Omega = np.diag(omega_diag)
        
        self.views = {"P": P, "q": q, "Omega": Omega}
        return self
    
    def compute_posterior(self) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Compute posterior expected returns and covariance.
        
        Uses the Black-Litterman master formula:
        
        μ_BL = [(τΣ)^-1 + P'Ω^-1 P]^-1 [(τΣ)^-1 π + P'Ω^-1 q]
        Σ_BL = [(τΣ)^-1 + P'Ω^-1 P]^-1
        
        Returns
        -------
        Tuple[pd.Series, pd.DataFrame]
            - Posterior expected returns
            - Posterior covariance matrix
        """
        Sigma = self.cov_matrix.values
        pi = self.prior_returns.values
        tau = self.tau
        
        if self.views is None:
            # No views: posterior = prior
            self.posterior_returns = self.prior_returns.copy()
            self.posterior_cov = self.cov_matrix.copy()
            return self.posterior_returns, self.posterior_cov
        
        P = self.views["P"]
        q = self.views["q"]
        Omega = self.views["Omega"]
        
        # Compute posterior using BL formula
        tau_Sigma = tau * Sigma
        tau_Sigma_inv = np.linalg.inv(tau_Sigma)
        Omega_inv = np.linalg.inv(Omega)
        
        # Posterior covariance
        M = tau_Sigma_inv + P.T @ Omega_inv @ P
        M_inv = np.linalg.inv(M)
        
        # Posterior mean
        mu_bl = M_inv @ (tau_Sigma_inv @ pi + P.T @ Omega_inv @ q)
        
        # Posterior covariance (for returns)
        Sigma_bl = M_inv
        
        self.posterior_returns = pd.Series(
            mu_bl,
            index=self.prior_returns.index
        )
        
        self.posterior_cov = pd.DataFrame(
            Sigma_bl,
            index=self.cov_matrix.index,
            columns=self.cov_matrix.columns
        )
        
        return self.posterior_returns, self.posterior_cov
    
    def compute_implied_returns(self, market_weights: pd.Series) -> pd.Series:
        """
        Compute implied equilibrium returns from market weights.
        
        Uses reverse optimization:
        π = δ * Σ * w_mkt
        
        Parameters
        ----------
        market_weights : pd.Series
            Market capitalization weights
            
        Returns
        -------
        pd.Series
            Implied equilibrium returns
        """
        # Align weights with covariance
        common_assets = market_weights.index.intersection(self.cov_matrix.index)
        w = market_weights.loc[common_assets].values
        Sigma = self.cov_matrix.loc[common_assets, common_assets].values
        
        # Implied returns: π = δΣw
        pi = self.risk_aversion * Sigma @ w
        
        return pd.Series(pi, index=common_assets)
    
    def get_view_deviations(self) -> pd.DataFrame:
        """
        Compare posterior returns to prior returns.
        
        Returns
        -------
        pd.DataFrame
            DataFrame showing prior, posterior, and deviation
        """
        if self.posterior_returns is None:
            raise ValueError("Must compute posterior first")
        
        comparison = pd.DataFrame({
            "Prior": self.prior_returns,
            "Posterior": self.posterior_returns,
            "Deviation": self.posterior_returns - self.prior_returns,
            "Pct_Change": (self.posterior_returns - self.prior_returns) / self.prior_returns.abs()
        })
        
        return comparison


def simple_black_litterman(
    prior_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    views: Optional[Dict] = None,
    tau: float = 0.025,
    risk_aversion: float = 2.5
) -> pd.Series:
    """
    Simple wrapper for Black-Litterman model.
    
    Parameters
    ----------
    prior_returns : pd.Series
        Prior expected returns (can be from CMA, CAPM, etc.)
    cov_matrix : pd.DataFrame
        Covariance matrix
    views : Optional[Dict], optional
        Dictionary of absolute views {asset: expected_return}, by default None
    tau : float, optional
        Uncertainty parameter, by default 0.025
    risk_aversion : float, optional
        Risk aversion parameter, by default 2.5
        
    Returns
    -------
    pd.Series
        Posterior expected returns
    """
    bl = BlackLittermanModel(prior_returns, cov_matrix, risk_aversion, tau)
    
    if views is not None:
        bl.add_absolute_views(views)
    
    posterior, _ = bl.compute_posterior()
    return posterior


def market_implied_returns(
    market_cap_weights: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_aversion: float = 2.5
) -> pd.Series:
    """
    Calculate market-implied equilibrium returns.
    
    Uses reverse optimization to infer returns implied by
    observed market capitalization weights.
    
    Parameters
    ----------
    market_cap_weights : pd.Series
        Market capitalization weights (should sum to 1)
    cov_matrix : pd.DataFrame
        Covariance matrix
    risk_aversion : float, optional
        Market risk aversion coefficient, by default 2.5
        
    Returns
    -------
    pd.Series
        Implied equilibrium returns
    """
    # Normalize weights
    weights = market_cap_weights / market_cap_weights.sum()
    
    # Align with covariance
    common_assets = weights.index.intersection(cov_matrix.index)
    w = weights.loc[common_assets].values
    Sigma = cov_matrix.loc[common_assets, common_assets].values
    
    # Implied returns: π = δΣw
    implied = risk_aversion * Sigma @ w
    
    return pd.Series(implied, index=common_assets)
