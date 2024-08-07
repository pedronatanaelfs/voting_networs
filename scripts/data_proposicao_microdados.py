import basedosdados as bd

# Para carregar o dado direto no pandas
df = bd.read_table(dataset_id='br_camara_dados_abertos',
                   table_id='proposicao_microdados',
                   billing_project_id="voting-networks")

# Salvar o DataFrame em um arquivo CSV
df.to_csv('data/proposicao_microdados.csv', index=False)