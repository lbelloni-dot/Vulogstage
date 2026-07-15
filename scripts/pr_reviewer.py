import os
import requests
from google import genai

# 1. Récupération des variables d'environnement
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO = os.environ.get("GITHUB_REPOSITORY")

def main():
    if not GEMINI_API_KEY:
        print("Erreur : GEMINI_API_KEY est introuvable.")
        exit(1)

    # 2. Récupérer le "diff" (le code modifié) de la Pull Request via l'API GitHub
    headers_gh = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url_gh = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    diff_response = requests.get(url_gh, headers=headers_gh)
    
    if diff_response.status_code != 200:
        print(f"Erreur lors de la récupération du code GitHub : {diff_response.status_code}")
        exit(1)
        
    code_diff = diff_response.text

    # 3. Préparer le prompt pour l'IA
    prompt = (
        "Tu es un développeur Senior bienveillant. Fais une revue de code concise sur ce 'diff'. "
        f"Voici le code à analyser :\n\n{code_diff}"
    )

    # 4. Appel à l'API Gemini (AVEC LE BON MODÈLE 2.5)
    print("Analyse du code avec Gemini 2.5 Flash...")
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

    # 5. Publication de la réponse sous forme de commentaire sur la Pull Request
    print("Publication de la revue sur GitHub...")
    comment_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url_comment = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    
    comment_response = requests.post(url_comment, headers=comment_headers, json={"body": ai_review})
    
    if comment_response.status_code == 201:
        print("✅ Revue de code postée avec succès sur la PR !")
    else:
        print(f"❌ Erreur lors de la publication du commentaire : {comment_response.text}")

if __name__ == "__main__":
    main()
