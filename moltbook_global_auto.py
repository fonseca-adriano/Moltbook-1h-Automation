import os
import requests
import json
import google.generativeai as genai
import random

# CONFIGURAÇÃO DE SEGURANÇA
GEMINI_API_KEY = os.getenv("AIzaSyAPQerxVh9q7w0UlvJScAwuv3k_rLRy6sM")
MOLTBOOK_TOKEN = os.getenv("moltbook_sk_abvIcVb98hL7TIUG_4A0TGLfNXiIYFgl")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def gerar_post_ingles():
    # A lista PRECISA estar definida aqui dentro para a função enxergá-la
    topics = [
        "Advanced piano techniques", "Music therapy and neuroscience", 
        "Systems Analysis in 2026", "A24 cinematography style", "Horror movie tropes", 
        "Humanoid robotics evolution", "Space exploration news", "Quantum physics", 
        "Cyberpunk aesthetics", "Global tech economy", "AI ethics", "Black hole theories",
        "The evolution of body horror", "Neuralink and brain-computer interfaces",
        "The mystery of Dark Matter", "Sustainable data centers in 2026"
    ]
    
    selected_topic = random.choice(topics)
    
    prompt = f"""
    Write a short social media post in English about: {selected_topic}.
    Return the result strictly as a JSON object with 'title' and 'content' keys.
    Do not include any other text or markdown formatting.
    """
    
    response = model.generate_content(prompt)
    clean_text = response.text.strip()
    
    # Limpeza manual caso a IA envie markdown
    if "```json" in clean_text:
        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_text:
        clean_text = clean_text.split("```")[1].split("```")[0].strip()
        
    return json.loads(clean_text)

def executar_agente():
    try:
        print("🧠 Selecting a topic and generating content...")
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
            print(f"❌ API Error: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"🚨 Traceback Error: {e}")

if __name__ == "__main__":
    executar_agente()
