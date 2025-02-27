import os
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from django.conf import settings


class FirebaseStorageManager:
    """Firebase Storage 管理類，用於上傳和獲取 MOPS 重大訊息圖片"""
    
    _instance = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        """獲取單例實例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化 Firebase Storage"""
        if not FirebaseStorageManager._initialized:
            # 檢查 Firebase 是否已初始化
            try:
                # 嘗試獲取已存在的 Firebase 應用
                app = firebase_admin.get_app()
                self.bucket = storage.bucket(app=app)
            except ValueError:
                # 如果未初始化，則初始化 Firebase
                cred_path = os.path.join(settings.BASE_DIR, 'stocksentiment-8cf69-firebase-adminsdk-rsalw-001d55408c.json')
                cred = credentials.Certificate(cred_path)
                app = firebase_admin.initialize_app(cred, {
                    'storageBucket': 'stocksentiment-8cf69.firebasestorage.app'
                }, name='storage_app')
                self.bucket = storage.bucket(app=app)
            
            FirebaseStorageManager._initialized = True
        else:
            # 如果已經初始化，使用現有的應用
            try:
                app = firebase_admin.get_app(name='storage_app')
            except ValueError:
                app = firebase_admin.get_app()
            self.bucket = storage.bucket(app=app)
    
    def upload_image(self, image_path, storage_path):
        """上傳圖片到 Firebase Storage"""
        try:
            # 加入 mops_images 前綴到儲存路徑
            blob = self.bucket.blob(f"mops_images/{storage_path}")
            blob.upload_from_filename(image_path)
            blob.make_public()
            
            print(f"成功上傳圖片: {blob.public_url}")
            return blob.public_url
        
        except Exception as e:
            print(f"上傳失敗: {e}")
            return None
    
    def get_news_images(self, stock_id=None, limit=10):
        """獲取 MOPS 重大訊息圖片列表
        
        Args:
            stock_id: 股票代碼，如果提供則只獲取該股票的圖片
            limit: 最大獲取數量
            
        Returns:
            圖片列表，每個元素包含 url, stock_id, date, time
        """
        try:
            prefix = f"mops_images/{stock_id}/" if stock_id else "mops_images/"
            blobs = list(self.bucket.list_blobs(prefix=prefix, max_results=limit))
            
            result = []
            for blob in blobs:
                # 從路徑解析股票代碼和時間
                # 路徑格式: mops_images/2330/20231105_133803
                path_parts = blob.name.replace('mops_images/', '').split('/')
                if len(path_parts) >= 2:
                    stock_id = path_parts[0]
                    date_time = path_parts[1].split('_')
                    
                    if len(date_time) >= 2:
                        # 將日期格式化為 YYYY/MM/DD
                        date_str = date_time[0]
                        if len(date_str) == 8:  # YYYYMMDD
                            date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"
                        else:
                            date = date_str
                        
                        # 將時間格式化為 HH:MM:SS
                        time_str = date_time[1]
                        if len(time_str) == 6:  # HHMMSS
                            time_formatted = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                        else:
                            time_formatted = time_str
                        
                        result.append({
                            'url': blob.public_url,
                            'stock_id': stock_id,
                            'date': date,
                            'time': time_formatted
                        })
            
            return result
        
        except Exception as e:
            print(f"獲取圖片列表失敗: {e}")
            return []


def scrape_mops_news(max_news=5):
    """爬取 MOPS 重大訊息並上傳到 Firebase Storage
    
    Args:
        max_news: 最大爬取數量
        
    Returns:
        上傳成功的圖片 URL 列表
    """
    storage_manager = FirebaseStorageManager.get_instance()
    uploaded_urls = []
    
    options = Options()
    options.headless = True
    
    # 確保臨時目錄存在
    temp_dir = os.path.join(settings.BASE_DIR, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        with webdriver.Firefox(options=options) as driver:
            wait = WebDriverWait(driver, 10)
            driver.get("https://mops.twse.com.tw/mops/web/t05st02")
            
            # 設定查詢日期為今天
            today = datetime.now()
            year = driver.find_element(By.ID, "year")
            year.clear()
            # 轉換為民國年
            year.send_keys(str(today.year - 1911))
            driver.find_element(By.ID, "month").send_keys(str(today.month))
            driver.find_element(By.ID, "day").send_keys(str(today.day))
            driver.find_element(By.XPATH, "//input[@value=' 查詢 ']").click()
            
            original_window = driver.current_window_handle
            wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='詳細資料']")))
            
            # 找到所有包含詳細資料按鈕的列
            table = driver.find_element(By.ID, 'table01')
            rows = table.find_elements(By.TAG_NAME, 'table')
            data = rows[2].find_elements(By.TAG_NAME, 'tr')
            data.pop(0)  # 移除標題行
            
            # 解析每一行資料
            for i, row in enumerate(data):
                if i >= max_news:
                    break
                
                cells = row.find_elements(By.TAG_NAME, 'td')
                
                if len(cells) > 0:
                    announce_date = cells[0].text.strip()  # 發言日期
                    announce_time = cells[1].text.strip()  # 發言時間
                    stock_id = cells[2].text.strip()  # 公司代號
                    company_name = cells[3].text.strip()  # 公司名稱
                    news_type = cells[4].text.strip()  # 主旨
                    
                    # 點擊詳細資料按鈕
                    button = row.find_element(By.XPATH, ".//input[@value='詳細資料']")
                    button.click()
                    
                    wait.until(EC.presence_of_element_located((By.ID, "table01")))
                    driver.switch_to.window(driver.window_handles[1])
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
                    time.sleep(0.5)
                    entire = driver.find_element(By.TAG_NAME, "body")
                    
                    # 使用股票代號和時間建立檔名
                    filename = f"{stock_id}_{announce_date.replace('/', '')}_{announce_time.replace(':', '')}.png"
                    temp_path = os.path.join(temp_dir, filename)
                    
                    entire.screenshot(temp_path)
                    print(f"儲存圖片: {filename}, 股票代號: {stock_id}")
                    
                    # 上傳到 Firebase Storage
                    storage_path = f"{stock_id}/{announce_date.replace('/', '')}_{announce_time.replace(':', '')}"
                    url = storage_manager.upload_image(temp_path, storage_path)
                    
                    if url:
                        uploaded_urls.append({
                            'url': url,
                            'stock_id': stock_id,
                            'company_name': company_name,
                            'date': announce_date,
                            'time': announce_time,
                            'news_type': news_type
                        })
                        print(f"已上傳圖片: {filename} 至: {url}")
                    
                    # 上傳完成後刪除本地檔案
                    os.remove(temp_path)
                    
                    driver.close()
                    driver.switch_to.window(original_window)
                    time.sleep(1)
            
            return uploaded_urls
    
    except Exception as e:
        print(f"爬取 MOPS 重大訊息失敗: {e}")
        return [] 