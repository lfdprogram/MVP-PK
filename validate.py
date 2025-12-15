import json

from models import Medicamento, MedicationDatabase


def validar_database(caminho_json: str):
    print("Iniciando validação...\n")

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # Validação do objeto raiz
    try:
        db = MedicationDatabase(**dados)
        print("Arquivo JSON validado com sucesso!\n")
    except Exception as e:
        print("Erro ao validar o JSON completo:")
        print(e)
        return

    # Validação dos medicamentos individualmente
    print("Validando medicamentos...\n")
    for nome, med_data in dados.get("medicamentos", {}).items():
        try:
            med = Medicamento(**med_data)
            print(f"[OK] {nome}")
        except Exception as e:
            print(f"[ERRO] {nome}:")
            print(e)
            print()

    print("\nValidação concluída.")


if __name__ == "__main__":
    validar_database("medicamentos.json")
