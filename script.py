import streamlit as st
import pandas as pd
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="NPD Tracker", layout="wide")
st.title("🚀 NPD Development & Revenue Impact Dashboard")

# --- MOCK DATA INITIALIZATION ---
if 'npd_data' not in st.session_state:
    st.session_state.npd_data = pd.DataFrame(columns=[
        "Project", "Brand", "SKU", "Market", 
        "Target_Launch", "Actual_Launch", 
        "Monthly_Volume", "NSV_per_Unit", "Status"
    ])

# --- SIDEBAR: FILTERS & INPUT ---
with st.sidebar:
    st.header("Add New Project")
    with st.form("npd_form"):
        p_name = st.text_input("Project Name")
        brand = st.selectbox("Brand", ["Royal Stag", "Blenders Pride", "Absolut", "Other"])
        sku = st.text_input("SKU (e.g., 750ml)")
        market = st.text_input("Market (e.g., Maharashtra)")
        
        col1, col2 = st.columns(2)
        target_date = col1.date_input("Target Launch")
        actual_date = col2.date_input("Projected/Actual Launch")
        
        vol = st.number_input("Est. Monthly Volume (Cases/Units)", min_value=0)
        nsv = st.number_input("NSV per Unit (₹)", min_value=0.0)
        
        submit = st.form_submit_button("Add Project")
        
        if submit:
            new_data = {
                "Project": p_name, "Brand": brand, "SKU": sku, "Market": market,
                "Target_Launch": target_date, "Actual_Launch": actual_date,
                "Monthly_Volume": vol, "NSV_per_Unit": nsv, "Status": "In Progress"
            }
            st.session_state.npd_data = pd.concat([st.session_state.npd_data, pd.DataFrame([new_data])], ignore_index=True)

# --- LOGIC: CALCULATE LOSS ---
df = st.session_state.npd_data.copy()

if not df.empty:
    # Convert to datetime for math
    df['Target_Launch'] = pd.to_datetime(df['Target_Launch'])
    df['Actual_Launch'] = pd.to_datetime(df['Actual_Launch'])
    
    # Calculate Delay in Months
    df['Delay_Days'] = (df['Actual_Launch'] - df['Target_Launch']).dt.days
    df['Delay_Months'] = df['Delay_Days'] / 30
    df['Delay_Months'] = df['Delay_Months'].apply(lambda x: max(0, x)) # No loss if early
    
    # Revenue Loss Calculation
    df['Revenue_Loss'] = df['Delay_Months'] * df['Monthly_Volume'] * df['NSV_per_Unit']

    # --- KPI DISPLAY ---
    total_at_risk = df['Revenue_Loss'].sum()
    avg_delay = df['Delay_Days'].mean()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total NPD Projects", len(df))
    c2.metric("Total Revenue at Risk", f"₹{total_at_risk:,.2f}", delta_color="inverse")
    c3.metric("Avg. Delay (Days)", f"{avg_delay:.1f} Days")

    # --- MAIN DASHBOARD ---
    st.subheader("Project Overview")
    
    # Applying Filters
    f_brand = st.multiselect("Filter by Brand", options=df['Brand'].unique())
    if f_brand:
        df = df[df['Brand'].isin(f_brand)]
        
    st.dataframe(df[["Project", "Brand", "SKU", "Market", "Target_Launch", "Actual_Launch", "Delay_Days", "Revenue_Loss"]], use_container_width=True)

else:
    st.info("Please add an NPD project in the sidebar to begin.")
  
