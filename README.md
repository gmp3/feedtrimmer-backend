# feedtrimmer-backend

Backend API Server for FeedTrimmer App

## Overview

This project provides a FastAPI backend for uploading and storing podcast RSS feeds. It validates XML content and uploads it to Supabase Storage, making the feed publicly accessible.

## Features

- REST API endpoint to upload podcast RSS feeds as XML
- XML validation before upload
- Storage of feeds in Supabase Storage bucket (`podcast-feeds`)
- Public URL returned for each uploaded feed
- Health check endpoint
- Root endpoint redirects with 403

## Requirements

- Python 3.11+
- [Supabase](https://supabase.com/) project with a storage bucket named `podcast-feeds`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/feedtrimmer-backend.git
    cd feedtrimmer-backend
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory with the following variables:
    ```
    SUPABASE_URL=your-supabase-url
    SUPABASE_SERVICE_ROLE=your-service-role-key
    ```

## Running Locally

Start the server with:

```sh
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Usage

### Root Endpoint

**GET /**  
Redirects to [https://gmp3.github.io/feedtrimmer](https://gmp3.github.io/feedtrimmer) with a 403 status.

### Health Check

**GET /healthz**  
Returns `OK` with status 200.

### Upload Feed

**POST /upload**


**Body:**
```json
{
  "fileName": "example.xml",
  "xmlContent": "<rss>...</rss>"
}
```

**Response:**
```json
{
  "url": "https://your-supabase-url/storage/v1/s3/object/public/podcast-feeds/example.xml"
}
```

**Note:**  
Each upload request is logged with the client IP, file name, and request headers.

## Deployment

This project is ready to deploy on [Render](https://render.com/) using the included `Dockerfile` and `render.yaml`.

## License

MIT License
