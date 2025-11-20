import argparse
import json
import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def main():
    parser = argparse.ArgumentParser(description='Scrape Amazon.')
    parser.add_argument('query', help='Keywords in search box.')
    parser.add_argument('--limit', type=int, default=5, help='Limit the number of items.')
    parser.add_argument('--enhance', action='store_true', help='Enhance search results with AI prompts.')
    args = vars(parser.parse_args())
    scrape_amazon(**args)


def scrape_amazon(query, limit=5, enhance=False):
    if enhance:
        query = 'laptops'
        # TODO: Make enhancements generic - i.e., not laptop-specific.

    driver = webdriver.Chrome()
    driver.get(f'https://www.amazon.com/s?k={query}')
    wait = WebDriverWait(driver, 10)
    div_resultlist = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 's-result-list')))
    divs_resultitem = div_resultlist.find_elements(By.CLASS_NAME, 's-result-item')

    products = list()
    for div_resultitem in divs_resultitem:
        if len(products) == limit:
            break

        driver.execute_script("arguments[0].scrollIntoView(true);", div_resultitem)
        product = dict()
        divs = div_resultitem.find_elements(By.TAG_NAME, 'div')
        for div in divs:
            data_cy = div.get_attribute('data-cy')
            if data_cy == 'title-recipe':
                # Title and URL.
                a_title = div.find_element(By.CLASS_NAME, 'a-link-normal')
                set_text_if_not_empty(product, a_title, 'title')
                product['url'] = a_title.get_attribute('href')
            elif data_cy == 'reviews-block':
                # Rating.
                span = div.find_element(By.TAG_NAME, 'span')
                set_text_if_not_empty(product, span, 'rating')
                # TODO: Number of ratings.
            elif data_cy == 'price-recipe':
                # Price.
                span = div.find_element(By.CLASS_NAME, 'a-price')
                set_text_if_not_empty(product, span, 'price')
            # TODO: Navigate and scrape inner-page description
            # TODO: Scrape reviews.

        if len(product.keys()) >= 4:
            products.append(product)

    if enhance:
        client = openai.OpenAI()

        # On individual items.
        for product in products:
            desc = 'Generate a description of this JSON amazon laptop listing:\n{}'.format(json.dumps(product))
            product['desc'] = get_api_response(client, desc)

        # Over all items.
        compare = 'Here is a list of descriptions of laptops in JSON format. Select the best one in the list for high-end gaming, and summarize why you think it is the best.\n{}'.format(json.dumps(products))
        print(get_api_response(client, compare))

    print(json.dumps(products, indent=4))


def set_text_if_not_empty(product, element, key):
    text = element.text
    if len(text) > 0:
        product[key] = text


def get_api_response(client: openai.OpenAI, prompt: str, model: str = 'gpt-5-mini'):
    response = client.responses.create(model=model,
                                       input=prompt)
    return response.output_text


if __name__ == '__main__':
    main()
