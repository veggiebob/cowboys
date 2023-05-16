import re
import requests

# goal: widthx660
# which means fit=x660


fit_match = re.compile(r'.*/(fit=[^/]*)/')
def change_link(url: str) -> str:
    ms = fit_match.match(url)
    gs = ms.groups()
    if len(gs) > 1:
        print(f'WARNING: multiple matches on url! \n\turl: {url}\n\tgroups: {gs}')
    if len(gs) == 0:
        print(f'WARNING: no matches! \n\turl: {url}')
        return url

    return url.replace(ms.groups()[0], 'fit=x660')

def save_img(url: str, filepath: str):
    try:
        img_data = requests.get(url).content
        with open(filepath, 'wb') as handler:
            handler.write(img_data)
    except:
        print(f'error occurred with url {url}')

if __name__ == '__main__':
    ex = 'https://www.roblangimages.com/img-get2/I00004eukieUbiHo/fit=188x188/fill=/g=G00007IpBModRaSo/I00004eukieUbiHo.jpg'
    print(f'original: {ex}')
    print(f'larger: {change_link(ex)}')
    print('saving image...')
    save_img(ex, '../test/ex-og-size.jpg')
    save_img(change_link(ex), '../test/ex-big-size.jpg')