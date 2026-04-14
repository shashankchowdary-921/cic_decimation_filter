# ============================================================
# CIC DECIMATION FILTER — Interactive Simulator
# Team Mavericks | 5G/6G RF Front-End Project
# Dependencies: streamlit, numpy, plotly  (NO matplotlib)
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
    page_title="CIC Decimation Filter",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
  .block-container{padding-top:1.2rem}
  .stTabs [data-baseweb="tab"]{font-size:14px;font-weight:700}
  div[data-testid="metric-container"]{background:#1e1e2e;border-radius:8px;padding:8px 12px}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Filter Parameters")

    architecture = st.selectbox(
        "Architecture",
        ["Pipelined", "Basic", "Folded"],
        help=(
            "Pipelined: pipeline register after every stage (matches your RTL).\n"
            "Basic: standard cascaded integrator-comb, no extra registers.\n"
            "Folded: single shared adder, time-multiplexed N× per sample."
        ),
    )
    st.divider()

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
    fs_label = st.selectbox("Input Sample Rate", list(FS_MAP.keys()), index=4)
    fs_in    = FS_MAP[fs_label]

    R = st.select_slider("Decimation Factor (R)",
                         options=[2, 4, 8, 16, 32, 64, 128, 256], value=4)
    N = st.slider("Number of Stages (N)", 1, 6, 2)
    M = st.select_slider("Differential Delay (M)", options=[1, 2], value=1)

    fs_out = fs_in / R
    if fs_out >= 1e6:
        fs_out_str = f"{fs_out/1e6:.3f} MHz"
    elif fs_out >= 1e3:
        fs_out_str = f"{fs_out/1e3:.2f} kHz"
    else:
        fs_out_str = f"{fs_out:.1f} Hz"

    st.metric("Output Sample Rate", fs_out_str)
    st.divider()

    st.subheader("🎵 Test Signal")
    sig_type  = st.selectbox("Signal Type",
        ["Sine","Ramp","DC","Multi-tone","Chirp","Square","Random Noise"])
    max_f     = max(10, int(fs_out / 3))
    f_sig     = st.slider("Signal Frequency (Hz)", 10, max_f, min(1000, max_f // 4))
    noise_db  = st.slider("Noise Level (dB)", -80, 0, -40)
    n_samples = st.select_slider("Input Samples",
                                 options=[128, 256, 512, 1024, 2048, 4096], value=512)

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
DARK = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
            font=dict(color="#e0e0e0"), margin=dict(t=45, b=20, l=50, r=20))
GRID = dict(gridcolor="#2a2a3e", zerolinecolor="#444")

def apply_dark(fig, height=420):
    fig.update_layout(height=height, **DARK)
    for ax in fig.layout:
        if ax.startswith("xaxis") or ax.startswith("yaxis"):
            fig.layout[ax].update(**GRID)
    return fig

# ──────────────────────────────────────────────────────────────
# PAGE HEADER
# ──────────────────────────────────────────────────────────────
st.title("🔬 CIC Decimation Filter — Interactive Simulator")
st.caption("Team Mavericks | 5G/6G RF Front-End Project")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Architecture",    architecture)
c2.metric("Input Rate",      fs_label)
c3.metric("Output Rate",     fs_out_str)
c4.metric("Bit Growth",      f"+{bit_growth(R,N,M)} bits")
c5.metric("Output Samples",  str(len(y_out)))

# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────
tab_sim, tab_freq, tab_arch, tab_stages, tab_vlog, tab_vcode = st.tabs([
    "🌊 Simulate",
    "📈 Frequency Response",
    "🏗️ Architecture",
    "📊 Stage Analysis",
    "⚡ Verilog Simulation",
    "📄 Verilog Code",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SIMULATE
# ══════════════════════════════════════════════════════════════
with tab_sim:
    st.subheader("Time-Domain & Spectrum")
    disp_in  = min(n_samples, 300)
    disp_out = min(len(y_out), 300)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"Input x[n]  ({fs_label})",
            f"Output y[m]  ({fs_out_str})",
            "Input Spectrum", "Output Spectrum",
        ],
        vertical_spacing=0.20, horizontal_spacing=0.10,
    )
    fig.add_trace(go.Scatter(x=t_in[:disp_in],  y=x_norm[:disp_in],
        mode="lines", line=dict(color="#4FC3F7", width=1.2), name="x[n]"), row=1, col=1)
    y_fnorm = y_out / (np.max(np.abs(y_out))+1e-12)
    fig.add_trace(go.Scatter(x=t_out[:disp_out], y=y_fnorm[:disp_out],
        mode="lines", line=dict(color="#EF9A9A", width=1.4), name="y[m]"), row=1, col=2)

    nfft = 2048
    X  = np.abs(np.fft.rfft(x_norm, n=nfft)) / nfft
    fx = np.fft.rfftfreq(nfft, 1/fs_in) / 1e3
    fig.add_trace(go.Scatter(x=fx, y=20*np.log10(np.maximum(X,1e-10)),
        mode="lines", line=dict(color="#4FC3F7", width=0.9), name="Input PSD"), row=2, col=1)
    Y  = np.abs(np.fft.rfft(y_norm, n=nfft)) / nfft
    fy = np.fft.rfftfreq(nfft, R/fs_in) / 1e3
    fig.add_trace(go.Scatter(x=fy, y=20*np.log10(np.maximum(Y,1e-10)),
        mode="lines", line=dict(color="#EF9A9A", width=0.9), name="Output PSD"), row=2, col=2)

    fig.update_xaxes(title_text="Time (µs)", row=1, col=1)
    fig.update_xaxes(title_text="Time (µs)", row=1, col=2)
    fig.update_xaxes(title_text="Freq (kHz)", range=[0, min(fs_in/2e3,200)], row=2, col=1)
    fig.update_xaxes(title_text="Freq (kHz)", range=[0, fs_out/2e3],         row=2, col=2)
    fig.update_yaxes(title_text="Amplitude", row=1, col=1)
    fig.update_yaxes(title_text="Amplitude", row=1, col=2)
    fig.update_yaxes(title_text="dBFS", range=[-100, 5], row=2, col=1)
    fig.update_yaxes(title_text="dBFS", range=[-100, 5], row=2, col=2)
    apply_dark(fig, height=560)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    snr_in  = snr_calc(x_norm, f_sig, fs_in)
    snr_out = snr_calc(y_norm, f_sig, fs_out)
    s1, s2, s3 = st.columns(3)
    s1.metric("Input SNR",  f"{snr_in:.1f} dB")
    s2.metric("Output SNR", f"{snr_out:.1f} dB")
    s3.metric("SNR Change", f"{snr_out-snr_in:+.1f} dB")

# ══════════════════════════════════════════════════════════════
# TAB 2 — FREQUENCY RESPONSE
# ══════════════════════════════════════════════════════════════
with tab_freq:
    st.subheader("CIC Magnitude Response")
    col_main, col_ctrl = st.columns([4, 1])
    with col_ctrl:
        show_alias = st.checkbox("Alias bands",   value=True)
        show_pb    = st.checkbox("Passband edge", value=True)
        f_lim      = st.slider("Display (MHz)", 0.1, max(0.2, fs_in/2e6),
                               min(fs_in/2e6, 8.0), step=0.1)
        y_min_db   = st.slider("Y min (dB)", -160, -20, -120)
    with col_main:
        mask = f_ax <= f_lim*1e6
        fig_fr = go.Figure()
        fig_fr.add_trace(go.Scatter(x=f_ax[mask]/1e6, y=H_db[mask],
            mode="lines", line=dict(color="#42A5F5", width=2), name="|H(f)|"))
        if show_alias:
            for k in range(1, 6):
                fa = k * fs_out
                if fa < f_lim*1e6:
                    fig_fr.add_vline(x=fa/1e6, line=dict(color="red", dash="dot", width=1),
                        annotation_text=f"Alias {k}", annotation_font_size=9)
        if show_pb:
            fig_fr.add_vline(x=0.4*fs_out/1e6, line=dict(color="#66BB6A", dash="dash", width=1.5),
                annotation_text="PB edge", annotation_font_size=9)
        fig_fr.add_hline(y=-3, line=dict(color="orange", dash="dash", width=1),
                         annotation_text="-3dB", annotation_font_size=8)
        fig_fr.add_hline(y=-6, line=dict(color="#AB47BC", dash="dash", width=1))
        fig_fr.update_layout(
            title=f"CIC Response  [N={N}, R={R}, M={M}, Fs={fs_in/1e6:.1f} MHz]",
            xaxis_title="Frequency (MHz)", yaxis_title="Magnitude (dB)",
            xaxis_range=[0, f_lim], yaxis_range=[y_min_db, 5],
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        apply_dark(fig_fr)
        st.plotly_chart(fig_fr, use_container_width=True)

    st.subheader("Passband Detail")
    pb_mask = f_ax <= 0.5*fs_out
    fig_pb  = go.Figure(go.Scatter(x=f_ax[pb_mask]/1e3, y=H_db[pb_mask],
        mode="lines", line=dict(color="#42A5F5", width=2)))
    fig_pb.add_hline(y=-3, line=dict(color="orange", dash="dash"))
    fig_pb.update_layout(xaxis_title="Frequency (kHz)", yaxis_title="dB",
                         title="Passband Droop (0 → Fs_out/2)")
    apply_dark(fig_pb, height=300)
    st.plotly_chart(fig_pb, use_container_width=True)

    with st.expander("📋 Attenuation Table"):
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
    st.subheader(f"Block Diagram — {architecture}  (N={N}, R={R}, M={M})")

    fig_bd = go.Figure()
    fig_bd.update_layout(
        xaxis=dict(range=[-0.5,14], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1.5, 3], showgrid=False, zeroline=False, visible=False),
        height=260, margin=dict(l=5,r=5,t=40,b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
    )

    def add_box(fig, cx, cy, label, ec, fc_a=0.18):
        import re as _re
        rgb = _re.findall(r'\d+', ec)
        r2,g2,b2 = (int(x) for x in rgb[:3])
        fig.add_shape(type="rect",
            x0=cx-0.48, x1=cx+0.48, y0=cy-0.32, y1=cy+0.32,
            line=dict(color=ec, width=2),
            fillcolor=f"rgba({r2},{g2},{b2},{fc_a})")
        fig.add_annotation(x=cx, y=cy, text=label, showarrow=False,
            font=dict(size=10, color="#ffffff"), align="center")

    def arr(fig, x0, x1, y=1.0):
        fig.add_annotation(x=x1, y=y, ax=x0, ay=y,
            axref="x", ayref="y", xref="x", yref="y",
            arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#888888")

    C_INT  = "rgb(66,165,250)"
    C_DS   = "rgb(255,112,67)"
    C_COMB = "rgb(102,187,106)"
    C_FF   = "rgb(171,71,188)"
    C_IN   = "rgb(120,200,255)"

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
                         line=dict(color="#555", dash="dash"))
        fig_bd.add_annotation(x=ds_x-1.5, y=0.25, text="← Fs_in →",
                               showarrow=False, font=dict(size=9,color="#aaa"))
        fig_bd.add_annotation(x=ds_x+1.5, y=0.25, text="← Fs_out →",
                               showarrow=False, font=dict(size=9,color="#aaa"))
        if architecture == "Folded":
            fig_bd.add_annotation(x=pos[N//2+1], y=2.4,
                text=f"⚡ 1 Shared Adder  ×{N} time-mux  |  Internal clk = {N}× Fs_in",
                showarrow=False, font=dict(size=11, color="#FF8A65"),
                bgcolor="rgba(255,87,34,0.12)", bordercolor="#FF8A65", borderwidth=1)
    else:  # Pipelined
        pos  = [0.5]
        lbls = ["x[n]"]
        cols = [C_IN]
        for i in range(N):
            bx = 1.5 + i*2.3
            pos  += [bx, bx+0.9]
            lbls += [f"Σ{i+1}", "FF"]
            cols += [C_INT, C_FF]
        ds_x = pos[-1] + 0.95
        pos  += [ds_x]
        lbls += [f"↓{R}"]
        cols += [C_DS]
        for i in range(N):
            bx = ds_x + 1.2 + i*2.3
            pos  += [bx, bx+0.9]
            lbls += [f"D{i+1}", "FF"]
            cols += [C_COMB, C_FF]
        for px, lb, cl in zip(pos, lbls, cols):
            add_box(fig_bd, px, 1.0, lb, cl)
        for i in range(len(pos)-1):
            arr(fig_bd, pos[i]+0.48, pos[i+1]-0.48)
        mid = pos[len(pos)//2]
        fig_bd.add_annotation(x=mid, y=2.45,
            text=f"Pipeline depth = {2*N} FFs  |  Latency = {2*N} clocks  |  Throughput = 1 samp/clk",
            showarrow=False, font=dict(size=11, color="#CE93D8"),
            bgcolor="rgba(156,39,176,0.12)", bordercolor="#9C27B0", borderwidth=1)

    st.plotly_chart(fig_bd, use_container_width=True)

    desc = {
        "Basic": (
            "**Basic CIC:** N integrators run at Fs_in. "
            "After ↓R downsampling, N comb (differencer) sections run at Fs_out. "
            "No pipeline registers — minimal hardware, but critical path spans all N adders."
        ),
        "Pipelined": (
            f"**Pipelined CIC (matches your RTL `cic_filter.v`):** "
            f"A D flip-flop (FF) register after every integrator and every comb stage creates a "
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

    with st.expander("📐 Transfer Function & Key Equations"):
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
    st.subheader("Per-Stage Output  (first 200 samples, normalised)")

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

    COLORS = ["#4FC3F7","#42A5F5","#1E88E5","#1565C0",
              "#FF8A65","#EF5350","#66BB6A","#43A047","#2E7D32",
              "#CE93D8","#AB47BC","#7E57C2"]

    cols_per_row = 2
    for row_start in range(0, len(y_stages), cols_per_row):
        cols = st.columns(cols_per_row)
        for ci, si in enumerate(range(row_start, min(row_start+cols_per_row, len(y_stages)))):
            s   = y_stages[si]
            lbl = stage_labels[si]
            col = COLORS[si % len(COLORS)]
            d   = min(200, len(s))
            with cols[ci]:
                fig_s = go.Figure(go.Scatter(
                    y=s[:d]/(np.max(np.abs(s[:d]))+1e-12),
                    mode="lines", line=dict(color=col, width=1.2),
                ))
                fig_s.update_layout(
                    title=lbl, height=200,
                    margin=dict(l=10,r=10,t=35,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
                    font=dict(color="#e0e0e0", size=10),
                    xaxis=dict(gridcolor="#2a2a3e", showticklabels=False),
                    yaxis=dict(gridcolor="#2a2a3e"),
                    showlegend=False,
                )
                st.plotly_chart(fig_s, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — VERILOG SIMULATION
# ══════════════════════════════════════════════════════════════
with tab_vlog:
    st.subheader("⚡ Run Actual Verilog Simulation (iverilog)")

    c1, c2, c3 = st.columns(3)
    with c1:
        sim_r = st.selectbox("R for simulation", [2, 4, 8, 16], index=1)
    with c2:
        sim_n = st.selectbox("N for simulation", [1, 2, 3, 4], index=1)
    with c3:
        run_btn = st.button("▶ Run Simulation", type="primary")

    if run_btn:
        with st.spinner("Compiling & simulating..."):
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
                    line=dict(color="#66BB6A", width=2),
                    marker=dict(size=6),
                ))
                fig_v.update_layout(
                    title=f"RTL Output — valid_out samples  [R={sim_r}, N={sim_n}]",
                    xaxis_title="Valid Sample #", yaxis_title="y_out",
                )
                apply_dark(fig_v, height=340)
                st.plotly_chart(fig_v, use_container_width=True)

    st.divider()
    st.subheader("Architecture Comparison")
    bg = bit_growth(R, N, M)
    st.markdown(f"""
| Metric | Basic | Pipelined | Folded |
|--------|-------|-----------|--------|
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

    st.subheader("Bit Growth vs R (all N values)")
    R_vals = [2, 4, 8, 16, 32, 64, 128, 256]
    fig_bg = go.Figure()
    for n_v in range(1, 7):
        fig_bg.add_trace(go.Scatter(
            x=R_vals, y=[bit_growth(r, n_v, M) for r in R_vals],
            mode="lines+markers", name=f"N={n_v}", line=dict(width=1.8),
        ))
    fig_bg.update_layout(
        xaxis_title="R", yaxis_title="Bit Growth",
        xaxis_type="log", title=f"Bit Growth = N·⌈log₂(R·M)⌉  [M={M}]",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(tickvals=R_vals, ticktext=[str(r) for r in R_vals]),
    )
    apply_dark(fig_bg, height=340)
    st.plotly_chart(fig_bg, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — VERILOG CODE VIEWER
# ══════════════════════════════════════════════════════════════
with tab_vcode:
    fpath, tpath = find_verilog()

    st.subheader("📄 cic_filter.v  — RTL Source")
    if fpath:
        with open(fpath) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("cic_filter.v not found. Expected location: `./verilog/cic_filter.v`")

    st.subheader("📄 cic_testbench.v  — Testbench")
    if tpath:
        with open(tpath) as f:
            st.code(f.read(), language="verilog")
    else:
        st.warning("cic_testbench.v not found. Expected location: `./verilog/cic_testbench.v`")

# ──────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "CIC Decimation Filter Visualizer — Team Mavericks | "
    "Architectures: Basic · Pipelined · Folded | "
    "Input rates: 500 kHz – 500 MHz | R: 2–256 | N: 1–6 | M: 1–2"
)
