# Black-Litterman Portfolio Optimization with Factor Models

A comprehensive implementation of the Black-Litterman portfolio optimization model incorporating factor-based risk models and capital market assumptions. This project demonstrates advanced portfolio construction techniques combining modern portfolio theory with practitioner insights.

## 📋 Overview

This repository implements a sophisticated portfolio optimization framework that:

- **Combines Black-Litterman methodology** with factor-based covariance estimation
- **Incorporates Capital Market Assumptions (CMA)** from institutional sources (BlackRock)
- **Uses Fama-French factors** and custom factor construction for robust risk modeling
- **Applies shrinkage techniques** (Ledoit-Wolf) for stable covariance estimation
- **Backtests strategies** across multiple asset classes (equities, bonds, commodities)

## 🎯 Key Features

- **Data Processing Pipeline**: Automated ETF price data processing and return calculations
- **Factor Model Construction**: Custom factors for Term, Credit, and Commodity exposures
- **Covariance Estimation**: Factor-based and shrinkage covariance matrices
- **Black-Litterman Implementation**: Full BL model with view incorporation
- **Portfolio Optimization**: Mean-variance and risk parity optimization with constraints
- **Backtesting Framework**: Historical performance analysis and attribution
- **Visualization**: Comprehensive plotting of weights, returns, and risk metrics

## 📁 Repository Structure

```
BL-Portfolio-optimization/
│
├── data/                          # Data files
│   ├── Factor_Data.xlsx          # Fama-French and custom factors
│   ├── Raw_data_ETFs.xlsx        # ETF historical prices
│   ├── Rates.xlsx                # Risk-free rates
│   └── blackrock-capital-market-assumptions.xlsx   # Capital market assumptions
│
├── notebooks/                     # Jupyter notebooks
│   ├── main_analysis.ipynb       # Complete end-to-end analysis with different segments 
│   ├── analysis_report.ipynb
|   └── quickstart.ipynb
|
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── data_loader.py            # Data loading utilities
│   ├── returns.py                # Return calculations
│   ├── factors.py                # Factor construction
│   ├── covariance.py             # Covariance estimation
│   ├── black_litterman.py        # BL model implementation
│   ├── optimization.py           # Portfolio optimization
│   ├── backtesting.py            # Backtesting framework
│   └── visualization.py          # Plotting utilities
│
├── docs/                         # Documentation
|   ├── PC_Anjeshnu_Trivedi_Report.pdf    Detailed report from the analysis                         
│   └── methodology.md            # Detailed methodology
│
├── tests/                         # Unit tests
│   └── test_black_litterman.py
│
├── results/                       # Output files
│   └── figures/                  # Generated plots
│
├── requirements.txt               # Python dependencies
├── setup.py                      # Package installation
├── .gitignore                    # Git ignore rules
├── LICENSE                       # License file
└── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Jupyter Notebook/Lab
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/anjeshnu/BL-portfolio-optimization.git
cd BL-portfolio-optimization
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

### Quick Start

Run the complete analysis:

```python
from src.data_loader import load_all_data
from src.black_litterman import BlackLittermanModel
from src.optimization import optimize_portfolio

# Load data
data = load_all_data()

# Run Black-Litterman
bl_model = BlackLittermanModel(data['returns'], data['cma_priors'])
posterior_returns = bl_model.compute_posterior()

# Optimize portfolio
weights = optimize_portfolio(posterior_returns, data['covariance'])
```

Or explore the Jupyter notebooks in the `notebooks/` directory.

## 📊 Methodology

### 1. Data Preparation
- Load ETF prices and calculate monthly returns
- Process Fama-French factor data
- Incorporate BlackRock Capital Market Assumptions as priors
- Construct risk-free rate series

### 2. Factor Model
- Use Fama-French 5-factor model (Mkt-RF, SMB, HML, RMW, CMA)
- Construct custom factors:
  - **Term Factor**: Interest rate duration exposure
  - **Credit Factor**: Credit spread exposure  
  - **Commodity Factor**: Commodity-specific risk
- Estimate factor exposures via time-series regression
- Build factor-based covariance matrix

### 3. Covariance Estimation
- Factor model covariance: Σ = B·F·B' + D
- Ledoit-Wolf shrinkage for robust estimation
- Handle missing data and estimation windows

### 4. Black-Litterman Model
- Use CMA as equilibrium priors (Π)
- Incorporate views with confidence levels
- Compute posterior expected returns
- Combine with robust covariance estimates

### 5. Portfolio Optimization
- Mean-variance optimization with BL inputs
- Long-only constraints
- Position limits and sector constraints
- Risk parity alternative strategies

### 6. Backtesting
- Rolling window optimization
- Transaction cost modeling
- Performance attribution
- Risk analytics (Sharpe, drawdowns, turnover)

## 📈 Key Results

The framework demonstrates:
- Improved out-of-sample Sharpe ratios vs. baseline strategies
- Lower portfolio turnover through stable covariance estimates
- Effective incorporation of market views
- Robust performance across different market regimes

*See the notebooks for detailed results and visualizations.*

## 🛠️ Technical Stack

- **Data Processing**: `pandas`, `numpy`
- **Statistical Analysis**: `statsmodels`, `scipy`
- **Optimization**: `cvxpy`
- **Covariance Estimation**: `sklearn.covariance`
- **Visualization**: `matplotlib`, `seaborn`
- **Notebook**: `jupyter`

## 📚 References

1. Black, F., & Litterman, R. (1992). "Global Portfolio Optimization". Financial Analysts Journal.
2. He, G., & Litterman, R. (1999). "The Intuition Behind Black-Litterman Model Portfolios".
3. Fama, E. F., & French, K. R. (2015). "A Five-Factor Asset Pricing Model".
4. Ledoit, O., & Wolf, M. (2004). "Honey, I Shrunk the Sample Covariance Matrix".

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Anjeshnu Trivedi**

- GitHub: [@anjeshnu](https://github.com/anjeshnu)
- LinkedIn: [Anjeshnu Trivedi](https://linkedin.com/in/anjeshnu-trivedi)
- Email: anjeshnu25@gmail.com

## 🙏 Acknowledgments

- CQF (Certificate in Quantitative Finance) program
- BlackRock for Capital Market Assumptions data
- Kenneth French Data Library for factor data
- Open-source Python community

## 📝 Citation

If you use this code in your research, please cite:

```bibtex
@software{trivedi2024blacklitterman,
  author = {Trivedi, Anjeshnu},
  title = {Black-Litterman Portfolio Optimization with Factor Models},
  year = {2024},
  url = {https://github.com/anjeshnu/BL-portfolio-optimization}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss proposed changes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or feedback, please open an issue or contact me directly.

---

⭐ Star this repository if you find it helpful!
