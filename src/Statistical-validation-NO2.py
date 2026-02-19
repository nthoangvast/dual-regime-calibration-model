# -*- coding: utf-8 -*-
# Copyright [2026] [Dr. Thanh Hoang Nguyen]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#==============================================================================
#Dual-regime calibration model based on segmented linear regression with dummy variables and independent validation (NH4⁺, NO2⁻).
#***Required Python packages:
# numpy
# pandas
# scikit-learn
# matplotlib
# openpyxl (for Excel I/O via pandas)
#-----------------------------------------------------------------------------
#Advanced statistical validation for ion NO2-
#==============================================================================

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import r2_score

#-----------------------------------------------------------------------------
#Data configuration
#-----------------------------------------------------------------------------
CALIBRATION_FILE = 'NO2-training.xlsx'
#at optimal concentration break-point (0.8 ppm for NO2-)
THRESHOLD_BG = 1.6419 

def advanced_validation_no2():
    print("=" * 80)
    print("Advanced statistical validation for ion NO2-")
    print("=" * 80)

    try:
        #Data processing
        df = pd.read_excel(CALIBRATION_FILE)
        df.columns = ['C', 'R', 'G', 'B']
        #Calculate ratio variables
        df['G_R'] = df['G'] / df['R']
        df['B_G'] = df['B'] / df['G']
        df['B_R'] = df['B'] / df['R']

        #Creating dummy variables (based on B/G)
        df['D'] = (df['B_G'] > THRESHOLD_BG).astype(int)
        
        #Creating interaction variables
        df['D_x_BG'] = df['D'] * df['B_G']
        df['D_x_GR'] = df['D'] * df['G_R']
        df['D_x_BR'] = df['D'] * df['B_R']

        #List of independent variables (x) and dependent variable (y)
        features = ['B_G', 'D', 'D_x_BG', 'D_x_GR', 'D_x_BR']
        X = df[features]
        y = df['C']

        #IN-DEPTH REGRESSION ANALYSIS (Using Statsmodels)
        X_with_const = sm.add_constant(X)
        ols_model = sm.OLS(y, X_with_const).fit()

        print("\nHypothesis Test Results (P-Values):")
        print(ols_model.summary2().tables[1][['Coef.', 'Std.Err.', 't', 'P>|t|']])
 	#If P>|t| of the variables D_x_... < 0.05, adding dummy variables is scientifically meaningful.

        print("\nMODEL SELECTION INDEX:")
        print(f" - R-squared (R²):         {ols_model.rsquared:.6f}")
        print(f" - Adjusted R-squared:     {ols_model.rsquared_adj:.6f}")
        print(f" - AIC (Akaike Info):      {ols_model.aic:.2f}")
        print(f" - BIC (Bayesian Info):    {ols_model.bic:.2f}")
        print(f" - BIC (Bayesian Info):    {ols_model.bic:.2f}")
        #The closer Adj R² is to R², the less redundant the variable. A lower AIC/BIC ratio is better. 
        
        #CHECK OVERFITTING USING CROSS-VALIDATION (Q-squared)
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        q2_scores = cross_val_score(LinearRegression(), X, y, cv=cv, scoring='r2')
        q2_mean = np.mean(q2_scores)

        print("\nCHECK OVERFITTING:")
        print(f" - Q-squared (Cross-validated R²): {q2_mean:.6f}")
        print(f" - Delta (R² - Q²):               {ols_model.rsquared - q2_mean:.6f}")
   	#If Delta < 0.05, the model is stable
   	
        #plot the residual analysis
        y_pred = ols_model.predict(X_with_const)
        residuals = y - y_pred

        plt.figure(figsize=(12, 5))

        #Check for error homogeneity: Residuals vs Predicted
        plt.subplot(1, 2, 1)
        plt.scatter(y_pred, residuals, color='purple', alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.title("Residuals vs Predicted Values (NO2-)")
        plt.xlabel("Predicted Concentration (ppm)")
        plt.ylabel("Residuals")

        #Check for normal distribution: Distribution of Residuals
        plt.subplot(1, 2, 2)
        sns.histplot(residuals, kde=True, color='blue')
        plt.title("Distribution of Residuals (NO2)")
        plt.xlabel("Residual Value")

        plt.tight_layout()
        plt.show()

        print("\n" + "=" * 80)
        print("The analysis process is complete!")

    except Exception as e:
        print(f"Error: {e}")
#-----------------------------------------------------------------------------
#MAIN
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    advanced_validation_no2()

#==============================================================================    
#END CODE
#============================================================================== 
