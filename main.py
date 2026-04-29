import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Inisialisasi memori chat
chat_history = []

app = FastAPI()

# Middleware CORS: Jembatan wajib agar HTML bisa akses Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    pesan: str

# API KEY OpenRouter kamu
OPENROUTER_API_KEY = "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"

@app.post("/chat/")
def ngobrol_dengan_ai(input_user: ChatInput):
    global chat_history
    try:
        # 1. Masukkan pesan kamu ke memori
        chat_history.append({"role": "user", "content": input_user.pesan})
        
        # 2. Batasi memori: Cukup ingat 4 pesan terakhir agar tidak overload (Token Limit)
        if len(chat_history) > 4:
            chat_history = chat_history[-4:]

        # 3. Request ke OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemma-3-4b-it:free",
                "messages": [
                    # Instruksi agar AI tetap ramah sebagai asisten Agung
                    {"role": "user", "content": "Instruksi: Kamu asisten Agung PPLG. pemilik mu adalah agung. Jawab singkat, ramah, dan pakai Bahasa Indonesia."}
                ] + chat_history
            })
        )
        
        hasil = response.json()

        # 4. Ambil jawaban (Logika Anti-Bengong)
        if "choices" in hasil and len(hasil["choices"]) > 0:
            jawaban = hasil["choices"][0]["message"].get("content", "")
            
            if jawaban.strip():
                chat_history.append({"role": "assistant", "content": jawaban})
                return {"jawaban_ai": jawaban}
        
        # 5. Jika gagal dapat jawaban, tampilkan pesan error dari server
        if chat_history: chat_history.pop() # Hapus chat terakhir yang gagal biar tidak macet
        
        error_info = hasil.get("error", {}).get("message", "Server OpenRouter sedang sibuk.")
        return {"jawaban_ai": f"Duh Gung, ada masalah: {error_info}"}

    except Exception as e:
        # Reset total jika ada error sistem
        chat_history = []
        return {"error": f"Terjadi kesalahan teknis: {str(e)}"}