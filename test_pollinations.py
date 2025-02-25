import httpx

url = "https://text.pollinations.ai/"
data = {
    "messages": [{"role":"user", "content":"Hello!"}],
    "model": "openai"
}

try:
    response = httpx.post(url, json=data, timeout=10.0)
    print("Status code:", response.status_code)
    print("Response body:", response.text)
except httpx.RequestError as e:
    print("An error occurred:", str(e))