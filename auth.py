import subprocess
import base64
import json
from config import URL_Base


def get_token(api_key: str, api_secret: str) -> str:
    credentials = f"{api_key}:{api_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()

    result = subprocess.run(
        [
            "curl", "-s",
            "-X", "POST",
            "-H", f"Authorization: Basic {encoded}",
            "-H", "Content-Type: application/x-www-form-urlencoded",
            "-d", "grant_type=client_credentials&scope=read",
            f"{URL_Base}/oauth/token"
        ],
        capture_output=True, text=True
    )

    data = json.loads(result.stdout)
    print(f"Token obtido! Expira em {data['expires_in']} segundos.\n")
    return data["access_token"]
