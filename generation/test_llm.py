import ollama

resp = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Say hello in five words."}],
)
print(resp["message"]["content"])
