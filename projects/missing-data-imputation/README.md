## Missing Data & Imputation (Breast Cancer Wisconsin)

A workflow that profiles missingness, compares imputation strategies, and evaluates regression models on the Breast Cancer Wisconsin dataset.
The dataset and its description are available [here](https://archive.ics.uci.edu/dataset/15/breast+cancer+wisconsin+original).

## Problem
The dataset contains missing values ("?") in one feature. The goal is to:
- quantify missingness,
- compare imputation approaches, and
- assess how imputation choices affect model fit.

## Solution
The script:
- visualizes missingness with `visdat`,
- performs mean imputation for a baseline,
- builds regression models to impute missing values,
- evaluates models with R-squared and adjusted R-squared, and
- applies regression-based imputation with perturbation with MICE/PMM (predictive mean matching)


## Highlights
- Missingness profiling and exploratory visualization.
- Multiple imputation strategies (mean, regression, MICE).
- Model comparison with explicit train/test split and fit metrics.
