from fastapi import FastAPI, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
from .models.cv_result import CVResult
from .services.pdf_parser import extract_text_pdf
from .services.docx_parser import extract_text_docx
from .services.extractor import clean_text, extract_email, extract_phone, extract_name, extract_degree

app = FastAPI(title="CV Extractor API – Partie B")

ALLOWED_CONTENT_TYPES = {
    "application/pdf": extract_text_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": extract_text_docx
}

@app.post("/api/v1/upload-cv", response_model=CVResult)
async def upload_cv(file: UploadFile = File(...)) -> CVResult:
    # Vérifier type de fichier
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Le fichier doit être PDF ou DOCX")

    # Sauvegarder temporairement le fichier
    with NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extraire le texte brut
    text = ALLOWED_CONTENT_TYPES[file.content_type](tmp_path)
    # Nettoyer le texte
    cleaned_text = clean_text(text)
    print(text)

    # Extraire informations
    first_name, last_name = extract_name(cleaned_text)
    cv_data = CVResult(
        first_name=first_name or "Non trouvé",
        last_name=last_name or "Non trouvé",
        email=extract_email(cleaned_text) or "Non trouvé",
        phone=extract_phone(cleaned_text) or "Non trouvé",
        degree=extract_degree(cleaned_text) or "Non trouvé"
    )

    return cv_data
