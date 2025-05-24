import os
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, PlainTextResponse

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# print (f"SUPABASE_URL: {SUPABASE_URL}")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")
# print (f"SUPABASE_KEY: {SUPABASE_KEY}")
API_KEY = os.getenv("API_KEY")
# print (f"API_KEY: {API_KEY}")

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

@app.get("/")
async def root():
    return RedirectResponse(url="https://gmp3.github.io/podtrimmer", status_code=403)

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("OK", status_code=200)

@app.post("/upload")
async def upload_feed(req: Request, body: UploadRequest):
    # Log request details
    print(f"[UPLOAD] Request from {req.client.host} - fileName: {body.fileName}, headers: {dict(req.headers)}")

    if req.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Validate XML
        try:
            ET.fromstring(body.xmlContent)
        except ET.ParseError as e:
            print(f"[UPLOAD][ERROR] XML ParseError for file '{body.fileName}': {str(e)}")
            print(f"[UPLOAD][ERROR] XML Content: {body.xmlContent}")
            raise HTTPException(status_code=400, detail=f"Invalid XML: {str(e)}")

        # Upload to Supabase
        data = body.xmlContent.encode("utf-8")
        file_name = body.fileName

        result = supabase.storage.from_("podcast-feeds").upload(file_name, data, {
            "content-type": "text/xml",
            "upsert": True
        })

        if result.get("error"):
            print(f"[UPLOAD][ERROR] Supabase upload error for file '{file_name}': {result['error']}")
            print(f"[UPLOAD][ERROR] Request headers: {dict(req.headers)}")
            print(f"[UPLOAD][ERROR] XML Content: {body.xmlContent}")
            raise Exception(result["error"]["message"])

        public_url = f"{SUPABASE_URL}/storage/v1/s3/object/public/podcast-feeds/{file_name}"
        return {"url": public_url}

    except Exception as e:
        print(f"[UPLOAD][ERROR] Exception for file '{body.fileName}': {str(e)}")
        print(f"[UPLOAD][ERROR] Request headers: {dict(req.headers)}")
        print(f"[UPLOAD][ERROR] XML Content: {body.xmlContent}")
        raise HTTPException(status_code=500, detail=str(e))
