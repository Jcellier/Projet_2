""" Projet de Web Scraping avec BeautifulSoup sur le site bookstoscrape.com """
import requests
from bs4 import BeautifulSoup

website_url = "books.toscrape.com"
base_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"  # Url qui va servir de base


def get_books_info():
    """ Fonction qui va chercher toutes les infos spécifique à un livre"""
    r = requests.get(base_url)  # Requests de la page du livre
    soup = BeautifulSoup(r.content, 'lxml')  # Parsing, mise en page de la page du livre

    upc = soup.find("table", class_="table table-striped").td.text  # Extraction de la donnée upc du livre

    title = soup.find("div", class_="col-sm-6 product_main").h1.text  # Extraction du titre du livre

    price_incl_tax = soup.find("table", class_="table table-striped").\
        find("th", text="Price (incl. tax)").nextSibling.text  # Extraction du prix TTC du livre
    price_excl_tax = soup.find("table", class_="table table-striped").\
        find("th", text="Price (excl. tax)").nextSibling.text  # Extraction du prix HT du livre

    availability = soup.find_all("td")[-2].text  # Extraction du nombre d'exemplaires disponible
    number_available = availability[10:12]  # Formattage de la string pour avoir un nombre

    product_description = soup.find("article", class_="product_page").find_all("p")[-1].text  # Extraction de la description du livre

    category = soup.find("ul", class_="breadcrumb").find_all("a")[-1].text  # Extraction de la categorie du livre

    review_rating = soup.find("p", class_="star-rating")["class"][-1] + " Out of Five"  # Extraction des reviews

    image_raw = soup.find("img", alt=title)["src"]  # Extraction de l'url brut de la jaquette
    image_url = website_url + image_raw.replace("../..", "")  # Correction du lien brut pour qvoir le bon url

    product_page_url = base_url

    print(image_url)


if __name__ == "__main__":
    get_books_info()
