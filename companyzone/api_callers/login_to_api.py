#Login to API

import requests

login_url = "http://127.0.0.1:8000/api/login/"
credentials = {
    "username":"Srikanth",
    "password":"Srikanth@1234"
}
response = requests.post(login_url, json=credentials)
print(response)
print(response.history)
print(response.url)
print(response.text)
print(response.json)
print(response.status_code)


"""
1. User Logs In  ──> [Send Password] ──> Django validates it
2. Tokens Issued ──> [Access & Refresh Tokens] ──> Sent back to Frontend
3. Read Data     ──> [Send Access Token] ──> Django returns Employee Table Data
4. Token Expires ──> [Access Token Dead!] ──> Django returns 401 Unauthorized
5. Silent Renew  ──> [Send Refresh Token] ──> Django returns New Access Token
"""