import os
import requests

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "static", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

SAMPLES = [
    {
        "filename": "sample-telegram-scam.jpg",
        "url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=700&auto=format&fit=crop&q=80",
        "description": "Abstract cyber fraud pattern"
    },
    {
        "filename": "sample-job-offer.jpg",
        "url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=700&auto=format&fit=crop&q=80",
        "description": "Document with stamp and seal"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for item in SAMPLES:
    path = os.path.join(IMAGE_DIR, item["filename"])
    if not os.path.exists(path):
        try:
            r = requests.get(item["url"], headers=headers, timeout=20)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                print(f"Saved {item['filename']}")
        except Exception as e:
            print(f"Error {item['filename']}: {e}")
