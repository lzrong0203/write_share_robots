import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor


class PTT_SCRAPER:
    ptt_url = "https://www.ptt.cc"

    def __init__(self, board):
        self.board = board
        self.url = PTT_SCRAPER.ptt_url + "/bbs/" + board
        self.post_num = 0
        self.goal = False
        self.max_posts = float('inf')  # 初始化為無限大

    @staticmethod
    def get_soup(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "*/*"}
        cookies = {"over18": "1"}
        session = requests.Session()
        session.max_redirects = 60
        r = session.get(url, headers=headers, cookies=cookies, allow_redirects=True)
        return BeautifulSoup(r.content, "html.parser")

    def get_title_href(self):
        soup = PTT_SCRAPER.get_soup(self.url)
        list_title = soup.find_all("div", {"class": "r-ent"})
        href_list = []
        for title in list_title:
            if title.find("a") is None:
                continue
            title.find("div", class_="author")
            href_list.append(title.find("a")["href"])

        return href_list

    def get_title_data(self, until_date=None):  # 移除 max_posts 參數
        soup = PTT_SCRAPER.get_soup(self.url)
        list_title = soup.find_all("div", {"class": "r-ent"})

        data = []
        # for d in reversed(list_title):
        #     if d.find("a") is None:
        #         continue
        #     if d.find_previous_sibling("div", clas    s_="r-list-sep"):
        #         continue
        data_filtered = [d for d in reversed(list_title)
                         if d.find("a") is not None and not d.find_previous_sibling("div", class_="r-list-sep")]
        # print(data_filtered)
        parallel_list = []
        remaining_posts = self.max_posts - self.post_num  # 計算還需要抓取幾篇文章

        for d in data_filtered:
            # # if self.post_num >= max_posts: # 移除這個檢查
            #     self.goal = True
            #     break
            if len(parallel_list) >= remaining_posts:  # 如果已經收集足夠的文章
                self.goal = True
                break

            # author = d.find("div", class_="author").text.strip()
            date = d.find("div", class_="date").text.strip()
            if datetime.strptime(date, "%m/%d") < until_date:
                self.goal = True
                break
            parallel_list.append(d)
            # title = d.find("a").text.strip()
            # href = d.find("a")["href"]
            # title_dict = {
            #     "title": title,
            #     "author": author,
            #     "date": date,
            #     "href": href,
            # }
            # title_dict.update(self.get_post_content_push(href))
            # # print(title_dict["title"], title_dict["date"])
        with ThreadPoolExecutor() as executor:
            page_list = list(executor.map(self.parallel_fetch, parallel_list))
        data.extend(page_list)

        return data

    def parallel_fetch(self, d):
        print(".", end="")
        title = d.find("a").text.strip()
        href = d.find("a")["href"]
        author = d.find("div", class_="author").text.strip()
        date = d.find("div", class_="date").text.strip()
        title_dict = {
            "title": title,
            "author": author,
            "date": date,
            "href": href,
        }
        title_dict.update(self.get_post_content_push(href))
        self.post_num += 1
        return title_dict

    def get_post_content_push(self, href):
        # hrefs = self.get_title_href()
        # for post_href in hrefs:
        soup = self.get_soup(PTT_SCRAPER.ptt_url + href)
        content_inside = soup.find("div", id="main-content")
        pushes = content_inside.find_all("div", class_="push")
        push_list = []
        for p in pushes:
            push_list.append(self.get_push(p))
        for tag in content_inside.find_all("div", class_="push"):
            tag.extract()
        for tag in content_inside.find_all("div", class_=["article-metaline", "article-metaline-right"]):
            tag.extract()
        return {"content": content_inside.text.strip(), "pushes": push_list}

    def get_push(self, push):
        try:
            if push.find("span", class_="push-tag") is None:
                return dict()
            push_tag = push.find("span", class_="push-tag").text.strip()
            push_userid = push.find("span", class_="push-userid").text.strip()
            push_content = push.find("span", class_="push-content").text.lstrip(": ")
            push_ipdatetime = push.find("span", class_="push-ipdatetime").text.strip()
            push_dict = {"tag": push_tag, "userid": push_userid,
                         "content": push_content, "datetime": push_ipdatetime}
            return push_dict  # 移到 try 區塊內
        except Exception as e:
            print(e)
            return dict()  # 發生異常時返回空字典

    def fetch_posts(self, max_posts=10, until_date=None):
        self.post_num = 0  # 新增這行：重置計數器
        self.max_posts = max_posts  # 設置最大文章數
        post_datas = []
        if until_date:  # 修改這行：加入條件判斷
            until_date = datetime.strptime(until_date, "%m/%d")
        while not self.goal and self.post_num < max_posts:
            if until_date is not None:
                post_data = self.get_title_data(until_date)
            else:
                post_data = self.get_title_data()
            post_datas.extend(post_data)
            self.url = PTT_SCRAPER.ptt_url + self.find_previous_page()

        # hrefs = self.get_title_href()
        # post_data = []
        # for post_href in hrefs:
        #     self.url = PTT_SCRAPER.ptt_url + post_href
        #     # print(self.url)
        #     post_content = self.get_post_content_push(post_href)
        #     post_content.update({"url": post_href})
        #     post_data.append(post_content)
        # post_data = self.get_title_data()
        return pd.DataFrame(post_datas)

    def find_previous_page(self):
        soup = PTT_SCRAPER.get_soup(self.url)
        prev = soup.find("a", string="‹ 上頁")
        return prev["href"]


if __name__ == "__main__":
    board = "stock"
    scraper = PTT_SCRAPER(board)
    st = time.time()
    print(scraper.fetch_posts(max_posts=30, until_date="1/20")[["title", "date"]])
    et = time.time()
    print(et - st)
    # print(pd.DataFrame(scraper.get_post_content_push("/bbs/Stock/M.1726581004.A.B1C.html")["pushes"]))
