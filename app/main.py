import os
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")
API_KEY = os.getenv("API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UploadRequest(BaseModel):
    fileName: str
    xmlContent: str

@app.post("/upload")
async def upload_feed(req: Request, body: UploadRequest):
    if req.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Validate XML
        try:
            ET.fromstring(body.xmlContent)
        except ET.ParseError as e:
            raise HTTPException(status_code=400, detail=f"Invalid XML: {str(e)}")

        # Upload to Supabase
        data = body.xmlContent.encode("utf-8")
        file_name = body.fileName

        result = supabase.storage.from_("podcast-feeds").upload(file_name, data, {
            "content-type": "application/rss+xml",
            "upsert": True
        })

        if result.get("error"):
            raise Exception(result["error"]["message"])

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/podcast-feeds/{file_name}"
        return {"url": public_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
