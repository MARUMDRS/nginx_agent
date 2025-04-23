from rich import print as rprint
from rich.panel import Panel
import questionary
from questionary import Style
from agent import ask_agent,  generate_from_docker_compose, ask_with_docs
from osops import save_config, lint_config
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
    if choice == "1. Static Content Serving":
        path = questionary.text("Enter the full path to your static files directory (e.g., /var/www/html):").ask()
        domain = questionary.text("Enter the domain name to serve these files (e.g., example.com):").ask()
        index_file = questionary.text("Enter the default index file (e.g., index.html):").ask()
        enable_gzip = questionary.confirm("Enable gzip compression?").ask()
        return f"I want to configure NGINX to serve static files from '{path}' for '{domain}' with default index '{index_file}'." + (" Enable gzip compression." if enable_gzip else "") + " Include index fallback and caching headers. Provide comments and HTTPS redirect."
    elif choice == "2. Reverse Proxy":
        domain = questionary.text("Enter the public domain name (e.g., example.com):").ask()
        backend = questionary.text("Enter the backend server URL (e.g., http://127.0.0.1:3000):").ask()
        add_headers = questionary.confirm("Do you want to add custom headers?").ask()
        timeout = questionary.text("Enter the timeout setting for upstream (e.g., 60s):").ask()
        return f"Set up NGINX as a reverse proxy from '{domain}' to '{backend}'." + (" Include custom headers." if add_headers else "") + f" Set timeout to {timeout}. Include caching and explain config reload."
    elif choice == "3. Load Balancing":
        backends = questionary.text("Enter comma-separated backend URLs (e.g., http://1.1.1.1, http://2.2.2.2):").ask()
        lb_method = questionary.select("Choose load balancing method:", choices=["Round Robin", "Least Connections", "IP Hash"]).ask()
        enable_health_checks = questionary.confirm("Enable health checks?").ask()
        return f"Configure NGINX to load balance between: {backends}. Use '{lb_method}' method." + (" Include health checks." if enable_health_checks else "") + " Enable HTTPS support."
    elif choice == "4. SSL/TLS Termination":
        domain = questionary.text("Enter domain name (e.g., secure.example.com):").ask()
        cert_path = questionary.text("Enter path to SSL certificate:").ask()
        key_path = questionary.text("Enter path to SSL key:").ask()
        redirect_http = questionary.confirm("Redirect HTTP to HTTPS?").ask()
        return f"Set up SSL/TLS for '{domain}' with cert '{cert_path}' and key '{key_path}'." + (" Redirect HTTP to HTTPS." if redirect_http else "") + " Include HSTS and strong ciphers."
    elif choice == "5. FastCGI/SCGI/uWSGI Proxying":
        protocol = questionary.select("Choose protocol:", choices=["FastCGI", "SCGI", "uWSGI"]).ask()
        backend = questionary.text(f"Enter {protocol} backend (socket or IP):").ask()
        buffer_settings = questionary.text("Enter buffer settings (or leave blank):").ask()
        return f"Set up {protocol} proxying to backend: {backend}." + (f" Buffer settings: {buffer_settings}." if buffer_settings else "") + " Include timeout tuning and security tips."
    elif choice == "6. WebSocket Proxying":
        backend = questionary.text("Enter WebSocket backend URL (e.g., ws://localhost:9000):").ask()
        use_ssl = questionary.confirm("Enable SSL/TLS for WebSocket?").ask()
        return f"Proxy WebSocket traffic to '{backend}'." + (" Use SSL." if use_ssl else "") + " Handle Upgrade/Connection headers properly."
    elif choice == "7. HTTP Caching":
        path = questionary.text("Enter cache directory path (e.g., /var/cache/nginx):").ask()
        cache_duration = questionary.text("Enter cache duration (e.g., 10m):").ask()
        cache_key = questionary.text("Enter custom cache key (or leave blank):").ask()
        return f"Enable caching using directory '{path}' for duration '{cache_duration}'." + (f" Use custom cache key: {cache_key}." if cache_key else "")
    elif choice == "8. API Gateway":
        apis = questionary.text("Enter API paths (e.g., /users,/orders):").ask()
        auth_method = questionary.select("Auth method?", choices=["None", "JWT", "API Key"]).ask()
        enable_rate_limiting = questionary.confirm("Enable rate limiting?").ask()
        return f"Set up NGINX API gateway for: {apis}." + (f" Use {auth_method} authentication." if auth_method != "None" else "") + (" Enable rate limiting." if enable_rate_limiting else "")
    elif choice == "9. Mail Proxy":
        protocol = questionary.select("Select mail protocol:", choices=["IMAP", "POP3", "SMTP"]).ask()
        backend = questionary.text(f"Enter {protocol} backend server:").ask()
        auth_server = questionary.text("Auth server URL (or leave blank):").ask()
        mail_ssl = questionary.confirm("Use SSL/TLS for mail?").ask()
        return f"Set up mail proxy for {protocol} to backend '{backend}'." + (f" Use auth server '{auth_server}'." if auth_server else "") + (" Enable SSL." if mail_ssl else "")
    elif choice == "10. Security Enhancements":
        features = questionary.checkbox("Choose features:", choices=[
            "Rate Limiting", "Request Filtering", "IP Whitelisting", "CSP Headers", "Referrer Policy"
        ]).ask()
        security_headers = questionary.checkbox("Security headers to apply:", choices=["CSP", "HSTS", "X-Frame-Options"]).ask()
        access_control = questionary.text("IPs to whitelist/blacklist:").ask()
        return f"Enhance NGINX security with: {', '.join(features)}. Add headers: {', '.join(security_headers)}. Access control: {access_control}."
    elif choice == "11. Custom Configuration":
        description = questionary.text("Describe your custom NGINX requirement:").ask()
        return f"Custom request: {description}. Add comments, follow security best practices, and link to official docs."
    return None

def main_menu():
    global current_config

    while True:
        rprint(Panel.fit(ascii_art, style="purple"))
        try:
            choice = questionary.select(
                "What type of NGINX configuration do you need?",
                choices=[
                    "1. Static Content Serving",
                    "2. Reverse Proxy",
                    "3. Load Balancing",
                    "4. SSL/TLS Termination",
                    "5. FastCGI/SCGI/uWSGI Proxying",
                    "6. WebSocket Proxying",
                    "7. HTTP Caching",
                    "8. API Gateway",
                    "9. Mail Proxy",
                    "10. Security Enhancements",
                    "11. Custom Configuration",
                    "12. From Docker Compose",
                    "13. Exit"
                ],
                style=custom_style
            ).ask()

            if choice == "13. Exit":
                rprint("\nGoodbye!")
                break

            user_prompt = get_prompt_by_choice(choice)
            if not user_prompt:
                continue

            if choice == "12. From Docker Compose":
                current_config = user_prompt
            else:
                rprint("\nGenerating NGINX configuration...")
                search_hint = choice.split(". ", 1)[1] if ". " in choice else choice
                current_config = ask_with_docs(user_prompt, doc_topic=search_hint)
                print(f"\nsearch_hint: '{search_hint}':\n")
                # print(f"\current_config: '{current_config}':\n")
                
            rprint(Panel.fit(current_config, title="NGINX Config", style="bold blue"))

            while True:
                try:
                    sub = questionary.select(
                        "What would you like to do next?",
                        choices=[
                            "1. Explain Config",
                            "2. Save Config",
                            "3. Lint Config",
                            "4. Search Docs",
                            "5. Chat with AI",
                            "6. Edit Config",
                            "7. Back"
                        ],
                        style=custom_style
                    ).ask()

                    if sub == "1. Explain Config":
                        explanation = ask_agent(f"Explain this config line-by-line:\n{current_config}")
                        rprint(Panel.fit(explanation, title="Explanation"))
                    elif sub == "2. Save Config":
                        try:
                            filename = questionary.text("Save as (default: nginx.conf):").ask() or "nginx.conf"
                            save_config(current_config, filename)
                        except KeyboardInterrupt:
                            rprint("[yellow]Cancelled saving.[/yellow]")
                    elif sub == "3. Lint Config":
                        try:
                            filename = questionary.text("Lint file (default: nginx.conf):").ask() or "nginx.conf"
                            lint_config(filename)
                        except KeyboardInterrupt:
                            rprint("[yellow]Cancelled linting.[/yellow]")
                    elif sub == "4. Search Docs":
                        try:
                            query = questionary.text("What do you want to look up on nginx.org?").ask()
                            answer = ask_with_docs(query)
                            rprint(Panel.fit(answer, title="AI Answer from nginx.org Docs", style="bold green"))
                        except KeyboardInterrupt:
                            rprint("[yellow]Cancelled docs search.[/yellow]")
                    elif sub == "5. Chat with AI":
                        try:
                            chat_input = questionary.text("What change do you want to make to the current config?").ask()
                            current_config = ask_agent(
                                f"Here is my current config:\n{current_config}\nPlease modify it as follows:\n{chat_input}"
                            )
                            rprint(Panel.fit(current_config, title="Modified Config", style="bold blue"))
                        except KeyboardInterrupt:
                            rprint("[yellow]Chat cancelled.[/yellow]")
                    elif sub == "6. Edit Config":
                        rprint(Panel.fit(current_config, title="Current Config", style="cyan"))
                        edit_description = questionary.text("Describe what you want to change in the config:").ask()
                        if edit_description is None:
                            rprint("[yellow]Edit cancelled.[/yellow]")
                            continue
                        full_edit_prompt = (
                            f"Here is my current config:\n{current_config}\n\n"
                            f"Please modify it as follows:\n{edit_description}"
                        )
                        response = ask_agent(full_edit_prompt)
                        current_config = response  # overwrite with updated config
                        rprint(Panel.fit(response, title="Modified Config", style="bold blue"))
                    elif sub == "7. Back":
                        break

                except KeyboardInterrupt:
                    rprint("[yellow]Cancelled. Returning to previous menu.[/yellow]")
                    break

        except KeyboardInterrupt:
            rprint("[yellow]Cancelled. Goodbye")
            break
