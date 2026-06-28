import json
import os
import time
import urllib.request
import ssl
import xml.etree.ElementTree as ET
from urllib.parse import quote

# Fichier pour stocker les IDs déjà vus sur GitHub (utilisé via les artefacts ou simplement ignoré si on filtre par date)
STATE_FILE = "seen_posts.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return []
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_state(seen_ids):
    with open(STATE_FILE, "w") as f:
        json.dump(seen_ids, f)

def send_notification(title, link):
    user_id = "5821137468"
    message = f"🚨 *Nouveau bug CORS détecté !*\n\nTitre: {title}\nLien: {link}"
    encoded_message = quote(message)
    url = f"https://api.callmebot.com/text.php?id={user_id}&text={encoded_message}"
    
    context = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            if response.status == 200:
                print(f"Notification Telegram envoyée pour : {title}")
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
            content = response.read()
            root = ET.fromstring(content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                post_id = entry.find('atom:id', ns).text
                title = entry.find('atom:title', ns).text
                link = entry.find('atom:link', ns).attrib['href']
                posts.append({'id': post_id, 'title': title, 'link': link})
    except Exception as e:
        print(f"Erreur SO: {e}")
    return posts

def main():
    seen_ids = load_state()
    new_posts = []

    so_posts = fetch_so_posts()
    for p in so_posts:
        if p['id'] not in seen_ids:
            new_posts.append(p)
            seen_ids.append(p['id'])

    # Sauvegarde locale (GitHub commitera ce changement pour garder la mémoire)
    if len(seen_ids) > 500:
        seen_ids = seen_ids[-500:]
    save_state(seen_ids)

    for p in new_posts:   
        send_notification(p['title'], p['link'])
        time.sleep(1)

if __name__ == "__main__":
    main()
