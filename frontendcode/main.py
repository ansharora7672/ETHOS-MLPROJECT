import streamlit as st
import pandas as pd
import numpy as np
import time

# --- Page Config ---
st.set_page_config(page_title="Project E.T.H.O.S.", layout="wide")

# --- Initialize Session States ---
if 'stage' not in st.session_state:
    st.session_state.stage = 'upload'
if 'discovery_df' not in st.session_state:
    st.session_state.discovery_df = None

# --- Sidebar ---
st.sidebar.title("🛰️ E.T.H.O.S. Control")
# model_type = st.sidebar.radio("Select Active Model:", ["Random Forest", "Neural Network (MLP)"])
st.sidebar.divider()
if st.sidebar.button("Reset Pipeline"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- Main UI ---
st.title("🌌 Extraterrestrial Target Habitability Observation System")

# # Model Status Indicator
# if model_type == "Random Forest":
#     st.info(f"🟢 **STATUS:** Engine running via **Random Forest Classifier**")
# else:
#     st.success(f"🟢 **STATUS:** Engine running via **Neural Network (MLP) Optimizer**")

# --- Step 1: File Upload ---
if st.session_state.stage == 'upload':
    uploaded_file = st.file_uploader("Upload Kepler Data (CSV)", type="csv")
    if uploaded_file:
        if st.button("🚀 Process Signals"):
            st.session_state.stage = 'discovery_loading'
            st.rerun()

# --- Step 2: Discovery Loading (5 Seconds) ---
if st.session_state.stage == 'discovery_loading':
    placeholder = st.empty()
    for i in range(5, 0, -1):
        with placeholder.container():
            # st.header(f"🔍 Analyzing Data via {model_type}...")
            st.subheader(f"Filtering telescope noise and star-shaking")
        time.sleep(1)
    
    # Generate 15 random entries and store them
    names = [f"Kepler-{np.random.randint(100, 999)}{chr(np.random.randint(97, 102))}" for _ in range(15)]
    status = np.random.choice(["Yes", "No"], size=15, p=[0.6, 0.4])
    st.session_state.discovery_df = pd.DataFrame({"Name": names, "Exoplanet Status": status})
    
    st.session_state.stage = 'discovery_results'
    st.rerun()

# --- Step 3: Display Results ---
if st.session_state.stage in ['discovery_results', 'habitability_loading', 'final_results']:
    st.header("Phase 1: Exoplanet Discovery Results")
    st.table(st.session_state.discovery_df)
    
    # Show button only if we haven't started habitability yet
    if st.session_state.stage == 'discovery_results':
        if st.button("✨ Check Habitability"):
            st.session_state.stage = 'habitability_loading'
            st.rerun()
#adfssdfg
# --- Step 4: Habitability Loading ---
if st.session_state.stage == 'habitability_loading':
    with st.spinner("Calculating Earth Similarity Index (ESI) for confirmed planets..."):
        time.sleep(3)
    st.session_state.stage = 'final_results'
    st.rerun()

# --- Step 5: Final Table (Appears below the first) ---
if st.session_state.stage == 'final_results':
    st.divider()
    st.header("Phase 2: Final Habitability Assessment")
    
    # Filter only "Yes" planets from the stored state
    confirmed_planets = st.session_state.discovery_df[st.session_state.discovery_df["Exoplanet Status"] == "Yes"].copy()
    
    if not confirmed_planets.empty:
        # Generate random Habitable Status and ESI
        confirmed_planets["Habitable Status"] = np.random.choice(["Yes", "No"], size=len(confirmed_planets))
        confirmed_planets["ESI Score"] = [round(np.random.uniform(0.4, 0.98), 3) for _ in range(len(confirmed_planets))]
        
        # Display the filtered second table
        st.dataframe(confirmed_planets, use_container_width=True)
        st.balloons()
    else:
        st.warning("No planets were confirmed as 'Yes' in Phase 1 to assess for habitability.")