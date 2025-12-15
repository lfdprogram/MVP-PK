from typing import Dict, Optional

from pydantic import BaseModel, Field, RootModel


class TissuePenetration(BaseModel):
    pulmao: Optional[str] = None
    osso: Optional[str] = None
    bhe: Optional[str] = None
    peritoneal: Optional[str] = None
    pleural: Optional[str] = None
    ocular: Optional[str] = None
    bile: Optional[str] = None


class Farmacocinetica(BaseModel):
    vd_L_kg: Optional[float] = Field(
        None, description="Volume de distribuição (L/kg)"
    )
    protein_binding_percent: Optional[float] = Field(
        None, description="Ligação a proteínas plasmáticas (%)"
    )
    renal_adjustment: Optional[str] = None
    obesos_pk: Optional[str] = None
    hepatopatas_pk: Optional[str] = None
    acido_ou_base: Optional[str] = None
    pKa: Optional[float] = None
    tissue_penetration: Optional[TissuePenetration] = None
    clinical_notes: Optional[str] = None
    alerts: Optional[str] = None


class Referencias(BaseModel):
    vd: Optional[str] = None
    protein_binding: Optional[str] = None
    pKa: Optional[str] = None
    renal_adjustment: Optional[str] = None
    obesos_pk: Optional[str] = None
    hepatopatas_pk: Optional[str] = None
    tissue_penetration: Optional[str] = None
    clinical_notes: Optional[str] = None
    alerts: Optional[str] = None


class Medicamento(BaseModel):
    nome: str
    classe: Optional[str] = None
    farmacocinetica: Optional[Farmacocinetica] = None
    referencias: Optional[Referencias] = None


class Paciente(BaseModel):
    peso: float = Field(..., description="Peso do paciente (kg)")
    altura: Optional[float] = Field(None, description="Altura (cm)")
    idade: Optional[int] = Field(None, description="Idade (anos)")
    sexo: Optional[str] = Field(None, description="Masculino, Feminino ou Outro")
    creatinina: Optional[float] = Field(
        None, description="Creatinina sérica (mg/dL)"
    )
    clcr: Optional[float] = Field(
        None, description="Clearance de creatinina já calculado"
    )


class InteracaoRequest(BaseModel):
    paciente: Paciente
    medicamento: str


class MedicationDatabase(RootModel[Dict[str, Medicamento]]):
    pass


class DecisaoDoseInput(BaseModel):
    medicamento: str
    clcr: Optional[float] = Field(
        None, description="Clearance de creatinina (mL/min), se disponível"
    )
    obeso: Optional[bool] = Field(
        None, description="Paciente obeso (True/False)"
    )
    hepatopata: Optional[bool] = Field(
        None, description="Paciente com doença hepática relevante"
    )
    sitio_infeccao: Optional[str] = Field(
        None,
        description="Sítio principal da infecção (pulmao, osso, bhe, peritoneal, pleural, ocular, bile etc.)",
    )
    sepse_choque: Optional[bool] = Field(
        None, description="Sepse grave ou choque séptico"
    )
    ventilacao_mecanica: Optional[bool] = Field(
        None, description="Paciente em ventilação mecânica"
    )
    tr_suporte_renal: Optional[bool] = Field(
        None, description="Terapia substitutiva renal (hemodiálise/CRRT)"
    )
