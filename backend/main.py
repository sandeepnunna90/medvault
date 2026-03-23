from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="MedVault API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to Streamlit Cloud URL after deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "medvault-api"}
