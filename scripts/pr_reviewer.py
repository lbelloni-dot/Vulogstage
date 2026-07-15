import os
import requests
import google.generativeai as genai

# 1. Récupération des variables d'environnement (injectées par GitHub)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO = os.environ.get("GITHUB_REPOSITORY")

# 2. Configuration de Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')

def main():
    # 3. Récupérer le "Diff" (les modifications de code) via l'API GitHub
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    diff_response = requests.get(url, headers=headers)
    code_diff = diff_response.text

    # 4. Construire le prompt pour Gemini
    prompt = f"""
    Tu es un développeur Senior bienveillant. Fais une revue de code sur ce 'diff' de Pull Request.
    Si le code est bon, dis-le. S'il y a des failles de sécurité, des problèmes de performance 
    ou des erreurs de style, signale-les avec bienveillance.
    
    Voici le code modifié :
    {code_diff}
    """

    # 5. Demander l'analyse à Gemini
    response = model.generate_content(prompt)
    review_comment = response.text

    # 6. Poster la réponse sur GitHub en tant que commentaire
    comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    requests.post(
        comment_url,
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        json={"body": f"🤖 **Revue de code par IA (Gemini) :**\n\n{review_comment}"}
    )

if __name__ == "__main__":
    main()
