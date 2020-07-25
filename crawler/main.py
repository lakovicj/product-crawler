from selenium import webdriver
import json
from selenium.webdriver.chrome.options import Options
import smtplib, ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def crawl(url, driver_path):
    # ovo je da se ne otvara prozor chroma
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(driver_path, options=options)

    driver.get(url)
    driver.implicitly_wait(5)
    loaded_products_WE = driver.find_elements_by_class_name("product-item")

    loaded_products = []
    for product in loaded_products_WE:
        product_name = product.find_element_by_class_name("product-item-name").text
        old_price_elem = product.find_element_by_class_name("old-price")
        new_price_elem = product.find_element_by_class_name("special-price")
        old_price = old_price_elem.find_element_by_class_name("price").text
        new_price = new_price_elem.find_element_by_class_name("price").text
        available_elem = product.find_element_by_class_name("algolia-in-stock")
        available = available_elem.find_element_by_tag_name("p").text
        href_elem = product.find_element_by_class_name("product-item-photo")
        href = href_elem.get_attribute("href")
        img_elem = product.find_element_by_class_name("result-thumbnail")
        img = img_elem.find_element_by_tag_name("img").get_attribute("src")
        p = {"name": product_name, "new-price": new_price, "old-price": old_price,
             "available": available, "href": href, "img": img}
        loaded_products.append(p)
    return loaded_products


def check_if_new(crawled_products, old_products_filepath):

    old_products = open_json(old_products_filepath)

    # ovo je samo kad se prvi put pokrene
    # i ako neko izbrise products iz liste u json fajlu
    if len(old_products["products"]) == 0:
        update_json(old_products_filepath, data=crawled_products)
        return crawled_products

    old_product_names = [x["name"] for x in old_products["products"]]
    output_products = []
    for product in crawled_products:
        if product["name"] not in old_product_names:
            output_products.append(product)

    if len(output_products) > 0:
        update_json(old_products_filepath, data=output_products)
        return output_products

    print("There is no new products!")
    return None


def open_json(file_path):
    with open(file_path) as json_file:
        saved_products = json.load(json_file)
    return saved_products


def update_json(file_path, data):
    json_data = {"products": data}
    with open(file_path, 'w') as outfile:
        json.dump(json_data, outfile)


def send_email(username, password, subscribers, products):

    plain_msg, html_msg = format_email_plain_and_html(products)

    message = MIMEMultipart("alternative")
    message["Subject"] = "New Products Available on iStyle"
    message["From"] = username
    part1 = MIMEText(plain_msg, "plain")
    part2 = MIMEText(html_msg, "html")
    message.attach(part1)
    message.attach(part2)

    port = 465  # For SSL
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(username, password)
        for subscriber in subscribers:
            message['To'] = subscriber
            server.sendmail(username, subscriber, message.as_string())

    print("emails sent!")

def format_email_plain_and_html(products):
    plain_msg = "GOOD NEWS! New unpacked products are on sale!!!\n"
    for product in products:
        plain_msg += "\n\n {} \nOld price: {}\nNew price: {}\nAvailable: {}".format(product['name'],
                                                    product['old-price'], product['new-price'], product['available'])

    html_msg = "<html><body>"
    html_msg += "<h1>GOOD NEWS! New unpacked products are on sale!!!</h1>"
    html_msg += "<br><br><hr>"
    for product in products:
        html_msg += "<a href=\"{}\">".format(product['href'])
        html_msg += "<img src=\"{}\" width=\"100\" height=\"100\">".format(product['img'])
        html_msg += "<h3>{}</h3></a><p>Old price: {}</p><p>New price: {}</p><p>Available: {}</p>".format(product['name'],
                                                product['old-price'],product['new-price'], product['available'])
        html_msg += "<hr>"

    html_msg += "</body></html>"

    return plain_msg, html_msg


if __name__ == '__main__':
    CONFIG_PATH = sys.argv[1]
    config = open_json(CONFIG_PATH)['config']
    URL = config['page-url']
    DRIVER_PATH = config['driver-path']
    PRODUCTS_FILE_PATH = config['products-file-path']
    SUBSCRIBERS = config['subscribers']
    SENDER_USERNAME = config['sender-email']
    SENDER_PASS = config['sender-pass']

    crawled = crawl(URL, DRIVER_PATH)
    crawled_products = check_if_new(crawled, PRODUCTS_FILE_PATH)

    if crawled_products is not None:
        send_email(SENDER_USERNAME, SENDER_PASS, SUBSCRIBERS, crawled_products)



