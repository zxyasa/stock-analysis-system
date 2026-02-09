import json
from pathlib import Path
import requests

CLIENT_SECRET_PATH = Path('secrets/google-calendar/client_secret.json')
TOKEN_PATH = Path('secrets/google-calendar/token.json')
REDIRECT_URI = 'http://localhost'


def main():
    if not CLIENT_SECRET_PATH.exists():
        raise FileNotFoundError('Client secret file missing at secrets/google-calendar/client_secret.json')

    data = json.loads(CLIENT_SECRET_PATH.read_text())
    client_info = data.get('installed') or data.get('web')
    if not client_info:
        raise RuntimeError('Client secret JSON missing "installed" or "web" section')

    client_id = client_info['client_id']
    client_secret = client_info['client_secret']
    token_uri = client_info.get('token_uri', 'https://oauth2.googleapis.com/token')

    redirect_url = input('Paste the full redirect URL (with code=...): ').strip()
    if not redirect_url:
        print('No redirect URL provided. Run the OAuth consent flow to obtain one.')
        return

    # Extract authorization code
    try:
        from urllib.parse import urlparse, parse_qs
    except ImportError:
        from urlparse import urlparse, parse_qs  # Python 2 fallback (not expected)

    query = urlparse(redirect_url).query
    params = parse_qs(query)
    code = params.get('code', [''])[0]
    if not code:
        raise RuntimeError('Authorization code not found in URL')

    payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    resp = requests.post(token_uri, data=payload)
    if resp.status_code != 200:
        print('Token request failed:', resp.status_code, resp.text)
        resp.raise_for_status()
    token_data = resp.json()
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(token_data))
    print('Saved token to', TOKEN_PATH)


if __name__ == '__main__':
    main()
