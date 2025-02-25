import httpx

def check_pollinations():
    url = "https://text.pollinations.ai/models"
    try:
        response = httpx.get(url, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_pollinations()