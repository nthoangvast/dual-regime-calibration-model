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
#Detect generalization optimal break-point for ion NH4+
#==============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
#-----------------------------------------------------------------------------
#Data configuration
#-----------------------------------------------------------------------------
TRAIN_FILE = 'NH4-training.xlsx'
TEST_FILES = ['NH4-test-L1.xlsx', 'NH4-test-L2.xlsx', 'NH4-test-L3.xlsx'] 

def process_data(file_path):
    df = pd.read_excel(file_path)
    df.columns = ['C', 'R', 'G', 'B']
    df['G_R'] = df['G'] / df['R']
    df['B_G'] = df['B'] / df['G']
    df['B_R'] = df['B'] / df['R']
    return df

df_train = process_data(TRAIN_FILE)
test_dfs = [process_data(f) for f in TEST_FILES]
#-----------------------------------------------------------------------------
#Grid search optimization
#-----------------------------------------------------------------------------
candidate_points = sorted(df_train['C'].unique())[1:-1]
results = []

for cp in candidate_points:
    #Determine Threshold based on candidate concentrations
    threshold_gr = df_train[df_train['C'] == cp]['G_R'].mean()
    
    #Prepare training data with dummy variable D
    df_t = df_train.copy()
    df_t['D'] = (df_t['G_R'] > threshold_gr).astype(int)
    features = ['G_R', 'D', 'D_x_GR', 'D_x_BG', 'D_x_BR']
    for feat in ['G_R', 'B_G', 'B_R']:
        df_t[f'D_x_{feat.replace("/", "_")}'] = df_t['D'] * df_t[feat]
        
    X_train = df_t[['G_R', 'D', 'D_x_G_R', 'D_x_B_G', 'D_x_B_R']]
    y_train = df_t['C']
    
    #Training model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    #Calculate Training RMSE (Root Mean Square Error)
    train_pred = model.predict(X_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    
    #Calculate the MAE test (average of all 3 test sets)
    total_test_mae = 0
    for df_test in test_dfs:
        df_temp = df_test.copy()
        df_temp['D'] = (df_temp['G_R'] > threshold_gr).astype(int)
        df_temp['D_x_G_R'] = df_temp['D'] * df_temp['G_R']
        df_temp['D_x_B_G'] = df_temp['D'] * df_temp['B_G']
        df_temp['D_x_B_R'] = df_temp['D'] * df_temp['B_R']
        
        X_test = df_temp[['G_R', 'D', 'D_x_G_R', 'D_x_B_G', 'D_x_B_R']]
        test_pred = model.predict(X_test)
        total_test_mae += mean_absolute_error(df_temp['C'], test_pred)
    
    avg_test_mae = total_test_mae / len(TEST_FILES)
    
    #Save the result and the largest coefficient
    max_coeff = np.max(np.abs(model.coef_))
    
    results.append({
        'cp': cp,
        'threshold': threshold_gr,
        'train_rmse': train_rmse,
        'test_mae': avg_test_mae,
        'stability': max_coeff
    })
#------------------------------------------------------------------------------------------------------------
#Select the optimal break-point, we choose the point where the training RMSE is low and test MAE is lowest.
#-----------------------------------------------------------------------------------------------------------
best_res = min(results, key=lambda x: x['test_mae'])

print(f"{'break-point (ppm)':<10} | {'Training RMSE':<12} | {'Testing MAE':<12} | {'Max Coeff (Stability)'}")
print("-" * 65)
for r in results:
    mark = " <-- Optimal break-point" if r['cp'] == best_res['cp'] else ""
    print(f"{r['cp']:<10.2f} | {r['train_rmse']:<12.5f} | {r['test_mae']:<12.5f} | {r['stability']:<15.2f} {mark}")

#-------------------------------------------------------
#Plotting
#-------------------------------------------------------
pts = [r['cp'] for r in results]
train_err = [r['train_rmse'] for r in results]
test_err = [r['test_mae'] for r in results]

plt.figure(figsize=(10, 5))
plt.plot(pts, train_err, 'b-o', label='Training RMSE')
plt.plot(pts, test_err, 'r-s', label='Testing MAE')
plt.axvline(x=best_res['cp'], color='green', linestyle='--', label=f'Optimal break-point: {best_res["cp"]} ppm')
plt.xlabel('Concentration break-point (ppm)')
plt.ylabel('Error (ppm)')
plt.title("Generalization-optimal breakpoint determination for NH$_4^+$")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
#-------------------------------------------------------
#Export data to replotting
#-------------------------------------------------------

df_out = pd.DataFrame(results)

#Keep the columns correctly aligned for drawing.
df_out = df_out[['cp', 'train_rmse', 'test_mae']]

df_out = df_out.rename(columns={
    'cp': 'Break_point_ppm',
    'train_rmse': 'Training_RMSE_ppm',
    'test_mae': 'Testing_MAE_ppm'
})
#-----------------------------------------------------------------------------
#Export .xlsx data file
#-----------------------------------------------------------------------------
OUTPUT_FILE = 'Generalization_optimal_breakpoint_NH4.xlsx'

df_out.to_excel(OUTPUT_FILE, index=False)

print(f"Exported validation data to: {OUTPUT_FILE}")
#-----------------------------------------------------------------------------
#END CODE
#-----------------------------------------------------------------------------



