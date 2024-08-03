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
    while True:
        data = fetch_data(votes_url)
        if not data:
            break
        items.extend(data)
        time.sleep(2)  # Sleep to avoid overloading the server
    for vote in votes:
        vote['voting_id'] = voting_id

    return votes

def main():
    base_url = 'https://dadosabertos.camara.leg.br/api/v2/'
    all_votings = []
    all_votes = []

    for year in range(2000, 2000):  # From 2000 to 2024
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        print(f"Collecting voting data for {year}...")
        votings_url = base_url + 'votacoes'
        votings_params = {'dataInicio': start_date, 'dataFim': end_date}
        votings = fetch_all_pages(votings_url, votings_params)
        
        for voting in votings:
            voting['year'] = year  # Add year to each voting
            all_votings.append(voting)
            print(f"Collecting votes for voting ID: {voting['id']}")
            votes = fetch_votes(voting['id'])
            all_votes.extend(votes)

    # Save all votings and votes to CSV
    if all_votings:
        df_votings = pd.DataFrame(all_votings)
        df_votings.to_csv('data/votings' + year + '.csv', index=False)
        print("All voting data saved in data/all_votings.csv")

    if all_votes:
        df_votes = pd.DataFrame(all_votes)
        df_votes.to_csv('data/votes' + year + '.csv', index=False)
        print("All votes data saved in data/all_votes.csv")

if __name__ == "__main__":
    main()
