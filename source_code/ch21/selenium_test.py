from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome import options as chrome_options
from selenium.webdriver.firefox import options as fire_options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from tqdm import tqdm


class TWSE_NEWS:
    def __init__(self, browser="FireFox", max_records=3, headless=True):
        if browser == "Chrome":
            options = chrome_options.Options()
            if headless:
                options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(options=options)

        elif browser == "FireFox":
            options = fire_options.Options()
            if headless:
                options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=options)

        self.max_records = max_records
        self.wait = WebDriverWait(self.driver, 5)
        self.output_directory = "screenshots"
        self.setup_output_directory()

    def setup_output_directory(self):
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)

    def get_screenshot_name(self, company_code):
        timestamp = time.strftime("%Y%m%d_%H%M")
        filename = f"/{company_code}_{timestamp}.png"
        return str(Path(self.output_directory) / filename)

    def test_driver(self, url):
        self.driver.get(url)
        time.sleep(5)
        self.driver.close()

    def get_day_news(self, url, year, month, day):
        self.driver.get(url)
        year_element = self.driver.find_element(By.ID, "year")
        year_element.clear()
        year_element.send_keys(year)

        self.driver.find_element(By.ID, "month").send_keys(month)
        self.driver.find_element(By.ID, "day").send_keys(day)
        self.driver.find_element(By.XPATH, "//input[@value=' 查詢 ']").click()

        wait = WebDriverWait(self.driver, timeout=5)
        element = (By.XPATH, "//input[@value='詳細資料']")
        condition = EC.element_to_be_clickable(element)
        self.wait.until(condition)
        buttons = self.driver.find_elements(By.XPATH, "//input[@value='詳細資料']")
        codes = self.driver.find_elements(By.XPATH, "//pre")
        # for code in codes:
        #     print(code.text.strip())
        self.get_news_content((buttons, codes))

    def get_news_content(self, info):
        for i in tqdm(range(min(len(info[0]), self.max_records)), desc="Processing news"):
            # print(self.driver.window_handles)
            root = self.driver.current_window_handle
            info[0][i].click()
            # print("After click", self.driver.window_handles)
            code = info[1][i].text.strip()
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.capture_detail_page(code)
            self.driver.switch_to.window(root)

    def capture_detail_page(self, code):
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        # print(self.driver.find_element(By.CLASS_NAME, "compName").text)
        # print(self.driver.find_element(By.XPATH, "//pre").text)
        # self.driver.save_screenshot(self.get_screenshot_name(code).replace(".png", "_1.png"))
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.screenshot(self.get_screenshot_name(code))
        self.driver.close()

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    driver = TWSE_NEWS(headless=True)
    url = "https://mops.twse.com.tw/mops/web/t05st02"
    driver.get_day_news(url, year=113, month=5, day=8)
    driver.close()
