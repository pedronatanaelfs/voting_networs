import requests
import pandas as pd
import time

def fetch_data(url, params=None):
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}, URL: {response.url}")
        return []
    return response.json().get('dados', [])  # Safe access to 'dados'

def fetch_all_pages(url, params=None):
    items = []
    params = params if params else {}
    params['pagina'] = 1
    params['itens'] = 100

    while True:
        data = fetch_data(url, params)
        if not data:
            break
        items.extend(data)
        params['pagina'] += 1
        time.sleep(1)
        if len(data) < params['itens']:
            break

    return items

def main():
    base_url = 'https://dadosabertos.camara.leg.br/api/v2/'

    # Collecting deputies data
    print("Collecting deputies data...")
    deputies_url = base_url + 'deputados'
    deputies = fetch_all_pages(deputies_url)
    if deputies:
        df_deputies = pd.DataFrame(deputies)
        df_deputies.to_csv('data/deputies.csv', index=False)
        print("Deputies data saved in data/deputies.csv")
    else:
        print("No deputies data to save.")

if __name__ == "__main__":
    main()
