from docx import Document
import logging

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

def extract_text_docx(file_path: str) -> str:
    """Extrait le texte brut d'un fichier DOCX."""
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du DOCX {file_path}: {e}")
        raise e