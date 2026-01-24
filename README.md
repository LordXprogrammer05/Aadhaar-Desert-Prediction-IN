# Aadhaar-Desert-Prediction-IN
UIDAI hackathon 2026
# 🆔 Aadhaar Desert Dashboard IN 🇮🇳  
### District-wise Risk Detection + Next Month Workload Forecasting (UIDAI Hackathon Project)

This project identifies **Aadhaar Desert Districts** (high-risk districts with high service pressure) and predicts **Next Month Aadhaar Service Workload** using **Machine Learning**.  
It also provides an interactive **Streamlit Dashboard** for district-wise insights, forecasting, and visual analytics.

---

## ✅ Problem Statement
Many districts face **high Aadhaar enrolment/update workload**, which causes:

- Long waiting time for citizens  
- Resource imbalance at Aadhaar centres  
- Operational overload in high-demand districts  
- Poor accessibility in remote regions  

### 🎯 Goal
✅ Detect Aadhaar desert (high-risk) districts  
✅ Predict next month workload in advance  
✅ Support administrators with actionable insights via a dashboard  

---

## ✅ Solution / Approach
This project is implemented in **two parts**:

### ✅ 1) Aadhaar Desert Detection (Risk Scoring)
We compute a **district risk score** based on:

- **Enrolment Load**
- **Update Load**
- **Service Load**
- **Update Pressure**
- **Child Ratio**
- **Biometric Ratio**
- **Normalized risk components**

Then we classify districts into risk categories:

- **HIGH_RISK**
- **MEDIUM_RISK**
- **LOW_RISK**

---

### ✅ 2) Next Month Workload Forecasting (ML Regression)
We built a **Demand Prediction Model** to forecast:

📌 **Next Month Service Load** for each district

Model used:
✅ `RandomForestRegressor`

We improved accuracy using time-based features:

- `month_num`
- `lag_1` (previous month service load)
- `lag_2` (2 months back service load)
- `rolling_3_mean` (3-month rolling average)

---

## 📊 Dataset Used (UIDAI Hackathon Dataset)
This project uses **UIDAI Aadhaar enrolment & update data** (district-level).

### Main columns used
- `date`
- `state`
- `district`
- `pincode`
- `age_0_5`
- `age_5_17`
- `age_18_greater`
- `total_enroll`
- `total_updates`
- `service_load`
- `update_pressure`
- `child_ratio`
- `bio_ratio`
- `risk_score`
- `risk_score_0_100`
- `risk_label`
- `month`

---

## 🧠 Methodology

### ✅ Data Cleaning
- Fixed incorrect spellings and duplicates of **state names**
- Fixed spelling differences in **district names**
- Removed invalid or noisy values
- Standardized text formatting (case, spaces, symbols)

### ✅ Feature Engineering
- `service_load = total_enroll + total_updates`
- `update_pressure = total_updates / (service_load + 1)`
- Risk scoring and normalization for district ranking
- Created time features for prediction model:
  - `month_num`
  - `lag_1`
  - `lag_2`
  - `rolling_3_mean`

---

## 📈 Visualisations Included
This project generates multiple insights using Matplotlib:

✅ Risk Category Distribution  
✅ Top 20 Aadhaar Desert Districts (High Risk)  
✅ Top 20 Districts by Risk Score  
✅ Service Load Trend (District wise)  
✅ Current vs Predicted Next Month Comparison  
✅ Top 10 Districts by Service Load (State wise)

---

## 🤖 Model Performance

### ✅ Demand Prediction Model (Improved)
**Evaluation Metrics:**
- ✅ MAE  : **4666.57**
- ✅ RMSE : **7869.50**
- ✅ R²   : **0.7090**

This indicates good predictive accuracy for next-month district workload forecasting.

---

## 🖥️ Streamlit Dashboard Features
✅ State dropdown  
✅ District dropdown (auto filtered by selected state)  
✅ Auto-load latest available district history  
✅ Predict next month workload  
✅ Graphs inside the app:
- District service load trend over months
- Current vs predicted workload comparison
- Top 10 districts in selected state (by latest service load)

✅ Recommendation output for decision-making

Output

✅ Aadhaar desert district identification (High risk ranking)
✅ Next-month workload forecast district-wise
✅ Visual insights with charts
✅ Top 20 high-risk districts forecast file


Impact & Applicability

This solution can help UIDAI / administrators to:

✅ Identify high-risk districts early
✅ Improve resource allocation and staffing
✅ Reduce delays and overload at Aadhaar centres
✅ Improve service coverage in underserved districts
✅ Support data-driven planning and monitoring

## 📂 Project Files
