import bs4 as bs
import pandas as pd
import urllib.request
import numpy as np
import json
import sys


def create_url_from_expansion(expansion, page=False):
    base_url = "https://www.cardmarket.com/en/Magic/Products/Singles/"
    if page:
        end_url = '?idRarity=0&site='
        return '{0}{1}{2}{3}'.format(base_url, expansion, end_url, page)
    else:
        end_url = "?idRarity=0&perSite=20"
        return '{0}{1}{2}'.format(base_url, expansion, end_url)


def get_data_for_expansion(expansion):
    source = urllib.request.urlopen(create_url_from_expansion(expansion)).read()
    child_soup = bs.BeautifulSoup(source, 'lxml')

    n_pages = int(
        np.ceil(int(child_soup.find_all('div', {"class": "col-auto d-none d-md-block"})[0].text.split(' ')[0]) / 20))

    urls = [create_url_from_expansion(expansion, page=page) for page in range(n_pages)]

    all_links = []
    for url in urls:
        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source, 'lxml')
        links_of_page = []
        for link in soup.find_all('a', href=True):
            if expansion + '/' in link['href']:
                links_of_page.append("https://www.cardmarket.com/" + link['href'])
        all_links.extend(links_of_page)

    df = pd.DataFrame()

    for link in all_links:
        source = urllib.request.urlopen(link).read()
        soup = bs.BeautifulSoup(source, 'lxml')

        first_chart_obj = str(soup.find_all('script', {'class': 'chart-init-script'})[0])
        readable_json_string = first_chart_obj[first_chart_obj.find('{'):-1].split('backgroundColor')[0][:-2] + "}]}}"

        temp = pd.DataFrame()
        temp['dates'] = json.loads(readable_json_string)['data']['labels']
        temp['prices'] = json.loads(readable_json_string)['data']['datasets'][0]['data']
        temp['card'] = pd.Series([link.split('/')[-1] for i in range(temp.shape[0])])
        print(temp)
        df = pd.concat([df, temp])

    return df


if __name__ == "__main__":
    expansion = str(sys.argv[1])
    nom_db = expansion + ".csv"
    print("start scraping")
    print(expansion)
    db = get_data_for_expansion(expansion)
    print("stop scraping")
    db.to_csv(nom_db, index=False)
