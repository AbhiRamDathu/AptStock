from fastapi import APIRouter, HTTPException
import os
import requests

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.get("/token")
async def get_voice_token():
    api_key = os.getenv("ASSEMBLYAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ASSEMBLYAI_API_KEY is not configured"
        )

    try:
        response = requests.get(
            "https://agents.assemblyai.com/v1/token",
            params={"expires_in_seconds": 300},
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            timeout=10
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"AssemblyAI token request failed: {str(e)}"
        )