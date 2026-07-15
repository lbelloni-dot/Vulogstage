import os
import requests
from google import genai

# 1. Récupération des variables
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO = os.environ.get("GITHUB_REPOSITORY")

def main():
    if not GEMINI_API_KEY:
        print("Erreur : GEMINI_API_KEY est introuvable.")
        exit(1)

    # 2. Récupérer le code de la Pull Request
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    diff_response = requests.get(url, headers=headers)
    code_diff = diff_response.text

    # 3. Préparer la question
    prompt = (
        "Tu es un développeur Senior bienveillant. Fais une revue de code sur ce 'diff' de Pull Request. "
        "Si le code est bon, dis-le. S'il y a des failles de sécurité, des problèmes de performance "
        "ou des erreurs de style, signale-les avec bienveillance.\n\n"
        f"Voici le code à analyser :\n\n{code_diff}"
    )

    # 4. Appeler Gemini avec la NOUVELLE bibliothèque
    print("Envoi du code à l'API Gemini...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )

    # 5. Poster la réponse sur GitHub
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
