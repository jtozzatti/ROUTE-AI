# 🛣️ ROUTE AI

### Intelligent Road Operations Assistant

**Assistente inteligente para apoio às operações rodoviárias, utilizando Inteligência Artificial Generativa, processamento de linguagem natural e reconhecimento de voz.**

O **ROUTE AI** é um projeto de Inteligência Artificial desenvolvido para explorar como modelos generativos podem auxiliar profissionais de inspeção rodoviária no registro e na consulta de informações operacionais.

A proposta é simplificar o registro de ocorrências por meio de interações em linguagem natural, permitindo que o profissional descreva uma situação por texto ou áudio e receba automaticamente um conjunto de informações estruturadas para revisão e confirmação.

O projeto está sendo desenvolvido como um protótipo acadêmico, inspirado em desafios reais de operações rodoviárias, com foco em **IA aplicada, automação de processos, integração de APIs e desenvolvimento de software**.

---

## 🎯 Objetivo

Desenvolver um assistente de IA capaz de apoiar o trabalho de agentes de inspeção de tráfego, reduzindo a necessidade de preenchimento manual de informações e facilitando a organização dos registros operacionais.

O ROUTE AI busca responder à seguinte questão:

> Como utilizar Inteligência Artificial Generativa e interfaces de voz para tornar o registro de ocorrências rodoviárias mais simples, estruturado e eficiente?

A solução prioriza três princípios:

- **Simplicidade:** interação por linguagem natural, sem exigir comandos complexos.
- **Confiabilidade:** revisão e confirmação humana antes do registro.
- **Rastreabilidade:** armazenamento estruturado das ocorrências para consultas posteriores.

## 💡 Contexto e problema

Durante atividades de inspeção rodoviária, profissionais precisam identificar situações, comunicar informações e registrar ocorrências de maneira organizada.

Essas atividades podem envolver o preenchimento de campos como rodovia, quilômetro, sentido e descrição da situação encontrada.

O ROUTE AI propõe utilizar IA para transformar relatos espontâneos em informações estruturadas, oferecendo apoio ao registro sem substituir a avaliação e a responsabilidade dos profissionais.

**Exemplo de relato:**

> "Estou na Rodovia Anhanguera, quilômetro 35, sentido capital. Encontrei um veículo parado no acostamento."

**Resultado esperado:**

```json
{
  "rodovia": "Anhanguera",
  "km": 35,
  "sentido": "capital",
  "descricao": "Veículo parado no acostamento"
}
```

Os dados são apresentados para conferência antes de serem registrados.

---

## ⚙️ Funcionalidades implementadas

### 1. Interpretação de ocorrências com IA

A aplicação recebe relatos em linguagem natural e utiliza o Google Gemini para identificar e estruturar informações relevantes.

**Endpoint:** `POST /ocorrencias/interpretar`

Campos extraídos:

- Rodovia
- Quilômetro
- Sentido
- Descrição da ocorrência

Quando uma informação não está presente no relato, o modelo é orientado a não inventá-la.

### 2. Transcrição e interpretação de áudio

O sistema recebe arquivos de áudio, utiliza o Gemini para transcrever a fala e encaminha o texto resultante ao serviço de interpretação.

**Endpoint:** `POST /ocorrencias/audio`

Fluxo:

1. Recebimento do arquivo de áudio.
2. Transcrição da fala.
3. Extração dos dados da ocorrência.
4. Retorno da transcrição e dos campos estruturados.
5. Revisão humana antes do registro.

O protótipo foi testado com sucesso utilizando um arquivo `.m4a`.

### 3. Confirmação e registro de ocorrências

Após revisar as informações, o usuário pode confirmar o registro por meio de uma requisição específica.

**Endpoint:** `POST /ocorrencias/confirmar`

A confirmação é obrigatória para que os dados sejam armazenados no banco SQLite.

Atualmente, essa confirmação é realizada pela documentação interativa da API (Swagger).

### 4. Consulta de ocorrências

Os registros armazenados podem ser recuperados por meio de uma rota de consulta.

**Endpoint:** `GET /ocorrencias`

A resposta inclui a quantidade de ocorrências e seus respectivos dados, como identificador, localização, descrição e data de criação.

---

## 🧠 Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Linguagem principal do projeto |
| FastAPI | Desenvolvimento da API REST |
| Google Gemini | Interpretação de relatos e transcrição de áudio |
| Google Gen AI SDK | Integração com os modelos Gemini |
| Pydantic | Definição e validação de estruturas de dados |
| SQLite | Armazenamento local das ocorrências |
| Uvicorn | Execução do servidor da API |
| python-dotenv | Carregamento das variáveis de ambiente |
| python-multipart | Recebimento de arquivos de áudio |

## 🏗️ Arquitetura atual

```text
                 AGENTE RODOVIÁRIO
                        |
                 Relato ou áudio
                        |
                        v
                  FASTAPI (API)
                        |
              +---------+---------+
              |                   |
              v                   v
        Relato em texto      Arquivo de áudio
              |                   |
              |                   v
              |            Gemini (transcrição)
              |                   |
              +---------+---------+
                        |
                        v
              Gemini (interpretação)
                        |
                        v
              Dados estruturados
                        |
                        v
                Revisão humana
                        |
                        v
               Confirmação via API
                        |
                        v
                  SQLite (banco)
                        |
                        v
                Consulta via API
```

A arquitetura separa o processamento de linguagem natural da persistência dos dados, permitindo a evolução independente de cada componente.

**Importante:** a IA auxilia na interpretação das informações, mas não realiza decisões operacionais, acionamentos de emergência ou comunicações automáticas com o Centro de Controle Operacional (CCO).

---

## 📂 Estrutura do projeto

```text
route-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── ai_service.py
│   ├── voice_service.py
│   └── database.py
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── route_ai.db
```

**Descrição dos arquivos:**

- `main.py`: definição das rotas da API.
- `ai_service.py`: integração com o Gemini para interpretar relatos.
- `voice_service.py`: transcrição de arquivos de áudio.
- `database.py`: criação, gravação e consulta de registros no SQLite.
- `.env`: configuração local da chave de API.
- `requirements.txt`: dependências do projeto.
- `route_ai.db`: banco SQLite criado localmente.

O arquivo `.env`, o ambiente virtual e o banco local não devem ser enviados ao repositório.

---

## 🚀 Como executar localmente

### Pré-requisitos

- Python instalado.
- Git instalado (para clonar o repositório).
- Chave de API do Google Gemini.
- Acesso à internet para utilizar os serviços do Gemini.

### 1. Obter o projeto

Clone o repositório quando estiver publicado:

```bash
git clone URL_DO_REPOSITORIO
cd route-ai
```

Ou abra a pasta do projeto diretamente no VS Code.

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

No Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar a API do Gemini

Crie um arquivo `.env` na pasta principal do projeto:

```dotenv
GEMINI_API_KEY=SUA_CHAVE_AQUI
```

A chave pode ser gerada no [Google AI Studio](https://aistudio.google.com/apikey).

**Nunca publique sua chave de API no GitHub.**

### 5. Iniciar o servidor

```bash
python -m uvicorn app.main:app --reload
```

Acesse a documentação interativa:

**http://127.0.0.1:8000/docs**

---

## 🧪 Testes realizados

Até o momento, foram realizados testes manuais utilizando o Swagger UI.

| Funcionalidade | Resultado |
|---|---|
| Inicialização da API FastAPI | Concluído |
| Interpretação de relato textual com Gemini | Concluído |
| Registro de ocorrência no SQLite | Concluído |
| Consulta de ocorrência armazenada | Concluído |
| Transcrição de arquivo `.m4a` | Concluído |
| Extração de dados a partir de áudio | Concluído |

### Exemplo de teste por áudio

Durante um teste, o sistema recebeu um relato sobre um veículo parado na Rodovia Anhanguera, quilômetro 35, sentido capital.

A API retornou uma transcrição e os seguintes dados:

```json
{
  "status": "aguardando_confirmacao",
  "dados": {
    "rodovia": "Anhanguera",
    "km": 35,
    "sentido": "capital",
    "descricao": "veículo parado no acostamento"
  }
}
```

O teste retornou **HTTP 200 OK**, demonstrando o funcionamento da integração entre recebimento de áudio, transcrição e interpretação.

Esses testes comprovam o funcionamento dos fluxos básicos em ambiente local, mas não representam uma validação completa para utilização operacional.

---

## 🗺️ Roadmap de desenvolvimento

### Fase 1 — Backend e IA

- [x] Configuração do ambiente Python.
- [x] Criação da API com FastAPI.
- [x] Integração com Google Gemini.
- [x] Interpretação de relatos em linguagem natural.
- [x] Criação do banco SQLite.
- [x] Registro mediante confirmação.
- [x] Consulta de ocorrências.
- [x] Transcrição e interpretação de áudio.

### Fase 2 — Interface visual

- [ ] Criar interface com Streamlit.
- [ ] Integrar envio de áudio pela interface.
- [ ] Permitir entrada de relatos por texto.
- [ ] Exibir os dados extraídos para revisão.
- [ ] Permitir correção dos campos antes da confirmação.
- [ ] Integrar o registro ao SQLite.
- [ ] Exibir histórico de ocorrências.

### Fase 3 — Evolução do assistente

- [ ] Consulta a procedimentos operacionais autorizados.
- [ ] Avaliação de RAG para recuperação de documentos.
- [ ] Melhoria da validação dos dados extraídos.
- [ ] Implementação de autenticação e controle de acesso.
- [ ] Ampliação de logs e rastreabilidade.
- [ ] Avaliação de alternativas para funcionamento com conectividade limitada.
- [ ] Testes automatizados e tratamento avançado de erros.
- [ ] Preparação para demonstração e disponibilização da aplicação.

---

## 🔒 Segurança e limitações

O ROUTE AI é atualmente um **protótipo acadêmico em desenvolvimento**.

As principais limitações são:

- O processamento com Gemini depende de conexão com a internet.
- A aplicação ainda não possui autenticação de usuários.
- A confirmação humana é realizada por meio de requisições à API.
- A transcrição e a interpretação podem apresentar erros.
- O sistema não está integrado aos sistemas operacionais da Motiva.
- Não há validação para uso em operações rodoviárias reais.
- O funcionamento offline ainda não foi implementado.

O projeto adota como princípio que informações interpretadas por IA devem ser verificadas antes do registro definitivo.

**Não utilizar dados operacionais sensíveis ou gravações reais sem autorização e controles adequados.**

---

## 🎓 Contexto acadêmico

O ROUTE AI está sendo desenvolvido como projeto acadêmico voltado à aplicação prática de Inteligência Artificial Generativa em um cenário de operações rodoviárias.

A solução é inspirada no desafio proposto pela **Motiva**, com foco em interfaces de voz, automação de registros e apoio a profissionais em campo.

O desenvolvimento permite explorar conceitos de:

- Inteligência Artificial Generativa e modelos de linguagem.
- Processamento de linguagem natural.
- Reconhecimento e transcrição de voz.
- Desenvolvimento de APIs REST.
- Modelagem e persistência de dados.
- Arquitetura de sistemas inteligentes.
- Human-in-the-loop (validação humana).

Este repositório representa um trabalho acadêmico independente, não um produto oficial ou sistema operacional da Motiva.

---

## 📌 Status do projeto

**Em desenvolvimento — Backend funcional, interface visual planejada.**

O próximo marco é a implementação de uma interface com Streamlit, permitindo utilizar os recursos existentes de forma mais intuitiva, sem depender diretamente do Swagger.

---

## 📄 Licença

Licença ainda não definida.

---

**ROUTE AI — Transformando relatos em informações estruturadas com Inteligência Artificial.**
