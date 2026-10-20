
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega a chave de API
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def transcrever_audio(audio: bytes, mime_type: str) -> str:
    # Envia o áudio para o Gemini
    resposta = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[
            "Transcreva este áudio em português brasileiro. "
            "Retorne somente o texto falado, sem explicações.",
            types.Part.from_bytes(
                data=audio,
                mime_type=mime_type
            )
        ]
    )

    if not resposta.text:
        raise ValueError("O modelo não retornou uma transcrição.")

    return resposta.text.strip()
