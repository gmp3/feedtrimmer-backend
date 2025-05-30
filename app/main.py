import os
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, PlainTextResponse
import urllib

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
    return RedirectResponse(url="https://gmp3.github.io/feedtrimmer", status_code=301)

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("OK", status_code=200)

@app.post("/upload")
async def upload_feed(req: Request):
    # Log request details
    print(f"[UPLOAD] Request from {req.client.host} - headers: {dict(req.headers)}")

    # if req.headers.get("x-api-key") != API_KEY:
    #     raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Validate XML
        print("inside try block")
        data = await req.body()
        print("after await req.body()")
        data_et = urllib.parse.unquote(data)
        print("after urllib.parse.unquote(data)")

        try:
            ET.fromstring(data_et)
        except ET.ParseError as e:
            print(f"[UPLOAD][ERROR] XML Content: {data_et}")
            raise HTTPException(status_code=400, detail=f"Invalid XML: {str(e)}")

        print("XML validated successfully")
        # Upload to Supabase
        file_name: str = "/podcast.xml"
        # data: str = "<?xml version='1.0' encoding='UTF-8'?></xml>"
        # data = bytes(data, encoding="utf-8")

        # print(data, "\n\n\n\n")

        result = supabase.storage.from_("feedtrimmer").upload("/podcast.xml", data, {
            "content-type": "application/rss+xml",
            "upsert": "True"
        })
        print(f"[UPLOAD] Upload result: {result}")

        if result.response.status_code != 200:
            print(f"[UPLOAD][ERROR] Supabase upload error for file '{file_name}': {result['error']}")
            print(f"[UPLOAD][ERROR] Request headers: {dict(req.headers)}")
            print(f"[UPLOAD][ERROR] XML Content: {data}")
            raise Exception(result["error"]["message"])

        public_url = f"{SUPABASE_URL}/storage/v1/s3/object/public/feedtrimmer/{file_name}"
        return {"url": public_url}

    except Exception as e:
        print(f"[UPLOAD][ERROR] Exception during upload: {str(e)}")
        print(f"[UPLOAD][ERROR] Request headers: {dict(req.headers)}")
        # print(f"[UPLOAD][ERROR] XML Content: {data}")
        raise HTTPException(status_code=500, detail=str(e))
