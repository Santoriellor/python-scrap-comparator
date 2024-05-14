import random

from bs4 import BeautifulSoup
import lxml
import time
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

def fetch_html(url):
    # Maximum number of retry attempts
    max_retries = 3
    # number of scroll down
    scroll = 5
    # time between each scroll down (s)
    time_to_scroll = 1

    # Initialize html_content with None
    html_content = None

    retry_count = 0
    while retry_count < max_retries:
        try:
            # Specify the path to the ChromeDriver executable
            chrome_driver_path = "./chromedriver.exe"

            # Set Chrome options
            chrome_options = Options()
            chrome_options.add_argument(f'--webdriver.chrome.driver={chrome_driver_path}')

            # Initialize the Chrome driver with specified options
            driver = webdriver.Chrome(options=chrome_options)

            # Set maximum time for page to load
            driver.set_page_load_timeout(10)  # Timeout in seconds

            # Navigate to the website
            driver.get(url)

            # Wait for specific elements to appear
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.ID, "some_element"))
            # )

            # Scroll down the page
            # You can adjust the number of scrolls and sleep time as needed
            for _ in range(scroll):
                # Scroll down using JavaScript
                driver.execute_script("window.scrollBy(0, 1000);")
                # Wait for a short time to allow images to load
                time.sleep(time_to_scroll)

            # Get the page source (HTML content) after it has been dynamically loaded
            html_content = driver.page_source

        except TimeoutException:
            # Handle timeout exception
            print("Page load timed out or element not found")

        except Exception as e:
            # Handle other exceptions
            print("An error occurred:", e)

        finally:
            # Quit the WebDriver
            driver.quit()

        if html_content:
            # If the HTML content was successfully retrieved, break out of the retry loop
            break
        else:
            # Increment the retry count
            retry_count += 1
            # Calculate the exponential backoff delay
            delay = 2 ** retry_count + random.uniform(0, 1)
            print(f"Retry attempt {retry_count}. Waiting for {delay} seconds before retrying...")
            time.sleep(delay)

    # Parse the HTML content using BeautifulSoup if html_content is not None
    if html_content:
        soup = BeautifulSoup(html_content, "lxml")
        return soup
    else:
        # Handle the case where html_content is still None after all retries
        return None

def scrape_website(url, parser_func):
    soup = fetch_html(url)
    return parser_func(soup)

def scrape_multiple_websites(urls_and_parsers):
    with ThreadPoolExecutor(max_workers=len(urls_and_parsers)) as executor:
        results = list(executor.map(lambda x: scrape_website(x[0], x[1]), urls_and_parsers))
    return dict(zip([url for url, _ in urls_and_parsers], results))

def scrap_coop(soup):
    # Find all <a> tags with an 'id' attribute consisting of seven numbers
    links_with_seven_digit_ids = soup.find_all("a", id=lambda x: x and x.isdigit() and len(x) == 7)

    links_data = []
    # Print the links
    for link in links_with_seven_digit_ids:
        # Create a dictionary to store data for the current link
        link_data = {}

        # Check if the <img> tag was found before accessing its attributes
        img_tag_src = link.find("img")
        if img_tag_src:
            # Extract src attribute value
            image_src = img_tag_src['src'].strip()
        else:
            image_src = None  # Or set a default value or handle the absence of the image URL in another way

        # Store the picture URL in link_data
        link_data["image_src"] = image_src

        img_tag_srcset = link.find("img", srcset=True)
        if img_tag_srcset:
            # Extract srcset attribute value
            image_srcset = img_tag_srcset['srcset'].strip()
        else:
            image_srcset = None  # Or set a default value or handle the absence of the image URL in another way

        # Store the picture URL in link_data
        link_data["image_srcset"] = image_srcset

        # Extract product name
        product_name_tag = link.find("p", {"data-title-clamp": True})
        if product_name_tag:
            product_name = product_name_tag.text.strip()
        else:
            product_name = None

        # Store the product name in link_data
        link_data["product_name"] = product_name

       # Extract product price
        product_price_tag = link.find("p", class_="productTile__price-value-lead-price")
        if product_price_tag:
            product_price = product_price_tag.text.strip()
        else:
            product_price = None

        # Store the product price in link_data
        link_data["product_price"] = product_price

        # Store the link_data dictionary in links_data
        links_data.append(link_data)
    
    return links_data

def scrap_migros(soup):
    # Find all <article> tags
    articles = soup.find_all("article")

    articles_data = []
    # Print the links
    for article in articles:
        # Create a dictionary to store data for the current link
        article_data = {}

        # Check if the <img> tag was found before accessing its attributes
        img_tag_src = article.find("img")
        if img_tag_src:
            # Extract src attribute value
            image_src = img_tag_src['src'].strip()
        else:
            image_src = "src empty"  # Or set a default value or handle the absence of the image URL in another way

        # Store the picture URL in link_data
        article_data["image_src"] = image_src

        img_tag_srcset = article.find("img", srcset=True)
        if img_tag_srcset:
            # Extract srcset attribute value
            image_srcset = img_tag_srcset['srcset'].strip()
        else:
            image_srcset = "srcset empty"  # Or set a default value or handle the absence of the image URL in another way

        # Store the picture URL in link_data
        article_data["image_srcset"] = image_srcset

        # Extract product name
        product_name_tag = article.find("lsp-product-name")
        if product_name_tag:
            product_name = product_name_tag.text.strip()
        else:
            product_name = "name empty"

        # Store the product name in link_data
        article_data["product_name"] = product_name

       # Extract product price
        product_price_tag = article.find("lsp-product-price")
        if product_price_tag:
            product_price = product_price_tag.text.strip()
        else:
            product_price = "price empty"

        # Store the product price in link_data
        article_data["product_price"] = product_price

        # Store the link_data dictionary in links_data
        articles_data.append(article_data)
    
    return articles_data

def scrap_aldi(soup):
    # Find all <product-item> tags
    products = soup.find_all("product-item")

    products_data = []
    # Print the links
    for product in products:
        # Create a dictionary to store data for the current link
        product_data = {}

        # Check if the <img> tag was found before accessing its attributes
        img_tag_src = product.find("img")
        if img_tag_src:
            # Extract src attribute value
            image_src = img_tag_src['src'].strip()
        else:
            image_src = None  # Or set a default value or handle the absence of the image URL in another way

        # Store the picture URL in link_data
        product_data["image_src"] = image_src

        img_tag_srcset = product.find("img", srcset=True)
        if img_tag_srcset:
            # Extract srcset attribute value
            image_srcset = img_tag_srcset['srcset'].strip()
        else:
            image_srcset = None  # Or set a default value or handle the absence of the image URL in another way

        # Store the picture URL in link_data
        product_data["image_srcset"] = image_srcset

        # Extract product name
        product_name_tag = product.find("a", class_="product-item__name")
        if product_name_tag:
            product_name = product_name_tag.text.strip()
        else:
            product_name = None

        # Store the product name in link_data
        product_data["product_name"] = product_name

       # Extract product price
        product_price_tag = product.find("span", class_="money-price__amount")
        if product_price_tag:
            product_price = product_price_tag.text.strip()
        else:
            product_price = None

        # Store the product price in link_data
        product_data["product_price"] = product_price

        # Store the link_data dictionary in links_data
        products_data.append(product_data)
    
    return products_data

if __name__ == '__main__':
    pass
