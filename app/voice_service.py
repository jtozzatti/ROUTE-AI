
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError

from app.ai_service import ResultadoAudio


# Carrega as variáveis de ambiente
load_dotenv()

# Configura o cliente Gemini
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def processar_audio_com_ia(
    audio: bytes,
    mime_type: str
) -> ResultadoAudio:
    """
    Transcreve e interpreta o áudio em uma única
    chamada ao Gemini.
    """

    if not audio:
        raise ValueError("O arquivo de áudio está vazio.")

    # Normaliza o formato recebido
    mime_type = (mime_type or "audio/wav").split(";")[0].lower()

    if mime_type in ("audio/x-wav", "audio/wave"):
        mime_type = "audio/wav"

    max_tentativas = 3
    inicio_total = time.perf_counter()

    for tentativa in range(1, max_tentativas + 1):
        try:
            resposta = client.models.generate_content(
                model="gemini-3.8-flash",
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

            # Valida a transcrição e os campos extraídos
            resultado = ResultadoAudio.model_validate_json(
                resposta.text
            )

            if not resultado.transcricao.strip():
                raise ValueError(
                    "O Gemini retornou uma transcrição vazia."
                )

            tempo_total = time.perf_counter() - inicio_total

            print(
                f"TEMPO ÁUDIO COMPLETO: "
                f"{tempo_total:.2f} segundos",
                flush=True
            )

            return resultado

        except ServerError as erro:
            print(
                f"GEMINI INDISPONÍVEL: "
                f"tentativa {tentativa}/{max_tentativas}: "
                f"{erro}",
                flush=True
            )

            if tentativa == max_tentativas:
                raise

            tempo_espera = 2 * tentativa
            time.sleep(tempo_espera)
