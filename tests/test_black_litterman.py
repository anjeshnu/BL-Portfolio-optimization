"""
Unit tests for Black-Litterman model implementation
"""

import pytest
import numpy as np
import pandas as pd
from src.black_litterman import BlackLittermanModel, simple_black_litterman


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    
    assets = ["Asset_A", "Asset_B", "Asset_C"]
    
    # Prior returns (annual)
    prior_returns = pd.Series([0.08, 0.10, 0.12], index=assets)
    
    # Covariance matrix (annual)
    cov_matrix = pd.DataFrame(
        [[0.04, 0.01, 0.02],
         [0.01, 0.09, 0.03],
         [0.02, 0.03, 0.16]],
        index=assets,
        columns=assets
    )
    
    return {"prior_returns": prior_returns, "cov_matrix": cov_matrix}


def test_black_litterman_initialization(sample_data):
    """Test BL model initialization."""
    bl = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    
    assert bl.prior_returns is not None
    assert bl.cov_matrix is not None
    assert bl.tau == 0.025
    assert bl.risk_aversion == 2.5


def test_no_views_equals_prior(sample_data):
    """Test that with no views, posterior equals prior."""
    bl = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    
    posterior, _ = bl.compute_posterior()
    
    # Posterior should equal prior when no views
    np.testing.assert_array_almost_equal(
        posterior.values,
        sample_data["prior_returns"].values,
        decimal=6
    )


def test_absolute_views(sample_data):
    """Test absolute view incorporation."""
    bl = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    
    # Add view: Asset_A will return 15%
    views = {"Asset_A": 0.15}
    bl.add_absolute_views(views)
    
    posterior, _ = bl.compute_posterior()
    
    # Posterior for Asset_A should be between prior (8%) and view (15%)
    assert sample_data["prior_returns"]["Asset_A"] < posterior["Asset_A"] < views["Asset_A"]


def test_relative_views(sample_data):
    """Test relative view incorporation."""
    bl = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    
    # Add view: Asset_A will outperform Asset_B by 5%
    views = {("Asset_A", "Asset_B"): 0.05}
    bl.add_relative_views(views)
    
    posterior, _ = bl.compute_posterior()
    
    # Check that relative ordering is affected
    assert isinstance(posterior, pd.Series)
    assert len(posterior) == 3


def test_high_confidence_views(sample_data):
    """Test that high confidence views have more impact."""
    # Low confidence
    bl_low = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    views = {"Asset_A": 0.15}
    bl_low.add_absolute_views(views, {"Asset_A": 0.1})
    posterior_low, _ = bl_low.compute_posterior()
    
    # High confidence
    bl_high = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    bl_high.add_absolute_views(views, {"Asset_A": 0.9})
    posterior_high, _ = bl_high.compute_posterior()
    
    # High confidence should be closer to view
    diff_low = abs(posterior_low["Asset_A"] - views["Asset_A"])
    diff_high = abs(posterior_high["Asset_A"] - views["Asset_A"])
    
    assert diff_high < diff_low


def test_simple_black_litterman(sample_data):
    """Test simple wrapper function."""
    views = {"Asset_A": 0.15, "Asset_B": 0.08}
    
    posterior = simple_black_litterman(
        sample_data["prior_returns"],
        sample_data["cov_matrix"],
        views=views
    )
    
    assert isinstance(posterior, pd.Series)
    assert len(posterior) == 3


def test_posterior_covariance(sample_data):
    """Test that posterior covariance is computed."""
    bl = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    
    views = {"Asset_A": 0.15}
    bl.add_absolute_views(views)
    
    _, posterior_cov = bl.compute_posterior()
    
    assert isinstance(posterior_cov, pd.DataFrame)
    assert posterior_cov.shape == (3, 3)
    # Should be positive definite
    assert np.all(np.linalg.eigvals(posterior_cov.values) > 0)


def test_view_deviations(sample_data):
    """Test view deviation calculation."""
    bl = BlackLittermanModel(
        sample_data["prior_returns"],
        sample_data["cov_matrix"]
    )
    
    views = {"Asset_A": 0.15}
    bl.add_absolute_views(views)
    bl.compute_posterior()
    
    deviations = bl.get_view_deviations()
    
    assert isinstance(deviations, pd.DataFrame)
    assert "Prior" in deviations.columns
    assert "Posterior" in deviations.columns
    assert "Deviation" in deviations.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
