import json, os, time, urllib.request, ssl, xml.etree.ElementTree as ET
from urllib.parse import quote_plus

STATE_FILE = "seen_posts.json"
TELEGRAM_ID = "5821137468"
API_KEY = "123456" # Votre clé API obtenue sur Telegram

def send_notification(text):
    # Ajout de l'apikey pour eviter le blocage IP de GitHub
    url = f"https://api.callmebot.com/text.php?id={TELEGRAM_ID}&text={quote_plus(text)}&apikey={API_KEY}"
    context = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            res_body = response.read().decode('utf-8')
            print(f"Reponse API: {res_body}")
    except Exception as e:
        print(f"Erreur envoi: {e}")

def fetch_so_posts():
    url = "https://stackoverflow.com/feeds/tag?tagnames=cors&sort=newest"
    posts = []
    context = ssl._create_unverified_context()
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            root = ET.fromstring(response.read())
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                posts.append({'id': entry.find('atom:id', ns).text, 'title': entry.find('atom:title', ns).text, 'link': entry.find('atom:link', ns).attrib['href']})
    except Exception as e: print(f"Erreur SO: {e}")
    return posts

def main():
    send_notification("Salut ! Ton agent CORS est en service avec sa cle API.")
    
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f: json.dump([], f)
    with open(STATE_FILE, "r") as f: seen_ids = json.load(f)
    
    new_posts = []
    for p in fetch_so_posts():
        if p['id'] not in seen_ids:
            new_posts.append(p)
            seen_ids.append(p['id'])
            
    with open(STATE_FILE, "w") as f: json.dump(seen_ids[-500:], f)
    
    for p in new_posts:
        msg = f"Bug CORS: {p['title']} - {p['link']}"
        send_notification(msg)
        time.sleep(2)

if __name__ == "__main__":
    main()
