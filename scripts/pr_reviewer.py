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
    
    try:
        diff_response = requests.get(url_gh, headers=headers_gh)
        code_diff = diff_response.text
    except Exception as e:
        print(f"Erreur lors de la récupération de la PR : {e}")
        exit(1)

    prompt = (
        "Tu es un développeur Senior bienveillant. Fais une revue de code concise sur ce 'diff'. "
        f"Voici le code à analyser :\n\n{code_diff}"
    )

    print("--- DEBUT DE L'ANALYSE AVEC GEMINI 3.1 FLASH LITE ---")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
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
    
    # Amélioration recommandée par le bot : gestion d'erreur sur le post du commentaire
    try:
        comment_response = requests.post(url_comment, headers=comment_headers, json={"body": ai_review})
        if comment_response.status_code == 201:
            print("✅ Revue de code postée avec succès !")
        else:
            print(f"❌ Erreur GitHub API ({comment_response.status_code}) : {comment_response.text}")
    except Exception as e:
        print(f"Erreur réseau lors de la publication du commentaire : {e}")

if __name__ == "__main__":
    main()
