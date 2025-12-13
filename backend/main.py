import sys
import os
import logging
from typing import Optional
from tempfile import NamedTemporaryFile

# Ajout du dossier courant au path pour les imports locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException, status

# Imports locaux
from models.cv_result import CVResult
from services.pdf_parser import extract_text_pdf
from services.docx_parser import extract_text_docx
from services.extractor import (
    clean_text, 
    extract_email, 
    extract_phone, 
    extract_name, 
    extract_degree
)

# Configuration Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("CVExtractor")

app = FastAPI(title="CV Extractor API")

# Mapping MIME Type -> Fonction de parsing
PARSERS = {
    "application/pdf": extract_text_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": extract_text_docx
}

@app.post("/api/v1/upload-cv", response_model=CVResult)
async def upload_cv(file: UploadFile = File(...)) -> CVResult:
    """
    Endpoint principal : Reçoit un fichier, l'analyse et retourne les infos extraites.
    """
    tmp_path: Optional[str] = None
    
    # 1. Validation du Format
    if file.content_type not in PARSERS:
        logger.warning(f"Format rejeté : {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Format non supporté. Utilisez PDF ou DOCX."
        )

    try:
        # 2. Gestion Fichier Temporaire
        suffix = ".pdf" if file.content_type == "application/pdf" else ".docx"
        
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Fichier vide.")
            
            tmp.write(content)
            tmp_path = tmp.name
            logger.info(f"Fichier reçu : {file.filename} -> {tmp_path}")

        # 3. Parsing du Texte
        try:
            parse_function = PARSERS[file.content_type]
            raw_text = parse_function(tmp_path)
            
            if not raw_text or len(raw_text.strip()) < 10:
                raise HTTPException(status_code=422, detail="Fichier illisible ou image scannée non supportée.")
                
        except Exception as e:
            # On capture les erreurs remontées par les parsers
            logger.error(f"Echec parsing : {e}")
            raise HTTPException(status_code=422, detail="Impossible de lire le contenu du fichier.")

        # 4. Extraction d'informations (NLP)
        logger.info("Analyse sémantique en cours...")
        cleaned_text = clean_text(raw_text)
        
        first_name, last_name = extract_name(cleaned_text)
        
        result = CVResult(
            first_name=first_name,
            last_name=last_name,
            email=extract_email(cleaned_text),
            phone=extract_phone(cleaned_text),
            degree=extract_degree(cleaned_text)
        )
        
        logger.info("Extraction réussie.")
        return result

    except HTTPException:
        raise # On relance les erreurs HTTP volontaires
        
    except Exception as e:
        logger.critical(f"Erreur serveur inattendue : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")
        
    finally:
        # 5. Nettoyage
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                logger.debug(f"Nettoyage temp : {tmp_path}")
            except OSError:
                logger.warning(f"Impossible de supprimer {tmp_path}")