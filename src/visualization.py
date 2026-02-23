"""
Visualization Utilities

Functions for creating charts and plots for portfolio analysis.
"""

from typing import Optional, List, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Set default style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10


def plot_weights(
    weights: pd.Series,
    title: str = "Portfolio Weights",
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot portfolio weights as a bar chart.
    
    Parameters
    ----------
    weights : pd.Series
        Portfolio weights
    title : str, optional
        Plot title
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    weights.sort_values().plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlabel("Weight")
    ax.set_title(title)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_weights_evolution(
    weights_history: pd.DataFrame,
    title: str = "Portfolio Weights Over Time",
    figsize: Tuple[int, int] = (14, 8)
) -> plt.Figure:
    """
    Plot evolution of portfolio weights over time (stacked area chart).
    
    Parameters
    ----------
    weights_history : pd.DataFrame
        Portfolio weights over time (time × assets)
    title : str, optional
        Plot title
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    weights_history.plot(
        kind="area",
        stacked=True,
        ax=ax,
        alpha=0.7,
        linewidth=0
    )
    
    ax.set_ylabel("Weight")
    ax.set_xlabel("Date")
    ax.set_title(title)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_cumulative_returns(
    returns: pd.DataFrame,
    title: str = "Cumulative Returns",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot cumulative returns for multiple strategies.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Returns for different strategies (time × strategies)
    title : str, optional
        Plot title
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    cumulative = (1 + returns).cumprod()
    cumulative.plot(ax=ax, linewidth=2)
    
    ax.set_ylabel("Cumulative Return")
    ax.set_xlabel("Date")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_drawdown(
    returns: pd.Series,
    title: str = "Drawdown",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot drawdown over time.
    
    Parameters
    ----------
    returns : pd.Series
        Return series
    title : str, optional
        Plot title
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    drawdown.plot(ax=ax, color="red", linewidth=2)
    ax.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color="red")
    
    ax.set_ylabel("Drawdown")
    ax.set_xlabel("Date")
    ax.set_title(title)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_correlation_matrix(
    returns: pd.DataFrame,
    title: str = "Correlation Matrix",
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot correlation matrix as a heatmap.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns
    title : str, optional
        Plot title
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    corr = returns.corr()
    
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdYlBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        ax=ax
    )
    
    ax.set_title(title)
    plt.tight_layout()
    return fig


def plot_efficient_frontier(
    frontier_returns: np.ndarray,
    frontier_vols: np.ndarray,
    portfolio_returns: Optional[pd.Series] = None,
    portfolio_vols: Optional[pd.Series] = None,
    portfolio_labels: Optional[List[str]] = None,
    title: str = "Efficient Frontier",
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot efficient frontier with optional portfolio points.
    
    Parameters
    ----------
    frontier_returns : np.ndarray
        Returns on the efficient frontier
    frontier_vols : np.ndarray
        Volatilities on the efficient frontier
    portfolio_returns : Optional[pd.Series], optional
        Returns of specific portfolios to plot
    portfolio_vols : Optional[pd.Series], optional
        Volatilities of specific portfolios to plot
    portfolio_labels : Optional[List[str]], optional
        Labels for specific portfolios
    title : str, optional
        Plot title
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot frontier
    ax.plot(
        frontier_vols * np.sqrt(12),  # Annualize
        frontier_returns * 12,  # Annualize
        "b-",
        linewidth=2,
        label="Efficient Frontier"
    )
    
    # Plot specific portfolios
    if portfolio_returns is not None and portfolio_vols is not None:
        ax.scatter(
            portfolio_vols * np.sqrt(12),
            portfolio_returns * 12,
            s=100,
            c="red",
            marker="*",
            label="Portfolios"
        )
        
        if portfolio_labels is not None:
            for i, label in enumerate(portfolio_labels):
                ax.annotate(
                    label,
                    (portfolio_vols.iloc[i] * np.sqrt(12), portfolio_returns.iloc[i] * 12),
                    xytext=(5, 5),
                    textcoords="offset points"
                )
    
    ax.set_xlabel("Volatility (Annualized)")
    ax.set_ylabel("Return (Annualized)")
    ax.set_title(title)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_risk_return_scatter(
    returns: pd.DataFrame,
    title: str = "Risk-Return Scatter",
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot risk-return scatter for multiple assets or strategies.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Returns (time × assets/strategies)
    title : str, optional
        Plot title
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    mean_returns = returns.mean() * 12  # Annualize
    vols = returns.std() * np.sqrt(12)  # Annualize
    
    ax.scatter(vols, mean_returns, s=100, alpha=0.6)
    
    for i, asset in enumerate(returns.columns):
        ax.annotate(
            asset,
            (vols.iloc[i], mean_returns.iloc[i]),
            xytext=(5, 5),
            textcoords="offset points"
        )
    
    ax.set_xlabel("Volatility (Annualized)")
    ax.set_ylabel("Return (Annualized)")
    ax.set_title(title)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_rolling_metrics(
    returns: pd.Series,
    window: int = 12,
    figsize: Tuple[int, int] = (14, 10)
) -> plt.Figure:
    """
    Plot rolling performance metrics.
    
    Parameters
    ----------
    returns : pd.Series
        Return series
    window : int, optional
        Rolling window size, by default 12
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, axes = plt.subplots(3, 1, figsize=figsize)
    
    # Rolling return
    rolling_return = returns.rolling(window).mean() * 12
    rolling_return.plot(ax=axes[0], linewidth=2, color="steelblue")
    axes[0].set_ylabel("Rolling Return")
    axes[0].set_title("Rolling 12-Month Return")
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    axes[0].grid(True, alpha=0.3)
    
    # Rolling volatility
    rolling_vol = returns.rolling(window).std() * np.sqrt(12)
    rolling_vol.plot(ax=axes[1], linewidth=2, color="coral")
    axes[1].set_ylabel("Rolling Volatility")
    axes[1].set_title("Rolling 12-Month Volatility")
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    axes[1].grid(True, alpha=0.3)
    
    # Rolling Sharpe
    rolling_sharpe = rolling_return / rolling_vol
    rolling_sharpe.plot(ax=axes[2], linewidth=2, color="green")
    axes[2].set_ylabel("Rolling Sharpe Ratio")
    axes[2].set_title("Rolling 12-Month Sharpe Ratio")
    axes[2].axhline(0, color="black", linewidth=0.5)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_performance_comparison(
    comparison_df: pd.DataFrame,
    figsize: Tuple[int, int] = (14, 8)
) -> plt.Figure:
    """
    Plot performance comparison table as a heatmap.
    
    Parameters
    ----------
    comparison_df : pd.DataFrame
        Performance comparison DataFrame
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Normalize for heatmap (higher is better for most metrics)
    normalized = comparison_df.copy()
    
    # Invert metrics where lower is better
    for col in ["Annual Volatility", "Max Drawdown", "Avg Monthly Turnover", "Avg Annual Turnover"]:
        if col in normalized.columns:
            normalized[col] = -normalized[col]
    
    # Create heatmap
    sns.heatmap(
        normalized,
        annot=comparison_df,  # Show original values
        fmt=".3f",
        cmap="RdYlGn",
        center=0,
        cbar_kws={"label": "Normalized Score"},
        ax=ax
    )
    
    ax.set_title("Strategy Performance Comparison")
    plt.tight_layout()
    return fig


def create_tearsheet(
    returns: pd.Series,
    weights_history: Optional[pd.DataFrame] = None,
    benchmark_returns: Optional[pd.Series] = None,
    figsize: Tuple[int, int] = (16, 12)
) -> plt.Figure:
    """
    Create a comprehensive performance tearsheet.
    
    Parameters
    ----------
    returns : pd.Series
        Strategy returns
    weights_history : Optional[pd.DataFrame], optional
        Portfolio weights over time
    benchmark_returns : Optional[pd.Series], optional
        Benchmark returns for comparison
    figsize : Tuple[int, int], optional
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Cumulative returns
    ax1 = fig.add_subplot(gs[0, :])
    cumulative = (1 + returns).cumprod()
    cumulative.plot(ax=ax1, linewidth=2, label="Strategy")
    if benchmark_returns is not None:
        benchmark_cum = (1 + benchmark_returns).cumprod()
        benchmark_cum.plot(ax=ax1, linewidth=2, label="Benchmark", alpha=0.7)
    ax1.set_title("Cumulative Returns")
    ax1.set_ylabel("Value")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Drawdown
    ax2 = fig.add_subplot(gs[1, 0])
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    drawdown.plot(ax=ax2, color="red", linewidth=2)
    ax2.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color="red")
    ax2.set_title("Drawdown")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax2.grid(True, alpha=0.3)
    
    # Monthly returns distribution
    ax3 = fig.add_subplot(gs[1, 1])
    returns.hist(bins=50, ax=ax3, alpha=0.7, edgecolor="black")
    ax3.axvline(returns.mean(), color="red", linestyle="--", label=f"Mean: {returns.mean():.2%}")
    ax3.axvline(returns.median(), color="green", linestyle="--", label=f"Median: {returns.median():.2%}")
    ax3.set_title("Return Distribution")
    ax3.set_xlabel("Return")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Weights evolution (if provided)
    if weights_history is not None:
        ax4 = fig.add_subplot(gs[2, :])
        weights_history.plot(
            kind="area",
            stacked=True,
            ax=ax4,
            alpha=0.7,
            linewidth=0
        )
        ax4.set_title("Portfolio Weights Over Time")
        ax4.set_ylabel("Weight")
        ax4.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        ax4.set_ylim(0, 1)
        ax4.grid(True, alpha=0.3)
    
    plt.suptitle("Portfolio Performance Tearsheet", fontsize=16, y=0.995)
    
    return fig
