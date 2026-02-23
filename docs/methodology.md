# Methodology

This document provides a detailed explanation of the methodology used in this Black-Litterman portfolio optimization implementation.

## Table of Contents

1. [Overview](#overview)
2. [Data Preparation](#data-preparation)
3. [Factor Model Construction](#factor-model-construction)
4. [Covariance Estimation](#covariance-estimation)
5. [Black-Litterman Model](#black-litterman-model)
6. [Portfolio Optimization](#portfolio-optimization)
7. [Backtesting](#backtesting)

## Overview

The Black-Litterman model provides a systematic framework for combining market equilibrium (prior views) with an investor's subjective views to generate expected returns for portfolio optimization. This implementation enhances the traditional model by:

1. Using factor-based covariance estimation for more stable risk models
2. Incorporating institutional Capital Market Assumptions as priors
3. Applying shrinkage techniques to improve out-of-sample performance
4. Implementing a comprehensive backtesting framework

## Data Preparation

### Asset Universe

The analysis focuses on a diversified multi-asset portfolio including:

- **US Equities**: SPY (S&P 500)
- **International Equities**: VGK (European), VWO (Emerging Markets)
- **Fixed Income**: IEF (7-10Y Treasuries), TLT (20+Y Treasuries), LQD (Investment Grade), HYG (High Yield), TIP (TIPS)
- **Commodities**: DBC (Commodity Index)

### Return Calculation

Monthly log returns are calculated as:

```
r_t = ln(P_t / P_{t-1})
```

Excess returns are computed by subtracting the risk-free rate (3-month Treasury):

```
r^e_t = r_t - r_f,t
```

### Prior Expected Returns

We use BlackRock's 10-year Capital Market Assumptions as equilibrium priors. These represent institutional consensus on long-term expected returns and provide a more robust starting point than historical averages or CAPM estimates.

## Factor Model Construction

### Fama-French Five-Factor Model

We use the Fama-French five-factor model as the foundation:

- **Mkt-RF**: Market risk premium
- **SMB**: Size factor (Small Minus Big)
- **HML**: Value factor (High Minus Low book-to-market)
- **RMW**: Profitability factor (Robust Minus Weak)
- **CMA**: Investment factor (Conservative Minus Aggressive)

### Custom Factors

To better capture fixed income and commodity risks, we construct three custom factors:

#### 1. Term Factor (TERM)

Captures interest rate duration risk:

```
TERM_t = r_{TLT,t} - r_{IEF,t}
```

Where TLT is 20+ year Treasuries and IEF is 7-10 year Treasuries.

#### 2. Credit Factor (CREDIT)

Captures credit spread risk:

```
CREDIT_t = r_{HYG,t} - r_{LQD,t}
```

Where HYG is high yield and LQD is investment grade corporate bonds.

#### 3. Commodity Factor (COMMODITY)

Captures commodity-specific risk:

```
COMMODITY_t = r_{DBC,t}
```

### Factor Exposure Estimation

For each asset *i*, we estimate factor exposures via time-series regression:

```
r^e_{i,t} = α_i + β'_i F_t + ε_{i,t}
```

Where:
- r^e_{i,t}: Excess return of asset i at time t
- α_i: Asset-specific alpha (intercept)
- β_i: Vector of factor exposures (betas)
- F_t: Vector of factor returns at time t
- ε_{i,t}: Idiosyncratic (asset-specific) return

## Covariance Estimation

### Factor Model Covariance

The covariance matrix is decomposed into systematic and idiosyncratic components:

```
Σ = B F B' + D
```

Where:
- B: Matrix of factor exposures (n_assets × n_factors)
- F: Factor covariance matrix (n_factors × n_factors)
- D: Diagonal matrix of idiosyncratic variances

This approach:
1. Reduces the number of parameters to estimate
2. Provides more stable estimates by imposing structure
3. Captures common risk factors explicitly

### Ledoit-Wolf Shrinkage

To further improve covariance estimation, we apply Ledoit-Wolf shrinkage:

```
Σ_shrunk = δ * S + (1 - δ) * Σ_target
```

Where:
- S: Sample covariance matrix
- Σ_target: Structured target matrix (constant correlation model)
- δ: Optimal shrinkage intensity (data-driven)

Benefits:
- Reduces estimation error
- Improves out-of-sample performance
- Automatically determines optimal shrinkage intensity

## Black-Litterman Model

### The Master Formula

The posterior expected returns combine the prior (equilibrium) with investor views:

```
μ_BL = [(τΣ)^{-1} + P'Ω^{-1}P]^{-1} [(τΣ)^{-1}π + P'Ω^{-1}q]
```

Components:
- π: Prior expected returns (from CMA)
- Σ: Covariance matrix
- τ: Uncertainty in prior (typically 0.01-0.05)
- P: Matrix mapping views to assets
- q: Vector of view returns
- Ω: Uncertainty in views (diagonal matrix)

### Posterior Covariance

The posterior covariance accounts for both prior and view uncertainty:

```
Σ_BL = [(τΣ)^{-1} + P'Ω^{-1}P]^{-1} + Σ
```

### View Incorporation

#### Absolute Views

"Asset A will return X%"

P matrix has a single 1 in the row for asset A.

#### Relative Views

"Asset A will outperform Asset B by X%"

P matrix has 1 for asset A and -1 for asset B in the same row.

### View Confidence

Higher confidence → Lower variance in Ω → More weight on views
Lower confidence → Higher variance in Ω → More weight on prior

The uncertainty for view i is typically:

```
Ω_{ii} = τ * P_i Σ P'_i / confidence_i
```

## Portfolio Optimization

### Mean-Variance Optimization

Maximize risk-adjusted returns:

```
max_w: μ'w - (λ/2)w'Σw

subject to:
  w'1 = 1      (budget constraint)
  w ≥ 0        (long-only)
  w ≤ w_max    (position limits)
```

Where λ is the risk aversion parameter.

### Maximum Sharpe Ratio

Maximize:

```
SR = (μ - r_f) / σ = (μ'w - r_f) / √(w'Σw)
```

This is reformulated as a convex optimization problem using the transformation y = w/κ.

### Minimum Variance

Minimize portfolio variance without considering returns:

```
min_w: w'Σw

subject to:
  w'1 = 1
  w ≥ 0
```

### Risk Parity

Allocate such that each asset contributes equally to portfolio risk:

```
w_i * (Σw)_i = 1/n * w'Σw   for all i
```

This ensures diversification by risk contribution rather than capital allocation.

## Backtesting

### Rolling Window Approach

1. Use historical window (e.g., 60 months) to estimate parameters
2. Optimize portfolio weights
3. Hold positions for rebalancing period (e.g., 1 month)
4. Calculate returns and transaction costs
5. Roll window forward and repeat

### Transaction Costs

Transaction costs are modeled as:

```
TC_t = c * ∑_i |w_{i,t} - w_{i,t-1}|
```

Where:
- c: Transaction cost rate (e.g., 10 bps)
- The sum represents total turnover

### Performance Metrics

#### Sharpe Ratio

```
SR = (R_p - R_f) / σ_p
```

Risk-adjusted excess return.

#### Sortino Ratio

```
Sortino = (R_p - R_f) / σ_downside
```

Similar to Sharpe but penalizes only downside volatility.

#### Maximum Drawdown

```
MDD = max_t [(Peak_t - Value_t) / Peak_t]
```

Largest peak-to-trough decline.

#### Calmar Ratio

```
Calmar = Annual_Return / |MDD|
```

Return per unit of maximum drawdown.

## References

1. Black, F., & Litterman, R. (1992). "Global Portfolio Optimization". *Financial Analysts Journal*, 48(5), 28-43.

2. He, G., & Litterman, R. (1999). "The Intuition Behind Black-Litterman Model Portfolios". *Goldman Sachs Quantitative Resources Group*.

3. Fama, E. F., & French, K. R. (2015). "A Five-Factor Asset Pricing Model". *Journal of Financial Economics*, 116(1), 1-22.

4. Ledoit, O., & Wolf, M. (2004). "Honey, I Shrunk the Sample Covariance Matrix". *The Journal of Portfolio Management*, 30(4), 110-119.

5. Idzorek, T. M. (2005). "A Step-by-Step Guide to the Black-Litterman Model". *Ibbotson Associates*.

6. Meucci, A. (2010). "The Black-Litterman Approach: Original Model and Extensions". *The Encyclopedia of Quantitative Finance*.
