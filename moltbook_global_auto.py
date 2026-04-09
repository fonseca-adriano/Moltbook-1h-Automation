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
    topics = [
        "Advanced piano techniques", "Music therapy and neuroscience", 
        "Systems Analysis in 2026", "A24 cinematography style", "Horror movie tropes", 
        "Humanoid robotics evolution", "Space exploration news", "Quantum physics", 
        "Cyberpunk aesthetics", "Global tech economy", "AI ethics", "Black hole theories",
        "The evolution of body horror", "Neuralink and brain-computer interfaces",
        "The mystery of Dark Matter", "Sustainable data centers in 2026"
    ]
    
    selected_topic = random.choice(topics)
    prompt = f"Write a short social media post in English about: {selected_topic}. Return strictly as JSON with 'title' and 'content' keys."
    
    response = model.generate_content(prompt)
    clean_text = response.text.strip()
    if "```json" in clean_text:
        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_text:
        clean_text = clean_text.split("```")[1].split("```")[0].strip()
    return json.loads(clean_text)

def interagir_com_a_rede():
    print("👀 Scanning the network for interesting posts...")
    url_base = "https://www.moltbook.com/api/v1"
    headers = {"Authorization": f"Bearer {MOLTBOOK_TOKEN}", "Content-Type": "application/json"}

    try:
        # Busca os posts recentes da timeline global
        res = requests.get(f"{url_base}/posts", headers=headers)
        if res.status_code == 200:
            posts = res.json().get("posts", [])
            # Comenta nos 3 posts mais recentes (para não exagerar)
            for post in posts[:3]:
                post_id = post.get("id")
                post_content = post.get("content")
                
                # Gemini cria um comentário baseado no contexto do post alheio
                prompt_comment = f"""
                As an intelligent AI agent, read this post: "{post_content}"
                Write a brilliant, short 1-sentence comment in English. 
                Be witty or insightful. No hashtags.
                """
                comment_text = model.generate_content(prompt_comment).text.strip()
                
                # Envia o comentário
                comm_res = requests.post(f"{url_base}/posts/{post_id}/comments", 
                                        headers=headers, 
                                        json={"content": comment_text})
                
                if comm_res.status_code in [200, 201]:
                    print(f"💬 Commented on post {post_id}: {comment_text}")
    except Exception as e:
        print(f"⚠️ Error during interaction: {e}")

def executar_agente():
    try:
        # PARTE 1: Criar um Post Novo
        print("🧠 Generating new post content...")
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
        
        # Lógica de verificação automática (se houver desafio matemático)
        if res.status_code in [200, 201]:
            data = res.json()
            v_obj = data.get("verification", {})
            v_code = data.get("verification_code") or v_obj.get("verification_code")
            challenge = data.get("challenge_text") or v_obj.get("challenge_text")

            if v_code and challenge:
                math_res = model.generate_content(f"Solve: {challenge}. Return only the number.").text.strip()
                requests.post(f"{url_base}/verify", headers=headers, json={"verification_code": v_code, "answer": math_res})
                print(f"✅ Verified: {math_res}")
            
            # PARTE 2: Interagir (Comentar nos outros)
            # Só comentamos se o nosso post deu certo para manter o fluxo
            interagir_com_a_rede()
            
        else:
            print(f"❌ API Error: {res.status_code}")
            
    except Exception as e:
        print(f"🚨 Traceback Error: {e}")

if __name__ == "__main__":
    executar_agente()
