""" Projet de Web Scraping avec BeautifulSoup sur le site bookstoscrape.com """
import requests
from bs4 import BeautifulSoup
import pandas as pd
import wget
import os

website_url = "http://books.toscrape.com"
category_list = []
df1 = pd.DataFrame()
if os.path.isdir("Book_image") == False and os.path.isdir("Book_Info") == False:  # Vérifie si les dossiers existe, et les crée si besoin
    os.mkdir("Book_image")
    os.mkdir("Book_info")
else:  #  Sinon continue
    pass

img_path = os.getcwd() + "/Book_image/"
info_path = os.getcwd() + "/Book_info/"


def get_books_info():
    """
    Fonction qui va chercher toutes les infos spécifique à un livre.
    """
    global df1
    for links, category in df1.iterrows():
        book_url = category["Links"]
        category_name = category["Category"]
        r = requests.get(book_url)  # Requests de la page du livre
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

            # Extraction de la description du livre
            product_description = soup.find("article", class_="product_page").find_all("p")[3].text

            category = soup.find("ul", class_="breadcrumb").find_all("a")[-1].text  # Extraction de la categorie du livre

            review_rating = soup.find("p", class_="star-rating")["class"][-1] + " Out of Five"  # Extraction des reviews

            image_raw = soup.find("img", alt=title)["src"]  # Extraction de l'url brut de la jaquette
            image_url = website_url + image_raw.replace("../..", "")  # Correction du lien brut pour avoir le bon url
            wget.download(image_url,  img_path + title.replace('/', "_") + '.jpg')  # Telechargement des images
            image_location = img_path + title.replace('/', '_' + '.jpg')  # Ajout d'une colonne pour l'emplacement de l'image

            product_page_url = book_url


            info = {"product_page_url": product_page_url, "universal_product_code": upc, "title": title,
                    "price_including_tax": price_incl_tax, "price_excluding_tax": price_excl_tax,
                    "number_available": number_available, "product_description": product_description, "category": category,
                    "review_rating": review_rating, "image_url": image_url, "image_location": image_location}
            result.append(info)
            df = pd.DataFrame(result, columns=["product_page_url", "universal_product_code", "title",
                                               "price_including_tax", "price_excluding_tax", "number_available",
                                               "product_description", "category", "review_rating", "image_url", "image_location"])
            if os.path.isfile(info_path + category_name + '.csv'):
                df.to_csv(info_path + category_name + ".csv", mode="a", encoding="utf-8", index=False, header=False)
            else:
                df.to_csv(info_path + category_name + ".csv", mode="a", encoding="utf-8", index=False, header=True)
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
    global df1
    links = []
    global category_list
    for key in category_list:
        url = key["cat url"]
        name = key["cat name"]
        next_url = url
        while True:
            r = requests.get(next_url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "lxml")
                lis = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
                for li in lis:
                    link = li.find("a")["href"]
                    fixed_link = link.replace('../../..', "")
                    links.append('http://books.toscrape.com/catalogue' + fixed_link)
                next_button_text = soup.find('div', class_="col-sm-8 col-md-9").find_all('a')[-1].text

                if next_button_text == "next":
                    next_button = soup.find("li", class_="next").find("a", href=True)
                    next_url = url + "/" + next_button["href"]
                else:
                    information = {"Links": links, "Category": name}
                    df = pd.DataFrame(information)  # columns=["Links", "Category"]
                    df1 = df1.append(df)
                    # df1.to_csv("Url_Books.csv", encoding="utf-8", index=False)
                    links = []
                    break


if __name__ == "__main__":
    get_category_url()
    get_books_url()
    get_books_info()

