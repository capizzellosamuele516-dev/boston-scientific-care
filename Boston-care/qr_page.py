import streamlit as st
from io import BytesIO
import qrcode
from PIL import Image, ImageDraw
import os

# ====================================================
# URL DELLA TUA APP PRINCIPALE SU STREAMLIT CLOUD
# ====================================================
APP_PUBLIC_URL = "https://boston-scientific-care-tsdqxxoqxmzznw9jj2jzgc.streamlit.app/" 


# ====================================================
# CONFIGURAZIONE STREAMLIT + TEMA CHIARO FORZATO
# ====================================================
st.set_page_config(
    page_title="Boston Scientific Care – QR accesso",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Forza tema chiaro e sfondo bianco
st.markdown("""
<style>
:root {
    color-scheme: light !important;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# CSS per testi
st.markdown(
    """
    <style>
    .qr-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #00447a;
        text-align: center;
        margin-top: 2rem;
        margin-bottom: 0.3rem;
    }
    .qr-subtitle {
        font-size: 1.0rem;
        color: #425870;
        text-align: center;
        margin-bottom: 1.4rem;
    }
    .qr-url {
        font-size: 0.9rem;
        color: #607496;
        text-align: center;
        margin-top: 0.8rem;
        word-wrap: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ====================================================
# GENERAZIONE QR BRANDIZZATO (BLU, "CIRCOLARE", LOGO GRANDE)
# ====================================================

# 1) QR base con alta correzione di errore
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=3,
)
qr.add_data(APP_PUBLIC_URL)
qr.make(fit=True)

# 2) QR blu Boston Scientific
qr_img = qr.make_image(fill_color="#005c99", back_color="white").convert("RGBA")
qr_width, qr_height = qr_img.size

# 3) Sfondo circolare bianco dietro al QR (effetto "badge" circolare)
circle_diameter = qr_width + 60
bg = Image.new("RGBA", (circle_diameter, circle_diameter), (0, 0, 0, 0))

draw = ImageDraw.Draw(bg)
draw.ellipse(
    (0, 0, circle_diameter - 1, circle_diameter - 1),
    fill=(255, 255, 255, 255)
)

# Centro il QR sul cerchio
offset = (
    (circle_diameter - qr_width) // 2,
    (circle_diameter - qr_height) // 2,
)
bg.paste(qr_img, offset, qr_img)

# 4) Logo Boston Scientific più grande al centro del QR
try:
    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "bs_logo.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")

        # Logo ~ 1/3 della larghezza del QR
        logo_size = qr_width // 3
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        center_x = circle_diameter // 2
        center_y = circle_diameter // 2
        logo_pos = (
            center_x - logo_size // 2,
            center_y - logo_size // 2,
        )

        bg.paste(logo, logo_pos, logo)
except Exception:
    # Se qualcosa va storto con il logo, lasciamo solo QR + cerchio bianco
    pass

# 5) Salvo in buffer per Streamlit
buf = BytesIO()
bg.save(buf, format="PNG")
buf.seek(0)


# ====================================================
# LAYOUT CENTRATO
# ====================================================

# Titolo + sottotitolo
st.markdown(
    """
    <div class="qr-title">
        Boston Scientific Care – Demo interattiva
    </div>
    <div class="qr-subtitle">
        Inquadra il QR code con il tuo smartphone<br/>
        per accedere alla piattaforma durante lo speech.
    </div>
    """,
    unsafe_allow_html=True,
)

# Contenitore centrale per il QR
st.markdown("""
<div style="
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
">
""", unsafe_allow_html=True)

# QR al centro (niente parametri deprecati)
st.image(buf, width=280)

# Chiudo il contenitore del QR
st.markdown("</div>", unsafe_allow_html=True)

# URL sotto, centrato
st.markdown(
    f"""
    <div class="qr-url">
        {APP_PUBLIC_URL}
    </div>
    """,
    unsafe_allow_html=True,
)

