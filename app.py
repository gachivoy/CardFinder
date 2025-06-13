from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BRANDS = ["nike", "adidas", "reebok", "puma", "zara", "apple", "samsung"]

def is_brand(name):
    return any(b in name.lower() for b in BRANDS)

def get_reviews_count(soup):
    return len(soup.find_all('div', class_='review__title'))

def get_sellers_count(soup):
    return len(soup.find_all('div', class_='sellers-table__seller'))

def has_buy_button(soup):
    return soup.find('button', class_='button_type_primary') is not None

def parse_category(category_url, max_reviews, max_sellers):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9",
    }
    items = []
    for page in range(1, 3):  # Кол-во страниц на категорию
        url = f"{category_url}?page={page}"
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('a', class_='item-card__name-link')
        for a in links:
            title = a.text.strip()
            if is_brand(title):
                continue
            link = "https://kaspi.kz" + a['href']
            try:
                product_page = requests.get(link, headers=headers)
                psoup = BeautifulSoup(product_page.text, 'html.parser')
                reviews = get_reviews_count(psoup)
                sellers = get_sellers_count(psoup)
                if reviews > max_reviews or sellers > max_sellers:
                    continue
                if not has_buy_button(psoup):
                    continue
                price = psoup.find('div', class_='product__price').text.strip()
                items.append({
                    "title": title,
                    "price": price,
                    "reviews": reviews,
                    "sellers": sellers,
                    "link": link
                })
            except Exception as e:
                print(f"Ошибка: {e}")
    return items

@app.route("/", methods=["GET", "POST"])
def home():
    results = None
    if request.method == "POST":
        cat_url = request.form.get("category")
        max_reviews = int(request.form.get("max_reviews", 20))
        max_sellers = int(request.form.get("max_sellers", 3))
        results = parse_category(cat_url, max_reviews, max_sellers)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
