import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()
"""
该版本写法，有hug，有时候抓取不到数据，睡眠时间一样不行
"""
if __name__ == '__main__':
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    base_url = "https://freedns.afraid.org/domain/registry/"
    domain_results = []
    page = 3  # 使用for循环抓取每页的数据时，遇到无法抓取到内容的hug，手动修改page，抓取某页数据时，一样可能遇到有能抓取到数据，有时不能抓取数据
    with open('domain.txt', mode='a+', encoding='utf-8') as wf:
        if page == 1:
            url = base_url
        else:
            headers["Referer"] = base_url + f"page-{page - 1}.html"
            url = base_url + f"page-{page}.html"
        try:
            print(url)
            response = requests.get(url, headers=headers, verify=False)
            print(f'正在解析第{page}页数据...')
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            table_elements = soup.find_all("table")
            if len(table_elements) > 3:
                table_element_domain = table_elements[3]
                tr_elements = soup.find_all('tr', class_='trl')
                domain_li = [tr.find_next('a').text for tr in tr_elements]
                for domain in domain_li:
                    print(domain)
                    wf.write(f'{domain}\n')
        except (requests.exceptions.RequestException, Exception) as e:
            print(f"An error occurred: {e}")
