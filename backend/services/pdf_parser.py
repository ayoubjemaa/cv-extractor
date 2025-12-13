import pdfplumber
import logging

logger = logging.getLogger(__name__)

def extract_text_pdf(file_path: str) -> str:
    """Extrait le texte brut d'un fichier PDF."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du PDF {file_path}: {e}")
        raise e