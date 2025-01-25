import requests
from bs4 import BeautifulSoup
import re
import time

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?\-–]', '', text)
    text = text.strip()
    return text if text else None

def scrape_wikipedia(start_url, output_file, max_articles=100):
    visited = set()
    to_visit = [start_url]
    collected_data = []

    while to_visit and len(collected_data) < max_articles:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка при запросе {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        visited.add(url)

        paragraphs = soup.find_all('p')
        article_text = ' '.join([clean_text(p.text) for p in paragraphs if clean_text(p.text)])

        if article_text:
            collected_data.append(article_text)
            print(f"Сохранена статья: {url}")

        for a in soup.find_all('a', href=True):
            if re.match(r"^/wiki/", a['href']) and ':' not in a['href']:
                full_url = f"https://ru.wikipedia.org{a['href']}"
                if full_url not in visited:
                    to_visit.append(full_url)

        time.sleep(0)

    with open(output_file, 'a', encoding='utf-8') as f:
        f.write('\n\n'.join(collected_data) + '\n\n')

    print(f"Сохранено {len(collected_data)} статей в файл {output_file}.")

if __name__ == "__main__":
    while True:
        start_url = "https://ru.wikipedia.org/wiki/" + input("(https://ru.wikipedia.org/wiki/Тема): ")
        output_file = "wikipedia_dataset.txt"
        scrape_wikipedia(start_url, output_file, max_articles=150)
