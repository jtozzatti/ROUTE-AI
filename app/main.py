
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.voice_service import processar_audio_com_ia
from app.ai_service import interpretar_ocorrencia
from app.database import (
    inicializar_banco,
    salvar_ocorrencia,
    listar_ocorrencias,
)


# ==========================================
# CONFIGURAÇÃO DA API
# ==========================================

app = FastAPI(
    title="ROUTE AI",
    description="Assistente inteligente para operações rodoviárias",
    version="0.4.0",
)

# Inicializa o banco de dados
inicializar_banco()


# ==========================================
# MODELOS DE DADOS
# ==========================================

class Relato(BaseModel):
    texto: str


class OcorrenciaConfirmada(BaseModel):
    rodovia: str
    km: float | None = None
    sentido: str | None = None
    descricao: str
    confirmado: bool


# ==========================================
# ROTA INICIAL
# ==========================================

@app.get("/")
def inicio():
    return {
        "mensagem": "ROUTE AI funcionando!",
        "versao": "0.4.0",
    }


# ==========================================
# INTERPRETAÇÃO POR TEXTO
# ==========================================

@app.post("/ocorrencias/interpretar")
def interpretar(relato: Relato):

    if not relato.texto.strip():
        raise HTTPException(
            status_code=400,
            detail="O relato não pode estar vazio.",
        )

    try:
        # Interpreta o relato com o Gemini
        dados = interpretar_ocorrencia(relato.texto)

        return {
            "status": "aguardando_confirmacao",
            "dados": dados.model_dump(),
            "mensagem": "Confira os dados antes de registrar.",
        }

    except Exception as erro:
        print(
            f"ERRO GEMINI: {type(erro).__name__}: {erro}",
            flush=True,
        )

        raise HTTPException(
            status_code=502,
            detail="Não foi possível interpretar o relato com IA.",
        ) from erro


# ==========================================
# CONFIRMAÇÃO E REGISTRO
# ==========================================

@app.post("/ocorrencias/confirmar")
def confirmar_ocorrencia(ocorrencia: OcorrenciaConfirmada):

    # Exige confirmação explícita
    if not ocorrencia.confirmado:
        raise HTTPException(
            status_code=400,
            detail="É necessário confirmar a ocorrência.",
        )

    # Valida os campos obrigatórios
    if not ocorrencia.rodovia.strip():
        raise HTTPException(
            status_code=400,
            detail="A rodovia deve ser informada.",
        )

    if not ocorrencia.descricao.strip():
        raise HTTPException(
            status_code=400,
            detail="A descrição da ocorrência deve ser informada.",
        )

    # O quilômetro é opcional, mas não pode ser negativo
    if ocorrencia.km is not None and ocorrencia.km < 0:
        raise HTTPException(
            status_code=400,
            detail="O quilômetro não pode ser negativo.",
        )

    # Salva a ocorrência no SQLite
    id_ocorrencia = salvar_ocorrencia(ocorrencia)

    return {
        "status": "registrada",
        "id": id_ocorrencia,
        "mensagem": "Ocorrência registrada com sucesso.",
    }


# ==========================================
# HISTÓRICO DE OCORRÊNCIAS
# ==========================================

@app.get("/ocorrencias")
def consultar_ocorrencias():

    # Busca os registros armazenados
    ocorrencias = listar_ocorrencias()

    return {
        "total": len(ocorrencias),
        "ocorrencias": ocorrencias,
    }


# ==========================================
# ÁUDIO: TRANSCRIÇÃO + INTERPRETAÇÃO
# ==========================================

@app.post("/ocorrencias/audio")
async def interpretar_audio(
    arquivo: UploadFile = File(...)
):

    # Formatos de áudio permitidos
    formatos_permitidos = {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/webm",
        "audio/ogg",
        "audio/mp4",
        "audio/x-m4a",
        "audio/m4a",
    }

    # Normaliza o tipo de áudio recebido
    mime_type = (
        (arquivo.content_type or "")
        .split(";")[0]
        .strip()
        .lower()
    )

    if mime_type not in formatos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Formato de áudio não suportado.",
        )

    # Limita o tamanho do áudio a 10 MB
    tamanho_maximo = 10 * 1024 * 1024

    audio = await arquivo.read(tamanho_maximo + 1)

    if len(audio) > tamanho_maximo:
        raise HTTPException(
            status_code=413,
            detail="O áudio deve ter no máximo 10 MB.",
        )

    if not audio:
        raise HTTPException(
            status_code=400,
            detail="O arquivo de áudio está vazio.",
        )

    try:
        # Uma única chamada ao Gemini:
        # transcrição + extração dos dados
        resultado = processar_audio_com_ia(
            audio,
            mime_type,
        )

        # Separa a transcrição dos campos extraídos
        transcricao = resultado.transcricao
        dados = resultado.dados

        # Devolve a mesma estrutura esperada pelo Streamlit
        return {
            "status": "aguardando_confirmacao",
            "transcricao": transcricao,
            "dados": dados.model_dump(),
            "mensagem": (
                "Confira a transcrição e os dados "
                "antes de registrar."
            ),
        }

    except Exception as erro:
        print(
            f"ERRO AUDIO: {type(erro).__name__}: {erro}",
            flush=True,
        )

        raise HTTPException(
            status_code=502,
            detail="Não foi possível processar o áudio.",
        ) from erro
