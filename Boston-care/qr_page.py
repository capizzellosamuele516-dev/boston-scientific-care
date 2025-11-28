import streamlit as st
from io import BytesIO
import qrcode
from PIL import Image
import os

# ====================================================
# URL della TUA APP PRINCIPALE su Streamlit Cloud
# (quella dove gira Boston Scientific Care)
# ====================================================
APP_PUBLIC_URL = "https://boston-scientific-care-4qdu5v9kzelsyzzmuzzpsj.streamlit.app/"  

st.set_page_config(
    page_title="Boston Scientific Care – QR accesso",
    layout="centered",
)

# =========================
# CSS minimal elegante
# =========================

st.markdown(
    """
    <style>
    body {
        background-color: #ffffff !important;
    }
    .qr-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 2rem;
    }
    .qr-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #00447a;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .qr-subtitle {
        font-size: 0.95rem;
        color: #425870;
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .qr-url {
        font-size: 0.8rem;
        color: #607496;
        text-align: center;
        margin-top: 0.6rem;
        word-wrap: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Generazione QR brandizzato
# =========================

# 1) QR di base con correzione alta (per poter mettere il logo al centro)
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=3,
)
qr.add_data(APP_PUBLIC_URL)
qr.make(fit=True)

# 2) QR con colore blu Boston Scientific
qr_img = qr.make_image(fill_color="#005c99", back_color="white").convert("RGB")

# 3) Tentativo di inserire il logo al centro (bs_logo.png)
try:
    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "bs_logo.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")

        qr_width, qr_height = qr_img.size
        logo_size = qr_width // 4  # logo ~25% della larghezza del QR
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        pos = (
            (qr_width - logo_size) // 2,
            (qr_height - logo_size) // 2,
        )

        qr_img.paste(logo, pos, mask=logo)
except Exception:
    # Se qualcosa va storto col logo, usiamo solo il QR blu
    pass

# 4) Mostro il QR in pagina
buf = BytesIO()
qr_img.save(buf, format="PNG")
buf.seek(0)

st.markdown('<div class="qr-container">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="qr-title">Boston Scientific Care – Demo interattiva</div>
    <div class="qr-subtitle">
        Inquadra il QR code con il tuo smartphone<br/>
        per accedere alla piattaforma durante lo speech.
    </div>
    """,
    unsafe_allow_html=True,
)
st.image(buf, width=260)
st.markdown(
    f'<div class="qr-url">{APP_PUBLIC_URL}</div>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)
