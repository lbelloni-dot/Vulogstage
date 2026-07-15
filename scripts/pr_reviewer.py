import os
import requests

# 1. Variables d'environnement
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO = os.environ.get("GITHUB_REPOSITORY")

def main():
    if not GEMINI_API_KEY:
        print("Erreur : GEMINI_API_KEY est introuvable.")
        exit(1)

    # 2. Récupérer le code de la Pull Request
    headers_gh = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url_gh = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    diff_response = requests.get(url_gh, headers=headers_gh)
    code_diff = diff_response.text

    # 3. Préparer la question
    prompt = (
        "Tu es un développeur Senior bienveillant. Fais une revue de code sur ce 'diff'. "
        f"Voici le code à analyser :\n\n{code_diff}"
    )

    # 4. REQUÊTE DIRECTE À L'API GEMINI (Sans bibliothèque Google)
    print("Envoi du code via requête HTTP directe...")
    
    # On teste avec le modèle PRO, souvent moins sujet aux 404 sur les nouveaux comptes
    url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
    
    headers_gemini = {"Content-Type": "application/json"}
    payload_gemini = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response_gemini = requests.post(url_gemini, headers=headers_gemini, json=payload_gemini)
    
    # Si ça échoue, on affiche la vraie erreur renvoyée par le serveur
    if response_gemini.status_code != 200:
        print(f"ÉCHEC DE L'API. Code HTTP: {response_gemini.status_code}")
        print(f"Détail de l'erreur brute : {response_gemini.text}")
        exit(1)

    # 5. Extraction de la réponse et publication
    data = response_gemini.json()
    ai_review = data['candidates'][0]['content']['parts'][0]['text']

    comment_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url_comment = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    
    requests.post(url_comment, headers=comment_headers, json={"body": ai_review})
    print("Revue de code postée avec succès !")

if __name__ == "__main__":
    main()
