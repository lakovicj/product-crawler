# product-crawler
Crawling iStyle for new products.

main.py - script doing the job

config.json - configuration file

    page-url: url being crawled (only works with /otvoreni-proizvodi.html for now)
    
    dirver-path: path to chome driver
    
    products-file-path: path to products.json
    
    sender-email & sender-pass: sender email credentials
    
    subscribers: list of subscribed emails
    
products.json - crawled products

requirements.txt - requirements for heroku
