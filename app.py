from flask import Flask, request, jsonify, render_template
import g4f
from g4f import Provider
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

chat_memory = {}

PREFERRED_MODELS = [
    "gpt-4o", "gpt-4o-mini", "gemini-1-5-flash",
    "claude-3.5-haiku", "llama-3.3-70b", "gpt-3.5-turbo"
]

def get_working_provider():
    for prov in Provider.__providers__:
        try:
            for model in getattr(prov, "models", []):
                if model in PREFERRED_MODELS:
                    g4f.ChatCompletion.create(
                        model=model,
                        provider=prov(),
                        messages=[{"role": "user", "content": "ping"}],
                        timeout=8
                    )
                    return prov, model
        except Exception:
            continue
    return None, None

provider, model = get_working_provider()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global provider, model
    data = request.get_json()
    user_text = data.get('text', '')
    lang = data.get('lang', 'en')
    user_ip = request.remote_addr

    if user_ip not in chat_memory:
        chat_memory[user_ip] = []

    if user_text.lower().startswith("image of"):
        prompt = user_text[9:].strip()
        image_urls = [
            f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}",
            f"https://lexica.art/?q={prompt.replace(' ', '%20')}"
        ]
        return jsonify({"type": "image", "urls": image_urls})

    chat_memory[user_ip].append({"role": "user", "content": user_text})

    try:
        res = g4f.ChatCompletion.create(
            model=model,
            provider=provider(),
            messages=chat_memory[user_ip]
        )
    except Exception:
        provider, model = get_working_provider()
        if not provider:
            return jsonify({"type": "error", "message": "No working provider"})
        res = g4f.ChatCompletion.create(
            model=model,
            provider=provider(),
            messages=chat_memory[user_ip]
        )

    chat_memory[user_ip].append({"role": "assistant", "content": res})

    audio_file = None
    try:
        audio_file = f"static/{uuid.uuid4()}.mp3"
        tts = gTTS(res, lang=lang)
        tts.save(audio_file)
    except Exception:
        audio_file = None

    return jsonify({
        "type": "text",
        "response": res,
        "audio": audio_file,
        "history": chat_memory[user_ip][-10:]
    })

if __name__ == '__main__':
    app.run(debug=True)
