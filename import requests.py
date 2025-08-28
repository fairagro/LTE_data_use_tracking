import requests
response = requests.post("http://127.0.0.1:8080/extract_metadata", json={"text": "Test text"})
print(response.status_code)
print(response.text)
