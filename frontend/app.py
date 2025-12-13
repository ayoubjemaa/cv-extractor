import streamlit as st
import requests
import json
import base64
import os
import time
import socket
import logging

#CONFIGURATION INITIALE
st.set_page_config(
    page_title="CBX Extractor",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend")


# CONSTANTES & CONFIGURATION API 

def get_api_url():
    """Détermine l'URL du backend de manière robuste."""
    env_url = os.getenv("BACKEND_API_URL")
    if env_url:
        return env_url
    
    try:
        hostname = socket.gethostname()
        if hostname == "cv-extractor-frontend":
            return "http://cv-extractor-backend:8000/api/v1/upload-cv"
    except Exception:
        pass
        
    return "http://localhost:8000/api/v1/upload-cv"

API_URL = get_api_url()
logger.info(f"Frontend connecté au Backend sur : {API_URL}")


# GESTION DES ASSETS & STYLES 

def load_image_as_base64(filename: str) -> str | None:
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Erreur chargement image {filename}: {e}")
    return None

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {
      --bg-color: #f8fafc;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border-color: #e2e8f0;
      --primary: #2563eb;
    }

    .stApp {
      background-color: var(--bg-color);
      font-family: 'Plus Jakarta Sans', sans-serif;
      color: var(--text-main);
    }
    
    header[data-testid="stHeader"], footer { display: none !important; }

    /* Navbar Fixe */
    .custom-navbar {
      position: fixed; top: 0; left: 0; right: 0; height: 72px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border-color);
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 32px; z-index: 10000;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Padding du contenu principal pour éviter d'être caché par la navbar */
    [data-testid="stAppViewContainer"] > .main > .block-container {
      padding-top: 100px !important;
      padding-bottom: 60px !important;
      max-width: 1400px;
    }

    /* Zone de dépôt de fichiers */
    [data-testid="stFileUploaderDropzone"] {
        background-color: white;
        border: 1px dashed #cbd5e1;
        border-radius: 12px;
        padding: 40px;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--primary);
        background-color: #f1f5f9;
    }

    /* Champs de saisie */
    .stTextInput input, .stTextArea textarea {
      background-color: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 10px 14px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
      outline: none;
    }

    /* Boutons */
    div.stButton > button, div.stDownloadButton > button {
      width: 100%;
      border-radius: 8px;
      font-weight: 600;
      background-color: white !important;
      border: 1px solid #cbd5e1 !important;
      color: var(--text-main) !important;
      transition: all 0.2s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
      background-color: #f8fafc !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Conteneurs principaux (CV et Formulaire) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.02); 
        padding: 24px;
        /* HACK : Force la hauteur minimale pour égaliser les deux colonnes sur Desktop */
        min-height: 700px; 
        display: flex;
        flex-direction: column;
    }

    /* Iframe PDF */
    iframe {
        border: none;
        display: block;
        background-color: #f1f5f9;
        border-radius: 8px;
        width: 100%;
        height: 100%;
        min-height: 650px; /* Prend toute la hauteur du conteneur parent */
    }

    /* --- RESPONSIVE MOBILE / TABLETTE (< 992px) --- */
    @media (max-width: 992px) {
      .custom-navbar { padding: 0 16px; height: 60px; }
      
      /* Sur mobile, on enlève la hauteur forcée pour laisser le contenu naturel */
      [data-testid="stVerticalBlockBorderWrapper"] > div {
          min-height: auto !important;
          height: auto !important;
      }

      /* Le PDF prend moins de hauteur sur mobile */
      iframe { min-height: 450px !important; } 
      
      /* Force les colonnes à passer l'une sous l'autre avec une marge */
      [data-testid="column"] { 
          width: 100% !important;
          margin-bottom: 24px;
          display: block;
      }
    }
    </style>
    """, unsafe_allow_html=True)


# COMPOSANTS UI

def render_navbar():
    logo_b64 = load_image_as_base64("logo.png")
    
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="Logo" style="height:36px; border-radius:4px;">'
        if logo_b64 else "<span style='font-weight:700; font-size:20px; color:#0f172a;'>CBX EXTRACTOR</span>"
    )
    
    st.markdown(f"""
    <div class="custom-navbar">
      <div style="display:flex;align-items:center;gap:14px;">
        {logo_html}
        <div style="height:24px;width:1px;background:#e2e8f0;margin:0 4px;"></div>
        <div style="display:flex;flex-direction:column;justify-content:center;">
            <span style="font-weight:700;font-size:16px;color:#0f172a;line-height:1.2;">Extraction CV</span>
            <span style="font-size:12px;color:#64748b;font-weight:500;">Portail RH</span>
        </div>
      </div>
      <div style="font-size:13px;color:#64748b;font-weight:600; background:#f1f5f9; padding:8px 16px; border-radius:20px;">
        v1.0
      </div>
    </div>
    """, unsafe_allow_html=True)


def reset_session():
    st.session_state.cv_data = None
    st.session_state.current_file_name = None
    st.session_state.current_file_content = None
    st.rerun()


# PAGES

def show_upload_page():
    _, col_center, _ = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("""
        <div style="text-align:center; margin-bottom: 40px; margin-top: 20px;">
            <h1 style="font-size:36px; font-weight:800; color:#0f172a; margin-bottom:16px; letter-spacing:-0.5px;">
                Extraction de données candidats
            </h1>
            <p style="font-size:16px; color:#64748b; margin:0 auto; max-width:600px; line-height:1.6;">
                Optimisez votre recrutement. Importez un CV (PDF/DOCX) pour extraire instantanément les informations clés.
            </p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Zone de dépôt", type=["pdf", "docx"], label_visibility="collapsed")

        if not uploaded_file:
            st.info("Glissez votre fichier ici (PDF ou DOCX)")

        if uploaded_file:
            st.markdown("###")
            with st.spinner("Analyse du document en cours..."):
                try:
                    time.sleep(0.5)
                    st.session_state.current_file_name = uploaded_file.name
                    st.session_state.current_file_content = uploaded_file.getvalue()
                    st.session_state.current_file_type = uploaded_file.type

                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    resp = requests.post(API_URL, files=files, timeout=30)

                    if resp.status_code == 200:
                        st.session_state.cv_data = resp.json()
                        st.rerun()
                    else:
                        st.error(f"Erreur d'analyse (Code {resp.status_code}) : {resp.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Impossible de contacter le serveur d'analyse. Vérifiez que le Backend est lancé.")
                except Exception as e:
                    st.error(f"Une erreur inattendue est survenue : {e}")


def show_result_page():
    st.markdown("""
    <div style="margin-bottom:20px; display:flex; align-items:center; gap:8px; font-size:14px;">
        <span style="color:#64748b;">Accueil</span>
        <span style="color:#cbd5e1;">/</span>
        <span style="font-weight:600; color:#0f172a;">Résultats d'extraction</span>
    </div>
    """, unsafe_allow_html=True)

    col_pdf, col_form = st.columns([1.2, 1], gap="large")

    # APERÇU DOCUMENT INSERE
    with col_pdf:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <span style="font-weight:700; font-size:16px; color:#0f172a;">Aperçu du document</span>
                <span style="font-size:12px; color:#64748b; background:#f1f5f9; padding:4px 10px; border-radius:6px;">
                    {st.session_state.current_file_name}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.current_file_type == "application/pdf":
                b64_pdf = base64.b64encode(st.session_state.current_file_content).decode("utf-8")
                # AJOUT : toolbar=1 pour réactiver la barre d'outils
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{b64_pdf}#toolbar=1&navpanes=0&view=FitH"></iframe>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("L'aperçu n'est disponible que pour les fichiers PDF.")
                st.markdown('<div style="height:400px; background:#f8fafc; display:flex; align-items:center; justify-content:center; color:#cbd5e1;">Aperçu non disponible</div>', unsafe_allow_html=True)

    # FORMULAIRE D'EXTRACTION
    with col_form:
        cv = st.session_state.cv_data
        
        with st.container(border=True):
            st.markdown("""
            <div style="margin-bottom:20px;">
                <span style="font-weight:700; font-size:18px; color:#0f172a;">Informations détectées</span>
                <p style="font-size:13px; color:#64748b; margin-top:4px;">Vous pouvez modifier les champs avant l'export.</p>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            fn = c1.text_input("Prénom", cv.get("first_name", ""))
            ln = c2.text_input("Nom", cv.get("last_name", ""))

            email = st.text_input("Email", cv.get("email", ""))
            phone = st.text_input("Téléphone", cv.get("phone", ""))
            
            degree = st.text_area("Diplôme / Formation", cv.get("degree", ""), height=120)

            st.markdown("<div style='flex-grow:1; min-height: 20px;'></div>", unsafe_allow_html=True)
            
            col_action_1, col_action_2 = st.columns(2)
            
            final_json = {
                "first_name": fn, "last_name": ln,
                "email": email, "phone": phone,
                "degree": degree
            }
            
            with col_action_1:
                st.download_button(
                    label="Télécharger JSON",
                    data=json.dumps(final_json, ensure_ascii=False, indent=4),
                    file_name=f"export_{st.session_state.current_file_name}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_action_2:
                if st.button("Analyser un autre CV", use_container_width=True):
                    reset_session()


# POINT D'ENTRÉE

def main():
    if "cv_data" not in st.session_state:
        st.session_state.cv_data = None
    if "current_file_name" not in st.session_state:
        st.session_state.current_file_name = None

    inject_custom_css()
    render_navbar()

    if st.session_state.cv_data is None:
        show_upload_page()
    else:
        show_result_page()

if __name__ == "__main__":
    main()