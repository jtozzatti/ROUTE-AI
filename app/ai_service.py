
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError
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
    
class ResultadoAudio(BaseModel):
    transcricao: str
    dados: DadosOcorrencia

def interpretar_ocorrencia(relato: str) -> DadosOcorrencia:

    # Inicia a medição do tempo
    inicio = time.perf_counter()

    # Número máximo de tentativas
    max_tentativas = 2

    for tentativa in range(1, max_tentativas + 1):

        try:
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
            dados = DadosOcorrencia.model_validate_json(
                resposta.text
            )

            # Calcula o tempo total de processamento
            tempo = time.perf_counter() - inicio

            # Exibe o tempo no terminal do FastAPI
            print(
                f"TEMPO GEMINI: {tempo:.2f} segundos",
                flush=True
            )

            return dados

        except ServerError as erro:

            # Registra a falha temporária
            print(
                f"GEMINI INDISPONÍVEL: "
                f"tentativa {tentativa}/{max_tentativas}",
                flush=True
            )

            # Se todas as tentativas falharem,
            # devolve o erro para o FastAPI
            if tentativa == max_tentativas:
                raise

            # Aguarda antes de tentar novamente
            tempo_espera = 1

            print(
                f"Nova tentativa em {tempo_espera} segundos...",
                flush=True
            )

            time.sleep(tempo_espera)
