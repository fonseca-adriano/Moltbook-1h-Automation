import os
import requests
import json
import google.generativeai as genai
import random

# Busca as chaves configuradas no GitHub Secrets
GEMINI_API_KEY = os.getenv("AIzaSyAPQerxVh9q7w0UlvJScAwuv3k_rLRy6sM")
MOLTBOOK_TOKEN = os.getenv("moltbook_sk_abvIcVb98hL7TIUG_4A0TGLfNXiIYFgl")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def gerar_post_ingles():
    topics = [
        "Modern cinematography trends", "Neuroscience of music therapy",
        "Future of humanoid robotics", "Quantum computing breakthroughs",
        "Space exploration and the Fermi Paradox", "Cybernetic enhancements",
        "The evolution of horror in digital media", "Piano improvisation theory",
        "Systems Analysis in the age of AI", "Global economic shifts in 2026"
    ]
    
    selected_topic = random.choice(topics)
    
    prompt = f"""
    Write a short, sophisticated social media post for an AI network.
    Topic: {selected_topic}. Language: Strictly North American English.
    Style: Insightful and mysterious. Maximum 280 characters.
    Return ONLY a JSON: {{"title": "...", "content": "..."}}
    """
    
    response = model.generate_content(prompt)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

def executar_agente():
    post_data = gerar_post_ingles()
    url_base = "https://www.moltbook.com/api/v1"
    headers = {"Authorization": f"Bearer {MOLTBOOK_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "submolt_name": "general",
        "title": post_data['title'],
        "content": post_data['content']
    }

    print(f"🚀 Posting: {post_data['title']}")
    res = requests.post(f"{url_base}/posts", headers=headers, json=payload)
    
    if res.status_code in [200, 201]:
        data = res.json()
        v_obj = data.get("verification", {})
        v_code = data.get("verification_code") or v_obj.get("verification_code")
        challenge = data.get("challenge_text") or v_obj.get("challenge_text")

        if v_code and challenge:
            prompt_math = f"Solve this math and return ONLY the number: {challenge}"
            math_res = model.generate_content(prompt_math).text.strip()
            requests.post(f"{url_base}/verify", headers=headers, json={"verification_code": v_code, "answer": math_res})
            print(f"✅ Verified: {math_res}")
        else:
            print("✨ Published successfully.")
    else:
        print(f"❌ Error: {res.text}")

if __name__ == "__main__":
    executar_agente()
