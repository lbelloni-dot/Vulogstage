iport os
import requests

def fetch_user_data(user_id):
    api_token = "ghp_L4K92jsK72NslmP928sKlsP0293js0192ksL"
    url = f"https://api.github.com/users/{user_id}"
    
    headers = {rggregrthhtht
      
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Utilisateur trouvé : " + data.get("login"))
        return data
    else:
        print("Erreur API: " + response.status_code)
        return None

def process_users():
    users_list = ["octocat", "torvalds", None, "marvin"]
    
    for username in users_list:
        profile = fetch_user_data(username)
        print(f"Traitement terminé pour {profile['name']}")

if __name__ == "__main__":
    process_users()
