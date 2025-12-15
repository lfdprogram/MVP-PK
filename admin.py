import json
from pathlib import Path

import streamlit as st

# ================================
# CONFIG
# ================================
st.set_page_config(page_title="Admin - Medicamentos", page_icon="🛠️")

JSON_PATH = Path("medicamentos.json")
PASSWORD = st.secrets["admin_password"]


# ================================
# AUTENTICAÇÃO SIMPLES
# ================================
st.title("🛠️ Painel Administrativo")
st.write("Gerencie os medicamentos da sua base.")

senha = st.text_input("Senha de administrador", type="password")

if senha != PASSWORD:
    st.error("Senha incorreta.")
    st.stop()

st.success("Acesso autorizado.")


# ================================
# CARREGAR BANCO
# ================================
if JSON_PATH.exists():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        database = json.load(f)
else:
    database = {}


# ================================
# FORMULÁRIO
# ================================
st.subheader("➕ Adicionar ou editar medicamento")

with st.form("form_med"):
    nome = st.text_input("Nome do medicamento (chave)", placeholder="vancomicina").strip().lower()

    classe = st.text_input("Classe farmacológica", placeholder="Glicopeptídeo")

    st.markdown("### ⚗️ Farmacocinética")
    vd = st.text_input("Vd (L/kg)", placeholder="0.7")
    protein = st.text_input("Ligação proteica (%)", placeholder="55")
    acido_base = st.text_input("Ácido ou Base", placeholder="Ácido fraco")
    pka = st.text_input("pKa", placeholder="7.2")

    renal = st.text_area("Ajuste renal")
    obesos = st.text_area("Ajuste em obesos")
    hepatopatas = st.text_area("Ajuste em hepatopatas")

    st.markdown("### 🧬 Penetração Tecidual")
    pulmao = st.text_input("Pulmão", placeholder="Boa")
    osso = st.text_input("Osso", placeholder="Moderada")
    bhe = st.text_input("Barreira hematoencefálica", placeholder="Baixa")
    peritoneal = st.text_input("Peritoneal")
    pleural = st.text_input("Pleural")
    ocular = st.text_input("Ocular")
    bile = st.text_input("Bile")

    st.markdown("### 📝 Notas clínicas")
    notes = st.text_area("Notas clínicas")

    st.markdown("### ⚠️ Alertas")
    alerts = st.text_area("Alertas")

    submitted = st.form_submit_button("Salvar medicamento")


# ================================
# SALVAR NO JSON
# ================================
if submitted:
    if not nome:
        st.error("O nome é obrigatório.")
        st.stop()

    novo_med = {
        nome: {
            "nome": nome.capitalize(),
            "classe": classe,
            "farmacocinetica": {
                "vd_L_kg": vd,
                "protein_binding_percent": protein,
                "acido_ou_base": acido_base,
                "pKa": pka,
                "renal_adjustment": renal,
                "obesos_pk": obesos,
                "hepatopatas_pk": hepatopatas,
                "tissue_penetration": {
                    "pulmao": pulmao,
                    "osso": osso,
                    "bhe": bhe,
                    "peritoneal": peritoneal,
                    "pleural": pleural,
                    "ocular": ocular,
                    "bile": bile,
                },
                "clinical_notes": notes,
                "alerts": alerts,
            },
            "referencias": {
                "vd": "",
                "protein_binding": "",
                "pKa": "",
                "renal_adjustment": "",
                "obesos_pk": "",
                "hepatopatas_pk": "",
                "tissue_penetration": "",
                "clinical_notes": "",
                "alerts": "",
            }
        }
    }

    # Atualizar ou criar
    database.update(novo_med)

    # Salvar
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=4)

    st.success(f"Medicamento **{nome}** salvo com sucesso!")
    st.balloons()
