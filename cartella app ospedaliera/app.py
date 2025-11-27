from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

app = FastAPI(
    title="Hospital Patient Engagement API",
    description="Backend per una webapp ospedaliera focalizzata su fidelizzazione pazienti.",
)

# CORS per permettere alla webapp (Streamlit) di chiamare il backend --- questa è l'backend della soluzione innovativa di MYLATITUDE 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint base (per test rapido)
@app.get("/")
def home():
    return {"message": "Hospital API attiva. Vai su /docs per vedere tutti gli endpoint."}


# ====================
# MODELLI (Pydantic)
# ====================

class PatientCreate(BaseModel):
    name: str
    email: EmailStr
    age: int
    sex: str  # "M" / "F" / "Altro"


class Patient(PatientCreate):
    id: int


class AppointmentCreate(BaseModel):
    patient_id: int
    specialty: str
    date: date
    reason: Optional[str] = None


class Appointment(AppointmentCreate):
    id: int
    status: str  # es. "prenotata", "completata", "cancellata"


class FollowUpCheckIn(BaseModel):
    patient_id: int
    days_from_procedure: int
    pain_level: int      # 0-10
    shortness_of_breath: bool
    fever: bool
    notes: Optional[str] = None


class FollowUpResponse(BaseModel):
    triage_level: str    # "verde", "giallo", "rosso"
    message: str
    suggested_action: str


class PreventionPlanRequest(BaseModel):
    age: int
    sex: str
    conditions: Optional[List[str]] = None  # es. ["ipertensione", "diabete"]


class PreventionPlan(BaseModel):
    risk_profile: str
    recommendations: List[str]
    suggested_screenings: List[str]


class FeedbackCreate(BaseModel):
    patient_id: Optional[int] = None
    rating: int  # 0-10
    comment: Optional[str] = None
    touchpoint: str  # "visita", "ricovero", "pronto soccorso", ecc.


class FeedbackSummary(BaseModel):
    n_responses: int
    average_rating: float
    nps: float  # Net Promoter Score stimato


class NavigationRequest(BaseModel):
    department: str
    building: Optional[str] = None
    floor: Optional[int] = None


class NavigationInfo(BaseModel):
    department: str
    description: str
    building: str
    floor: int
    guidance: List[str]


# ====================
# "DATABASE" IN MEMORIA (PER PROTOTIPO)
# ====================

patients_db: List[Patient] = []
appointments_db: List[Appointment] = []
feedback_db: List[FeedbackCreate] = []


# ====================
# ENDPOINT PAZIENTI
# ====================

@app.post("/patients", response_model=Patient)
def register_patient(data: PatientCreate):
    new_id = len(patients_db) + 1
    patient = Patient(id=new_id, **data.dict())
    patients_db.append(patient)
    return patient


@app.get("/patients", response_model=List[Patient])
def list_patients():
    return patients_db


@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int):
    for p in patients_db:
        if p.id == patient_id:
            return p
    raise HTTPException(status_code=404, detail="Paziente non trovato")


@app.get("/patients/{patient_id}/summary")
def patient_summary(patient_id: int):
    # Info paziente
    patient = None
    for p in patients_db:
        if p.id == patient_id:
            patient = p
            break
    if not patient:
        raise HTTPException(status_code=404, detail="Paziente non trovato")

    # Appuntamenti
    upcoming = [a for a in appointments_db if a.patient_id == patient_id and a.status == "prenotata"]
    past = [a for a in appointments_db if a.patient_id == patient_id and a.status == "completata"]

    # Feedback
    patient_feedback = [f for f in feedback_db if f.patient_id == patient_id]

    return {
        "patient": patient,
        "upcoming_appointments": upcoming,
        "past_appointments": past,
        "feedback_count": len(patient_feedback),
    }


# ====================
# ENDPOINT APPUNTAMENTI
# ====================

@app.post("/appointments", response_model=Appointment)
def create_appointment(data: AppointmentCreate):
    # Controllo che il paziente esista
    if not any(p.id == data.patient_id for p in patients_db):
        raise HTTPException(status_code=404, detail="Paziente non trovato")

    new_id = len(appointments_db) + 1
    appt = Appointment(id=new_id, status="prenotata", **data.dict())
    appointments_db.append(appt)
    return appt


@app.get("/appointments/by_patient/{patient_id}", response_model=List[Appointment])
def get_appointments_by_patient(patient_id: int):
    return [a for a in appointments_db if a.patient_id == patient_id]


# ====================
# ENDPOINT FOLLOW-UP
# ====================

@app.post("/followup/checkin", response_model=FollowUpResponse)
def followup_checkin(data: FollowUpCheckIn):
    # Logica molto semplificata per triage
    risk_points = 0

    if data.pain_level >= 7:
        risk_points += 2
    elif data.pain_level >= 4:
        risk_points += 1

    if data.shortness_of_breath:
        risk_points += 2

    if data.fever:
        risk_points += 1

    if data.days_from_procedure <= 2:
        risk_points += 1  # primi giorni più delicati

    if risk_points <= 1:
        triage = "verde"
        message = "Controllo post-procedura nella norma."
        action = "Prosegui con le indicazioni ricevute e ripeti il check-in domani."
    elif risk_points <= 3:
        triage = "giallo"
        message = "Alcuni sintomi meritano attenzione."
        action = "Valuta un contatto telefonico con il reparto o il medico curante."
    else:
        triage = "rosso"
        message = "Sintomi importanti rilevati."
        action = "Contatta subito il numero indicato dall'ospedale o valuta l'accesso al pronto soccorso."

    return FollowUpResponse(
        triage_level=triage,
        message=message,
        suggested_action=action,
    )


# ====================
# ENDPOINT PREVENZIONE
# ====================

@app.post("/prevention/plan", response_model=PreventionPlan)
def prevention_plan(data: PreventionPlanRequest):
    recs: List[str] = []
    screenings: List[str] = []

    # Profilo rischio in base all'età
    if data.age < 40:
        risk_profile = "basso"
        recs.append("Mantieni uno stile di vita attivo e una dieta equilibrata.")
    elif data.age < 60:
        risk_profile = "moderato"
        recs.append("Controlla regolarmente pressione, colesterolo e glicemia.")
        screenings.append("Check-up cardiovascolare ogni 1-2 anni.")
    else:
        risk_profile = "elevato"
        recs.append("Programma controlli regolari con il medico di riferimento.")
        screenings.append("Controlli cardiologici e metabolici almeno annuali.")

    # Sesso
    if data.sex == "F":
        screenings.append("Valuta uno screening senologico e ginecologico secondo indicazione medica.")
    elif data.sex == "M":
        screenings.append("Valuta uno screening secondo indicazione medica.")

    # Condizioni preesistenti
    if data.conditions:
        if "diabete" in data.conditions:
            recs.append("Controlla regolarmente glicemia e programma visita oculistica periodica.")
        if "ipertensione" in data.conditions:
            recs.append("Monitora la pressione e riduci l'apporto di sale.")
        if "ipercolesterolemia" in data.conditions:
            recs.append("Riduci grassi saturi e segui dieta ipolipidica.")
        if "fumo" in data.conditions:
            recs.append("Valuta un programma di cessazione del fumo.")
        if "obesità" in data.conditions:
            recs.append("Consulta nutrizionista e valuta attività fisica regolare.")

    return PreventionPlan(
        risk_profile=risk_profile,
        recommendations=recs,
        suggested_screenings=screenings,
    )


# ====================
# ENDPOINT FEEDBACK
# ====================

@app.post("/feedback", response_model=FeedbackCreate)
def add_feedback(data: FeedbackCreate):
    if data.rating < 0 or data.rating > 10:
        raise HTTPException(status_code=400, detail="Rating deve essere tra 0 e 10.")
    feedback_db.append(data)
    return data


@app.get("/feedback/summary", response_model=FeedbackSummary)
def feedback_summary():
    if not feedback_db:
        return FeedbackSummary(n_responses=0, average_rating=0.0, nps=0.0)

    ratings = [f.rating for f in feedback_db]
    avg_rating = sum(ratings) / len(ratings)

    # NPS = %promotori - %detrattori (0-6 detrattori, 7-8 neutri, 9-10 promotori)
    detractors = sum(1 for r in ratings if r <= 6)
    promoters = sum(1 for r in ratings if r >= 9)
    n = len(ratings)
    nps = ((promoters - detractors) / n) * 100

    return FeedbackSummary(
        n_responses=n,
        average_rating=round(avg_rating, 2),
        nps=round(nps, 1),
    )


# ====================
# ENDPOINT NAVIGAZIONE
# ====================

@app.post("/navigation/info", response_model=NavigationInfo)
def navigation_info(data: NavigationRequest):
    building = data.building or "Corpo A"
    floor = data.floor if data.floor is not None else 2

    guidance = [
        "Entra dall'ingresso principale.",
        f"Segui le indicazioni per il {building}.",
        f"Sali al piano {floor}.",
        f"Cerca la segnaletica per il reparto {data.department}.",
    ]

    description = f"Informazioni di accesso per il reparto {data.department}."

    return NavigationInfo(
        department=data.department,
        description=description,
        building=building,
        floor=floor,
        guidance=guidance,
    )
