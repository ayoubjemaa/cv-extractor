from pydantic import BaseModel

class CVResult(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    degree: str
