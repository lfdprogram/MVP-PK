import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="UTI PK Helper", layout="centered")
st.title("UTI PK Helper – Decisão de Dose")

st.markdown(
    "Preencha os dados do paciente e o medicamento para gerar o card clínico. "
    "Ferramenta de apoio; não substitui protocolos locais nem julgamento clínico."
)


@st.cache_data(ttl=300)
def carregar_medicamentos():
    try:
        resp = requests.get(f"{API_URL}/lista", timeout=5)
        resp.raise_for_status()
        meds = resp.json()
        return sorted(meds)
    except Exception:
        return ["meropenem", "vancomicina", "amicacina"]


medicamentos = carregar_medicamentos()


def calcular_clcr_cg(sexo: str, idade: float, peso: float, creat: float) -> float:
    fator = 0.85 if sexo.lower().startswith("f") else 1.0
    clcr = ((140 - idade) * peso * fator) / (72 * creat)
    return clcr


with st.form("decisao_dose_form"):
    medicamento = st.selectbox("Medicamento", medicamentos)

    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    idade = st.number_input("Idade (anos)", min_value=18, max_value=110, value=60)
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=80.0)
    creat = st.number_input("Creatinina sérica (mg/dL)", min_value=0.1, max_value=10.0, value=1.0)

    obeso = st.checkbox("Paciente obeso")
    hepatopata = st.checkbox("Paciente hepatopata")
    sepse_choque = st.checkbox("Sepse grave / choque séptico")
    ventilacao_mecanica = st.checkbox("Ventilação mecânica")
    tr_suporte_renal = st.checkbox("Terapia substitutiva renal (hemodiálise/CRRT)")

    sitio = st.selectbox(
        "Sítio infeccioso",
        ["", "pulmao", "osso", "bhe", "peritoneal", "pleural", "ocular", "bile"],
        index=0,
    )

    submitted = st.form_submit_button("Gerar decisão")

if submitted:
    clcr_calc = calcular_clcr_cg(sexo, idade, peso, creat)
    st.markdown(f"**ClCr estimado (Cockcroft-Gault):** {clcr_calc:.1f} mL/min")

    payload = {
        "medicamento": medicamento,
        "clcr": clcr_calc,
        "obeso": obeso,
        "hepatopata": hepatopata,
        "sitio_infeccao": sitio or None,
        "sepse_choque": sepse_choque,
        "ventilacao_mecanica": ventilacao_mecanica,
        "tr_suporte_renal": tr_suporte_renal,
    }

    try:
        resp = requests.post(f"{API_URL}/decisao-dose", json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json()

            st.subheader(f"{data['medicamento']} ({data.get('classe', '')})")

            # RENAL
            texto_renal = data.get("resumo_renal", "") or ""
            if "ajuste" in texto_renal.lower() or "<" in texto_renal:
                st.warning(f"**Ajuste renal**\n\n{texto_renal}")
            else:
                st.info(f"**Ajuste renal**\n\n{texto_renal}")

            # OBESIDADE
            st.markdown("**Obesidade**")
            st.write(data.get("resumo_obesos", ""))

            # HEPATOPATIA
            st.markdown("**Hepatopatia**")
            st.write(data.get("resumo_hepatico", ""))

            # SÍTIO
            texto_sitio = data.get("resumo_sitio", "") or ""
            if "baixa" in texto_sitio.lower() or "sem dado" in texto_sitio.lower():
                st.warning(f"**Sítio infeccioso**\n\n{texto_sitio}")
            else:
                st.info(f"**Sítio infeccioso**\n\n{texto_sitio}")

            # NOTAS CLÍNICAS
            st.markdown("**Notas clínicas**")
            notas = data.get("notas_clinicas") or []
            if isinstance(notas, str):
                notas = [notas]
            for nota in notas:
                st.markdown(f"- {nota}")

            # ALERTAS
            alertas = data.get("alertas", "") or ""
            if any(palavra in alertas.lower() for palavra in ["nefro", "oto", "convuls", "depressão respiratória"]):
                st.error(f"**Alertas**\n\n{alertas}")
            else:
                st.warning(f"**Alertas**\n\n{alertas}")

        else:
            st.error(f"Erro da API ({resp.status_code}): {resp.text}")
    except Exception as e:
        st.error(f"Erro ao conectar na API: {e}")
