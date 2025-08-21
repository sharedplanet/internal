import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

download_dir = os.path.join(os.getcwd(), "ndc_pdfs")
os.makedirs(download_dir, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})

driver = webdriver.Chrome(options=chrome_options)

url = "https://unfccc.int/NDCREG"
driver.get(url)
time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

records = []

for submission in soup.find_all("tr", class_=lambda x: x and x.startswith("submission-nid-")):
    country_div = submission.find("td", class_="views-field views-field-title")
    country = country_div.get_text(strip=True) if country_div else "Unknown"

    pdf_links = submission.find_all("a", class_="ndc-acr-download-link is-original")
    for link in pdf_links:
        language_span = link.find_previous("span", class_="field--name-field-set-item-language is-original")
        language = language_span.get_text(strip=True) if language_span else "Unknown"

        pdf_url = link.get("href")
        if not pdf_url.startswith("http"):
            pdf_url = "https://www4.unfccc.int" + pdf_url

        if language == "English" and pdf_url not in [r["PDF"] for r in records]:
            records.append({
                "Country": country,
                "Language": language,
                "PDF": pdf_url
            })

df = pd.DataFrame(records)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
print(df)

for i, row in df.head(10).iterrows():
    pdf_url = row["PDF"]
    country_name = row["Country"].replace(" ", "_")
    print(f"\nDownloading PDF {i+1}: {pdf_url}")
    driver.get(pdf_url)
    time.sleep(5)

driver.quit()
print(f"\nPDFs directory: {download_dir}")