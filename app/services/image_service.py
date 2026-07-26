import os
import uuid
import random
import mimetypes
import requests

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

TEMP_DIR = "app/temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)

# Cache previously downloaded images
_image_cache = {}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
}


def download_image(query: str):
    """
    Search Google Images using SerpAPI and download
    a random valid image from the top search results.
    """

    query = query.strip()

    print(f"\n[IMAGE] Searching for: {query}")

    # Return cached image if already downloaded
    if query in _image_cache:
        cached = _image_cache[query]
        if os.path.exists(cached):
            print(f"[IMAGE] Using cached image: {cached}")
            return cached

    params = {
        "engine": "google_images",
        "q": query,
        "api_key": SERPAPI_API_KEY,
    }

    try:
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:
        print(f"[SERPAPI ERROR] {e}")
        return None

    images = data.get("images_results", [])

    print(f"[IMAGE] {len(images)} results found")

    if not images:
        return None

    # Randomly shuffle the top 10 search results
    candidates = images[:10] if len(images) >= 10 else images
    random.shuffle(candidates)

    # Try random images until one downloads successfully
    for index, image in enumerate(candidates):

        image_url = image.get("original")

        if not image_url:
            continue

        print(f"[IMAGE] Trying random image #{index + 1}")

        try:

            img = requests.get(
                image_url,
                headers=HEADERS,
                timeout=20,
                stream=True,
                allow_redirects=True,
            )

            img.raise_for_status()

            content_type = img.headers.get(
                "Content-Type",
                "image/jpeg"
            )

            extension = mimetypes.guess_extension(
                content_type.split(";")[0]
            )

            if extension is None:
                extension = ".jpg"

            filename = os.path.join(
                TEMP_DIR,
                f"{uuid.uuid4()}{extension}"
            )

            with open(filename, "wb") as f:
                for chunk in img.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            _image_cache[query] = filename

            print(f"[IMAGE] Download successful -> {filename}")

            return filename

        except Exception as e:

            print(f"[IMAGE] Failed random image #{index + 1}: {e}")

            continue

    print("[IMAGE] No downloadable image found")

    return None