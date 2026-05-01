"""
app.py

TerraScore Streamlit Dashboard
- Train Model
- Predict Drought
- Visualize NDVI & LST
- Credit Score Dashboard
"""

import streamlit as st
import matplotlib.pyplot as plt
import requests
import pandas as pd
import datetime
from dotenv import load_dotenv
import os

# =====================================================
# ------------------ CONFIG ----------------------------
# =====================================================

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="TerraScore AI", layout="wide")


# =====================================================
# ------------------ STYLING ---------------------------
# =====================================================

st.markdown("""
<style>
.main { background-color: #0e1117; }
.block-container { padding-top: 2rem; }

.stMetric {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    transition: 0.3s;
}

.stMetric:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px rgba(0,255,150,0.2);
}

h1, h2, h3 { color: #ffffff; }
</style>
""", unsafe_allow_html=True)


# =====================================================
# ------------------ HEADER ----------------------------
# =====================================================

st.markdown("""
<h1 style='text-align: center;'>🌍 TerraScore AI Dashboard</h1>
<p style='text-align: center; color: gray;'>Smart Climate Intelligence for Farmers</p>
""", unsafe_allow_html=True)


# =====================================================
# ------------------ SIDEBAR ---------------------------
# =====================================================

st.sidebar.header("📍 Configuration")

lat = st.sidebar.number_input("Latitude", value=28.4, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=77.0, format="%.4f")

st.sidebar.subheader("📅 Training Dates")
train_start = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
train_end = st.sidebar.date_input("End Date", datetime.date(2023, 12, 31))

st.sidebar.subheader("📅 Prediction Dates")
pred_start = st.sidebar.date_input("Prediction Start", datetime.date(2024, 1, 1))
pred_end = st.sidebar.date_input("Prediction End", datetime.date(2024, 1, 31))


# =====================================================
# ------------------ API FUNCTIONS ---------------------
# =====================================================

def call_train_api():
    payload = {
        "lat": lat,
        "lon": lon,
        "start_date": train_start.strftime("%Y%m%d"),
        "end_date": train_end.strftime("%Y%m%d")
    }
    return requests.post(f"{API_URL}/train", json=payload)


@st.cache_data(show_spinner=False)
def call_predict_api_cached(payload):
    return requests.post(f"{API_URL}/predict", json=payload).json()


# =====================================================
# ------------------ CHART FUNCTION --------------------
# =====================================================

def plot_trend(df, x_col, y_col, title, ylabel):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(df[x_col], df[y_col], marker='o', linewidth=2)

    ax.set_xticks(df[x_col][::max(1, len(df)//6)])
    plt.xticks(rotation=30)

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)

    st.pyplot(fig)


# =====================================================
# ------------------ MAIN LAYOUT -----------------------
# =====================================================

col1, col2 = st.columns(2)


# ================= TRAIN =================
with col1:
    st.subheader("⚙️ Model Training")

    if st.button("🚀 Train Model", use_container_width=True):
        with st.spinner("Training model..."):
            try:
                response = call_train_api()

                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Model trained successfully!")

                    if "metrics" in data:
                        m1, m2 = st.columns(2)
                        m1.metric("MSE", f"{data['metrics']['mse']:.4f}")
                        m2.metric("R² Score", f"{data['metrics']['r2']:.4f}")
                    else:
                        st.info(data["message"])

                else:
                    st.error(f"Error: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not running")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")


# ================= PREDICT =================
with col2:
    st.subheader("🌾 Drought Prediction")

    if st.button("🔍 Get Prediction", use_container_width=True):
        with st.spinner("🚀 Running AI model..."):
            try:
                payload = {
                    "lat": lat,
                    "lon": lon,
                    "start_date": pred_start.strftime("%Y-%m-%d"),
                    "end_date": pred_end.strftime("%Y-%m-%d")
                }

                data = call_predict_api_cached(payload)

                st.success("✅ Prediction generated!")

                # ---------------- RESULT ----------------
                st.subheader("📊 Result Overview")
                st.write(f"📅 Date: {data['date']}")

                c1, c2, c3, c4 = st.columns(4)

                c1.metric("🌡️ Drought", f"{data['predicted_drought_index']:.2f}")
                c2.metric("🌿 NDVI", f"{data['ndvi']:.3f}")
                c3.metric("🔥 LST", f"{data['lst']:.2f}")
                c4.metric("💳 Credit", f"{data['credit_score']:.2f}")

                # ---------------- RISK ----------------
                risk = data["farmer_score"]

                if "Excellent" in risk:
                    st.success("🟢 Excellent Conditions")
                elif "Moderate" in risk:
                    st.warning("🟡 Moderate Risk")
                else:
                    st.error("🔴 High Risk")

                st.markdown("---")

                # ---------------- BAR CHART ----------------
                chart_df = pd.DataFrame({
                    "Metric": ["Drought", "NDVI", "LST"],
                    "Value": [
                        data['predicted_drought_index'],
                        data['ndvi'],
                        data['lst']
                    ]
                })

                st.bar_chart(chart_df.set_index("Metric"))

                st.markdown("---")

                # ---------------- TRENDS ----------------
                colA, colB = st.columns(2)

                with colA:
                    st.subheader("🌿 NDVI Trend")
                    df = pd.DataFrame(data["ndvi_trend"])
                    df["date"] = pd.to_datetime(df["date"])
                    plot_trend(df, "date", "ndvi", "NDVI Trend", "NDVI")

                with colB:
                    st.subheader("🔥 LST Trend")
                    df = pd.DataFrame(data["lst_trend"])
                    df["date"] = pd.to_datetime(df["date"])
                    plot_trend(df, "date", "lst", "LST Trend", "°C")

                st.markdown("---")

                # ---------------- CREDIT ----------------
                st.subheader("💳 Farmer Credit Score")

                score = data["credit_score"]
                st.metric("Credit Score", f"{score}/100")
                st.progress(score / 100)

                if score > 75:
                    st.success("🟢 Low Risk Farmer")
                elif score > 50:
                    st.warning("🟡 Medium Risk")
                else:
                    st.error("🔴 High Risk")

            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not running")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")