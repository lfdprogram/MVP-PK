import json
from difflib import get_close_matches

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Carrega o JSON uma vez
with open("medicamentos.json", "r", encoding="utf-8") as f:
    DB = json.load(f)

@router.get("/buscar")
def buscar_medicamento(nome: str):
    nome = nome.lower().strip()

    # Se houver correspondência exata
    if nome in DB:
        return DB[nome]

    # Busca aproximada (retorna até 4 melhores)
    candidatos = get_close_matches(nome, DB.keys(), n=4, cutoff=0.45)

    if not candidatos:
        raise HTTPException(status_code=404, detail="Nenhum medicamento encontrado.")

    # Retorna os candidatos encontrados
    return {
        "resultado": "nenhuma correspondência exata",
        "sugestoes": candidatos,
        "detalhes_sugestao_principal": DB[candidatos[0]]
    }
