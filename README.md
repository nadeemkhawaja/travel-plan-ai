# Travel Plan AI

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## Overview
Travel Plan AI is a Streamlit-based travel itinerary generator powered by Python and OpenAI.  
Users provide their destination, travel dates, and preferences, and the AI generates a structured day-by-day travel plan.  
Optional PDF export is available for sharing or printing itineraries.  

This project demonstrates practical AI integration in Python and serves as a professional, portfolio-ready project.

---

## Features
- Personalized AI-generated travel itineraries
- Supports multiple destinations and flexible durations
- Optional PDF export of itineraries
- Streamlit-based user interface for easy interaction
- Clean, professional project structure

---

## Prerequisites
- Python 3.10+  
- Visual Studio Code (optional, recommended)  
- OpenAI API Key (provided offline)  
- Internet access

---

## Project Structure

```text
travel-plan-ai/
├── travel_plan.py       # Main Python program
├── requirements.txt    # Dependencies
├── .env                # Environment variables (API key)
├── README.md           # Project documentation
├── LICENSE             # MIT License
├── assets/             # Screenshots and sample PDFs
├── data/               # Optional CSV/JSON for destinations
└── .venv/              # Virtual environment

```

---

## Setup Instructions (macOS & Windows)

### Step 1: Create Virtual Environment

**macOS / Linux:**
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

**Windows (PowerShell):**
```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### Step 2: Install Dependencies
```
python -m pip install -r requirements.txt
```

### Step 3: Configure OpenAI API Key
Create a .env file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

⚠️ Never commit your real API key to GitHub. Use a placeholder in the repository.

### Step 4: Run the Application
```
streamlit run travel_plan.py
```

Follow the prompts in the browser to input travel preferences and generate a complete itinerary.

### Step 5: Optional — Using Visual Studio Code

Open Visual Studio Code

Open the project folder

Open Terminal from View > Terminal

Select the Python Interpreter inside .venv

### Screenshots
Add screenshots of your program in the assets/ folder

### Troubleshooting

Ensure Streamlit is installed in the virtual environment
Ensure .env file exists and contains your API key
Run commands in the terminal, not Python REPL
If Streamlit doesn’t launch, ensure your virtual environment is activated