import requests
import pandas as pd
import time
import xml.etree.ElementTree as ET

def fetch_data(url, params=None, max_retries=5, timeout=20):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for URL: {url}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data: {e}, URL: {url}")
            print(f"Response content: {response.content}")  # Debug: print the response content
            return None
    print(f"Max retries exceeded for URL: {url}. Skipping this request.")
    return None

def parse_xml(content):
    try:
        root = ET.fromstring(content)
        return root
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        return None

def fetch_all_propositions(year, tipo):
    url = 'https://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoesVotadasEmPlenario'
    params = {
        'ano': year,
        'tipo': tipo
    }
    print(f"Fetching propositions for year: {year}, type: {tipo}, URL: {url}, params: {params}")  # Debug
    content = fetch_data(url, params)
    if content:
        root = parse_xml(content)
        if root:
            return [proposicao for proposicao in root.findall('.//proposicao')]
    return []

def fetch_votes(proposition_id, tipo, numero, ano):
    url = 'https://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ObterVotacaoProposicao'
    params = {
        'idProposicao': proposition_id,
        'tipo': tipo,
        'numero': numero,
        'ano': ano
    }
    print(f"Fetching votes with params: {params}")  # Debug
    content = fetch_data(url, params)
    if content:
        root = parse_xml(content)
        if root:
            return [votacao for votacao in root.findall('.//votacao')]
    return []

def main():
    try:
        all_propositions = []
        all_votes = []

        tipos = ['PL', 'PEC', 'MPV', 'PDC', 'PLP']

        for year in range(2000, 2024):
            print(f"Collecting propositions data for {year}...")
            for tipo in tipos:
                print(f"Collecting {tipo} propositions for {year}...")
                propositions = fetch_all_propositions(year, tipo)

                for proposition in propositions:
                    proposition_id = proposition.find('codProposicao').text
                    numero = proposition.find('nomeProposicao').text.split()[1].split('/')[0]
                    print(f"Collecting votes for proposition ID: {proposition_id}, tipo: {tipo}, numero: {numero}, ano: {year}")
                    votes = fetch_votes(proposition_id, tipo, numero, year)
                    if votes:
                        all_propositions.append(proposition)
                        for vote in votes:
                            vote.attrib['proposition_id'] = proposition_id
                            all_votes.append(vote)
                        print(f"Collected votes for proposition ID: {proposition_id}")
                    else:
                        print(f"No votes found for proposition ID: {proposition_id}")

            # Save propositions and votes to CSV
            if all_propositions:
                df_propositions = pd.DataFrame([{child.tag: child.text for child in prop} for prop in all_propositions])
                df_propositions.to_csv(f'data/propositions_{year}.csv', index=False)
                print(f"All propositions data for {year} saved in data/propositions_{year}.csv")

        if all_votes:
            df_votes = pd.DataFrame([vote.attrib for vote in all_votes])
            df_votes.to_csv(f'data/all_votes.csv', index=False)
            print("All votes data saved in data/all_votes.csv")
        else:
            print("No votes data to save.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
