import os
import requests

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "static", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# List of high-quality, real-world images related to job scams, recruitment verification, and careers
IMAGES_TO_DOWNLOAD = [
    {
        "filename": "hero-security.jpg",
        "url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&auto=format&fit=crop&q=80",
        "description": "Cybersecurity digital shield & scam protection"
    },
    {
        "filename": "fake-offer-scam.jpg",
        "url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&auto=format&fit=crop&q=80",
        "description": "Document verification and fraudulent contract inspection"
    },
    {
        "filename": "email-phishing-analysis.jpg",
        "url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
        "description": "Email code analysis and digital fraud detection"
    },
    {
        "filename": "remote-job-scam-chat.jpg",
        "url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=80",
        "description": "Recruitment message on laptop and smartphone"
    },
    {
        "filename": "verified-careers.jpg",
        "url": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800&auto=format&fit=crop&q=80",
        "description": "Verified official corporate job interview and career team"
    },
    {
        "filename": "community-warning.jpg",
        "url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=800&auto=format&fit=crop&q=80",
        "description": "Legal protection and community fraud reporting"
    },
    {
        "filename": "mobile-scam-alert.jpg",
        "url": "https://images.unsplash.com/photo-1584433144859-1fc3ab64a957?w=800&auto=format&fit=crop&q=80",
        "description": "Smartphone receiving suspicious recruitment message"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_all():
    print(f"Downloading {len(IMAGES_TO_DOWNLOAD)} real-world images into {IMAGE_DIR}...")
    success_count = 0
    for item in IMAGES_TO_DOWNLOAD:
        path = os.path.join(IMAGE_DIR, item["filename"])
        print(f"Fetching: {item['filename']} ({item['description']})...")
        try:
            r = requests.get(item["url"], headers=headers, timeout=20)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(path, "wb") as f:
                    f.write(r.content)
                size_kb = len(r.content) / 1024
                print(f"  -> Saved {item['filename']} ({size_kb:.1f} KB)")
                success_count += 1
            else:
                print(f"  -> Failed (HTTP {r.status_code})")
        except Exception as e:
            print(f"  -> Error: {e}")
    print(f"\nDownload complete: {success_count}/{len(IMAGES_TO_DOWNLOAD)} images saved.")

if __name__ == "__main__":
    download_all()
