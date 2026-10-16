import requests

url = "https://docs.powertools.aws.dev/lambda/python/latest/core/logger/"
html = requests.get(url).text

with open("logger.html", "w", encoding="utf-8") as f:
    f.write(html)