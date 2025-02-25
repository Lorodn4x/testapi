import httpx

url = "http://127.0.0.1:8000/v1/chat/completions"
data = {
    "model": "openai",
    "messages": [{"role": "user", "content": "Hello!"}]
}

try:
    response = httpx.post(url, json=data, timeout=10.0)
    print("Status code:", response.status_code)
    print("Response body:", response.json())
except httpx.RequestError as e:
    print("An error occurred:", str(e))