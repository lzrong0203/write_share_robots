import firebase_admin
from firebase_admin import credentials, storage
# from ch21.selenium_test import get_news
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import os


class FirebaseStorageUploader:
    def __init__(self):
        """
        初始化 Firebase Storage
        """
        # 初始化 Firebase（請替換成您的憑證檔案路徑）
        cred = credentials.Certificate("stocksentiment-8cf69-firebase-adminsdk-rsalw-a998bda61f.json")
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'stocksentiment-8cf69.firebasestorage.app'
        })
        self.bucket = storage.bucket()

    def upload_image(self, image_path, storage_path):
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


def get_news(driver, max_news=10):
    wait = WebDriverWait(driver, 10)
    driver.get("https://mopsov.twse.com.tw/mops/web/t05st02")
    year = driver.find_element(By.ID, "year")
    year.clear()
    year.send_keys("114")
    driver.find_element(By.ID, "month").send_keys("2")
    driver.find_element(By.ID, "day").send_keys("27")
    driver.find_element(By.XPATH, "//input[@value=' 查詢 ']").click()
    original_window = driver.current_window_handle
    print(driver.current_window_handle)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='詳細資料']")))

    # 找到所有包含詳細資料按鈕的列
    table = driver.find_element(By.ID, 'table01')
    rows = table.find_elements(By.TAG_NAME, 'table')
    data = rows[2].find_elements(By.TAG_NAME, 'tr')
    data.pop(0)
    # print(data[0].find_elements(By.TAG_NAME, 'td'))
    # 解析每一行資料
    for i, row in enumerate(data):
        if i >= max_news:
            break

        cells = row.find_elements(By.TAG_NAME, 'td')

        if len(cells) > 0:
            # stock_code = cells[2].text.strip()  # 股票代碼
            # print(stock_code)
            # date = cells[0].text.strip()  # 日期
            # print(f"股票代碼: {stock_code}, 日期: {date}")
            #
            announce_date = cells[0].text.strip()  # 發言日期
            announce_time = cells[1].text.strip()  # 發言時間
            stock_id = cells[2].text.strip()  # 公司代號

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
        entire.screenshot(filename)
        print(f"儲存圖片: {filename}, 股票代號: {stock_id}")

        driver.close()
        driver.switch_to.window(original_window)
        time.sleep(1)


def run_scraper_and_upload(max_news=3):
    uploader = FirebaseStorageUploader()

    options = Options()
    options.add_argument("--headless")

    with webdriver.Firefox(options=options) as driver:
        get_news(driver, max_news)

        # 尋找所有已下載的圖片並上傳
        for filename in os.listdir('.'):
            if filename.endswith('.png'):
                # 從檔名解析股票代碼和時間
                parts = filename.replace('.png', '').split('_')
                stock_id = parts[0]  # 股票代碼
                date_time = f"{parts[1]}_{parts[2]}"  # 日期和時間

                if os.path.exists(filename):
                    # 上傳到 Firebase Storage，路徑包含股票代碼子目錄
                    url = uploader.upload_image(
                        image_path=filename,
                        storage_path=f"{stock_id}/{date_time}"  # 例如: 2330/1130103_160807
                    )

                    if url:
                        print(f"已上傳圖片: {filename} 至: {url}")

                    # 上傳完成後刪除本地檔案
                    os.remove(filename)
                    print(f"已刪除本地檔案: {filename}")


if __name__ == "__main__":
    run_scraper_and_upload(max_news=5)