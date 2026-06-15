import httpx
import json
import os
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(".env")

TOKEN = os.getenv("GARANT_TOKEN")
BASE_URL = os.getenv("GARANT_BASE_URL", "https://api.garant.ru/v2")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "garant-mcp-test/1.0",
}

SAMPLE_TOPIC = 10900200  # НК РФ часть 1

to_date = datetime.now().strftime("%Y-%m-%d")
from_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

ENDPOINTS = [
    ("GET", "/limits", None),
    (
        "POST",
        "/search",
        {"text": "налог", "env": "internet", "sort": 0, "sortOrder": 0, "page": 1},
    ),
    ("GET", f"/topic/{SAMPLE_TOPIC}", None),
    ("POST", "/snippets", {"text": "налог", "topic": SAMPLE_TOPIC}),
    (
        "POST",
        "/find-hyperlinks",
        {"text": "Статья 36 ЖК РФ", "baseUrl": "https://internet.garant.ru"},
    ),
    (
        "POST",
        "/find-modified",
        {"topics": [SAMPLE_TOPIC], "modDate": "2025-01-01", "needEvents": True},
    ),
    ("GET", "/prime", None),
    (
        "POST",
        "/prime/create-news",
        {"categories": [24], "fromDate": from_date, "toDate": to_date, "sort": 1},
    ),
    (
        "POST",
        "/sutyazhnik-search",
        {"text": "арбитражный управляющий", "count": 5, "kind": ["301", "302"]},
    ),
    ("GET", f"/topic/{SAMPLE_TOPIC}/download", None),
    ("GET", f"/topic/{SAMPLE_TOPIC}/html", None),
    ("GET", f"/topic/{SAMPLE_TOPIC}/entry/36/html", None),
    ("GET", f"/topic/{SAMPLE_TOPIC}/download-odt", None),
    ("GET", f"/topic/{SAMPLE_TOPIC}/download-pdf", None),
    ("GET", "/image/12345", None),
    ("GET", f"/formula?text={base64.b64encode(b'x^2+y^2=z^2').decode()}&fmt=png", None),
]


def call(method, path, json_data=None):
    url = f"{BASE_URL}{path}"
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            if method == "GET":
                r = client.get(url, headers=HEADERS)
            else:
                r = client.post(url, headers=HEADERS, json=json_data)
        content_type = r.headers.get("content-type", "")
        body_preview = r.text[:500]
        if "json" in content_type:
            try:
                parsed = r.json()
                body_preview = json.dumps(parsed, ensure_ascii=False, indent=2)[:500]
            except Exception:
                pass
        return {
            "method": method,
            "url": url,
            "status": r.status_code,
            "content_type": content_type,
            "content_length": len(r.content),
            "body_preview": body_preview,
            "headers": dict(r.headers),
        }
    except Exception as e:
        return {
            "method": method,
            "url": url,
            "status": None,
            "error": str(e),
        }


def main():
    print("=" * 80)
    print("Ручная проверка всех endpoint Гарант API")
    print(f"Токен: {TOKEN[:8]}...{TOKEN[-8:]}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)

    results = []
    for method, path, data in ENDPOINTS:
        result = call(method, path, data)
        results.append(result)
        print(f"\n{method} {path}")
        print(f"  URL: {result['url']}")
        if "status" in result and result["status"] is not None:
            print(f"  Status: {result['status']}")
            print(f"  Content-Type: {result.get('content_type', '')}")
            print(f"  Body preview: {result['body_preview']}")
        else:
            print(f"  ERROR: {result.get('error')}")

    # Save detailed results
    output_dir = "manual_api_check"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n\nПодробные результаты сохранены в: {filename}")


if __name__ == "__main__":
    main()
