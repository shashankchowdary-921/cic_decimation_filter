# ============================================================
# CIC DECIMATION FILTER — Interactive Simulator v3.0
# Team Mavericks | 5G/6G RF Front-End Project
# Dependencies: streamlit, numpy, plotly
# ============================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import subprocess, os, tempfile, re

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CIC Filter | Team Mavericks",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# GLOBAL STYLES — Clean Modern Dark Theme
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&family=Syne:wght@700;800&display=swap');

  /* ── Root & Body ── */
  html, body, [data-testid="stApp"] {
    background: #070d1a;
    color: #cbd5e1;
    font-family: 'Space Grotesk', sans-serif;
  }
  .block-container { padding-top: 0.5rem; padding-bottom: 1rem; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1323 0%, #0e1729 100%);
    border-right: 1px solid #1e3a5f;
  }
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Syne', sans-serif;
    color: #60a5fa;
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #0b1323;
    border-bottom: 1px solid #1e3a5f;
    gap: 1px;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    color: #475569;
    border-radius: 6px 6px 0 0;
    padding: 9px 18px;
    border: 1px solid transparent;
    transition: all 0.25s ease;
    text-transform: uppercase;
  }
  .stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, #1e3a5f 0%, #0e1729 100%) !important;
    color: #60a5fa !important;
    border-color: #2d5a9e !important;
    border-bottom-color: transparent !important;
    box-shadow: 0 -2px 12px rgba(96,165,250,0.15);
  }
  .stTabs [data-baseweb="tab-panel"] {
    background: #070d1a;
    padding-top: 1.2rem;
  }

  /* ── Metric Cards ── */
  div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0e1729 0%, #0b1323 100%);
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(96,165,250,0.05);
    font-family: 'JetBrains Mono', monospace;
    transition: box-shadow 0.2s;
  }
  div[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 24px rgba(96,165,250,0.12);
  }
  div[data-testid="metric-container"] label {
    color: #60a5fa !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
  }
  div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: #e2e8f0 !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #2d5a9e);
    border: 1px solid #3b82f6;
    color: #93c5fd;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-radius: 8px;
    padding: 9px 22px;
    box-shadow: 0 2px 12px rgba(59,130,246,0.2);
    transition: all 0.25s ease;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #2d5a9e, #3b82f6);
    box-shadow: 0 4px 20px rgba(59,130,246,0.35);
    color: #ffffff;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0891b2, #0e7490);
    border-color: #22d3ee;
    color: white;
    box-shadow: 0 2px 16px rgba(34,211,238,0.3);
  }
  .stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 24px rgba(34,211,238,0.45);
  }

  /* ── Info boxes ── */
  .stInfo, .stAlert {
    background: linear-gradient(135deg, #0b1323, #0e1729);
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    font-family: 'Space Grotesk', sans-serif;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    background: #0e1729 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #60a5fa !important;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }
  .streamlit-expanderContent {
    background: #0b1323 !important;
    border: 1px solid #1e3a5f !important;
    border-top: none !important;
  }

  hr { border-color: #1e3a5f !important; }

  /* ── Hero Banner ── */
  .hero-banner {
    background: linear-gradient(135deg, #070d1a 0%, #0b1323 40%, #0e1729 70%, #070d1a 100%);
    border: 1px solid #1e3a5f;
    border-top: 2px solid #3b82f6;
    border-radius: 14px;
    padding: 22px 32px 18px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 60px rgba(59,130,246,0.05);
  }
  .hero-banner::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 40%;
    height: 100%;
    background: radial-gradient(ellipse at top right, rgba(96,165,250,0.06) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #f8fafc;
    margin: 0;
    line-height: 1.2;
  }
  .hero-title span { color: #60a5fa; }
  .hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #475569;
    letter-spacing: 2px;
    margin-top: 5px;
    text-transform: uppercase;
  }
  .hero-tag {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #22d3ee;
    text-transform: uppercase;
    border: 1px solid rgba(34,211,238,0.4);
    border-radius: 4px;
    padding: 3px 10px;
    display: inline-block;
    background: rgba(34,211,238,0.05);
    margin-bottom: 8px;
  }

  /* ── Author Cards ── */
  .author-grid {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 12px;
  }
  .author-card {
    background: rgba(30,58,95,0.3);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 8px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #7dd3fc;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.2s ease;
  }
  .author-card:hover {
    border-color: #3b82f6;
    background: rgba(30,58,95,0.5);
    color: #bae6fd;
  }
  .author-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 9px;
    font-weight: 600;
    color: #60a5fa;
    letter-spacing: 0.5px;
    margin-top: 2px;
  }

  /* ── Section Headers ── */
  .section-header {
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #60a5fa;
    text-transform: uppercase;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 8px;
    margin-bottom: 16px;
    margin-top: 8px;
  }

  /* ── Workflow Cards ── */
  .workflow-card {
    background: linear-gradient(135deg, #0e1729, #0b1323);
    border: 1px solid #1e3a5f;
    border-left: 3px solid #3b82f6;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 10px;
  }
  .workflow-card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: #3b82f6;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .workflow-card-body {
    font-size: 13px;
    color: #7c9cbf;
    line-height: 1.6;
    font-family: 'Space Grotesk', sans-serif;
  }
  .wc-green  { border-left-color: #22c55e; }
  .wc-yellow { border-left-color: #eab308; }
  .wc-purple { border-left-color: #a855f7; }
  .wc-cyan   { border-left-color: #06b6d4; }
  .wc-orange { border-left-color: #f97316; }
  .wc-green  .workflow-card-title { color: #22c55e; }
  .wc-yellow .workflow-card-title { color: #eab308; }
  .wc-purple .workflow-card-title { color: #a855f7; }
  .wc-cyan   .workflow-card-title { color: #06b6d4; }
  .wc-orange .workflow-card-title { color: #f97316; }

  /* ── Code blocks ── */
  .stCode, code {
    font-family: 'JetBrains Mono', monospace !important;
    background: #0b1323 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 6px !important;
  }

  /* ── Table ── */
  table { width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
  th {
    background: #0e1729;
    color: #60a5fa;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    padding: 9px 13px;
    border: 1px solid #1e3a5f;
    text-transform: uppercase;
  }
  td { background: #0b1323; color: #7c9cbf; padding: 8px 13px; border: 1px solid #1e3a5f; }
  tr:hover td { background: #0e1729; color: #cbd5e1; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: #070d1a; }
  ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #3b82f6; }

  /* ── Radio / Checkboxes ── */
  .stRadio label, .stCheckbox label {
    font-family: 'Space Grotesk', sans-serif;
    color: #7c9cbf;
  }

  /* ── Select / Slider labels ── */
  .stSelectbox label, .stSlider label, .stSelectSlider label {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    color: #94a3b8 !important;
  }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:800;
                color:#60a5fa;letter-spacing:2px;text-align:center;
                padding:12px 0 6px;">
      📡 CIC FILTER
    </div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:9px;
                color:#475569;letter-spacing:3px;text-align:center;
                text-transform:uppercase;margin-bottom:10px;">
      Control Panel
    </div>
    <hr style="border-color:#1e3a5f;margin:0 0 14px;">
    """, unsafe_allow_html=True)

    architecture = st.selectbox(
        "🏗️ Architecture",
        ["Pipelined", "Basic", "Folded"],
        help=(
            "Pipelined: pipeline register after every stage (matches RTL).\n"
            "Basic: standard cascaded integrator-comb.\n"
            "Folded: single shared adder, time-multiplexed."
        ),
    )
    st.markdown("---")

    FS_MAP = {
        "500 kHz":   500_000,
        "1 MHz":   1_000_000,
        "2 MHz":   2_000_000,
        "4 MHz":   4_000_000,
        "8 MHz":   8_000_000,
        "16 MHz": 16_000_000,
        "20 MHz": 20_000_000,
        "32 MHz": 32_000_000,
        "40 MHz": 40_000_000,
        "48 MHz": 48_000_000,
        "64 MHz": 64_000_000,
        "80 MHz": 80_000_000,
        "96 MHz": 96_000_000,
        "100 MHz":100_000_000,
        "128 MHz":128_000_000,
        "200 MHz":200_000_000,
        "256 MHz":256_000_000,
        "500 MHz":500_000_000,
    }
    fs_label = st.selectbox("⚡ Input Sample Rate", list(FS_MAP.keys()), index=4)
    fs_in    = FS_MAP[fs_label]

    R = st.select_slider("📉 Decimation Factor (R)",
                         options=[2, 4, 8, 16, 32, 64, 128, 256], value=4)
    N = st.slider("🔢 Number of Stages (N)", 1, 6, 2)
    M = st.select_slider("⏱️ Differential Delay (M)", options=[1, 2], value=1)

    fs_out = fs_in / R
    if fs_out >= 1e6:
        fs_out_str = f"{fs_out/1e6:.3f} MHz"
    elif fs_out >= 1e3:
        fs_out_str = f"{fs_out/1e3:.2f} kHz"
    else:
        fs_out_str = f"{fs_out:.1f} Hz"

    st.markdown("---")
    st.markdown("""<div style="font-family:'Space Grotesk',sans-serif;font-size:9px;font-weight:600;
                    color:#475569;letter-spacing:2px;text-transform:uppercase;">Output Rate</div>""",
                unsafe_allow_html=True)
    st.metric("", fs_out_str)
    st.markdown("---")

    st.markdown("""<div style="font-family:'Space Grotesk',sans-serif;font-size:9px;font-weight:600;
                    color:#475569;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Test Signal</div>""",
                unsafe_allow_html=True)
    sig_type  = st.selectbox("Signal Type",
        ["Sine","Ramp","DC","Multi-tone","Chirp","Square","Random Noise"])
    max_f     = max(10, int(fs_out / 3))
    f_sig     = st.slider("Signal Frequency (Hz)", 10, max_f, min(1000, max_f // 4))
    noise_db  = st.slider("Noise Level (dB)", -80, 0, -40)
    n_samples = st.select_slider("Input Samples",
                                 options=[128, 256, 512, 1024, 2048, 4096], value=512)

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Space Grotesk',sans-serif;font-size:8px;color:#1e3a5f;
                letter-spacing:2px;text-align:center;padding-top:4px;text-transform:uppercase;">
      Team Mavericks · 2024<br>5G/6G RF Front-End
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
    if kind == "Sine":
        return np.sin(2*np.pi*f0*t) + nz
    elif kind == "Ramp":
        return (np.arange(n) % 20) * 0.05 + nz
    elif kind == "DC":
        return np.ones(n) * 0.5 + nz
    elif kind == "Multi-tone":
        s = (np.sin(2*np.pi*f0*t)
             + 0.5*np.sin(2*np.pi*f0*3*t)
             + 0.3*np.sin(2*np.pi*f0*7*t))
        return s / np.max(np.abs(s)+1e-12) + nz
    elif kind == "Chirp":
        f_end = min(f0*10, fs/2.5)
        return np.sin(2*np.pi*(f0+(f_end-f0)*t/(n/fs))*t) + nz
    elif kind == "Square":
        return np.sign(np.sin(2*np.pi*f0*t)) + nz
    else:
        return np.random.randn(n)

x_in_raw = make_signal(sig_type, n_samples, fs_in, f_sig, noise_db)

# ──────────────────────────────────────────────────────────────
# CIC MODELS — FIXED COMB FILTER
# NOTE: Comb computes y[n] - y[n-M]  (delay-M first-order diff)
#       NOT np.diff(y, M) which gives M-th ORDER difference —
#       that would be wrong for M>1.
# ──────────────────────────────────────────────────────────────

def apply_comb(y, M):
    """
    Correct CIC comb: y_out[n] = y[n] - y[n-M]
    For M=1: standard first difference (same as np.diff)
    For M=2: y[n] - y[n-2]  (NOT second-order diff)
    Past samples beyond the buffer are assumed 0.
    """
    y = np.asarray(y, dtype=float)
    out = np.empty_like(y)
    out[:M]  = y[:M]                  # no history yet → subtract 0
    out[M:]  = y[M:] - y[:-M]
    return out

def cic_basic(x, R, N, M=1):
    y = x.astype(float)
    # N integrators at Fs_in
    for _ in range(N):
        y = np.cumsum(y)
    # Downsample by R
    y = y[::R].copy()
    # N comb sections at Fs_out
    for _ in range(N):
        y = apply_comb(y, M)
    return y

def cic_pipelined(x, R, N, M=1):
    """
    Matches RTL cic_filter_pipelined.v:
    - D flip-flop (register) inserted after every integrator stage
    - D flip-flop inserted after every comb stage
    - Pipeline depth = 2N register stages
    """
    y = x.astype(float)
    # N integrators + pipeline registers at Fs_in
    for _ in range(N):
        y = np.cumsum(y)
        reg = np.roll(y, 1)
        reg[0] = 0.0
        y = reg
    # Downsample by R
    y = y[::R].copy()
    # N comb + pipeline registers at Fs_out
    for _ in range(N):
        y = apply_comb(y, M)
        reg = np.roll(y, 1)
        reg[0] = 0.0
        y = reg
    return y

def cic_folded(x, R, N, M=1):
    """
    Folded: functionally identical to Basic (same I/O),
    just uses 1 shared adder time-multiplexed — captured here
    by reusing cic_basic.
    """
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
    sfdr_db = 20*np.log10(Y[peak_idx] / (np.max(Y[mask]) + 1e-30))
    return sfdr_db

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
    candidates = [
        VLOG_DIR,
        os.path.dirname(os.path.abspath(__file__)),
        "/mount/src/cic_decimation_filter/verilog",
        "/mount/src/cic_decimation_filter",
    ]
    for d in candidates:
        f = os.path.join(d, "cic_filter.v")
        t = os.path.join(d, "cic_testbench.v")
        if os.path.exists(f) and os.path.exists(t):
            return f, t
    return None, None

def run_iverilog(r_val=4, n_val=2, arch="Pipelined"):
    arch_file_map = {
        "Pipelined": "cic_filter_pipelined.v",
        "Folded":    "cic_filter_folded.v",
        "Basic":     "cic_filter.v",
    }
    tb_file_map = {
        "Pipelined": "cic_tb_pipelined.v",
        "Folded":    "cic_tb_folded.v",
        "Basic":     "cic_testbench.v",
    }
    candidates = [
        VLOG_DIR,
        os.path.dirname(os.path.abspath(__file__)),
        "/mount/src/cic_decimation_filter/verilog",
        "/mount/src/cic_decimation_filter",
    ]
    fpath, tpath = None, None
    for d in candidates:
        fp = os.path.join(d, arch_file_map.get(arch, "cic_filter.v"))
        tp = os.path.join(d, tb_file_map.get(arch, "cic_testbench.v"))
        if os.path.exists(fp) and os.path.exists(tp):
            fpath, tpath = fp, tp
            break
        fp2 = os.path.join(d, "cic_filter.v")
        tp2 = os.path.join(d, "cic_testbench.v")
        if os.path.exists(fp2) and os.path.exists(tp2):
            fpath, tpath = fp2, tp2
            break

    if fpath is None:
        return None, (
            f"Verilog files not found for arch='{arch}'.\n"
            f"Expected: `verilog/{arch_file_map[arch]}` + `verilog/{tb_file_map[arch]}`"
        )

    with tempfile.TemporaryDirectory() as tmp:
        out_bin = os.path.join(tmp, "cic_sim")
        with open(tpath) as f:
            tb = f.read()
        tb = re.sub(r"\.R\(\d+\)", f".R({r_val})", tb)
        tb = re.sub(r"\.N\(\d+\)", f".N({n_val})", tb)
        tb_mod = os.path.join(tmp, "tb.v")
        with open(tb_mod, "w") as f:
            f.write(tb)
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
    plot_bgcolor="#0b1120",
    font=dict(color="#7c9cbf", family="JetBrains Mono"),
    margin=dict(t=50, b=30, l=55, r=20),
)
GRID = dict(gridcolor="#132038", zerolinecolor="#1e3a5f", gridwidth=1)

def apply_dark(fig, height=420):
    fig.update_layout(height=height, **DARK)
    for ax in fig.layout:
        if ax.startswith("xaxis") or ax.startswith("yaxis"):
            fig.layout[ax].update(**GRID)
    fig.update_layout(
        title_font=dict(family="Space Grotesk", size=12, color="#60a5fa"),
    )
    return fig

# Colour palette
C_BLUE   = "#60a5fa"
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
  <div class="hero-tag">5G / 6G RF Front-End · DSP Project</div>
  <div class="hero-title">📡 CIC <span>Decimation</span> Filter</div>
  <div class="hero-sub">Interactive RTL Simulator · Team Mavericks</div>
  <div class="author-grid" style="margin-top:14px;">
    <div class="author-card">
      <span style="color:#60a5fa;font-size:18px;font-family:Syne,sans-serif;font-weight:800;">①</span>
      <div>
        <div style="color:#e2e8f0;font-size:12px;font-weight:600;font-family:Space Grotesk,sans-serif;">Shashank T</div>
        <div class="author-num">REG · 23BVD1031</div>
      </div>
    </div>
    <div class="author-card">
      <span style="color:#22d3ee;font-size:18px;font-family:Syne,sans-serif;font-weight:800;">②</span>
      <div>
        <div style="color:#e2e8f0;font-size:12px;font-weight:600;font-family:Space Grotesk,sans-serif;">Pasyanth P</div>
        <div class="author-num">REG · 23BVD1004</div>
      </div>
    </div>
    <div class="author-card">
      <span style="color:#c084fc;font-size:18px;font-family:Syne,sans-serif;font-weight:800;">③</span>
      <div>
        <div style="color:#e2e8f0;font-size:12px;font-weight:600;font-family:Space Grotesk,sans-serif;">Abin Mohammad</div>
        <div class="author-num">REG · 23BVD1047</div>
      </div>
    </div>
    <div class="author-card">
      <span style="color:#4ade80;font-size:18px;font-family:Syne,sans-serif;font-weight:800;">④</span>
      <div>
        <div style="color:#e2e8f0;font-size:12px;font-weight:600;font-family:Space Grotesk,sans-serif;">Yagnesh</div>
        <div class="author-num">Team Mavericks</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ──
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
c1.metric("Architecture",  architecture)
c2.metric("Input Rate",    fs_label)
c3.metric("Output Rate",   fs_out_str)
c4.metric("Decimation R",  f"÷{R}")
c5.metric("Stages N",      str(N))
c6.metric("Bit Growth",    f"+{bg_bit} bits")
c7.metric("SNR Δ",         f"{snr_out-snr_in:+.1f} dB")

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TABS  (Project Flow removed)
# ──────────────────────────────────────────────────────────────
tab_sim, tab_freq, tab_arch, tab_stages, tab_metrics, tab_vlog, tab_vcode = st.tabs([
    "🌊 SIMULATE",
    "📈 FREQ RESPONSE",
    "🏗️ ARCHITECTURE",
    "📊 STAGE ANALYSIS",
    "📐 METRICS",
    "⚡ RTL SIMULATION",
    "📄 VERILOG CODE",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SIMULATE
# ══════════════════════════════════════════════════════════════
with tab_sim:
    st.markdown('<div class="section-header">Time-Domain Waveforms & Spectral Analysis</div>',
                unsafe_allow_html=True)

    disp_in  = min(n_samples, 300)
    disp_out = min(len(y_out), 300)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"Input x[n]  ·  {fs_label}",
            f"Output y[m]  ·  {fs_out_str}",
            "Input Spectrum",
            "Output Spectrum",
        ],
        vertical_spacing=0.18, horizontal_spacing=0.08,
    )
    fig.add_trace(go.Scatter(
        x=t_in[:disp_in], y=x_norm[:disp_in],
        mode="lines", line=dict(color=C_BLUE, width=1.4),
        fill='tozeroy', fillcolor="rgba(96,165,250,0.07)", name="x[n]"
    ), row=1, col=1)

    y_fnorm = y_out / (np.max(np.abs(y_out))+1e-12)
    fig.add_trace(go.Scatter(
        x=t_out[:disp_out], y=y_fnorm[:disp_out],
        mode="lines", line=dict(color=C_ORANGE, width=1.6),
        fill='tozeroy', fillcolor="rgba(251,146,60,0.07)", name="y[m]"
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
        mode="lines", line=dict(color=C_ORANGE, width=1.0), name="Output PSD"
    ), row=2, col=2)

    fig.update_xaxes(title_text="Time (µs)", title_font=dict(size=10), row=1, col=1)
    fig.update_xaxes(title_text="Time (µs)", title_font=dict(size=10), row=1, col=2)
    fig.update_xaxes(title_text="Freq (kHz)", title_font=dict(size=10),
                     range=[0, min(fs_in/2e3,200)], row=2, col=1)
    fig.update_xaxes(title_text="Freq (kHz)", title_font=dict(size=10),
                     range=[0, fs_out/2e3], row=2, col=2)
    fig.update_yaxes(title_text="Amplitude", title_font=dict(size=10), row=1, col=1)
    fig.update_yaxes(title_text="Amplitude", title_font=dict(size=10), row=1, col=2)
    fig.update_yaxes(title_text="dBFS", title_font=dict(size=10), range=[-100, 5], row=2, col=1)
    fig.update_yaxes(title_text="dBFS", title_font=dict(size=10), range=[-100, 5], row=2, col=2)

    for ann in fig.layout.annotations:
        ann.font = dict(family="Space Grotesk", size=10, color="#60a5fa")

    apply_dark(fig, height=560)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    sfdr_out = sfdr_calc(y_norm, fs_out)
    thd_out  = thd_calc(y_norm, f_sig, fs_out) if sig_type in ["Sine","Square","Multi-tone"] else float('nan')
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Input SNR",  f"{snr_in:.1f} dB")
    s2.metric("Output SNR", f"{snr_out:.1f} dB")
    s3.metric("SNR Change", f"{snr_out-snr_in:+.1f} dB")
    s4.metric("SFDR (out)", f"{sfdr_out:.1f} dB")
    if not np.isnan(thd_out):
        s5.metric("THD (out)", f"{thd_out:.1f} dB")
    else:
        s5.metric("THD (out)", "N/A")

# ══════════════════════════════════════════════════════════════
# TAB 2 — FREQUENCY RESPONSE
# ══════════════════════════════════════════════════════════════
with tab_freq:
    st.markdown('<div class="section-header">CIC Magnitude Response</div>', unsafe_allow_html=True)

    col_main, col_ctrl = st.columns([4, 1])
    with col_ctrl:
        show_alias = st.checkbox("Alias bands",   value=True)
        show_pb    = st.checkbox("Passband edge", value=True)
        show_comp  = st.checkbox("Compensated",   value=False,
                                 help="Overlay a simple 1-tap compensation curve")
        f_lim      = st.slider("Display (MHz)", 0.1, max(0.2, fs_in/2e6),
                               min(fs_in/2e6, 8.0), step=0.1)
        y_min_db   = st.slider("Y min (dB)", -160, -20, -120)

    with col_main:
        mask = f_ax <= f_lim*1e6
        fig_fr = go.Figure()
        fig_fr.add_trace(go.Scatter(
            x=f_ax[mask]/1e6, y=H_db[mask],
            mode="lines", line=dict(color=C_BLUE, width=2),
            name="|H(f)|",
            fill='tozeroy', fillcolor="rgba(96,165,250,0.05)"
        ))

        if show_comp:
            f_comp = f_ax[mask]
            h_comp_inv = -H_db[mask] * 0.5
            fig_fr.add_trace(go.Scatter(
                x=f_comp/1e6, y=h_comp_inv,
                mode="lines", line=dict(color=C_GREEN, width=1.5, dash="dot"),
                name="Compensation gain"
            ))
            fig_fr.add_trace(go.Scatter(
                x=f_comp/1e6, y=H_db[mask] + h_comp_inv,
                mode="lines", line=dict(color=C_YELLOW, width=1.5),
                name="Compensated |H(f)|"
            ))

        if show_alias:
            for k in range(1, 6):
                fa = k * fs_out
                if fa < f_lim*1e6:
                    fig_fr.add_vline(x=fa/1e6,
                        line=dict(color="#ef4444", dash="dot", width=1),
                        annotation_text=f"Alias {k}",
                        annotation_font=dict(size=9, color="#ef4444"))
        if show_pb:
            fig_fr.add_vline(x=0.4*fs_out/1e6,
                line=dict(color=C_GREEN, dash="dash", width=1.5),
                annotation_text="PB edge",
                annotation_font=dict(size=9, color=C_GREEN))

        fig_fr.add_hline(y=-3, line=dict(color=C_ORANGE, dash="dash", width=1),
                         annotation_text="-3dB", annotation_font=dict(size=9, color=C_ORANGE))
        fig_fr.add_hline(y=-6, line=dict(color=C_PURPLE, dash="dash", width=1))

        fig_fr.update_layout(
            title=f"CIC Response  [N={N}, R={R}, M={M}, Fs={fs_in/1e6:.1f} MHz]",
            xaxis_title="Frequency (MHz)", yaxis_title="Magnitude (dB)",
            xaxis_range=[0, f_lim], yaxis_range=[y_min_db, 5],
            legend=dict(bgcolor="rgba(7,13,26,0.9)", bordercolor="#1e3a5f",
                        font=dict(family="JetBrains Mono", size=10)),
        )
        apply_dark(fig_fr)
        st.plotly_chart(fig_fr, use_container_width=True)

    st.markdown('<div class="section-header">Passband Detail</div>', unsafe_allow_html=True)
    pb_mask = f_ax <= 0.5*fs_out
    fig_pb  = go.Figure(go.Scatter(
        x=f_ax[pb_mask]/1e3, y=H_db[pb_mask],
        mode="lines", line=dict(color=C_CYAN, width=2),
        fill='tozeroy', fillcolor="rgba(34,211,238,0.06)"
    ))
    fig_pb.add_hline(y=-3, line=dict(color=C_ORANGE, dash="dash"))
    fig_pb.update_layout(
        xaxis_title="Frequency (kHz)", yaxis_title="dB",
        title="Passband Droop (0 → Fs_out/2)"
    )
    apply_dark(fig_pb, height=280)
    st.plotly_chart(fig_pb, use_container_width=True)

    with st.expander("📋 ATTENUATION TABLE"):
        checks = [
            ("Passband edge (0.4·Fout)", 0.4*fs_out),
            ("Nyquist       (0.5·Fout)", 0.5*fs_out),
            ("1st alias     (1.0·Fout)", 1.0*fs_out),
            ("2nd alias     (2.0·Fout)", 2.0*fs_out),
            ("3rd alias     (3.0·Fout)", 3.0*fs_out),
        ]
        st.markdown("| Point | Frequency | Attenuation |\n|---|---|---|")
        for name, fc in checks:
            if fc < fs_in/2:
                idx = np.argmin(np.abs(f_ax - fc))
                st.markdown(f"| {name} | {fc/1e3:.2f} kHz | {H_db[idx]:.1f} dB |")

# ══════════════════════════════════════════════════════════════
# TAB 3 — ARCHITECTURE
# ══════════════════════════════════════════════════════════════
with tab_arch:
    st.markdown(f'<div class="section-header">Block Diagram — {architecture} (N={N}, R={R}, M={M})</div>',
                unsafe_allow_html=True)

    fig_bd = go.Figure()
    fig_bd.update_layout(
        xaxis=dict(range=[-0.5,14], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1.5, 3], showgrid=False, zeroline=False, visible=False),
        height=280, margin=dict(l=5,r=5,t=50,b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
    )

    def add_box(fig, cx, cy, label, ec, fc_a=0.18):
        rgb = re.findall(r'\d+', ec)
        r2,g2,b2 = (int(x) for x in rgb[:3])
        fig.add_shape(type="rect",
            x0=cx-0.48, x1=cx+0.48, y0=cy-0.32, y1=cy+0.32,
            line=dict(color=ec, width=2),
            fillcolor=f"rgba({r2},{g2},{b2},{fc_a})")
        fig.add_annotation(x=cx, y=cy, text=label, showarrow=False,
            font=dict(size=10, color="#ffffff", family="JetBrains Mono"), align="center")

    def arr(fig, x0, x1, y=1.0):
        fig.add_annotation(x=x1, y=y, ax=x0, ay=y,
            axref="x", ayref="y", xref="x", yref="y",
            arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#2d5a9e")

    C_INT  = "rgb(96,165,250)"
    C_DS   = "rgb(251,146,60)"
    C_COMB = "rgb(74,222,128)"
    C_FF   = "rgb(192,132,252)"
    C_IN   = "rgb(34,211,238)"

    if architecture in ("Basic", "Folded"):
        pos  = [0.5] + [1.5+i*1.35 for i in range(N)] + [1.5+N*1.35+0.7]
        pos += [pos[-1]+1.2+i*1.35 for i in range(N)]
        lbls = ["x[n]"]+[f"Σ{i+1}" for i in range(N)]+[f"↓{R}"]+[f"D{i+1}" for i in range(N)]
        cols = [C_IN]+[C_INT]*N+[C_DS]+[C_COMB]*N
        for px, lb, cl in zip(pos, lbls, cols):
            add_box(fig_bd, px, 1.0, lb, cl)
        for i in range(len(pos)-1):
            arr(fig_bd, pos[i]+0.48, pos[i+1]-0.48)
        ds_x = pos[N+1]
        fig_bd.add_shape(type="line", x0=ds_x, x1=ds_x, y0=0.55, y1=1.45,
                         line=dict(color="#1e3a5f", dash="dash"))
        fig_bd.add_annotation(x=ds_x-1.5, y=0.2, text="← Fs_in →",
                               showarrow=False, font=dict(size=9,color="#475569"))
        fig_bd.add_annotation(x=ds_x+1.5, y=0.2, text="← Fs_out →",
                               showarrow=False, font=dict(size=9,color="#475569"))
        if architecture == "Folded":
            fig_bd.add_annotation(x=pos[N//2+1], y=2.4,
                text=f"⚡ 1 Shared Adder  ×{N} time-mux  |  Internal clk = {N}× Fs_in",
                showarrow=False, font=dict(size=11, color="#fb923c"),
                bgcolor="rgba(251,146,60,0.1)", bordercolor="#fb923c", borderwidth=1)
    else:  # Pipelined
        pos  = [0.5]; lbls = ["x[n]"]; cols = [C_IN]
        for i in range(N):
            bx = 1.5 + i*2.3
            pos  += [bx, bx+0.9]; lbls += [f"Σ{i+1}", "FF"]; cols += [C_INT, C_FF]
        ds_x = pos[-1] + 0.95
        pos  += [ds_x]; lbls += [f"↓{R}"]; cols += [C_DS]
        for i in range(N):
            bx = ds_x + 1.2 + i*2.3
            pos  += [bx, bx+0.9]; lbls += [f"D{i+1}", "FF"]; cols += [C_COMB, C_FF]
        for px, lb, cl in zip(pos, lbls, cols):
            add_box(fig_bd, px, 1.0, lb, cl)
        for i in range(len(pos)-1):
            arr(fig_bd, pos[i]+0.48, pos[i+1]-0.48)
        mid = pos[len(pos)//2]
        fig_bd.add_annotation(x=mid, y=2.45,
            text=f"Pipeline depth = {2*N} FFs  |  Latency = {2*N} clocks  |  Throughput = 1 samp/clk",
            showarrow=False, font=dict(size=11, color="#c084fc"),
            bgcolor="rgba(192,132,252,0.1)", bordercolor="#a855f7", borderwidth=1)

    apply_dark(fig_bd, height=280)
    st.plotly_chart(fig_bd, use_container_width=True)

    desc = {
        "Basic": (
            "**Basic CIC:** N integrators run at Fs_in. "
            "After ↓R downsampling, N comb (differencer) sections run at Fs_out. "
            "Each comb stage computes `y[n] - y[n-M]` — a delay-M first-order difference. "
            "No pipeline registers — minimal hardware, but critical path spans all N adders."
        ),
        "Pipelined": (
            f"**Pipelined CIC (matches RTL `cic_filter_pipelined.v`):** "
            f"A D flip-flop (FF) after every integrator and every comb stage creates a "
            f"**{2*N}-stage deep pipeline**. Critical path = 1 adder → maximum clock speed. "
            f"Latency = {2*N} clock cycles. Throughput = 1 output per R input clocks."
        ),
        "Folded": (
            f"**Folded CIC (matches RTL `cic_filter_folded.v`):** "
            f"A single adder is reused {N}× per input sample via time-multiplexing. "
            f"Internal clock runs at {N}× Fs_in. Area reduced by ~{2*N-1} adders vs Basic. "
            "Throughput same as Basic."
        ),
    }
    st.info(desc[architecture])

    with st.expander("📐 TRANSFER FUNCTION & KEY EQUATIONS"):
        st.latex(r"H(z) = \left(\frac{1 - z^{-RM}}{1 - z^{-1}}\right)^N")
        st.latex(r"|H(f)| = \left|\frac{\sin(\pi M R f/F_s)}{\sin(\pi f/F_s)}\right|^N")
        st.latex(r"\text{Comb: } y[n] = x[n] - x[n-M] \quad \text{(delay-M first-order difference)}")
        st.markdown(f"""
| Parameter | Value |
|-----------|-------|
| N (stages) | {N} |
| R (decimation) | {R} |
| M (differential delay) | {M} |
| Fs_in | {fs_in/1e6:.3f} MHz |
| Fs_out | {fs_out_str} |
| DC gain (linear) | {int((M*R)**N)} |
| Bit growth | +{bit_growth(R,N,M)} bits |
| Pipeline depth | {2*N if architecture=="Pipelined" else 0} registers |
| Adder count | {"1 (shared)" if architecture=="Folded" else str(2*N)} |
""")

# ══════════════════════════════════════════════════════════════
# TAB 4 — STAGE ANALYSIS
# ══════════════════════════════════════════════════════════════
with tab_stages:
    st.markdown('<div class="section-header">Per-Stage Output Waveforms (normalised)</div>',
                unsafe_allow_html=True)

    y_stages, stage_labels = [], []
    yc = x_in_raw.astype(float)
    y_stages.append(yc.copy()); stage_labels.append("Input x[n]")

    for i in range(N):
        yc = np.cumsum(yc)
        if architecture == "Pipelined":
            reg = np.roll(yc,1); reg[0]=0.0; yc=reg
        y_stages.append(yc.copy())
        stage_labels.append(f"Integrator {i+1}" + (" + FF" if architecture=="Pipelined" else ""))

    yc_ds = yc[::R]
    y_stages.append(yc_ds.copy()); stage_labels.append(f"After ↓{R}")

    yc2 = yc_ds.copy()
    for i in range(N):
        yc2 = apply_comb(yc2, M)           # ← FIXED: correct comb
        if architecture == "Pipelined":
            reg = np.roll(yc2,1); reg[0]=0.0; yc2=reg
        y_stages.append(yc2.copy())
        stage_labels.append(f"Comb {i+1}" + (" + FF" if architecture=="Pipelined" else ""))

    STAGE_COLORS = [C_CYAN, C_BLUE, "#3b82f6", "#1d4ed8",
                    C_ORANGE, "#ef4444", C_GREEN, "#16a34a",
                    C_PURPLE, "#7c3aed", C_PINK, C_YELLOW]

    cols_per_row = 3
    for row_start in range(0, len(y_stages), cols_per_row):
        cols = st.columns(cols_per_row)
        for ci, si in enumerate(range(row_start, min(row_start+cols_per_row, len(y_stages)))):
            s   = y_stages[si]
            lbl = stage_labels[si]
            col = STAGE_COLORS[si % len(STAGE_COLORS)]
            d   = min(200, len(s))
            with cols[ci]:
                fig_s = go.Figure(go.Scatter(
                    y=s[:d]/(np.max(np.abs(s[:d]))+1e-12),
                    mode="lines",
                    line=dict(color=col, width=1.3),
                    fill='tozeroy',
                    fillcolor="rgba(96,165,250,0.05)"
                ))
                fig_s.update_layout(
                    title=lbl,
                    title_font=dict(family="Space Grotesk", size=10, color=col),
                    height=195,
                    margin=dict(l=10,r=10,t=36,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0b1120",
                    font=dict(color="#7c9cbf", size=9, family="JetBrains Mono"),
                    xaxis=dict(gridcolor="#132038", showticklabels=False),
                    yaxis=dict(gridcolor="#132038", range=[-1.1, 1.1]),
                    showlegend=False,
                )
                st.plotly_chart(fig_s, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — METRICS DASHBOARD
# ══════════════════════════════════════════════════════════════
with tab_metrics:
    st.markdown('<div class="section-header">Performance Metrics & Architecture Comparison</div>',
                unsafe_allow_html=True)

    bg = bit_growth(R, N, M)
    col_t, col_b = st.columns([3, 2])

    with col_t:
        st.markdown("**Architecture Comparison**")
        st.markdown(f"""
| Metric | Basic | Pipelined | Folded |
|--------|:-----:|:---------:|:------:|
| Adder count | {2*N} | {2*N} | **1** |
| Register count | {2*N} | **{4*N}** | {N+1} |
| MUX count | 0 | 0 | {N-1} |
| Critical path | {2*N} adders | **1 adder** | 1 adder |
| Pipeline latency | 0 | {2*N} cycles | ≥{2*N} cycles |
| Throughput | 1/clk | **1/clk** | 1/{N}/clk |
| Internal clock mult | 1× | 1× | **{N}×** |
| Bit growth | +{bg} | +{bg} | +{bg} |
| Best for | Low area | **Max speed** | **Min area** |
""")

    with col_b:
        categories = ['Throughput','Speed','Area Eff.','Power Eff.','Scalability']
        basic_scores    = [3, 2, 3, 4, 3]
        pipeline_scores = [5, 5, 2, 2, 4]
        folded_scores   = [3, 3, 5, 5, 3]

        RADAR_CONFIGS = [
            (basic_scores,    "Basic",     C_BLUE,   "rgba(96,165,250,0.12)"),
            (pipeline_scores, "Pipelined", C_GREEN,  "rgba(74,222,128,0.12)"),
            (folded_scores,   "Folded",    C_PURPLE, "rgba(192,132,252,0.12)"),
        ]
        fig_radar = go.Figure()
        for scores, name, color, fill in RADAR_CONFIGS:
            fig_radar.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill='toself', name=name,
                line=dict(color=color, width=2),
                fillcolor=fill,
            ))
        apply_dark(fig_radar, height=360)
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#0b1120",
                radialaxis=dict(range=[0,5], gridcolor="#132038",
                                tickfont=dict(size=8, color="#475569")),
                angularaxis=dict(gridcolor="#132038",
                                 tickfont=dict(size=9, color="#7c9cbf",
                                               family="Space Grotesk")),
            ),
            title="Architecture Trade-offs",
            legend=dict(bgcolor="rgba(7,13,26,0.9)", bordercolor="#1e3a5f",
                        font=dict(family="JetBrains Mono", size=10)),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    col_bg, col_noise = st.columns(2)
    with col_bg:
        R_vals = [2, 4, 8, 16, 32, 64, 128, 256]
        fig_bg = go.Figure()
        colors_n = [C_BLUE, C_CYAN, C_GREEN, C_YELLOW, C_ORANGE, C_PURPLE]
        for n_v in range(1, 7):
            fig_bg.add_trace(go.Scatter(
                x=R_vals, y=[bit_growth(r, n_v, M) for r in R_vals],
                mode="lines+markers", name=f"N={n_v}",
                line=dict(color=colors_n[n_v-1], width=1.8),
                marker=dict(size=5)
            ))
        fig_bg.update_layout(
            xaxis_title="R", yaxis_title="Bit Growth",
            xaxis_type="log", title=f"Bit Growth = N·⌈log₂(R·M)⌉  [M={M}]",
            legend=dict(bgcolor="rgba(7,13,26,0.9)", bordercolor="#1e3a5f",
                        font=dict(family="JetBrains Mono", size=10)),
            xaxis=dict(tickvals=R_vals, ticktext=[str(r) for r in R_vals]),
        )
        apply_dark(fig_bg, height=320)
        st.plotly_chart(fig_bg, use_container_width=True)

    with col_noise:
        R_test = [2,4,8,16,32,64]
        snr_gains = [10*np.log10(r) for r in R_test]
        fig_snr = go.Figure(go.Bar(
            x=[str(r) for r in R_test], y=snr_gains,
            marker=dict(
                color=snr_gains,
                colorscale=[[0,"#0e1729"],[0.5,"#3b82f6"],[1.0,"#22d3ee"]],
                showscale=False,
                line=dict(color="#3b82f6", width=1)
            ),
            text=[f"{g:.1f} dB" for g in snr_gains],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#60a5fa"),
        ))
        fig_snr.update_layout(
            title="Theoretical SNR Gain vs R (10·log₁₀ R)",
            xaxis_title="R (Decimation Factor)",
            yaxis_title="SNR Gain (dB)",
        )
        apply_dark(fig_snr, height=320)
        st.plotly_chart(fig_snr, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — VERILOG SIMULATION
# ══════════════════════════════════════════════════════════════
with tab_vlog:
    st.markdown('<div class="section-header">RTL Simulation via Icarus Verilog</div>',
                unsafe_allow_html=True)

    st.info(
        "**Required Verilog files in `verilog/` folder:**\n\n"
        "| Architecture | RTL file | Testbench |\n"
        "|---|---|---|\n"
        "| Basic | `cic_filter.v` | `cic_testbench.v` |\n"
        "| Pipelined | `cic_filter_pipelined.v` | `cic_tb_pipelined.v` |\n"
        "| Folded | `cic_filter_folded.v` | `cic_tb_folded.v` |"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sim_arch = st.selectbox("Architecture", ["Pipelined", "Basic", "Folded"], index=0)
    with c2:
        sim_r = st.selectbox("R for simulation", [2, 4, 8, 16], index=1)
    with c3:
        sim_n = st.selectbox("N for simulation", [1, 2, 3, 4], index=1)
    with c4:
        st.write("")
        st.write("")
        run_btn = st.button("▶ RUN SIMULATION", type="primary")

    if run_btn:
        with st.spinner("Compiling & simulating Verilog..."):
            output, err = run_iverilog(sim_r, sim_n, sim_arch)
        if err:
            st.error(err)
        else:
            st.success("✅ Simulation completed!")
            st.code(output, language="text")
            pattern = re.compile(r"VALID #(\d+).*?y_out=(-?\d+)")
            matches = pattern.findall(output)
            if matches:
                indices = [int(m[0]) for m in matches]
                values  = [int(m[1]) for m in matches]
                fig_v = go.Figure(go.Scatter(
                    x=indices, y=values,
                    mode="lines+markers",
                    line=dict(color=C_GREEN, width=2),
                    marker=dict(size=6, color=C_GREEN),
                    fill='tozeroy', fillcolor="rgba(74,222,128,0.06)"
                ))
                fig_v.update_layout(
                    title=f"RTL Output — valid_out samples  [{sim_arch}, R={sim_r}, N={sim_n}]",
                    xaxis_title="Valid Sample #", yaxis_title="y_out",
                )
                apply_dark(fig_v, height=340)
                st.plotly_chart(fig_v, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Architecture Comparison Table</div>',
                unsafe_allow_html=True)
    bg = bit_growth(R, N, M)
    st.markdown(f"""
| Metric | Basic | Pipelined | Folded |
|--------|:-----:|:---------:|:------:|
| Adder count | {2*N} | {2*N} | **1** |
| Register count | {2*N} | **{4*N}** | {N+1} |
| MUX count | 0 | 0 | {N-1} |
| Critical path | {2*N} adders | **1 adder** | 1 adder |
| Pipeline latency | 0 | {2*N} cycles | ≥{2*N} cycles |
| Throughput | 1/clk | **1/clk** | 1/{N}/clk |
| Internal clock mult | 1× | 1× | **{N}×** |
| Bit growth | +{bg} | +{bg} | +{bg} |
| Best for | Low area | **Max speed ✅** | **Min area ✅** |
""")

# ══════════════════════════════════════════════════════════════
# TAB 7 — VERILOG CODE VIEWER
# ══════════════════════════════════════════════════════════════
with tab_vcode:
    fpath, tpath = find_verilog()

    st.markdown('<div class="section-header">cic_filter_pipelined.v — Pipelined RTL</div>',
                unsafe_allow_html=True)

    pip_path = None
    for d in [VLOG_DIR,
              os.path.dirname(os.path.abspath(__file__)),
              "/mount/src/cic_decimation_filter/verilog",
              "/mount/src/cic_decimation_filter"]:
        p = os.path.join(d, "cic_filter_pipelined.v")
        if os.path.exists(p):
            pip_path = p
            break
    if pip_path is None and fpath:
        pip_path = fpath

    if pip_path:
        with open(pip_path) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("cic_filter_pipelined.v not found. Expected: `./verilog/cic_filter_pipelined.v`")

    st.markdown('<div class="section-header">cic_filter_folded.v — Folded RTL</div>',
                unsafe_allow_html=True)
    fold_path = None
    for d in [VLOG_DIR,
              os.path.dirname(os.path.abspath(__file__)),
              "/mount/src/cic_decimation_filter/verilog",
              "/mount/src/cic_decimation_filter"]:
        p = os.path.join(d, "cic_filter_folded.v")
        if os.path.exists(p):
            fold_path = p
            break
    if fold_path:
        with open(fold_path) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("cic_filter_folded.v not found. Expected: `./verilog/cic_filter_folded.v`")

    st.markdown('<div class="section-header">cic_filter.v — Basic RTL</div>',
                unsafe_allow_html=True)
    if fpath:
        with open(fpath) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("cic_filter.v not found. Expected: `./verilog/cic_filter.v`")

    st.markdown('<div class="section-header">Testbenches</div>',
                unsafe_allow_html=True)
    if tpath:
        with open(tpath) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("Testbench not found. Expected: `./verilog/cic_testbench.v`")

    st.markdown("---")
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#475569;
            background:#0b1323;border:1px solid #1e3a5f;border-radius:8px;padding:16px;">
  📎 GitHub: <a href="https://github.com/shashankchowdary-921/cic_decimation_filter"
               style="color:#60a5fa;text-decoration:none;">github.com/shashankchowdary-921/cic_decimation_filter</a><br>
  🌐 Live App: <a href="https://cic-decimation-filter.streamlit.app/"
               style="color:#22d3ee;text-decoration:none;">cic-decimation-filter.streamlit.app</a><br>
  📄 Reference: Hogenauer, E.B. — IEEE Trans. ASSP, vol.29 no.2, Apr 1981
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-family:'Space Grotesk',sans-serif;font-size:9px;
            font-weight:600;color:#1e3a5f;letter-spacing:2px;text-transform:uppercase;
            padding:6px 0 2px;">
  CIC Decimation Filter Simulator · Team Mavericks · 5G/6G RF Front-End
  <span style="color:#132038;"> · </span>
  Shashank · Pasyanth · Abin · Yagnesh
</div>
""", unsafe_allow_html=True)
