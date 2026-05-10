# LLM-Powered PID Tuner

Enter a transfer function, calculate PID parameters using Pole Placement, simulate the response, and get an AI-powered interpretation with GPT-4o.

## Features
- Automatic PID calculation using Pole Placement method
- Step response and control signal plots
- AI-powered interpretation in Turkish using GPT-4o

## Usage
1. Enter numerator and denominator coefficients of your transfer function
2. Adjust damping ratio (ζ) and natural frequency (ωn)
3. Click "Pole Placement ile hesapla" to compute PID parameters
4. Click "Simülasyonu çalıştır" to see the plots
5. Click "Bu sonucu LLM ile yorumla" to get GPT-4o interpretation

## Installation

```bash
pip install streamlit langchain langchain-openai control matplotlib numpy python-dotenv
```

Create a `.env` file:

OPENAI_API_KEY=sk-...

Run:
```bash
python -m streamlit run app.py
```

## Tech Stack
- Python, Streamlit
- LangChain, GPT-4o
- python-control, NumPy, Matplotlib
