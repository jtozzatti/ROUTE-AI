import streamlit as st
import requests
import time

# ==========================================
# CONFIGURACAO DA APLICACAO
# ==========================================
st.set_page_config(
    page_title="ROUTE AI",
    page_icon="🛣️",
    layout="wide",
)

API_URL = "http://127.0.0.1:8000"


# ==========================================
# FUNCOES AUXILIARES
# ==========================================
def mostrar_erro_api(erro, mensagem):
    st.error(mensagem)

    if isinstance(erro, requests.exceptions.HTTPError):
        resposta = erro.response
        if resposta is not None:
            st.write(f"Código HTTP: {resposta.status_code}")
            try:
                st.json(resposta.json())
            except ValueError:
                st.code(resposta.text)
    else:
        st.caption(str(erro))



def processar_audio(arquivo):
    """Envia áudio gravado ou carregado para a API."""

    try:
        # Inicia a medição do tempo
        inicio = time.perf_counter()

        # Exibe feedback enquanto a IA processa o áudio
        with st.spinner(
            "🤖 Analisando ocorrência com IA... "
            "Transcrevendo áudio e identificando informações.",
            show_time=True
        ):
            resposta = requests.post(
                f"{API_URL}/ocorrencias/audio",
                files={
                    "arquivo": (
                        arquivo.name,
                        arquivo.getvalue(),
                        arquivo.type or "audio/wav",
                    )
                },
                timeout=180,
            )

            resposta.raise_for_status()

        # Calcula o tempo total da solicitação
        tempo_total = time.perf_counter() - inicio

        resultado = resposta.json()
        dados = resultado["dados"]
        transcricao = resultado["transcricao"]

        if not isinstance(dados, dict):
            raise TypeError("Dados da ocorrência inválidos")

        st.session_state["ocorrencia"] = dados
        st.session_state["transcricao"] = transcricao

        st.success("Áudio processado com sucesso!")

        st.caption(
            f"⏱️ Tempo de processamento: {tempo_total:.2f} segundos"
        )

    except requests.exceptions.RequestException as erro:
        mostrar_erro_api(
            erro,
            "Não foi possível processar o áudio."
        )

    except (ValueError, KeyError, TypeError):
        st.error(
            "A API retornou uma resposta em formato inesperado."
        )


# ==========================================
# CABECALHO
# ==========================================
st.title("🛣️ ROUTE AI")
st.caption("Intelligent Road Operations Assistant")
st.divider()

st.subheader("Registro inteligente de ocorrências")
st.write(
    "Descreva uma ocorrência rodoviária por texto ou grave um áudio "
    "diretamente na aplicação para interpretação com IA."
)

aba_texto, aba_audio = st.tabs(["📝 Relato por texto", "🎙️ Relato por áudio"])


# ==========================================
# RELATO POR TEXTO
# ==========================================
with aba_texto:
    relato = st.text_area(
        "Descreva a ocorrência:",
        placeholder=(
            "Ex.: Estou na Rodovia Anhanguera, km 35, "
            "sentido capital. Veículo parado no acostamento."
        ),
        height=150,
    )

    if st.button("Interpretar relato", type="primary"):
        if not relato.strip():
            st.warning("Digite um relato antes de continuar.")
        else:
            try:
                with st.spinner("Interpretando ocorrência..."):
                    resposta = requests.post(
                        f"{API_URL}/ocorrencias/interpretar",
                        json={"texto": relato},
                        timeout=90,
                    )
                    resposta.raise_for_status()

                resultado = resposta.json()
                st.session_state["ocorrencia"] = resultado["dados"]
                st.session_state.pop("transcricao", None)
                st.success("Relato interpretado com sucesso!")

            except requests.exceptions.RequestException as erro:
                mostrar_erro_api(erro, "Não foi possível interpretar o relato.")
            except (ValueError, KeyError, TypeError):
                st.error("A API retornou uma resposta em formato inesperado.")


# ==========================================
# RELATO POR AUDIO: GRAVACAO OU UPLOAD
# ==========================================
with aba_audio:
    opcao_audio = st.radio(
        "Como deseja fornecer o áudio?",
        ["🎤 Gravar pelo microfone", "📁 Enviar arquivo"],
        horizontal=True,
    )

    if opcao_audio == "🎤 Gravar pelo microfone":
        st.write("Grave seu relato diretamente pelo microfone do dispositivo.")
        audio_gravado = st.audio_input("Gravar relato da ocorrência")

        if audio_gravado is not None:
            st.audio(audio_gravado)
            if st.button("Transcrever e interpretar gravação", type="primary"):
                processar_audio(audio_gravado)

    else:
        arquivo_audio = st.file_uploader(
            "Selecione um arquivo de áudio:",
            type=["mp3", "wav", "m4a", "ogg", "webm"],
        )

        if arquivo_audio is not None:
            st.audio(arquivo_audio)
            if st.button("Transcrever e interpretar arquivo", type="primary"):
                processar_audio(arquivo_audio)


# ==========================================
# TRANSCRICAO
# ==========================================
if "transcricao" in st.session_state:
    st.subheader("Transcrição")
    st.info(st.session_state["transcricao"])


# ==========================================
# REVISAO E CONFIRMACAO
# ==========================================
if "ocorrencia" in st.session_state:
    st.divider()
    st.subheader("Revisar ocorrência")
    st.write(
        "Confira as informações identificadas pela IA. "
        "Você pode corrigir os campos antes de registrar."
    )

    dados = st.session_state["ocorrencia"]

    with st.form("formulario_ocorrencia"):
        rodovia = st.text_input("Rodovia", value=dados.get("rodovia") or "")

        col1, col2 = st.columns(2)
        with col1:
            km_texto = st.text_input(
                "Quilômetro",
                value=str(dados["km"]) if dados.get("km") is not None else "",
                placeholder="Ex.: 42 ou 42.5",
            )
        with col2:
            sentido = st.text_input("Sentido", value=dados.get("sentido") or "")

        descricao = st.text_area(
            "Descrição da ocorrência",
            value=dados.get("descricao") or "",
            height=120,
        )

        confirmar = st.form_submit_button(
            "Confirmar e registrar ocorrência",
            type="primary",
        )

    if confirmar:
        if not rodovia.strip() or not descricao.strip():
            st.warning("Preencha a rodovia e a descrição antes de registrar.")
        else:
            try:
                km = (
                    float(km_texto.strip().replace(",", "."))
                    if km_texto.strip()
                    else None
                )
                if km is not None and km < 0:
                    st.error("O quilômetro não pode ser negativo.")
                    st.stop()
            except ValueError:
                st.error("Quilômetro inválido. Informe um número, como 42 ou 42.5.")
                st.stop()

            ocorrencia_confirmada = {
                "rodovia": rodovia.strip(),
                "km": km,
                "sentido": sentido.strip() or None,
                "descricao": descricao.strip(),
                "confirmado": True,
            }

            try:
                with st.spinner("Registrando ocorrência..."):
                    resposta = requests.post(
                        f"{API_URL}/ocorrencias/confirmar",
                        json=ocorrencia_confirmada,
                        timeout=30,
                    )
                    resposta.raise_for_status()

                resultado = resposta.json()
                st.success(
                    "Ocorrência registrada com sucesso! "
                    f"ID: {resultado.get('id', 'não informado')}"
                )
                st.session_state.pop("ocorrencia", None)
                st.session_state.pop("transcricao", None)
                st.info("O registro foi confirmado. Você pode iniciar uma nova ocorrência.")

            except requests.exceptions.RequestException as erro:
                mostrar_erro_api(erro, "Não foi possível registrar a ocorrência.")
            except (ValueError, TypeError):
                st.error("A API retornou uma resposta em formato inesperado.")


# ==========================================
# HISTORICO DE OCORRENCIAS
# ==========================================
st.divider()
st.subheader("📋 Histórico de ocorrências")
st.write("Consulte as ocorrências registradas no sistema.")

if st.button("🔄 Atualizar histórico"):
    st.rerun()

try:
    resposta = requests.get(f"{API_URL}/ocorrencias", timeout=15)
    resposta.raise_for_status()
    resultado = resposta.json()
    ocorrencias = resultado.get("ocorrencias", [])

    if ocorrencias:
        st.metric("Total de ocorrências", resultado.get("total", len(ocorrencias)))
        tabela = []
        for ocorrencia in ocorrencias:
            tabela.append(
                {
                    "ID": ocorrencia.get("id"),
                    "Rodovia": ocorrencia.get("rodovia"),
                    "KM": ocorrencia.get("km"),
                    "Sentido": ocorrencia.get("sentido"),
                    "Descrição": ocorrencia.get("descricao"),
                    "Registrado em": ocorrencia.get("criado_em"),
                }
            )

        st.dataframe(tabela, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma ocorrência registrada até o momento.")

except requests.exceptions.RequestException as erro:
    mostrar_erro_api(erro, "Não foi possível carregar o histórico de ocorrências.")
except (ValueError, TypeError, AttributeError):
    st.error("A API retornou um histórico em formato inesperado.")
