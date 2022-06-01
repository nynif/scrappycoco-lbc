import os
from datetime import date
from os.path import exists
from bs4 import BeautifulSoup
import pandas as pd
import re

BASE_URL_LBC = "https://www.leboncoin.fr"

############## Modifier les valeurs ici
MY_URL="https://www.leboncoin.fr/recherche?category=9&locations=69009__45.77616427381966_4.797311205072112_7921&owner_type=private&real_estate_type=2&immo_sell_type=old&price=10000-max"
NAME="lyon_9"


path_html_page      = "data/" + NAME + "/page"
path_html_detail    = "data/" + NAME + "/detail"
path_file_allData        = "data/" + NAME + "/result.csv"

#Init des dossiers
os.system(""" 
mkdir data
mkdir data/"""+NAME+"""
mkdir data/"""+NAME+"""/page
mkdir data/"""+NAME+"""/detail
""")

# Télécharger les pages principales contenant les annonces et les stocker dans data/ville/html
pageExist = True
page=1
if True:
    while pageExist:
        CURL_URL=MY_URL+"&page="+str(page)
        OUTPUT_FILE = path_html_page+"/page"+str(page)+".html"

        os.system("""
        curl '""" + CURL_URL + """' \
            -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36' \
            -H 'accept-language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7' \
            --compressed > """+OUTPUT_FILE+"""
        """)
        page+=1
        # Utiliser bs4 pour vérifier si la page contient des résultats ou non
        soup = BeautifulSoup(open(OUTPUT_FILE, encoding="utf8"), "html.parser")
        soup_results = soup.find("p", string=re.compile("Désolé, nous n'avons pas ça sous la main"))

        if soup_results is not None:
            # Supprimer la dernière page qui est vide de résultat
            os.system("""
               rm """+OUTPUT_FILE+"""
                """)
            pageExist = False

## À ce moment du code le dossier path_html_page contient toutes pages html des listes d'objets qui nous intéresse

list_detail_url = []
nbrObj = 0

files = os.listdir(path_html_page)

for filename in files:
    if not filename.startswith('.'):
        soup = BeautifulSoup(open(path_html_page+'/'+filename, encoding="utf8"), "html.parser")
        results = soup.find_all(attrs={"data-qa-id": "aditem_container"})
        for el in results:
            obj_link = el.get('href')
            list_detail_url.append(obj_link)
            nbrObj += 1

## list_detail_url contient la liste des urls à aller télécharger pour avoir le détail des objets
if True:
    for url in list_detail_url:
        obj_id = url.split('/')[-1].split('.')[0]

        CURL_URL=BASE_URL_LBC+url
        OUTPUT_FILE = path_html_detail+'/'+obj_id+".html"

        os.system("""
        curl '""" + CURL_URL + """' \
            -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36' \
            -H 'accept-language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7' \
            --compressed > """+OUTPUT_FILE+"""
        """)

## À ce moment du code le dossier path_html_detail contient toutes les pages html des objets qui nous intéresse
## Plus qu'à parser ->

data = []
files_detail = os.listdir(path_html_detail)
for filename in files_detail:
    if not filename.startswith('.'):
        path_url = path_html_detail+"/"+filename
        soup = BeautifulSoup(open(path_url, encoding="utf8"), "html.parser")

        descr_cont = soup.find(attrs={"data-qa-id": "adview_spotlight_description_container"})

        # LINK & ID
        link = soup.find('meta', attrs={"property": "og:url"})
        d_link = link['content'] if link else ''
        obj_id = d_link.split('/')[-1].split('.')[0]

        # PRIX
        results = descr_cont.find(attrs={"data-qa-id": "adview_price"}) if descr_cont else ''
        d_price = results.find('span').text if results else '0'
        d_price = d_price[:-2]

        # TAILLE
        d_size = descr_cont.find(text=re.compile(' m²')) if descr_cont else '0'

        # PRIX / M2
        d_price_size_1 = descr_cont.find(text=re.compile('€/m²')) if descr_cont else ''
        d_price_size_1 = d_price_size_1[:-5] if d_price_size_1  else '0'

        # ENERGIE
        ener = soup.find(attrs={"data-qa-id": "criteria_item_energy_rate"})
        nrj = ener.find("div", class_=re.compile('styles_active')) if ener else ''
        d_nrj = nrj.text if nrj else '0'

        d_date_add = date.today()
        d_date_remove = '' #np.NaN

        if obj_id:
            new_d = [obj_id, d_price_size_1, d_price, d_size, d_nrj, d_link, d_date_add, d_date_remove]
            data.append(new_d)

df_all = pd.DataFrame(data, columns=['id', 'pricebysize', 'price', 'size', 'energy', 'link', 'date_add', 'date_remove'])

if exists(path_file_allData):
    df_all.to_csv(path_file_allData, index=False, mode='a', header=False)
else:
    df_all.to_csv(path_file_allData, index=False)