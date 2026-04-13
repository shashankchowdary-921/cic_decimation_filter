import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd
from scipy.signal import firwin, lfilter

# ──────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CIC Decimation Filter Visualizer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; }
    .metric-box {
        background: #f0f2f6; border-radius: 8px;
        padding: 10px 14px; margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Filter Parameters")

    architecture = st.selectbox(
        "Architecture",
        ["Basic", "Pipelined", "Folded"],
        help=(
            "Basic: Standard cascaded integrator–comb.\n"
            "Pipelined: Pipeline registers between every stage for max throughput.\n"
            "Folded: Time-multiplexed – one adder reused N times per sample."
        ),
    )

    st.divider()

    FS_OPTIONS = {
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
        "120 MHz":120_000_000,
        "128 MHz":128_000_000,
        "160 MHz":160_000_000,
        "192 MHz":192_000_000,
        "200 MHz":200_000_000,
        "240 MHz":240_000_000,
        "256 MHz":256_000_000,
        "320 MHz":320_000_000,
        "400 MHz":400_000_000,
        "500 MHz":500_000_000,
    }
    fs_label = st.selectbox("Input Sample Rate (Fs_in)", list(FS_OPTIONS.keys()), index=4)
    fs_in = FS_OPTIONS[fs_label]

    R = st.select_slider(
        "Decimation Factor (R)",
        options=[2, 4, 8, 16, 32, 64, 128, 256],
        value=8,
    )
    N = st.slider("Number of Stages (N)", min_value=1, max_value=6, value=3)
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

    SIG_TYPES = ["Sine", "Multi-tone", "Chirp", "Noise + Sine", "Square Wave"]
    signal_type = st.selectbox("Signal Type", SIG_TYPES)

    max_sig_f = max(100, int(fs_out / 3))
    f_sig = st.slider(
        "Signal Frequency (Hz)",
        min_value=10,
        max_value=max_sig_f,
        value=min(1000, max_sig_f // 4),
    )
    noise_db = st.slider("Noise Level (dB)", min_value=-80, max_value=0, value=-30)
    n_samples = st.select_slider(
        "Input Samples",
        options=[256, 512, 1024, 2048, 4096, 8192],
        value=1024,
    )

# ──────────────────────────────────────────────────────────────────
# CORE MATH
# ──────────────────────────────────────────────────────────────────

def cic_basic(x: np.ndarray, R: int, N: int, M: int = 1) -> np.ndarray:
    """Standard CIC decimation: N integrators → ↓R → N combs."""
    y = x.astype(np.float64)
    for _ in range(N):
        y = np.cumsum(y)
    y = y[::R]
    for _ in range(N):
        y = np.diff(y, M, prepend=np.zeros(M))
    return y


def cic_pipelined(x: np.ndarray, R: int, N: int, M: int = 1):
    """
    Pipelined CIC: each integrator stage has an output register (1-cycle delay).
    The filter output is mathematically identical to Basic but each stage is
    separated by a flip-flop register, enabling maximum clock speed.
    Returns (output, pipeline_stages, latency_cycles).
    """
    y = x.astype(np.float64)
    stage_outputs = []          # capture output of every registered stage
    for stage in range(N):
        y = np.cumsum(y)
        # Model pipeline register: shift by 1 sample (zero-pad start)
        y_reg = np.roll(y, 1)
        y_reg[0] = 0.0
        stage_outputs.append(y_reg.copy())

    y = stage_outputs[-1]       # output of last integrator pipeline register
    y = y[::R]                  # down-sample

    for stage in range(N):
        y = np.diff(y, M, prepend=np.zeros(M))
        y_reg = np.roll(y, 1)
        y_reg[0] = 0.0
        stage_outputs.append(y_reg.copy())

    latency_cycles = 2 * N      # N integrator regs + N comb regs
    return stage_outputs[-1], stage_outputs, latency_cycles


def cic_folded(x: np.ndarray, R: int, N: int, M: int = 1):
    """
    Folded (time-multiplexed) CIC.
    A single adder is reused N times per input clock cycle, requiring an
    internal clock N× faster than the input rate.
    Returns (output, utilisation_info).
    """
    # Functionally equivalent to Basic; architecture differs in hardware
    y = x.astype(np.float64)
    for _ in range(N):
        y = np.cumsum(y)
    y = y[::R]
    for _ in range(N):
        y = np.diff(y, M, prepend=np.zeros(M))

    # Hardware resource info
    info = {
        "adders_used":    1,
        "adders_basic":   2 * N,          # N integrators + N combs in basic
        "registers_used": N + 1,          # feedback register per stage + state
        "multiplexer_count": N - 1,
        "internal_clock_mult": N,         # internal clock = N × fs_in
    }
    return y, info


def cic_frequency_response(R: int, N: int, M: int, fs_in: float, npts: int = 8192):
    """
    Theoretical CIC magnitude response (dB) up to fs_in/2.
    H(f) = [sin(π·M·R·f/fs) / sin(π·f/fs)]^N  (normalised to 0 dB at DC)
    """
    f = np.linspace(0, fs_in / 2, npts)
    with np.errstate(divide="ignore", invalid="ignore"):
        num = np.sin(np.pi * M * R * f / fs_in)
        den = np.sin(np.pi * f / fs_in)
        ratio = np.where(np.abs(den) < 1e-12, float(M * R), np.abs(num / den))
    H_mag = (ratio / (M * R)) ** N
    H_db = 20 * np.log10(np.maximum(H_mag, 1e-12))
    return f, H_db


def bit_growth(R: int, N: int, M: int = 1) -> int:
    """Maximum bit-growth: B_out = B_in + N·ceil(log2(R·M))"""
    return N * int(np.ceil(np.log2(R * M)))


def generate_signal(sig_type: str, n: int, fs: float, f0: float, noise_db: float) -> np.ndarray:
    t = np.arange(n) / fs
    noise_amp = 10 ** (noise_db / 20)
    noise = noise_amp * np.random.randn(n)

    if sig_type == "Sine":
        s = np.sin(2 * np.pi * f0 * t)
    elif sig_type == "Multi-tone":
        s = (
            np.sin(2 * np.pi * f0 * t) +
            0.5 * np.sin(2 * np.pi * f0 * 3 * t) +
            0.3 * np.sin(2 * np.pi * f0 * 7 * t)
        )
        s /= np.max(np.abs(s) + 1e-12)
    elif sig_type == "Chirp":
        f_end = min(f0 * 10, fs / 2.5)
        s = np.sin(2 * np.pi * (f0 + (f_end - f0) * t / (n / fs)) * t)
    elif sig_type == "Noise + Sine":
        s = np.sin(2 * np.pi * f0 * t) + noise
        return s
    elif sig_type == "Square Wave":
        s = np.sign(np.sin(2 * np.pi * f0 * t))
    else:
        s = np.sin(2 * np.pi * f0 * t)

    return s + noise


def compute_snr(y: np.ndarray, f0: float, fs: float) -> float:
    Y = np.abs(np.fft.rfft(y, n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, 1 / fs)
    idx = np.argmin(np.abs(freqs - f0))
    signal_power = Y[max(0, idx - 2) : idx + 3].sum()
    noise_power = Y.sum() - signal_power
    if noise_power <= 0:
        return np.inf
    return 10 * np.log10(signal_power / noise_power)


# ──────────────────────────────────────────────────────────────────
# BLOCK DIAGRAM HELPERS
# ──────────────────────────────────────────────────────────────────

def _box(ax, x, y, w, h, label, color="#4C72B0", fc=None, fontsize=9):
    fc = fc or color + "33"
    rect = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.05", linewidth=1.5,
        edgecolor=color, facecolor=fc
    )
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color="#1a1a2e")


def _arrow(ax, x0, y0, x1, y1, color="#333"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5))


def draw_basic_diagram(ax, N):
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-1, 2)
    ax.axis("off")
    ax.set_title(f"Basic CIC  (N={N} stages)", fontsize=11, fontweight="bold")

    # Input
    ax.text(0.2, 0.5, "x[n]\nFs_in", ha="center", va="center", fontsize=8)
    _arrow(ax, 0.6, 0.5, 1.0, 0.5)

    # N integrators
    integ_x = [1.5 + i * 1.2 for i in range(N)]
    for i, x in enumerate(integ_x):
        _box(ax, x, 0.5, 0.9, 0.6, f"∑\n(Integ {i+1})", "#2196F3")
        if i > 0:
            _arrow(ax, integ_x[i-1] + 0.45, 0.5, x - 0.45, 0.5)

    # Downsampler
    ds_x = integ_x[-1] + 1.2
    _box(ax, ds_x, 0.5, 0.9, 0.6, f"↓R\n(R={R})", "#FF5722")
    _arrow(ax, integ_x[-1] + 0.45, 0.5, ds_x - 0.45, 0.5)

    # N combs
    comb_x = [ds_x + 1.2 + i * 1.2 for i in range(N)]
    for i, x in enumerate(comb_x):
        _box(ax, x, 0.5, 0.9, 0.6, f"D\n(Comb {i+1})", "#4CAF50")
        if i == 0:
            _arrow(ax, ds_x + 0.45, 0.5, x - 0.45, 0.5)
        else:
            _arrow(ax, comb_x[i-1] + 0.45, 0.5, x - 0.45, 0.5)

    ax.text(comb_x[-1] + 0.7, 0.5, "y[m]\nFs_out", ha="center", va="center", fontsize=8)
    _arrow(ax, comb_x[-1] + 0.45, 0.5, comb_x[-1] + 0.65, 0.5)

    # Rate label
    ax.axvline(ds_x, color="gray", linestyle="--", alpha=0.5)
    ax.text(ds_x - 1.5, -0.5, "High Rate (Fs_in)", ha="center", fontsize=7, color="gray")
    ax.text(ds_x + 1.5, -0.5, "Low Rate (Fs_in/R)", ha="center", fontsize=7, color="gray")


def draw_pipelined_diagram(ax, N):
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-1.5, 3)
    ax.axis("off")
    ax.set_title(f"Pipelined CIC  (N={N}  — pipeline registers between every stage)",
                 fontsize=11, fontweight="bold")

    ax.text(0.2, 1.0, "x[n]\nFs_in", ha="center", va="center", fontsize=8)
    _arrow(ax, 0.55, 1.0, 0.95, 1.0)

    integ_x = [1.5 + i * 2.0 for i in range(N)]
    for i, x in enumerate(integ_x):
        _box(ax, x, 1.0, 0.9, 0.6, f"Integ\n{i+1}", "#2196F3")
        # Pipeline register
        _box(ax, x + 0.9, 1.0, 0.5, 0.55, "FF", "#9C27B0")
        _arrow(ax, x + 0.45, 1.0, x + 0.65, 1.0)
        if i > 0:
            _arrow(ax, integ_x[i-1] + 1.15, 1.0, x - 0.45, 1.0)

    ds_x = integ_x[-1] + 1.8
    _box(ax, ds_x, 1.0, 0.9, 0.6, f"↓R\nR={R}", "#FF5722")
    _arrow(ax, integ_x[-1] + 1.15, 1.0, ds_x - 0.45, 1.0)

    comb_x = [ds_x + 1.5 + i * 2.0 for i in range(N)]
    for i, x in enumerate(comb_x):
        _box(ax, x, 1.0, 0.9, 0.6, f"Comb\n{i+1}", "#4CAF50")
        _box(ax, x + 0.9, 1.0, 0.5, 0.55, "FF", "#9C27B0")
        _arrow(ax, x + 0.45, 1.0, x + 0.65, 1.0)
        if i == 0:
            _arrow(ax, ds_x + 0.45, 1.0, x - 0.45, 1.0)
        else:
            _arrow(ax, comb_x[i-1] + 1.15, 1.0, x - 0.45, 1.0)

    ax.text(comb_x[-1] + 1.1, 1.0, "y[m]", ha="center", va="center", fontsize=8)

    # Legend
    ax.add_patch(FancyBboxPatch((0.1, -1.2), 0.5, 0.4, boxstyle="round", ec="#2196F3", fc="#2196F333", lw=1.2))
    ax.text(0.7, -1.0, "Integrator", fontsize=7)
    ax.add_patch(FancyBboxPatch((2.0, -1.2), 0.5, 0.4, boxstyle="round", ec="#4CAF50", fc="#4CAF5033", lw=1.2))
    ax.text(2.6, -1.0, "Comb", fontsize=7)
    ax.add_patch(FancyBboxPatch((3.8, -1.2), 0.5, 0.4, boxstyle="round", ec="#9C27B0", fc="#9C27B033", lw=1.2))
    ax.text(4.4, -1.0, "Pipeline Register (FF)", fontsize=7)


def draw_folded_diagram(ax, N):
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-2, 3.5)
    ax.axis("off")
    ax.set_title(f"Folded (Time-Multiplexed) CIC  (N={N}  — one adder reused N×)",
                 fontsize=11, fontweight="bold")

    # Single adder in the middle
    _box(ax, 3.5, 1.5, 1.2, 0.7, "Shared\nAdder ×1", "#FF9800", fc="#FF980033")

    # Feedback/accumulator registers (N of them)
    for i in range(N):
        y_pos = 0.0 - i * 0.7
        _box(ax, 6.0, y_pos, 1.0, 0.5, f"Reg_{i+1}", "#9C27B0", fc="#9C27B033", fontsize=8)
        ax.annotate("", xy=(3.5, 1.15), xytext=(6.0, y_pos + 0.25),
                    arrowprops=dict(arrowstyle="->", color="#9C27B0",
                                   connectionstyle="arc3,rad=0.3", lw=1.2))
        ax.annotate("", xy=(6.0, y_pos + 0.25), xytext=(3.5, 1.15),
                    arrowprops=dict(arrowstyle="->", color="#2196F3",
                                   connectionstyle="arc3,rad=-0.3", lw=1.2))

    # Mux
    _box(ax, 1.5, 1.5, 0.8, 0.6, f"MUX\n(1:{N})", "#607D8B", fc="#607D8B33")
    _arrow(ax, 1.9, 1.5, 2.9, 1.5)
    ax.text(0.4, 1.5, "x[n]\nFs_in", ha="center", fontsize=8)
    _arrow(ax, 0.8, 1.5, 1.1, 1.5)

    # Counter/Control
    _box(ax, 3.5, -0.8, 1.2, 0.5, f"Counter\nmod {N}", "#795548", fc="#79554833", fontsize=8)
    ax.annotate("", xy=(1.5, 1.2), xytext=(3.5, -0.55),
                arrowprops=dict(arrowstyle="->", color="#795548", lw=1.2,
                                connectionstyle="arc3,rad=0.2"))

    # Downsampler
    _box(ax, 8.5, 1.5, 0.9, 0.6, f"↓R\nR={R}", "#FF5722")
    _arrow(ax, 6.5, 0.0, 7.5, 1.5)
    ax.text(7.5, 1.5, "→", fontsize=12)

    # N comb stages (folded similarly)
    _box(ax, 8.5, 0.3, 1.2, 0.6, "Shared\nComb ×1", "#4CAF50", fc="#4CAF5033")
    _arrow(ax, 8.5, 1.2, 8.5, 0.6)

    ax.text(9.8, 0.3, "y[m]\nFs_out", ha="center", fontsize=8)
    _arrow(ax, 9.1, 0.3, 9.6, 0.3)

    # Internal clock annotation
    ax.text(3.5, 3.2,
            f"⚡ Internal clock = {N}× Fs_in  |  Adder utilisation = 100%",
            ha="center", fontsize=8, color="#E91E63",
            bbox=dict(boxstyle="round", fc="#FCE4EC", ec="#E91E63", lw=1))


# ──────────────────────────────────────────────────────────────────
# GENERATE SIGNAL + RUN FILTER
# ──────────────────────────────────────────────────────────────────
np.random.seed(42)
x_in = generate_signal(signal_type, n_samples, fs_in, f_sig, noise_db)

if architecture == "Basic":
    y_out = cic_basic(x_in, R, N, M)
    pipeline_latency = 0
    folded_info = None
elif architecture == "Pipelined":
    y_out, stage_outs, pipeline_latency = cic_pipelined(x_in, R, N, M)
    folded_info = None
else:  # Folded
    y_out, folded_info = cic_folded(x_in, R, N, M)
    pipeline_latency = 0

# Trim y_out edges (ramp artefact)
guard = min(N * M, len(y_out) // 4)
y_plot = y_out[guard:]
y_plot = y_plot / (np.max(np.abs(y_plot)) + 1e-12)

x_norm = x_in / (np.max(np.abs(x_in)) + 1e-12)
t_in = np.arange(len(x_in)) / fs_in * 1e6   # µs
t_out = np.arange(len(y_out)) * R / fs_in * 1e6

f_in_axis, H_db = cic_frequency_response(R, N, M, fs_in)

# ──────────────────────────────────────────────────────────────────
# MAIN TITLE
# ──────────────────────────────────────────────────────────────────
st.title("🔬 CIC Decimation Filter Visualizer")
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Architecture", architecture)
col_b.metric("Input Rate",   fs_label)
col_c.metric("Output Rate",  fs_out_str)
col_d.metric("Bit Growth",   f"+{bit_growth(R, N, M)} bits")

# ──────────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏗️ Architecture",
    "📈 Frequency Response",
    "🌊 Signal Simulation",
    "📊 Stage Analysis",
    "⚡ Performance Table",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 – ARCHITECTURE BLOCK DIAGRAM
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f"Block Diagram — {architecture} CIC  (N={N}, R={R}, M={M})")

    fig_arch, ax_arch = plt.subplots(figsize=(14, 4))
    fig_arch.patch.set_alpha(0)
    ax_arch.set_facecolor("none")

    if architecture == "Basic":
        draw_basic_diagram(ax_arch, N)
    elif architecture == "Pipelined":
        draw_pipelined_diagram(ax_arch, N)
    else:
        draw_folded_diagram(ax_arch, N)

    st.pyplot(fig_arch, use_container_width=True)
    plt.close(fig_arch)

    # Description card
    desc = {
        "Basic": (
            "**How it works:** All N integrators run at Fs_in; after down-sampling by R, "
            "N comb sections (each a differencer of delay M) run at Fs_out = Fs_in/R.  "
            "No pipeline registers → minimal hardware, but the critical path spans all N integrators."
        ),
        "Pipelined": (
            "**How it works:** A D flip-flop (FF) is inserted after every integrator and comb stage.  "
            f"This creates a **{2*N}-stage deep pipeline**, allowing the clock to run as fast as a "
            "single-stage delay allows.  Latency increases by 2N cycles but throughput = 1 sample/clock.  "
            "Ideal for high-speed FPGA/ASIC implementations."
        ),
        "Folded": (
            "**How it works:** Instead of N separate adder units, a **single shared adder** is "
            f"time-multiplexed N times per input sample, with an internal clock running {N}× Fs_in.  "
            "State is stored in N small registers.  Area is reduced by ~(2N−1) adders; "
            "throughput is 1 output per R input clocks — same as Basic."
        ),
    }
    st.info(desc[architecture])

    with st.expander("📐 Transfer Function & Key Equations"):
        st.latex(r"H(z) = \left(\frac{1 - z^{-RM}}{1 - z^{-1}}\right)^N")
        st.latex(
            r"|H(f)| = \left|\frac{\sin(\pi M R f/F_s)}{\sin(\pi f/F_s)}\right|^N"
            r"\quad \text{(normalised to 1 at DC)}"
        )
        st.markdown(f"""
| Parameter | Value |
|-----------|-------|
| N (stages) | {N} |
| R (decimation) | {R} |
| M (diff. delay) | {M} |
| Fs_in | {fs_in/1e6:.3f} MHz |
| Fs_out | {fs_out_str} |
| Passband edge | ≈ {0.5*fs_out/1e3:.2f} kHz |
| DC gain (linear) | {(R*M)**N:.0f} |
| Bit growth | +{bit_growth(R,N,M)} bits |
| Pipeline latency | {pipeline_latency} cycles |
""")

# ══════════════════════════════════════════════════════════════════
# TAB 2 – FREQUENCY RESPONSE
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Magnitude Response")
    col1, col2 = st.columns([3, 1])

    with col2:
        show_alias_bands = st.checkbox("Show alias bands", value=True)
        show_pass_edge   = st.checkbox("Show passband edge", value=True)
        f_limit_mhz      = st.slider(
            "Freq display limit (MHz)",
            0.1, max(0.1, fs_in / 2e6),
            min(fs_in / 2e6, 10.0),
            step=0.1,
        )
        y_min_db = st.slider("Y-axis min (dB)", -160, -20, -120)

    with col1:
        fig_fr, ax_fr = plt.subplots(figsize=(10, 5))
        mask = f_in_axis <= f_limit_mhz * 1e6
        ax_fr.plot(f_in_axis[mask] / 1e6, H_db[mask], color="#1565C0", linewidth=2, label="CIC Response")

        if show_alias_bands:
            for k in range(1, 6):
                f_alias = k * fs_out
                if f_alias < f_limit_mhz * 1e6:
                    ax_fr.axvline(f_alias / 1e6, color="red", linestyle=":", alpha=0.5,
                                  label=f"Alias band {k}" if k == 1 else "")
                    ax_fr.axvspan(f_alias / 1e6 - fs_out / 2e6,
                                  f_alias / 1e6 + fs_out / 2e6,
                                  alpha=0.05, color="red")

        if show_pass_edge:
            f_pass = 0.4 * fs_out
            ax_fr.axvline(f_pass / 1e6, color="green", linestyle="--", linewidth=1.5,
                          label=f"Passband edge ≈ {f_pass/1e3:.1f} kHz")

        ax_fr.axhline(-3, color="orange", linestyle="--", linewidth=1, alpha=0.7, label="−3 dB")
        ax_fr.axhline(-6, color="purple", linestyle="--", linewidth=1, alpha=0.5, label="−6 dB")
        ax_fr.set_xlabel("Frequency (MHz)", fontsize=11)
        ax_fr.set_ylabel("Magnitude (dB)", fontsize=11)
        ax_fr.set_ylim(y_min_db, 5)
        ax_fr.set_xlim(0, f_limit_mhz)
        ax_fr.set_title(
            f"CIC Frequency Response  [N={N}, R={R}, M={M}, Fs={fs_in/1e6:.1f} MHz]",
            fontsize=12
        )
        ax_fr.legend(fontsize=8, loc="lower left")
        ax_fr.grid(True, alpha=0.3)
        ax_fr.set_facecolor("#fafafa")
        st.pyplot(fig_fr, use_container_width=True)
        plt.close(fig_fr)

    # Passband droop
    st.subheader("Passband Detail")
    fig_pb, ax_pb = plt.subplots(figsize=(10, 3.5))
    pb_mask = f_in_axis <= 0.5 * fs_out
    ax_pb.plot(f_in_axis[pb_mask] / 1e3, H_db[pb_mask], color="#1565C0", linewidth=2)
    ax_pb.axhline(-3, color="orange", linestyle="--", linewidth=1, alpha=0.8, label="−3 dB")
    ax_pb.set_xlabel("Frequency (kHz)", fontsize=10)
    ax_pb.set_ylabel("Magnitude (dB)", fontsize=10)
    ax_pb.set_title("Passband Droop (0 → Fs_out/2)", fontsize=11)
    ax_pb.grid(True, alpha=0.3)
    ax_pb.legend()
    ax_pb.set_facecolor("#fafafa")
    st.pyplot(fig_pb, use_container_width=True)
    plt.close(fig_pb)

    # Attenuation at Nyquist & first alias
    with st.expander("📋 Attenuation Table"):
        freqs_check = [
            ("Passband edge (0.4·Fs_out)", 0.4 * fs_out),
            ("Nyquist (0.5·Fs_out)",       0.5 * fs_out),
            ("First alias centre (Fs_out)", 1.0 * fs_out),
            ("2nd alias (2·Fs_out)",        2.0 * fs_out),
            ("3rd alias (3·Fs_out)",        3.0 * fs_out),
        ]
        rows = []
        for name, f_check in freqs_check:
            if f_check < fs_in / 2:
                idx = np.argmin(np.abs(f_in_axis - f_check))
                rows.append({"Frequency": name, "Value (kHz)": f"{f_check/1e3:.2f}", "Attenuation (dB)": f"{H_db[idx]:.1f}"})
        st.table(pd.DataFrame(rows))

# ══════════════════════════════════════════════════════════════════
# TAB 3 – SIGNAL SIMULATION
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Time-Domain Signal Simulation")

    disp_in  = min(n_samples, 256)
    disp_out = min(len(y_out), 256)

    fig_sig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(2, 2, hspace=0.45, wspace=0.35)

    # ── Input time ──────────────────────────────────────────────
    ax_ti = fig_sig.add_subplot(gs[0, 0])
    ax_ti.plot(t_in[:disp_in], x_norm[:disp_in], color="#1565C0", linewidth=0.9)
    ax_ti.set_title(f"Input  x[n]   ({fs_label})", fontsize=10)
    ax_ti.set_xlabel("Time (µs)"); ax_ti.set_ylabel("Amplitude (norm)")
    ax_ti.grid(True, alpha=0.3)

    # ── Output time ─────────────────────────────────────────────
    ax_to = fig_sig.add_subplot(gs[0, 1])
    y_norm = y_out / (np.max(np.abs(y_out)) + 1e-12)
    ax_to.plot(t_out[:disp_out], y_norm[:disp_out], color="#C62828", linewidth=1.1)
    ax_to.set_title(f"Output  y[m]   ({fs_out_str})", fontsize=10)
    ax_to.set_xlabel("Time (µs)"); ax_to.set_ylabel("Amplitude (norm)")
    ax_to.grid(True, alpha=0.3)

    # ── Input spectrum ───────────────────────────────────────────
    ax_si = fig_sig.add_subplot(gs[1, 0])
    nfft = 2048
    X = np.abs(np.fft.rfft(x_norm, n=nfft)) / nfft
    freqs_x = np.fft.rfftfreq(nfft, 1 / fs_in)
    X_db = 20 * np.log10(np.maximum(X, 1e-10))
    ax_si.plot(freqs_x / 1e3, X_db, color="#1565C0", linewidth=0.8)
    ax_si.set_title("Input Spectrum", fontsize=10)
    ax_si.set_xlabel("Frequency (kHz)"); ax_si.set_ylabel("dBFS")
    ax_si.set_xlim(0, min(fs_in / 2e3, 200))
    ax_si.set_ylim(-100, 5)
    ax_si.grid(True, alpha=0.3)

    # ── Output spectrum ──────────────────────────────────────────
    ax_so = fig_sig.add_subplot(gs[1, 1])
    Y = np.abs(np.fft.rfft(y_norm, n=nfft)) / nfft
    freqs_y = np.fft.rfftfreq(nfft, R / fs_in)
    Y_db = 20 * np.log10(np.maximum(Y, 1e-10))
    ax_so.plot(freqs_y / 1e3, Y_db, color="#C62828", linewidth=0.8)
    ax_so.set_title("Output Spectrum", fontsize=10)
    ax_so.set_xlabel("Frequency (kHz)"); ax_so.set_ylabel("dBFS")
    ax_so.set_xlim(0, fs_out / 2e3)
    ax_so.set_ylim(-100, 5)
    ax_so.grid(True, alpha=0.3)

    st.pyplot(fig_sig, use_container_width=True)
    plt.close(fig_sig)

    # SNR
    snr_in  = compute_snr(x_norm, f_sig, fs_in)
    snr_out = compute_snr(y_norm[guard:], f_sig, fs_out)
    c1, c2, c3 = st.columns(3)
    c1.metric("Input SNR",  f"{snr_in:.1f} dB")
    c2.metric("Output SNR", f"{snr_out:.1f} dB")
    c3.metric("SNR Change", f"{snr_out - snr_in:+.1f} dB")

# ══════════════════════════════════════════════════════════════════
# TAB 4 – STAGE ANALYSIS (Pipelined only shows register detail)
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Per-Stage Output Analysis")

    if architecture == "Pipelined":
        _, stage_outs_all, _ = cic_pipelined(x_in, R, N, M)
        total_stages = len(stage_outs_all)
        cols_per_row = 2
        for row_start in range(0, total_stages, cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx, stage_idx in enumerate(range(row_start, min(row_start + cols_per_row, total_stages))):
                s = stage_outs_all[stage_idx]
                stage_type = "Integrator" if stage_idx < N else "Comb"
                stage_num  = stage_idx + 1 if stage_idx < N else stage_idx - N + 1
                with cols[col_idx]:
                    fig_s, ax_s = plt.subplots(figsize=(5, 2.5))
                    display_len = min(128, len(s))
                    ax_s.plot(s[:display_len], linewidth=0.9,
                              color="#2196F3" if stage_type == "Integrator" else "#4CAF50")
                    ax_s.set_title(f"Stage {stage_idx+1}: {stage_type} {stage_num} (after FF)", fontsize=9)
                    ax_s.grid(True, alpha=0.3)
                    st.pyplot(fig_s, use_container_width=True)
                    plt.close(fig_s)

    else:
        # Run all intermediate stages manually
        y_stages = [x_in.astype(np.float64)]
        y_cur = x_in.astype(np.float64)
        for i in range(N):
            y_cur = np.cumsum(y_cur)
            y_stages.append(y_cur.copy())

        y_cur_ds = y_cur[::R]
        y_stages.append(y_cur_ds)

        y_cur2 = y_cur_ds.copy()
        for i in range(N):
            y_cur2 = np.diff(y_cur2, M, prepend=np.zeros(M))
            y_stages.append(y_cur2.copy())

        stage_labels = (
            ["Input"] +
            [f"After Integrator {i+1}" for i in range(N)] +
            [f"After ↓{R}"] +
            [f"After Comb {i+1}" for i in range(N)]
        )

        cols_per_row = 2
        for row_start in range(0, len(y_stages), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx, stage_idx in enumerate(range(row_start, min(row_start + cols_per_row, len(y_stages)))):
                s = y_stages[stage_idx]
                lbl = stage_labels[stage_idx]
                with cols[col_idx]:
                    fig_s, ax_s = plt.subplots(figsize=(5, 2.5))
                    display_len = min(256, len(s))
                    color = "#2196F3" if "Integrator" in lbl else ("#FF5722" if "↓" in lbl else "#4CAF50" if "Comb" in lbl else "#607D8B")
                    ax_s.plot(s[:display_len] / (np.max(np.abs(s[:display_len])) + 1e-12),
                              linewidth=0.9, color=color)
                    ax_s.set_title(lbl, fontsize=9)
                    ax_s.grid(True, alpha=0.3)
                    st.pyplot(fig_s, use_container_width=True)
                    plt.close(fig_s)

# ══════════════════════════════════════════════════════════════════
# TAB 5 – PERFORMANCE TABLE
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Architecture Comparison Table")

    bg = bit_growth(R, N, M)

    data = {
        "Metric": [
            "Adder count",
            "Register count",
            "MUX count",
            "Critical path depth (FO4)",
            "Pipeline latency (cycles)",
            "Throughput (samples/clock)",
            "Internal clock multiplier",
            "Bit growth",
            "Area efficiency",
            "Max clock speed",
        ],
        "Basic": [
            f"{2*N}",
            f"{2*N}",
            "0",
            f"{2*N} adder stages",
            "0",
            "1",
            "1×",
            f"+{bg} bits",
            "Moderate",
            "Low (long path)",
        ],
        "Pipelined": [
            f"{2*N}",
            f"{4*N}",
            "0",
            "1 adder stage",
            f"{2*N}",
            "1 (full throughput)",
            "1×",
            f"+{bg} bits",
            "Low (more regs)",
            "High ✅",
        ],
        "Folded": [
            "1",
            f"{N + 1}",
            f"{N - 1}",
            "1 adder stage (shared)",
            f"≥ {2*N}",
            f"1/{N} (time-mux)",
            f"{N}×",
            f"+{bg} bits",
            "High ✅ (min area)",
            "Moderate",
        ],
    }
    df = pd.DataFrame(data).set_index("Metric")
    st.dataframe(df, use_container_width=True, height=420)

    st.divider()
    st.subheader("Alias Band Attenuation Across Decimation Factors")
    R_vals = [2, 4, 8, 16, 32, 64, 128, 256]
    atten_rows = []
    for r in R_vals:
        _, h = cic_frequency_response(r, N, M, fs_in)
        f_ax = np.linspace(0, fs_in / 2, len(h))
        first_alias_idx = np.argmin(np.abs(f_ax - (fs_in / r)))
        if first_alias_idx < len(h):
            atten = h[first_alias_idx]
        else:
            atten = 0
        atten_rows.append({
            "R": r,
            "Fs_out (kHz)": f"{fs_in/(r*1e3):.1f}",
            "First Alias Atten. (dB)": f"{atten:.1f}",
            "Bit Growth": f"+{bit_growth(r, N, M)} bits",
        })
    st.dataframe(pd.DataFrame(atten_rows).set_index("R"), use_container_width=True)

    st.divider()
    st.subheader("Bit Growth vs N and R")
    fig_bg, ax_bg = plt.subplots(figsize=(8, 4))
    R_range = [2, 4, 8, 16, 32, 64, 128, 256]
    for n_val in range(1, 7):
        bg_vals = [bit_growth(r, n_val, M) for r in R_range]
        ax_bg.plot(R_range, bg_vals, marker="o", label=f"N={n_val}", linewidth=1.5)
    ax_bg.set_xscale("log", base=2)
    ax_bg.set_xlabel("Decimation Factor R", fontsize=10)
    ax_bg.set_ylabel("Bit Growth (bits)", fontsize=10)
    ax_bg.set_title(f"Bit Growth  B_extra = N·⌈log₂(R·M)⌉  [M={M}]", fontsize=11)
    ax_bg.legend(fontsize=8, ncol=3)
    ax_bg.grid(True, alpha=0.3)
    ax_bg.set_facecolor("#fafafa")
    st.pyplot(fig_bg, use_container_width=True)
    plt.close(fig_bg)

# ──────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "CIC Decimation Filter Visualizer — Supports Basic · Pipelined · Folded architectures  |  "
    "Input rates: 500 kHz – 500 MHz  |  R: 2–256  |  N: 1–6  |  M: 1–2"
)
