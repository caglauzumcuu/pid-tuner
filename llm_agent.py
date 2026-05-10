import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_pid_suggestion(num, den):
    #llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen deneyimli bir kontrol mühendisisin.
SADECE şu JSON formatında yanıt ver, başka hiçbir şey yazma:
{{"Kp": sayı, "Ki": sayı, "Kd": sayı, "aciklama": "metin"}}"""),
        ("human", "Pay: {num}\nPayda: {den}\n\nBu sistem için PID parametresi öner.")
    ])
    chain = prompt | llm
    response = chain.invoke({"num": str(num), "den": str(den)})
    return response.content


def interpret_results(num, den, Kp, Ki, Kd, metrics):
    #llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen deneyimli bir kontrol mühendisisin.
Verilen PID simülasyon sonucunu Türkçe yorumla.
Hem step response hem de kontrol sinyali hakkında yorum yap:
- Kontrol sinyali çok büyükse aktüatör doyumu riski var
- Kontrol sinyali salınım yapıyorsa Kd çok büyük olabilir
- Kararlı haldeki kontrol sinyali sıfıra yakınsa Ki iyi ayarlanmış demektir
Düz metin yaz, JSON değil."""),
        ("human", """Sistem: Pay={num}, Payda={den}
PID: Kp={Kp}, Ki={Ki}, Kd={Kd}
Step response → Aşım={overshoot}%, Yerleşme={settling}s, Kararlı hal={steady}
Kontrol sinyali → Maksimum={u_max}, Kararlı haldeki değer={u_final}

Bu sonucu yorumla.""")
    ])
    chain = prompt | llm
    response = chain.invoke({
        "num": str(num), "den": str(den),
        "Kp": Kp, "Ki": Ki, "Kd": Kd,
        "overshoot": metrics["overshoot"],
        "settling": metrics["settling_time"],
        "steady": metrics["steady_state"],
        "u_max": metrics["u_max"],
        "u_final": metrics["u_final"]
    })
    return response.content