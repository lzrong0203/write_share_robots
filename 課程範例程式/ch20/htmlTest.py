from bs4 import BeautifulSoup

with open("test.html") as fhand:
    html_content = fhand.read()

soup = BeautifulSoup(html_content, "html.parser")
# print(soup.find("p"))
#
# print(soup.find_all("p"))

# print(soup.find("p", {"id": "text"}))

print(soup.find("body").main.p)
print(soup.find("body").p)
