"""
api.py

TerraScore Climate ML API
- Train model
- Predict drought risk
- Generate farmer credit score
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# ------------------ IMPORTS ------------------
from backend.datacollection.climate import get_climate_data
from backend.datacollection.ndvi import get_ndvi_data
from backend.datacollection.lst import get_lst_data
from preprocessing.cleaning import clean_climate_data
from preprocessing.feature_engineering import add_features
from models.drought_model import train_model, load_model, predict

# ------------------ ENV ------------------
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "drought_xgboost.joblib")

app = FastAPI(title="TerraScore Climate ML API")


# =====================================================
# ------------------ REQUEST MODELS --------------------
# =====================================================

class BaseRequest(BaseModel):
    lat: float
    lon: float
    start_date: str
    end_date: str

    @field_validator("start_date", "end_date")
    def validate_date(cls, v):
        for fmt in ("%Y-%m-%d", "%Y%m%d"):
            try:
                return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
            except:
                continue
        raise ValueError("Invalid date format")


class TrainRequest(BaseRequest):
    pass


class PredictRequest(BaseRequest):
    pass


# =====================================================
# ------------------ UTIL FUNCTIONS --------------------
# =====================================================

def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")


def standardize_datetime(df):
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.floor("s")
    return df


def clean_merged_columns(df, lat, lon):
    if 'ndvi_x' in df.columns:
        df['ndvi'] = df['ndvi_x']
    elif 'ndvi_y' in df.columns:
        df['ndvi'] = df['ndvi_y']

    if 'lst_x' in df.columns:
        df['lst'] = df['lst_x']
    elif 'lst_y' in df.columns:
        df['lst'] = df['lst_y']

    df = df[[c for c in df.columns if not c.endswith('_x') and not c.endswith('_y')]].copy()

    df['lat'] = lat
    df['lon'] = lon

    return df


# =====================================================
# ------------------ CORE PIPELINE ---------------------
# =====================================================

def prepare_dataset(lat, lon, start_date, end_date):

    df_climate = get_climate_data(lat, lon, format_date(start_date), format_date(end_date))
    df_ndvi = get_ndvi_data(lat, lon, start_date, end_date)
    df_lst = get_lst_data(lat, lon, start_date, end_date)

    # -------- Fallbacks --------
    if df_ndvi.empty:
        df_ndvi = pd.DataFrame({
            "date": df_climate["date"],
            "ndvi": df_climate["PRECTOTCORR"].rolling(7, min_periods=1).mean() / 10
        })

    if df_lst.empty:
        df_lst = pd.DataFrame({
            "date": df_climate["date"],
            "lst": [25] * len(df_climate)
        })

    # -------- Standardize --------
    df_climate = standardize_datetime(df_climate).sort_values("date")
    df_ndvi = standardize_datetime(df_ndvi).sort_values("date")
    df_lst = standardize_datetime(df_lst).sort_values("date")

    # -------- Merge --------
    df = pd.merge_asof(df_climate, df_ndvi, on="date", direction="nearest")
    df = pd.merge_asof(df, df_lst, on="date", direction="nearest")

    df = clean_merged_columns(df, lat, lon)

    # -------- Clean --------
    for col in ["ndvi", "lst"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].interpolate().bfill().ffill()

    df_clean = clean_climate_data(df)
    df_feats = add_features(df_clean).bfill().ffill()

    return df, df_feats


# =====================================================
# ------------------ BUSINESS LOGIC --------------------
# =====================================================

def calculate_risk(pred, ndvi):
    if pred < 2 and ndvi > 0.6:
        return "Excellent"
    elif pred < 4:
        return "Moderate Risk"
    return "High Risk"


def calculate_credit_score(pred, ndvi, lst):
    ndvi_score = ndvi * 100
    drought_score = max(0, 100 - (pred * 20))
    lst_score = max(0, 100 - (lst * 2))

    return round((0.5 * ndvi_score) + (0.3 * drought_score) + (0.2 * lst_score), 2)


# =====================================================
# ------------------ ROUTES ----------------------------
# =====================================================

@app.get("/")
def read_root():
    return {"message": "Welcome to TerraScore Climate ML API"}


@app.post("/train")
def api_train(request: TrainRequest):
    try:
        if os.path.exists(MODEL_PATH):
            return {"message": "Model already trained. Delete file to retrain."}

        _, df_feats = prepare_dataset(
            request.lat, request.lon,
            request.start_date, request.end_date
        )

        _, metrics = train_model(df_feats, model_path=MODEL_PATH)

        return {"message": "Model trained successfully", "metrics": metrics}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
def api_predict(request: PredictRequest):
    try:
        model = load_model(MODEL_PATH)

        if model is None:
            raise HTTPException(status_code=400, detail="Model not found. Train first.")

        df, df_feats = prepare_dataset(
            request.lat, request.lon,
            request.start_date, request.end_date
        )

        if df_feats.empty:
            raise HTTPException(status_code=400, detail="Insufficient data")

        predictions = predict(model, df_feats)
        df_feats["predicted_drought_index"] = predictions
        latest = df_feats.iloc[-1]

        pred_val = float(latest["predicted_drought_index"])
        ndvi_val = float(latest["ndvi"])
        lst_val = float(latest["lst"])

        return {
            "date": latest["date"].strftime("%Y-%m-%d"),
            "lat": request.lat,
            "lon": request.lon,
            "predicted_drought_index": pred_val,
            "ndvi": ndvi_val,
            "lst": lst_val,
            "farmer_score": calculate_risk(pred_val, ndvi_val),
            "credit_score": calculate_credit_score(pred_val, ndvi_val, lst_val),

            "ndvi_trend": [
                {"date": r["date"].strftime("%Y-%m-%d"), "ndvi": float(r["ndvi"])}
                for _, r in df[["date", "ndvi"]].dropna().iterrows()
            ],
            "lst_trend": [
                {"date": r["date"].strftime("%Y-%m-%d"), "lst": float(r["lst"])}
                for _, r in df[["date", "lst"]].dropna().iterrows()
            ]
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))