
import requests
from bs4 import BeautifulSoup

# Get vulnerabilities directory listing
response = requests.get('http://31.97.117.123/vulnerabilities/')
print("Vulnerabilities directory listing:")
print(response.text)

