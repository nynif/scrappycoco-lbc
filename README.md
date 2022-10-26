# Scrapping immobilier sur le bon coin

Ce programme est un programme de scraping de biens immobiliers sur le site leboncoin.fr

Dernier test le : 26/10/2022  
Status: OK

## Comment lancer le projet
### 1ere étape : Cloner le projet

    git clone

### 2ᵉ étape : Installer les dépendances 

    python3 -m venv env
    source env/bin/activate
    pip -r install requirements.txt

### 3ᵉ étape : Remplir les variables suivantes (dans l'entête de main.py)
- **MY_URL**  
Pour obtenir votre url de recherche rendez-vous sur le site leboncoin.fr et faites une recherche dans la catégorie IMMOBILIER/ VENTE IMMOBILIERES. Vous pouvez utiliser les filtres proposés par le site. Ensuite cliquez sur Rechercher. Copiez alors l'url qui sera du type

```MY_URL="https://www.leboncoin.fr/recherche?category=9&locations=69009__45.77616427381966_4.797311205072112_7921&owner_type=private&real_estate_type=2&immo_sell_type=old&price=10000-max"```

- **NAME**  
Choissisez le nom que vous voulez donner à cette recherche


### 4ᵉ étape : Lancer le programme  

```python3 main.py```

## Fonctionnement

L'algorithme prend en entrée une url de recherche du site leboncoin.fr et récupère les informations des objets en ligne  
Il ne fonctionne que pour les biens de la catégorie immobiliers (category=9). 

En sortie d'algorithme crée un dossier avec les pages html scrappées ainsi qu'un tableau csv (result.csv) contenant les informations récupérées.

## Fonctionnement du scraping 

- STEP 1 (curl)
  - On télécharge les pages principales que l'on place dans 
  - data/{NAME}/page/
- STEP 2 (py)
  - On scrap les ID des objets dans les pages principales
- STEP 3 (curl)
  - On télécharge toutes les pages "détails" des objets
  - data/{NAME}/detail/
- STEP 4 (py)
  - On scrap l'ensemble des pages details et on récupere les informations que l'on stock dans un tableau
  - data/{NAME}/resultat.csv


## REGLE DE SCRAPPING AU 26/10/2022
J'indique ici les règles de scrapping utilisées, si le site le leboncoin change sa mise en page le scrapping peux ne plus fonctionner il faudra donc modifier ces règles

### Sur les pages de résultats
Exemple : https://www.leboncoin.fr/recherche?category=9&locations=69009&page=2

#### Identifier une cellule objet dans la page de résultat
```soup.find_all(attrs={"data-qa-id": "aditem_container"})```

#### Identifier qu'il n'y a pas de résultat sur une page de résultat:
```soup.find("p", string=re.compile("Désolé, nous n'avons pas ça sous la main"))```


### Sur les pages details d'un objet
Exemple : https://www.leboncoin.fr/ventes_immobilieres/2164281681.htm

#### Identifier une cellule object dans la page de résultat
```descr_cont = soup.find(attrs={"data-qa-id": "adview_spotlight_description_container"})```

#### Identifier le prix
```descr_cont.find(attrs={"data-qa-id": "adview_price"})```

#### Identifier la taille
```descr_cont.find(text=re.compile(' m²'))```

#### Identifier le prix/ m2
```descr_cont.find(text=re.compile('€/m²'))```

#### Identifier la catégorie energetique
```ener = soup.find(attrs={"data-qa-id": "criteria_item_energy_rate"})```  
```ener.find("div", class_=re.compile('styles_active'))```


## TODO/ IDÉES
- Récupérer l'adresse postal precise du bien immobilier
- Mettre les variables à remplir ailleurs que dans le fichier main (dans confix.txt)
- Temporiser entre chaque requête pour éviter que l'adresse IP soit banni
- Utiliser un VPN automatique pour éviter que l'adresse IP soit banni
- Mettre des logs de progression pendant le scrapping
- Pour le moment cette version de l'algorithme n'a vocation à tourner qu'une fois, s'il tourne une deuxième fois, on va écrire à la suite du tableau, on aura donc des doublons. Il conviendrait de permettre d'identifier les biens déjà existants, ont-ils étaient modifiés, supprimés etc.