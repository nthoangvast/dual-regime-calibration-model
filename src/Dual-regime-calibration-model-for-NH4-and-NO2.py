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
#==============================================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# -------------------------------------------------------
# Global rounding to 4 decimal
# -------------------------------------------------------
ROUND_N = 4
r4 = lambda x: np.round(x, ROUND_N)
# -------------------------------------------------------
# Ion configuration
# -------------------------------------------------------
ION_CONFIG = {

    "NH4": {
        "train_file": "NH4-training.xlsx",
        "test_files": [
            "NH4-test-L1.xlsx",
            "NH4-test-L2.xlsx",
            "NH4-test-L3.xlsx"
        ],
        "threshold_value": 2.3183,
        "signal": lambda df: df["G"] / df["R"],
        "extra_terms": lambda df: {
            "B_G": df["B"] / df["G"],
            "B_R": df["B"] / df["R"]
        }
    },

    "NO2": {
        "train_file": "NO2-training.xlsx",
        "test_files": [
            "NO2-test-L1.xlsx",
            "NO2-test-L2.xlsx",
            "NO2-test-L3.xlsx"
        ],
        "threshold_value": 1.6419,
        "signal": lambda df: df["B"] / df["G"],
        "extra_terms": lambda df: {
            "G_R": df["G"] / df["R"],
            "B_R": df["B"] / df["R"]
        }
    }
}

# -------------------------------------------------------
# Data loading from .xlsx file (4 column)
# -------------------------------------------------------
def load_data(fname):
    df = pd.read_excel(fname)
    df.columns = ["C", "R", "G", "B"]
    return df

#-------------------------------------------------------
# Feature construction
#-------------------------------------------------------

def build_features(df, cfg):
    C = df["C"].values
    signal = cfg["signal"](df).values
    D = (signal > cfg["threshold_value"]).astype(int)

    X = [signal, D, D * signal]
    names = ["Signal", "D", "D×Signal"]

    extras = cfg["extra_terms"](df)
    for k, v in extras.items():
        X.append(D * v.values)
        names.append(f"D×{k}")

    return np.column_stack(X), C, names


#-------------------------------------------------------
# MODEL TRAINING
#-------------------------------------------------------

def train_model(df_train, cfg):
    X, y, names = build_features(df_train, cfg)
    model = LinearRegression().fit(X, y)
    y_pred = model.predict(X)

    r2 = r4(r2_score(y, y_pred))
    mae = r4(mean_absolute_error(y, y_pred))
    rmse = r4(np.sqrt(mean_squared_error(y, y_pred)))

    print(f"Training  -> R²={r2}, MAE={mae}, RMSE={rmse}")

    print("\nLow-regime equation:")
    print(f"C = {r4(model.intercept_)} + {r4(model.coef_[0])}·Signal")

    print("\nHigh-regime equation:")
    terms = [f"{r4(model.coef_[i]):+}·{names[i]}" for i in range(len(names))]
    print("C = " + f"{r4(model.intercept_)} " + " ".join(terms))

    return model, names


#-------------------------------------------------------
# MODEL EVALUATION
#-------------------------------------------------------

def evaluate_model(model, df, cfg):
    X, y, _ = build_features(df, cfg)
    y_pred = np.maximum(0, model.predict(X))

    return (
        r4(r2_score(y, y_pred)),
        r4(mean_absolute_error(y, y_pred)),
        r4(np.sqrt(mean_squared_error(y, y_pred))),
        r4(y),
        r4(y_pred)
    )


#-------------------------------------------------------
# Export data to replotting
#-------------------------------------------------------

def export_origin_data(df, model, cfg, ion, tag, out_dir):
    _, _, _, y, y_pred = evaluate_model(model, df, cfg)

    out = df.copy()
    out["Predicted_C"] = y_pred
    out["Residual"] = r4(y - y_pred)

    fname = f"{ion}_{tag}_OriginData.xlsx"
    out.to_excel(os.path.join(out_dir, fname), index=False)


#-------------------------------------------------------
# Export figure result 
#-------------------------------------------------------

def plot_combined_performance(df_train, model, cfg, ion, fig_dir):

    _, _, _, ytr, ytr_pred = evaluate_model(model, df_train, cfg)

    plt.figure(figsize=(10, 7))

    #Training
    plt.scatter(
        ytr, ytr_pred,
        s=90,
        color="blue",
        marker="o",
        label=f"Training (R²={r4(r2_score(ytr, ytr_pred))})"
    )

    TEST_STYLE = {
        "L1": {"color": "red",    "marker": "D"}, #Diamond
        "L2": {"color": "gold",   "marker": "*"}, #Star
        "L3": {"color": "purple", "marker": "^"} #triangle_up
    }

    max_C = ytr.max()

    #Test sets
    for f in cfg["test_files"]:
        df_test = load_data(f)
        r2, _, _, yt, yt_pred = evaluate_model(model, df_test, cfg)

        level = f.split("-")[-1].replace(".xlsx", "")
        style = TEST_STYLE[level]

        plt.scatter(
            yt, yt_pred,
            facecolors="none",
            edgecolors=style["color"],
            marker=style["marker"],
            s=130,
            linewidths=1.5,
            label=f"Test {level} (R²={r4(r2)})"
        )

        max_C = max(max_C, yt.max())

    #Ideal line y=x
    plt.plot(
        [0, max_C * 1.1],
        [0, max_C * 1.1],
        "r--",
        linewidth=1.2,
        label="Ideal line (y = x)"
    )

    plt.xlabel("Actual concentration (ppm)")
    plt.ylabel("Predicted concentration (ppm)")
    plt.title(f"{ion} – Dual-regime calibration model")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(fig_dir, f"{ion}_dual-regime-calibration-model.png"),
        dpi=600
    )
    plt.close()


#------------------------------------------------------------------------------
#Calculating the LOD & LOQ value form 11 blank samples by ICH Q2(R1) Guideline: Validation of Analytical Procedures: Text and Methodology
#------------------------------------------------------------------------------

def compute_lod_loq_hybrid(ion):

    if ion == "NH4":
        blank = np.array([1.7245,1.7182,1.7155,1.7195,1.7224,
                          1.7098,1.7099,1.7109,1.7182,1.7150,1.7017])
        df = load_data("NH4-training.xlsx")
        signal = df["G"]/df["R"]
        D = (signal > 2.3183).astype(int)
        X = np.column_stack([signal, D, D*signal,
                             D*(df["B"]/df["G"]),
                             D*(df["B"]/df["R"])])
    else:
        blank = np.array([1.1002,1.1008,1.0994,1.1027,1.1052,
                          1.1015,1.1019,1.1040,1.1008,1.1036,1.1030])
        df = load_data("NO2-training.xlsx")
        signal = df["B"]/df["G"]
        D = (signal > 1.6419).astype(int)
        X = np.column_stack([signal, D, D*signal,
                             D*(df["G"]/df["R"]),
                             D*(df["B"]/df["R"])])

    model = LinearRegression().fit(X, df["C"])
    slope = model.coef_[0]
    sigma = np.std(blank, ddof=1)

    return r4(3.3 * sigma * slope), r4(10 * sigma * slope)


#-------------------------------------------------------
#Export summary data
#-------------------------------------------------------

def export_summary_results(ion, cfg, model, df_train, tab_dir):

    rows = []

    r2, mae, rmse, _, _ = evaluate_model(model, df_train, cfg)
    lod, loq = compute_lod_loq_hybrid(ion)

    rows.append(["Training", r2, mae, rmse, lod, loq])

    for f in cfg["test_files"]:
        df_test = load_data(f)
        r2, mae, rmse, _, _ = evaluate_model(model, df_test, cfg)
        level = f.split("-")[-1].replace(".xlsx", "")
        rows.append([f"Test {level}", r2, mae, rmse, None, None])

    df = pd.DataFrame(
        rows,
        columns=["Dataset", "R2", "MAE", "RMSE", "LOD (ppm)", "LOQ (ppm)"]
    )

    df.to_excel(os.path.join(tab_dir, f"{ion}_Model_Summary.xlsx"), index=False)


#------------------------------------------------------------------------------
# Automated workflow to train, evaluate, and export results for a specific ion.
#------------------------------------------------------------------------------

def run_pipeline(ion):

    print("=" * 70)
    print(f"Dual-regime calibration model for {ion}")
    print("=" * 70)
    #Setup
    cfg = ION_CONFIG[ion]
    #make directories for output results
    out_root = f"outputs/{ion}"
    fig_dir = os.path.join(out_root, "figures")
    tab_dir = os.path.join(out_root, "tables")

    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(tab_dir, exist_ok=True)
    #Model Training
    df_train = load_data(cfg["train_file"])
    model, _ = train_model(df_train, cfg)

    export_origin_data(df_train, model, cfg, ion, "Train", tab_dir)
     #Evaluation & Testing
    for f in cfg["test_files"]:
        df_test = load_data(f)
        tag = os.path.splitext(os.path.basename(f))[0]
        r2, mae, _, _, _ = evaluate_model(model, df_test, cfg)
        print(f"Test {tag} -> R²={r2}, MAE={mae}")
        #Data Export
        export_origin_data(df_test, model, cfg, ion, tag, tab_dir)
    plot_combined_performance(df_train, model, cfg, ion, fig_dir)  #Visualization
    export_summary_results(ion, cfg, model, df_train, tab_dir)  #Export summary data 


#-------------------------------------------------------
#MAIN
#-------------------------------------------------------

if __name__ == "__main__":
    run_pipeline("NH4")
    run_pipeline("NO2")
# =========================================================
# END_CODE
# =========================================================
