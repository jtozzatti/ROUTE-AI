
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configura a conexão com o Gemini
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Define os campos que a IA deve extrair
class DadosOcorrencia(BaseModel):
    rodovia: str | None
    km: float | None
    sentido: str | None
    descricao: str | None


def interpretar_ocorrencia(relato: str) -> DadosOcorrencia:

    # Envia o relato para o modelo de IA
    resposta = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=relato,
        config=types.GenerateContentConfig(
            system_instruction=(
                "Você é um assistente de apoio à inspeção rodoviária. "
                "Extraia do relato a rodovia, o quilômetro, "
                "o sentido e a descrição da ocorrência. "
                "Não invente informações ausentes. "
                "Quando um campo não for informado, use null. "
                "Não tome decisões operacionais."
            ),
            response_mime_type="application/json",
            response_schema=DadosOcorrencia,
            temperature=0,
        ),
    )

    # Valida e organiza a resposta recebida
    return DadosOcorrencia.model_validate_json(resposta.text)
