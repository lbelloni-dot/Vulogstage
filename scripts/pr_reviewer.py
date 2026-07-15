import os
import requests

# 1. Récupération des variables d'environnement
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO = os.environ.get("GITHUB_REPOSITORY")

def main():
    if not GEMINI_API_KEY:
        print("Erreur : GEMINI_API_KEY est introuvable.")
        exit(1)

    # 2. Récupérer le 'Diff' de la Pull Request
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url_diff = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    diff_response = requests.get(url_diff, headers=headers)
    
    if diff_response.status_code != 200:
        print(f"Impossible de récupérer le diff. Code : {diff_response.status_code}")
        exit(1)
        
    code_diff = diff_response.text

    # 3. Construire le prompt pour l'IA
    prompt = (
        "Tu es un développeur Senior bienveillant. Fais une revue de code sur ce 'diff' de Pull Request. "
        "Si le code est bon, dis-le. S'il y a des failles de sécurité, des problèmes de performance "
        "ou des erreurs de style, signale-les avec bienveillance.\n\n"
        f"Voici le code à analyser :\n\n{code_diff}"
    )

    # 4. Appeler l'API Gemini (Configuration spéciale pour clé AQ)
    print("Envoi du code à l'API Gemini...")
    gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # Pour les clés AQ, on passe la clé dans l'en-tête "x-goog-api-key" au lieu de l'URL
    gemini_headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(gemini_url, headers=gemini_headers, json=payload)
    
    if response.status_code != 200:
        print(f"Erreur de l'API Gemini (Code {response.status_code}) : {response.text}")
        exit(1)

    # Extraction de la réponse textuelle
    try:
        review_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Erreur lors de la lecture de la réponse de Gemini : {e}")
        print("Réponse brute :", response.text)
        exit(1)

    # 5. Poster le commentaire sur la Pull Request
    comment_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url_comment = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    comment_payload = {"body": review_text}
    
    post_response = requests.post(url_comment, headers=comment_headers, json=comment_payload)
    
    if post_response.status_code == 201:
        print("Revue de code postée avec succès !")
    else:
        print(f"Impossible de poster le commentaire. Code : {post_response.status_code}, Réponse : {post_response.text}")
        exit(1)

if __name__ == "__main__":
    main()
