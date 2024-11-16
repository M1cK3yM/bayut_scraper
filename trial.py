import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()

chrome_options.add_experimental_option(
    "prefs",
    {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheet": 2,
        "profile.managed_default_content_settings.fonts": 2,
    },
)
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--load-extension=Adblock-Plus_v3.21.1.crx")

driver = webdriver.Chrome(options=chrome_options)

base_url = 'https://www.bayut.com/brokers/essam-afify-2335821.html'
page = 1  # Start from the first page
links = []

while True:
    # Generate the page-specific URL
    if page == 1:
        url = base_url
    else:
        url = f"{base_url}?page={page}"

    driver.get(url)

    # Get all elements with the class name that contains links
    lists = driver.find_elements(By.CLASS_NAME, 'fbc619bc')

    # Break the loop if no more listings are found on the page
    if not lists:
        break

    # Collect the links on the current page
    for list_element in lists:
        try:
            href_element = list_element.find_element(By.CLASS_NAME, "d40f2294")
            links.append(href_element.get_attribute("href"))
        except NoSuchElementException:
            continue

    page += 1

    print("page " + str(page) + " loaded")
data = []
# Print the collected links
for link in links:
    driver.get(link)
    try:
        title = driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[3]/div[1]/div/h1').text
        currency = driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[1]/div[1]/div[1]/div/span[1]').text
        price = int((driver.find_element(
            By.XPATH, './/*[@id="body-wrapper"]/main/div[2]/div[4]/div[1]/div[1]/div[1]/div/span[3]').text).replace(",", ""))
        area = int((driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[1]/div[3]/div[3]/span[2]/span/span').text).split(" ")[0].replace(",", ""))
        bedRooms = 0 if (driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[1]/div[3]/div[1]/span[2]/span').text) == "Studio" else int((driver.find_element(
                By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[1]/div[3]/div[1]/span[2]/span').text).split(" ")[0])
        bathRooms = int((driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[1]/div[3]/div[2]/span[2]/span').text).split(" ")[0])
        description = driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[3]/div[1]/div/div[1]/div[1]/div/div/div/span').text
        category = driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[3]/div[1]/div/div[2]/ul/li[1]/span[2]').text
        purpose = (driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[3]/div[1]/div/div[2]/ul/li[2]/span[2]').text).split(" ")[-1]
        l = (driver.find_element(
            By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[4]/div[1]/div[2]').text)
        location = {
            "building_name": l.split(",")[0],
            "address_line_2": l.split(",")[1],
            "address_line_1": l.split(",")[-2],
            "city": l.split(",")[-1]
        }
        ownerAgent = {
            "name": driver.find_element(By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[5]/div[1]/div/div[1]/div[1]/div[2]/span/a/h2').text,
            "state": "Available",
            "user_image": driver.find_element(By.XPATH, '//*[@id="body-wrapper"]/main/div[2]/div[5]/div[1]/div/div[1]/div[1]/div[1]/picture/img').get_attribute('src')
        }
        slug = link.split("/")[-1].split(".")[0]

        image_links = []
        amenities = []
        try:
            # Wait until the "View gallery" button is clickable
            view_gallery_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div[aria-label='View gallery']"))
            )
            view_gallery_button.click()

            view_gallery_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, '_940ca6cc'))
            )
            # Extract images from the gallery
            container = driver.find_element(
                By.CLASS_NAME, '_940ca6cc')
            images = container.find_elements(By.TAG_NAME, "img")
            image_links = [img.get_attribute('src') for img in images]

            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.a7132536.ceb74c58"))
            )
            close_button.click()

            features_header = driver.find_element(By.CLASS_NAME, "_461e7694")
            driver.execute_script(
                "arguments[0].scrollIntoView();", features_header)

            features_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "_6e45c68c"))
            )
            features_button.click()

            features = driver.find_element(
                By.CLASS_NAME, 'b52999d9').find_elements(
                By.CLASS_NAME, 'da8f482a')
            for feature in features:
                feature_title = feature.find_element(
                    By.CLASS_NAME, '_1c78af3b').text
                feature_lists = feature.find_element(
                    By.CLASS_NAME, '_117b341a'
                ).find_elements(By.CLASS_NAME, '_7181e5ac')

                amenitie = {
                    feature_title: [
                        feature_list.text for feature_list in feature_lists]
                }
                amenities.append(amenitie)
        except Exception as e:
            print(e)
        # Add data to the list
        data.append({
            "title": title,
            "currency": currency,
            "price": price,
            "rooms": bedRooms,
            "baths": bathRooms,
            "area": area,
            "description": description,
            "category": [{"name": category}],
            "purpose": purpose,
            "location": location,
            "photos": image_links,
            "amenities": amenities,
            "coverPhoto_url": image_links[0],
            "ownerAgent": ownerAgent,
            "slug": slug,
            "url": link
        })
        print({
            "title": title,
            "currency": currency,
            "price": price,
            "rooms": bedRooms,
            "baths": bathRooms,
            "area": area,
            "category": [{"name": category}],
            "purpose": purpose,
            "location": location,
            "coverPhoto_url": image_links[0],
            "ownerAgent": ownerAgent,
            "slug": slug,
            "url": link
        })
    except NoSuchElementException:
        continue

# Save data to JSON file
with open("property_data.json", "w") as file:
    json.dump(data, file, indent=4)
