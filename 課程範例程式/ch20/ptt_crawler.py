import requests
from bs4 import BeautifulSoup
import time

ptt_url = "https://www.ptt.cc/"

r = requests.get(ptt_url + "bbs/")

# print(r.status_code)
soup = BeautifulSoup(r.content, "html.parser")
board = soup.find("a", {"class": "board"})
# print(board.find("div", {"class": "board-title"}).text)
# print(board["href"])

board = "stock"
headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/58.0.3029.110 Safari/537.3", }
cookies = {"over18": "1"}
r1 = requests.get(ptt_url + "/bbs/" + board, cookies=cookies, headers=headers)
soup = BeautifulSoup(r1.content, "html.parser")
list_title = soup.find_all("div", {"class": "r-ent"})
href_list = []
for title in list_title:
    # time.sleep(0.5)

    # print(title.find("a").text)
    href_list.append(title.find("a")["href"])

r2 = requests.get(ptt_url + href_list[0])
# print(r2.content)
content = BeautifulSoup(r2.content, "html.parser")
content_inside = content.find("div", id="main-content")
# print(content_inside)
# print("===============")
push_list = []
for tag in content_inside.find_all("div", class_="push"):
    push_list.append(tag.text)
    tag.extract()

for tag in content_inside.find_all("div", class_=["article-metaline", "article-metaline-right"]):
    # print(tag)
    tag.extract()
print(content_inside.text)

print(push_list)



