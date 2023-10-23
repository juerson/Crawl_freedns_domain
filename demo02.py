import random
import sys
import time
import re
from datetime import datetime
import csv

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException


def get_web_data_and_write_file(page, file, writer):
    max_attempts = 3  # 设置最大尝试次数
    while True:
        try:
            elements = driver.find_elements(By.CLASS_NAME, "trl")
            for element in elements:
                first_a_element = element.find_element(By.TAG_NAME, 'a')
                domain = first_a_element.text
                span_element = element.find_element(By.CSS_SELECTOR, 'span')
                host_usage = driver.execute_script("return arguments[0].firstChild.textContent.trim();", span_element)
                match = re.search(r"\d+", host_usage)
                if match:
                    use_host_num = match.group()
                else:
                    use_host_num = '0'
                sub_results = [domain, use_host_num]
                td_elements = element.find_elements(By.TAG_NAME, 'td')
                # 使用正则表达式匹配数字和日期(提取网页中age列的数据)
                pattern = r'(\d+) days ago \((\d{2}/\d{2}/\d{4})\)'
                for td in td_elements[1:]:
                    td_info = td.text
                    if "days ago" in td_info:
                        match = re.search(pattern, td_info)
                        if match:
                            days_ago = int(match.group(1))  # 提取数字并转换为整数
                            date_str = match.group(2)  # 提取日期字符串
                            # 将日期字符串转换为 "YYYY-mm-dd" 格式
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                            # 将数据添加到列表中
                            sub_results.append(days_ago)
                            sub_results.append(formatted_date)
                        else:
                            print(f"没有匹配到任何内容，检查第{page}页网页，最后那列Age是否有其他信息干扰！")
                    else:
                        sub_results.append(td_info)
                print(*sub_results, sep=', ')
                writer.writerow(sub_results)
                file.flush()
            break  # 如果成功执行操作，退出循环
        except StaleElementReferenceException:
            if max_attempts == 0:
                sys.exit(1)
            max_attempts -= 1
            # 如果发生StaleElementReferenceException，重新打开网页，重新定位元素
            driver.get(f"https://freedns.afraid.org/domain/registry/?page={page}&sort=4&q=")
            print(f"StaleElementReferenceException异常，尝试重新打开第{page}页的网页！")
            WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CLASS_NAME, "trl")))
            time.sleep(2)


if __name__ == '__main__':
    # 启用Firefox无头模式
    options = webdriver.FirefoxOptions()
    options.headless = True
    # 初始化WebDriver并指定FirefoxOptions
    driver = webdriver.Firefox(options=options)
    start_page = 301
    end_page = 328
    driver.get(f"https://freedns.afraid.org/domain/registry/?page={start_page}&sort=4&q=")

    # 用"newline=''"参数创建CSV文件，确保每行之间有换行
    with open('output.csv', mode='w', newline='') as file:
        header = ["domain", "use numbers", "status(public/private)", "owner", "days", "datatime"]
        writer = csv.writer(file)
        # 写入标题行
        writer.writerow(header)
        for page in range(start_page, end_page):
            wait = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CLASS_NAME, "trl")))
            get_web_data_and_write_file(page, file, writer)  # 抓取数据
            time.sleep(random.randint(5, 8))
            try:
                next_page_xpath = "//td[@align='right']//a/font[contains(text(), 'Next page')]"
                # 使用XPath选择器来查找包含"Next page"字段元素
                next_page_element = driver.find_element(By.XPATH, next_page_xpath)
                # 获取<font>元素（也就是"Next page"字段元素）的父元素<a>元素
                a_next_page_element = next_page_element.find_element(By.XPATH, '..')  # 点击Next page所在元素中父元素<a>元素
                # 模拟点击该链接以打开下一页
                a_next_page_element.click()
                time.sleep(2)
            except NoSuchElementException:
                print('没有找到Next page的链接！')
        driver.quit()
