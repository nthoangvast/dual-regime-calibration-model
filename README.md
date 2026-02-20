# Dual-Regime RGB Calibration Model for NH₄⁺ and NO₂⁻

This repository provides the complete source codes and datasets used in the development, validation, and deployment of a unified dual-regime calibration model for quantitative determination of ammonium (NH₄⁺) and nitrite (NO₂⁻) ions using smartphone-based RGB colorimetric sensing.

The proposed approach formulates the calibration as a segmented linear regression using a dummy-variable framework, enabling simultaneous representation of low- and high-concentration regimes within a single ordinary least squares (OLS) regression model. This strategy explicitly reconciles trace-level sensitivity with wide-range quantitative accuracy and ensures continuity and parameter coherence across concentration regimes.

## Overview of the Computational Workflow

The modeling and validation pipeline consists of three independent and sequential stages:

1. **Generalization-optimal breakpoint determination (Script S1)**  
   The concentration breakpoint separating low- and high-concentration regimes is objectively determined for each target ion by minimizing prediction error on independent external test sets.

2. **Unified dual-regime calibration model construction (Script S2)**  
   Using the optimized breakpoint, a single segmented linear regression model is constructed via a dummy-variable approach. The model yields explicit analytical expressions for each regime while being estimated as a unified OLS problem.

3. **Advanced statistical validation (Script S3)**  
   Model robustness and reliability are assessed through goodness-of-fit metrics, external test-set evaluation, cross-validated Q² statistics, regression significance testing, and residual diagnostics.

## Repository Structure
/Code
Script_S1_1_Generalization-optimal-break-point-NH4+.py
Script_S1_2_Generalization-optimal-break-point-NO2-.py
Script_S2_Dual-regime-calibration-model-for-NH4-and-NO2.py
Script_S3_1_Statistical-validation-NH4.py
Script_S3_2_Statistical-validation-NO2.py

/Data
NH4_training.xlsx
NH4_test_L1.xlsx
NH4_test_L2.xlsx
NH4_test_L3.xlsx
NO2_training.xlsx
NO2_test_L1.xlsx
NO2_test_L2.xlsx
NO2_test_L3.xlsx

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

The source codes require **Python 3.x** and the following libraries:

- pandas (data handling)
- numpy (numerical operations)
- scikit-learn (modeling and performance metrics)
- statsmodels (OLS regression and statistical inference)
- matplotlib (visualization)
- openpyxl (Excel file support)
  
All dependencies can be installed using:
pip3 install -r requirements.txt

## Citation

If you use this code or data in your work, please cite the associated manuscrip
