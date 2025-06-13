from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

BRANDS = ["nike", "adidas", "reebok", "puma", "under armour", "zara"]

def get_reviews_count(soup):
    reviews = soup.find_all('div', class_='review__title')
    return len(reviews)

def get_sellers_count(soup):
    sellers = soup.find_all('div', class_='sellers-table__seller')
    return len(sellers)

def has_buy_button(soup):
    return bool(soup.find('button', class_='button_type_primary'))

def is_brand(name):
    lname = name.lower()
    return any(b in lname for b in BRANDS)

def parse(query, min_reviews, max_sellers):
    items = []
    for page in range(1, 3):
        url = f"https://kaspi.kz/shop/search/?text={query}&page={page}"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'html.parser')
        cards = soup.find_all('a', class_='item-card__name-link')
        for a in cards:
            link = "https://kaspi.kz" + a['href']
            title = a.text.strip()
            if is_brand(title):
                continue
            pr = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            s2 = BeautifulSoup(pr.text, 'html.parser')
            reviews = get_reviews_count(s2)
            sellers = get_sellers_count(s2)
            if reviews < min_reviews or sellers > max_sellers:
                continue
            if not has_buy_button(s2):
                continue
            price = s2.find('div', class_='product__price').text.strip()
            items.append({
                "title": title,
                "price": price,
                "reviews": reviews,
                "sellers": sellers,
                "link": link
            })
    return items

@app.route('/', methods=['GET', 'POST'])
def home():
    results = None
    if request.method == 'POST':
        q = request.form.get('query')
        mr = int(request.form.get('min_reviews', 4))
        ms = int(request.form.get('max_sellers', 3))
        results = parse(q, mr, ms)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
