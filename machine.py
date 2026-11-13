%%writefile app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(
    page_title="Sleep Insights & Forecast",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set dark custom visual style override
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    h1 {
        color: #3b82f6 !important;
    }
    h3 {
        color: #f1f5f9 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌙 Sleep Insights & Forecast Portal")
st.write("Adjust your metrics in the side panel to dynamically predict sleep duration and evaluate habit impact weights.")

@st.cache_resource
def load_models():
    lr_model = joblib.load('linear_regression_model.pkl')
    return lr_model

try:
    lr_model = load_models()
    avg_sleep = 6.27
except Exception as e:
    st.error(f"Initialization Error: {e}. Please ensure your model .pkl files are saved in the project directory.")
    st.stop()

# Side Panel Control Controls
st.sidebar.header("🛠️ Lifestyle Metrics")
screentime = st.sidebar.slider("Bedtime Phone Screen Time (Minutes)", 0, 300, 60, step=5)
brightness = st.sidebar.slider("Screen Brightness (%)", 0, 100, 50, step=5)
age = st.sidebar.slider("Age (Years)", 10, 100, 30, step=1)
caffeine = st.sidebar.slider("Caffeine Post-5pm (mg)", 0, 300, 50, step=10)
activity = st.sidebar.slider("Physical Activity (Minutes)", 0, 180, 30, step=5)

# Dynamic ML inference execution
input_data = np.array([[screentime, brightness, age, caffeine, activity]])
predicted_hours = lr_model.predict(input_data)[0]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Model Sleep Duration Prediction")
    st.metric(
        label="Estimated Total Sleep", 
        value=f"{predicted_hours:.2f} Hours", 
        delta=f"{predicted_hours - avg_sleep:.2f} hrs vs Average"
    )

    if predicted_hours < 6.0:
        st.error("Your predicted sleep is quite low. Try minimizing evening phone minutes and lowering your screen brightness!")
    elif predicted_hours >= 7.5:
        st.success("Excellent! This routine yields a healthy and highly restorative sleep schedule.")
    else:
        st.warning("Your sleep schedule is acceptable, but you can improve it further by capping screen time and caffeine post-5 PM.")

with col2:
    st.subheader("📉 Live Sleep Impact Chart")
    coefs = lr_model.coef_
    impacts = {
        'Phone Screen Time': screentime * coefs[0],
        'Screen Brightness': brightness * coefs[1],
        'Late Caffeine': caffeine * coefs[3],
        'Physical Exercise': activity * coefs[4]
    }
    chart_df = pd.DataFrame(list(impacts.items()), columns=['Lifestyle Habit', 'Hours Added/Lost'])
    st.bar_chart(chart_df.set_index('Lifestyle Habit'))
