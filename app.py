import streamlit as st
import numpy as np
import subprocess
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import shutil

st.set_page_config(
    page_title="CIC Filter Simulator — Team Mavericks",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.hero { background: linear-gradient(135deg, #0d1b2a 0%, #112240 50%, #0a192f 100%); border: 1px solid #1e3a5f; border-radius: 12px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; }
.hero h1 { font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 600; color: #00d4ff; margin: 0 0 6px 0; }
.hero p  { color: #8892b0; font-size: 0.9rem; margin: 0; }
.tag { display:inline-block; background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3); color:#00d4ff; font-size:11px; padding:3px 10px; border-radius:20px; margin-right:6px; margin-bottom:10px; font-family:'JetBrains Mono',monospace; }
.metric-card { background:#112240; border:1px solid #1e3a5f; border-radius:10px; padding:1rem 1.2rem; text-align:center; }
.metric-card .val { font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:600; color:#00d4ff; line-height:1; }
.metric-card .lbl { font-size:11px; color:#8892b0; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px; }
.section-header { font-family:'JetBrains Mono',monospace; font-size:12px; color:#00d4ff; text-transform:uppercase; letter-spacing:2px; border-bottom:1px solid #1e3a5f; padding-bottom:8px; margin-bottom:1rem; }
.output-block { background:#0d1117; border:1px solid #2ea043; border-radius:8px; padding:1rem; font-family:'JetBrains Mono',monospace; font-size:12px; color:#56d364; white-space:pre-wrap; max-height:320px; overflow-y:auto; }
.error-block  { background:#0d1117; border:1px solid #e74c3c; border-radius:8px; padding:1rem; font-family:'JetBrains Mono',monospace; font-size:12px; color:#ff6b6b; white-space:pre-wrap; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <span class="tag">5G / 6G RF Front-End</span>
  <span class="tag">RTL Verified</span>
  <span class="tag">Team Mavericks</span>
  <h1>📡 CIC Decimation Filter — Interactive Simulator</h1>
  <p>Cascaded Integrator-Comb filter · Verilog HDL · Real iverilog simulation · Live waveform analysis</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="section-header">Filter Parameters</div>', unsafe_allow_html=True)
    R = st.slider("Decimation Factor (R)", 2, 16, 4, 1)
    N = st.slider("Number of Stages (N)", 1, 4, 2, 1)
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Test Signal</div>', unsafe_allow_html=True)
    signal_type = st.selectbox("Input Signal", [
        "Ramp (0->1900 repeating)", "DC Constant", "Sine Wave", "Step Function", "Random Noise"
    ])
    dc_val, freq_norm, amplitude = 500, 0.05, 1000
    if signal_type == "DC Constant":
        dc_val = st.slider("DC Value", 100, 2000, 500, 100)
    if signal_type == "Sine Wave":
        freq_norm = st.slider("Normalized Frequency", 0.01, 0.49, 0.05, 0.01)
        amplitude = st.slider("Amplitude", 100, 5000, 1000, 100)
    num_samples = st.slider("Input Samples", 64, 512, 200, 16)
    st.markdown("""
    <div style="font-size:12px;color:#8892b0;line-height:1.7;margin-top:1rem">
    <b style="color:#cdd9e5">23BVD1004</b> Pasyanth P<br>
    <b style="color:#cdd9e5">23BVD1031</b> T Shashank<br>
    <b style="color:#cdd9e5">23BVD1047</b> Abin Mohammad
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Simulate", "Frequency Response", "Architecture", "Verilog Code"])

with tab1:
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.markdown('<div class="section-header">Simulation Engine</div>', unsafe_allow_html=True)
        iverilog_available = shutil.which("iverilog") is not None
        if iverilog_available:
            st.success("iverilog detected - real Verilog simulation active")
        else:
            st.info("Running Python model (same logic as Verilog RTL)")
        st.markdown('<div class="section-header" style="margin-top:1.2rem">Key Parameters</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.markdown(f'<div class="metric-card"><div class="val">{R}</div><div class="lbl">Decim. Factor</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val">{N}</div><div class="lbl">Stages</div></div>', unsafe_allow_html=True)
        m3, m4 = st.columns(2)
        out_samples = num_samples // R
        growth = N * int(np.ceil(np.log2(R)))
        out_bits = 16 + growth
        m3.markdown(f'<div class="metric-card"><div class="val">{out_samples}</div><div class="lbl">Output Samples</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="val">{out_bits}</div><div class="lbl">Output Bits</div></div>', unsafe_allow_html=True)

    with col_r:
        t = np.arange(num_samples)
        if signal_type == "Ramp (0->1900 repeating)":
            x_in = np.array([(i % 20) * 100 for i in range(num_samples)], dtype=np.int64)
        elif signal_type == "DC Constant":
            x_in = np.full(num_samples, dc_val, dtype=np.int64)
        elif signal_type == "Sine Wave":
            x_in = (amplitude * np.sin(2 * np.pi * freq_norm * t)).astype(np.int64)
        elif signal_type == "Step Function":
            x_in = np.where(t >= num_samples // 4, 1000, 0).astype(np.int64)
        else:
            x_in = np.random.default_rng(42).integers(-1000, 1000, num_samples)

        def simulate_cic(x, R, N):
            integ = [0] * N
            dec_count = 0
            comb_reg = [0] * N
            comb_delay = [0] * N
            outputs, out_idx = [], []
            for idx, sample in enumerate(x):
                integ[0] += int(sample)
                for k in range(1, N):
                    integ[k] += integ[k-1]
                dec_valid = False
                if dec_count == R - 1:
                    dec_count = 0
                    dec_out = integ[N-1]
                    dec_valid = True
                else:
                    dec_count += 1
                if dec_valid:
                    comb_reg[0] = dec_out - comb_delay[0]
                    comb_delay[0] = dec_out
                    for j in range(1, N):
                        new_r = comb_reg[j-1] - comb_delay[j]
                        comb_delay[j] = comb_reg[j-1]
                        comb_reg[j] = new_r
                    outputs.append(comb_reg[N-1])
                    out_idx.append(idx)
            return np.array(outputs), np.array(out_idx)

        y_out, out_idx = simulate_cic(x_in, R, N)

        fig = make_subplots(rows=2, cols=1,
            subplot_titles=("Input Signal (High Rate)", "CIC Output (Decimated)"),
            vertical_spacing=0.18)
        fig.add_trace(go.Scatter(x=list(range(len(x_in))), y=x_in.tolist(),
            mode='lines', name='x_in', line=dict(color='#64b5f6', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=out_idx.tolist(), y=y_out.tolist(),
            mode='lines+markers', name='y_out',
            line=dict(color='#00d4ff', width=2),
            marker=dict(color='#00d4ff', size=6, line=dict(color='#0a0e1a', width=1))), row=2, col=1)
        fig.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0d1b2a',
            font=dict(family='Space Grotesk', color='#8892b0', size=12),
            legend=dict(bgcolor='rgba(13,27,42,0.8)', bordercolor='#1e3a5f', borderwidth=1),
            margin=dict(l=10, r=10, t=40, b=10))
        for i in [1, 2]:
            fig.update_xaxes(gridcolor='#1e3a5f', zerolinecolor='#1e3a5f', row=i, col=1)
            fig.update_yaxes(gridcolor='#1e3a5f', zerolinecolor='#1e3a5f', row=i, col=1)
        st.plotly_chart(fig, use_container_width=True)

        if iverilog_available:
            st.markdown('<div class="section-header">Verilog Console Output</div>', unsafe_allow_html=True)
            base = os.path.dirname(os.path.abspath(__file__))
            v_filter = os.path.join(base, "cic_filter.v")
            v_tb = os.path.join(base, "cic_testbench.v")
            try:
                result = subprocess.run(
                    ["iverilog", "-o", "/tmp/cic_sim", v_filter, v_tb],
                    capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    vvp = subprocess.run(["vvp", "/tmp/cic_sim"],
                        capture_output=True, text=True, timeout=15)
                    st.markdown(f'<div class="output-block">{vvp.stdout}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-block">Compile error:\n{result.stderr}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-block">Error: {e}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-header">CIC Frequency Response</div>', unsafe_allow_html=True)
    f = np.linspace(0.0001, 0.5, 2000)
    with np.errstate(divide='ignore', invalid='ignore'):
        H = np.abs(np.sin(np.pi * f * R) / (R * np.sin(np.pi * f))) ** N
        H = np.where(np.isnan(H), 1.0, H)
    H_db = 20 * np.log10(np.maximum(H, 1e-10))
    comp_coeffs = np.array([-1, R + 2, -1]) / R
    H_comp = np.array([abs(sum(comp_coeffs[i] * np.exp(-1j*2*np.pi*fr*i)
                               for i in range(len(comp_coeffs)))) for fr in f])
    H_combined_db = 20 * np.log10(np.maximum(H * H_comp, 1e-10))
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=f.tolist(), y=H_db.tolist(), name='CIC Filter',
        line=dict(color='#64b5f6', width=2)))
    fig2.add_trace(go.Scatter(x=f.tolist(), y=(20*np.log10(np.maximum(H_comp,1e-10))).tolist(),
        name='Compensation FIR', line=dict(color='#ffd166', width=1.5, dash='dot')))
    fig2.add_trace(go.Scatter(x=f.tolist(), y=H_combined_db.tolist(), name='Combined',
        line=dict(color='#00d4ff', width=2.5)))
    fig2.add_vline(x=0.5/R, line_dash="dash", line_color="#ef4444",
        annotation_text="fs/(2R)", annotation_font_color="#ef4444")
    fig2.add_hline(y=-3, line_dash="dot", line_color="#888",
        annotation_text="-3 dB", annotation_font_color="#888")
    fig2.update_layout(height=460, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0d1b2a',
        font=dict(family='Space Grotesk', color='#8892b0', size=12),
        xaxis=dict(title='Normalized Frequency (xFs)', gridcolor='#1e3a5f', range=[0, 0.5]),
        yaxis=dict(title='Magnitude (dB)', gridcolor='#1e3a5f', range=[-80, 5]),
        legend=dict(bgcolor='rgba(13,27,42,0.8)', bordercolor='#1e3a5f', borderwidth=1),
        margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig2, use_container_width=True)
    passband_end = 0.5 / R
    passband_droop = float(H_db[np.argmin(np.abs(f - passband_end))])
    stopband_idx = np.argmin(np.abs(f - min(1.0/R, 0.499)))
    stopband_atten = float(H_db[stopband_idx])
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in [
        (c1, f"1/{R} Fs", "Passband Edge"),
        (c2, f"{passband_droop:.1f} dB", "Passband Droop"),
        (c3, f"{abs(stopband_atten):.0f} dB", "Stopband Atten."),
        (c4, f"{N * int(np.ceil(np.log2(R)))}", "Growth Bits"),
    ]:
        col.markdown(f'<div class="metric-card"><div class="val" style="font-size:1.2rem">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-header">Pipeline Architecture</div>', unsafe_allow_html=True)
    stages = [("S1", "ADC Input", "16-bit signed input at Fs")]
    for i in range(N):
        stages.append((f"I{i+1}", f"Integrator Stage {i+1}", f"Accumulator at Fs — adds previous stage every clock"))
    stages.append(("dR", f"Decimator / {R}", f"Passes one sample every {R} clocks — rate becomes Fs/{R}"))
    for i in range(N):
        stages.append((f"C{i+1}", f"Comb Stage {i+1}", f"Difference filter at Fs/{R} — y[n] minus y[n-1]"))
    stages.append(("OUT", "Output Register", "32-bit valid_out — HIGH for exactly 1 clock per output sample"))
    colors = ["#1e3a5f"] + ["#0f2a4a"]*N + ["#1a3a2a"] + ["#2a1a0a"]*N + ["#1e3a5f"]
    for (num, name, desc), color in zip(stages, colors):
        st.markdown(f"""
        <div style="background:{color};border:1px solid #1e3a5f;border-radius:8px;
                    padding:12px 16px;margin:5px 0;display:flex;align-items:center;gap:12px">
          <div style="background:rgba(0,212,255,0.15);color:#00d4ff;font-family:'JetBrains Mono',monospace;
                      font-size:11px;padding:4px 10px;border-radius:5px;min-width:36px;text-align:center">{num}</div>
          <div>
            <div style="font-weight:500;font-size:14px;color:#cdd9e5">{name}</div>
            <div style="font-size:12px;color:#8892b0;margin-top:2px">{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    bits = N * int(np.ceil(np.log2(R)))
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Transfer Function</div>', unsafe_allow_html=True)
    st.code(f"H(z) = [(1 - z^(-R)) / (1 - z^(-1))]^N\n\nR={R}, N={N}\n|H(f)| = |sin(pi*f*{R}) / ({R}*sin(pi*f))|^{N}\nBit growth = {N} x ceil(log2({R})) = {bits} bits\nOutput word = 16 + {bits} = {16+bits} bits (32-bit reg)", language="text")

with tab4:
    base = os.path.dirname(os.path.abspath(__file__))
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">cic_filter.v</div>', unsafe_allow_html=True)
        v_path = os.path.join(base, "cic_filter.v")
        if os.path.exists(v_path):
            with open(v_path, "r") as fh:
                st.code(fh.read(), language="verilog")
        else:
            st.warning("cic_filter.v not found")
    with col_b:
        st.markdown('<div class="section-header">cic_testbench.v</div>', unsafe_allow_html=True)
        tb_path = os.path.join(base, "cic_testbench.v")
        if os.path.exists(tb_path):
            with open(tb_path, "r") as fh:
                st.code(fh.read(), language="verilog")
        else:
            st.warning("cic_testbench.v not found")
