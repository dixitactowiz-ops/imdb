import os
import gzip
import mysql.connector
from parsel import Selector
from curl_cffi import requests

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz",
    database="imdb"
)
cursor = conn.cursor()

# Create data table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS imdb_movies (
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


def save_page_gz(content, filename, folder=r"D:\pagesave\imdb"):
    """
    Save HTML page as a .gz file.
    """
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{filename}.gz")
    
    with gzip.open(file_path, "wt", encoding="utf-8") as f:
        f.write(content)
        
    print(f"GZ Saved: {file_path}")


# 1. Fetch only pending URLs (STATUS = 0)
cursor.execute("SELECT id, url FROM imdb_urls_1 WHERE STATUS = 0 ORDER BY id ASC")
urls = cursor.fetchall()

for row in urls:
    url_id = row[0]
    url = row[1]
    
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.imdb.com/title/',
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
        response = requests.get(
            url,
            headers=headers,
            impersonate="chrome136",
            timeout=15
        )
    except Exception as e:
        print(f"Network error on {url}: {e}")
        continue

    if response.status_code == 200:
        # Generate a unique filename using the IMDb ID (extracted from URL) or the row ID
        imdb_id = url.split("/title/")[-1].split("/")[0] if "/title/" in url else f"movie_{url_id}"
        
        # 2. Save raw HTML content to a compressed gzip file
        save_page_gz(response.text, imdb_id)

        # 3. Parse fields from HTML response
        selector = Selector(response.text)
        title = selector.xpath('//h1[@data-testid="hero__pageTitle"]/span/text()').get()
        year = selector.xpath('//h1[@data-testid="hero__pageTitle"]/following-sibling::ul/li[1]/a/text()').get()
        certificate = selector.xpath('//h1[@data-testid="hero__pageTitle"]/following-sibling::ul/li[2]/a/text()').get()
        runtime = selector.xpath('//h1[@data-testid="hero__pageTitle"]/following-sibling::ul/li[3]/text()').get()
        imdb_rating = selector.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span[1]/text()').get()
        rating_count = selector.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/following-sibling::div/text()').get()
        popularity = selector.xpath('//div[@data-testid="hero-rating-bar__popularity__score"]/text()').get()

        # 4. Save extracted items to data table
        cursor.execute("""
        INSERT INTO imdb_movies
        (url, title, year, certificate, runtime, imdb_rating, rating_count, popularity)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (url, title, year, certificate, runtime, imdb_rating, rating_count, popularity))

        # 5. Update source queue table status from 0 to 1
        cursor.execute("""
        UPDATE imdb_urls_1 
        SET STATUS = 1 
        WHERE id = %s
        """, (url_id,))
        
        conn.commit()
        print(f"DB updated: {title} (ID: {url_id})")
        
    else:
        print(f"Failed Status: {response.status_code} for URL: {url}")

cursor.close()
conn.close()
print("Process finished.")