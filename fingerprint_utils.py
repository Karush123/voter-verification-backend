import requests

def capture_fingerprint():
    try:
        response = requests.get("http://localhost:11100/rd/capture")
        return response.text
    except:
        return None
