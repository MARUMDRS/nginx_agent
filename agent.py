import os
import ollama
from dotenv import load_dotenv
import yaml
from crawler import get_docs_for_prompt

load_dotenv()

# Model name from the .env 
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")

system_prompt = """You are NGINX_configurator, an expert assistant in configuring NGINX.
Your role is to guide users in setting up secure and correct nginx.conf files.
Always include the actual nginx.conf configuration block as part of your response.
Format your output as follows:
- Every line that is not a configuration directive must start with '#'
- All explanations, steps, and instructions must be written as shell-style comments (using '#')
- Only lines that belong in an actual nginx.conf file must be left uncommented (e.g., 'listen 80;', 'location / {', etc)
- Do NOT include markdown code blocks or triple backticks.
- Add inline comments using '#' at the end of config lines when necessary.

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
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]

def ask_with_docs(user_prompt, doc_topic=None):
    # Use concise topic for searching, full prompt for answering
    search_query = doc_topic or user_prompt[:80]
    url, prompt = get_docs_for_prompt(search_query, user_prompt=user_prompt)
    if not prompt:
        return "Sorry, I couldn't fetch documentation at this time."
    # Debug print
    #print(f"\n Final Prompt Sent to Model:\n{'-' * 40}\n{prompt}\n{'-' * 40}\n")
    response = ask_agent(prompt)
    return response

def generate_from_docker_compose(path_to_yml):
    if not os.path.exists(path_to_yml):
        return " docker-compose.yml not found."
    try:
        with open(path_to_yml, "r") as f:
            compose = yaml.safe_load(f)
        services = compose.get("services", {})
        prompt_parts = [
            "Create an NGINX configuration that proxies the following docker-compose services:"
        ]
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
