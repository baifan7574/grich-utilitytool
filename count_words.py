import os
from bs4 import BeautifulSoup

def count_words_in_p():
    path = "dist/p"
    files = sorted(os.listdir(path))[:10]
    for f in files:
        with open(os.path.join(path, f), 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            text = soup.get_text()
            words = len(text.split())
            print(f"{f}: {words} words")

if __name__ == "__main__":
    count_words_in_p()
