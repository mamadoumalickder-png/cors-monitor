import json, os, time, urllib.request, ssl, xml.etree.ElementTree as ET
from urllib.parse import quote

STATE_FILE = "seen_posts.json"

def send_notification(title, link):
    # Version ultra-simplifiée pour éviter les erreurs
    text = f"ALERTE CORS: {title} - Lien: {link}"
    url = f"https://api.callmebot.com/text.php?id=5821137468&text={quote(text)}"
    context = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            if response.status == 200: print(f"Succès: {title}")
    except Exception as e: print(f"Erreur: {e}")

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
        send_notification(p['title'], p['link'])
        time.sleep(1)

if __name__ == "__main__": main()
