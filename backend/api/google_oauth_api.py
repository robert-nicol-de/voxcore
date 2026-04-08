from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlencode
import requests
import os

router = APIRouter()

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/connect/google/callback")

@router.get("/api/connect/google")
def connect_google():
    params = urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/spreadsheets.readonly",
        "access_type": "offline",
        "prompt": "consent"
    })
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    )

@router.get("/api/connect/google/callback")
def google_callback(code: str):
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    )
    tokens = token_res.json()
    access_token = tokens.get("access_token")
    # TODO: Store access_token in session/db for user
    # For demo, just redirect to a placeholder
    return RedirectResponse("/select-sheet")
