import os
import subprocess
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