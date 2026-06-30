import os
import gzip
import mysql.connector
from parsel import Selector
from curl_cffi import requests
from concurrent.futures import ThreadPoolExecutor

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "imdb"
}

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS imdbTv (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255),
        title VARCHAR(255),
        year VARCHAR(10),
        certificate VARCHAR(20),
        runtime VARCHAR(20),
        imdb_rating VARCHAR(10),
        rating_count VARCHAR(20),
        popularity VARCHAR(20)
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def save_page_gz(content, filename, folder="tv_pages"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{filename}.html.gz")
    with gzip.open(file_path, "wt", encoding="utf-8") as f:
        f.write(content)

def process_url(row):
    url_id, url = row
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.imdb.com/',
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
        'cookie': 'csm-hit=tb:9JVJR5YCJFCGMADDR2F0+s-9JVJR5YCJFCGMADDR2F0|1782814762963&t:1782814762963&adb:adblk_no; aws-waf-token=a879ef80-bfb5-429f-b136-a66dc3f5feef:EQoAtYRHB4kQAAAA:/VLvSYCQRsTvLsp9s1PMhWDl8TSQhTqAx7aIS9xjkr5q9zlvNa05ZA+CeOQnhDhOFOnMsH8cfENf+4a8/vLPfIG43o7jkb46p5lm/Lu/inpVpcSLYb89FEOP4Q3gvWm9xp0bf9CwU6Gch3NrWPIgeIiUnPwHTgOpHvxfKjz082KFhD1hersA36Q2E/4QNHA=',

    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome136")
        if response.status_code == 200:
            movie_id = url.split("/title/")[1].split("/")[0]
            
            save_page_gz(response.text, movie_id)
            
            selector = Selector(response.text)
            title = selector.xpath('//h1[@data-testid="hero__pageTitle"]/span/text()').get()
            certificate = selector.xpath('//a[contains(@href,"parentalguide")]/text()').get()
            year = selector.xpath('//h1[@data-testid="hero__pageTitle"]/following-sibling::ul/li[2]/a/text()').get()
            runtime = selector.xpath('//li[@data-testid="title-techspec_runtime"]//div[@class="ipc-metadata-list-item__content-container"]//span/text()').get()
            imdb_rating = selector.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span[1]/text()').get()
            rating_count = selector.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/following-sibling::div/text()').get()
            popularity = selector.xpath('//div[@data-testid="hero-rating-bar__popularity__score"]/text()').get()

            cursor.execute("""
            INSERT INTO imdbTv
            (url, title, year, certificate, runtime, imdb_rating, rating_count, popularity)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (url, title, year, certificate, runtime, imdb_rating, rating_count, popularity))

            cursor.execute("""
            UPDATE imdb_urls_tops 
            SET STATUS = 1 
            WHERE id = %s
            """, (url_id,))
            
            conn.commit()
            print("Saved:", title)
        else:
            print(f"Failed {response.status_code}: {url}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
    
    main_conn = mysql.connector.connect(**DB_CONFIG)
    main_cursor = main_conn.cursor()
    main_cursor.execute("SELECT id, url FROM imdb_urls_tops WHERE STATUS = 0 ORDER BY id ASC")
    urls_to_process = main_cursor.fetchall()
    main_cursor.close()
    main_conn.close()

    if urls_to_process:
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(process_url, urls_to_process)
            
    print("Completed")