import requests
import pandas as pd
import time

def fetch_data(url, params=None, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise an HTTPError on bad status
            return response.json().get('dados', [])  # Safe access to 'dados'
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for URL: {url}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data: {e}, URL: {url}")
            return []
    print(f"Max retries exceeded for URL: {url}. Skipping this request.")
    return []

def fetch_all_pages(url, params=None):
    items = []
    params = params if params else {}
    params['pagina'] = 1
    params['itens'] = 50  # Number of items per page

    while True:
        data = fetch_data(url, params)
        if not data:
            break
        items.extend(data)
        params['pagina'] += 1
        time.sleep(2)  # Sleep to avoid overloading the server
        if len(data) < params['itens']:
            break

    return items

def fetch_votes(voting_id):
    votes_url = f"https://dadosabertos.camara.leg.br/api/v2/votacoes/{voting_id}/votos"
    items = []
    votes = items
    data = fetch_data(votes_url)
    if data:
        items.extend(data)
        time.sleep(2)  # Sleep to avoid overloading the server
        for vote in votes:
            vote['voting_id'] = voting_id
        return votes
    else:
        print(f"Skipped fetching votes for voting ID: {voting_id} due to timeout.")
        return []

def main():
    base_url = 'https://dadosabertos.camara.leg.br/api/v2/'
    all_votings = []
    all_votes = []
    print('Código Iniciado...')

    for year in range(2000, 2001):  # From 2000 to 2023
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        print(f"Collecting voting data for {year}...")
        votings_url = base_url + 'votacoes'
        votings_params = {'dataInicio': start_date, 'dataFim': end_date}
        votings = fetch_all_pages(votings_url, votings_params)
        
        if votings:
            for voting in votings:
                voting['year'] = year  # Add year to each voting
                all_votings.append(voting)
                print(f"Collecting votes for voting ID: {voting['id']}")
                votes = fetch_votes(voting['id'])
                if votes:
                    all_votes.extend(votes)
                    print(f"Collected {len(votes)} votes for voting ID: {voting['id']}")
        else:
            print(f"Skipped collecting votings for {year} due to timeout.")

        # Save all votings and votes to CSV for the current year
        if votings:
            df_votings = pd.DataFrame(votings)
            df_votings.to_csv(f'data/votings_{year}.csv', index=False)
            print(f"All voting data for {year} saved in data/votings_{year}.csv")
  
