import streamlit as st
import pandas as pd
import requests
import io
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

KEPLER_FIELDS = [
    "koi_period", "koi_impact", "koi_duration", "koi_depth",
    "koi_ror", "koi_srho", "koi_prad", "koi_sma",
    "koi_incl", "koi_teq", "koi_insol", "koi_dor",
    "koi_max_sngle_ev", "koi_max_mult_ev", "koi_model_snr",
    "koi_count", "koi_num_transits", "koi_bin_oedp_sig",
    "koi_steff", "koi_slogg", "koi_smet", "koi_srad",
    "koi_smass", "koi_kepmag", "koi_fwm_stat_sig",
]

# Human-readable labels for the form fields
FIELD_LABELS = {
    "koi_period":        "Orbital Period (days)",
    "koi_impact":        "Impact Parameter",
    "koi_duration":      "Transit Duration (hrs)",
    "koi_depth":         "Transit Depth (ppm)",
    "koi_ror":           "Planet-Star Radius Ratio",
    "koi_srho":          "Fitted Stellar Density (g/cm³)",
    "koi_prad":          "Planetary Radius (Earth radii)",
    "koi_sma":           "Semi-Major Axis (AU)",
    "koi_incl":          "Inclination (°)",
    "koi_teq":           "Equilibrium Temperature (K)",
    "koi_insol":         "Insolation Flux (Earth flux)",
    "koi_dor":           "Planet-Star Distance / Star Radius",
    "koi_max_sngle_ev":  "Max Single Event Statistic",
    "koi_max_mult_ev":   "Max Multiple Event Statistic",
    "koi_model_snr":     "Transit Model SNR",
    "koi_count":         "Number of Planets in System",
    "koi_num_transits":  "Number of Transits",
    "koi_bin_oedp_sig":  "Odd-Even Depth Significance",
    "koi_steff":         "Stellar Effective Temp (K)",
    "koi_slogg":         "Stellar Surface Gravity (log g)",
    "koi_smet":          "Stellar Metallicity (dex)",
    "koi_srad":          "Stellar Radius (Solar radii)",
    "koi_smass":         "Stellar Mass (Solar masses)",
    "koi_kepmag":        "Kepler-band Magnitude",
    "koi_fwm_stat_sig":  "FW Motion Stat. Significance",
}

# ── PAGE SETUP ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project E.T.H.O.S.",
    page_icon="🌌",
    layout="wide",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    .main .block-container { padding-top: 2rem; }

    /* ── Metric cards ── */
    .result-card {
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .result-confirmed {
        background: linear-gradient(135deg, #0d4d2b 0%, #134e28 50%, #1a6334 100%);
        border: 1px solid #2ecc71;
    }
    .result-false {
        background: linear-gradient(135deg, #4d0d0d 0%, #5e1414 50%, #722020 100%);
        border: 1px solid #e74c3c;
    }
    .result-card h1 { font-size: 2.4rem; margin-bottom: 0.2rem; }
    .result-card p  { font-size: 1.1rem; opacity: 0.85; }

    /* ── Required columns list ── */
    .col-chip {
        display: inline-block;
        background: #262730;
        border: 1px solid #444;
        border-radius: 6px;
        padding: 3px 10px;
        margin: 3px;
        font-family: monospace;
        font-size: 0.82rem;
    }

    /* ── Table status badges ── */
    .badge-confirmed {
        background: #1a6334; color: #2ecc71;
        padding: 3px 10px; border-radius: 12px;
        font-weight: 600; font-size: 0.85rem;
    }
    .badge-false {
        background: #5e1414; color: #e74c3c;
        padding: 3px 10px; border-radius: 12px;
        font-weight: 600; font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "phase1_results" not in st.session_state:
    st.session_state.phase1_results = None
if "phase1_mode" not in st.session_state:
    st.session_state.phase1_mode = None   # "single" or "csv"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.title("🛰️ E.T.H.O.S. Control")
st.sidebar.caption("Extraterrestrial Target Habitability Observation System")
st.sidebar.divider()
st.sidebar.markdown("**Backend:** `" + API_BASE + "`")

if st.sidebar.button("🔄 Reset Pipeline", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.divider()
st.sidebar.info(
    "**Phase 1** — Exoplanet Discovery  \n"
    "Uses a Random Forest classifier to predict CONFIRMED vs FALSE POSITIVE.\n\n"
    "**Phase 2** — Habitability Assessment *(coming soon)*"
)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🌌 Project E.T.H.O.S.")
st.caption("Extraterrestrial Target Habitability Observation System  •  Phase 1: Exoplanet Discovery Classifier")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — INPUT
# ═══════════════════════════════════════════════════════════════════════════════

tab_form, tab_csv = st.tabs(["📝  Single Prediction", "📁  CSV Bulk Upload"])

# ── TAB 1: SINGLE FORM ───────────────────────────────────────────────────────
with tab_form:
    st.subheader("Enter Kepler Object of Interest (KOI) Parameters")
    st.markdown("Fill in all **25 features** below and click **Predict** to classify this signal.")

    with st.form("single_pred_form"):
        form_values = {}

        # Lay out 3 columns of inputs
        cols = st.columns(3)
        for idx, field in enumerate(KEPLER_FIELDS):
            with cols[idx % 3]:
                form_values[field] = st.number_input(
                    label=FIELD_LABELS.get(field, field),
                    value=0.0,
                    format="%.6f",
                    key=f"form_{field}",
                    help=f"Backend field: `{field}`",
                )

        submitted = st.form_submit_button("🚀 Predict", use_container_width=True)

    if submitted:
        with st.spinner("Contacting backend model…"):
            try:
                resp = requests.post(f"{API_BASE}/predict", json=form_values, timeout=30)
                resp.raise_for_status()
                result = resp.json()

                st.session_state.phase1_mode = "single"
                st.session_state.phase1_results = result

            except requests.exceptions.ConnectionError:
                st.error("❌ **Cannot reach the backend.**  Make sure FastAPI is running at `" + API_BASE + "`.")
            except requests.exceptions.HTTPError as e:
                detail = ""
                try:
                    detail = e.response.json().get("detail", "")
                except Exception:
                    detail = str(e)
                st.error(f"❌ Backend error: {detail}")


# ── TAB 2: CSV UPLOAD ────────────────────────────────────────────────────────
with tab_csv:
    st.subheader("Upload a Kepler CSV File")

    # Show required columns
    with st.expander("📋 View required columns (25 features)", expanded=False):
        chips_html = "".join(f'<span class="col-chip">{c}</span>' for c in KEPLER_FIELDS)
        st.markdown(chips_html, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your `.csv` file here",
        type=["csv"],
        key="csv_uploader",
    )

    if uploaded_file is not None:
        # Preview the uploaded data
        try:
            preview_df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
            st.markdown(f"**Uploaded:** `{uploaded_file.name}` — {len(preview_df)} rows, {len(preview_df.columns)} columns")

            # Client-side column validation
            missing = [c for c in KEPLER_FIELDS if c not in preview_df.columns]
            extra   = [c for c in preview_df.columns if c not in KEPLER_FIELDS]

            if missing:
                st.error(f"❌ **Missing required columns:** {', '.join(missing)}")
            else:
                if extra:
                    st.warning(f"⚠️ Extra columns will be ignored by the model: {', '.join(extra)}")

                with st.expander("Preview uploaded data", expanded=False):
                    st.dataframe(preview_df.head(10), use_container_width=True)

                if st.button("🚀 Run Bulk Prediction", use_container_width=True):
                    with st.spinner("Sending CSV to backend…"):
                        try:
                            # Reset file pointer and send
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                            resp = requests.post(f"{API_BASE}/predict/csv", files=files, timeout=120)
                            resp.raise_for_status()
                            result = resp.json()

                            st.session_state.phase1_mode = "csv"
                            st.session_state.phase1_results = {
                                "api_response": result,
                                "original_df": preview_df,
                            }
                            st.rerun()

                        except requests.exceptions.ConnectionError:
                            st.error("❌ **Cannot reach the backend.**  Make sure FastAPI is running at `" + API_BASE + "`.")
                        except requests.exceptions.HTTPError as e:
                            detail = ""
                            try:
                                detail = e.response.json().get("detail", "")
                            except Exception:
                                detail = str(e)
                            st.error(f"❌ Backend error: {detail}")
        except Exception as ex:
            st.error(f"Failed to read CSV: {ex}")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.phase1_results is not None:
    st.divider()
    st.header("📊 Phase 1 Results — Exoplanet Discovery")

    # ── SINGLE RESULT ─────────────────────────────────────────────────────────
    if st.session_state.phase1_mode == "single":
        result = st.session_state.phase1_results
        prediction = result.get("prediction", "UNKNOWN")
        is_confirmed = prediction == "CONFIRMED"

        card_class = "result-confirmed" if is_confirmed else "result-false"
        icon = "✅" if is_confirmed else "❌"

        st.markdown(f"""
        <div class="result-card {card_class}">
            <h1>{icon} {prediction}</h1>
            <p>The model classified this signal as <strong>{prediction}</strong>.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.metric("Prediction", prediction)
        col2.metric("Raw Model Output", result.get("raw_output", "—"))

    # ── CSV TABLE RESULT ──────────────────────────────────────────────────────
    elif st.session_state.phase1_mode == "csv":
        api_resp = st.session_state.phase1_results["api_response"]
        original_df = st.session_state.phase1_results["original_df"]
        predictions = api_resp.get("predictions", [])
        total = api_resp.get("total_processed", len(predictions))

        st.success(f"✅ Processed **{total}** rows successfully.")

        # Build results DataFrame
        result_df = original_df.copy()

        # Map predictions back by row_index
        pred_map = {p["row_index"]: p["result"] for p in predictions}
        result_df["Prediction"] = result_df.index.map(lambda i: pred_map.get(i, "UNKNOWN"))

        # ── SORT: CONFIRMED first, then FALSE POSITIVE ────────────────────────
        sort_order = {"CONFIRMED": 0, "FALSE POSITIVE": 1}
        result_df["_sort"] = result_df["Prediction"].map(sort_order).fillna(2)
        result_df = result_df.sort_values("_sort").drop(columns=["_sort"]).reset_index(drop=True)

        # Summary metrics
        confirmed_count = sum(1 for p in predictions if p["result"] == "CONFIRMED")
        false_count     = total - confirmed_count

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Rows", total)
        m2.metric("🟢 Confirmed", confirmed_count)
        m3.metric("🔴 False Positive", false_count)

        # Color the Prediction column for display
        def highlight_prediction(val):
            if val == "CONFIRMED":
                return "background-color: #1a6334; color: #2ecc71; font-weight: 600;"
            elif val == "FALSE POSITIVE":
                return "background-color: #5e1414; color: #e74c3c; font-weight: 600;"
            return ""

        styled_df = result_df.style.map(highlight_prediction, subset=["Prediction"])
        st.dataframe(styled_df, use_container_width=True, height=500)


    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2 — HABITABILITY (PLACEHOLDER)
    # ═══════════════════════════════════════════════════════════════════════════
    st.divider()
    st.header("🌍 Phase 2 — Habitability Assessment")
    st.caption("Evaluate confirmed exoplanets for potential habitability using the Earth Similarity Index (ESI).")

    if st.button("✨ Check Habitability", use_container_width=True):
        st.info(
            "🚧 **Habitability model is not available yet.**\n\n"
            "This feature will use the Phase 2 regression model to compute an "
            "Earth Similarity Index (ESI) score for each confirmed planet. "
            "Stay tuned — coming soon!"
        )