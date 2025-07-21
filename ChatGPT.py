import g4f

# Preferred models (fast and smart)
PREFERRED_MODELS = [
    "gpt-4o", "gpt-3.5-turbo", "claude-3.5-haiku", "gemini-1-5-pro"
]

# Get available providers
available_providers = g4f.Provider.__providers__

def get_working_provider():
    for provider in available_providers:
        try:
            models = provider.models
            for model in PREFERRED_MODELS:
                if model in models:
                    return provider, model
        except Exception:
            continue
    return None, None

provider, model = get_working_provider()

if provider is None:
    print("❌ No working provider/model found. Try updating g4f or installing more providers.")
else:
    print(f"🤖 ChatBot Ready — Using {provider.__name__} with model {model} (Type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Bot: See you later! 👋")
            break

        try:
            response = g4f.ChatCompletion.create(
                model=model,
                provider=provider(),
                messages=[{"role": "user", "content": user_input}]
            )
            print("Bot:", response)
        except Exception as e:
            print("❌ Error:", e)