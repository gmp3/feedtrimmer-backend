import os
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, PlainTextResponse
import urllib
import random
import string
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")

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

    try:
        # Validate XML
        data = await req.body()
        data_et = urllib.parse.unquote(data)

        try:
            ET.fromstring(data_et)
        except ET.ParseError as e:
            print(f"[UPLOAD][ERROR] XML Content: {data_et}")
            raise HTTPException(status_code=400, detail=f"Invalid XML: {str(e)}")

        print("XML validated successfully")
        
        # Upload to Supabase
        file_name: str = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}.xml"
        upload_to_supabase(file_name, data_et.encode('utf-8'), req)
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/feedtrimmer/{file_name}"
        return {"public_url": public_url}

    except Exception as e:
        print(f"[UPLOAD][ERROR] Exception during upload: {str(e)}")
        print(f"[UPLOAD][ERROR] Request headers: {dict(req.headers)}")
        # print(f"[UPLOAD][ERROR] XML Content: {data}")
        raise HTTPException(status_code=500, detail=str(e))

def upload_to_supabase(file_name: str, data: bytes, req: Request) -> str:
    print(f"[UPLOAD] Uploading file: {file_name}")

    try:
        result = supabase.storage.from_("feedtrimmer").upload(file_name, data, {
            "content-type": "application/rss+xml",
            "upsert": "True"
        })
        print(f"[UPLOAD] Upload result: {result}")

        if result.status_code != 200 and result.status_code != 400:
            print(f"[UPLOAD][ERROR] Supabase upload error for file '{file_name}': {result['error']}")
            print(f"[UPLOAD][ERROR] Request headers: {dict(req.headers)}")
            print(f"[UPLOAD][ERROR] XML Content: {data}")
            raise Exception(result["error"]["message"])
    except Exception as upload_error:
        print(f"[UPLOAD][ERROR] Exception during Supabase upload: {str(upload_error)}")
        raise HTTPException(status_code=500, detail=f"Supabase upload failed: {str(upload_error)}")

def shorten_url(long_url: str) -> str:
    api_url = f"https://api.tinyurl.com/create?api_token=YOUR_API_TOKEN"
    payload = {
        "url": long_url,
        "domain": "tinyurl.com"
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 201:
        return response.json()["data"]["tiny_url"]
    else:
        raise Exception(f"Shorten URL failed: {response.text}")
