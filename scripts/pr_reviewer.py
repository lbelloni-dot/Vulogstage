import os
import requests
import google.generativeai as genai

# 1. Récupération des variables d'environnement
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO = os.environ.get("GITHUB_REPOSITORY")

def main():
    if not GEMINI_API_KEY:
        print("Erreur : GEMINI_API_KEY est introuvable.")
        exit(1)

    # 2. Configuration de Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # 3. Récupérer le 'Diff' de la Pull Request via l'API GitHub
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    diff_response = requests.get(url, headers=headers)
    code_diff = diff_response.text

    # 4. Demander l'analyse à Gemini
    prompt = (
        "Tu es un développeur Senior bienveillant. Fais une revue de code sur ce 'diff' de Pull Request. "
        "Si le code est bon, dis-le. S'il y a des failles de sécurité, des problèmes de performance "
        "ou des erreurs de style, signale-les avec bienveillance.\n\n"
        f"Voici le code à analyser :\n\n{code_diff}"
    )
    
    print("Envoi du code à l'API Gemini...")
    response = model.generate_content(prompt)

    # 5. Poster le commentaire sur la Pull Request
    comment_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url_comment = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    comment_payload = {"body": response.text}
    
    requests.post(url_comment, headers=comment_headers, json=comment_payload)
    print("Revue de code postée avec succès !")

if __name__ == "__main__":
    main()
