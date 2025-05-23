# podtrimmer-backend

Backend API Server for Podtrimmer App

## Overview

This project provides a FastAPI backend for uploading and storing podcast RSS feeds. It validates XML content and uploads it to Supabase Storage, making the feed publicly accessible.

## Features

- REST API endpoint to upload podcast RSS feeds as XML
- XML validation before upload
- Storage of feeds in Supabase Storage bucket (`podcast-feeds`)
- Public URL returned for each uploaded feed
- API key authentication for secure uploads

## Requirements

- Python 3.11+
- [Supabase](https://supabase.com/) project with a storage bucket named `podcast-feeds`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/podtrimmer-backend.git
    cd podtrimmer-backend
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory with the following variables:
    ```
    SUPABASE_URL=your-supabase-url
    SUPABASE_SERVICE_ROLE=your-service-role-key
    API_KEY=your-secret-api-key
    ```

## Running Locally

Start the server with:

```sh
uvicorn app.main:app --reload
```
