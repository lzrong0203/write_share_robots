from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time


def get_news(driver):
    wait = WebDriverWait(driver, 10)
    driver.get("https://mops.twse.com.tw/mops/web/t05st02")
    year = driver.find_element(By.ID, "year")
    year.clear()
    year.send_keys("111")
    driver.find_element(By.ID, "month").send_keys("10")
    driver.find_element(By.ID, "day").send_keys("5")
    driver.find_element(By.XPATH, "//input[@value=' 查詢 ']").click()
    original_window = driver.current_window_handle
    print(driver.current_window_handle)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='詳細資料']")))
    for i, button in enumerate(driver.find_elements(By.XPATH, "//input[@value='詳細資料']")):
        button.click()
        wait.until(EC.presence_of_element_located((By.ID, "table01")))
        driver.switch_to.window(driver.window_handles[1])
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        time.sleep(0.5)
        entire = driver.find_element(By.TAG_NAME, "body")
        # driver.save_screenshot(f"{i}.png")
        entire.screenshot(f"{i}.png")
        print(f"{i}.png...")
        driver.close()
        driver.switch_to.window(original_window)
        if i == 3:
            break
        time.sleep(3)


if __name__ == "__main__":
    options = Options()
    options.headless = True
    with webdriver.Firefox() as driver:
        get_news(driver)
