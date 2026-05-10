import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import json
from simulator import simulate_pid, pole_placement_pid
from llm_agent import get_pid_suggestion, interpret_results
from dotenv import load_dotenv
import os
load_dotenv()

st.title("LLM Destekli PID Tuner")
user_api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
if not user_api_key:
    st.warning("Devam etmek için OpenAI API key'inizi girin.")
    st.stop()

os.environ["OPENAI_API_KEY"] = user_api_key
st.caption("Transfer fonksiyonu gir → PID hesapla → Simülasyonu gör → LLM yorumlasın")

st.subheader("Sistem transfer fonksiyonu G(s)")
col1, col2 = st.columns(2)
with col1:
    num_str = st.text_input("Pay katsayıları", value="5")
with col2:
    den_str = st.text_input("Payda katsayıları", value="1 10 15")

st.subheader("PID parametreleri")

col_z, col_w = st.columns(2)
zeta = col_z.slider("Sönümleme oranı (ζ)", 0.3, 1.0, 0.7, 0.05)
wn = col_w.slider("Doğal frekans (ωn)", 0.5, 10.0, 2.0, 0.5)

if st.button("Pole Placement ile hesapla"):
    num = list(map(float, num_str.split()))
    den = list(map(float, den_str.split()))
    Kp_pp, Ki_pp, Kd_pp = pole_placement_pid(num, den, zeta, wn)
    st.session_state["Kp"] = Kp_pp
    st.session_state["Ki"] = Ki_pp
    st.session_state["Kd"] = Kd_pp
    st.session_state["llm_aciklama"] = (
        f"Pole placement → ζ={zeta}, ωn={wn} | Kp={Kp_pp}, Ki={Ki_pp}, Kd={Kd_pp}"
    )

if "llm_aciklama" in st.session_state:
    st.info(st.session_state["llm_aciklama"])

c1, c2, c3 = st.columns(3)
Kp = c1.number_input("Kp", value=st.session_state.get("Kp", 1.0), step=0.1)
Ki = c2.number_input("Ki", value=st.session_state.get("Ki", 0.5), step=0.1)
Kd = c3.number_input("Kd", value=st.session_state.get("Kd", 0.1), step=0.05)

if st.button("Simülasyonu çalıştır"):
    num = list(map(float, num_str.split()))
    den = list(map(float, den_str.split()))
    t, y, u, metrics = simulate_pid(num, den, Kp, Ki, Kd)
    st.session_state["sim_t"] = t.tolist()
    st.session_state["sim_y"] = y.tolist()
    st.session_state["sim_u"] = u.tolist()
    st.session_state["last_metrics"] = metrics
    st.session_state["last_num"] = num
    st.session_state["last_den"] = den
    st.session_state["last_Kp"] = Kp
    st.session_state["last_Ki"] = Ki
    st.session_state["last_Kd"] = Kd
    st.session_state["yorum"] = None

if "sim_t" in st.session_state:
    t = np.array(st.session_state["sim_t"])
    y = np.array(st.session_state["sim_y"])
    u = np.array(st.session_state["sim_u"])
    metrics = st.session_state["last_metrics"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

    ax1.plot(t, y, color="#185FA5", linewidth=2)
    ax1.axhline(y=1, color="gray", linestyle="--", alpha=0.5, label="Hedef")
    ax1.set_ylabel("Çıkış")
    ax1.set_title("Step Response")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(t, u, color="#D85A30", linewidth=2)
    ax2.axhline(y=0, color="gray", linestyle="--", alpha=0.3)
    ax2.set_xlabel("Zaman (s)")
    ax2.set_ylabel("u(t)")
    ax2.set_title("Kontrol Sinyali")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Aşım", f"{metrics['overshoot']}%")
    m2.metric("Yerleşme süresi", f"{metrics['settling_time']} s")
    m3.metric("Kararlı hal", metrics['steady_state'])
    m4.metric("u maks", metrics['u_max'])

    if st.button("Bu sonucu LLM ile yorumla"):
        with st.spinner("LLM yorumluyor..."):
            yorum = interpret_results(
                st.session_state["last_num"],
                st.session_state["last_den"],
                st.session_state["last_Kp"],
                st.session_state["last_Ki"],
                st.session_state["last_Kd"],
                st.session_state["last_metrics"]
            )
            st.session_state["yorum"] = yorum

    if st.session_state.get("yorum"):
        st.success(st.session_state["yorum"])
