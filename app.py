import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="Aadhaar Desert Dashboard IN", layout="wide")

st.title("🆔 Aadhaar Desert Dashboard IN 🇮🇳")
st.write("District-wise Demand Forecasting + Visual Insights ")

# ---------------- LOAD FILES ----------------
@st.cache_data
def load_monthly_data():
    df = pd.read_csv("Monthly_Demand_Dataset.csv")
    df["month"] = df["month"].astype(str)
    return df

@st.cache_resource
def load_model():
    return joblib.load("Demand_Prediction_Model.pkl")

monthly_df = load_monthly_data()
demand_model = load_model()

# Sort once
monthly_df = monthly_df.sort_values(["state", "district", "month"])

# ---------------- SIDEBAR ----------------
st.sidebar.header("📌 Aadhaar Desert Dashboard")
st.sidebar.write("✅ Auto-load district data → predict next month workload")

# ---------------- MAIN UI ----------------
st.subheader("📍 Predict using State + District selection")

# ✅ State dropdown
all_states = sorted(monthly_df["state"].dropna().unique().tolist())
selected_state = st.selectbox("Select State", all_states)

# ✅ District dropdown
state_data = monthly_df[monthly_df["state"] == selected_state]
all_districts = sorted(state_data["district"].dropna().unique().tolist())
selected_district = st.selectbox("Select District", all_districts)

# ✅ Selected district history
district_history = monthly_df[
    (monthly_df["state"] == selected_state) &
    (monthly_df["district"] == selected_district)
].sort_values("month")

if district_history.empty:
    st.error("❌ No data found for selected district.")
    st.stop()

# ✅ Latest record
latest_row = district_history.tail(1).iloc[0]
total_enroll = int(latest_row["total_enroll"])
total_updates = int(latest_row["total_updates"])
service_load = int(latest_row["service_load"])
last_month = latest_row["month"]

st.markdown("### ✅ Latest Available Data (Auto-loaded)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("State", selected_state)
c2.metric("District", selected_district)
c3.metric("Last Month", last_month)
c4.metric("Current Service Load", service_load)

st.write("📌 Latest record")
st.dataframe(district_history.tail(1), use_container_width=True)


# ✅ BUILD FEATURES FOR NEW MODEL

district_history = district_history.copy()
district_history["month_num"] = pd.to_datetime(district_history["month"]).dt.month

district_history["lag_1"] = district_history["service_load"].shift(1)
district_history["lag_2"] = district_history["service_load"].shift(2)
district_history["rolling_3_mean"] = (
    district_history["service_load"].shift(1).rolling(3).mean()
)

prediction_value = None
diff = None
recommendation = ""


# ✅ PREDICTION BUTTON (WITH SILENT FALLBACK)

if st.button("🔮 Predict Next Month Work Load"):

    latest_features = district_history.tail(1)
    lag_1 = latest_features["lag_1"].values[0]
    lag_2 = latest_features["lag_2"].values[0]
    rolling_3_mean = latest_features["rolling_3_mean"].values[0]

    # ✅ Silent fallback if not enough history
    if pd.isna(lag_1) or pd.isna(lag_2) or pd.isna(rolling_3_mean):
        prediction_value = float(service_load)
    else:
        input_data = pd.DataFrame([{
            "total_enroll": total_enroll,
            "total_updates": total_updates,
            "service_load": service_load,
            "month_num": int(latest_features["month_num"].values[0]),
            "lag_1": float(lag_1),
            "lag_2": float(lag_2),
            "rolling_3_mean": float(rolling_3_mean)
        }])

        prediction_value = float(demand_model.predict(input_data)[0])

    st.success(f"✅ Predicted Next Month Work Load: {round(prediction_value)}")

    diff = prediction_value - service_load

    if diff > 0:
        st.warning(f"📈 Workload may increase by ~{round(diff)} next month.")
        recommendation = "Allocate extra operators/machines and increase appointment slots to reduce waiting time."
        st.info(f"✅ Recommendation: {recommendation}")
    elif diff < 0:
        st.info(f"📉 Workload may decrease by ~{abs(round(diff))} next month.")
        recommendation = "Optimize staffing schedule and use time for backlog updates or maintenance."
        st.info(f"✅ Recommendation: {recommendation}")
    else:
        recommendation = "Workload is expected to remain stable. Maintain current staffing and monitoring."
        st.info("✅ Workload is expected to remain stable next month.")
        st.info(f"✅ Recommendation: {recommendation}")

st.markdown("---")


# ✅ GRAPH 1: District Trend

st.subheader("📈 District Service Load Trend")

fig1 = plt.figure(figsize=(10, 4))
plt.plot(district_history["month"], district_history["service_load"], marker="o")
plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Service Load")
plt.title(f"Service Load Trend: {selected_district}, {selected_state}")
plt.tight_layout()
st.pyplot(fig1)


# ✅ GRAPH 2: Current vs Predicted

st.subheader("📊 Current vs Predicted Next Month Comparison")

fig2 = None
if prediction_value is None:
    st.info("Click **Predict Next Month Work Load** to view prediction comparison chart.")
else:
    fig2 = plt.figure(figsize=(6, 4))
    plt.bar(["Current Month", "Predicted Next Month"], [service_load, prediction_value])
    plt.ylabel("Service Load")
    plt.title("Current vs Predicted Next Month Load")
    plt.tight_layout()
    st.pyplot(fig2)


# ✅ GRAPH 3: Top 10 districts in state

st.subheader("🏙️ Top 10 Districts in Selected State (Latest Month Service Load)")

latest_state_data = (
    state_data.sort_values("month")
    .groupby("district", as_index=False)
    .tail(1)
)

top10_state = latest_state_data.sort_values("service_load", ascending=False).head(10)

fig3 = plt.figure(figsize=(10, 4))
plt.barh(top10_state["district"], top10_state["service_load"])
plt.gca().invert_yaxis()
plt.xlabel("Service Load")
plt.title(f"Top 10 Districts by Service Load in {selected_state}")
plt.tight_layout()
st.pyplot(fig3)


# ✅ PDF GENERATOR FUNCTION (A4)

def create_pdf_report():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, Aadhaar Desert Report (Auto Generated)")
    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 25

    # District details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Prediction Summary")
    y -= 18

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"State: {selected_state}")
    y -= 15
    c.drawString(50, y, f"District: {selected_district}")
    y -= 15
    c.drawString(50, y, f"Last Month in Dataset: {last_month}")
    y -= 15
    c.drawString(50, y, f"Total Enrollments: {total_enroll}")
    y -= 15
    c.drawString(50, y, f"Total Updates: {total_updates}")
    y -= 15
    c.drawString(50, y, f"Current Service Load: {service_load}")
    y -= 20

    # Prediction
    if prediction_value is None:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Prediction not generated yet. Please predict first.")
        y -= 20
    else:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"Predicted Next Month Work Load: {round(prediction_value)}")
        y -= 15
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Difference (Predicted - Current): {round(diff)}")
        y -= 20

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Recommendation:")
        y -= 15
        c.setFont("Helvetica", 11)
        c.drawString(50, y, recommendation[:95])
        y -= 25

    def fig_to_img(fig):
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format="png", dpi=200, bbox_inches="tight")
        img_buf.seek(0)
        return img_buf

    # Graph 1
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Graph 1: Service Load Trend")
    y -= 10
    img1 = ImageReader(fig_to_img(fig1))
    c.drawImage(img1, 50, y - 170, width=500, height=170)
    y -= 190

    if y < 250:
        c.showPage()
        y = height - 50

    # Graph 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Graph 2: Current vs Predicted Next Month")
    y -= 10
    if fig2 is not None:
        img2 = ImageReader(fig_to_img(fig2))
        c.drawImage(img2, 50, y - 170, width=450, height=170)
        y -= 190
    else:
        c.setFont("Helvetica", 11)
        c.drawString(50, y - 20, "Prediction not generated yet. No comparison chart.")
        y -= 50

    if y < 250:
        c.showPage()
        y = height - 50

    # Graph 3
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Graph 3: Top 10 Districts in {selected_state}")
    y -= 10
    img3 = ImageReader(fig_to_img(fig3))
    c.drawImage(img3, 50, y - 220, width=500, height=220)
    y -= 240

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ✅ DOWNLOAD BUTTON (PDF)

st.markdown("---")
st.subheader("📥 Download Report (A4 PDF)")

if prediction_value is None:
    st.info("✅ First click **Predict Next Month Work Load**, then you can download the report.")
else:
    pdf_file = create_pdf_report()
    st.download_button(
        label="⬇️ Download Full Prediction Report (PDF)",
        data=pdf_file,
        file_name=f"UIDAI_Report_{selected_state}_{selected_district}.pdf",
        mime="application/pdf"
    )

# ---------------- FOOTER ----------------
st.markdown("---")


