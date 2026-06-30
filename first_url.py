# from curl_cffi import requests
# import json
# import jmespath

# headers = {
#     'accept': 'application/graphql+json, application/json',
#     'accept-language': 'en-US,en;q=0.9',
#     'cache-control': 'no-cache',
#     'content-type': 'application/json',
#     'origin': 'https://www.imdb.com',
#     'pragma': 'no-cache',
#     'priority': 'u=1, i',
#     'referer': 'https://www.imdb.com/',
#     'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-site',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
#     'x-amzn-sessionid': '136-9966520-8400053',
#     'x-imdb-client-name': 'imdb-web-next-localized',
#     'x-imdb-client-rid': 'NXFC5GZPBQ98YQCQG9FQ',
#     'x-imdb-consent-info': 'eyJhZ2VTaWduYWwiOiJBRFVMVCIsImlzR2RwciI6ZmFsc2V9',
#     'x-imdb-user-country': 'US',
#     'x-imdb-user-language': 'en-US',
#     'x-imdb-weblab-treatment-overrides': '{"IMDB_DISCO_KNOWNFOR_V2_1328450":"T1","IMDB_NAV_PRO_FLY_OUT_1418917":"T1","IMDB_NEXT_SSO_US_LAUNCH_1374904":"T1","IMDB_PRODUCER_CREDITS_DISPLAY_DEFAULT_1377204":"T1","IMDB_SEARCH_DISCOVER_MODERN_1367402":"T2"}',
#     #'cookie': 'session-id=136-9966520-8400053; session-id-time=2082787201l; ad-oo=0; ci=eyJhZ2VTaWduYWwiOiJBRFVMVCIsImlzR2RwciI6ZmFsc2V9; ubid-main=132-5095882-8669364; session-token=eoOoC4cJaDa3JCkZvg4XmNvQAnAQIY5XhNiQJt7ejTCIyy5rCmEX0v8nL2/Q1l5zXhDXopegRyb/HbhYSQLQQO/il/iBFNVydemTNyHJiFNRj25IvCXBLf4fJU9640F8Coaepj6e8nEPOB/+Hu3jNSfGDB2m6sTAgotXZsy5779SJmbfRxQDogqD9iIbOjrc5FaysJ0oXMMKJwufzMIMghHFrWgQL+oS',
# }

# params = {
#     'operationName': 'RVI_Items',
#     'variables': '{"count":250,"locale":"en-US"}',
#     'extensions': '{"persistedQuery":{"sha256Hash":"32eda43bfa1053f69036b945638fc4a0ae6cc4a2429de224b3185f8b0e37717b","version":1}}',
# }

# response = requests.get('https://api.graphql.imdb.com/', params=params, headers=headers)

# l1 =[]
# if response.status_code == 200:
#     with open("data.json", "w", encoding="utf-8") as f:
#         json.dump(response.json(), f, indent=4, ensure_ascii=False)

#     json_data = response.json()
#     id = jmespath.search("data.recentlyViewedItems.edges[*].node.id",json_data)

#     url = f"https://www.imdb.com/title/{id}/?ref_=chttp_t_1"
    
#     l1.append(url)

#     print(l1)
# else:
#     print("not")





from curl_cffi import requests
from parsel import Selector
import json
import jmespath
import mysql.connector



def save_urls_to_db(urls):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="actowiz",      # Change if needed
        database="imdb"          # Change your database name
    )

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imdb_urls_1 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(500) UNIQUE
        )
    """)

    query = """
        INSERT IGNORE INTO imdb_urls_1 (url)
        VALUES (%s)
    """

    data = [(url,) for url in urls]

    cursor.executemany(query, data)

    conn.commit()

    print(f"{cursor.rowcount} URLs inserted.")

    cursor.close()
    conn.close()



headers =  {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'priority': 'u=0, i',
  'referer': 'https://www.imdb.com/chart/top/',
  'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
  'Cookie': 'session-token=VuziSqmbqIPsuC02rbE1KFqABrFCW21FnlbxLGmLE4NayeQtTH2QVCCW5tACuksNpYmng3tBfYa/eZMuTw6iMeJ6LF9Y9s7D93jra21yzckPwN6e4M6kfDqstpCyuATJCZyE6u5x5J0nretWDwaK8tllyVYUroI3mui124P39k2H/tRPoWt0SxMpJX+9LRgsO8qiYYk/N1ABGBCFj/pZWkdIa10/fnwC; aws-waf-token=a879ef80-bfb5-429f-b136-a66dc3f5feef:EQoAp5Yz40MDAAAA:cjHPJgyWnI3al/pRxTr/07WpZZME/nYsATynV1VntAZzUD3ouJ5KKwOG/GqVlmEsCB6kJJMcyTAvFGfFDijvqo9fKmZBYj9geiu1BsWuXFsvgTbcQm6jZtNIgE/AGEGIG99CY7QIAjClWrec0Skh9rNDcW4+0vHFzVbawb5+BH88JpluExRvFIeGwCa7u2I=; session-id=137-9421585-4801017; session-id-time=2082787201l; ad-oo=0; csm-hit=tb:s-QCF0CZ3XKH6T1V9DE8H6|1782804494456&t:1782804496410&adb:adblk_no; ci=eyJhZ2VTaWduYWwiOiJBRFVMVCIsImlzR2RwciI6ZmFsc2V9; session-id=137-9421585-4801017; session-id-time=2082787201l; session-token=VuziSqmbqIPsuC02rbE1KFqABrFCW21FnlbxLGmLE4NayeQtTH2QVCCW5tACuksNpYmng3tBfYa/eZMuTw6iMeJ6LF9Y9s7D93jra21yzckPwN6e4M6kfDqstpCyuATJCZyE6u5x5J0nretWDwaK8tllyVYUroI3mui124P39k2H/tRPoWt0SxMpJX+9LRgsO8qiYYk/N1ABGBCFj/pZWkdIa10/fnwC; ubid-main=133-4137360-5208142'
}


response = requests.get('https://www.imdb.com/chart/top/', headers=headers,impersonate="chrome120")

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