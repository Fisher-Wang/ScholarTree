import requests
from bs4 import BeautifulSoup


def get_webpage_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
