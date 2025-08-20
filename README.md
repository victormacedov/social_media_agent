# YouTube video-based social media post generator

Aplicação que gera posts para **LinkedIn**, **Instagram** e **Twitter** a partir da transcrição de vídeos do YouTube, utilizando **Whisper** para transcrição e **Ollama** para gerar os textos de marketing digital.

---

## Features

- Transcrição de vídeos do YouTube (via `youtube-transcript-api` ou áudio com `faster-whisper`).  
- Geração de posts separados para cada rede social (LinkedIn, Instagram, Twitter).  
- Prompt padronizado para criar textos otimizados para cada público.  
- Rápida execução local com cache de downloads de áudio.  

---

## Pré-requisitos

- Python 3.11+  
- [Ollama](https://ollama.com/) instalado e rodando localmente  
- ffmpeg instalado (para yt-dlp e Whisper)  

---

## Setup do Projeto

1. **Clone o repositório**

```bash
git clone <seu-repo-url>
cd <nome-do-repo>
```

2. **Crie um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```
OLLAMA_BASE_URL="http://127.0.0.1:11434"
OLLAMA_MODEL="llama3:8b"
```

> **Observação:** Ajuste o modelo conforme o disponível no Ollama.

---

## Rodando o Ollama localmente

No terminal:

```bash
ollama serve
```

> Ele deve ficar escutando na porta definida em `OLLAMA_BASE_URL` (padrão: `11434`).

---

## Rodando a API FastAPI

```bash
uvicorn app:app --reload
```

- A API ficará disponível em `http://127.0.0.1:8000`.
- Endpoint principal:

```
POST /generate_post
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=EXEMPLO"
}
```

---

## Estrutura do Projeto

```
├─ app.py               # Código principal da aplicação
├─ requirements.txt     # Dependências Python
├─ .env                 # Variáveis de ambiente (não comitar)
├─ downloads/           # Áudios baixados temporariamente
├─ .gitignore           # Ignora venv, downloads e .env
└─ README.md
```

---

## Resposta do Endpoint

Exemplo de JSON retornado:

```json
{
  "linkedin": "Texto do post do LinkedIn...",
  "instagram": "Texto do post do Instagram...",
  "twitter": "Texto do post do Twitter..."
}
```

> Todos os textos já vêm formatados para a rede social correspondente, sem quebras de linha desnecessárias.

---

## Observações

- Certifique-se de que o Ollama esteja rodando antes de fazer requisições.  
- O `faster-whisper` é mais rápido que o `openai-whisper` tradicional e funciona em CPU usando int8.  
- O download de áudio é armazenado em `downloads/` para cache, evitando downloads repetidos.
