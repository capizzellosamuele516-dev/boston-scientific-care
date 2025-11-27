import streamlit as st
import requests
from datetime import date, datetime, timedelta
import base64
import os

# URL del backend FastAPI
BACKEND_URL = "http://127.0.0.1:9000"

st.set_page_config(
    page_title="Boston Scientific Care",
    page_icon="bs_logo.png",  ###icona della pagina
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# Funzione LOGOUT (enterprise)
# =========================

def do_logout():
    st.session_state["logged_in"] = False
    st.session_state["user_name"] = None
    st.session_state["user_email"] = None
    st.session_state["current_patient_id"] = None
    st.session_state["auth_token"] = None
    st.rerun()

def reset_app_state():
    # Reset totale, come "svuotare la cache" della sessione Streamlit
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# =========================
# CSS – versione enterprise stabile
# =========================

custom_css = """
<style>


/* =============== */
/* HAMBURGER A SINISTRA */
/* =============== */

/* Header trasparente, niente barra bianca */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    box-shadow: none !important;
    height: 40px !important;
    position: relative !important;
    z-index: 2 !important;
}

/* Hamburger (menu principale) a sinistra, sempre visibile */
header[data-testid="stHeader"] div[role="button"] {
    position: absolute !important;
    left: 10px !important;
    top: 7px !important;
    z-index: 9999 !important;
}

header[data-testid="stHeader"] div[role="button"] svg {
    width: 26px !important;
    height: 26px !important;
    color: white !important;
}

/* Niente testo vicino all'hamburger */
header[data-testid="stHeader"] div[role="button"] span {
    display: none !important;
}

/* =============== */
/* “SCHIERARE” → ICONCINA ⋯ A DESTRA */
/* =============== */

/* Sposta la deploy button (Schierare + ⋮) a destra, vicino a Logout */
header[data-testid="stHeader"] [data-testid="stDeployButton"] button span {
    display: none !important;
    right: 110px !important;  /* 🔧 avvicina/allontana rispetto al Logout */
    top: 7px !important;
    z-index: 9999 !important;
}

/* Nasconde testo e icone interne originali */
header[data-testid="stHeader"] [data-testid="stDeployButton"] button span,
header[data-testid="stHeader"] [data-testid="stDeployButton"] button svg {
    display: none !important;
}

/* Trasforma il bottone in una piccola icona ⋯ */
header[data-testid="stHeader"] [data-testid="stDeployButton"] button {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    width: auto !important;
    min-width: auto !important;
    padding: 0 !important;
    cursor: pointer;
}

/* Iconcina effettiva (puoi cambiare contenuto: "⋯" → "⚙" se preferisci) */
header[data-testid="stHeader"] [data-testid="stDeployButton"] button::after {
    content: "⋯";  /* cambia in "⚙" se ti piace di più */
    font-size: 20px;
    color: white;
    font-weight: 700;
    display: inline-block;
    padding: 0 4px;
}

/* =============== */
/* TOP BAR BLU ATTACCATA SU */
/* =============== */

.bs-top-bar {
    margin-top: 0 !important;
}

/* NASCONDI SOLO IL TASTO "SCHIERARE" DELLA TOOLBAR */
header[data-testid="stHeader"] button[title^="Schierare"],
header[data-testid="stHeader"] button[aria-label^="Schierare"] {
    display: none !important;
}


/* Sfondo principale app */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e6f4ff 0%, #f5fbff 45%, #ffffff 100%) !important;
}

/* Contenuto principale: pochissimo spazio sopra */
.block-container {
    padding-top: 0.1rem !important;
}

/* Top Bar */
.bs-top-bar {
    position: sticky;
    top: 0;
    z-index: 10;
    background: linear-gradient(90deg, #dcdcdc 0%, #e8e8e8 50%, #f3f3f3 100%);
    padding: 0.25rem 0.9rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    border-radius: 0 0 10px 10px;
}
.bs-top-left {
    display: flex;
    align-items: center;
    gap: 14px;
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
    color: #005c99;
    opacity: 0.9;
}
.bs-top-title-main {
    font-size: 1.0rem;
    font-weight: 600;
    color: #00447a;
}
.bs-top-right-text {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
    color: #e6f4ff;
    font-size: 0.8rem;
}
.bs-top-badge {
    font-size: 0.7rem;
    padding: 0.1rem 0.4rem;
    border-radius: 999px;
    border: 1px solid rgba(230,244,255,0.7);
    opacity: 0.9;
}

/* Header descrittivo */
.bs-main-header {
    margin-top: 0.4rem;
    margin-bottom: 0.6rem;
    padding: 0.4rem 0.4rem;
    color: #004065;
    font-size: 0.9rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f0f6ff !important;
    border-right: 1px solid #c4d8f5;
}

/* Card generica */
.bs-card {
    background-color: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    padding: 1.0rem 1.1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    border: 1px solid rgba(148, 181, 225, 0.35);
}
.bs-section-title {
    font-size: 1.02rem;
    font-weight: 700;
    color: #005c99;
    border-left: 4px solid #005c99;
    padding-left: 0.5rem;
    margin-bottom: 0.5rem;
}

/* Pulsanti */
.stButton > button {
    background-color: #005c99 !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    border: none !important;
    padding: 0.4rem 1.2rem !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(0, 60, 120, 0.25);
}
.stButton > button:hover {
    background-color: #00497a !important;
}

/* Testo input */
input, textarea {
    color: #003b73 !important;
}

/* Giorni della settimana in italiano (solo etichette grafiche) */
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
    font-size: 0.78rem;
    color: #446388;
    padding: 0.4rem 0 0.8rem 0;
    text-align: center;
}

/* Mobile */
@media (max-width: 768px) {
    .bs-top-bar {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.3rem;
    }
    .bs-card {
        padding: 0.8rem;
        margin-bottom: 0.7rem;
    }
}

/* ============================================
   ADATTAMENTO PER TELEFONO (MOBILE)
   Evita sovrapposizione hamburger / tre puntini
   con la barra grigia personalizzata
============================================ */

/* Header Streamlit: trasparente, altezza fissa, icone tutte visibili */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    box-shadow: none !important;
    height: 48px !important;
    display: flex;
    align-items: center;
    padding: 0 8px;
    z-index: 100 !important;
}

/* ===== HEADER STREAMLIT: TRASPARENTE, NON TOCCO L'ALTEZZA ===== */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    box-shadow: none !important;
}

/* colore icone (hamburger + tre puntini) */
header[data-testid="stHeader"] svg {
    color: #005c99 !important;  /* blu carino, visibile su grigio/bianco */
}

/* ===== MOBILE: SPOSTO SOLO LA BARRA GRIGIA PIÙ IN BASSO ===== */
@media (max-width: 768px) {

    /* sposto la top-bar grigia un pochino più giù
       così NON si sovrappone alle icone dell'header */
    .bs-top-bar {
        margin-top: 2.8rem !important;   /* se serve, prova 3.2rem o 2.4rem */
        padding: 0.3rem 0.7rem !important;
    }

    /* riduco leggermente logo e testi per farli stare meglio */
    .bs-logo {
        height: 26px !important;
    }

    .bs-top-title-small {
        font-size: 0.7rem !important;
    }

    .bs-top-title-main {
        font-size: 0.9rem !important;
    }
}


</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

st.markdown(custom_css, unsafe_allow_html=True)

# =========================
# Logo helper
# =========================

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
    logo_html = '<span class="bs-top-title-main">Boston Scientific</span>'

# =========================
# Top bar + Logout enterprise
# =========================

st.markdown(
    f"""
    <div class="bs-top-bar">
        <div class="bs-top-left">
            {logo_html}
            <div>
                <div class="bs-top-title-small">
                    Patient Engagement Platform
                </div>
                <div class="bs-top-title-main">
                   Boston Scientific Care
                </div>
            </div>
        </div>
        <div class="bs-top-right-text">
            <span>Clinical Demo User</span>
            <div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Logout reale, allineato a destra sotto la top bar
logout_col_left, logout_col_right = st.columns([0.80, 0.10])
with logout_col_right:
    if st.button("Logout", key="logout_real"):
        do_logout()

st.markdown(
    """
    <div class="bs-main-header">
        Soluzione digitale per la continuità delle cure: accesso sicuro ai servizi,
        prenotazione delle visite con notifiche, monitoraggio clinico, programmi di prevenzione,
        raccolta strutturata dei feedback e assistenza virtuale tramite chatbot.
        Un ecosistema integrato di dispositivi e servizi ispirato agli standard Boston Scientific.
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# Session state base
# =========================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_name"] = None
    st.session_state["user_email"] = None
if "last_registered_phone" not in st.session_state:
    st.session_state["last_registered_phone"] = ""
if "current_patient_id" not in st.session_state:
    st.session_state["current_patient_id"] = None
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None


# =========================
# Funzioni utilità backend
# =========================

def get_auth_headers():
    headers = {}
    token = st.session_state.get("auth_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def get_auth_headers():
    """
    Restituisce sempre un header Authorization finto,
    così l'OAuth2PasswordBearer/HTTPBearer del backend è soddisfatto.
    """
    return {"Authorization": "Bearer demo-token"}

def safe_get(path: str, params=None):
    try:
        headers = get_auth_headers()
        r = requests.get(
            f"{BACKEND_URL}{path}",
            params=params,
            headers=headers,
            timeout=5,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        st.error(f"Errore backend {r.status_code} su {path}: {detail}")
        return None
    except Exception as e:
        st.error(f"Errore di connessione al backend: {e}")
        return None

def safe_post(path: str, json=None):
    try:
        headers = get_auth_headers()
        r = requests.post(
            f"{BACKEND_URL}{path}",
            json=json,
            headers=headers,
            timeout=5,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        st.error(f"Errore backend {r.status_code} su {path}: {detail}")
        return None
    except Exception as e:
        st.error(f"Errore di connessione al backend: {e}")
        return None
    
# =========================
# Chatbot triage (demo logica)
# =========================

def chatbot_triage(symptom: str, severity: int, red_flags: list, free_text: str):
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

# =========================
# SMS di preparazione esame – mock
# =========================

def generate_preparation_sms(patient_name: str, specialty: str, appt_date: date, time_slot: str):
    name_part = patient_name or "Gentile paziente"
    date_str = appt_date.strftime("%d/%m/%Y")
    base = f"{name_part}, promemoria visita di {specialty.lower()} il {date_str} nella fascia {time_slot} presso Ospedale Demo."

    if "Prelievo" in specialty:
        extra = " Presentati a digiuno da almeno 8 ore e porta tessera sanitaria e documento di identità."
    elif "Cardio" in specialty or "Cardiologia" in specialty:
        extra = " Porta elenco aggiornato dei farmaci e l’ultimo referto cardiologico se disponibile."
    elif "Ecografia" in specialty or "addome" in specialty:
        extra = " Segui le indicazioni di preparazione ricevute (es. vescica piena o digiuno, se previsto)."
    elif "Oncologia" in specialty:
        extra = " Ti ricordiamo di arrivare con qualche minuto di anticipo per la fase di accettazione."
    else:
        extra = " Arriva con qualche minuto di anticipo per l’accettazione."

    return base + extra

# =========================
# Sidebar: paziente + navigazione
# =========================

with st.sidebar:
    st.markdown("### 👤 Paziente attivo")

    patients = []
    user_email = st.session_state.get("user_email")

    # ✅ Chiama il backend SOLO se sei loggato
    if st.session_state.get("logged_in"):
        patients = [
    {
        "id": 1,
        "name": "Paziente Demo",
        "email": st.session_state.get("user_email", "demo@example.com"),
        "age": 45,
        "sex": "M",
    }
]

    else:
        st.info("Effettua l’accesso per caricare il tuo profilo paziente.")

    filtered_patients = []
    if user_email and patients:
        filtered_patients = [
            p for p in patients
            if str(p.get("email", "")).lower() == user_email
        ]
    

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
        "🆕 Registrazione paziente",
        "📅 Visite e prenotazioni",
        "🩺 Monitoraggio paziente",
        "🛡️ Prevenzione",
        "💬 Feedback",
        "🤖 Chatbot sintomi",
        "🧭 Navigazione ospedale",
        "📊 Dashboard paziente",
        "🏥 Dashboard clinica (demo)",
        "💳 Pagamenti visite",
    ]

    page_map = {
        "🆕 Registrazione paziente": "Registrazione paziente",
        "📅 Visite e prenotazioni": "Visite e prenotazioni",
        "🩺 Monitoraggio paziente": "Monitoraggio paziente",
        "🛡️ Prevenzione": "Prevenzione",
        "💬 Feedback": "Feedback",
        "🤖 Chatbot sintomi": "Chatbot sintomi",
        "🧭 Navigazione ospedale": "Navigazione ospedale",
        "📊 Dashboard paziente": "Dashboard paziente",
        "🏥 Dashboard clinica (demo)": "Dashboard clinica",
        "💳 Pagamenti visite": "Pagamenti",
    }

    page_label = st.radio("", pages_labels)
    page = page_map[page_label]

    st.markdown("---")
    if st.button("🔄 Reset app / cache", use_container_width=True):
        reset_app_state()

# =========================
# Layout principale
# =========================

left_spacer, main_col, right_spacer = st.columns([0.04, 0.92, 0.04])

with main_col:

    left_spacer, main_col, right_spacer = st.columns([0.04, 0.92, 0.04])

with main_col:

    # =========================
    # LOGIN – SPID/CIE (demo)
    # =========================
    if not st.session_state["logged_in"]:

        st.markdown("## 🔐 Accesso paziente")
        st.write("Simulazione di accesso con SPID/CIE (demo).")

        col1, col2 = st.columns(2)
        with col1:
            method = st.radio("Metodo di accesso", ["SPID", "CIE"])
        with col2:
            cf_or_email = st.text_input(
                "Email (demo)",
                placeholder="nome.cognome@example.com"
            )

        # 👉 inizializziamo sempre una variabile locale sicura
        input_value = cf_or_email.strip()

        if st.button("Accedi"):
            if not input_value:
                st.warning("Inserisci una email per accedere.")
            elif "@" not in input_value or "." not in input_value:
                st.warning("Inserisci una email valida (con @).")
            else:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = "Paziente demo"
                st.session_state["user_email"] = input_value.lower()
                # se usi il token per il backend:
                # st.session_state["auth_token"] = "demo-token"
                st.success("Accesso eseguito (simulazione).")
                st.rerun()

        # fermiamo il resto della pagina finché non hai fatto login
        st.stop()

    
   # 1) REGISTRAZIONE PAZIENTE
    if page == "Registrazione paziente":
        ...


    # 1) REGISTRAZIONE PAZIENTE
    if page == "Registrazione paziente":
        with st.container():
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
                    payload = {
                        "name": name,
                        "email": login_email,
                        "age": int(age),
                        "sex": sex,
                    }
                    res = safe_post("/patients", json=payload)
                    st.session_state["last_registered_phone"] = phone or ""
                    if res:
                        st.success(f"Paziente registrato con ID {res['id']}.")
                        st.info("Questo profilo è legato all'accesso corrente (email).")

            st.markdown('</div>', unsafe_allow_html=True)

    # 2) VISITE E PRENOTAZIONI (con SMS demo)
    elif page == "Visite e prenotazioni":
        with st.container():
            st.markdown('<div class="bs-card">', unsafe_allow_html=True)
            st.markdown('<div class="bs-section-title">📅 Prenotazione visite</div>', unsafe_allow_html=True)
            st.write("Prenota una visita, scegli data e fascia oraria e configura le notifiche di preparazione.")

            if not current_patient_id:
                st.info("Seleziona o registra un paziente per prenotare una visita.")
            else:
                # Proviamo a recuperare il nome paziente per SMS più realistico
                current_patient = next((p for p in filtered_patients if p["id"] == current_patient_id), None)
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
                    payload = {
                        "patient_id": current_patient_id,
                        "specialty": specialty,
                        "date": appt_date.isoformat(),
                        "reason": reason or None,
                    }
                    res = safe_post("/appointments", json=payload)
                    if res:
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

                        # SMS mock per referto/preparazione
                        if sms_reminder:
                            sms_text = generate_preparation_sms(patient_name, specialty, appt_date, time_slot)
                            st.markdown("**Anteprima SMS (simulazione):**")
                            st.code(sms_text, language="text")

                st.subheader("Tutte le visite del paziente")
                appts = safe_get(f"/appointments/by_patient/{current_patient_id}")
                if appts:
                    st.table(appts)
                else:
                    st.write("Nessuna visita ancora registrata.")

            st.markdown('</div>', unsafe_allow_html=True)

    # 3) MONITORAGGIO PAZIENTE
    elif page == "Monitoraggio paziente":
        with st.container():
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
                    payload = {
                        "patient_id": current_patient_id,
                        "days_from_procedure": int(days),
                        "pain_level": int(pain),
                        "shortness_of_breath": breath,
                        "fever": fever,
                        "notes": notes or None,
                    }
                    res = safe_post("/followup/checkin", json=payload)
                    if res:
                        st.subheader("Risultato triage (demo)")
                        st.write(f"Livello: **{res['triage_level']}**")
                        st.write(res["message"])
                        st.info(res["suggested_action"])

            st.markdown('</div>', unsafe_allow_html=True)

    # 4) PREVENZIONE (senza età/sesso in UI)
    elif page == "Prevenzione":
        with st.container():
            st.markdown('<div class="bs-card">', unsafe_allow_html=True)
            st.markdown('<div class="bs-section-title">🛡️ Piano di prevenzione personalizzato</div>', unsafe_allow_html=True)

            st.write(
                "Sezione demo basata sulle condizioni di rischio auto-dichiarate. "
                "Per semplicità non chiediamo età e sesso nella UI, ma li impostiamo "
                "a valori neutri nel modello backend."
            )

            conditions = st.multiselect(
                "Condizioni note (facoltativo)",
                ["ipertensione", "diabete", "ipercolesterolemia", "fumo", "obesità"],
            )

            # Valori di default “neutri” per non rompere il backend
            default_age = 50
            default_sex = "Altro"

            if st.button("Genera piano di prevenzione"):
                payload = {
                    "age": int(default_age),
                    "sex": default_sex,
                    "conditions": conditions or None,
                }
                res = safe_post("/prevention/plan", json=payload)
                if res:
                    st.subheader(f"Profilo di rischio: **{res['risk_profile']}**")
                    st.write("**Raccomandazioni:**")
                    for r in res["recommendations"]:
                        st.markdown(f"- {r}")
                    st.write("**Screening suggeriti:**")
                    for s in res["suggested_screenings"]:
                        st.markdown(f"- {s}")

            st.markdown('</div>', unsafe_allow_html=True)

    # 5) FEEDBACK
    elif page == "Feedback":
        with st.container():
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
                payload = {
                    "patient_id": current_patient_id,
                    "rating": int(rating),
                    "comment": comment or None,
                    "touchpoint": touchpoint,
                }
                res = safe_post("/feedback", json=payload)
                if res:
                    st.success("Grazie, il feedback è stato registrato.")

            st.subheader("Sintesi generale soddisfazione")
            summary = safe_get("/feedback/summary")
            if summary:
                st.write(f"Numero di risposte: **{summary['n_responses']}**")
                st.write(f"Rating medio: **{summary['average_rating']} / 10**")
                st.write(f"NPS stimato: **{summary['nps']}**")

            st.markdown('</div>', unsafe_allow_html=True)

    # 6) CHATBOT SINTOMI
    elif page == "Chatbot sintomi":
        with st.container():
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
        with st.container():
            st.markdown('<div class="bs-card">', unsafe_allow_html=True)
            st.markdown('<div class="bs-section-title">🧭 Come arrivare al reparto</div>', unsafe_allow_html=True)

            department = st.text_input("Reparto (es: Cardiologia, Ortopedia...)")
            building = st.text_input("Corpo/Edificio (facoltativo)", value="")
            floor = st.number_input("Piano (facoltativo, -1 a 10)", min_value=-1, max_value=10, value=2)

            if st.button("Genera indicazioni"):
                if not department:
                    st.warning("Inserisci almeno il nome del reparto.")
                else:
                    payload = {
                        "department": department,
                        "building": building or None,
                        "floor": int(floor),
                    }
                    res = safe_post("/navigation/info", json=payload)
                    if res:
                        st.subheader(f"Reparto: {res['department']}")
                        st.write(res["description"])
                        st.write(f"Edificio: **{res['building']}**, piano **{res['floor']}**")
                        st.write("Indicazioni:")
                        for step in res["guidance"]:
                            st.markdown(f"- {step}")

            st.markdown('</div>', unsafe_allow_html=True)

    # 8) DASHBOARD PAZIENTE – con integrazione device (mock) + SMS referto
    elif page == "Dashboard paziente":
        with st.container():
            st.markdown('<div class="bs-card">', unsafe_allow_html=True)
            st.markdown('<div class="bs-section-title">📊 Dashboard paziente</div>', unsafe_allow_html=True)

            if not current_patient_id:
                st.info("Seleziona o registra un paziente per vedere la dashboard.")
            else:
                summary = safe_get(f"/patients/{current_patient_id}/summary")
                if summary:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Dati paziente")
                        st.write(summary.get("patient", {}))
                    with col2:
                        st.subheader("Sintesi relazione")
                        st.metric("Feedback registrati", summary.get("feedback_count", 0))
                        st.write("Appuntamenti futuri:", len(summary.get("upcoming_appointments", [])))
                        st.write("Appuntamenti passati:", len(summary.get("past_appointments", [])))

                    # Sezione: integrazione device (mock)
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

                        # SMS referto pronto (mock)
                        last_appt = past_appts[-1]
                        spec = last_appt.get("specialty", "visita")
                        raw_date = last_appt.get("date", "")
                        try:
                            d = datetime.fromisoformat(raw_date).strftime("%d/%m/%Y")
                        except Exception:
                            d = raw_date
                        if st.button("Simula SMS: referto pronto"):
                            sms_referto = (
                                f"Gentile paziente, il referto relativo alla tua {spec.lower()} "
                                f"del {d} è disponibile nell’area riservata dell’Ospedale Demo."
                            )
                            st.markdown("**Anteprima SMS (referto pronto):**")
                            st.code(sms_referto, language="text")
                    else:
                        st.write("Nessun appuntamento passato registrato.")

            st.markdown('</div>', unsafe_allow_html=True)

    # 9) DASHBOARD CLINICA (demo per medici / management)
    elif page == "Dashboard clinica":
        with st.container():
            st.markdown('<div class="bs-card">', unsafe_allow_html=True)
            st.markdown('<div class="bs-section-title">🏥 Dashboard clinica (demo)</div>', unsafe_allow_html=True)

            st.write(
                "Vista sintetica pensata per direzione sanitaria e clinici: panoramica pazienti, "
                "appuntamenti e soddisfazione. I dati sono basati sulle chiamate all’API demo."
            )

            all_patients = patients  # già recuperati prima
            st.write(f"**Pazienti attivi sulla piattaforma (demo):** {len(all_patients)}")

            feedback_summary = safe_get("/feedback/summary")
            if feedback_summary:
                colA, colB, colC = st.columns(3)
                with colA:
                    st.metric("Feedback raccolti", feedback_summary["n_responses"])
                with colB:
                    st.metric("Rating medio", f"{feedback_summary['average_rating']} / 10")
                with colC:
                    st.metric("NPS stimato", feedback_summary["nps"])

            # Tabella sintetica per i primi N pazienti
            rows = []
            max_patients = min(len(all_patients), 10)
            for p in all_patients[:max_patients]:
                pid = p["id"]
                name = p.get("name", "")
                try:
                    s = safe_get(f"/patients/{pid}/summary")
                    if not s:
                        continue
                    upc = len(s.get("upcoming_appointments", []))
                    past = len(s.get("past_appointments", []))
                    fb = s.get("feedback_count", 0)
                    rows.append({
                        "ID paziente": pid,
                        "Nome": name,
                        "Visite future": upc,
                        "Visite passate": past,
                        "Feedback registrati": fb,
                    })
                except Exception:
                    continue

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

    # 10) PAGAMENTI
    elif page == "Pagamenti":
        with st.container():
            st.markdown('<div class="bs-card">', unsafe_allow_html=True)
            st.markdown('<div class="bs-section-title">💳 Pagamento visite</div>', unsafe_allow_html=True)

            st.write(
                "Sezione dimostrativa per il pagamento digitale delle visite. "
                "I prezzi sono simulati a scopo di esempio."
            )

            if not current_patient_id:
                st.info("Seleziona un paziente per vedere le visite da pagare.")
            else:
                appts = safe_get(f"/appointments/by_patient/{current_patient_id}") or []
                future_appts = []
                for a in appts:
                    raw = a.get("date", "")
                    try:
                        d = datetime.fromisoformat(raw).date()
                        if d >= date.today():
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
            © 2024 Boston Scientific Corporation o sue affiliate. Tutti i diritti  privacy riservati.
        </div>
        """,
        unsafe_allow_html=True,
    )
