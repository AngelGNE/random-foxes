import requests

URL = "https://randomfox.ca/floof"

def random_fox():
    try:
        response = requests.get(URL)
        return response.json()
    except Exception as e:
        print(e)
