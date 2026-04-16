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

