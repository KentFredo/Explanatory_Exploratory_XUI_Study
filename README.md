# 🧠 Sepsis Mortality Risk – XAI Study App

This **Streamlit-based application** was developed as part of a study comparing **exploratory** and **explanatory** explainable user interfaces (XUIs) in the context of **clinical decision support systems (CDSS)** for **sepsis mortality risk prediction**.

The app guides participants through the **entire study flow**, including informed consent, model-based decision support, and a questionnaire. Upon completion, the collected study data can be **downloaded as a ZIP archive** containing CSV files.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # For Windows
# OR
source .venv/bin/activate  # For macOS/Linux
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app/app.py
```

---

## 📦 Features

- Exploratory and explanatory explainable AI interfaces for clinical models
- Full study flow including consent, model interaction, and questionnaire
- Local data collection and export (ZIP of CSV files)
