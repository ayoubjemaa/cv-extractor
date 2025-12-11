from fastapi import FastAPI, UploadFile, File, HTTPException
from .models.cv_result import CVResult
app = FastAPI(title="CV Extractor API – Partie A")

@app.post("/api/v1/upload-cv", response_model=CVResult)
async def upload_cv(file: UploadFile = File(...)):
    # Vérification du type de fichier
    if file.content_type not in ["application/pdf",
                                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Le fichier doit être PDF ou DOCX")

    # Retour JSON statique 
    return CVResult(
        first_name="Alain",
        last_name="Bernard",
        email="xxxx@gmail.com",
        phone="+336xxxxxxx",
        degree="Master Informatique"
    )
