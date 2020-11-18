""" Projet de Web Scraping avec BeautifulSoup sur le site bookstoscrape.com """
import requests
from bs4 import BeautifulSoup
import pandas as pd

website_url = "books.toscrape.com"
base_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"  # Url qui va servir de base
category_list = []


def get_books_info():
    """
    Fonction qui va chercher toutes les infos spécifique à un livre.
    """
    r = requests.get(base_url)  # Requests de la page du livre
    if r.status_code == 200:  # Si la page est accessible alors on continue
        result = []  # Creation d'une liste vide pour y ajouter les infos du livres plus tard
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

        info = {"product_page_url": product_page_url, "universal_product_code": upc, "title": title,
                "price_including_tax": price_incl_tax, "price_excluding_tax": price_excl_tax,
                "number_available": number_available, "product_description": product_description, "category": category,
                "review_rating": review_rating, "image_url": image_url}
        result.append(info)
        df = pd.DataFrame(result, columns=["product_page_url", "universal_product_code", "title",
                                           "price_including_tax", "price_excluding_tax", "number_available",
                                           "product_description", "category", "review_rating", "image_url"])
        df.to_csv("book_info.csv", mode="w", encoding="utf-8", index=False)

    else:
        print(r.status_code)


def get_category_url():
    """
    Fonction qui fetch et concatenate les urls des categories pour avoir des urls valides.
    :return:
    """
    global category_list
    base_url = "http://books.toscrape.com/"

    r = requests.get(base_url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "lxml")

        categories_raw = soup.find("ul", class_="nav nav-list").find_all("a")[1:]
        for cat in categories_raw:
            catty = cat["href"].replace("/index.html", "")
            categories_url = base_url + catty
            categories_name = categories_url.replace("http://books.toscrape.com/catalogue/category/books/", "")
            category_dict = {"cat url": categories_url, "cat name": categories_name}
            category_list.append(category_dict)
    else:
        print(r.status_code)


def get_books_url():
    """
    Fonction qui va chercher les urls de chaque livre par categorie.
    :return:
    """
    # book_links = []
    links = []
    trial_url = "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
    website_url = "http://books.toscrape.com"
    global category_list
    # print(category_list)
    for key in category_list:
        url = key["cat url"]
        name = key["cat name"]
        next_url = url
        while True:
            # print(name)
            r = requests.get(next_url)
            # print(next_url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "lxml")
                lis = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
                # print(lis)
                for li in lis:
                    link = li.find("a")["href"]
                    # print(link)
                    fixed_link = link.replace('../../..', "")
                    # print(fixed_link)
                    links.append('http://books.toscrape.com/catalogue' + fixed_link)
                next_button_text = soup.find('div', class_="col-sm-8 col-md-9").find_all('a')[-1].text
                # print(next_button_text)

                if next_button_text == "next":
                    next_button = soup.find("li", class_="next").find("a", href=True)
                    next_url = url + "/" + next_button["href"]
                    # print(next_url)
                else:
                    df = pd.DataFrame(links)
                    # df.to_csv("Url_" + name + ".csv", encoding="utf-8", index=False, header=False)
                    links = []
                    # print(df1)
                    break
    print(df)




if __name__ == "__main__":
    # get_books_info()
    get_category_url()
    get_books_url()