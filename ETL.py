# %%
import pandas as pd # manipular
import os # path
import json # manipular la respuesta de la api
import requests # para conectar a la api
import re # limpiar datos regex

# %%
path = os.getcwd()
path_credenciales = os.path.join(path, 'Credentials', 'credentials.json')
with open(path_credenciales) as file:
    credenciales = json.load(file)['Credentials']
    client_id = credenciales['client_id']
    client_secret = credenciales['client_secret']
# %%
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret':client_secret
}
token_url = 'https://accounts.spotify.com/api/token'
response = requests.post(token_url, data=data)
if response.status_code == 200:
    access_token = response.json()['access_token']
    print("Token de acceso:", access_token)
else:
    print("Error al solicitar el token de acceso:", response.text)

# %%
# Cargar los csv de Spotify Charts
dfs = [
    pd.read_csv(os.path.join(path, 'Data',file)).assign(Date=re.findall(r'\d{4}-\d{2}-\d{2}', file)[0])
    for file in os.listdir(os.path.join(path, 'Data'))
]
spotify_charts_df = pd.concat(dfs, ignore_index=True)
# %%
track = spotify_charts_df['uri'][0].split(':')[-1]
url = f'https://api.spotify.com/v1/audio-features/{track}'
url_track_info = f'https://api.spotify.com/v1/tracks/{track}'
headers = {
    'Authorization': f'Bearer {access_token}'
}
# %%
# extract data from all tracks
def get_track_info(track):
    url = f'https://api.spotify.com/v1/audio-features/{track}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

unique_tracks = spotify_charts_df['uri'].apply(lambda x: x.split(':')[-1]).unique()
df_analisis = pd.DataFrame()
for track in unique_tracks:
    #create df with track info
    track_info = get_track_info(track)
    track_info = {k: [v] for k, v in track_info.items()}
    track_info_df = pd.DataFrame(track_info)
    df_analisis = pd.concat([df_analisis, track_info_df], ignore_index=True)
# %%
spotify_charts_df = pd.merge(
    spotify_charts_df, 
    df_analisis, 
    on='uri', 
    how='left')
# %%
