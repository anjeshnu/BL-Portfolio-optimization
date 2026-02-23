"""
Backtesting Framework

Functions for backtesting portfolio strategies with transaction costs
and performance analysis.
"""

from typing import Callable, Optional, Dict
import pandas as pd
import numpy as np


class PortfolioBacktest:
    """
    Backtest portfolio strategies with rolling optimization.
    """
    
    def __init__(
        self,
        returns: pd.DataFrame,
        optimization_func: Callable,
        lookback_period: int = 60,
        rebalance_frequency: int = 1,
        transaction_cost: float = 0.001
    ):
        """
        Initialize backtest.
        
        Parameters
        ----------
        returns : pd.DataFrame
            Asset returns (time × assets)
        optimization_func : Callable
            Function that takes returns and returns optimal weights
        lookback_period : int, optional
            Rolling window for optimization, by default 60
        rebalance_frequency : int, optional
            Rebalance every N periods, by default 1 (monthly)
        transaction_cost : float, optional
            Transaction cost as fraction of trade value, by default 0.001 (10 bps)
        """
        self.returns = returns
        self.optimization_func = optimization_func
        self.lookback_period = lookback_period
        self.rebalance_frequency = rebalance_frequency
        self.transaction_cost = transaction_cost
        
        self.weights_history = None
        self.portfolio_returns = None
        self.portfolio_value = None
        self.turnover = None
    
    def run(self) -> pd.DataFrame:
        """
        Run the backtest.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with backtest results including weights, returns, value
        """
        returns = self.returns
        dates = returns.index[self.lookback_period:]
        
        weights_list = []
        portfolio_returns_list = []
        turnover_list = []
        
        prev_weights = None
        
        for i, date in enumerate(dates):
            # Check if rebalancing period
            if i % self.rebalance_frequency == 0:
                # Get historical returns for optimization
                hist_returns = returns.iloc[i:i+self.lookback_period]
                
                try:
                    # Optimize
                    new_weights = self.optimization_func(hist_returns)
                    
                    # Calculate turnover
                    if prev_weights is not None:
                        turnover = (new_weights - prev_weights).abs().sum()
                        transaction_costs = turnover * self.transaction_cost
                    else:
                        turnover = new_weights.abs().sum()
                        transaction_costs = turnover * self.transaction_cost
                    
                    prev_weights = new_weights
                    
                except Exception as e:
                    print(f"Optimization failed at {date}: {e}")
                    if prev_weights is None:
                        # Equal weight as fallback
                        new_weights = pd.Series(
                            1.0 / len(returns.columns),
                            index=returns.columns
                        )
                    else:
                        new_weights = prev_weights
                    turnover = 0
                    transaction_costs = 0
            else:
                # No rebalancing
                new_weights = prev_weights
                turnover = 0
                transaction_costs = 0
            
            # Calculate portfolio return
            current_returns = returns.loc[date]
            portfolio_return = (new_weights * current_returns).sum() - transaction_costs
            
            weights_list.append(new_weights)
            portfolio_returns_list.append(portfolio_return)
            turnover_list.append(turnover)
        
        # Compile results
        self.weights_history = pd.DataFrame(weights_list, index=dates)
        self.portfolio_returns = pd.Series(portfolio_returns_list, index=dates)
        self.turnover = pd.Series(turnover_list, index=dates)
        
        # Calculate cumulative value
        self.portfolio_value = (1 + self.portfolio_returns).cumprod()
        
        results = pd.DataFrame({
            "Portfolio_Return": self.portfolio_returns,
            "Portfolio_Value": self.portfolio_value,
            "Turnover": self.turnover
        })
        
        return results
    
    def get_performance_stats(self, risk_free_rate: float = 0.0) -> Dict:
        """
        Calculate performance statistics.
        
        Parameters
        ----------
        risk_free_rate : float, optional
            Risk-free rate (monthly), by default 0.0
            
        Returns
        -------
        Dict
            Performance statistics
        """
        if self.portfolio_returns is None:
            raise ValueError("Must run backtest first")
        
        returns = self.portfolio_returns
        
        # Basic statistics
        total_return = self.portfolio_value.iloc[-1] - 1
        annual_return = (1 + total_return) ** (12 / len(returns)) - 1
        annual_vol = returns.std() * np.sqrt(12)
        sharpe_ratio = (annual_return - risk_free_rate * 12) / annual_vol if annual_vol > 0 else 0
        
        # Downside statistics
        negative_returns = returns[returns < 0]
        downside_vol = negative_returns.std() * np.sqrt(12) if len(negative_returns) > 0 else 0
        sortino_ratio = (annual_return - risk_free_rate * 12) / downside_vol if downside_vol > 0 else 0
        
        # Drawdown
        cumulative = self.portfolio_value
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (returns > 0).sum() / len(returns)
        
        # Turnover
        avg_turnover = self.turnover.mean()
        avg_annual_turnover = avg_turnover * 12
        
        # Calmar ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        stats = {
            "Total Return": total_return,
            "Annual Return": annual_return,
            "Annual Volatility": annual_vol,
            "Sharpe Ratio": sharpe_ratio,
            "Sortino Ratio": sortino_ratio,
            "Max Drawdown": max_drawdown,
            "Calmar Ratio": calmar_ratio,
            "Win Rate": win_rate,
            "Avg Monthly Turnover": avg_turnover,
            "Avg Annual Turnover": avg_annual_turnover,
        }
        
        return stats


def compare_strategies(
    returns: pd.DataFrame,
    strategies: Dict[str, Callable],
    lookback_period: int = 60,
    rebalance_frequency: int = 1,
    transaction_cost: float = 0.001,
    risk_free_rate: float = 0.0
) -> pd.DataFrame:
    """
    Compare multiple portfolio strategies.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns
    strategies : Dict[str, Callable]
        Dictionary mapping strategy names to optimization functions
    lookback_period : int, optional
        Rolling window, by default 60
    rebalance_frequency : int, optional
        Rebalance frequency, by default 1
    transaction_cost : float, optional
        Transaction cost, by default 0.001
    risk_free_rate : float, optional
        Risk-free rate, by default 0.0
        
    Returns
    -------
    pd.DataFrame
        Comparison table of performance statistics
    """
    results = {}
    
    for name, opt_func in strategies.items():
        print(f"Backtesting {name}...")
        
        backtest = PortfolioBacktest(
            returns,
            opt_func,
            lookback_period,
            rebalance_frequency,
            transaction_cost
        )
        
        try:
            backtest.run()
            stats = backtest.get_performance_stats(risk_free_rate)
            results[name] = stats
        except Exception as e:
            print(f"  Failed: {e}")
            results[name] = {k: np.nan for k in [
                "Total Return", "Annual Return", "Annual Volatility",
                "Sharpe Ratio", "Sortino Ratio", "Max Drawdown",
                "Calmar Ratio", "Win Rate", "Avg Monthly Turnover",
                "Avg Annual Turnover"
            ]}
    
    comparison = pd.DataFrame(results).T
    return comparison


def rolling_performance(
    portfolio_returns: pd.Series,
    window: int = 12
) -> pd.DataFrame:
    """
    Calculate rolling performance metrics.
    
    Parameters
    ----------
    portfolio_returns : pd.Series
        Portfolio returns
    window : int, optional
        Rolling window size, by default 12 (1 year for monthly data)
        
    Returns
    -------
    pd.DataFrame
        Rolling performance metrics
    """
    rolling_return = portfolio_returns.rolling(window).mean() * 12
    rolling_vol = portfolio_returns.rolling(window).std() * np.sqrt(12)
    rolling_sharpe = rolling_return / rolling_vol
    
    results = pd.DataFrame({
        "Rolling_Return": rolling_return,
        "Rolling_Volatility": rolling_vol,
        "Rolling_Sharpe": rolling_sharpe
    })
    
    return results


def performance_attribution(
    portfolio_weights: pd.DataFrame,
    asset_returns: pd.DataFrame
) -> pd.DataFrame:
    """
    Perform performance attribution.
    
    Decompose portfolio returns into asset-level contributions.
    
    Parameters
    ----------
    portfolio_weights : pd.DataFrame
        Portfolio weights over time (time × assets)
    asset_returns : pd.DataFrame
        Asset returns (time × assets)
        
    Returns
    -------
    pd.DataFrame
        Contribution to portfolio return by asset
    """
    # Align dates
    common_dates = portfolio_weights.index.intersection(asset_returns.index)
    weights = portfolio_weights.loc[common_dates]
    returns = asset_returns.loc[common_dates]
    
    # Calculate contributions
    contributions = weights * returns
    
    return contributions


def calculate_drawdowns(returns: pd.Series) -> pd.DataFrame:
    """
    Calculate drawdown series.
    
    Parameters
    ----------
    returns : pd.Series
        Return series
        
    Returns
    -------
    pd.DataFrame
        DataFrame with cumulative returns, running max, and drawdown
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    results = pd.DataFrame({
        "Cumulative_Return": cumulative,
        "Running_Max": running_max,
        "Drawdown": drawdown
    })
    
    return results
