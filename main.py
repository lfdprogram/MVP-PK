import json

from fastapi import FastAPI, HTTPException, Query

from models import DecisaoDoseInput, MedicationDatabase

app = FastAPI()


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "UTI PK Helper API online",
        "endpoints": ["/lista", "/buscar", "/decisao-dose", "/docs"],
    }


# Carrega o banco na inicialização
with open("medicamentos.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

db = MedicationDatabase.model_validate(raw)


@app.get("/lista")
def listar_medicamentos():
    return list(db.root.keys())


@app.get("/buscar")
def buscar_medicamento(nome: str = Query(..., description="Nome do medicamento")):
    nome_normalizado = nome.strip().lower()

    if nome_normalizado not in db.root:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")

    med = db.root[nome_normalizado]

    fk = med.farmacocinetica or {}
    tp = fk.get("tissue_penetration", {}) if isinstance(fk, dict) else (
        fk.tissue_penetration if fk and fk.tissue_penetration else {}
    )

    ref = med.referencias or {}

    resposta_formatada = {
        "nome": med.nome,
        "classe": med.classe,
        "farmacocinetica": {
            "vd_L_kg": fk.get("vd_L_kg") if isinstance(fk, dict) else getattr(fk, "vd_L_kg", None),
            "protein_binding_percent": fk.get("protein_binding_percent") if isinstance(fk, dict) else getattr(fk, "protein_binding_percent", None),
            "acido_ou_base": fk.get("acido_ou_base") if isinstance(fk, dict) else getattr(fk, "acido_ou_base", None),
            "pKa": fk.get("pKa") if isinstance(fk, dict) else getattr(fk, "pKa", None),
        },
        "ajustes": {
            "renal": fk.get("renal_adjustment") if isinstance(fk, dict) else getattr(fk, "renal_adjustment", None),
            "obesos": fk.get("obesos_pk") if isinstance(fk, dict) else getattr(fk, "obesos_pk", None),
            "hepatopatas": fk.get("hepatopatas_pk") if isinstance(fk, dict) else getattr(fk, "hepatopatas_pk", None),
        },
        "tissue_penetration": {
            "pulmao": tp.get("pulmao") if isinstance(tp, dict) else getattr(tp, "pulmao", None),
            "osso": tp.get("osso") if isinstance(tp, dict) else getattr(tp, "osso", None),
            "bhe": tp.get("bhe") if isinstance(tp, dict) else getattr(tp, "bhe", None),
            "peritoneal": tp.get("peritoneal") if isinstance(tp, dict) else getattr(tp, "peritoneal", None),
            "pleural": tp.get("pleural") if isinstance(tp, dict) else getattr(tp, "pleural", None),
            "ocular": tp.get("ocular") if isinstance(tp, dict) else getattr(tp, "ocular", None),
            "bile": tp.get("bile") if isinstance(tp, dict) else getattr(tp, "bile", None),
        },
        "clinical_notes": fk.get("clinical_notes") if isinstance(fk, dict) else getattr(fk, "clinical_notes", None),
        "alerts": fk.get("alerts") if isinstance(fk, dict) else getattr(fk, "alerts", None),
        "referencias": {
            "vd": ref.get("vd") if isinstance(ref, dict) else getattr(ref, "vd", None),
            "protein_binding": ref.get("protein_binding") if isinstance(ref, dict) else getattr(ref, "protein_binding", None),
            "pKa": ref.get("pKa") if isinstance(ref, dict) else getattr(ref, "pKa", None),
            "renal_adjustment": ref.get("renal_adjustment") if isinstance(ref, dict) else getattr(ref, "renal_adjustment", None),
            "obesos_pk": ref.get("obesos_pk") if isinstance(ref, dict) else getattr(ref, "obesos_pk", None),
            "hepatopatas_pk": ref.get("hepatopatas_pk") if isinstance(ref, dict) else getattr(ref, "hepatopatas_pk", None),
            "tissue_penetration": ref.get("tissue_penetration") if isinstance(ref, dict) else getattr(ref, "tissue_penetration", None),
            "clinical_notes": ref.get("clinical_notes") if isinstance(ref, dict) else getattr(ref, "clinical_notes", None),
            "alerts": ref.get("alerts") if isinstance(ref, dict) else getattr(ref, "alerts", None),
        }
    }

    return resposta_formatada


@app.post("/decisao-dose")
def decisao_dose(payload: DecisaoDoseInput):
    nome_normalizado = payload.medicamento.strip().lower()

    if nome_normalizado not in db.root:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")

    med = db.root[nome_normalizado]
    fk = med.farmacocinetica or {}

    if isinstance(fk, dict):
        tp = fk.get("tissue_penetration", {}) or {}
        renal_adj = fk.get("renal_adjustment")
        obesos_pk = fk.get("obesos_pk")
        hepatopatas_pk = fk.get("hepatopatas_pk")
        clinical_notes = fk.get("clinical_notes")
        alerts = fk.get("alerts")
    else:
        tp = fk.tissue_penetration.dict() if fk.tissue_penetration else {}
        renal_adj = fk.renal_adjustment
        obesos_pk = fk.obesos_pk
        hepatopatas_pk = fk.hepatopatas_pk
        clinical_notes = fk.clinical_notes
        alerts = fk.alerts

    # Bloco rim (texto base + comentário pelo ClCr)
    resumo_renal = renal_adj or "Sem recomendações específicas de ajuste renal."

    comentario_clcr = None
    if payload.clcr is not None:
        clcr_val = payload.clcr

        if nome_normalizado == "meropenem":
            limiar = 50
            if clcr_val < limiar:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (< {limiar}): ajuste de dose/intervalo "
                    "muito provavelmente necessário."
                )
            else:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (≥ {limiar}): ajuste renal provavelmente "
                    "não necessário na prática clínica."
                )

        elif nome_normalizado == "fluconazol":
            limiar = 50
            if clcr_val < limiar:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (< {limiar}): costuma-se reduzir dose "
                    "ou prolongar intervalo."
                )
            else:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (≥ {limiar}): ajuste renal geralmente "
                    "não é necessário."
                )

        elif nome_normalizado == "amicacina":
            limiar = 60
            if clcr_val < limiar:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (< {limiar}): alta prioridade de ajuste "
                    "individual e monitorização de níveis."
                )
            else:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (≥ {limiar}): ainda assim é recomendada "
                    "monitorização de níveis, conforme protocolos."
                )

        elif nome_normalizado == "vancomicina":
            limiar = 50
            if clcr_val < limiar:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (< {limiar}): alta prioridade de ajuste "
                    "de dose/intervalo e monitorização por AUC/TDM."
                )
            else:
                comentario_clcr = (
                    f"ClCr = {clcr_val:.1f} mL/min (≥ {limiar}): manutenção possível com "
                    "dose empírica, mas ainda se recomenda TDM para atingir AUC 400–600."
                )

        # Comentário genérico se não houver regra específica
        if comentario_clcr is None and renal_adj:
            comentario_clcr = (
                f"ClCr informado = {clcr_val:.1f} mL/min; interpretar em conjunto com a "
                "recomendação de ajuste acima."
            )

    if comentario_clcr:
        resumo_renal = f"{resumo_renal} {comentario_clcr}"

    # Bloco obesos
    if payload.obeso:
        resumo_obesos = obesos_pk or "Sem recomendação específica para obesos."
    else:
        resumo_obesos = "Sem recomendações específicas para não obesos."

    # Bloco hepatopatas
    if payload.hepatopata:
        resumo_hepatico = hepatopatas_pk or "Sem orientação específica para hepatopatas."
    else:
        resumo_hepatico = "Sem recomendações específicas para não hepatopatas."

    # Bloco sítio infeccioso
    if payload.sitio_infeccao:
        chave_sitio = payload.sitio_infeccao.strip().lower()
        nivel = tp.get(chave_sitio)
        if nivel:
            resumo_sitio = f"{chave_sitio.capitalize()}: {nivel}."
        else:
            resumo_sitio = f"Sem dado específico para o sítio '{chave_sitio}'."
    else:
        resumo_sitio = "Sítio infeccioso não informado."

    # Comentários adicionais por condições clínicas → lista de notas
    notas_lista = []

    if clinical_notes:
        notas_lista.append(clinical_notes)

    if payload.sepse_choque:
        notas_lista.append(
            "Sepse/choque: evitar subdosagem inicial e priorizar dose plena, especialmente para antibióticos tempo-dependentes e vancomicina."
        )

    if payload.ventilacao_mecanica:
        notas_lista.append(
            "Ventilação mecânica: pacientes críticos podem ter volume de distribuição e clearance alterados; considerar monitorização terapêutica quando disponível."
        )

    if payload.tr_suporte_renal:
        notas_lista.append(
            "Terapia substitutiva renal: seguir protocolo local de hemodiálise/CRRT para ajuste de dose."
        )

    notas_clinicas = notas_lista if notas_lista else None

    resposta = {
        "medicamento": med.nome,
        "classe": med.classe,
        "resumo_renal": resumo_renal,
        "resumo_obesos": resumo_obesos,
        "resumo_hepatico": resumo_hepatico,
        "resumo_sitio": resumo_sitio,
        "notas_clinicas": notas_clinicas,
        "alertas": alerts,
    }

    return resposta
