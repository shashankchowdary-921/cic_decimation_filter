# CIC Decimation Filter — Interactive Simulator
### Team Mavericks | 5G/6G RF Front-End Project

---

## 📁 Project Structure

```
cic_tool/
├── app.py                  ← Streamlit web app (main file)
├── requirements.txt        ← Python dependencies
├── packages.txt            ← System packages (iverilog)
├── .streamlit/
│   └── config.toml         ← Dark theme config
└── verilog/
    ├── cic_filter.v        ← Your RTL design
    └── cic_testbench.v     ← Your testbench
```

---

## 🚀 Option A — Run Locally (5 minutes)

### Step 1: Install Python dependencies
```bash
pip install streamlit numpy plotly
```

### Step 2: Install iverilog (to run actual Verilog)

**Ubuntu/Debian:**
```bash
sudo apt install iverilog
```
**macOS:**
```bash
brew install icarus-verilog
```
**Windows:**
Download installer from: https://bleyer.org/icarus/

### Step 3: Run the app
```bash
cd cic_tool
streamlit run app.py
```
Opens at → http://localhost:8501

---

## 🌐 Option B — Deploy Online FREE (Streamlit Cloud)

Get a public URL like: `https://your-app.streamlit.app`

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "CIC filter simulator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cic-filter.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to → https://share.streamlit.io
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repo, branch = `main`, file = `app.py`
5. Click **Deploy** → you get a free public URL in ~2 minutes!

> **Note:** `packages.txt` automatically installs `iverilog` on the cloud server,
> so your real Verilog simulation runs on the public URL too.

---

## 🔬 What the Tool Does

| Tab | Feature |
|-----|---------|
| **Simulate** | Choose input signal → runs CIC model → live waveform plots |
| **Frequency Response** | CIC magnitude response + compensation filter curve |
| **Architecture** | Pipeline stages breakdown + transfer function |
| **Verilog Code** | Your actual RTL code displayed with syntax highlighting |

### Parameters you can adjust:
- **R** — Decimation factor (2–16)
- **N** — Number of stages (1–4)
- **Signal type** — Ramp, DC, Sine, Step, Random
- **Number of samples** — 64–512

---

## 📖 Reference
Hogenauer, E.B., "An Economical Class of Digital Filters for Decimation and Interpolation,"
IEEE TASSP, vol. 29, no. 2, pp. 155–162, April 1981.
https://ieeexplore.ieee.org/document/1163535
