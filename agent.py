import os
import subprocess
import ollama
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import yaml

# Load environment variables from .env file
load_dotenv()

# Get the model name from the environment variable
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")

# System prompt for Mistral
system_prompt = """You are NGINX_configuator, an expert assistant in configuring NGINX.
Your role is to guide users in setting up secure and correct nginx.conf files.
Always:
- Explain your decisions
- Add inline comments
- Follow best practices from https://nginx.org/en/docs/
- Include doc links at the end
"""

def ask_agent(user_prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response["message"]["content"]

def search_docs(query, max_results=5):
    with DDGS() as ddgs:
        results = ddgs.text(f"{query} site:nginx.org", max_results=max_results)
        return [f"{r['title']}: {r['href']}" for r in results]

def save_config(config, filename="nginx.conf"):
    with open(filename, "w") as f:
        f.write(config)
    print(f"\n Saved to {filename}")

def lint_config(filename="nginx.conf"):
    print("\n Running nginx -t...")
    try:
        result = subprocess.run(["nginx", "-t", "-c", os.path.abspath(filename)], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    except FileNotFoundError:
        print(" NGINX not found. Is it installed and in your PATH?")

def generate_from_docker_compose(path_to_yml):
    if not os.path.exists(path_to_yml):
        return " docker-compose.yml not found."
    try:
        with open(path_to_yml, 'r') as f:
            compose = yaml.safe_load(f)
        services = compose.get('services', {})
        prompt_parts = ["Create an NGINX configuration that proxies the following docker-compose services:"]
        for name, details in services.items():
            ports = details.get("ports", [])
            for p in ports:
                if isinstance(p, str) and ":" in p:
                    host_port, container_port = p.split(":")
                    prompt_parts.append(
                        f"Service '{name}' should forward from host:{host_port} to container:{container_port}."
                    )
        prompt = "\n".join(prompt_parts)
        return ask_agent(prompt)
    except Exception as e:
        return f" Error parsing docker-compose file: {e}"
