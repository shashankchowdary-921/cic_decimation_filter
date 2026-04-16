
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import subprocess, os, tempfile, re

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CIC Filter Simulator | Team Mavericks",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# GLOBAL STYLES — Clean, Readable, Professional
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fira+Code:wght@300;400;500;600&family=Playfair+Display:wght@700;800&display=swap');

  /* ── Root & Body ── */
  html, body, [data-testid="stApp"] {
    background: #0f1117;
    color: #dde3ee;
    font-family: 'Outfit', sans-serif;
  }
  .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1300px; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #161b26;
    border-right: 1px solid #252d3d;
  }
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Outfit', sans-serif;
    color: #7c9cff;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 700;
  }
  [data-testid="stSidebar"] label {
    font-family: 'Outfit', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #a8b5cc !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #161b26;
    border-bottom: 2px solid #252d3d;
    gap: 0;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.3px;
    color: #64748b;
    border-radius: 0;
    padding: 12px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s ease;
    background: transparent;
  }
  .stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #7c9cff !important;
    border-bottom: 2px solid #7c9cff !important;
    box-shadow: none !important;
  }
  .stTabs [data-baseweb="tab-panel"] {
    background: #0f1117;
    padding-top: 1.5rem;
  }

  /* ── Metric Cards ── */
  div[data-testid="metric-container"] {
    background: #161b26;
    border: 1px solid #252d3d;
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  div[data-testid="metric-container"]:hover {
    border-color: #7c9cff;
    box-shadow: 0 4px 20px rgba(124,156,255,0.1);
  }
  div[data-testid="metric-container"] label {
    color: #7c9cff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
  }
  div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Fira Code', monospace !important;
    color: #f0f4ff !important;
    font-size: 1.2rem !important;
    font-weight: 500 !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: #1e2a4a;
    border: 1px solid #3d5a9e;
    color: #a8c0ff;
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-radius: 8px;
    padding: 10px 24px;
    transition: all 0.2s ease;
    width: 100%;
  }
  .stButton > button:hover {
    background: #2a3d6b;
    border-color: #7c9cff;
    color: #ffffff;
    box-shadow: 0 4px 16px rgba(124,156,255,0.25);
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3d6fff, #5a82ff);
    border: none;
    color: white;
    font-weight: 700;
    box-shadow: 0 4px 16px rgba(61,111,255,0.4);
  }
  .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #5a82ff, #7c9cff);
    box-shadow: 0 6px 24px rgba(124,156,255,0.5);
    transform: translateY(-1px);
  }

  /* ── Info / Alert boxes ── */
  .stInfo { background: #161b26; border-left: 3px solid #7c9cff; border-radius: 0 8px 8px 0; }
  .stSuccess { background: #0d1f1a; border-left: 3px solid #4ade80; border-radius: 0 8px 8px 0; }
  .stWarning { background: #1f1a0d; border-left: 3px solid #fbbf24; border-radius: 0 8px 8px 0; }
  .stError { background: #1f0d0d; border-left: 3px solid #f87171; border-radius: 0 8px 8px 0; }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    background: #161b26 !important;
    border: 1px solid #252d3d !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #7c9cff !important;
  }
  .streamlit-expanderContent {
    background: #161b26 !important;
    border: 1px solid #252d3d !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
  }

  hr { border-color: #252d3d !important; margin: 1rem 0 !important; }

  /* ── Hero Banner ── */
  .hero-banner {
    background: linear-gradient(135deg, #161b26 0%, #1a2138 60%, #161b26 100%);
    border: 1px solid #252d3d;
    border-top: 3px solid #7c9cff;
    border-radius: 16px;
    padding: 28px 36px 24px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }
  .hero-banner::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(124,156,255,0.07) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 800;
    color: #f0f4ff;
    margin: 0;
    line-height: 1.2;
  }
  .hero-title span { color: #7c9cff; }
  .hero-sub {
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    color: #4a5568;
    margin-top: 6px;
    letter-spacing: 1px;
  }
  .hero-badge {
    display: inline-block;
    font-family: 'Outfit', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #38bdf8;
    text-transform: uppercase;
    border: 1px solid rgba(56,189,248,0.35);
    border-radius: 20px;
    padding: 4px 14px;
    background: rgba(56,189,248,0.06);
    margin-bottom: 10px;
  }

  /* ── Author Cards ── */
  .author-grid { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
  .author-card {
    background: rgba(124,156,255,0.07);
    border: 1px solid #252d3d;
    border-radius: 10px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.2s ease;
    min-width: 170px;
  }
  .author-card:hover { border-color: #7c9cff; background: rgba(124,156,255,0.12); }
  .author-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Playfair Display', serif;
    font-size: 16px; font-weight: 700;
    color: white;
    flex-shrink: 0;
  }
  .author-name {
    font-family: 'Outfit', sans-serif;
    font-size: 13px; font-weight: 600;
    color: #dde3ee;
    line-height: 1.2;
  }
  .author-reg {
    font-family: 'Fira Code', monospace;
    font-size: 10px; color: #64748b;
    margin-top: 2px;
  }

  /* ── Section Headers ── */
  .section-header {
    font-family: 'Outfit', sans-serif;
    font-size: 13px; font-weight: 700;
    letter-spacing: 1px; color: #7c9cff;
    text-transform: uppercase;
    border-bottom: 1px solid #252d3d;
    padding-bottom: 10px;
    margin-bottom: 18px; margin-top: 10px;
  }

  /* ── Explanation Cards ── */
  .explain-card {
    background: #161b26;
    border: 1px solid #252d3d;
    border-left: 3px solid #7c9cff;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 12px 0;
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    color: #8899b3;
    line-height: 1.6;
  }
  .explain-card strong { color: #dde3ee; font-weight: 600; }
  .explain-card .ec-title {
    font-size: 11px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    color: #7c9cff; margin-bottom: 6px;
  }
  .ec-green { border-left-color: #4ade80; }
  .ec-green .ec-title { color: #4ade80; }
  .ec-orange { border-left-color: #fb923c; }
  .ec-orange .ec-title { color: #fb923c; }
  .ec-purple { border-left-color: #c084fc; }
  .ec-purple .ec-title { color: #c084fc; }
  .ec-cyan { border-left-color: #22d3ee; }
  .ec-cyan .ec-title { color: #22d3ee; }

  /* ── Result Badge ── */
  .result-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0d1f1a; border: 1px solid #4ade80;
    border-radius: 20px; padding: 4px 14px;
    font-family: 'Fira Code', monospace;
    font-size: 12px; color: #4ade80;
    margin: 4px 4px 4px 0;
  }
  .result-badge.bad { background: #1f0d0d; border-color: #f87171; color: #f87171; }
  .result-badge.warn { background: #1f1a0d; border-color: #fbbf24; color: #fbbf24; }
  .result-badge.info { background: #0d1020; border-color: #7c9cff; color: #7c9cff; }

  /* ── Verilog Output Table ── */
  .vlog-table-wrap {
    background: #0b0f1a;
    border: 1px solid #252d3d;
    border-radius: 10px;
    overflow: hidden;
    margin: 12px 0;
  }
  .vlog-table { width: 100%; border-collapse: collapse; font-family: 'Fira Code', monospace; font-size: 12px; }
  .vlog-table th {
    background: #161b26; color: #7c9cff;
    font-family: 'Outfit', sans-serif;
    font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
    padding: 10px 16px; border-bottom: 1px solid #252d3d; text-align: left;
  }
  .vlog-table td { color: #8899b3; padding: 8px 16px; border-bottom: 1px solid #1a2030; }
  .vlog-table tr:last-child td { border-bottom: none; }
  .vlog-table tr:hover td { background: #161b26; color: #dde3ee; }
  .vlog-table .val-col { color: #4ade80; font-weight: 500; }
  .vlog-table .idx-col { color: #7c9cff; }

  /* ── Code blocks ── */
  .stCode, code { font-family: 'Fira Code', monospace !important; }

  /* ── Sidebar input groups ── */
  .sidebar-group {
    background: #1a2030;
    border: 1px solid #252d3d;
    border-radius: 10px;
    padding: 14px 14px 10px;
    margin-bottom: 14px;
  }
  .sidebar-group-title {
    font-family: 'Outfit', sans-serif;
    font-size: 10px; font-weight: 700;
    letter-spacing: 1.5px; color: #4a5568;
    text-transform: uppercase; margin-bottom: 10px;
  }

  /* ── Table ── */
  table { width: 100%; border-collapse: collapse; font-family: 'Fira Code', monospace; font-size: 12px; }
  th {
    background: #161b26; color: #7c9cff;
    font-family: 'Outfit', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 1px; padding: 10px 14px; border: 1px solid #252d3d; text-transform: uppercase;
  }
  td { background: #0f1117; color: #8899b3; padding: 9px 14px; border: 1px solid #252d3d; }
  tr:hover td { background: #161b26; color: #dde3ee; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: #0f1117; }
  ::-webkit-scrollbar-thumb { background: #252d3d; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #7c9cff; }

  /* ── Select/Slider ── */
  .stSelectbox label, .stSlider label, .stSelectSlider label {
    font-family: 'Outfit', sans-serif !important;
    font-size: 13px !important; color: #a8b5cc !important; font-weight: 500 !important;
  }
  .stRadio label, .stCheckbox label {
    font-family: 'Outfit', sans-serif; color: #8899b3; font-size: 13px;
  }

  /* ── Hint text ── */
  .input-hint {
    font-family: 'Outfit', sans-serif;
    font-size: 11px; color: #4a5568;
    margin-top: -8px; margin-bottom: 8px;
    padding: 0 2px;
    line-height: 1.4;
  }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR — Properly Labelled Inputs
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 12px;">
      <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:800;color:#f0f4ff;">
        🔬 CIC Filter
      </div>
      <div style="font-family:'Fira Code',monospace;font-size:10px;color:#4a5568;
                  letter-spacing:2px;margin-top:4px;">CONTROL PANEL</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Filter Architecture Group ──
    st.markdown("""<div class="sidebar-group-title">⚙️ Filter Architecture</div>""",
                unsafe_allow_html=True)
    architecture = st.selectbox(
        "Architecture Type",
        ["Pipelined", "Basic", "Folded"],
        help="How the filter is implemented in hardware",
    )
    ARCH_HINTS = {
        "Pipelined": "Fastest clock speed — pipeline register after every stage. Best for high-speed designs.",
        "Basic": "Standard CIC — integrators then downsampler then comb sections. Simple and efficient.",
        "Folded": "Area-saving — single shared adder reused N times. Best when chip area is limited.",
    }
    st.markdown(f'<div class="input-hint">💡 {ARCH_HINTS[architecture]}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sample Rate Group ──
    st.markdown("""<div class="sidebar-group-title">📡 Sample Rates</div>""", unsafe_allow_html=True)
    FS_MAP = {
        "500 kHz": 500_000, "1 MHz": 1_000_000, "2 MHz": 2_000_000,
        "4 MHz": 4_000_000, "8 MHz": 8_000_000, "16 MHz": 16_000_000,
        "20 MHz": 20_000_000, "32 MHz": 32_000_000, "40 MHz": 40_000_000,
        "48 MHz": 48_000_000, "64 MHz": 64_000_000, "80 MHz": 80_000_000,
        "96 MHz": 96_000_000, "100 MHz": 100_000_000, "128 MHz": 128_000_000,
        "200 MHz": 200_000_000, "256 MHz": 256_000_000, "500 MHz": 500_000_000,
    }
    fs_label = st.selectbox(
        "Input Sample Rate (Fs_in)",
        list(FS_MAP.keys()), index=4,
        help="Rate at which the ADC or source produces samples. Integrators run at this speed."
    )
    fs_in = FS_MAP[fs_label]
    st.markdown('<div class="input-hint">Rate at which input samples arrive (before decimation)</div>',
                unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Filter Parameters Group ──
    st.markdown("""<div class="sidebar-group-title">🔧 Filter Parameters</div>""", unsafe_allow_html=True)

    R = st.select_slider(
        "Decimation Factor (R)",
        options=[2, 4, 8, 16, 32, 64, 128, 256], value=4,
        help="How much to reduce the sample rate. Output rate = Input rate ÷ R"
    )
    st.markdown(f'<div class="input-hint">Output rate = {fs_label} ÷ {R}</div>', unsafe_allow_html=True)

    N = st.slider(
        "Number of Stages (N)", 1, 6, 2,
        help="More stages = sharper roll-off & better alias rejection, but more hardware"
    )
    st.markdown(f'<div class="input-hint">More stages → steeper filter, more bits needed</div>',
                unsafe_allow_html=True)

    M = st.select_slider(
        "Differential Delay (M)", options=[1, 2], value=1,
        help="Delay used inside each comb section. M=1 is most common. M=2 improves stopband slightly."
    )
    st.markdown('<div class="input-hint">M=1 standard · M=2 slightly better stopband</div>',
                unsafe_allow_html=True)

    fs_out = fs_in / R
    if fs_out >= 1e6:
        fs_out_str = f"{fs_out/1e6:.3f} MHz"
    elif fs_out >= 1e3:
        fs_out_str = f"{fs_out/1e3:.2f} kHz"
    else:
        fs_out_str = f"{fs_out:.1f} Hz"

    st.markdown(f"""
    <div style="background:#1a2a1a;border:1px solid #2a4a2a;border-radius:10px;
                padding:12px 16px;margin:12px 0;">
      <div style="font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;
                  color:#4ade80;letter-spacing:1.5px;text-transform:uppercase;">Output Sample Rate</div>
      <div style="font-family:'Fira Code',monospace;font-size:20px;
                  color:#f0f4ff;font-weight:600;margin-top:4px;">{fs_out_str}</div>
      <div style="font-family:'Outfit',sans-serif;font-size:11px;color:#4a5568;margin-top:2px;">
        Comb sections & output run at this rate
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Test Signal Group ──
    st.markdown("""<div class="sidebar-group-title">🎚️ Test Signal</div>""", unsafe_allow_html=True)
    sig_type = st.selectbox(
        "Signal Type",
        ["Sine", "Ramp", "DC", "Multi-tone", "Chirp", "Square", "Random Noise"],
        help="Shape of the test input signal applied to the filter"
    )
    SIG_HINTS = {
        "Sine": "Single frequency tone — best for SNR / THD tests",
        "Ramp": "Linearly increasing signal — tests DC tracking",
        "DC": "Constant value — filter should pass through unchanged",
        "Multi-tone": "3 harmonics — reveals intermodulation distortion",
        "Chirp": "Frequency sweep — shows filter's frequency response",
        "Square": "Rich in harmonics — tests harmonic suppression",
        "Random Noise": "White noise — for measuring noise floor",
    }
    st.markdown(f'<div class="input-hint">{SIG_HINTS[sig_type]}</div>', unsafe_allow_html=True)

    max_f = max(10, int(fs_out / 3))
    f_sig = st.slider(
        "Signal Frequency (Hz)", 10, max_f, min(1000, max_f // 4),
        help="Frequency of the test signal. Should be below Fs_out/2 to avoid aliasing."
    )
    st.markdown(
        f'<div class="input-hint">Keep below {fs_out/2:.0f} Hz (Nyquist limit at output)</div>',
        unsafe_allow_html=True,
    )

    noise_db = st.slider(
        "Added Noise Level (dBFS)", -80, 0, -40,
        help="Amplitude of random noise added to the test signal. -40 dB is moderate, -80 dB is nearly clean."
    )
    noise_labels = {
        range(-80, -60): "very clean signal",
        range(-60, -40): "clean signal",
        range(-40, -20): "moderate noise",
        range(-20, 1): "noisy signal",
    }
    nl = next((v for k, v in noise_labels.items() if noise_db in k), "")
    st.markdown(f'<div class="input-hint">{noise_db} dBFS → {nl}</div>', unsafe_allow_html=True)

    n_samples = st.select_slider(
        "Number of Input Samples",
        options=[128, 256, 512, 1024, 2048, 4096], value=512,
        help="How many input samples to simulate. More samples = better spectral resolution."
    )
    st.markdown(f'<div class="input-hint">Gives {n_samples // R} output samples after decimation</div>',
                unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Outfit',sans-serif;font-size:10px;color:#252d3d;
                letter-spacing:1px;text-align:center;padding-top:4px;text-transform:uppercase;">
      Team Mavericks · DSP Project · 2024
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIGNAL GENERATOR
# ──────────────────────────────────────────────────────────────
np.random.seed(42)

def make_signal(kind, n, fs, f0, noise_db):
    t   = np.arange(n) / fs
    amp = 10 ** (noise_db / 20)
    nz  = amp * np.random.randn(n)
    if kind == "Sine":          return np.sin(2*np.pi*f0*t) + nz
    elif kind == "Ramp":        return (np.arange(n) % 20) * 0.05 + nz
    elif kind == "DC":          return np.ones(n) * 0.5 + nz
    elif kind == "Multi-tone":
        s = (np.sin(2*np.pi*f0*t) + 0.5*np.sin(2*np.pi*f0*3*t) + 0.3*np.sin(2*np.pi*f0*7*t))
        return s / np.max(np.abs(s)+1e-12) + nz
    elif kind == "Chirp":
        f_end = min(f0*10, fs/2.5)
        return np.sin(2*np.pi*(f0+(f_end-f0)*t/(n/fs))*t) + nz
    elif kind == "Square":      return np.sign(np.sin(2*np.pi*f0*t)) + nz
    else:                       return np.random.randn(n)

x_in_raw = make_signal(sig_type, n_samples, fs_in, f_sig, noise_db)

# ──────────────────────────────────────────────────────────────
# CIC FILTER MODELS
# ──────────────────────────────────────────────────────────────
def apply_comb(y, M):
    y = np.asarray(y, dtype=float)
    out = np.empty_like(y)
    out[:M] = y[:M]
    out[M:] = y[M:] - y[:-M]
    return out

def cic_basic(x, R, N, M=1):
    y = x.astype(float)
    for _ in range(N): y = np.cumsum(y)
    y = y[::R].copy()
    for _ in range(N): y = apply_comb(y, M)
    return y

def cic_pipelined(x, R, N, M=1):
    y = x.astype(float)
    for _ in range(N):
        y = np.cumsum(y)
        reg = np.roll(y, 1); reg[0] = 0.0; y = reg
    y = y[::R].copy()
    for _ in range(N):
        y = apply_comb(y, M)
        reg = np.roll(y, 1); reg[0] = 0.0; y = reg
    return y

def cic_folded(x, R, N, M=1):
    return cic_basic(x, R, N, M)

def freq_response(R, N, M, fs, npts=4096):
    f = np.linspace(1e-6, fs/2, npts)
    with np.errstate(divide="ignore", invalid="ignore"):
        num = np.sin(np.pi*M*R*f/fs)
        den = np.sin(np.pi*f/fs)
        ratio = np.where(np.abs(den)<1e-10, float(M*R), np.abs(num/den))
    H = (ratio/(M*R))**N
    return f, 20*np.log10(np.maximum(H, 1e-12))

def bit_growth(R, N, M=1):
    return N * int(np.ceil(np.log2(R*M + 1e-9)))

def snr_calc(sig, f0, fs):
    nfft = 2048
    Y  = np.abs(np.fft.rfft(sig, n=nfft))**2
    fr = np.fft.rfftfreq(nfft, 1/fs)
    idx = np.argmin(np.abs(fr - f0))
    sp  = Y[max(0, idx-2):idx+3].sum()
    np_ = Y.sum() - sp
    return 10*np.log10(sp / max(np_, 1e-30))

def sfdr_calc(sig, fs):
    nfft = 2048
    Y  = np.abs(np.fft.rfft(sig, n=nfft))
    peak_idx = np.argmax(Y)
    mask = np.ones(len(Y), dtype=bool)
    mask[max(0,peak_idx-3):peak_idx+4] = False
    return 20*np.log10(Y[peak_idx] / (np.max(Y[mask]) + 1e-30))

def thd_calc(sig, f0, fs, harmonics=5):
    nfft = 2048
    Y  = np.abs(np.fft.rfft(sig, n=nfft))
    fr = np.fft.rfftfreq(nfft, 1/fs)
    fund_idx = np.argmin(np.abs(fr - f0))
    fund_pow = Y[fund_idx]**2
    harm_pow = 0
    for h in range(2, harmonics+1):
        hf = h * f0
        if hf < fs/2:
            hi = np.argmin(np.abs(fr - hf))
            harm_pow += Y[hi]**2
    return 10*np.log10(harm_pow / max(fund_pow, 1e-30))

# ── Run chosen architecture ──
if architecture == "Pipelined":
    y_out = cic_pipelined(x_in_raw, R, N, M)
elif architecture == "Folded":
    y_out = cic_folded(x_in_raw, R, N, M)
else:
    y_out = cic_basic(x_in_raw, R, N, M)

guard  = min(N*M, len(y_out)//4)
y_norm = y_out[guard:]
y_norm = y_norm / (np.max(np.abs(y_norm))+1e-12)
x_norm = x_in_raw / (np.max(np.abs(x_in_raw))+1e-12)

t_in  = np.arange(n_samples) / fs_in * 1e6
t_out = np.arange(len(y_out)) * R / fs_in * 1e6
f_ax, H_db = freq_response(R, N, M, fs_in)

# ──────────────────────────────────────────────────────────────
# VERILOG RUNNER
# ──────────────────────────────────────────────────────────────
VLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verilog")

def find_verilog():
    candidates = [VLOG_DIR, os.path.dirname(os.path.abspath(__file__)),
                  "/mount/src/cic_decimation_filter/verilog", "/mount/src/cic_decimation_filter"]
    for d in candidates:
        f = os.path.join(d, "cic_filter.v")
        t = os.path.join(d, "cic_testbench.v")
        if os.path.exists(f) and os.path.exists(t):
            return f, t
    return None, None

def run_iverilog(r_val=4, n_val=2, arch="Pipelined"):
    arch_file_map = {"Pipelined": "cic_filter_pipelined.v", "Folded": "cic_filter_folded.v", "Basic": "cic_filter.v"}
    tb_file_map   = {"Pipelined": "cic_tb_pipelined.v",    "Folded": "cic_tb_folded.v",    "Basic": "cic_testbench.v"}
    candidates = [VLOG_DIR, os.path.dirname(os.path.abspath(__file__)),
                  "/mount/src/cic_decimation_filter/verilog", "/mount/src/cic_decimation_filter"]
    fpath, tpath = None, None
    for d in candidates:
        fp = os.path.join(d, arch_file_map.get(arch, "cic_filter.v"))
        tp = os.path.join(d, tb_file_map.get(arch, "cic_testbench.v"))
        if os.path.exists(fp) and os.path.exists(tp):
            fpath, tpath = fp, tp; break
        fp2 = os.path.join(d, "cic_filter.v"); tp2 = os.path.join(d, "cic_testbench.v")
        if os.path.exists(fp2) and os.path.exists(tp2):
            fpath, tpath = fp2, tp2; break
    if fpath is None:
        return None, f"Verilog files not found for arch='{arch}'.\nExpected: `verilog/{arch_file_map[arch]}` + `verilog/{tb_file_map[arch]}`"
    with tempfile.TemporaryDirectory() as tmp:
        out_bin = os.path.join(tmp, "cic_sim")
        with open(tpath) as f: tb = f.read()
        tb = re.sub(r"\.R\(\d+\)", f".R({r_val})", tb)
        tb = re.sub(r"\.N\(\d+\)", f".N({n_val})", tb)
        tb_mod = os.path.join(tmp, "tb.v")
        with open(tb_mod, "w") as f: f.write(tb)
        try:
            cp = subprocess.run(["iverilog", "-o", out_bin, fpath, tb_mod],
                                capture_output=True, text=True, timeout=15)
        except FileNotFoundError:
            return None, "iverilog not installed. Add `iverilog` to packages.txt."
        except subprocess.TimeoutExpired:
            return None, "Compile timed out."
        if cp.returncode != 0:
            return None, f"Compile error:\n{cp.stderr}"
        try:
            rp = subprocess.run(["vvp", out_bin], capture_output=True, text=True, timeout=15)
        except subprocess.TimeoutExpired:
            return None, "Simulation timed out."
        return rp.stdout + rp.stderr, None

# ──────────────────────────────────────────────────────────────
# PLOTLY DARK DEFAULTS
# ──────────────────────────────────────────────────────────────
DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0b0f1a",
    font=dict(color="#64748b", family="Fira Code"),
    margin=dict(t=55, b=35, l=60, r=25),
)
GRID = dict(gridcolor="#1a2030", zerolinecolor="#252d3d", gridwidth=1)

def apply_dark(fig, height=420):
    fig.update_layout(height=height, **DARK)
    for ax in fig.layout:
        if ax.startswith("xaxis") or ax.startswith("yaxis"):
            fig.layout[ax].update(**GRID)
    fig.update_layout(title_font=dict(family="Outfit", size=13, color="#7c9cff"))
    return fig

# Colour palette
C_BLUE   = "#7c9cff"
C_CYAN   = "#22d3ee"
C_GREEN  = "#4ade80"
C_ORANGE = "#fb923c"
C_PURPLE = "#c084fc"
C_PINK   = "#f472b6"
C_YELLOW = "#fbbf24"

# ──────────────────────────────────────────────────────────────
# HERO BANNER
# ──────────────────────────────────────────────────────────────
bg_bit  = bit_growth(R, N, M)
snr_in  = snr_calc(x_norm, f_sig, fs_in)
snr_out = snr_calc(y_norm, f_sig, fs_out)

st.markdown(f"""
<div class="hero-banner">
  <div class="hero-badge">DSP Project · Team Mavericks</div>
  <div class="hero-title">CIC <span>Decimation</span> Filter Simulator</div>
  <div class="hero-sub">Cascaded Integrator-Comb · Interactive RTL Simulator</div>
  <div class="author-grid">
    <div class="author-card">
      <div class="author-avatar" style="background:linear-gradient(135deg,#3d6fff,#7c9cff);">S</div>
      <div>
        <div class="author-name">Shashank T</div>
        <div class="author-reg">23BVD1031</div>
      </div>
    </div>
    <div class="author-card">
      <div class="author-avatar" style="background:linear-gradient(135deg,#0891b2,#22d3ee);">P</div>
      <div>
        <div class="author-name">Pasyanth P</div>
        <div class="author-reg">23BVD1004</div>
      </div>
    </div>
    <div class="author-card">
      <div class="author-avatar" style="background:linear-gradient(135deg,#7c3aed,#c084fc);">A</div>
      <div>
        <div class="author-name">Abin Mohammed</div>
        <div class="author-reg">23BVD1047</div>
      </div>
    </div>
    <div class="author-card">
      <div class="author-avatar" style="background:linear-gradient(135deg,#166534,#4ade80);">Y</div>
      <div>
        <div class="author-name">Yagnesh M</div>
        <div class="author-reg">23BVD1046</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ──
snr_delta = snr_out - snr_in
kpi_cols = st.columns(7)
kpi_cols[0].metric("Architecture",  architecture)
kpi_cols[1].metric("Input Rate",    fs_label)
kpi_cols[2].metric("Output Rate",   fs_out_str)
kpi_cols[3].metric("Decimation R",  f"÷{R}")
kpi_cols[4].metric("Stages N",      str(N))
kpi_cols[5].metric("Bit Growth",    f"+{bg_bit} bits")
kpi_cols[6].metric("SNR Change",    f"{snr_delta:+.1f} dB")

# ── Interpretation bar ──
snr_interp = "✅ Filter improved SNR" if snr_delta > 1 else ("⚠️ SNR roughly unchanged" if snr_delta > -3 else "⚠️ Check signal/noise settings")
bit_interp = f"Internal registers need {bg_bit} extra bits to avoid overflow (word-length growth)"
st.markdown(f"""
<div style="background:#161b26;border:1px solid #252d3d;border-radius:10px;
            padding:10px 18px;margin:10px 0 18px;display:flex;gap:20px;flex-wrap:wrap;
            font-family:'Outfit',sans-serif;font-size:12px;color:#64748b;">
  <span style="color:#4ade80;">{snr_interp}</span>
  <span>·</span>
  <span>📦 {bit_interp}</span>
  <span>·</span>
  <span>⚡ {n_samples} input → {len(y_out)} output samples</span>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────
tab_sim, tab_freq, tab_arch, tab_stages, tab_metrics, tab_vlog, tab_vcode = st.tabs([
    "🌊 Simulate",
    "📈 Frequency Response",
    "🏗️ Architecture",
    "📊 Stage Analysis",
    "📐 Metrics",
    "⚡ RTL Simulation",
    "📄 Verilog Code",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SIMULATE
# ══════════════════════════════════════════════════════════════
with tab_sim:
    st.markdown('<div class="section-header">Time-Domain Waveforms</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="explain-card">
      <div class="ec-title">What am I looking at?</div>
      The <strong>left plots</strong> show the input signal (before filtering) and the output signal (after CIC decimation).
      The sample rate drops by factor R, so the output has fewer points.
      The <strong>right plots</strong> show the frequency spectrum — peaks represent signal components.
      Noise floor dropping in the output means the filter is working correctly.
    </div>
    """, unsafe_allow_html=True)

    disp_in  = min(n_samples, 300)
    disp_out = min(len(y_out), 300)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"📥 Input Signal  ·  {fs_label}  ·  {n_samples} samples",
            f"📤 Output Signal  ·  {fs_out_str}  ·  {len(y_out)} samples (after ÷{R})",
            "📊 Input Spectrum — frequency content of the input",
            "📊 Output Spectrum — frequency content after filtering",
        ],
        vertical_spacing=0.20, horizontal_spacing=0.08,
    )
    fig.add_trace(go.Scatter(
        x=t_in[:disp_in], y=x_norm[:disp_in], mode="lines",
        line=dict(color=C_BLUE, width=1.5),
        fill='tozeroy', fillcolor="rgba(124,156,255,0.07)", name="Input x[n]"
    ), row=1, col=1)

    y_fnorm = y_out / (np.max(np.abs(y_out))+1e-12)
    fig.add_trace(go.Scatter(
        x=t_out[:disp_out], y=y_fnorm[:disp_out], mode="lines",
        line=dict(color=C_GREEN, width=1.8),
        fill='tozeroy', fillcolor="rgba(74,222,128,0.07)", name="Output y[m]"
    ), row=1, col=2)

    nfft = 2048
    X  = np.abs(np.fft.rfft(x_norm, n=nfft)) / nfft
    fx = np.fft.rfftfreq(nfft, 1/fs_in) / 1e3
    fig.add_trace(go.Scatter(
        x=fx, y=20*np.log10(np.maximum(X,1e-10)),
        mode="lines", line=dict(color=C_BLUE, width=1.0), name="Input PSD"
    ), row=2, col=1)

    Y  = np.abs(np.fft.rfft(y_norm, n=nfft)) / nfft
    fy = np.fft.rfftfreq(nfft, R/fs_in) / 1e3
    fig.add_trace(go.Scatter(
        x=fy, y=20*np.log10(np.maximum(Y,1e-10)),
        mode="lines", line=dict(color=C_GREEN, width=1.0), name="Output PSD"
    ), row=2, col=2)

    fig.update_xaxes(title_text="Time (µs)", title_font=dict(size=11, color="#64748b"), row=1, col=1)
    fig.update_xaxes(title_text="Time (µs) — fewer samples due to ÷R decimation",
                     title_font=dict(size=11, color="#64748b"), row=1, col=2)
    fig.update_xaxes(title_text="Frequency (kHz)", title_font=dict(size=11, color="#64748b"),
                     range=[0, min(fs_in/2e3, 200)], row=2, col=1)
    fig.update_xaxes(title_text="Frequency (kHz) — narrower range after decimation",
                     title_font=dict(size=11, color="#64748b"), range=[0, fs_out/2e3], row=2, col=2)
    fig.update_yaxes(title_text="Amplitude (normalised 0→1)", title_font=dict(size=10, color="#64748b"),
                     row=1, col=1)
    fig.update_yaxes(title_text="Amplitude (normalised 0→1)", title_font=dict(size=10, color="#64748b"),
                     row=1, col=2)
    fig.update_yaxes(title_text="Power (dBFS)", title_font=dict(size=10, color="#64748b"),
                     range=[-100, 5], row=2, col=1)
    fig.update_yaxes(title_text="Power (dBFS) — 0 dBFS = full scale",
                     title_font=dict(size=10, color="#64748b"), range=[-100, 5], row=2, col=2)

    for ann in fig.layout.annotations:
        ann.font = dict(family="Outfit", size=11, color="#a8b5cc")
    apply_dark(fig, height=580)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # ── Metrics with interpretation ──
    sfdr_out = sfdr_calc(y_norm, fs_out)
    thd_out  = thd_calc(y_norm, f_sig, fs_out) if sig_type in ["Sine","Square","Multi-tone"] else float('nan')

    st.markdown('<div class="section-header">Signal Quality Metrics — Output</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="explain-card ec-cyan">
      <div class="ec-title">How to read these metrics</div>
      <strong>SNR</strong> = Signal-to-Noise Ratio — higher is better (clean signal).
      <strong>SFDR</strong> = Spurious-Free Dynamic Range — gap between signal peak and next largest spur, higher is better.
      <strong>THD</strong> = Total Harmonic Distortion — power in harmonics relative to fundamental, less negative (closer to 0) means more distortion.
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Input SNR",         f"{snr_in:.1f} dB",  help="Signal quality before filtering")
    m2.metric("Output SNR",        f"{snr_out:.1f} dB", help="Signal quality after filtering — should be ≥ Input SNR")
    m3.metric("SNR Improvement",   f"{snr_delta:+.1f} dB",
              delta=f"{snr_delta:+.1f} dB",
              help="Positive = filter improved SNR. Expected gain ≈ 10·log10(R) = {:.1f} dB".format(10*np.log10(R)))
    m4.metric("SFDR (output)",     f"{sfdr_out:.1f} dB", help="Higher = fewer spurious tones. >60 dB is good.")
    thd_str = f"{thd_out:.1f} dB" if not np.isnan(thd_out) else "N/A (use Sine/Square)"
    m5.metric("THD (output)",      thd_str, help="Total Harmonic Distortion. More negative = less distortion.")

    # Interpretation badges
    def snr_badge(v):
        if v > 60:   return "good", "Excellent SNR"
        elif v > 40: return "info", "Good SNR"
        elif v > 20: return "warn", "Moderate SNR"
        else:        return "bad",  "Low SNR — increase signal or reduce noise"
    cls, lbl = snr_badge(snr_out)
    sfdr_cls = "good" if sfdr_out > 60 else ("info" if sfdr_out > 40 else "warn")
    st.markdown(f"""
    <div style="margin-top:10px;">
      <span class="result-badge {'bad' if cls=='bad' else ('warn' if cls=='warn' else '')}">
        SNR: {lbl}
      </span>
      <span class="result-badge {'warn' if sfdr_cls=='warn' else ''}">
        SFDR: {'Good — spurs well suppressed' if sfdr_out > 60 else ('Moderate — some spurious tones' if sfdr_out > 40 else 'Low — check signal purity')}
      </span>
      <span class="result-badge info">
        Expected SNR gain ≈ {10*np.log10(R):.1f} dB for R={R}
      </span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — FREQUENCY RESPONSE
# ══════════════════════════════════════════════════════════════
with tab_freq:
    st.markdown('<div class="section-header">CIC Filter Frequency Response</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="explain-card">
      <div class="ec-title">What this shows</div>
      The magnitude response shows <strong>how much each frequency is attenuated</strong> by the CIC filter.
      0 dB = no attenuation (passes through). −60 dB = signal reduced to 1/1000 of its original level.
      The <strong>passband</strong> is the region of frequencies you want to keep (left of the green line).
      The <strong>stopband</strong> is where aliases must be rejected (should be well below −40 dB or more).
    </div>
    """, unsafe_allow_html=True)

    col_main, col_ctrl = st.columns([4, 1])
    with col_ctrl:
        st.markdown("**Display Options**")
        show_alias = st.checkbox("Show alias bands", value=True, help="Red lines mark where aliased copies land")
        show_pb    = st.checkbox("Show passband edge", value=True, help="Green line = 40% of output Nyquist")
        show_comp  = st.checkbox("Show compensation curve", value=False,
                                 help="A droop-correction gain to flatten the passband")
        f_lim      = st.slider("Frequency display range (MHz)", 0.1,
                               max(0.2, fs_in/2e6), min(fs_in/2e6, 8.0), step=0.1)
        y_min_db   = st.slider("Minimum Y axis (dB)", -160, -20, -120,
                               help="Set lower to see deeper into the stopband")

    with col_main:
        mask = f_ax <= f_lim*1e6
        fig_fr = go.Figure()
        fig_fr.add_trace(go.Scatter(
            x=f_ax[mask]/1e6, y=H_db[mask], mode="lines",
            line=dict(color=C_BLUE, width=2.2), name="|H(f)| — CIC response",
            fill='tozeroy', fillcolor="rgba(124,156,255,0.05)"
        ))
        if show_comp:
            f_comp = f_ax[mask]
            h_comp_inv = -H_db[mask] * 0.5
            fig_fr.add_trace(go.Scatter(
                x=f_comp/1e6, y=h_comp_inv, mode="lines",
                line=dict(color=C_GREEN, width=1.5, dash="dot"), name="Compensation gain"
            ))
            fig_fr.add_trace(go.Scatter(
                x=f_comp/1e6, y=H_db[mask] + h_comp_inv, mode="lines",
                line=dict(color=C_YELLOW, width=1.5), name="Compensated response"
            ))
        if show_alias:
            for k in range(1, 6):
                fa = k * fs_out
                if fa < f_lim*1e6:
                    fig_fr.add_vline(x=fa/1e6,
                        line=dict(color="#ef4444", dash="dot", width=1),
                        annotation_text=f"Alias {k}  ({fa/1e6:.2f} MHz)",
                        annotation_font=dict(size=9, color="#ef4444"))
        if show_pb:
            fig_fr.add_vline(x=0.4*fs_out/1e6,
                line=dict(color=C_GREEN, dash="dash", width=1.5),
                annotation_text=f"Passband edge ({0.4*fs_out/1e3:.1f} kHz)",
                annotation_font=dict(size=9, color=C_GREEN))
        fig_fr.add_hline(y=-3,  line=dict(color=C_ORANGE, dash="dash", width=1),
                         annotation_text="-3 dB (half power)",
                         annotation_font=dict(size=9, color=C_ORANGE))
        fig_fr.add_hline(y=-40, line=dict(color="#4a5568", dash="dot", width=1),
                         annotation_text="-40 dB (good rejection)",
                         annotation_font=dict(size=9, color="#4a5568"))
        fig_fr.update_layout(
            title=f"CIC Frequency Response  [N={N} stages, R={R} decimation, M={M} delay, Fs_in={fs_in/1e6:.1f} MHz]",
            xaxis_title="Frequency (MHz)", yaxis_title="Attenuation (dB)  — 0 dB = no loss, negative = signal reduced",
            xaxis_range=[0, f_lim], yaxis_range=[y_min_db, 5],
            legend=dict(bgcolor="rgba(11,15,26,0.9)", bordercolor="#252d3d",
                        font=dict(family="Fira Code", size=11)),
        )
        apply_dark(fig_fr)
        st.plotly_chart(fig_fr, use_container_width=True)

    st.markdown('<div class="section-header">Passband Detail — Droop in the signal band</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="explain-card ec-orange">
      <div class="ec-title">Passband Droop</div>
      CIC filters are not perfectly flat — they roll off (droop) even within the passband.
      This plot zooms in on the passband (0 to Fs_out/2) to show how much droop occurs.
      At the Nyquist limit (Fs_out/2) the response is typically −3 dB to −10 dB depending on N and R.
    </div>
    """, unsafe_allow_html=True)
    pb_mask = f_ax <= 0.5*fs_out
    fig_pb  = go.Figure(go.Scatter(
        x=f_ax[pb_mask]/1e3, y=H_db[pb_mask], mode="lines",
        line=dict(color=C_CYAN, width=2),
        fill='tozeroy', fillcolor="rgba(34,211,238,0.05)"
    ))
    fig_pb.add_hline(y=-3, line=dict(color=C_ORANGE, dash="dash"),
                     annotation_text="-3 dB point", annotation_font=dict(size=9, color=C_ORANGE))
    fig_pb.update_layout(
        xaxis_title=f"Frequency (kHz)  →  up to Fs_out/2 = {fs_out/2e3:.2f} kHz",
        yaxis_title="Attenuation (dB)",
        title=f"Passband Droop — zoomed to output band [0 → {fs_out_str}/2]"
    )
    apply_dark(fig_pb, height=290)
    st.plotly_chart(fig_pb, use_container_width=True)

    with st.expander("📋 Attenuation at Key Frequencies"):
        st.markdown("These values tell you how much the CIC filter attenuates signals at specific points:")
        checks = [
            ("Passband edge  (0.4 × Fs_out)", 0.4*fs_out, "Should be close to 0 dB — signal passes through"),
            ("Nyquist limit  (0.5 × Fs_out)", 0.5*fs_out, "Half of output rate — ideally −3 dB or less"),
            ("1st alias band (1.0 × Fs_out)", 1.0*fs_out, "Must be heavily attenuated — ideally < −40 dB"),
            ("2nd alias band (2.0 × Fs_out)", 2.0*fs_out, "Should be attenuated — aliases fold back here"),
            ("3rd alias band (3.0 × Fs_out)", 3.0*fs_out, "Should be attenuated"),
        ]
        rows = []
        for name, fc, interp in checks:
            if fc < fs_in/2:
                idx = np.argmin(np.abs(f_ax - fc))
                val = H_db[idx]
                status = "✅ Good" if (fc <= 0.5*fs_out and val > -6) or (fc > 0.5*fs_out and val < -20) else "⚠️ Check"
                rows.append(f"| {name} | {fc/1e3:.2f} kHz | **{val:.1f} dB** | {status} | {interp} |")
        st.markdown("| Frequency Point | Hz/kHz | Attenuation | Status | Notes |\n|---|---|---|---|---|\n" + "\n".join(rows))

# ══════════════════════════════════════════════════════════════
# TAB 3 — ARCHITECTURE
# ══════════════════════════════════════════════════════════════
with tab_arch:
    st.markdown(f'<div class="section-header">Block Diagram — {architecture} (N={N} stages, R={R}, M={M})</div>',
                unsafe_allow_html=True)

    fig_bd = go.Figure()
    fig_bd.update_layout(
        xaxis=dict(range=[-0.5,14], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1.5, 3], showgrid=False, zeroline=False, visible=False),
        height=300, margin=dict(l=5, r=5, t=60, b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dde3ee"),
    )

    def add_box(fig, cx, cy, label, ec, fc_a=0.18):
        rgb = re.findall(r'\d+', ec)
        r2,g2,b2 = (int(x) for x in rgb[:3])
        fig.add_shape(type="rect",
            x0=cx-0.52, x1=cx+0.52, y0=cy-0.34, y1=cy+0.34,
            line=dict(color=ec, width=2),
            fillcolor=f"rgba({r2},{g2},{b2},{fc_a})")
        fig.add_annotation(x=cx, y=cy, text=label, showarrow=False,
            font=dict(size=10, color="#ffffff", family="Fira Code"), align="center")

    def arr(fig, x0, x1, y=1.0):
        fig.add_annotation(x=x1, y=y, ax=x0, ay=y, axref="x", ayref="y",
            xref="x", yref="y", arrowhead=2, arrowsize=1,
            arrowwidth=1.5, arrowcolor="#3d5a9e")

    C_INT  = "rgb(124,156,255)"
    C_DS   = "rgb(251,146,60)"
    C_COMB = "rgb(74,222,128)"
    C_FF   = "rgb(192,132,252)"
    C_IN   = "rgb(34,211,238)"

    if architecture in ("Basic","Folded"):
        pos  = [0.5] + [1.5+i*1.35 for i in range(N)] + [1.5+N*1.35+0.7]
        pos += [pos[-1]+1.2+i*1.35 for i in range(N)]
        lbls = ["x[n]"]+[f"Σ{i+1}" for i in range(N)]+[f"↓{R}"]+[f"D{i+1}" for i in range(N)]
        cols_bd = [C_IN]+[C_INT]*N+[C_DS]+[C_COMB]*N
        for px, lb, cl in zip(pos, lbls, cols_bd): add_box(fig_bd, px, 1.0, lb, cl)
        for i in range(len(pos)-1): arr(fig_bd, pos[i]+0.52, pos[i+1]-0.52)
        ds_x = pos[N+1]
        fig_bd.add_shape(type="line", x0=ds_x, x1=ds_x, y0=0.52, y1=1.48,
                         line=dict(color="#252d3d", dash="dash"))
        fig_bd.add_annotation(x=ds_x-1.5, y=0.15,
            text=f"← Integrators at {fs_label} →", showarrow=False,
            font=dict(size=9, color="#64748b"))
        fig_bd.add_annotation(x=ds_x+1.5, y=0.15,
            text=f"← Comb sections at {fs_out_str} →", showarrow=False,
            font=dict(size=9, color="#64748b"))
        if architecture == "Folded":
            fig_bd.add_annotation(x=pos[N//2+1], y=2.5,
                text=f"⚡ 1 Shared Adder  ×{N} time-mux  |  Internal clock = {N}× Fs_in",
                showarrow=False, font=dict(size=11, color="#fb923c"),
                bgcolor="rgba(251,146,60,0.08)", bordercolor="#fb923c", borderwidth=1)
    else:
        pos = [0.5]; lbls = ["x[n]"]; cols_bd = [C_IN]
        for i in range(N):
            bx = 1.5+i*2.3
            pos += [bx, bx+0.9]; lbls += [f"Σ{i+1}", "FF"]; cols_bd += [C_INT, C_FF]
        ds_x = pos[-1]+0.95
        pos += [ds_x]; lbls += [f"↓{R}"]; cols_bd += [C_DS]
        for i in range(N):
            bx = ds_x+1.2+i*2.3
            pos += [bx, bx+0.9]; lbls += [f"D{i+1}", "FF"]; cols_bd += [C_COMB, C_FF]
        for px, lb, cl in zip(pos, lbls, cols_bd): add_box(fig_bd, px, 1.0, lb, cl)
        for i in range(len(pos)-1): arr(fig_bd, pos[i]+0.52, pos[i+1]-0.52)
        mid = pos[len(pos)//2]
        fig_bd.add_annotation(x=mid, y=2.5,
            text=f"Pipeline: {2*N} flip-flops deep  |  Latency = {2*N} clock cycles  |  Throughput = 1 sample / clock",
            showarrow=False, font=dict(size=11, color="#c084fc"),
            bgcolor="rgba(192,132,252,0.08)", bordercolor="#a855f7", borderwidth=1)

    apply_dark(fig_bd, height=300)
    st.plotly_chart(fig_bd, use_container_width=True)

    # Legend
    st.markdown("""
    <div style="display:flex;gap:16px;flex-wrap:wrap;padding:8px 0 16px;
                font-family:'Outfit',sans-serif;font-size:12px;">
      <span style="display:flex;align-items:center;gap:6px;">
        <span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:#7c9cff;"></span>
        <span style="color:#a8b5cc;">Integrator (Σ) — accumulates/sums samples, runs at Fs_in</span>
      </span>
      <span style="display:flex;align-items:center;gap:6px;">
        <span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:#fb923c;"></span>
        <span style="color:#a8b5cc;">Downsampler (↓R) — keeps every R-th sample</span>
      </span>
      <span style="display:flex;align-items:center;gap:6px;">
        <span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:#4ade80;"></span>
        <span style="color:#a8b5cc;">Comb (D) — computes y[n]-y[n-M], runs at Fs_out</span>
      </span>
      <span style="display:flex;align-items:center;gap:6px;">
        <span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:#c084fc;"></span>
        <span style="color:#a8b5cc;">Flip-Flop (FF) — pipeline register (Pipelined only)</span>
      </span>
    </div>
    """, unsafe_allow_html=True)

    desc = {
        "Basic": (
            "**Basic CIC:** N integrators run at the input sample rate (Fs_in). "
            "After ↓R downsampling, N comb (differencer) sections run at the lower output rate (Fs_out). "
            "Each comb stage computes `y[n] - y[n-M]`. "
            "No pipeline registers — minimal hardware, but the critical path spans all N adders."
        ),
        "Pipelined": (
            f"**Pipelined CIC:** A flip-flop after every integrator and every comb stage creates a "
            f"**{2*N}-stage deep pipeline**. Critical path = just 1 adder → maximum clock speed. "
            f"Cost: {2*N} extra clock cycles of latency (one-time startup delay). "
            f"Throughput = 1 output every R input clocks."
        ),
        "Folded": (
            f"**Folded CIC:** A single adder is reused {N}× per sample via time-multiplexing. "
            f"The internal clock runs at {N}× Fs_in. Area reduced by ~{2*N-1} adders vs Basic. "
            f"Best when chip area is the main constraint."
        ),
    }
    st.info(desc[architecture])

    with st.expander("📐 Transfer Function & Key Equations"):
        st.latex(r"H(z) = \left(\frac{1 - z^{-RM}}{1 - z^{-1}}\right)^N")
        st.latex(r"|H(f)| = \left|\frac{\sin(\pi M R f/F_s)}{\sin(\pi f/F_s)}\right|^N")
        st.latex(r"\text{Comb: } y[n] = x[n] - x[n-M] \quad \text{(first-order difference with delay M)}")
        col_eq1, col_eq2 = st.columns(2)
        with col_eq1:
            st.markdown(f"""
| Parameter | Value | Meaning |
|-----------|-------|---------|
| N | {N} | Number of stages |
| R | {R} | Decimation factor |
| M | {M} | Differential delay |
| Fs_in | {fs_in/1e6:.3f} MHz | Input sample rate |
| Fs_out | {fs_out_str} | Output sample rate |
""")
        with col_eq2:
            st.markdown(f"""
| Derived Value | Result | Meaning |
|---------------|--------|---------|
| DC gain | {int((M*R)**N)} | Max output value for DC=1 input |
| Bit growth | +{bit_growth(R,N,M)} bits | Extra bits needed inside filter |
| Pipeline depth | {2*N if architecture=="Pipelined" else 0} FFs | Clock cycles of latency |
| Adder count | {"1 (shared)" if architecture=="Folded" else str(2*N)} | Hardware adders used |
| Theoretical SNR gain | +{10*np.log10(R):.1f} dB | Expected improvement |
""")

# ══════════════════════════════════════════════════════════════
# TAB 4 — STAGE ANALYSIS
# ══════════════════════════════════════════════════════════════
with tab_stages:
    st.markdown('<div class="section-header">Per-Stage Output Waveforms</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="explain-card ec-purple">
      <div class="ec-title">What this shows</div>
      Each plot shows the signal at one stage of the CIC pipeline.
      <strong>Integrators</strong> accumulate (sum) all past samples — the waveform grows and "integrates" the input.
      After <strong>downsampling</strong> the signal is shorter (÷R fewer points).
      <strong>Comb sections</strong> take differences, which restores the original signal shape at the lower rate.
      All waveforms are normalised to ±1 so they can be visually compared.
    </div>
    """, unsafe_allow_html=True)

    y_stages, stage_labels, stage_hints = [], [], []
    yc = x_in_raw.astype(float)
    y_stages.append(yc.copy())
    stage_labels.append("📥 Input x[n]")
    stage_hints.append(f"Raw input · {n_samples} samples · {fs_label}")

    for i in range(N):
        yc = np.cumsum(yc)
        if architecture == "Pipelined":
            reg = np.roll(yc,1); reg[0]=0.0; yc=reg
        y_stages.append(yc.copy())
        stage_labels.append(f"Integrator {i+1}" + (" + FF" if architecture=="Pipelined" else ""))
        stage_hints.append(f"Running sum of all previous samples · still at {fs_label}")

    yc_ds = yc[::R]
    y_stages.append(yc_ds.copy())
    stage_labels.append(f"After ↓{R} Downsampler")
    stage_hints.append(f"Sample rate reduced by {R}× · now at {fs_out_str} · {len(yc_ds)} samples")

    yc2 = yc_ds.copy()
    for i in range(N):
        yc2 = apply_comb(yc2, M)
        if architecture == "Pipelined":
            reg = np.roll(yc2,1); reg[0]=0.0; yc2=reg
        y_stages.append(yc2.copy())
        stage_labels.append(f"Comb {i+1}" + (" + FF" if architecture=="Pipelined" else ""))
        stage_hints.append(f"Difference y[n]-y[n-{M}] · undoes the integration · at {fs_out_str}")

    STAGE_COLORS = [C_CYAN, C_BLUE, "#5b7aff", "#3d5ae0",
                    C_ORANGE, "#ef4444", C_GREEN, "#16a34a",
                    C_PURPLE, "#7c3aed", C_PINK, C_YELLOW]

    cols_per_row = 3
    for row_start in range(0, len(y_stages), cols_per_row):
        cols = st.columns(cols_per_row)
        for ci, si in enumerate(range(row_start, min(row_start+cols_per_row, len(y_stages)))):
            s   = y_stages[si]
            lbl = stage_labels[si]
            hint= stage_hints[si]
            col = STAGE_COLORS[si % len(STAGE_COLORS)]
            d   = min(200, len(s))
            with cols[ci]:
                fig_s = go.Figure(go.Scatter(
                    y=s[:d]/(np.max(np.abs(s[:d]))+1e-12),
                    mode="lines", line=dict(color=col, width=1.4),
                    fill='tozeroy', fillcolor="rgba(124,156,255,0.04)"
                ))
                fig_s.update_layout(
                    title=dict(text=lbl, font=dict(family="Outfit", size=11, color=col)),
                    height=200, margin=dict(l=10, r=10, t=38, b=30),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0b0f1a",
                    font=dict(color="#64748b", size=9, family="Fira Code"),
                    xaxis=dict(gridcolor="#1a2030", showticklabels=False,
                               title=dict(text=hint, font=dict(size=8, color="#4a5568"))),
                    yaxis=dict(gridcolor="#1a2030", range=[-1.1, 1.1],
                               title=dict(text="Amplitude (norm.)", font=dict(size=8, color="#4a5568"))),
                    showlegend=False,
                )
                st.plotly_chart(fig_s, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — METRICS DASHBOARD
# ══════════════════════════════════════════════════════════════
with tab_metrics:
    st.markdown('<div class="section-header">Architecture Comparison & Performance Analysis</div>',
                unsafe_allow_html=True)

    bg = bit_growth(R, N, M)
    col_t, col_b = st.columns([3, 2])

    with col_t:
        st.markdown("**Architecture Trade-off Table**")
        st.markdown(f"""
| Metric | Basic | Pipelined | Folded | What it means |
|--------|:-----:|:---------:|:------:|---------------|
| Adder count | {2*N} | {2*N} | **1** | Hardware adders required |
| Register count | {N} | **{4*N}** | {N+1} | Flip-flops / memory elements |
| Critical path | {2*N} adders | **1 adder** | 1 adder | Limits max clock frequency |
| Pipeline latency | 0 | {2*N} cycles | ≥{2*N} cycles | Startup delay before first output |
| Throughput | 1/clk | **1/clk** | 1/{N}/clk | Outputs per clock cycle |
| Internal clock | 1× Fs | 1× Fs | **{N}× Fs** | Internal operating frequency |
| Bit growth | +{bg} | +{bg} | +{bg} | Extra bits needed (same for all) |
| **Best for** | Low power | **Max speed** | **Min area** | Design goal |
""")
        st.markdown(f"""
    <div class="explain-card ec-green">
      <div class="ec-title">Current selection: {architecture}</div>
      {desc[architecture].replace('**','<strong>').replace('**','</strong>')}
    </div>
    """, unsafe_allow_html=True)

    with col_b:
        categories = ['Throughput','Clock Speed','Area Efficiency','Power Efficiency','Scalability']
        fig_radar = go.Figure()
        for scores, name, color, fill in [
            ([3,2,3,4,3], "Basic",     C_BLUE,   "rgba(124,156,255,0.10)"),
            ([5,5,2,2,4], "Pipelined", C_GREEN,  "rgba(74,222,128,0.10)"),
            ([3,3,5,5,3], "Folded",    C_PURPLE, "rgba(192,132,252,0.10)"),
        ]:
            fig_radar.add_trace(go.Scatterpolar(
                r=scores+[scores[0]], theta=categories+[categories[0]],
                fill='toself', name=name,
                line=dict(color=color, width=2), fillcolor=fill,
            ))
        apply_dark(fig_radar, height=380)
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#0b0f1a",
                radialaxis=dict(range=[0,5], gridcolor="#1a2030",
                                tickfont=dict(size=8, color="#4a5568")),
                angularaxis=dict(gridcolor="#1a2030",
                                 tickfont=dict(size=10, color="#8899b3", family="Outfit")),
            ),
            title="Architecture Trade-off Radar",
            legend=dict(bgcolor="rgba(11,15,26,0.9)", bordercolor="#252d3d",
                        font=dict(family="Outfit", size=11)),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    col_bg, col_noise = st.columns(2)

    with col_bg:
        st.markdown("""
        <div class="explain-card">
          <div class="ec-title">Bit Growth vs Decimation Factor</div>
          As R increases, the internal values get larger, requiring more bits to represent without overflow.
          More stages (N) multiplies the growth. This tells you the minimum internal word length needed.
        </div>
        """, unsafe_allow_html=True)
        R_vals = [2, 4, 8, 16, 32, 64, 128, 256]
        fig_bg = go.Figure()
        colors_n = [C_BLUE, C_CYAN, C_GREEN, C_YELLOW, C_ORANGE, C_PURPLE]
        for n_v in range(1, 7):
            fig_bg.add_trace(go.Scatter(
                x=R_vals, y=[bit_growth(r, n_v, M) for r in R_vals],
                mode="lines+markers", name=f"N={n_v} stages",
                line=dict(color=colors_n[n_v-1], width=1.8),
                marker=dict(size=5)
            ))
        fig_bg.add_trace(go.Scatter(
            x=[R], y=[bit_growth(R, N, M)], mode="markers",
            marker=dict(size=14, color="#ffffff", symbol="star", line=dict(color=C_YELLOW, width=2)),
            name=f"Current: N={N}, R={R}"
        ))
        fig_bg.update_layout(
            xaxis_title="Decimation Factor R", yaxis_title="Additional Bits Required",
            xaxis_type="log", title=f"Bit Growth = N × ⌈log₂(R×M)⌉  —  Current: +{bit_growth(R,N,M)} bits",
            legend=dict(bgcolor="rgba(11,15,26,0.9)", bordercolor="#252d3d",
                        font=dict(family="Outfit", size=11)),
            xaxis=dict(tickvals=R_vals, ticktext=[str(r) for r in R_vals]),
        )
        apply_dark(fig_bg, height=340)
        st.plotly_chart(fig_bg, use_container_width=True)

    with col_noise:
        st.markdown("""
        <div class="explain-card">
          <div class="ec-title">Theoretical SNR Gain vs Decimation Factor</div>
          Decimation averages out noise — the more you decimate, the more SNR improves.
          The gain is 10·log₁₀(R) dB. However, this assumes white noise (not correlated noise).
        </div>
        """, unsafe_allow_html=True)
        R_test = [2,4,8,16,32,64]
        snr_gains = [10*np.log10(r) for r in R_test]
        highlight = [1 if r == R else 0 for r in R_test]
        fig_snr = go.Figure(go.Bar(
            x=[str(r) for r in R_test], y=snr_gains,
            marker=dict(
                color=["#3d6fff" if r == R else "#1e2a4a" for r in R_test],
                line=dict(color=["#7c9cff" if r == R else "#252d3d" for r in R_test], width=1.5)
            ),
            text=[f"{g:.1f} dB" for g in snr_gains],
            textposition="outside",
            textfont=dict(family="Outfit", size=11, color="#7c9cff"),
        ))
        fig_snr.update_layout(
            title=f"SNR Gain = 10·log₁₀(R)  —  Current R={R} → +{10*np.log10(R):.1f} dB",
            xaxis_title="Decimation Factor R  (highlighted = your current setting)",
            yaxis_title="SNR Improvement (dB)",
        )
        apply_dark(fig_snr, height=340)
        st.plotly_chart(fig_snr, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — RTL SIMULATION
# ══════════════════════════════════════════════════════════════
with tab_vlog:
    st.markdown('<div class="section-header">RTL Hardware Simulation via Icarus Verilog</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="explain-card ec-cyan">
      <div class="ec-title">What this does</div>
      This runs the actual <strong>Verilog RTL code</strong> through Icarus Verilog (iverilog) — the same simulation
      that would validate a chip design. The testbench applies a ramp input and checks that the hardware
      output matches expected values. The table below shows each valid output sample from the hardware simulation.
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "**Required files in the `verilog/` folder:**\n\n"
        "| Architecture | RTL Module | Testbench |\n"
        "|---|---|---|\n"
        "| Basic | `cic_filter.v` | `cic_testbench.v` |\n"
        "| Pipelined | `cic_filter_pipelined.v` | `cic_tb_pipelined.v` |\n"
        "| Folded | `cic_filter_folded.v` | `cic_tb_folded.v` |"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sim_arch = st.selectbox("Architecture to simulate", ["Pipelined", "Basic", "Folded"], index=0)
    with c2:
        sim_r = st.selectbox("Decimation factor R", [2, 4, 8, 16], index=1,
                             help="How much to decimate in the hardware simulation")
    with c3:
        sim_n = st.selectbox("Number of stages N", [1, 2, 3, 4], index=1,
                             help="Number of integrator-comb stage pairs")
    with c4:
        st.write("")
        st.write("")
        run_btn = st.button("▶  Run RTL Simulation", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("⚙️ Compiling Verilog and running simulation..."):
            output, err = run_iverilog(sim_r, sim_n, sim_arch)

        if err:
            st.error(f"**Simulation Error**\n\n{err}")
        else:
            st.success(f"✅ RTL Simulation Complete — {sim_arch} architecture, R={sim_r}, N={sim_n}")

            # Parse the output
            pattern = re.compile(r"VALID\s+#(\d+)\s+x_in=(-?\d+)\s+y_out=(-?\d+)")
            matches = pattern.findall(output)

            if matches:
                indices = [int(m[0]) for m in matches]
                x_vals  = [int(m[1]) for m in matches]
                y_vals  = [int(m[2]) for m in matches]

                col_chart, col_table = st.columns([3, 2])

                with col_chart:
                    st.markdown(f"""
                    <div class="explain-card ec-green">
                      <div class="ec-title">RTL Output Waveform</div>
                      This is the <strong>actual hardware output</strong> from the Verilog simulation.
                      For a ramp input, the CIC filter produces an integrated-then-differentiated version.
                      Total valid samples: <strong>{len(y_vals)}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    fig_v = go.Figure()
                    fig_v.add_trace(go.Scatter(
                        x=indices, y=y_vals, mode="lines+markers",
                        line=dict(color=C_GREEN, width=2),
                        marker=dict(size=5, color=C_GREEN),
                        fill='tozeroy', fillcolor="rgba(74,222,128,0.06)",
                        name="y_out (hardware)"
                    ))
                    fig_v.add_trace(go.Scatter(
                        x=indices, y=x_vals, mode="lines",
                        line=dict(color=C_BLUE, width=1.2, dash="dot"),
                        name="x_in (input)"
                    ))
                    fig_v.update_layout(
                        title=f"Hardware RTL Output  [{sim_arch}, R={sim_r}, N={sim_n}]  —  {len(y_vals)} valid samples",
                        xaxis_title="Valid Sample Number (each output requires R input clocks)",
                        yaxis_title="Output Value (integer — fixed-point hardware)",
                        legend=dict(bgcolor="rgba(11,15,26,0.9)", bordercolor="#252d3d",
                                    font=dict(family="Outfit", size=11)),
                    )
                    apply_dark(fig_v, height=340)
                    st.plotly_chart(fig_v, use_container_width=True)

                with col_table:
                    st.markdown("""
                    <div class="explain-card ec-green">
                      <div class="ec-title">Sample-by-Sample Hardware Output</div>
                      Each row is one valid output sample from the RTL simulation.
                      <strong>x_in</strong> = input value applied, <strong>y_out</strong> = hardware output.
                    </div>
                    """, unsafe_allow_html=True)

                    # Show table — limit to 40 rows, offer scroll
                    display_n = min(40, len(matches))
                    rows_html = ""
                    for i, (idx, xv, yv) in enumerate(zip(indices[:display_n], x_vals[:display_n], y_vals[:display_n])):
                        rows_html += f"<tr><td class='idx-col'>#{idx}</td><td>{xv}</td><td class='val-col'>{yv}</td></tr>"

                    st.markdown(f"""
                    <div class="vlog-table-wrap" style="max-height:320px;overflow-y:auto;">
                      <table class="vlog-table">
                        <thead>
                          <tr>
                            <th>Sample #</th>
                            <th>x_in (input)</th>
                            <th>y_out (output)</th>
                          </tr>
                        </thead>
                        <tbody>{rows_html}</tbody>
                      </table>
                    </div>
                    {'<div style="font-family:Outfit,sans-serif;font-size:11px;color:#64748b;padding:6px 0;">Showing first ' + str(display_n) + ' of ' + str(len(matches)) + ' samples</div>' if len(matches) > display_n else ''}
                    """, unsafe_allow_html=True)

                    # Summary stats
                    y_arr = np.array(y_vals)
                    st.markdown(f"""
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;">
                      <div class="explain-card" style="margin:0;padding:10px 14px;">
                        <div class="ec-title">Min output</div>
                        <div style="font-family:'Fira Code';font-size:16px;color:#f0f4ff;">{y_arr.min()}</div>
                      </div>
                      <div class="explain-card" style="margin:0;padding:10px 14px;">
                        <div class="ec-title">Max output</div>
                        <div style="font-family:'Fira Code';font-size:16px;color:#f0f4ff;">{y_arr.max()}</div>
                      </div>
                      <div class="explain-card" style="margin:0;padding:10px 14px;">
                        <div class="ec-title">Total samples</div>
                        <div style="font-family:'Fira Code';font-size:16px;color:#f0f4ff;">{len(y_vals)}</div>
                      </div>
                      <div class="explain-card" style="margin:0;padding:10px 14px;">
                        <div class="ec-title">Average output</div>
                        <div style="font-family:'Fira Code';font-size:16px;color:#f0f4ff;">{y_arr.mean():.1f}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.warning("⚠️ No `VALID #N x_in=... y_out=...` lines found in output. "
                           "Check that your testbench uses this format for output.")
                with st.expander("📋 Raw simulation output (click to expand)"):
                    st.code(output, language="text")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Architecture Comparison Reference</div>', unsafe_allow_html=True)
    bg = bit_growth(R, N, M)
    st.markdown(f"""
| Metric | Basic | Pipelined | Folded | Why it matters |
|--------|:-----:|:---------:|:------:|----------------|
| Adder count | {2*N} | {2*N} | **1** | Silicon area cost |
| Register count | {N} | **{4*N}** | {N+1} | Memory cost |
| Critical path | {2*N} adders | **1 adder** | 1 adder | Sets max Fclk |
| Pipeline latency | 0 cycles | {2*N} cycles | ≥{2*N} cycles | Startup delay |
| Throughput | 1/clk | **1/clk** | 1/{N}/clk | Output rate |
| Internal clock | 1× Fs | 1× Fs | **{N}× Fs** | Power cost |
| Bit growth | +{bg} bits | +{bg} bits | +{bg} bits | Word length needed |
| **Recommended when** | Balanced | **Speed critical** | **Area critical** | Design goal |
""")

# ══════════════════════════════════════════════════════════════
# TAB 7 — VERILOG CODE VIEWER
# ══════════════════════════════════════════════════════════════
with tab_vcode:
    fpath, tpath = find_verilog()

    def show_vlog_file(filename, title, description):
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="input-hint" style="font-size:13px;color:#8899b3;">{description}</div>',
                    unsafe_allow_html=True)
        found = None
        for d in [VLOG_DIR, os.path.dirname(os.path.abspath(__file__)),
                  "/mount/src/cic_decimation_filter/verilog", "/mount/src/cic_decimation_filter"]:
            p = os.path.join(d, filename)
            if os.path.exists(p): found = p; break
        if found:
            with open(found) as f: code = f.read()
            lines = len(code.splitlines())
            st.markdown(f'<div style="font-family:Fira Code,monospace;font-size:11px;color:#4a5568;'
                        f'margin-bottom:6px;">📄 {filename}  ·  {lines} lines</div>', unsafe_allow_html=True)
            st.code(code, language="verilog")
        else:
            st.warning(f"File not found: `verilog/{filename}`  — upload it to your repo's `verilog/` folder")

    show_vlog_file("cic_filter_pipelined.v", "cic_filter_pipelined.v — Pipelined RTL",
                   "Pipelined architecture with flip-flop registers after every stage for maximum clock speed")
    show_vlog_file("cic_filter_folded.v",    "cic_filter_folded.v — Folded RTL",
                   "Folded architecture using a single time-multiplexed adder to minimize chip area")
    show_vlog_file("cic_filter.v",           "cic_filter.v — Basic RTL",
                   "Standard CIC: N integrators → downsampler → N comb sections")
    show_vlog_file("cic_tb_pipelined.v",     "cic_tb_pipelined.v — Pipelined Testbench",
                   "Simulation testbench for the pipelined architecture")
    show_vlog_file("cic_tb_folded.v",        "cic_tb_folded.v — Folded Testbench",
                   "Simulation testbench for the folded architecture")
    show_vlog_file("cic_testbench.v",        "cic_testbench.v — Basic Testbench",
                   "Simulation testbench for the basic CIC architecture")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
<div style="font-family:'Fira Code',monospace;font-size:12px;color:#4a5568;
            background:#161b26;border:1px solid #252d3d;border-radius:10px;padding:18px;
            line-height:2;">
  📎 GitHub Repository:
  <a href="https://github.com/shashankchowdary-921/cic_decimation_filter"
     style="color:#7c9cff;text-decoration:none;">
    github.com/shashankchowdary-921/cic_decimation_filter
  </a><br>
  🌐 Live App:
  <a href="https://cic-decimation-filter.streamlit.app/"
     style="color:#22d3ee;text-decoration:none;">
    cic-decimation-filter.streamlit.app
  </a><br>
  📄 Reference: Hogenauer, E.B. — "An Economical Class of Digital Filters" — IEEE Trans. ASSP, vol.29 no.2, Apr 1981
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-family:'Outfit',sans-serif;font-size:11px;
            font-weight:500;color:#252d3d;letter-spacing:1px;padding:4px 0 2px;">
  CIC Decimation Filter Simulator · Team Mavericks
  &nbsp;·&nbsp; Shashank (23BVD1031) · Pasyanth (23BVD1004) · Abin (23BVD1047) · Yagnesh (23BVD1046)
</div>
""", unsafe_allow_html=True)
