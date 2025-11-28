import streamlit as st
from datetime import date, datetime, timedelta
import base64
import os
import time
import pandas as pd


# ====================================================
# CONFIGURAZIONE PAGINA
# ====================================================

st.set_page_config(
    page_title="Boston Scientific Care",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ====================================================
# TEMA CHIARO FORZATO + COLORI PERSONALIZZATI
# ====================================================

st.markdown(
    """
    <style>
    :root, html[data-theme="dark"] {
        --primary-color: #004a80 !important;
        --background-color: #ffffff !important;
        --secondary-background-color: #e9f4ff !important;
        --text-color: #004a80 !important;
        --font: "sans serif" !important;
        color-scheme: light !important;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
    }

    /* Mostro l'header di Streamlit con sfondo trasparente,
       così si vede l'hamburger ma senza barra bianca brutta */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        box-shadow: none !important;
    }

    /* Nascondo solo il footer */
    footer {
        display: none !important;
    }

    /* Contenitore principale più compatto in alto */
    .block-container {
        padding-top: 0.1rem !important;
    }

    /* Top bar grigia, ABBASSATA per far vedere l'hamburger sopra */
    .bs-top-bar {
        margin-top: 2.2rem;  /* spazio sotto l'header con hamburger */
        z-index: 10;
        background: #f0f2f5;
        padding: 0.35rem 0.9rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
        border-radius: 0 0 10px 10px;
    }

    .bs-logo {
        height: 32px;
        filter: brightness(1.05);
        transition: transform 0.25s ease, filter 0.25s ease;
    }
    .bs-logo:hover {
        transform: scale(1.03);
        filter: brightness(1.2);
    }

    .bs-top-title-small {
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #004a80;
        opacity: 0.9;
    }
    .bs-top-title-main {
        font-size: 1.0rem;
        font-weight: 700;
        color: #004a80;
    }

    /* Logout stile link blu dentro la top bar */
    .logout-btn > button {
        background: transparent !important;
        color: #005c99 !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    .logout-btn > button:hover {
        text-decoration: underline !important;
        color: #003d70 !important;
    }

    /* Card generiche (background tabellare azzurro) */
    .bs-card {
        background-color: rgba(233, 244, 255, 0.95) !important;
        border-radius: 16px !important;
        padding: 1.0rem 1.1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
        border: 1px solid rgba(148, 181, 225, 0.6) !important;
    }

    .bs-section-title {
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        color: #005c99 !important;
        border-left: 4px solid #005c99 !important;
        padding-left: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Testi generali blu */
    h1, h2, h3, h4, h5, h6, label, p, span, div, li, th, td {
        color: #004a80 !important;
    }

    /* Pulsanti principali */
    .stButton > button {
        background-color: #ffffff !important;
        color: #ffffff !important;
        border-radius: 999px !important;
        border: none !important;
        padding: 0.4rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(0, 60, 120, 0.25) !important;
    }
    .stButton > button:hover {
        background-color: #E6F4FF !important;
        color: #ffffff !important;
    }

    /* Input fields */
    input, textarea, select, .stTextInput input, .stSelectbox div {
        background-color: #E6F4FF !important;
        border: 1px solid #bcd0e0 !important;
        color: #003a72 !important;
        border-radius: 8px !important;
    }

    /* Giorni della settimana in italiano (calendar) */
    .DayPicker-Weekday abbr {
        visibility: hidden !important;
    }
    .DayPicker-Weekday:nth-child(1)::after { content: "Lu"; }
    .DayPicker-Weekday:nth-child(2)::after { content: "Ma"; }
    .DayPicker-Weekday:nth-child(3)::after { content: "Me"; }
    .DayPicker-Weekday:nth-child(4)::after { content: "Gi"; }
    .DayPicker-Weekday:nth-child(5)::after { content: "Ve"; }
    .DayPicker-Weekday:nth-child(6)::after { content: "Sa"; }
    .DayPicker-Weekday:nth-child(7)::after { content: "Do"; }
    .DayPicker-Weekday {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #003b73 !important;
    }

    /* Footer */
    .bs-footer {
        font-size: 0.8rem;
        color: #446388;
        padding: 0.4rem 0 0.8rem 0;
        text-align: center;
    }

    /* Mobile: top bar più compatta */
    @media (max-width: 768px) {
        .bs-top-bar {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.3rem;
        }
        .bs-card {
            padding: 0.8rem !important;
            margin-bottom: 0.7rem !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ====================================================
# LOGO HELPER
# ====================================================

def get_logo_src():
    base_dir = os.path.dirname(__file__)
    local_path = os.path.join(base_dir, "bs_logo.png")
    if os.path.exists(local_path):
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            logo_base64 = base64.b64encode(data).decode()
            return f"data:image/png;base64,{logo_base64}"
        except Exception:
            return None
    return None

logo_src = get_logo_src()
if logo_src:
    logo_html = f'<img src="{logo_src}" class="bs-logo" alt="Boston Scientific logo" />'
else:
    logo_html = '<div class="bs-top-title-main">Boston Scientific</div>'


# ====================================================
# INIZIALIZZAZIONE SESSIONE / "DATABASE" IN MEMORIA
# ====================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_name"] = None
    st.session_state["user_email"] = None

if "current_patient_id" not in st.session_state:
    st.session_state["current_patient_id"] = None

if "patients" not in st.session_state:
    st.session_state["patients"] = []  # ogni elemento: dict{id, name, email, age, sex, phone}

if "appointments" not in st.session_state:
    st.session_state["appointments"] = []  # dict{id, patient_id, specialty, date_iso, reason, status}

if "feedbacks" not in st.session_state:
    st.session_state["feedbacks"] = []  # dict{patient_id, rating, comment, touchpoint}


# ====================================================
# FUNZIONI DI UTILITÀ (FAKE BACKEND IN MEMORIA)
# ====================================================

def register_patient(name: str, email: str, age: int, sex: str, phone: str | None = None):
    """Registra un nuovo paziente legato all'email di login."""
    patients = st.session_state["patients"]
    new_id = len(patients) + 1
    patient = {
        "id": new_id,
        "name": name,
        "email": (email or "").lower(),
        "age": age,
        "sex": sex,
        "phone": phone or "",
    }
    patients.append(patient)
    st.session_state["patients"] = patients
    return patient


def get_patients_by_email(email: str):
    """Restituisce tutti i pazienti associati a una certa email."""
    if not email:
        return []
    return [
        p for p in st.session_state["patients"]
        if p.get("email", "").lower() == email.lower()
    ]


def get_patient_by_id(pid: int):
    """Restituisce il paziente con id = pid, se esiste."""
    for p in st.session_state["patients"]:
        if p["id"] == pid:
            return p
    return None


def create_appointment(patient_id: int, specialty: str, d: date, reason: str | None = None):
    """Crea un nuovo appuntamento per un paziente."""
    appts = st.session_state["appointments"]
    new_id = len(appts) + 1
    appt = {
        "id": new_id,
        "patient_id": patient_id,
        "specialty": specialty,
        "date": d.isoformat(),
        "reason": reason,
        "status": "prenotata",
    }
    # ✅ AGGIUNGIAMO IL SINGOLO DIZIONARIO, NON LA LISTA INTERA
    appts.append(appt)
    st.session_state["appointments"] = appts
    return appt


def get_appointments_by_patient(pid: int):
    """Restituisce tutti gli appuntamenti validi per uno specifico paziente."""
    appts = st.session_state["appointments"]
    cleaned = []
    for a in appts:
        if isinstance(a, dict) and "patient_id" in a:
            if a["patient_id"] == pid:
                cleaned.append(a)
    return cleaned


def add_feedback(patient_id: int | None, rating: int, comment: str | None, touchpoint: str):
    """Aggiunge un feedback (NPS-like) al 'database' in memoria."""
    fbs = st.session_state["feedbacks"]
    fbs.append(
        {
            "patient_id": patient_id,
            "rating": rating,
            "comment": comment,
            "touchpoint": touchpoint,
        }
    )
    st.session_state["feedbacks"] = fbs


def feedback_summary():
    """Sintesi NPS-like dei feedback raccolti."""
    fbs = st.session_state["feedbacks"]
    if not fbs:
        return {
            "n_responses": 0,
            "average_rating": 0.0,
            "nps": 0.0,
        }
    ratings = [fb["rating"] for fb in fbs]
    avg = sum(ratings) / len(ratings)
    detractors = sum(1 for r in ratings if r <= 6)
    promoters = sum(1 for r in ratings if r >= 9)
    n = len(ratings)
    nps = ((promoters - detractors) / n) * 100
    return {
        "n_responses": len(ratings),
        "average_rating": round(avg, 2),
        "nps": round(nps, 1),
    }


def patient_summary(pid: int):
    """Riepilogo di paziente: dati, appuntamenti futuri/passati, numero feedback."""
    patient = get_patient_by_id(pid)
    if not patient:
        return None

    appts = get_appointments_by_patient(pid)
    upcoming = [a for a in appts if a.get("status") == "prenotata"]
    past = [a for a in appts if a.get("status") == "completata"]

    feedbacks = [f for f in st.session_state["feedbacks"] if f["patient_id"] == pid]

    return {
        "patient": patient,
        "upcoming_appointments": upcoming,
        "past_appointments": past,
        "feedback_count": len(feedbacks),
    }



# ====================================================
# LOGICA CHATBOT TRIAGE (DEMO)
# ====================================================

def chatbot_triage(symptom: str, severity: int, red_flags: list[str], free_text: str):
    level = "basso"
    message = "Sintomi lievi: contatta il tuo medico di base nei prossimi giorni per un confronto."

    if "dolore toracico" in red_flags or "mancanza di respiro" in red_flags:
        level = "alto"
        message = (
            "Segnali potenzialmente seri. In un contesto reale dovresti contattare subito "
            "un medico o il servizio di emergenza (112)."
        )
    elif severity >= 7:
        level = "medio-alto"
        message = (
            "Sintomi intensi. In un contesto reale sarebbe consigliabile un contatto rapido con il medico "
            "o la guardia medica."
        )
    elif "febbre alta" in red_flags:
        level = "medio"
        message = (
            "Febbre significativa. In un contesto reale dovresti monitorare e sentire il medico "
            "se non migliora."
        )

    dettaglio = ""
    if free_text.strip():
        dettaglio = " Dettagli forniti: \"" + free_text.strip()[:200] + "\"."

    return level, message + dettaglio


# ====================================================
# PIANO DI PREVENZIONE (DEMO)
# ====================================================

def generate_prevention_plan(age: int, sex: str, conditions: list[str] | None):
    recs: list[str] = []
    screenings: list[str] = []

    if age < 40:
        risk_profile = "basso"
        recs.append("Mantieni uno stile di vita attivo e una dieta equilibrata.")
    elif age < 60:
        risk_profile = "moderato"
        recs.append("Controlla regolarmente pressione, colesterolo e glicemia.")
        screenings.append("Check-up cardiovascolare ogni 1-2 anni.")
    else:
        risk_profile = "elevato"
        recs.append("Programma controlli regolari con il medico di riferimento.")
        screenings.append("Controlli cardiologici e metabolici almeno annuali.")

    if sex == "F":
        screenings.append("Valuta uno screening senologico e ginecologico secondo indicazione medica.")
    elif sex == "M":
        screenings.append("Valuta screening prostato-specifici secondo indicazione medica.")

    if conditions:
        if "diabete" in conditions:
            recs.append("Controlla regolarmente glicemia e programma visita oculistica periodica.")
        if "ipertensione" in conditions:
            recs.append("Monitora la pressione e riduci l'apporto di sale.")
        if "ipercolesterolemia" in conditions:
            recs.append("Riduci grassi saturi e segui dieta ipolipidica.")
        if "fumo" in conditions:
            recs.append("Valuta un programma di cessazione del fumo.")
        if "obesità" in conditions:
            recs.append("Consulta nutrizionista e valuta attività fisica regolare.")

    return risk_profile, recs, screenings


# ====================================================
# LOGIN PAGE (SE NON LOGGATO)
# ====================================================

if not st.session_state["logged_in"]:
    st.markdown(
        f"""
        <div class="bs-top-bar">
            <div style="display:flex; align-items:center; gap:14px;">
                {logo_html}
                <div>
                    <div class="bs-top-title-small">
                        Piattaforma di Coinvolgimento dei Pazienti
                    </div>
                    <div class="bs-top-title-main">
                        Boston Scientific Care
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="bs-card">', unsafe_allow_html=True)
    st.markdown('<div class="bs-section-title">🔐 Accesso paziente (demo)</div>', unsafe_allow_html=True)
    st.write("Simulazione di accesso con SPID o CIE (solo demo, nessun dato reale).")

    col_l, col_r = st.columns(2)
    with col_l:
        method = st.radio("Metodo di accesso", ["SPID", "CIE"])
    with col_r:
        email = st.text_input("Email (demo)", placeholder="nome.cognome@example.com")

    if st.button("Accedi"):
        val = (email or "").strip()
        if not val:
            st.warning("Inserisci una email per accedere.")
        elif "@" not in val or "." not in val:
            st.warning("Per questa demo inserisci una email valida (con @).")
        else:
            st.session_state["logged_in"] = True
            st.session_state["user_name"] = "Paziente demo"
            st.session_state["user_email"] = val.lower()
            st.success("Accesso eseguito (simulazione).")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ====================================================
# TOP BAR (UTENTE LOGGATO) CON LOGOUT
# ====================================================

top_container = st.container()
with top_container:
    st.markdown('<div class="bs-top-bar">', unsafe_allow_html=True)
    col_left, col_right = st.columns([2.50, 0.2])

    with col_left:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:14px;">
                {logo_html}
                <div>
                    <div class="bs-top-title-small">
                        Piattaforma di Coinvolgimento dei Pazienti
                    </div>
                    <div class="bs-top-title-main">
                        Boston Scientific Care
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_right:
        if st.button("Logout", key="logout_btn", help="Termina la sessione"):
            st.session_state.clear()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="margin-top:0.4rem; margin-bottom:0.6rem; padding:0.4rem 0.4rem;">
        Soluzione digitale per la continuità delle cure: accesso sicuro ai servizi,
        prenotazione delle visite con notifiche, monitoraggio clinico, programmi di prevenzione,
        raccolta strutturata dei feedback e assistenza virtuale tramite chatbot.
        Un ecosistema integrato di dispositivi e servizi ispirato agli standard Boston Scientific.
    </div>
    """,
    unsafe_allow_html=True,
)

# ====================================================
# SIDEBAR: PAZIENTE + NAVIGAZIONE
# ====================================================

with st.sidebar:
    st.markdown("### 👤 Paziente attivo")

    patients = st.session_state["patients"]
    user_email = st.session_state.get("user_email")

    filtered_patients = get_patients_by_email(user_email) if user_email else []

    if filtered_patients:
        if len(filtered_patients) == 1:
            current_patient_id = filtered_patients[0]["id"]
            st.session_state["current_patient_id"] = current_patient_id
            st.write(f"Profilo paziente: **{filtered_patients[0]['name']}**")
        else:
            options = [f"{p['id']} – {p['name']}" for p in filtered_patients]
            selected_label = st.selectbox("Seleziona paziente", options=options)
            current_patient_id = int(selected_label.split("–")[0].strip())
            st.session_state["current_patient_id"] = current_patient_id
    else:
        current_patient_id = None
        st.session_state["current_patient_id"] = None
        st.info(
            "Nessun profilo paziente associato a questo accesso.\n\n"
            "Vai su **Registrazione paziente** per creare il tuo profilo."
        )

    st.markdown("---")
    st.markdown("### 📂 Sezioni")

    pages_labels = [
        "🆕 Registra nuovo paziente",
        "📅 Prenotazione visite",
        "🩺 Monitoraggio post-visita",
        "🛡️ Piano di prevenzione",
        "💬 Valutazione esperienza",
        "🤖 Assistente sintomi",
        "🧭 Come raggiungere il reparto",
        "📄 Referti digitali",
        "📊 Area personale",
        "🏥 Area clinica (demo)",
        "💳 Pagamento visite",
]



    page_map = {
        "🆕 Registra nuovo paziente": "Registrazione paziente",
        "📅 Prenotazione visite": "Visite e prenotazioni",
        "🩺 Monitoraggio post-visita": "Monitoraggio paziente",
        "🛡️ Piano di prevenzione": "Prevenzione",
        "💬 Valutazione esperienza": "Feedback",
        "🤖 Assistente sintomi": "Chatbot sintomi",
        "🧭 Come raggiungere il reparto": "Navigazione ospedale",
        "📄 Referti digitali": "Referti digitali",
        "📊 Area personale": "Dashboard paziente",
        "🏥 Area clinica (demo)": "Dashboard clinica",
        "💳 Pagamento visite": "Pagamenti",
}

    page_label = st.radio("", pages_labels)
    page = page_map[page_label]


# ====================================================
# LAYOUT PRINCIPALE
# ====================================================

left_spacer, main_col, right_spacer = st.columns([0.03, 0.94, 0.03])

with main_col:

    # 1) REGISTRAZIONE PAZIENTE
    if page == "Registrazione paziente":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">👤 Nuovo paziente</div>', unsafe_allow_html=True)

        login_email = st.session_state.get("user_email")
        st.caption(f"Accesso corrente (SPID/CIE demo): {login_email}")

        with st.form("register_patient"):
            name = st.text_input("Nome e cognome")
            phone = st.text_input("Numero di telefono (per SMS di notifica)", placeholder="+39...")
            age = st.number_input("Età", min_value=0, max_value=120, value=40)
            sex = st.selectbox("Sesso", ["M", "F", "Altro"])
            submitted = st.form_submit_button("Registra paziente")

        if submitted:
            if not name:
                st.warning("Inserisci almeno il nome.")
            else:
                patient = register_patient(
                    name=name,
                    email=login_email,
                    age=int(age),
                    sex=sex,
                    phone=phone,
                )
                st.success(f"Paziente registrato con ID {patient['id']}.")
                st.info("Questo profilo è legato all'accesso corrente (email).")

        st.markdown('</div>', unsafe_allow_html=True)

    # 2) VISITE E PRENOTAZIONI
    elif page == "Visite e prenotazioni":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">📅 Prenotazione visite</div>', unsafe_allow_html=True)
        st.write("Prenota una visita, scegli data e fascia oraria e configura le notifiche di preparazione.")
        


        if not current_patient_id:
            st.info("Seleziona o registra un paziente per prenotare una visita.")
        else:
            current_patient = get_patient_by_id(current_patient_id)
            patient_name = current_patient["name"] if current_patient else "Gentile paziente"

            with st.form("create_appointment"):
                col1, col2 = st.columns(2)
                with col1:
                    specialty = st.selectbox(
                        "Specialità",
                        [
                            "Cardiologia",
                            "Ortopedia",
                            "Neurologia",
                            "Medicina generale",
                            "Oncologia",
                            "Prelievo sangue",
                            "Ecografia addome",
                            "Altro",
                        ],
                    )
                with col2:
                    appt_date = st.date_input("Data appuntamento (gg/mm/aaaa)", value=date.today())
                    if appt_date:
                        st.caption(f"📅 Data selezionata: {appt_date.strftime('%d/%m/%Y')}")

                time_slot = st.selectbox(
                    "Fascia oraria",
                    [
                        "08:30–09:30",
                        "09:30–10:30",
                        "10:30–11:30",
                        "11:30–12:30",
                        "14:00–15:00",
                        "15:00–16:00",
                        "16:00–17:00",
                    ],
                )

                reason = st.text_area("Motivo della visita (facoltativo)")

                st.markdown("#### 🔔 Notifiche di preparazione")
                fasting = st.checkbox("Promemoria: digiuno 8 ore prima (se pertinente)")
                prep_drugs = st.checkbox("Promemoria: verifica farmaci da sospendere con il medico")
                sms_reminder = st.checkbox("Promemoria SMS il giorno prima della visita")

                submit_appt = st.form_submit_button("Prenota visita")

            if submit_appt:
                appt = create_appointment(
                    patient_id=current_patient_id,
                    specialty=specialty,
                    d=appt_date,
                    reason=reason or None,
                )
                st.success(
                    f"Visita prenotata per il {appt_date.strftime('%d/%m/%Y')} "
                    f"nella fascia {time_slot} (demo)."
                )
                if fasting or prep_drugs or sms_reminder:
                    note = []
                    if fasting:
                        note.append("digiuno pre-esame")
                    if prep_drugs:
                        note.append("farmaci da verificare")
                    if sms_reminder:
                        note.append("SMS promemoria")
                    st.info(
                        "Notifiche attivate (demo): "
                        + ", ".join(note)
                        + ". Nella realtà verrebbero inviati SMS / notifiche push."
                    )

            st.subheader("Tutte le visite del paziente")
            appts = get_appointments_by_patient(current_patient_id)
            if appts:
                st.table(appts)
            else:
                st.write("Nessuna visita ancora registrata.")

        st.markdown('</div>', unsafe_allow_html=True)

    # 3) MONITORAGGIO PAZIENTE
    elif page == "Monitoraggio paziente":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">🩺 Monitoraggio post-visita/intervento</div>', unsafe_allow_html=True)

        if not current_patient_id:
            st.info("Seleziona un paziente per registrare un monitoraggio.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                days = st.number_input("Giorni dalla procedura", min_value=0, max_value=60, value=1)
                pain = st.slider("Dolore (0-10)", 0, 10, 3)
            with col2:
                breath = st.checkbox("Fiato corto", value=False)
                fever = st.checkbox("Febbre", value=False)
            notes = st.text_area("Note aggiuntive (facoltativo)")

            if st.button("Invia check-in"):
                risk_points = 0
                if pain >= 7:
                    risk_points += 2
                elif pain >= 4:
                    risk_points += 1
                if breath:
                    risk_points += 2
                if fever:
                    risk_points += 1
                if days <= 2:
                    risk_points += 1

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

                st.subheader("Risultato triage (demo)")
                st.write(f"Livello: **{triage}**")
                st.write(message)
                st.info(action)

        st.markdown('</div>', unsafe_allow_html=True)

    
    # 4) PREVENZIONE – SOLO CONDIZIONI NOTE
        # 4) PREVENZIONE – SOLO CONDIZIONI NOTE
    elif page == "Prevenzione":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">🛡️ Piano di prevenzione personalizzato</div>', unsafe_allow_html=True)

        st.write(
            "In questa sezione puoi selezionare eventuali condizioni note del paziente. "
            "Il sistema genera un piano di prevenzione basato esclusivamente su queste informazioni "
            "e su parametri di riferimento standard (età e sesso non vengono richiesti in questa demo)."
        )

        # ✅ SOLO CONDIZIONI NELLA UI
        conditions = st.multiselect(
            "Condizioni note del paziente",
            ["ipertensione", "diabete", "ipercolesterolemia", "fumo", "obesità"],
        )

        if st.button("Genera piano di prevenzione"):
            # ✅ Valori interni di default (non mostrati in UI)
            default_age = 50
            default_sex = "Altro"

            risk_profile, recs, screenings = generate_prevention_plan(
                int(default_age),
                default_sex,
                conditions or [],
            )

            st.subheader(f"Profilo di rischio: **{risk_profile}**")
            st.write("**Raccomandazioni:**")
            for r in recs:
                st.markdown(f"- {r}")

            st.write("**Screening suggeriti:**")
            for s in screenings:
                st.markdown(f"- {s}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 5) FEEDBACK
    elif page == "Feedback":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">💬 Feedback del paziente</div>', unsafe_allow_html=True)

        with st.form("feedback_form"):
            rating = st.slider("Quanto consiglieresti l'ospedale ad un amico? (0-10)", 0, 10, 8)
            touchpoint = st.selectbox(
                "Esperienza a cui si riferisce il feedback",
                ["visita", "ricovero", "pronto soccorso", "altro"],
            )
            comment = st.text_area("Commento (facoltativo)")
            submit_fb = st.form_submit_button("Invia feedback")

        if submit_fb:
            add_feedback(
                patient_id=current_patient_id,
                rating=int(rating),
                comment=comment or None,
                touchpoint=touchpoint,
            )
            st.success("Grazie, il feedback è stato registrato.")

        st.subheader("Sintesi generale soddisfazione")
        summary_fb = feedback_summary()
        st.write(f"Numero di risposte: **{summary_fb['n_responses']}**")
        st.write(f"Rating medio: **{summary_fb['average_rating']} / 10**")
        st.write(f"NPS stimato: **{summary_fb['nps']}**")

        st.markdown('</div>', unsafe_allow_html=True)

    # 6) CHATBOT SINTOMI
    elif page == "Chatbot sintomi":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">🤖 Chatbot sintomi (demo)</div>', unsafe_allow_html=True)

        st.write(
            "Chatbot dimostrativo per malesseri lievi. "
            "Non sostituisce il medico e non fornisce indicazioni diagnostiche reali."
        )

        symptom = st.selectbox(
            "Che tipo di sintomo senti principalmente?",
            [
                "Mal di testa",
                "Dolore addominale",
                "Dolore al petto",
                "Fiato corto",
                "Febbre",
                "Stanchezza",
                "Altro",
            ],
        )
        severity = st.slider("Quanto è intenso (0-10)?", 0, 10, 5)
        red_flags = st.multiselect(
            "Hai anche qualcuno di questi sintomi?",
            ["dolore toracico", "mancanza di respiro", "svenimento", "febbre alta"],
        )
        free_text = st.text_area("Descrivi meglio cosa senti (facoltativo)")

        if st.button("Analizza sintomi"):
            level, message = chatbot_triage(symptom, severity, red_flags, free_text)
            st.subheader(f"Livello di urgenza stimato (demo): {level}")
            st.write(message)
            st.warning(
                "Questa funzione è solo dimostrativa e NON sostituisce il parere del medico, "
                "né fornisce indicazioni per diagnosi o terapia."
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # 7) NAVIGAZIONE OSPEDALE
    elif page == "Navigazione ospedale":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">🧭 Come arrivare al reparto</div>', unsafe_allow_html=True)

        department = st.text_input("Reparto (es: Cardiologia, Ortopedia...)")
        building = st.text_input("Corpo/Edificio (facoltativo)", value="")
        floor = st.number_input("Piano (facoltativo, -1 a 10)", min_value=-1, max_value=10, value=2)

        if st.button("Genera indicazioni"):
            if not department:
                st.warning("Inserisci almeno il nome del reparto.")
            else:
                building_final = building or "Corpo A"
                floor_final = floor
                guidance = [
                    "Entra dall'ingresso principale.",
                    f"Segui le indicazioni per il {building_final}.",
                    f"Sali al piano {floor_final}.",
                    f"Cerca la segnaletica per il reparto {department}.",
                ]
                st.subheader(f"Reparto: {department}")
                st.write(f"Edificio: **{building_final}**, piano **{floor_final}**")
                st.write("Indicazioni:")
                for step in guidance:
                    st.markdown(f"- {step}")

        st.markdown('</div>', unsafe_allow_html=True)

        # 8) REFERTI DIGITALI
    elif page == "Referti digitali":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">📄 Referti digitali (demo)</div>', unsafe_allow_html=True)

        st.write(
            "Sezione dimostrativa per la gestione dei referti clinici. "
            "Il paziente può caricare un referto in PDF o immagine, oppure simulare "
            "la scansione tramite fotocamera. In questa demo nessun file viene salvato "
            "su sistemi esterni."
        )

        col1, col2 = st.columns(2)

        # Colonna sinistra: caricamento file
        with col1:
            st.subheader("Carica referto esistente")
            uploaded_files = st.file_uploader(
                "Carica uno o più referti (PDF, JPG, PNG)",
                type=["pdf", "jpg", "jpeg", "png"],
                accept_multiple_files=True,
            )

            if uploaded_files:
                st.success(f"Hai caricato {len(uploaded_files)} referto/i (demo).")

                # Mostro i file caricati in tabella (nome + tipo + dimensione)
                rows_upload = []
                for f in uploaded_files:
                    size_kb = getattr(f, "size", None)
                    if size_kb is not None:
                        size_kb = round(size_kb / 1024, 1)
                        size_str = f"{size_kb} KB"
                    else:
                        size_str = "n.d."

                    ext = os.path.splitext(f.name)[1].lower().replace(".", "").upper()
                    if ext == "":
                        ext = "FILE"

                    rows_upload.append(
                        {
                            "Tipo": f"📄 {ext}",
                            "Nome file": f.name,
                            "Dimensione": size_str,
                        }
                    )

                if rows_upload:
                    df_upload = pd.DataFrame(rows_upload)
                    st.dataframe(df_upload, use_container_width=True)

                st.info(
                    "In una versione enterprise reale, i referti verrebbero "
                    "indicizzati e collegati automaticamente alla cartella clinica del paziente."
                )

        # Colonna destra: finta scansione da fotocamera
        with col2:
            st.subheader("Scansiona referto (fotocamera)")
            st.write(
                "Simulazione della scansione di un referto cartaceo tramite fotocamera "
                "dello smartphone o tablet."
            )
            if st.button("Scansiona referto (demo)"):
                with st.spinner("Analisi automatica del referto in corso..."):
                    time.sleep(1.5)

                st.success(
                    "Referto scansionato (demo). I principali dati clinici sono stati "
                    "riconosciuti e associati al profilo paziente."
                )
                st.caption(
                    "Funzionalità dimostrativa: nessuna analisi reale viene eseguita in questa versione."
                )

        # Lista referti già presenti (demo) in forma tabellare
        st.markdown("---")
        st.subheader("Referti presenti in archivio (demo)")

        st.caption(
            "Elenco simulato di referti già digitalizzati e collegati al profilo paziente. "
            "In una versione reale, questi dati verrebbero letti dal sistema informativo ospedaliero."
        )

        referti_demo = [
            {
                "data": "12/11/2024",
                "esame": "ECG di controllo",
                "struttura": "Cardiologia – Ospedale Demo",
                "stato": "Referto disponibile",
            },
            {
                "data": "03/10/2024",
                "esame": "Rx torace",
                "struttura": "Radiologia – Ospedale Demo",
                "stato": "Referto disponibile",
            },
            {
                "data": "18/09/2024",
                "esame": "Analisi sangue completo",
                "struttura": "Laboratorio analisi – Ospedale Demo",
                "stato": "Referto disponibile",
            },
        ]

        df_referti = pd.DataFrame(
            [
                {
                    "Tipo": "📄 PDF",
                    "Esame": r["esame"],
                    "Struttura / reparto": r["struttura"],
                    "Data": r["data"],
                    "Stato referto": r["stato"],
                }
                for r in referti_demo
            ]
        )

        st.dataframe(df_referti, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


    # 9) DASHBOARD PAZIENTE
    elif page == "Dashboard paziente":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">📊 Dashboard paziente</div>', unsafe_allow_html=True)

        if not current_patient_id:
            st.info("Seleziona o registra un paziente per vedere la dashboard.")
        else:
            summary = patient_summary(current_patient_id)
            if summary:
                            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Dati paziente")

                patient = summary["patient"]

                # Creiamo una piccola tabella anagrafica elegante
                rows = [
                    {"Campo": "ID paziente", "Valore": patient.get("id", "-")},
                    {"Campo": "Nome", "Valore": patient.get("name", "-")},
                    {"Campo": "Email", "Valore": patient.get("email", "-")},
                    {"Campo": "Età", "Valore": patient.get("age", "-")},
                    {"Campo": "Sesso", "Valore": patient.get("sex", "-")},
                    {"Campo": "Telefono", "Valore": patient.get("phone", "-")},
                ]

                df_patient = pd.DataFrame(rows)

                st.table(df_patient)

            with col2:
                st.subheader("Sintesi relazione")
                st.metric("Feedback registrati", summary.get("feedback_count", 0))
                st.write("Appuntamenti futuri:", len(summary.get("upcoming_appointments", [])))
                st.write("Appuntamenti passati:", len(summary.get("past_appointments", [])))

                st.markdown("### 📡 Dati da dispositivo / wearable (simulazione)")
                now = datetime.now()
                last_sync = (now - timedelta(hours=5)).strftime("%d/%m/%Y %H:%M")
                st.write(f"Ultima trasmissione: **{last_sync}**")
                colD1, colD2, colD3 = st.columns(3)
                with colD1:
                    st.metric("Frequenza cardiaca media", "72 bpm")
                with colD2:
                    st.metric("Saturazione O₂", "97 %")
                with colD3:
                    st.metric("Episodi registrati (30 gg)", "0 aritmie rilevanti")

                st.caption(
                    "Dati a solo scopo dimostrativo: in un ambiente reale, i parametri sarebbero "
                    "sincronizzati con il device impiantabile o wearable certificato."
                )

                st.subheader("Prossimi appuntamenti")
                if summary.get("upcoming_appointments"):
                    st.table(summary["upcoming_appointments"])
                else:
                    st.write("Nessun appuntamento prenotato.")

                st.subheader("Appuntamenti passati")
                past_appts = summary.get("past_appointments", [])
                if past_appts:
                    st.table(past_appts)
                else:
                    st.write("Nessun appuntamento passato registrato.")

        st.markdown('</div>', unsafe_allow_html=True)

    # 10) DASHBOARD CLINICA
    elif page == "Dashboard clinica":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">🏥 Dashboard clinica (demo)</div>', unsafe_allow_html=True)

        st.write(
            "Vista sintetica pensata per direzione sanitaria e clinici: panoramica pazienti, "
            "appuntamenti e soddisfazione. I dati sono basati sulle interazioni all’interno di questa demo."
        )

        all_patients = st.session_state["patients"]
        st.write(f"**Pazienti attivi sulla piattaforma (demo):** {len(all_patients)}")

        fb_sum = feedback_summary()
        colA, colB, colC = st.columns(3)
        with colA:
            st.metric("Feedback raccolti", fb_sum["n_responses"])
        with colB:
            st.metric("Rating medio", f"{fb_sum['average_rating']} / 10")
        with colC:
            st.metric("NPS stimato", fb_sum["nps"])

        rows = []
        max_patients = min(len(all_patients), 10)
        for p in all_patients[:max_patients]:
            pid = p["id"]
            s = patient_summary(pid)
            if not s:
                continue
            upc = len(s.get("upcoming_appointments", []))
            past = len(s.get("past_appointments", []))
            fb = s.get("feedback_count", 0)
            rows.append({
                "ID paziente": pid,
                "Nome": p.get("name", ""),
                "Visite future": upc,
                "Visite passate": past,
                "Feedback registrati": fb,
            })

        if rows:
            st.subheader("Pazienti (estratto demo)")
            st.table(rows)
        else:
            st.write("Nessun dato paziente disponibile per la sintesi.")

        st.caption(
            "In una versione enterprise reale, questa dashboard potrebbe integrarsi con il sistema informativo "
            "ospedaliero (HIS), i registry dei device e i sistemi di business intelligence."
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # 11) PAGAMENTI
    elif page == "Pagamenti":
        st.markdown('<div class="bs-card">', unsafe_allow_html=True)
        st.markdown('<div class="bs-section-title">💳 Pagamento visite</div>', unsafe_allow_html=True)

        st.write(
            "Sezione dimostrativa per il pagamento digitale delle visite. "
            "I prezzi sono simulati a scopo di esempio."
        )

        if not current_patient_id:
            st.info("Seleziona un paziente per vedere le visite da pagare.")
        else:
            appts = get_appointments_by_patient(current_patient_id) or []
            future_appts = []
            today = date.today()
            for a in appts:
                raw = a.get("date", "")
                try:
                    d = datetime.fromisoformat(raw).date()
                    if d >= today:
                        future_appts.append(a)
                except Exception:
                    pass

            if not future_appts:
                st.write("Non ci sono visite future da pagare.")
            else:
                for a in future_appts:
                    spec = a.get("specialty", "Visita")
                    raw = a.get("date", "")
                    try:
                        d = datetime.fromisoformat(raw)
                        nice_date = d.strftime("%d/%m/%Y")
                    except Exception:
                        nice_date = raw

                    base_price = 60
                    if "Cardio" in spec or "Cardiologia" in spec:
                        base_price = 90
                    elif "Oncologia" in spec:
                        base_price = 120
                    elif "Prelievo" in spec:
                        base_price = 30

                    st.markdown(f"**ID {a.get('id')} – {spec} ({nice_date})**")
                    st.write(f"Importo: **€ {base_price}**")

                    metodo = st.selectbox(
                        "Metodo di pagamento",
                        ["Carta di credito", "Bancomat", "Satispay", "App bancaria"],
                        key=f"pay_method_{a.get('id')}",
                    )
                    if st.button("Paga ora", key=f"pay_btn_{a.get('id')}"):
                        st.success(
                            f"Pagamento simulato completato per la visita {a.get('id')} "
                            f"con {metodo} (demo: nessuna transazione reale)."
                        )
                    st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div class="bs-footer">
            Concept demo – non è un dispositivo medico né sostituisce il giudizio clinico.<br/>
            © 2024 Boston Scientific Corporation o sue affiliate. Tutti i diritti privacy riservati.
        </div>
        """,
        unsafe_allow_html=True,
    )
