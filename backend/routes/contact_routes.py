from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.contact_service import load_contacts, find_email_by_name
import tempfile

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.post("/upload")
async def upload_contacts(file: UploadFile = File(...)):
    """Upload contacts CSV/Excel."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        result = load_contacts(tmp.name)
    return result


@router.get("/lookup/{name}")
def lookup_contact(name: str):
    """Find email by name."""
    email = find_email_by_name(name)
    if not email:
        raise HTTPException(status_code=404, detail=f"No contact found for {name}")
    return {"name": name, "email": email}
