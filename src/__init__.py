"""
Black-Litterman Portfolio Optimization Package

A comprehensive implementation of the Black-Litterman portfolio optimization model
incorporating factor-based risk models and capital market assumptions.
"""

__version__ = "1.0.0"
__author__ = "Anjeshnu Trivedi"

from . import data_loader
from . import returns
from . import factors
from . import covariance
from . import black_litterman
from . import optimization
from . import backtesting
from . import visualization

__all__ = [
    "data_loader",
    "returns",
    "factors",
    "covariance",
    "black_litterman",
    "optimization",
    "backtesting",
    "visualization",
]
