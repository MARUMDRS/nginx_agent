# nginx\_agent

**nginx\_agent** is a stylish, AI-powered CLI assistant that helps you generate, explain, edit, lint, and manage NGINX configuration files. It uses a local [Mistral](https://mistral.ai) model (via [Ollama](https://ollama.com)) and DuckDuckGo search to provide documentation-aware, secure, and customizable configurations — fast. 

> This project uses the Mistral model specifically for generating and editing NGINX configurations with doc-based reasoning, enhanced by live searches from official [nginx.org](https://nginx.org/en/docs/).



---

##  Features

-  Interactive config generation for:

  - Static Content Serving
  - Reverse Proxy
  - Load Balancing (Round Robin, Least Connections, IP Hash)
  - SSL/TLS Termination
  - FastCGI/SCGI/uWSGI Proxying
  - WebSocket Proxying
  - HTTP Caching
  - API Gateway (with JWT or API Key support)
  - Mail Proxy (IMAP, POP3, SMTP)
  - Security Enhancements (rate limiting, CSP, etc.)
  - Custom configuration prompts

-  Context-aware answers and code generation using DuckDuckGo and BeautifulSoup to scrape only the meaningful `<div id="content">`

-  Cached documentation lookup from multiple sources

-  Formatted and commented config output using shell-style comments

-  Linting using `nginx -t`

-  Terminal UI built with [Questionary](https://github.com/tmbo/questionary) and [Rich](https://github.com/Textualize/rich)

-  Supports full edits to existing configs via chat or raw editing

-  Session state stored in memory for interactive workflows

---
![screenshot](screenshot.png)  <!-- optional preview -->
##  Installation

### 1. Install requirements

```bash
pip install -r requirements.txt
sudo apt install nginx        # Or use brew install nginx on macOS
```

### 2. Download Ollama and pull Mistral

```bash
# https://ollama.com/download
ollama pull mistral
```

### 3. Create .env file

```env
OLLAMA_MODEL=mistral
```

---

## 🔬 Usage

Launch the tool:

```bash
python main.py
```

Follow prompts like:

```
3. Load Balancing
Enter comma-separated backend URLs: http://1.1.1.1, http://2.2.2.2
Choose method: Round Robin
Enable health checks? Yes
```

Example generated config:

```nginx
# Define upstream
upstream backend_servers {
    server 1.1.1.1;
    server 2.2.2.2;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend_servers;
        # Add headers and timeouts here...
    }
}
```

### After generation you can:

-  Explain the config
- Edit or rewrite via AI
- Save as `nginx.conf`
- Search nginx.org
- Lint with `nginx -t`

---

##  Docker Compose Support

Choose "From Docker Compose" to analyze your `docker-compose.yml`, for example:

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"

  api:
    image: node:18
    ports:
      - "3000:3000"
```

And get a matching proxy config automatically.

---

##  Smart Prompting & Search

- Prompts generated with detailed context-aware options
- Search hint is extracted from the menu choice
- Real docs fetched from DuckDuckGo and nginx.org
- Uses cache in `.cache/` folder for repeat performance

---

##  Dependencies

```text
rich
questionary
dotenv
ollama
duckduckgo-search
beautifulsoup4
pyyaml
requests
```

---

##  Relevant Links

- [Mistral](https://mistral.ai) for the base model
- [Ollama](https://ollama.com) for local inference
- [nginx.org](https://nginx.org/en/docs/) for authoritative documentation

---

Built as a side project to explore the synergy between AI agents and intelligent web crawling for practical developer tooling.
