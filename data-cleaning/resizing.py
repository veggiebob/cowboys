from multiprocessing.pool import Pool
import subprocess
import os

DIRECTORY = 'data/stretched-data/images'
IMG_SIZE = 64
# setup
os.chdir('..')
os.makedirs(DIRECTORY, exist_ok=True)

# include the dot in new_ext
# ex. change_ext('file.jpg', '.png')
def change_ext(filename: str, new_ext: str) -> str:
    idx = filename.rfind('.')
    return filename[:idx] + new_ext

def stretch_file(filename: str):
    nfn = change_ext(filename, '.jpg')
    subprocess.run(
        f'ffmpeg -i data/original-data/images/{filename} -vf scale={IMG_SIZE}:{IMG_SIZE} \
{DIRECTORY}/{nfn}'.split(' '),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)

pool = Pool()
pool.map(stretch_file, os.listdir('data/original-data/images/'))

print('done!')