from django.core.management.base import BaseCommand
from django.core.validators import RegexValidator
from bs4 import BeautifulSoup
import requests
from products.models import Category, Product
import multiprocessing
import logging
import json
import time
from django.core import files
from io import BytesIO

FORMAT = '%(asctime) - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO,
                    format=FORMAT)

title_validator = RegexValidator("^[а-яА-Яa-zA-Z0-9,\-\(\)\._ \t\/]*$")
price_validator = RegexValidator("^[0-9 ]*$")

headers = {'User-agent': 'Mozilla/5.0'}


def get_with_timeout(url, timeout=60):
    """
    citilink банит айпишники, чтобы парсить на постоянной освнове,
    нужно либо брать прокси, либо селениумом открывать и ждать пока
    jquery не обновит страницу и увеличивать timeout, можно рекурсивно
    """
    time.sleep(timeout)
    return requests.get(url, headers=headers)


def save_product(soup, category, sub_name):

    input_list = None
    product_list = soup.find("section", {"class": "ProductGroupList"})
    product_grid = soup.find("section", {"class": "GroupGrid"})

    if product_list:
        input_list = product_list
    elif product_grid:
        input_list = product_grid

    if not input_list:
        return

    list_of_products = input_list.children
    for product in list_of_products:

        try:
            json_data = json.loads(product['data-params'])
        except KeyError:
            continue

        name = json_data.get('shortName')
        price = json_data.get('price')

        link_img = product.find("img")['src']
        img = requests.get(link_img)

        product = Product(
            name=name,
            price=price,
            category=category,
            sub_category=sub_name
        )
        product.save()

        if img.status_code == 200:
            fd = BytesIO()
            fd.write(img.content)
            file_name = link_img.split("/")[-1]
            product.image.save(file_name, files.File(fd))


def parse_products(category, sub):
    page = get_with_timeout(sub['href']).text
    sub_name = sub.text.strip()
    soup = BeautifulSoup(page, "html.parser")

    sub_cat = soup.find("div",
                        {"class": "CatalogCategoryCardWrapper"})

    if sub_cat:
        links = soup.find_all("a", {'class': "CatalogCategoryCard__link"})
        for link in links:
            parse_products(category, link)
    else:
        save_product(soup, category, sub_name)
        pages = soup.find_all("a", {"class": "PaginationWidget__page"})
        for p in pages:
            print(p["href"])
            soup = BeautifulSoup(get_with_timeout(p['href']).text,
                                 "html.parser")
            save_product(soup, category, sub_name)


def parse_category(link):
    category = Category.objects.get_or_create(
        name=link.find("span").text.strip()
    )
    sub_category_page = get_with_timeout(link['href']).text
    soup = BeautifulSoup(sub_category_page, "html.parser")
    sub_categorys = soup.find_all("a", {'class': "CatalogCategoryCard__link"})
    for sub in sub_categorys[0:1]:
        parse_products(category, sub)
    exit(0)

#
class Command(BaseCommand):
    def handle(self, **options):
        request_url = "https://www.citilink.ru/catalog/"
        catalog = get_with_timeout(request_url)

        soup = BeautifulSoup(catalog.text, "html.parser")

        links_to_subcategorys = soup.find_all("a", {
            "class": "CatalogLayout__link_level-1"})

        joined_proc = []
        for link in links_to_subcategorys:
            proc = multiprocessing.Process(
                target=parse_category, args=(link,)
            )
            joined_proc.append(proc)
            proc.start()

        for proc in joined_proc:
            proc.join()
