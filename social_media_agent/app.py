import os
import yt_dlp
import requests
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from faster_whisper import WhisperModel

app = FastAPI(title="YouTube Post Generator")

# === Configurações Ollama ===
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

if not OLLAMA_BASE_URL or not OLLAMA_MODEL:
    raise RuntimeError("As variáveis OLLAMA_BASE_URL e OLLAMA_MODEL não estão definidas no .env")

# === Carregar modelo faster-whisper só 1 vez ===
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")

# === Modelo de entrada ===
class VideoURL(BaseModel):
    url: str

# === Funções utilitárias ===
def extract_video_id(url: str) -> str:
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    raise ValueError("URL do YouTube inválida")

def get_transcript(url: str) -> str | None:
    try:
        video_id = extract_video_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["pt", "en"])
        return " ".join([t["text"] for t in transcript])
    except Exception:
        return None

def download_audio(url: str) -> str:
    video_id = extract_video_id(url)
    filename = f"downloads/{video_id}.m4a"
    os.makedirs("downloads", exist_ok=True)

    if os.path.exists(filename):
        return filename

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "concurrent-fragments": 4,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename

def transcribe_with_whisper(audio_file: str) -> str:
    segments, _ = whisper_model.transcribe(audio_file, language="pt")
    return " ".join([seg.text for seg in segments])

def call_ollama(prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Falha ao chamar Ollama: {e}")

def extract_sections(text: str) -> dict:
    sections = {}
    for section in ["LinkedIn", "Instagram", "Twitter"]:
        pattern = re.compile(rf"\*\*{section} Post\*\*\s*(.*?)(?=(\*\*(LinkedIn|Instagram|Twitter) Post\*\*|$))", re.DOTALL)
        match = pattern.search(text)
        sections[section.lower()] = match.group(1).strip() if match else ""
    return sections


def generate_posts(transcript: str) -> dict:
    prompt = f"""
    Você é um especialista em marketing digital e copywriting, com foco em criar conteúdos ideais para cada rede social. 
    A partir do texto abaixo (transcrição de um vídeo do YouTube), crie posts otimizados para cada rede, todos os textos devem ser em Português do Brasil:

    **LinkedIn Post**
    - Profissional e inspirador.
    - Estruturado em parágrafos curtos, fácil leitura.
    - Tom motivacional ou educativo, reforçando autoridade e insights do tema.
    - Incluir até 3 hashtags relevantes, sem exageros.
    - Evitar emojis ou linguagem informal.

    **Instagram Post**
    - Descontraído e envolvente.
    - Utilize emojis estratégicos para reforçar emoção ou contexto.
    - Frases curtas e diretas, com storytelling ou curiosidade.
    - Incluir hashtags relevantes (5 a 10) para aumentar alcance.
    - Pode usar chamadas à ação criativas, como perguntas ou incentivos a comentar.

    **Twitter Post**
    - Direto, impactante e conciso (até 280 caracteres).
    - Mensagem clara, chamativa, que gera engajamento imediato.
    - Inclua hashtags estratégicas, no máximo 3.
    - Pode usar abreviações ou linguagem informal, mas mantendo clareza.

    Texto original:
    {transcript}
    """.strip()

    output = call_ollama(prompt)
    return extract_sections(output)

# === Endpoint principal ===
@app.post("/generate_post")
def generate_post(video: VideoURL):
    transcript = get_transcript(video.url)
    if not transcript:
        audio_path = download_audio(video.url)
        try:
            transcript = transcribe_with_whisper(audio_path)
        finally:
            try:
                os.remove(audio_path)
            except Exception:
                pass

    if not transcript or not transcript.strip():
        raise HTTPException(status_code=400, detail="Não foi possível obter transcrição.")

    posts = generate_posts(transcript)
    return posts
