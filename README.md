# Source code for paper entitled "A New Portable Colorimetric Sensing Device Prototype Using Machine-Learning-Assisted Dual-Regime Calibration Model for Cloud-Integrated Monitoring of Environmental Water Contaminants"
[![ACS Analytical Chemistry](https://img.shields.io/badge/ACS-Analytical%20Chemistry-orange.svg)](https://pubs.acs.org/doi/10.1021/acs.analchem.6c01885)
[![DOI:10.1021/acs.analchem.6c01885](https://img.shields.io/badge/DOI-10.1021%2Facs.analchem.6c01885-blue.svg)](https://pubs.acs.org/doi/10.1021/acs.analchem.6c01885)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

This repository provides the complete source codes and datasets used in the development, validation, and deployment of a unified dual-regime calibration model for quantitative determination of ammonium ($\text{NH}_4^+$) and nitrite ($\text{NO}_2^-$) ions using smartphone-based RGB colorimetric sensing.

The proposed approach formulates the calibration as a segmented linear regression using a dummy-variable framework, enabling simultaneous representation of low- and high-concentration regimes within a single ordinary least squares (OLS) regression model. This strategy explicitly reconciles trace-level sensitivity with wide-range quantitative accuracy and ensures continuity and parameter coherence across concentration regimes.

---

## Overview of the Computational Workflow

The modeling and validation pipeline consists of three independent and sequential stages:

1. **Generalization-optimal breakpoint determination (Script S1)**
   The concentration breakpoint separating low- and high-concentration regimes is objectively determined for each target ion by minimizing prediction error on independent external test sets.
2. **Unified dual-regime calibration model construction (Script S2)**
   Using the optimized breakpoint, a single segmented linear regression model is constructed via a dummy-variable approach. The model yields explicit analytical expressions for each regime while being estimated as a unified OLS problem.
3. **Advanced statistical validation (Script S3)**
   Model robustness and reliability are assessed through goodness-of-fit metrics, external test-set evaluation, cross-validated $Q^2$ statistics, regression significance testing, and residual diagnostics.

---

## 📂 Repository Structure

```text
├── Code/
│   ├── Script_S1_1_Generalization-optimal-break-point-NH4+.py
│   ├── Script_S1_2_Generalization-optimal-break-point-NO2-.py
│   ├── Script_S2_Dual-regime-calibration-model-for-NH4-and-NO2.py
│   ├── Script_S3_1_Statistical-validation-NH4.py
│   └── Script_S3_2_Statistical-validation-NO2.py
├── Data/
│   ├── NH4_training.xlsx
│   ├── NH4_test_L1.xlsx
│   ├── NH4_test_L2.xlsx
│   ├── NH4_test_L3.xlsx
│   ├── NO2_training.xlsx
│   ├── NO2_test_L1.xlsx
│   ├── NO2_test_L2.xlsx
│   └── NO2_test_L3.xlsx
├── requirements.txt
└── README.md
```
## Data Description
- **Training datasets**: Used to estimate the dual-regime calibration model parameters.
- **Independent test datasets (L1–L3)**: Used exclusively for external validation to evaluate generalization performance and robustness.

## Performance Metrics

Model performance is evaluated using:
- Coefficient of determination (R²)
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Cross-validated Q² statistics

Limits of detection (LOD) and quantification (LOQ) are estimated using a blank-based approach in accordance with ICH Q2(R1), based on the sensitivity of the low-concentration regime.

## Software Requirements
Core Dependencies
The source codes require **Python 3.x** and the following libraries:

- pandas (data handling)
- numpy (numerical operations)
- scikit-learn (modeling and performance metrics)
- statsmodels (OLS regression and statistical inference)
- matplotlib (visualization)
- openpyxl (Excel file support)
## Installation
Clone this repository and install all dependencies via **pip**:<br>
git clone https://github.com/nthoangvast/dual-regime-calibration-model.git<br>
cd dual-regime-calibration-model.git<br>
pip3 install -r requirements.txt<br>

## Citation

If you use this code, data, or methodological framework in your research, please cite our paper published in Analytical Chemistry:

*Dual-Regime RGB Calibration Model for Unified Quantitative Determination of Ammonium and Nitrite Ions Using Smartphone-Based Colorimetric Sensing. Anal. Chem. 2026. DOI: 10.1021/acs.analchem.6c01885*
