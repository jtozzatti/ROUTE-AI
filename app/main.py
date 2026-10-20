
from fastapi import FastAPI, HTTPException, UploadFile, File
from app.voice_service import transcrever_audio
from pydantic import BaseModel

from app.ai_service import interpretar_ocorrencia
from app.database import (
    inicializar_banco,
    salvar_ocorrencia,
    listar_ocorrencias
)

app = FastAPI(
    title="ROUTE AI",
    description="Assistente inteligente para operações rodoviárias",
    version="0.3.0"
)

# Cria a tabela de ocorrências
inicializar_banco()


class Relato(BaseModel):
    texto: str


class OcorrenciaConfirmada(BaseModel):
    rodovia: str
    km: float
    sentido: str
    descricao: str
    confirmado: bool


@app.get("/")
def inicio():
    return {
        "mensagem": "ROUTE AI funcionando!",
        "versao": "0.3.0"
    }


@app.post("/ocorrencias/interpretar")
def interpretar(relato: Relato):
    try:
        dados = interpretar_ocorrencia(relato.texto)

        return {
            "status": "aguardando_confirmacao",
            "dados": dados.model_dump(),
            "mensagem": "Confira os dados antes de registrar."
        }

    except Exception as erro:
        print(f"ERRO GEMINI: {type(erro).__name__}: {erro}")

        raise HTTPException(
            status_code=502,
            detail="Não foi possível interpretar o relato com IA."
        )


@app.post("/ocorrencias/confirmar")
def confirmar_ocorrencia(ocorrencia: OcorrenciaConfirmada):

    # Impede o registro sem confirmação explícita
    if not ocorrencia.confirmado:
        raise HTTPException(
            status_code=400,
            detail="É necessário confirmar a ocorrência."
        )

    # Salva os dados no banco
    id_ocorrencia = salvar_ocorrencia(ocorrencia)

    return {
        "status": "registrada",
        "id": id_ocorrencia,
        "mensagem": "Ocorrência registrada com sucesso."
    }

@app.get("/ocorrencias")
def consultar_ocorrencias():
    # Busca todos os registros armazenados
    ocorrencias = listar_ocorrencias()

    return {
        "total": len(ocorrencias),
        "ocorrencias": ocorrencias
    }

@app.post("/ocorrencias/audio")
async def interpretar_audio(arquivo: UploadFile = File(...)):

    # Aceita somente formatos de áudio definidos
    formatos_permitidos = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/x-m4a",
    "audio/m4a"
}

    if arquivo.content_type not in formatos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Formato de áudio não suportado."
        )

    # Limita o tamanho do arquivo a 10 MB
    audio = await arquivo.read(10 * 1024 * 1024 + 1)

    if len(audio) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="O áudio deve ter no máximo 10 MB."
        )

    try:
        # Converte áudio em texto
        transcricao = transcrever_audio(
            audio,
            arquivo.content_type
        )

        # Extrai os dados da ocorrência
        dados = interpretar_ocorrencia(transcricao)

        return {
            "status": "aguardando_confirmacao",
            "transcricao": transcricao,
            "dados": dados.model_dump(),
            "mensagem": "Confira a transcrição e os dados antes de registrar."
        }

    except Exception as erro:
        print(f"ERRO AUDIO: {type(erro).__name__}: {erro}")

        raise HTTPException(
            status_code=502,
            detail="Não foi possível processar o áudio."
        )
