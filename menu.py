from rich import print as rprint
from rich.panel import Panel
import questionary
from questionary import Style
from agent import ask_agent, search_docs, save_config, lint_config,generate_from_docker_compose  
import os

current_config = ""

ascii_art = """

                 ▏▏▋▊▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▁▃▃▃▃▃▃▃▃▃▃▁▌▏
              ▍▋▉▊▌▏                          ▎▊▇██████████▄▉▌▎
            ▌▆▂▁▉▁▂▂▂▁▁▁▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▃▃▃▄▄▃▃▄▃▇▅▇▃▅▄▃▎
            ▂███▆▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▄▄███▇▇▅▅▅▇▇▆▇▆▇███▍
            ▃██████████████████████████████████████▃▄█████▁█████▍
            ▃██████████████████████████████████████▆▇█▇▇██▅█████▍
            ▃███▇▅▅▅▅█▅▅▅▆▇▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▆▅▆▆▅▅▆▅████▍
            ▃██████████████████████████████████████▉▃█▇▇██▊█████▍
                ╔────────────────────────────────────────────╗██▍
          ▃████│░█▀█░█▀▀░▀█▀░█▀█░█░█░░░░░█▀█░█▀▀░█▀▀░█▀█░▀█▀│███▍█
            ▃██│░█░█░█░█░░█░░█░█░▄▀▄░░░░░█▀█░█░█░█▀▀░█░█░░█░│█████████████▍
                │░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░░▀░│██▍
                ╚────────────────────────────────────────────╝████████▍
            ▃███████████████████████████████████████████████████▍
                
            ▃███████████████████████████████████████████████████▍
            ▃███▆▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▄▅▆▇███▍
            ▃█████████████████████████████████████▇▅▇█████▃█████▍
          ▊▇█████████████████████████████████████████████████████▄▎
          ▏▍▍▍▍▍▌▌▍▍▍▍▍▍▍▍▍▍▍▍▍▊▊▊▁▁▁▁▁▁▁▁▁▋▌▋▋▋▊▁▉▊▌▍▍▍▍▌▌▍▍▍▍▍

"""

custom_style = Style([
    ("pointer", "fg:#800080 bold"),
    ("selected", "fg:#800080 bold"),
    ("question", "bold"),
    ("answer", "fg:#00ffcc bold"),
])
def get_prompt_by_choice(choice):
    extra = ""
    if choice == "1. Reverse Proxy":
        domain = questionary.text("Domain name:").ask()
        backend = questionary.text("Backend server (e.g. http://127.0.0.1:3000):").ask()
        extra = questionary.text("Do you want to add anything else? (CORS, headers, etc):").ask()
        return f"Set up a reverse proxy from {domain} to {backend}. {extra}"
    elif choice == "2. Forward Proxy":
        extra = questionary.text("Customizations?").ask()
        return f"Set up NGINX as a forward proxy. {extra}"
    elif choice == "3. Load Balancer":
        servers = questionary.text("Comma-separated backends:").ask()
        extra = questionary.text("Any features? (sticky sessions, etc):").ask()
        return f"Set up load balancer with: {servers}. {extra}"
    elif choice == "4. SSL Termination":
        domain = questionary.text("Domain for SSL:").ask()
        extra = questionary.text("Redirect HTTP? HSTS?").ask()
        return f"Enable HTTPS for domain {domain}. {extra}"
    elif choice == "5. Security Setup":
        extra = questionary.text("Security features? (rate limit, headers):").ask()
        return f"Add rate limiting and security headers. {extra}"
    elif choice == "6. Static Hosting":
        path = questionary.text("Static directory:").ask()
        domain = questionary.text("Domain name:").ask()
        extra = questionary.text("Index fallback, caching?").ask()
        return f"Serve static files from {path} at {domain}. {extra}"
    elif choice == "7. Custom Help":
        return questionary.text("Describe the custom directive/topic:").ask()
    elif choice == "8. From Docker Compose":
        path = questionary.text("Path to docker-compose.yml (default: ./docker-compose.yml):").ask()
        if not path:
            path = "docker-compose.yml"
        if not os.path.isfile(path):
            rprint("[red] File not found. Returning to main menu.[/red]")
            return None
        return generate_from_docker_compose(path)
    return None

def main_menu():
    global current_config

    while True:
        rprint(Panel.fit(ascii_art, style="purple"))

        choice = questionary.select(
            "What type of NGINX configuration do you need?",
            choices=[
                "1. Reverse Proxy",
                "2. Forward Proxy",
                "3. Load Balancer",
                "4. SSL Termination",
                "5. Security Setup",
                "6. Static Hosting",
                "7. Custom Help",
                "8. From Docker Compose",
                "9. Exit"
            ],
            style=custom_style
        ).ask()

        if choice == "9. Exit":
            rprint("\nGoodbye!")
            break

        user_prompt = get_prompt_by_choice(choice)
        if not user_prompt:
            continue

        if choice == "8. From Docker Compose":
            current_config = user_prompt
        else:
            rprint("\nGenerating NGINX configuration...")
            current_config = ask_agent(user_prompt)

        rprint(Panel.fit(current_config, title="NGINX Config", style="bold blue"))

        while True:
            sub = questionary.select(
                "What would you like to do next?",
                choices=[
                    "1. Explain Config",
                    "2. Save Config",
                    "3. Lint Config",
                    "4. Search Docs",
                    "5. Chat with AI",
                    "6. Back"
                ],
                style=custom_style
            ).ask()

            if sub == "1. Explain Config":
                explanation = ask_agent(f"Explain this config line-by-line:\n{current_config}")
                rprint(Panel.fit(explanation, title="Explanation"))

            elif sub == "2. Save Config":
                filename = questionary.text("Save as (default: nginx.conf):").ask() or "nginx.conf"
                save_config(current_config, filename)

            elif sub == "3. Lint Config":
                filename = questionary.text("Lint file (default: nginx.conf):").ask() or "nginx.conf"
                lint_config(filename)

            elif sub == "4. Search Docs":
                query = questionary.text("What do you want to look up on nginx.org?").ask()
                results = search_docs(query)
                rprint(Panel.fit("\n".join(results), title="NGINX Docs"))

            elif sub == "5. Chat with AI":
                chat_input = questionary.text("What change do you want to make to the current config?").ask()
                if chat_input.strip().lower() != "esc":
                    current_config = ask_agent(f"Here is my current config:\n{current_config}\nPlease modify it as follows:\n{chat_input}")
                    rprint(Panel.fit(current_config, title="Modified Config", style="bold blue"))

            elif sub == "6. Back":
                break