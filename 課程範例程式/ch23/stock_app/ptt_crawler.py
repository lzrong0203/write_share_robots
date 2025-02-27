import requests
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from .firebase_ptt import upload_ptt_post

class PTTCrawler:
    """PTT 股票版爬蟲類"""
    
    PTT_URL = 'https://www.ptt.cc'
    STOCK_BOARD = '/bbs/Stock'
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 處理年齡驗證
        self._handle_age_check()
    
    def _handle_age_check(self):
        """處理 PTT 的年齡驗證"""
        response = self.session.get(f"{self.PTT_URL}{self.STOCK_BOARD}/index.html")
        if "年齡驗證" in response.text:
            payload = {
                'from': f'{self.STOCK_BOARD}/index.html',
                'yes': 'yes'
            }
            self.session.post(f'{self.PTT_URL}/ask/over18', data=payload)
    
    def get_latest_posts(self, pages=1):
        """獲取最新的文章列表
        
        Args:
            pages: 要爬取的頁數
            
        Returns:
            文章列表，每個元素包含 title, author, date, url
        """
        posts = []
        current_page_url = f"{self.STOCK_BOARD}/index.html"
        
        for _ in range(pages):
            response = self.session.get(f"{self.PTT_URL}{current_page_url}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 獲取文章列表
            for div in soup.find_all('div', class_='r-ent'):
                title_div = div.find('div', class_='title')
                
                # 跳過被刪除的文章
                if '(本文已被刪除)' in title_div.text:
                    continue
                
                title_link = title_div.find('a')
                if title_link:
                    title = title_link.text.strip()
                    url = title_link['href']
                    
                    meta_div = div.find('div', class_='meta')
                    author = meta_div.find('div', class_='author').text.strip()
                    date = meta_div.find('div', class_='date').text.strip()
                    
                    posts.append({
                        'title': title,
                        'author': author,
                        'date': date,
                        'url': url
                    })
            
            # 獲取上一頁的連結
            prev_link = soup.find('a', string='‹ 上頁')
            if prev_link:
                current_page_url = prev_link['href']
            else:
                break
        
        return posts
    
    def get_post_content(self, post_url):
        """獲取文章內容
        
        Args:
            post_url: 文章 URL
            
        Returns:
            文章內容，包含 title, author, date, content, pushes
        """
        response = self.session.get(f"{self.PTT_URL}{post_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 獲取文章標題、作者、日期
        main_content = soup.find('div', id='main-content')
        if not main_content:
            return {
                'title': "無法獲取文章",
                'author': "Unknown",
                'date': datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
                'content': "無法獲取文章內容",
                'pushes': []
            }
        
        # 獲取文章 meta 資訊
        meta_lines = main_content.find_all('span', class_='article-meta-value')
        if len(meta_lines) >= 4:
            author = meta_lines[0].text
            board = meta_lines[1].text
            title = meta_lines[2].text
            date = meta_lines[3].text
        else:
            # 如果無法獲取完整的 meta 資訊，使用預設值
            author = "Unknown"
            board = "Stock"
            title = "Unknown Title"
            date = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        
        # 獲取文章內容
        # 複製 main_content 以避免修改原始對象
        content_div = main_content
        
        # 移除 meta 資訊
        for meta in content_div.find_all('div', class_='article-metaline'):
            meta.extract()
        for meta in content_div.find_all('div', class_='article-metaline-right'):
            meta.extract()
        
        # 移除推文
        for push in content_div.find_all('div', class_='push'):
            push.extract()
        
        # 移除引用的文章資訊
        for span in content_div.find_all('span', class_='f2'):
            if '※ 發信站:' in span.text or '※ 文章網址:' in span.text or '※ 編輯:' in span.text:
                span.extract()
        
        # 獲取清理後的文章內容
        content = content_div.text.strip()
        
        # 獲取推文
        pushes = []
        for push in soup.find_all('div', class_='push'):
            push_tag = push.find('span', class_='push-tag')
            push_userid = push.find('span', class_='push-userid')
            push_content = push.find('span', class_='push-content')
            push_ipdatetime = push.find('span', class_='push-ipdatetime')
            
            if push_tag and push_userid and push_content and push_ipdatetime:
                push_type = push_tag.text.strip()
                push_user = push_userid.text.strip()
                push_text = push_content.text.strip()
                if push_text.startswith(': '):
                    push_text = push_text[2:]
                push_time = push_ipdatetime.text.strip()
                
                pushes.append({
                    'type': push_type,
                    'user': push_user,
                    'content': push_text,
                    'time': push_time
                })
        
        return {
            'title': title,
            'author': author,
            'date': date,
            'content': content,
            'pushes': pushes
        }
    
    def crawl_and_upload(self, pages=1):
        """爬取文章並上傳到 Firebase
        
        Args:
            pages: 要爬取的頁數
            
        Returns:
            上傳成功的文章數量
        """
        posts = self.get_latest_posts(pages)
        uploaded_count = 0
        
        for post in posts:
            try:
                post_content = self.get_post_content(post['url'])
                
                # 上傳到 Firebase
                post_id = upload_ptt_post(
                    title=post_content['title'],
                    author=post_content['author'],
                    date=post_content['date'],
                    content=post_content['content'],
                    pushes=post_content['pushes']
                )
                
                if post_id:
                    uploaded_count += 1
                    print(f"上傳成功: {post_content['title']}")
                else:
                    print(f"上傳失敗: {post_content['title']}")
                
                # 避免過快請求
                time.sleep(1)
            
            except Exception as e:
                print(f"處理文章時發生錯誤: {e}")
                continue
        
        return uploaded_count


def crawl_ptt_stock(pages=1):
    """爬取 PTT 股票版文章並上傳到 Firebase
    
    Args:
        pages: 要爬取的頁數
        
    Returns:
        上傳成功的文章數量
    """
    crawler = PTTCrawler()
    return crawler.crawl_and_upload(pages) 