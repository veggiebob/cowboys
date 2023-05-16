import pandas as pd
from util import save_img
from multiprocessing import Pool
import os

cowboy_metadata = pd.read_csv('cowboy_metadata.csv')
already_saved = set(os.listdir('images/'))

srcs = cowboy_metadata['src']
names = cowboy_metadata['filename']

print('spawning processes...')
pool = Pool()
results = []
index = 0
for img, name in zip(srcs, names):
    # if name in already_saved:
    #     continue
    results.append(pool.apply_async(save_img, (img, f'images-out/{index}-{name}')))
    index += 1

print('waiting for processes to end...')
index = 0
for p in results:
    if index % 20 == 0:
        print(f'{round(index / len(results) * 100.0, 2)}% done')
    index += 1
    p.wait()

print('all done!')