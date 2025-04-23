import os
import hashlib
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def search_nginx_docs(query, max_results=3):
    # Debug purposes
    print(f"[🔍] Searching DuckDuckGo for: {query} site:nginx.org/en/docs/")  
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(f"{query} site:nginx.org/en/docs/"):
            results.append(r)
            if len(results) >= max_results:
                break
    print("🔍 Found results:")
    for r in results:
        print(f"• {r.get('title')} - {r.get('href')}")
    return results

def get_cache_filename(url):
    hash_key = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{hash_key}.txt")

def fetch_page_text(url):
    cache_file = get_cache_filename(url)
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as err:
        print(f"Error fetching {url}: {err}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find("div", id="content") or soup.body
    text = main.get_text(separator='\n', strip=True) if main else ""

    if text:
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(text)

    return text

def get_docs_for_prompt(search_query, user_prompt, max_chars=15000):
    results = search_nginx_docs(search_query)
    if not results:
        return None, None

    docs = []
    urls_used = []

    for r in results:
        content = fetch_page_text(r['href'])
        if content:
            urls_used.append(r['href'])
            docs.append(f"[{r['href']}]\n{content}")
        if len("".join(docs)) >= max_chars:
            break

    if not docs:
        return None, None

    combined = "\n\n---\n\n".join(docs)[:max_chars]
    doc_block = "\n".join(urls_used)

    prompt = (
        f"Based on the following NGINX documentation pages:\n{doc_block}\n\n"
        f"{combined}\n\n"
        f"Now generate a full nginx.conf configuration that matches the request below:\n"
        f"{user_prompt}\n\n"
        f"Follow this format:\n"
        f"- All configuration lines must appear exactly as they'd be used in nginx.conf\n"
        f"- Any explanations, tips, or extra info must be commented using '#'\n"
        f"- Do not include prose paragraphs or markdown\n"
        f"- Output only nginx.conf-style text"
    )

    return urls_used[0], prompt

