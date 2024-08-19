import requests
from bs4 import BeautifulSoup

ptt_url = "https://www.ptt.cc/"

r = requests.get(ptt_url + "bbs/")

print(r.status_code)
soup = BeautifulSoup(r.content, "html.parser")
board = soup.find("a", {"class": "board"})
print(board.find("div", {"class": "board-title"}).text)
print(board["href"])
print(board.attrs)
