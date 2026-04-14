# ============================================================
# CIC DECIMATION FILTER — Interactive Simulator v2.0
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
# GLOBAL STYLES — Cyber/RF Dark Theme
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=JetBrains+Mono:wght@300;400;600&family=Rajdhani:wght@300;400;600&display=swap');

  /* ── Root & Body ── */
  html, body, [data-testid="stApp"] {
    background: #020817;
    color: #c9d8f0;
    font-family: 'Rajdhani', sans-serif;
  }
  .block-container { padding-top: 0.5rem; padding-bottom: 1rem; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050e1f 0%, #0a1628 100%);
    border-right: 1px solid #0d3060;
  }
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Orbitron', monospace;
    color: #3b9eff;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  /* ── Sidebar title ── */
  [data-testid="stSidebar"] .stTitle {
    font-family: 'Orbitron', monospace !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #050e1f;
    border-bottom: 2px solid #0d3060;
    gap: 2px;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    color: #4a7aaa;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px;
    border: 1px solid transparent;
    transition: all 0.3s ease;
  }
  .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0d3060, #0a1e40) !important;
    color: #3b9eff !important;
    border-color: #1a5499 !important;
    box-shadow: 0 0 12px rgba(59,158,255,0.3);
  }
  .stTabs [data-baseweb="tab-panel"] {
    background: #020817;
    padding-top: 1rem;
  }

  /* ── Metric Cards ── */
  div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0a1628 0%, #050e1f 100%);
    border: 1px solid #0d3060;
    border-radius: 8px;
    padding: 10px 14px;
    box-shadow: 0 0 15px rgba(0,80,180,0.1), inset 0 0 20px rgba(0,0,0,0.3);
    font-family: 'JetBrains Mono', monospace;
  }
  div[data-testid="metric-container"] label {
    color: #3b9eff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
  }
  div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: #a8d4ff !important;
    font-size: 1.2rem !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, #0d3060, #1a5499);
    border: 1px solid #3b9eff;
    color: #3b9eff;
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    letter-spacing: 1.5px;
    border-radius: 6px;
    padding: 8px 20px;
    box-shadow: 0 0 15px rgba(59,158,255,0.2);
    transition: all 0.3s ease;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #1a5499, #2470cc);
    box-shadow: 0 0 25px rgba(59,158,255,0.4);
    color: #ffffff;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00b4d8, #0077b6);
    border-color: #00b4d8;
    color: white;
    box-shadow: 0 0 20px rgba(0,180,216,0.4);
  }

  /* ── Info / Warning boxes ── */
  .stInfo, .stAlert {
    background: linear-gradient(135deg, #050e1f, #0a1628);
    border-left: 3px solid #3b9eff;
    border-radius: 0 8px 8px 0;
    font-family: 'Rajdhani', sans-serif;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    background: #0a1628 !important;
    border: 1px solid #0d3060 !important;
    border-radius: 6px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 11px !important;
    color: #3b9eff !important;
    letter-spacing: 1px;
  }
  .streamlit-expanderContent {
    background: #050e1f !important;
    border: 1px solid #0d3060 !important;
    border-top: none !important;
  }

  /* ── Divider ── */
  hr { border-color: #0d3060 !important; }

  /* ── Select boxes & Sliders ── */
  .stSelectbox > div > div,
  .stSlider > div,
  .stSelectSlider > div {
    background: #0a1628;
  }

  /* ── Header Banner ── */
  .hero-banner {
    background: linear-gradient(135deg, #020c1b 0%, #050e1f 30%, #0a1628 60%, #020c1b 100%);
    border: 1px solid #0d3060;
    border-radius: 12px;
    padding: 20px 30px 16px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(0,80,180,0.15), inset 0 0 60px rgba(0,0,0,0.4);
  }
  .hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
      90deg, transparent, transparent 40px,
      rgba(59,158,255,0.015) 40px, rgba(59,158,255,0.015) 41px
    ),
    repeating-linear-gradient(
      0deg, transparent, transparent 40px,
      rgba(59,158,255,0.015) 40px, rgba(59,158,255,0.015) 41px
    );
    pointer-events: none;
  }
  .hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #3b9eff;
    text-shadow: 0 0 20px rgba(59,158,255,0.5);
    margin: 0;
    line-height: 1.3;
  }
  .hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #4a7aaa;
    letter-spacing: 2px;
    margin-top: 4px;
  }
  .hero-tag {
    font-family: 'Orbitron', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    color: #00b4d8;
    text-transform: uppercase;
    border: 1px solid #00b4d8;
    border-radius: 4px;
    padding: 2px 8px;
    display: inline-block;
    box-shadow: 0 0 8px rgba(0,180,216,0.3);
    margin-bottom: 6px;
  }

  /* ── Author Cards ── */
  .author-grid {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 10px;
  }
  .author-card {
    background: linear-gradient(135deg, #0a1628, #050e1f);
    border: 1px solid #0d3060;
    border-radius: 8px;
    padding: 8px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #7ab8ff;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 0 10px rgba(0,60,150,0.2);
    transition: all 0.3s ease;
  }
  .author-card:hover {
    border-color: #3b9eff;
    box-shadow: 0 0 18px rgba(59,158,255,0.3);
    color: #a8d4ff;
  }
  .author-num {
    font-family: 'Orbitron', monospace;
    font-size: 9px;
    color: #3b9eff;
    letter-spacing: 1px;
  }

  /* ── Section Headers ── */
  .section-header {
    font-family: 'Orbitron', monospace;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #3b9eff;
    text-transform: uppercase;
    border-bottom: 1px solid #0d3060;
    padding-bottom: 8px;
    margin-bottom: 14px;
    margin-top: 8px;
    text-shadow: 0 0 10px rgba(59,158,255,0.3);
  }

  /* ── Workflow Cards ── */
  .workflow-card {
    background: linear-gradient(135deg, #0a1628, #050e1f);
    border: 1px solid #0d3060;
    border-left: 3px solid #3b9eff;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-family: 'Rajdhani', sans-serif;
  }
  .workflow-card-title {
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    color: #3b9eff;
    letter-spacing: 2px;
    margin-bottom: 6px;
  }
  .workflow-card-body {
    font-size: 14px;
    color: #8ab4d8;
    line-height: 1.5;
  }
  .wc-green  { border-left-color: #22c55e; }
  .wc-yellow { border-left-color: #eab308; }
  .wc-purple { border-left-color: #a855f7; }
  .wc-cyan   { border-left-color: #06b6d4; }
  .wc-orange { border-left-color: #f97316; }

  .wc-green  .workflow-card-title  { color: #22c55e; }
  .wc-yellow .workflow-card-title  { color: #eab308; }
  .wc-purple .workflow-card-title  { color: #a855f7; }
  .wc-cyan   .workflow-card-title  { color: #06b6d4; }
  .wc-orange .workflow-card-title  { color: #f97316; }

  /* ── Badge ── */
  .badge {
    display: inline-block;
    font-family: 'Orbitron', monospace;
    font-size: 8px;
    letter-spacing: 1px;
    padding: 2px 7px;
    border-radius: 4px;
    margin-left: 6px;
    vertical-align: middle;
  }
  .badge-blue   { background: rgba(59,158,255,0.15); border: 1px solid #3b9eff; color: #3b9eff; }
  .badge-green  { background: rgba(34,197,94,0.15);  border: 1px solid #22c55e; color: #22c55e; }
  .badge-purple { background: rgba(168,85,247,0.15); border: 1px solid #a855f7; color: #a855f7; }
  .badge-orange { background: rgba(249,115,22,0.15); border: 1px solid #f97316; color: #f97316; }

  /* ── Code blocks ── */
  .stCode {
    font-family: 'JetBrains Mono', monospace !important;
    background: #050e1f !important;
    border: 1px solid #0d3060 !important;
  }

  /* ── Table ── */
  table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
  }
  th {
    background: #0a1628;
    color: #3b9eff;
    font-family: 'Orbitron', monospace;
    font-size: 9px;
    letter-spacing: 1.5px;
    padding: 8px 12px;
    border: 1px solid #0d3060;
    text-transform: uppercase;
  }
  td {
    background: #050e1f;
    color: #8ab4d8;
    padding: 7px 12px;
    border: 1px solid #0d3060;
  }
  tr:hover td { background: #0a1628; color: #c9d8f0; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #020817; }
  ::-webkit-scrollbar-thumb { background: #0d3060; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #3b9eff; }

  /* ── Radio / Checkboxes ── */
  .stRadio label, .stCheckbox label {
    font-family: 'Rajdhani', sans-serif;
    color: #8ab4d8;
  }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;font-size:14px;font-weight:900;
                color:#3b9eff;letter-spacing:3px;text-align:center;
                padding:10px 0 4px;text-shadow:0 0 15px rgba(59,158,255,0.5);">
      📡 CIC FILTER<br>
      <span style="font-size:9px;color:#4a7aaa;letter-spacing:4px;">CONTROL PANEL</span>
    </div>
    <hr style="border-color:#0d3060;margin:8px 0 12px;">
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
    st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:9px;
                    color:#4a7aaa;letter-spacing:2px;">OUTPUT RATE</div>""",
                unsafe_allow_html=True)
    st.metric("", fs_out_str)
    st.markdown("---")

    st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:9px;
                    color:#4a7aaa;letter-spacing:2px;margin-bottom:8px;">TEST SIGNAL</div>""",
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
    <div style="font-family:'Orbitron',monospace;font-size:8px;color:#1a4080;
                letter-spacing:2px;text-align:center;padding-top:4px;">
      TEAM MAVERICKS · 2024<br>5G/6G RF FRONT-END
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
# CIC MODELS
# ──────────────────────────────────────────────────────────────

def cic_basic(x, R, N, M=1):
    y = x.astype(float)
    for _ in range(N):
        y = np.cumsum(y)
    y = y[::R]
    for _ in range(N):
        y = np.diff(y, M, prepend=np.zeros(M))
    return y

def cic_pipelined(x, R, N, M=1):
    y = x.astype(float)
    for _ in range(N):
        y = np.cumsum(y)
        reg = np.roll(y, 1); reg[0] = 0.0
        y = reg
    y = y[::R]
    for _ in range(N):
        y = np.diff(y, M, prepend=np.zeros(M))
        reg = np.roll(y, 1); reg[0] = 0.0
        y = reg
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
    fr = np.fft.rfftfreq(nfft, 1/fs)
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

# Run chosen architecture
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

def run_iverilog(r_val=4, n_val=2):
    fpath, tpath = find_verilog()
    if fpath is None:
        return None, "Verilog files not found. Place cic_filter.v and cic_testbench.v in the `verilog/` folder."
    with tempfile.TemporaryDirectory() as tmp:
        out_bin = os.path.join(tmp, "cic_sim")
        with open(tpath) as f:
            tb = f.read()
        tb = re.sub(r"\.R\(\d+\)", f".R({r_val})", tb)
        tb = re.sub(r"\.N\(\d+\)", f".N({n_val})", tb)
        tb_file = os.path.join(tmp, "tb.v")
        with open(tb_file, "w") as f:
            f.write(tb)
        try:
            cp = subprocess.run(["iverilog", "-o", out_bin, fpath, tb_file],
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
    plot_bgcolor="#020c1b",
    font=dict(color="#8ab4d8", family="JetBrains Mono"),
    margin=dict(t=50, b=30, l=55, r=20),
)
GRID = dict(gridcolor="#0d2040", zerolinecolor="#1a3060", gridwidth=1)

def apply_dark(fig, height=420):
    fig.update_layout(height=height, **DARK)
    for ax in fig.layout:
        if ax.startswith("xaxis") or ax.startswith("yaxis"):
            fig.layout[ax].update(**GRID)
    fig.update_layout(
        title_font=dict(family="Orbitron", size=12, color="#3b9eff"),
    )
    return fig

# colour palette
C_BLUE   = "#3b9eff"
C_CYAN   = "#06b6d4"
C_GREEN  = "#22c55e"
C_ORANGE = "#f97316"
C_PURPLE = "#a855f7"
C_PINK   = "#ec4899"
C_YELLOW = "#eab308"

# ──────────────────────────────────────────────────────────────
# HERO BANNER
# ──────────────────────────────────────────────────────────────
bg_bit = bit_growth(R, N, M)
snr_in  = snr_calc(x_norm, f_sig, fs_in)
snr_out = snr_calc(y_norm, f_sig, fs_out)

st.markdown(f"""
<div class="hero-banner">
  <div class="hero-tag">5G / 6G RF FRONT-END · DSP PROJECT</div>
  <div class="hero-title">📡 CIC DECIMATION FILTER</div>
  <div class="hero-sub">INTERACTIVE RTL SIMULATOR · TEAM MAVERICKS</div>
  <div class="author-grid" style="margin-top:12px;">
    <div class="author-card">
      <span style="color:#3b9eff;font-size:16px;">①</span>
      <div>
        <div style="color:#a8d4ff;font-size:12px;font-weight:600;">Shashank T</div>
        <div class="author-num">REG · 23BVD1031</div>
      </div>
    </div>
    <div class="author-card">
      <span style="color:#06b6d4;font-size:16px;">②</span>
      <div>
        <div style="color:#a8d4ff;font-size:12px;font-weight:600;">Pasyanth P</div>
        <div class="author-num">REG · 23BVD1004</div>
      </div>
    </div>
    <div class="author-card">
      <span style="color:#a855f7;font-size:16px;">③</span>
      <div>
        <div style="color:#a8d4ff;font-size:12px;font-weight:600;">Abin Mohammad</div>
        <div class="author-num">REG · 23BVD1047</div>
      </div>
    </div>
    <div class="author-card">
      <span style="color:#22c55e;font-size:16px;">④</span>
      <div>
        <div style="color:#a8d4ff;font-size:12px;font-weight:600;">Yagnesh</div>
        <div class="author-num">TEAM MAVERICKS</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ──
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
c1.metric("Architecture",   architecture)
c2.metric("Input Rate",     fs_label)
c3.metric("Output Rate",    fs_out_str)
c4.metric("Decimation R",   f"÷{R}")
c5.metric("Stages N",       str(N))
c6.metric("Bit Growth",     f"+{bg_bit} bits")
c7.metric("SNR Δ",          f"{snr_out-snr_in:+.1f} dB")

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────
tab_sim, tab_freq, tab_arch, tab_stages, tab_metrics, tab_flow, tab_vlog, tab_vcode = st.tabs([
    "🌊 SIMULATE",
    "📈 FREQ RESPONSE",
    "🏗️ ARCHITECTURE",
    "📊 STAGE ANALYSIS",
    "📐 METRICS",
    "🗺️ PROJECT FLOW",
    "⚡ RTL SIMULATION",
    "📄 VERILOG CODE",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SIMULATE
# ══════════════════════════════════════════════════════════════
with tab_sim:
    st.markdown('<div class="section-header">TIME-DOMAIN WAVEFORMS & SPECTRAL ANALYSIS</div>',
                unsafe_allow_html=True)

    disp_in  = min(n_samples, 300)
    disp_out = min(len(y_out), 300)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"◈ Input x[n]  ·  {fs_label}",
            f"◈ Output y[m]  ·  {fs_out_str}",
            "◈ Input Spectrum",
            "◈ Output Spectrum",
        ],
        vertical_spacing=0.18, horizontal_spacing=0.08,
    )
    fig.add_trace(go.Scatter(
        x=t_in[:disp_in], y=x_norm[:disp_in],
        mode="lines", line=dict(color=C_BLUE, width=1.3),
        fill='tozeroy', fillcolor="rgba(59,158,255,0.06)", name="x[n]"
    ), row=1, col=1)

    y_fnorm = y_out / (np.max(np.abs(y_out))+1e-12)
    fig.add_trace(go.Scatter(
        x=t_out[:disp_out], y=y_fnorm[:disp_out],
        mode="lines", line=dict(color=C_ORANGE, width=1.5),
        fill='tozeroy', fillcolor="rgba(249,115,22,0.06)", name="y[m]"
    ), row=1, col=2)

    nfft = 2048
    X  = np.abs(np.fft.rfft(x_norm, n=nfft)) / nfft
    fx = np.fft.rfftfreq(nfft, 1/fs_in) / 1e3
    fig.add_trace(go.Scatter(
        x=fx, y=20*np.log10(np.maximum(X,1e-10)),
        mode="lines", line=dict(color=C_BLUE, width=0.9), name="Input PSD"
    ), row=2, col=1)

    Y  = np.abs(np.fft.rfft(y_norm, n=nfft)) / nfft
    fy = np.fft.rfftfreq(nfft, R/fs_in) / 1e3
    fig.add_trace(go.Scatter(
        x=fy, y=20*np.log10(np.maximum(Y,1e-10)),
        mode="lines", line=dict(color=C_ORANGE, width=0.9), name="Output PSD"
    ), row=2, col=2)

    fig.update_xaxes(title_text="Time (µs)", title_font=dict(size=10), row=1, col=1)
    fig.update_xaxes(title_text="Time (µs)", title_font=dict(size=10), row=1, col=2)
    fig.update_xaxes(title_text="Freq (kHz)", title_font=dict(size=10),
                     range=[0, min(fs_in/2e3,200)], row=2, col=1)
    fig.update_xaxes(title_text="Freq (kHz)", title_font=dict(size=10),
                     range=[0, fs_out/2e3], row=2, col=2)
    fig.update_yaxes(title_text="Amplitude", title_font=dict(size=10), row=1, col=1)
    fig.update_yaxes(title_text="Amplitude", title_font=dict(size=10), row=1, col=2)
    fig.update_yaxes(title_text="dBFS", title_font=dict(size=10),
                     range=[-100, 5], row=2, col=1)
    fig.update_yaxes(title_text="dBFS", title_font=dict(size=10),
                     range=[-100, 5], row=2, col=2)

    # title font for subplot titles
    for ann in fig.layout.annotations:
        ann.font = dict(family="Orbitron", size=10, color="#3b9eff")

    apply_dark(fig, height=560)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # SNR row
    sfdr_out = sfdr_calc(y_norm, fs_out)
    thd_out  = thd_calc(y_norm, f_sig, fs_out) if sig_type in ["Sine","Square","Multi-tone"] else float('nan')
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Input SNR",      f"{snr_in:.1f} dB")
    s2.metric("Output SNR",     f"{snr_out:.1f} dB")
    s3.metric("SNR Change",     f"{snr_out-snr_in:+.1f} dB")
    s4.metric("SFDR (out)",     f"{sfdr_out:.1f} dB")
    if not np.isnan(thd_out):
        s5.metric("THD (out)",  f"{thd_out:.1f} dB")
    else:
        s5.metric("THD (out)",  "N/A")

# ══════════════════════════════════════════════════════════════
# TAB 2 — FREQUENCY RESPONSE
# ══════════════════════════════════════════════════════════════
with tab_freq:
    st.markdown('<div class="section-header">CIC MAGNITUDE RESPONSE</div>', unsafe_allow_html=True)

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
            fill='tozeroy', fillcolor="rgba(59,158,255,0.04)"
        ))

        if show_comp:
            # Simple sinc compensation: 1/H^0.5 approximation
            f_comp = f_ax[mask]
            with np.errstate(divide="ignore", invalid="ignore"):
                h_comp_inv = -H_db[mask] * 0.5  # add back half the droop
            fig_fr.add_trace(go.Scatter(
                x=f_comp/1e6, y=h_comp_inv,
                mode="lines", line=dict(color=C_GREEN, width=1.5, dash="dot"),
                name="Compensation gain"
            ))
            comp_total = H_db[mask] + h_comp_inv
            fig_fr.add_trace(go.Scatter(
                x=f_comp/1e6, y=comp_total,
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
                         annotation_text="-3dB",
                         annotation_font=dict(size=9, color=C_ORANGE))
        fig_fr.add_hline(y=-6, line=dict(color=C_PURPLE, dash="dash", width=1))

        fig_fr.update_layout(
            title=f"CIC Response  [N={N}, R={R}, M={M}, Fs={fs_in/1e6:.1f} MHz]",
            xaxis_title="Frequency (MHz)", yaxis_title="Magnitude (dB)",
            xaxis_range=[0, f_lim], yaxis_range=[y_min_db, 5],
            legend=dict(bgcolor="rgba(2,8,23,0.8)", bordercolor="#0d3060",
                        font=dict(family="JetBrains Mono", size=10)),
        )
        apply_dark(fig_fr)
        st.plotly_chart(fig_fr, use_container_width=True)

    st.markdown('<div class="section-header">PASSBAND DETAIL</div>', unsafe_allow_html=True)
    pb_mask = f_ax <= 0.5*fs_out
    fig_pb  = go.Figure(go.Scatter(
        x=f_ax[pb_mask]/1e3, y=H_db[pb_mask],
        mode="lines", line=dict(color=C_CYAN, width=2),
        fill='tozeroy', fillcolor="rgba(6,182,212,0.05)"
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
    st.markdown(f'<div class="section-header">BLOCK DIAGRAM — {architecture} (N={N}, R={R}, M={M})</div>',
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
            arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#3b6ea0")

    C_INT  = "rgb(59,158,255)"
    C_DS   = "rgb(249,115,22)"
    C_COMB = "rgb(34,197,94)"
    C_FF   = "rgb(168,85,247)"
    C_IN   = "rgb(6,182,212)"

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
                         line=dict(color="#334466", dash="dash"))
        fig_bd.add_annotation(x=ds_x-1.5, y=0.2, text="← Fs_in →",
                               showarrow=False, font=dict(size=9,color="#4a7aaa"))
        fig_bd.add_annotation(x=ds_x+1.5, y=0.2, text="← Fs_out →",
                               showarrow=False, font=dict(size=9,color="#4a7aaa"))
        if architecture == "Folded":
            fig_bd.add_annotation(x=pos[N//2+1], y=2.4,
                text=f"⚡ 1 Shared Adder  ×{N} time-mux  |  Internal clk = {N}× Fs_in",
                showarrow=False, font=dict(size=11, color="#f97316"),
                bgcolor="rgba(249,115,22,0.1)", bordercolor="#f97316", borderwidth=1)
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
            showarrow=False, font=dict(size=11, color="#ce93d8"),
            bgcolor="rgba(168,85,247,0.1)", bordercolor="#a855f7", borderwidth=1)

    apply_dark(fig_bd, height=280)
    st.plotly_chart(fig_bd, use_container_width=True)

    desc = {
        "Basic": (
            "**Basic CIC:** N integrators run at Fs_in. "
            "After ↓R downsampling, N comb (differencer) sections run at Fs_out. "
            "No pipeline registers — minimal hardware, but critical path spans all N adders."
        ),
        "Pipelined": (
            f"**Pipelined CIC (matches RTL `cic_filter.v`):** "
            f"A D flip-flop (FF) after every integrator and every comb stage creates a "
            f"**{2*N}-stage deep pipeline**. Critical path = 1 adder → maximum clock speed. "
            f"Latency = {2*N} clock cycles. Throughput = 1 output per R input clocks."
        ),
        "Folded": (
            f"**Folded CIC:** A single adder is reused {N}× per input sample via time-multiplexing. "
            f"Internal clock runs at {N}× Fs_in. Area reduced by ~{2*N-1} adders vs Basic. "
            "Throughput same as Basic."
        ),
    }
    st.info(desc[architecture])

    with st.expander("📐 TRANSFER FUNCTION & KEY EQUATIONS"):
        st.latex(r"H(z) = \left(\frac{1 - z^{-RM}}{1 - z^{-1}}\right)^N")
        st.latex(r"|H(f)| = \left|\frac{\sin(\pi M R f/F_s)}{\sin(\pi f/F_s)}\right|^N")
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
    st.markdown('<div class="section-header">PER-STAGE OUTPUT WAVEFORMS (normalised)</div>',
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
        yc2 = np.diff(yc2, M, prepend=np.zeros(M))
        if architecture == "Pipelined":
            reg = np.roll(yc2,1); reg[0]=0.0; yc2=reg
        y_stages.append(yc2.copy())
        stage_labels.append(f"Comb {i+1}" + (" + FF" if architecture=="Pipelined" else ""))

    STAGE_COLORS = [C_CYAN, C_BLUE, "#1E88E5", "#1565C0",
                    C_ORANGE, "#ef4444", C_GREEN, "#43A047", "#2E7D32",
                    C_PURPLE, "#7E57C2", C_PINK]

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
                    line=dict(color=col, width=1.2),
                    fill='tozeroy',
                    fillcolor="rgba(59,158,255,0.05)"
                ))
                fig_s.update_layout(
                    title=lbl,
                    title_font=dict(family="Orbitron", size=9, color=col),
                    height=190,
                    margin=dict(l=10,r=10,t=35,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#020c1b",
                    font=dict(color="#8ab4d8", size=9, family="JetBrains Mono"),
                    xaxis=dict(gridcolor="#0d2040", showticklabels=False),
                    yaxis=dict(gridcolor="#0d2040", range=[-1.1, 1.1]),
                    showlegend=False,
                )
                fig_s.update_traces(line_color=col)
                st.plotly_chart(fig_s, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — METRICS DASHBOARD
# ══════════════════════════════════════════════════════════════
with tab_metrics:
    st.markdown('<div class="section-header">PERFORMANCE METRICS & ARCHITECTURE COMPARISON</div>',
                unsafe_allow_html=True)

    # Architecture Comparison Table
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
        # Spider / radar chart comparing architectures
        categories = ['Throughput','Speed','Area Eff.','Power Eff.','Scalability']
        basic_scores   = [3, 2, 3, 4, 3]
        pipeline_scores= [5, 5, 2, 2, 4]
        folded_scores  = [3, 3, 5, 5, 3]

        RADAR_CONFIGS = [
            (basic_scores,    "Basic",     C_BLUE,   "rgba(59,158,255,0.15)"),
            (pipeline_scores, "Pipelined", C_GREEN,  "rgba(34,197,94,0.15)"),
            (folded_scores,   "Folded",    C_PURPLE, "rgba(168,85,247,0.15)"),
        ]
        fig_radar = go.Figure()
        for scores, name, color, fill in RADAR_CONFIGS:
            fig_radar.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=name,
                line=dict(color=color, width=2),
                fillcolor=fill,
            ))
        apply_dark(fig_radar, height=360)
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#020c1b",
                radialaxis=dict(range=[0,5], gridcolor="#0d2040",
                                tickfont=dict(size=8, color="#4a7aaa")),
                angularaxis=dict(gridcolor="#0d2040",
                                 tickfont=dict(size=9, color="#8ab4d8", family="Orbitron")),
            ),
            title="Architecture Trade-offs",
            legend=dict(bgcolor="rgba(2,8,23,0.8)", bordercolor="#0d3060",
                        font=dict(family="JetBrains Mono", size=10)),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # Bit Growth vs R chart
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
            legend=dict(bgcolor="rgba(2,8,23,0.8)", bordercolor="#0d3060",
                        font=dict(family="JetBrains Mono", size=10)),
            xaxis=dict(tickvals=R_vals, ticktext=[str(r) for r in R_vals]),
        )
        apply_dark(fig_bg, height=320)
        st.plotly_chart(fig_bg, use_container_width=True)

    with col_noise:
        # SNR improvement vs R
        R_test = [2,4,8,16,32,64]
        snr_gains = [10*np.log10(r) for r in R_test]
        fig_snr = go.Figure(go.Bar(
            x=[str(r) for r in R_test], y=snr_gains,
            marker=dict(
                color=snr_gains,
                colorscale=[[0,"#0d3060"],[0.5,"#3b9eff"],[1.0,"#06b6d4"]],
                showscale=False,
                line=dict(color="#3b9eff", width=1)
            ),
            text=[f"{g:.1f} dB" for g in snr_gains],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#3b9eff"),
        ))
        fig_snr.update_layout(
            title="Theoretical SNR Gain vs R (10·log₁₀ R)",
            xaxis_title="R (Decimation Factor)",
            yaxis_title="SNR Gain (dB)",
        )
        apply_dark(fig_snr, height=320)
        st.plotly_chart(fig_snr, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — PROJECT FLOW
# ══════════════════════════════════════════════════════════════
with tab_flow:
    st.markdown('<div class="section-header">PROJECT WORKFLOW — TEAM MAVERICKS</div>',
                unsafe_allow_html=True)

    # Flow diagram using plotly
    fig_flow = go.Figure()
    fig_flow.update_layout(
        xaxis=dict(range=[-0.5, 12], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-0.5, 10], showgrid=False, zeroline=False, visible=False),
        height=480, margin=dict(l=10,r=10,t=40,b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0", family="JetBrains Mono"),
        title=dict(text="Summary Flow — CIC Filter Project",
                   font=dict(family="Orbitron", size=12, color="#3b9eff"))
    )

    def flow_box(fig, cx, cy, label, sub, color, w=1.8, h=0.7):
        rgb = re.findall(r'\d+', color)
        r2,g2,b2 = (int(x) for x in rgb[:3])
        fig.add_shape(type="rect",
            x0=cx-w/2, x1=cx+w/2, y0=cy-h/2, y1=cy+h/2,
            line=dict(color=color, width=2),
            fillcolor=f"rgba({r2},{g2},{b2},0.15)")
        fig.add_annotation(x=cx, y=cy+0.15, text=f"<b>{label}</b>",
            showarrow=False, font=dict(size=11, color=color, family="Orbitron"),
            align="center")
        if sub:
            fig.add_annotation(x=cx, y=cy-0.2, text=sub,
                showarrow=False, font=dict(size=9, color="#8ab4d8"),
                align="center")

    def flow_arrow(fig, x0, y0, x1, y1):
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0,
            axref="x", ayref="y", xref="x", yref="y",
            arrowhead=2, arrowsize=1.2, arrowwidth=2, arrowcolor="#1a5499")

    # Nodes
    flow_box(fig_flow, 6, 9.0, "TOPIC", "CIC Decimation Filter for 5G/6G", "rgb(59,158,255)", w=3, h=0.8)

    # Individual tasks
    flow_box(fig_flow, 2, 7.2, "INDIVIDUAL", "Pipelining Analysis", "rgb(168,85,247)", w=2.5, h=0.8)
    flow_box(fig_flow, 6, 7.2, "INDIVIDUAL", "Folding Analysis", "rgb(34,197,94)", w=2.5, h=0.8)
    flow_box(fig_flow, 10, 7.2, "INDIVIDUAL", "CIC Theory & Ref", "rgb(249,115,22)", w=2.5, h=0.8)

    # Group tasks
    flow_box(fig_flow, 4, 5.2, "GROUP TASK", "Verilog RTL Design", "rgb(6,182,212)", w=3, h=0.8)
    flow_box(fig_flow, 8, 5.2, "GROUP TASK", "Testbench & Verify", "rgb(6,182,212)", w=3, h=0.8)

    # Pipelining
    flow_box(fig_flow, 2, 3.2, "PIPELINING", "Paper Submission", "rgb(168,85,247)", w=2.8, h=0.8)
    flow_box(fig_flow, 5, 3.2, "PIPELINING", "Code → Sim Output", "rgb(168,85,247)", w=2.8, h=0.8)

    # Folding
    flow_box(fig_flow, 7.5, 3.2, "FOLDING", "Work on Paper", "rgb(34,197,94)", w=2.4, h=0.8)
    flow_box(fig_flow, 10.5, 3.2, "FOLDING", "Code → Sim Output", "rgb(34,197,94)", w=2.4, h=0.8)

    # Final
    flow_box(fig_flow, 6, 1.2, "FINAL OUTPUT", "RTL + Simulator + Paper", "rgb(234,179,8)", w=4, h=0.8)

    # Arrows — Topic → Individuals
    flow_arrow(fig_flow, 6, 8.6, 2, 7.6)
    flow_arrow(fig_flow, 6, 8.6, 6, 7.6)
    flow_arrow(fig_flow, 6, 8.6, 10, 7.6)

    # Individuals → Group Tasks
    flow_arrow(fig_flow, 2, 6.8, 4, 5.6)
    flow_arrow(fig_flow, 6, 6.8, 4, 5.6)
    flow_arrow(fig_flow, 6, 6.8, 8, 5.6)
    flow_arrow(fig_flow, 10, 6.8, 8, 5.6)

    # Group → Pipelining
    flow_arrow(fig_flow, 4, 4.8, 2, 3.6)
    flow_arrow(fig_flow, 4, 4.8, 5, 3.6)
    # Group → Folding
    flow_arrow(fig_flow, 8, 4.8, 7.5, 3.6)
    flow_arrow(fig_flow, 8, 4.8, 10.5, 3.6)

    # Pipelining/Folding → Final
    flow_arrow(fig_flow, 2, 2.8, 6, 1.6)
    flow_arrow(fig_flow, 5, 2.8, 6, 1.6)
    flow_arrow(fig_flow, 7.5, 2.8, 6, 1.6)
    flow_arrow(fig_flow, 10.5, 2.8, 6, 1.6)

    apply_dark(fig_flow, height=480)
    st.plotly_chart(fig_flow, use_container_width=True)

    st.markdown("---")

    # Detailed breakdown cards
    st.markdown('<div class="section-header">TASK BREAKDOWN</div>', unsafe_allow_html=True)
    col_a, col_b_col = st.columns(2)

    with col_a:
        st.markdown("""
<div class="workflow-card wc-blue">
  <div class="workflow-card-title">📌 TOPIC</div>
  <div class="workflow-card-body">
    Verilog HDL Design of a High-Speed Decimation Filter for 5G/6G RF Front-End Systems
    using a Cascaded Integrator-Comb (CIC) architecture.
  </div>
</div>

<div class="workflow-card wc-purple">
  <div class="workflow-card-title">👤 INDIVIDUAL TASK — PIPELINING</div>
  <div class="workflow-card-body">
    <b>Assigned to: Shashank T & Pasyanth P</b><br>
    • Study and derive pipelined CIC architecture on paper<br>
    • Write RTL Verilog code for pipelined design<br>
    • Run simulation and capture output waveforms<br>
    • Submit paper analysis with equations and diagrams
  </div>
</div>

<div class="workflow-card wc-green">
  <div class="workflow-card-title">👤 INDIVIDUAL TASK — FOLDING</div>
  <div class="workflow-card-body">
    <b>Assigned to: Abin Mohammad & Yagnesh</b><br>
    • Work out the folded CIC architecture by hand<br>
    • Implement Verilog code for time-multiplexed folded design<br>
    • Run simulation and capture output<br>
    • Document area vs speed trade-offs
  </div>
</div>
""", unsafe_allow_html=True)

    with col_b_col:
        st.markdown("""
<div class="workflow-card wc-cyan">
  <div class="workflow-card-title">🤝 GROUP TASK</div>
  <div class="workflow-card-body">
    • Integrate pipelined + folded modules into one RTL project<br>
    • Develop shared testbench (cic_testbench.v)<br>
    • Cross-verify simulation outputs between architectures<br>
    • Prepare frequency response and attenuation plots<br>
    • Write joint project report (VDSP_Project.pdf)
  </div>
</div>

<div class="workflow-card wc-yellow">
  <div class="workflow-card-title">📄 PAPER SUBMISSION</div>
  <div class="workflow-card-body">
    • Reference: Hogenauer, E.B. (1981) — IEEE Trans. ASSP, vol.29, no.2<br>
    • Work out CIC decimation & interpolation theory on paper<br>
    • Derive H(z) transfer function and passband droop equations<br>
    • Compare Basic / Pipelined / Folded architectures analytically<br>
    • Submit paper + simulation output screenshots
  </div>
</div>

<div class="workflow-card wc-orange">
  <div class="workflow-card-title">✅ DELIVERABLES</div>
  <div class="workflow-card-body">
    • cic_filter.v — RTL source<br>
    • cic_testbench.v — Functional testbench<br>
    • Streamlit interactive simulator (this app)<br>
    • VDSP_Project.pdf — Full report<br>
    • GitHub: shashankchowdary-921/cic_decimation_filter
  </div>
</div>
""", unsafe_allow_html=True)

    # Team member roles
    st.markdown("---")
    st.markdown('<div class="section-header">TEAM ROLES</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    for col_r, name, reg, role, color in [
        (r1, "Shashank T",    "23BVD1031", "Pipelining RTL\n& Simulation",  "#3b9eff"),
        (r2, "Pasyanth P",    "23BVD1004", "CIC Theory &\nPaper Analysis",   "#06b6d4"),
        (r3, "Abin Mohammad", "23BVD1047", "Folding RTL\n& Testbench",       "#a855f7"),
        (r4, "Yagnesh",       "–",         "Folding Theory\n& Verification",  "#22c55e"),
    ]:
        col_r.markdown(f"""
<div style="background:linear-gradient(135deg,#0a1628,#050e1f);border:1px solid {color};
            border-radius:10px;padding:16px;text-align:center;
            box-shadow:0 0 15px {color}33;">
  <div style="font-family:'Orbitron',monospace;font-size:18px;color:{color};margin-bottom:4px;">
    ◈
  </div>
  <div style="font-family:'Orbitron',monospace;font-size:11px;color:{color};
              letter-spacing:1px;margin-bottom:4px;">{name}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#4a7aaa;
              margin-bottom:8px;">{reg}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:#8ab4d8;
              white-space:pre-line;">{role}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 7 — VERILOG SIMULATION
# ══════════════════════════════════════════════════════════════
with tab_vlog:
    st.markdown('<div class="section-header">RTL SIMULATION VIA IVERILOG</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        sim_r = st.selectbox("R for simulation", [2, 4, 8, 16], index=1)
    with c2:
        sim_n = st.selectbox("N for simulation", [1, 2, 3, 4], index=1)
    with c3:
        st.write("")
        st.write("")
        run_btn = st.button("▶ RUN SIMULATION", type="primary")

    if run_btn:
        with st.spinner("Compiling & simulating Verilog..."):
            output, err = run_iverilog(sim_r, sim_n)
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
                    fill='tozeroy', fillcolor="rgba(34,197,94,0.05)"
                ))
                fig_v.update_layout(
                    title=f"RTL Output — valid_out samples  [R={sim_r}, N={sim_n}]",
                    xaxis_title="Valid Sample #", yaxis_title="y_out",
                )
                apply_dark(fig_v, height=340)
                st.plotly_chart(fig_v, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">ARCHITECTURE COMPARISON TABLE</div>',
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
# TAB 8 — VERILOG CODE VIEWER
# ══════════════════════════════════════════════════════════════
with tab_vcode:
    fpath, tpath = find_verilog()

    st.markdown('<div class="section-header">cic_filter.v — RTL SOURCE</div>',
                unsafe_allow_html=True)
    if fpath:
        with open(fpath) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("cic_filter.v not found. Expected location: `./verilog/cic_filter.v`")
        st.markdown("""
> **To display RTL code here:** Place your `cic_filter.v` and `cic_testbench.v`
> in a `verilog/` subfolder alongside this app.
> They will be auto-detected and displayed.
""")

    st.markdown('<div class="section-header">cic_testbench.v — TESTBENCH</div>',
                unsafe_allow_html=True)
    if tpath:
        with open(tpath) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("cic_testbench.v not found. Expected location: `./verilog/cic_testbench.v`")

    st.markdown("---")
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#4a7aaa;
            background:#050e1f;border:1px solid #0d3060;border-radius:6px;padding:14px;">
  📎 GitHub: <a href="https://github.com/shashankchowdary-921/cic_decimation_filter"
               style="color:#3b9eff;">github.com/shashankchowdary-921/cic_decimation_filter</a><br>
  🌐 Live App: <a href="https://cic-decimation-filter.streamlit.app/"
               style="color:#06b6d4;">cic-decimation-filter.streamlit.app</a><br>
  📄 Reference: Hogenauer, E.B. — IEEE Trans. ASSP, vol.29 no.2, Apr 1981
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-family:'Orbitron',monospace;font-size:9px;
            color:#1a4080;letter-spacing:3px;padding:6px 0 2px;">
  CIC DECIMATION FILTER SIMULATOR · TEAM MAVERICKS · 5G/6G RF FRONT-END
  <span style="color:#0d3060;"> · </span>
  SHASHANK · PASYANTH · ABIN · YAGNESH
</div>
""", unsafe_allow_html=True)
