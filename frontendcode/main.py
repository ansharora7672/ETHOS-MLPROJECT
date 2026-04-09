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

# ── ANIMATED SPACE BACKGROUND (Canvas + CSS) ─────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Global Dark Space Theme ── */
    .stApp {
        background: radial-gradient(ellipse at 20% 50%, #0a0e27 0%, #020515 50%, #000000 100%);
        color: #e0e6ff;
    }

    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }

    /* ── Twinkling Stars (pure CSS) ── */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        z-index: 0;
        background-image:
            radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 20% 60%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1.5px 1.5px at 30% 10%, rgba(180,200,255,0.9), transparent),
            radial-gradient(1px 1px at 40% 80%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1.5px 1.5px at 50% 40%, rgba(200,220,255,0.7), transparent),
            radial-gradient(1px 1px at 60% 90%, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 70% 30%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1.5px 1.5px at 80% 70%, rgba(180,200,255,0.6), transparent),
            radial-gradient(1px 1px at 90% 15%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1px 1px at 15% 45%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1.5px 1.5px at 25% 75%, rgba(200,180,255,0.8), transparent),
            radial-gradient(1px 1px at 35% 55%, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 45% 25%, rgba(255,255,255,0.9), transparent),
            radial-gradient(1.5px 1.5px at 55% 85%, rgba(180,220,255,0.5), transparent),
            radial-gradient(1px 1px at 65% 5%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1px 1px at 75% 50%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1.5px 1.5px at 85% 35%, rgba(200,200,255,0.8), transparent),
            radial-gradient(1px 1px at 95% 65%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1px 1px at 5% 95%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1.5px 1.5px at 48% 12%, rgba(180,200,255,0.7), transparent);
        animation: twinkle 4s ease-in-out infinite alternate;
    }

    @keyframes twinkle {
        0%   { opacity: 0.6; }
        50%  { opacity: 1.0; }
        100% { opacity: 0.7; }
    }

    /* ── Nebula glow overlays ── */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        z-index: 0;
        background:
            radial-gradient(600px circle at 15% 30%, rgba(63, 0, 113, 0.15), transparent 70%),
            radial-gradient(500px circle at 85% 60%, rgba(0, 50, 120, 0.12), transparent 70%),
            radial-gradient(400px circle at 50% 80%, rgba(0, 100, 80, 0.08), transparent 70%);
        animation: nebula-drift 20s ease-in-out infinite alternate;
    }

    @keyframes nebula-drift {
        0%   { transform: scale(1) translateX(0); }
        100% { transform: scale(1.05) translateX(20px); }
    }

    /* ── Ensure content is above background ── */
    .main, [data-testid="stSidebar"], .stTabs, .stForm, .element-container {
        position: relative;
        z-index: 1;
    }

    /* ── Typography ── */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Orbitron', monospace, sans-serif !important;
        letter-spacing: 1px;
    }

    p, span, label, .stMarkdown, div {
        font-family: 'Exo 2', sans-serif;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050a1a 0%, #0a1628 40%, #0d1f3c 100%) !important;
        border-right: 1px solid rgba(100, 140, 255, 0.15);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #a0b4d8;
    }

    /* ── Glowing Title ── */
    .hero-title {
        font-family: 'Orbitron', monospace, sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #64b5f6 0%, #a78bfa 30%, #818cf8 60%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0;
        animation: glow-shift 6s ease-in-out infinite alternate;
        text-shadow: 0 0 40px rgba(100, 130, 255, 0.3);
    }

    @keyframes glow-shift {
        0%   { filter: brightness(1) drop-shadow(0 0 10px rgba(100,130,255,0.3)); }
        50%  { filter: brightness(1.2) drop-shadow(0 0 20px rgba(130,100,255,0.5)); }
        100% { filter: brightness(1) drop-shadow(0 0 10px rgba(100,130,255,0.3)); }
    }

    .hero-subtitle {
        font-family: 'Orbitron', monospace, sans-serif;
        text-align: center;
        color: #7b8cad;
        font-size: 0.85rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: 4px;
        margin-bottom: 1.5rem;
    }

    /* ── Status Bar ── */
    .status-bar {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 12px 24px;
        background: rgba(10, 20, 50, 0.6);
        border: 1px solid rgba(100, 140, 255, 0.12);
        border-radius: 50px;
        margin: 0 auto 2rem auto;
        max-width: 700px;
        backdrop-filter: blur(10px);
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Exo 2', sans-serif;
        font-size: 0.82rem;
        color: #7b8cad;
    }

    .status-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-dot 2s ease-in-out infinite;
    }

    .status-dot.green { background: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .status-dot.blue  { background: #3b82f6; box-shadow: 0 0 8px #3b82f6; }
    .status-dot.amber { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%      { opacity: 0.5; transform: scale(0.8); }
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(10, 20, 50, 0.5);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(100, 140, 255, 0.1);
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #7b8cad;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(100, 140, 255, 0.1);
        color: #c0d0ff;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(139, 92, 246, 0.2)) !important;
        color: #e0e6ff !important;
        border: 1px solid rgba(100, 140, 255, 0.3) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ── Glass Cards ── */
    .glass-card {
        background: rgba(10, 18, 40, 0.65);
        border: 1px solid rgba(100, 140, 255, 0.12);
        border-radius: 16px;
        padding: 1.8rem;
        backdrop-filter: blur(12px);
        margin: 1rem 0;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }

    .glass-card:hover {
        border-color: rgba(100, 140, 255, 0.25);
        box-shadow: 0 4px 30px rgba(59, 130, 246, 0.08);
    }

    /* ── Result Cards ── */
    .result-card {
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
    }

    .result-card::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.03), transparent 30%);
        animation: rotate-glow 8s linear infinite;
    }

    @keyframes rotate-glow {
        100% { transform: rotate(360deg); }
    }

    .result-confirmed {
        background: linear-gradient(135deg, #041f12 0%, #0a3d1e 50%, #0d4d2b 100%);
        border: 1px solid rgba(46, 204, 113, 0.4);
        box-shadow: 0 0 40px rgba(46, 204, 113, 0.1), inset 0 0 40px rgba(46, 204, 113, 0.05);
    }

    .result-false {
        background: linear-gradient(135deg, #1f0404 0%, #3d0a0a 50%, #4d0d0d 100%);
        border: 1px solid rgba(231, 76, 60, 0.4);
        box-shadow: 0 0 40px rgba(231, 76, 60, 0.1), inset 0 0 40px rgba(231, 76, 60, 0.05);
    }

    .result-card h1 {
        font-size: 2.8rem;
        margin-bottom: 0.3rem;
        position: relative;
        z-index: 1;
    }

    .result-card p {
        font-size: 1.1rem;
        opacity: 0.8;
        position: relative;
        z-index: 1;
    }

    /* ── Metric Cards ── */
    [data-testid="stMetric"] {
        background: rgba(10, 18, 40, 0.6);
        border: 1px solid rgba(100, 140, 255, 0.12);
        border-radius: 12px;
        padding: 16px 20px;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(100, 140, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.12);
    }

    [data-testid="stMetricLabel"] {
        color: #7b8cad !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.7rem !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        color: #e0e6ff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
    }

    /* ── Form Inputs ── */
    .stNumberInput > div > div > input {
        background: rgba(10, 18, 40, 0.6) !important;
        border: 1px solid rgba(100, 140, 255, 0.15) !important;
        color: #c0d0ff !important;
        border-radius: 8px !important;
        font-family: 'Exo 2', sans-serif !important;
        transition: border-color 0.3s ease !important;
    }

    .stNumberInput > div > div > input:focus {
        border-color: rgba(100, 140, 255, 0.5) !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.15) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5) !important;
        background: linear-gradient(135deg, #2146a0 0%, #4a90f7 50%, #7577f5 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #065f46 0%, #059669 50%, #10b981 100%) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }

    .stFormSubmitButton > button:hover {
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
        background: linear-gradient(135deg, #08775a 0%, #07b07d 50%, #22d39a 100%) !important;
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        background: rgba(10, 18, 40, 0.4);
        border: 2px dashed rgba(100, 140, 255, 0.2);
        border-radius: 16px;
        padding: 1rem;
        transition: border-color 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(100, 140, 255, 0.4);
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(10, 18, 40, 0.5) !important;
        border: 1px solid rgba(100, 140, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #7b8cad !important;
        font-family: 'Exo 2', sans-serif !important;
    }

    /* ── Column Chips ── */
    .col-chip {
        display: inline-block;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(100, 140, 255, 0.2);
        border-radius: 8px;
        padding: 4px 12px;
        margin: 3px;
        font-family: 'Exo 2', monospace;
        font-size: 0.8rem;
        color: #a0b4f0;
        transition: all 0.2s ease;
    }

    .col-chip:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: rgba(100, 140, 255, 0.4);
        color: #c0d0ff;
        transform: translateY(-1px);
    }

    /* ── Dividers ── */
    hr {
        border-color: rgba(100, 140, 255, 0.1) !important;
    }

    /* ── DataFrame ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(100, 140, 255, 0.12);
    }

    /* ── Info/Warning/Error boxes ── */
    .stAlert {
        border-radius: 12px !important;
        backdrop-filter: blur(8px);
    }

    /* ── Section Headers ── */
    .section-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #c0d0ff;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(100, 140, 255, 0.15);
        display: flex;
        align-items: center;
        gap: 10px;
    }



    /* ── Scrollbar ── */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #050a1a;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 140, 255, 0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 140, 255, 0.4);
    }

    /* ── Sidebar button override ── */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(100, 140, 255, 0.1) !important;
        border: 1px solid rgba(100, 140, 255, 0.2) !important;
        box-shadow: none !important;
        color: #7b8cad !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(100, 140, 255, 0.2) !important;
        border-color: rgba(100, 140, 255, 0.4) !important;
        color: #c0d0ff !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.15) !important;
    }

    /* ── Sidebar info box ── */
    [data-testid="stSidebar"] .stAlert {
        background: rgba(59, 130, 246, 0.08) !important;
        border: 1px solid rgba(100, 140, 255, 0.15) !important;
        color: #8ba4cc !important;
    }
</style>
""", unsafe_allow_html=True)


# ── ANIMATED SOLAR SYSTEM HEADER (HTML/JS/CSS) ───────────────────────────────
import streamlit.components.v1 as components

components.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }

    .solar-scene {
        width: 100%;
        height: 320px;
        position: relative;
        overflow: hidden;
        background: transparent;
    }

    /* ── Shooting Stars ── */
    .shooting-star {
        position: absolute;
        width: 80px; height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.8), transparent);
        border-radius: 50%;
        animation: shoot linear infinite;
    }

    .shooting-star:nth-child(1) { top: 15%; left: -80px; animation-duration: 1.8s; animation-delay: 0s; }
    .shooting-star:nth-child(2) { top: 35%; left: -80px; animation-duration: 2.2s; animation-delay: 3s; }
    .shooting-star:nth-child(3) { top: 55%; left: -80px; animation-duration: 1.5s; animation-delay: 6s; }

    @keyframes shoot {
        0%   { transform: translateX(0) translateY(0) rotate(-20deg); opacity: 0; }
        5%   { opacity: 1; }
        70%  { opacity: 1; }
        100% { transform: translateX(calc(100vw + 200px)) translateY(100px) rotate(-20deg); opacity: 0; }
    }

    /* ── Orbiting Planets Container ── */
    .orbit-center {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
    }

    /* ── Star (Sun) ── */
    .star-core {
        width: 40px; height: 40px;
        background: radial-gradient(circle, #fff8e1 0%, #ffb74d 40%, #ff8f00 70%, #e65100 100%);
        border-radius: 50%;
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        box-shadow:
            0 0 30px rgba(255, 183, 77, 0.6),
            0 0 60px rgba(255, 143, 0, 0.4),
            0 0 100px rgba(255, 111, 0, 0.2);
        animation: star-pulse 3s ease-in-out infinite;
        z-index: 10;
    }

    @keyframes star-pulse {
        0%, 100% { box-shadow: 0 0 30px rgba(255,183,77,0.6), 0 0 60px rgba(255,143,0,0.4), 0 0 100px rgba(255,111,0,0.2); }
        50%      { box-shadow: 0 0 40px rgba(255,183,77,0.8), 0 0 80px rgba(255,143,0,0.5), 0 0 120px rgba(255,111,0,0.3); }
    }

    /* ── Orbit Rings ── */
    .orbit-ring {
        position: absolute;
        border: 1px solid rgba(100, 140, 255, 0.08);
        border-radius: 50%;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
    }

    .orbit-ring-1 { width: 120px; height: 120px; }
    .orbit-ring-2 { width: 200px; height: 200px; }
    .orbit-ring-3 { width: 290px; height: 290px; }
    .orbit-ring-4 { width: 380px; height: 380px; }

    /* ── Planets ── */
    .planet-orbit {
        position: absolute;
        top: 50%; left: 50%;
        transform-origin: 0 0;
        animation: orbit-spin linear infinite;
    }

    .planet {
        border-radius: 50%;
        position: absolute;
        transform: translate(-50%, -50%);
    }

    /* Planet 1 - Small rocky (Mercury-like) */
    .planet-1-container { animation-duration: 6s; }
    .planet-1 {
        width: 8px; height: 8px;
        background: radial-gradient(circle at 35% 35%, #e0e0e0, #9e9e9e);
        left: 60px; top: 0;
        box-shadow: 0 0 6px rgba(200,200,200,0.3);
    }

    /* Planet 2 - Earth-like */
    .planet-2-container { animation-duration: 10s; animation-delay: -2s; }
    .planet-2 {
        width: 14px; height: 14px;
        background: radial-gradient(circle at 35% 35%, #64b5f6, #1565c0 50%, #0d47a1);
        left: 100px; top: 0;
        box-shadow: 0 0 10px rgba(100,181,246,0.4);
    }

    /* Planet 3 - Gas giant (Jupiter-like) */
    .planet-3-container { animation-duration: 16s; animation-delay: -5s; }
    .planet-3 {
        width: 22px; height: 22px;
        background: radial-gradient(circle at 35% 35%, #ffcc80, #ef6c00 40%, #bf360c 80%);
        left: 145px; top: 0;
        box-shadow: 0 0 15px rgba(239,108,0,0.3);
    }
    .planet-3::after {
        content: '';
        position: absolute;
        width: 32px; height: 6px;
        border: 1.5px solid rgba(255,204,128,0.3);
        border-radius: 50%;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%) rotateX(75deg);
    }

    /* Planet 4 - Ice giant */
    .planet-4-container { animation-duration: 22s; animation-delay: -8s; }
    .planet-4 {
        width: 12px; height: 12px;
        background: radial-gradient(circle at 35% 35%, #b2dfdb, #00897b 60%, #004d40);
        left: 190px; top: 0;
        box-shadow: 0 0 10px rgba(0,137,123,0.3);
    }

    @keyframes orbit-spin {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* ── Satellite ── */
    .satellite {
        position: absolute;
        width: 20px; height: 20px;
        animation: satellite-fly 18s linear infinite;
        z-index: 20;
    }

    .satellite-body {
        width: 6px; height: 4px;
        background: #e0e0e0;
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        border-radius: 1px;
    }

    .satellite-panel-l, .satellite-panel-r {
        width: 8px; height: 3px;
        background: linear-gradient(90deg, #42a5f5, #1976d2);
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        border-radius: 1px;
        box-shadow: 0 0 4px rgba(66,165,245,0.4);
    }

    .satellite-panel-l { right: calc(50% + 3px); }
    .satellite-panel-r { left: calc(50% + 3px); }

    @keyframes satellite-fly {
        0%   { top: 80%; left: -5%; transform: rotate(-15deg); }
        25%  { top: 20%; left: 30%; transform: rotate(-10deg); }
        50%  { top: 10%; left: 65%; transform: rotate(0deg); }
        75%  { top: 40%; left: 90%; transform: rotate(5deg); }
        100% { top: 80%; left: 105%; transform: rotate(10deg); }
    }
</style>

<div class="solar-scene">
    <!-- Shooting stars -->
    <div class="shooting-star"></div>
    <div class="shooting-star"></div>
    <div class="shooting-star"></div>

    <!-- Solar system -->
    <div class="orbit-center">
        <div class="star-core"></div>

        <div class="orbit-ring orbit-ring-1"></div>
        <div class="orbit-ring orbit-ring-2"></div>
        <div class="orbit-ring orbit-ring-3"></div>
        <div class="orbit-ring orbit-ring-4"></div>

        <div class="planet-orbit planet-1-container">
            <div class="planet planet-1"></div>
        </div>
        <div class="planet-orbit planet-2-container">
            <div class="planet planet-2"></div>
        </div>
        <div class="planet-orbit planet-3-container">
            <div class="planet planet-3"></div>
        </div>
        <div class="planet-orbit planet-4-container">
            <div class="planet planet-4"></div>
        </div>
    </div>

    <!-- Satellite -->
    <div class="satellite">
        <div class="satellite-panel-l"></div>
        <div class="satellite-body"></div>
        <div class="satellite-panel-r"></div>
    </div>
</div>
""", height=320)


# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "phase1_results" not in st.session_state:
    st.session_state.phase1_results = None
if "phase1_mode" not in st.session_state:
    st.session_state.phase1_mode = None   # "single" or "csv"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center; padding: 1rem 0;">
    <div style="font-family: 'Orbitron', sans-serif; font-size: 1.3rem; font-weight: 700;
                background: linear-gradient(135deg, #64b5f6, #a78bfa);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;">
        🛰️ MISSION CONTROL
    </div>
    <div style="font-size: 0.7rem; color: #5a6a8a; letter-spacing: 3px; margin-top: 4px;
                font-family: 'Orbitron', sans-serif; text-transform: uppercase;">
        E.T.H.O.S. Command
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

st.sidebar.markdown(f"""
<div style="font-size: 0.78rem; color: #5a6a8a; font-family: 'Exo 2', sans-serif;">
    <span style="color: #3b82f6;">▸</span> Backend: <code style="color: #7b8cad; background: rgba(59,130,246,0.1);
    padding: 2px 6px; border-radius: 4px; font-size: 0.72rem;">{API_BASE}</code>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Reset Pipeline", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.divider()

st.sidebar.markdown("""
<div style="font-family: 'Exo 2', sans-serif; font-size: 0.82rem; line-height: 1.8;">
    <div style="color: #64b5f6; font-family: 'Orbitron', sans-serif; font-size: 0.72rem;
                letter-spacing: 1px; margin-bottom: 8px;">◈ ACTIVE MODULE</div>
    <div style="color: #8ba4cc;">
        <span style="color: #2ecc71;">●</span> <strong>Exoplanet Discovery</strong><br/>
        <span style="font-size: 0.75rem; color: #5a6a8a; margin-left: 16px;">
            Random Forest Classifier</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-title">PROJECT E.T.H.O.S.</div>
<div class="hero-subtitle">Extraterrestrial Target Habitability Observation System</div>

<div class="status-bar">
    <div class="status-item">
        <span class="status-dot green"></span>
        RF Model Online
    </div>
    <div class="status-item">
        <span class="status-dot blue"></span>
        Discovery Engine Active
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — INPUT
# ═══════════════════════════════════════════════════════════════════════════════

tab_form, tab_csv = st.tabs(["📡  Single Signal Analysis", "📁  Bulk CSV Processing"])

# ── TAB 1: SINGLE FORM ───────────────────────────────────────────────────────
with tab_form:
    st.markdown("""
    <div class="section-header">📡 Signal Parameter Input</div>
    <p style="color: #5a6a8a; font-size: 0.9rem; margin-bottom: 1rem;">
        Enter all <strong style="color:#64b5f6;">25 KOI features</strong> to classify a single telescope signal.
    </p>
    """, unsafe_allow_html=True)

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

        submitted = st.form_submit_button("🚀 LAUNCH ANALYSIS", use_container_width=True)

    if submitted:
        with st.spinner("Transmitting data to classification engine…"):
            try:
                resp = requests.post(f"{API_BASE}/predict", json=form_values, timeout=30)
                resp.raise_for_status()
                result = resp.json()

                st.session_state.phase1_mode = "single"
                st.session_state.phase1_results = result

            except requests.exceptions.ConnectionError:
                st.error("❌ **Signal lost — cannot reach backend.**  Verify FastAPI is running at `" + API_BASE + "`.")
            except requests.exceptions.HTTPError as e:
                detail = ""
                try:
                    detail = e.response.json().get("detail", "")
                except Exception:
                    detail = str(e)
                st.error(f"❌ Backend transmission error: {detail}")


# ── TAB 2: CSV UPLOAD ────────────────────────────────────────────────────────
with tab_csv:
    st.markdown("""
    <div class="section-header">📁 Bulk Signal Processing</div>
    <p style="color: #5a6a8a; font-size: 0.9rem; margin-bottom: 1rem;">
        Upload a CSV with telescope observation data for batch classification.
    </p>
    """, unsafe_allow_html=True)

    # Show required columns
    with st.expander("📋 View required telemetry columns (25 features)", expanded=False):
        chips_html = "".join(f'<span class="col-chip">{c}</span>' for c in KEPLER_FIELDS)
        st.markdown(chips_html, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your `.csv` telemetry file here",
        type=["csv"],
        key="csv_uploader",
    )

    if uploaded_file is not None:
        # Preview the uploaded data
        try:
            preview_df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem 1.5rem;">
                <span style="color: #64b5f6;">📄</span>
                <strong>{uploaded_file.name}</strong>
                <span style="color: #5a6a8a;"> — {len(preview_df)} rows, {len(preview_df.columns)} columns</span>
            </div>
            """, unsafe_allow_html=True)

            # Client-side column validation
            missing = [c for c in KEPLER_FIELDS if c not in preview_df.columns]
            extra   = [c for c in preview_df.columns if c not in KEPLER_FIELDS]

            if missing:
                st.error(f"❌ **Missing required columns:** {', '.join(missing)}")
            else:
                if extra:
                    st.warning(f"⚠️ Extra columns will be filtered by the model: {', '.join(extra)}")

                with st.expander("Preview uploaded data", expanded=False):
                    st.dataframe(preview_df.head(10), use_container_width=True)

                if st.button("🚀 LAUNCH BULK ANALYSIS", use_container_width=True):
                    with st.spinner("Processing signal batch through classification engine…"):
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
                            st.error("❌ **Signal lost — cannot reach backend.**  Verify FastAPI is running at `" + API_BASE + "`.")
                        except requests.exceptions.HTTPError as e:
                            detail = ""
                            try:
                                detail = e.response.json().get("detail", "")
                            except Exception:
                                detail = str(e)
                            st.error(f"❌ Backend transmission error: {detail}")
        except Exception as ex:
            st.error(f"Failed to parse CSV telemetry: {ex}")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.phase1_results is not None:
    st.markdown("""
    <div style="margin-top: 2rem;">
        <div class="section-header">📊 Phase 1 Results — Exoplanet Discovery</div>
    </div>
    """, unsafe_allow_html=True)

    # ── SINGLE RESULT ─────────────────────────────────────────────────────────
    if st.session_state.phase1_mode == "single":
        result = st.session_state.phase1_results
        prediction = result.get("prediction", "UNKNOWN")
        is_confirmed = prediction == "CONFIRMED"

        card_class = "result-confirmed" if is_confirmed else "result-false"
        icon = "✅" if is_confirmed else "❌"
        glow_color = "46, 204, 113" if is_confirmed else "231, 76, 60"

        st.markdown(f"""
        <div class="result-card {card_class}">
            <h1 style="font-family: 'Orbitron', sans-serif; position:relative; z-index:1;">{icon} {prediction}</h1>
            <p style="font-family: 'Exo 2', sans-serif; position:relative; z-index:1;">
                Classification engine determined this signal as <strong>{prediction}</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.metric("Classification", prediction)
        col2.metric("Raw Model Output", result.get("raw_output", "—"))

    # ── CSV TABLE RESULT ──────────────────────────────────────────────────────
    elif st.session_state.phase1_mode == "csv":
        api_resp = st.session_state.phase1_results["api_response"]
        original_df = st.session_state.phase1_results["original_df"]
        predictions = api_resp.get("predictions", [])
        total = api_resp.get("total_processed", len(predictions))

        st.success(f"✅ Successfully processed **{total}** signals.")

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
        m1.metric("Total Signals", total)
        m2.metric("🟢 Confirmed", confirmed_count)
        m3.metric("🔴 False Positive", false_count)

        # Color the Prediction column for display
        def highlight_prediction(val):
            if val == "CONFIRMED":
                return "background-color: #0a3d1e; color: #2ecc71; font-weight: 600;"
            elif val == "FALSE POSITIVE":
                return "background-color: #3d0a0a; color: #e74c3c; font-weight: 600;"
            return ""

        styled_df = result_df.style.map(highlight_prediction, subset=["Prediction"])
        st.dataframe(styled_df, use_container_width=True, height=500)

