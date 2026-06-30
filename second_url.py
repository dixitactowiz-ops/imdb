from curl_cffi import requests
from parsel import Selector
import json
import jmespath
import mysql.connector

def save_urls_to_db(urls):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="actowiz",
            database="imdb"
        )

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imdb_urls_tops (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(500) UNIQUE
            )
        """)

        conn.commit()   # Commit after CREATE TABLE

        query = """
            INSERT IGNORE INTO imdb_urls_tops (url)
            VALUES (%s)
        """

        data = [(url,) for url in urls]

        cursor.executemany(query, data)
        conn.commit()

        print(f"{cursor.rowcount} URLs inserted.")

    except mysql.connector.Error as e:
        print("MySQL Error:", e)

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.imdb.com/chart/toptv/',
    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    'cookie': 'aws-waf-token=a879ef80-bfb5-429f-b136-a66dc3f5feef:EQoAeNw5qA8FAAAA:drDolvMi7YbldhYrStnpeqEk1sseCGxkBHkta1Esg0landru0WMyiUcuPyJemH3jBlDfwUQQk6lz7Ah+rmZXaWIVAMpwyLllL9Sfzp72PsXa13uY6S9bROTzbkGy/zyDIeFIDGz9IjSEUUwZeXe7xW7MYhliOZ6lPzahb6UaKaDoEB6J4+1aOQ7rprHrilE=; session-id=143-4377243-3391947; session-id-time=2082787201l; ad-oo=0; ci=eyJhZ2VTaWduYWwiOiJBRFVMVCIsImlzR2RwciI6ZmFsc2V9; ubid-main=130-1622969-9830861; session-token=RXF5CpEBZTV07iTrpVBxx+N8ZS85PhYH8jVsoBNl+poU9mU5DeiQI/wAK+Z+SffSkg5FTrFjdXh0+m0/hUprIL044g+6ZXgROBpRSAGZKXwoFquFvS9cesGddnihbfeXXxOyiz5Fofm/0szzIUqraFojrTOmH9Amdh/MBBEyN2Yaif8GaSr/NiWRE54Xm5/3nOI2oMhfJg0jx6E1JkSQVP5+N9rw+/5T; csm-hit=tb:s-P6D6Z4DPJAEFYDSATR7F|1782807768264&t:1782807768843&adb:adblk_no',
}

response = requests.get('https://www.imdb.com/chart/toptv/', headers=headers,impersonate="chrome120")


if response.status_code == 200:
    print("sucess")
    html_data = Selector(response.text)
    script_data = html_data.xpath("//script[contains(@type,'application/ld+json')]//text()").get()
    json_data = json.loads(script_data)
    with open("data.json", "w", encoding="utf-8") as f:
         json.dump(json.loads(script_data), f, indent=4, ensure_ascii=False)

    url = jmespath.search("itemListElement[*].item.url",json_data)
    urls = [
        f"{url}?ref_=chttp_t_{i}"
        for i, url in enumerate(url, start=1)
    ]
    save_urls_to_db(urls)

    print(urls)
    print(len(url))

    # print(script_data)

else:
    print(response.status_code)