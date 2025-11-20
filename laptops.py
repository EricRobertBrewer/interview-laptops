import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def main():
    driver = webdriver.Chrome()
    driver.get('https://www.amazon.com/s?k=laptops')
    wait = WebDriverWait(driver, 10)
    div_resultlist = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 's-result-list')))
    divs_resultitem = div_resultlist.find_elements(By.CLASS_NAME, 's-result-item')

    products = list()
    for div_resultitem in divs_resultitem:
        if len(products) == 5:
            break

        driver.execute_script("arguments[0].scrollIntoView(true);", div_resultitem)
        product = dict()
        divs = div_resultitem.find_elements(By.TAG_NAME, 'div')
        for div in divs:
            data_cy = div.get_attribute('data-cy')
            if data_cy == 'title-recipe':
                # Title and URL.
                a_title = div.find_element(By.TAG_NAME, 'a')
                set_text_if_not_empty(product, a_title, 'title')
                product['url'] = a_title.get_attribute('href')
            elif data_cy == 'reviews-block':
                # Rating.
                span = div.find_element(By.TAG_NAME, 'span')
                set_text_if_not_empty(product, span, 'rating')
            elif data_cy == 'price-recipe':
                # Price.
                span = div.find_element(By.CLASS_NAME, 'a-price')
                set_text_if_not_empty(product, span, 'price')

        if len(product.keys()) >= 4:
            products.append(product)

    print(json.dumps(products, indent=4))


def set_text_if_not_empty(product, element, key):
    text = element.text
    if len(text) > 0:
        product[key] = text


if __name__ == '__main__':
    main()
