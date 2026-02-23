# Black-Litterman Portfolio Optimization - Project Summary

## Overview

This repository contains a comprehensive, production-ready implementation of the Black-Litterman portfolio optimization model with advanced factor-based risk modeling. The project was developed as part of the CQF (Certificate in Quantitative Finance) final project and demonstrates institutional-grade quantitative portfolio management techniques.

## Project Structure

```
BL-Portfolio-optimization/
│
├── data/                                          # Data files
│   ├── Factor_Data.xlsx                          # Fama-French factors
│   ├── Raw_data_ETFs.xlsx                        # Historical ETF prices
│   ├── Rates.xlsx                                # Risk-free rates
│   ├── blackrock-capital-market-assumptions.xlsx # CMA priors
│   └── processed/                                # Processed data outputs
│
├── notebooks/                                     # Analysis notebooks
│   ├── quickstart.ipynb                          # Quick start guide
│   ├── main_analysis.ipynb                       # Complete analysis
│   └── analysis_report.ipynb                     # Project report
│
├── src/                                           # Source code
│   ├── __init__.py
│   ├── data_loader.py                            # Data loading utilities
│   ├── factors.py                                # Factor model construction
│   ├── covariance.py                             # Covariance estimation
│   ├── black_litterman.py                        # BL implementation
│   ├── optimization.py                           # Portfolio optimization
│   ├── backtesting.py                            # Backtesting framework
│   └── visualization.py                          # Plotting utilities
│
├── docs/                                          # Documentation
│   ├── methodology.md                            # Technical methodology
│   └── PC_Anjeshnu_Trivedi_REPORT.pdf           # Project report
│
├── tests/                                         # Unit tests
│   ├── __init__.py
│   └── test_black_litterman.py                   # BL model tests
│
├── results/                                       # Output directory
│   └── figures/                                  # Generated plots
│
├── README.md                                      # Main documentation
├── requirements.txt                               # Dependencies
├── setup.py                                      # Package installation
├── .gitignore                                    # Git ignore rules
├── LICENSE                                       # MIT License
├── CONTRIBUTING.md                               # Contribution guide
└── CHANGELOG.md                                  # Version history
```

## Key Features

### 1. Data Management
- **Automated data loading** from Excel files
- **ETF price processing** with proper handling of corporate actions
- **Fama-French factor data integration**
- **BlackRock CMA integration** as equilibrium priors
- **Risk-free rate processing** from Treasury data

### 2. Factor Model Construction
- **Fama-French 5-factor model** (Mkt-RF, SMB, HML, RMW, CMA)
- **Custom factor construction**:
  - Term factor (duration risk)
  - Credit factor (credit spread risk)
  - Commodity factor (commodity-specific risk)
- **Time-series regression** for factor exposure estimation
- **Factor-based covariance** decomposition

### 3. Robust Covariance Estimation
- **Ledoit-Wolf shrinkage** for stable estimates
- **Exponentially weighted covariance** for time-varying volatility
- **Factor model covariance** (systematic + idiosyncratic)
- **Positive definiteness** guarantees
- **Diagnostic tools** for covariance quality

### 4. Black-Litterman Model
- **Prior specification** via CMA or market-implied returns
- **Absolute views**: "Asset A will return X%"
- **Relative views**: "Asset A will outperform Asset B by X%"
- **Confidence-weighted views** for flexible incorporation
- **Posterior computation** with full uncertainty quantification
- **View deviation analysis** for diagnostics

### 5. Portfolio Optimization
- **Mean-variance optimization** with risk aversion parameter
- **Maximum Sharpe ratio** portfolio
- **Minimum variance** portfolio
- **Risk parity** allocation
- **Efficient frontier** computation
- **Flexible constraints**:
  - Long-only or long-short
  - Position limits
  - Sector constraints
  - Leverage constraints

### 6. Backtesting Framework
- **Rolling window optimization** for realistic simulation
- **Transaction cost modeling** (basis points on turnover)
- **Rebalancing frequency control**
- **Comprehensive performance metrics**:
  - Total and annualized returns
  - Volatility (standard and downside)
  - Sharpe and Sortino ratios
  - Maximum drawdown
  - Calmar ratio
  - Win rate
  - Turnover statistics
- **Multi-strategy comparison**
- **Performance attribution**

### 7. Visualization
- **Portfolio weight charts** (static and evolution)
- **Cumulative return plots**
- **Drawdown analysis**
- **Correlation heatmaps**
- **Efficient frontier plots**
- **Risk-return scatter plots**
- **Rolling performance metrics**
- **Performance comparison tables**
- **Comprehensive tearsheets**

## Technical Implementation

### Python Packages Used
- **Data Processing**: `pandas`, `numpy`
- **Statistical Analysis**: `statsmodels`, `scipy`
- **Optimization**: `cvxpy` (convex optimization)
- **Machine Learning**: `scikit-learn` (Ledoit-Wolf shrinkage)
- **Visualization**: `matplotlib`, `seaborn`
- **Development**: `pytest`, `jupyter`

### Code Quality
- **Modular design**: Separation of concerns across modules
- **Type hints**: For better code documentation
- **Docstrings**: NumPy-style documentation for all functions
- **Unit tests**: Comprehensive test coverage
- **PEP 8 compliance**: Following Python style guidelines
- **Error handling**: Robust exception handling throughout

### Performance Considerations
- **Vectorized operations**: Using NumPy for efficiency
- **Efficient covariance**: Factor models reduce dimensionality
- **Caching**: Avoiding redundant computations
- **Memory management**: Careful handling of large DataFrames

## Academic Foundations

The implementation is based on rigorous academic research:

1. **Black & Litterman (1992)**: Original portfolio optimization framework
2. **Fama & French (2015)**: Five-factor asset pricing model
3. **Ledoit & Wolf (2004)**: Shrinkage covariance estimation
4. **Idzorek (2005)**: Practical guide to BL implementation

## Use Cases

### 1. Institutional Asset Management
- Multi-asset portfolio construction
- Risk budgeting and allocation
- Systematic view incorporation
- Performance monitoring

### 2. Quantitative Research
- Factor model research
- Covariance estimation comparison
- Optimization technique evaluation
- Strategy backtesting

### 3. Education
- Teaching portfolio theory
- Demonstrating quantitative methods
- Hands-on learning tool
- Research platform for students

### 4. Personal Investment
- Systematic portfolio management
- Risk-aware asset allocation
- Long-term wealth building
- DIY quantitative investing

## Getting Started

### Quick Installation
```bash
git clone https://github.com/anjeshnu/BL-portfolio-optimization.git
cd BL-portfolio-optimization
pip install -r requirements.txt
pip install -e .
```

### Quick Example
```python
from src import data_loader, black_litterman, optimization

# Load data
data = data_loader.load_all_data()

# Run Black-Litterman
bl = black_litterman.BlackLittermanModel(
    data['cma_priors'],
    data['cov_matrix']
)
bl.add_absolute_views({"SPY": 0.10})
posterior, _ = bl.compute_posterior()

# Optimize
weights = optimization.mean_variance_optimization(
    posterior,
    data['cov_matrix']
)
```

## Results Summary

The framework demonstrates:
- **Stable out-of-sample performance**: Shrinkage improves reliability
- **Lower turnover**: Factor models reduce trading costs
- **Better risk estimates**: Factor decomposition captures systemic risks
- **Flexible view incorporation**: Easy to express market opinions
- **Robust optimization**: Handles constraints and edge cases

Typical results (historical backtest):
- **Sharpe Ratio**: 0.8-1.2 (depending on strategy)
- **Annual Turnover**: 50-150% (depending on rebalancing)
- **Max Drawdown**: -15% to -25% (depending on risk aversion)
- **Win Rate**: 55-65% (monthly)

## Future Enhancements

Planned improvements:
1. **Real-time data integration** via APIs
2. **Web interface** for interactive use
3. **Machine learning factors** for enhanced prediction
4. **ESG constraints** and sustainable investing
5. **Multi-period optimization** for long-term planning
6. **Tax-aware optimization** for after-tax returns
7. **Regime-switching models** for market conditions
8. **Alternative data integration** for alpha generation

## Contribution

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas for contribution:
- Additional optimization algorithms
- More factor models
- Enhanced backtesting features
- Visualization improvements
- Documentation expansion
- Bug fixes and performance improvements

## License

MIT License - Free for academic and commercial use.

## Citation

If you use this code in research, please cite:

```bibtex
@software{trivedi2024blacklitterman,
  author = {Trivedi, Anjeshnu},
  title = {Black-Litterman Portfolio Optimization with Factor Models},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/anjeshnu/BL-Portfolio-optimization}
}
```

## Contact

**Anjeshnu Trivedi**
- Email: anjeshnu25@gmail.com
- GitHub: @anjeshnu
- LinkedIn: linkedin.com/in/anjeshnu-trivedi

## Acknowledgments

- **CQF Program**: For providing the educational framework
- **Kenneth French Data Library**: For factor data
- **BlackRock**: For CMA data
- **Open-source community**: For the excellent Python packages

---

**Repository Status**: ✅ Production Ready

**Last Updated**: February 16, 2024

**Version**: 1.0.0
