import requests
import pandas as pd
import time

def fetch_data(url, params=None):
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('dados')  # Using 'get' to avoid KeyError if 'dados' is not present

def fetch_all_pages(url, params=None):
    items = []
    params = params if params else {}
    params['pagina'] = 1
    params['itens'] = 100  # Adjust based on the API's maximum capacity

    while True:
        data = fetch_data(url, params)
        if not data:
            break
        items.extend(data)
        params['pagina'] += 1
        time.sleep(1)  # To avoid overloading the API servers

    return items

def add_year_to_data(data, year):
    for item in data:
        item['year'] = year
    return data

def save_data(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(f'data/{filename}.csv', index=False)
    print(f'Data saved in data/{filename}.csv')

def main():
    base_url = 'https://dadosabertos.camara.leg.br/api/v2/'
    categories = {
        'deputies': 'deputados',
        'propositions': 'proposicoes',
        'parties': 'partidos',
        'blocs': 'blocos',
        'votings': 'votacoes'
    }

    data_accumulated = {key: [] for key in categories}

    for year in range(2000, 2024):
        for category, endpoint in categories.items():
            print(f"Collecting {category} data for {year}...")
            full_url = base_url + endpoint
            params = {'ano': year} if category != 'parties' and category != 'blocs' else {}
            fetched_data = fetch_all_pages(full_url, params)
            dated_data = add_year_to_data(fetched_data, year)
            data_accumulated[category].extend(dated_data)

    for category, data in data_accumulated.items():
        save_data(data, f'{category}')

if __name__ == "__main__":
    main()
