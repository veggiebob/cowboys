import time
from multiprocessing.pool import Pool

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from util import change_link, save_img

def scrape_image_profile(gallery_url: str, url: str):
    g = gallery_url
    options = ChromeOptions()
    options.headless = True
    img_driver = webdriver.Chrome(options=options)

    try:
        img_driver.get(url)
        img_element = img_driver.find_element(By.CSS_SELECTOR, '.imageWidget div img')
        if not img_element:
            print(f'warning: missed image! called {cowboy_link}')
            return None
        long_description = img_element.get_attribute('alt')
        short_description = img_driver.find_element(By.CSS_SELECTOR, '.more-holder h1').text
        filename = img_driver.find_element(By.CSS_SELECTOR, '.more-holder .name').text
        listed_items = img_driver.find_elements(By.CSS_SELECTOR, '.more-holder dl dd')
        image_size = listed_items[1].text
        keywords = img_driver.find_element(By.CSS_SELECTOR, '.more-holder dl .keywords-list').text.split('\n')
        src = img_element.get_attribute('src')
        return (g, src, filename, short_description, long_description, keywords, image_size)
    except Exception as e:
        print(f'had to skip this cowboy at {url} because {e}')
        return None

options = ChromeOptions()
options.headless = True
driver = webdriver.Chrome(options=options)

driver.get('https://www.roblangimages.com/gallery-collection/COWBOYS/C0000Gf_QH23ruF0')

elements = driver.find_elements(By.CSS_SELECTOR, '.info .name a')
galleries = [ a.get_attribute('href') for a in elements ]

cowboy_metadata = dict(
    gallery_link=[],
    src=[], # url for the image
    filename=[],
    short_description=[],
    description=[],
    tags=[], # pipe (|) separated
    image_size=[], # image size advertised
    size_scraped=[] # image size that was scraped
)

def add_cowboy(gallery_link: str,
               src: str,
               filename: str,
               short_description: str,
               description: str,
               tags: list[str],
               image_size: str='unk',
               size_scraped: str='unk'):
    if len(tags) > 1:
        tags = tags[:-1] # exclude "Only search this gallery"
    cowboy_metadata['gallery_link'].append(gallery_link)
    cowboy_metadata['src'].append(change_link(src))
    cowboy_metadata['filename'].append(filename)
    cowboy_metadata['short_description'].append(short_description)
    cowboy_metadata['description'].append(description)
    cowboy_metadata['tags'].append('|'.join(tags))
    cowboy_metadata['image_size'].append(image_size)
    cowboy_metadata['size_scraped'].append(size_scraped)

debug_cowboys = None
max_debug_cowboys = 5

pool = Pool()
results = []

for g in galleries:
    driver.get(g)
    next_page = True
    print(f'new gallery! {g}')
    page = 0
    while next_page:
        print(f'checking page {page}')
        try:
            es = driver.find_elements(By.CSS_SELECTOR, '.view_options a')
            view_options = { e.text: e for e in es }
            if 'All' in view_options:
                view_options['All'].click()
                time.sleep(1.0)
                next_page = False
            # else:
            #     print(f'unable to find "All" option in view_options. skipping {g}')
            #     print(f'options: {list(view_options.keys())}')
            img_es = driver.find_elements(By.CSS_SELECTOR, '.thumbnail a')
            cowboy_links = [i.get_attribute('href') for i in img_es]

            for cowboy_link in cowboy_links:
                results.append(pool.apply_async(scrape_image_profile, (g, cowboy_link)))

            if next_page:
                # .pagination a
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, '.pagination a.page_next')
                    next_button.click()
                    page += 1
                except:
                    next_page = False
        except:
            print(f'had to skip the gallery at {g}')
            next_page = False

print('main driver finished.')
print('waiting for all cowboy requests to finish...')
skipped_cowboys = 0
index = 0
for result in results:
    cowboy = result.get()
    if cowboy is None:
        skipped_cowboys += 1
    else:
        add_cowboy(*cowboy)

    index += 1
    if index % 20 == 0:
        print(f'\t{round(index/len(results)*100.0, 2)}% done')

print(f'skipped cowboys: {skipped_cowboys}')

print('finished scraping data! writing metadata...')
import pandas as pd
df = pd.DataFrame(cowboy_metadata)
df.to_csv('cowboy_metadata.csv')
print('wrote metadata!')
