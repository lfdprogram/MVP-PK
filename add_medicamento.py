import json
from pathlib import Path

from models import MedicationDatabase, MedicationPK, TissuePenetration

JSON_PATH = Path("medicamentos.json")

def load_db():
    return MedicationDatabase.parse_file(JSON_PATH).__root__

def save_db(db):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def add_med(name: str, pk: MedicationPK):
    db = load_db()
    key = name.lower().replace(" ", "_")
    if key in db:
        raise KeyError(f"Medicamento {key} já existe.")
    db[key] = pk.dict()
    save_db(db)
    print(f"Adicionado: {key}")

if __name__ == "__main__":
    # Exemplo de uso: editar aqui e rodar para adicionar
    novo = MedicationPK(
        vd_L=10.0,
        protein_binding_percent=20.0,
        renal_adjustment="Nenhum",
        obesos_pk="Dados",
        hepatopatas_pk="Dados",
        acido_ou_base="Neutro",
        tissue_penetration=TissuePenetration(
            pulmao="Boa",
            osso="Baixa",
            bhe="Baixa",
            peritoneal="Baixa",
            pleural="Baixa",
            ocular="Baixa",
            bile="Baixa"
        ),
        clinical_notes="Exemplo",
        alerts="Nenhum"
    )
    add_med("exemplo_medicamento", novo)
