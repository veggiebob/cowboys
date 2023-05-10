import time

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from util import change_link, save_img

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

for g in galleries:
    driver.get(g)
    try:
        print('got a new gallery...')
        es = driver.find_elements(By.CSS_SELECTOR, '.view_options a')
        view_options = { e.text: e for e in es }
        if 'All' in view_options:
            view_options['All'].click()
            time.sleep(2.0)
        else:
            print(f'unable to find "All" option in view_options. skipping {g}')
            print(f'options: {list(view_options.keys())}')
        img_es = driver.find_elements(By.CSS_SELECTOR, '.thumbnail a')
        cowboy_links = [i.get_attribute('href') for i in img_es]
        for cowboy_link in cowboy_links:
            try:
                driver.get(cowboy_link)
                img_element = driver.find_element(By.CSS_SELECTOR, '.imageWidget div img')
                if not img_element:
                    print(f'warning: missed image! called {cowboy_link}')
                    continue
                long_description = img_element.get_attribute('alt')
                short_description = driver.find_element(By.CSS_SELECTOR, '.more-holder h1').text
                filename = driver.find_element(By.CSS_SELECTOR, '.more-holder .name').text
                listed_items = driver.find_elements(By.CSS_SELECTOR, '.more-holder dl dd')
                image_size = listed_items[1].text
                keywords = driver.find_element(By.CSS_SELECTOR, '.more-holder dl .keywords-list').text.split('\n')
                src = img_element.get_attribute('src')
                add_cowboy(g, src, filename, short_description, long_description, keywords, image_size)
                if debug_cowboys is not None:
                    debug_cowboys += 1
                    if debug_cowboys > max_debug_cowboys:
                        break
            except:
                print(f'had to skip this cowboy at {cowboy_link}')
        if debug_cowboys is not None and debug_cowboys > max_debug_cowboys:
            break
    except:
        print(f'had to skip the gallery at {g}')

print('finished scraping data! writing metadata...')
import pandas as pd
df = pd.DataFrame(cowboy_metadata)
df.to_csv('cowboy_metadata.csv')
print('wrote metadata!')
print('saving images...')
index = 0
srcs = cowboy_metadata['src']
names = cowboy_metadata['filename']
for img, name in zip(srcs, names):
    if index % 20 == 0:
        print(f'{round(index / len(srcs), 2)}% done')
    index += 1

    save_img(img, f'images/{name}')

print('finished saving full size images!')
print('all done!')