import os
import requests
from google import genai

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO = os.environ.get("GITHUB_REPOSITORY")

def main():
    if not GEMINI_API_KEY:
        print("Erreur : GEMINI_API_KEY est introuvable.")
        exit(1)

    headers_gh = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url_gh = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    diff_response = requests.get(url_gh, headers=headers_gh)
    code_diff = diff_response.text

    prompt = (
        "Tu es un développeur Senior bienveillant. Fais une revue de code concise sur ce 'diff'. "
        f"Voici le code à analyser :\n\n{code_diff}"
    )

    # 4. APPEL AVEC LE MODÈLE SECU EN 2.0
    print("--- DEBUT DE L'ANALYSE AVEC GEMINI 2.0 FLASH ---")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        ai_review = response.text
    except Exception as e:
        print(f"Erreur lors de l'appel à Gemini : {e}")
        exit(1)

    print("Publication de la revue sur GitHub...")
    comment_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url_comment = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    requests.post(url_comment, headers=comment_headers, json={"body": ai_review})
    print("✅ Revue de code postée avec succès !")

if __name__ == "__main__":
    main()
