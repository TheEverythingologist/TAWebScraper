import requests
url = 'https://www.trueachievements.com/game-pass-ultimate/games'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Site': 'none',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
    'Priority': 'u-0, i',
    'Cookie': 'ASP.NET_SessionId=z45wfsxxopqxvidfm3puo12o; ContentRecordRegionID=1; cf_clearance=GI4i2Hs3jC4y5JOOtlQoQnE2QYcUbwkbn2ZrdGneShM-1742851113-1.2.1.1-yuobSHMQBuWjrDkyu4CRDOraoN6Lb0W.IphU9gDRj2pmQs0KsCi3dnNshoN_fkzGgXkJ.jOcXAR1Gu28CBRXKrtNiuzs.YYHnhlEbV1lT5h26XwrRnwqEnVFYrcduUi8cjE1y8q0hPKMtPzuExZLZ4qyzhTFH7ig0DhR48_RY8vgBsxReAwiXOks9029LK5cteyyu4uMFNstY6leFbPDudKZTq.piFlt9.cnv_tflniK2UqkqEqQtDdWGQhcijdkCQ_TcQM67ywksfHPxGJJg5h4EQ_q1EDRSmPW8K8Y6M7_PHmB8vzU08MQr1Orrh_RwQtIf4bVxx.qelb8cgxNJQiN9OxaPkRtLL8yaK.wLo0',
    'Sec-Ch-Ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Referer': 'https://www.trueachievements.com/game-pass-ultimate/games'
}
req = requests.get(url, headers=headers, timeout=1000)

print('Done!')