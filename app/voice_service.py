
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

from app.ai_service import ResultadoAudio


# ==========================================
# CONFIGURAÇÃO DO GEMINI
# ==========================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Modelos utilizados no processamento
MODELOS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash"
]


# ==========================================
# PROCESSAMENTO INTELIGENTE DE ÁUDIO
# ==========================================

def processar_audio_com_ia(
    audio: bytes,
    mime_type: str
) -> ResultadoAudio:
    """
    Transcreve e interpreta o áudio em uma única
    chamada por modelo.

    Se o modelo principal estiver indisponível,
    tenta automaticamente o modelo alternativo.
    """

    if not audio:
        raise ValueError("O arquivo de áudio está vazio.")

    # Normaliza o formato do áudio
    mime_type = (mime_type or "audio/wav").split(";")[0].lower()

    if mime_type in ("audio/x-wav", "audio/wave"):
        mime_type = "audio/wav"

    inicio_total = time.perf_counter()

    # Percorre os modelos disponíveis
    for indice, modelo in enumerate(MODELOS, start=1):

        try:
            inicio_modelo = time.perf_counter()

            print(
                f"PROCESSANDO ÁUDIO COM: {modelo}",
                flush=True
            )

            resposta = client.models.generate_content(
                model=modelo,
                contents=[
                    (
                        "Analise este áudio de uma ocorrência "
                        "rodoviária em português brasileiro. "
                        "Transcreva fielmente o que foi falado "
                        "e extraia rodovia, km, sentido e "
                        "descrição da ocorrência. "
                        "Não invente informações ausentes. "
                        "Use null para campos não informados. "
                        "Não tome decisões operacionais."
                    ),
                    types.Part.from_bytes(
                        data=audio,
                        mime_type=mime_type
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ResultadoAudio,
                    temperature=0
                )
            )

            if not resposta.text:
                raise ValueError(
                    "O Gemini não retornou uma resposta."
                )

            resultado = ResultadoAudio.model_validate_json(
                resposta.text
            )

            if not resultado.transcricao.strip():
                raise ValueError(
                    "O Gemini retornou uma transcrição vazia."
                )

            tempo_modelo = time.perf_counter() - inicio_modelo
            tempo_total = time.perf_counter() - inicio_total

            print(
                f"MODELO UTILIZADO: {modelo}",
                flush=True
            )

            print(
                f"TEMPO DO MODELO: {tempo_modelo:.2f} segundos",
                flush=True
            )

            print(
                f"TEMPO ÁUDIO COMPLETO: {tempo_total:.2f} segundos",
                flush=True
            )

            return resultado

        except (ServerError, ClientError) as erro:

            print(
                f"MODELO INDISPONÍVEL: {modelo} "
                f"({indice}/{len(MODELOS)}): {erro}",
                flush=True
            )

            # Se ainda existe outro modelo, tenta o próximo
            if indice < len(MODELOS):
                print(
                    "ATIVANDO MODELO ALTERNATIVO...",
                    flush=True
                )
                continue

            # Todos os modelos falharam
            raise
