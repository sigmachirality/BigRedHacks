import requests
import face_app_routes

client_id = 'd1c6d4ce29344d8781fc4965d067f203'
client_secret = '739bfdda44c84fd882a54e6d994ea28f'

access_token = ""
refresh_token = ""

together = client_id + ':' + client_secret

"""
'Tunable' attributes for a song, as defined by Spotify, range 0..1
"""
tunable_attributes = [
    'danceability',
    'energy',
    'loudness',
    'mode',
    'tempo',
    'valence'
]

"""
Gets an access token from spotify based on our registered app
"""
def get_access_token():
    #r = requests.post('https://accounts.spotify.com/api/token', headers={'Authorization': 'Basic ' + 'ZDFjNmQ0Y2UyOTM0NGQ4NzgxZmM0OTY1ZDA2N2YyMDM6NzM5YmZkZGE0NGM4NGZkODgyYTU0ZTZkOTk0ZWEyOGYK'}, data={'grant_type': 'client_credentials'})
    r = requests.post('https://accounts.spotify.com/api/token', data={'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret})
    access_token = (r.json())["access_token"]
    headers_data = {'Authorization' : 'Bearer ' + access_token}
    return access_token, headers_data


"""
Asks user to sign into our app
"""
def sign_in():
    scopes = 'scope=streaming%20user-modify-playback-state%20playlist-modify-private%20user-library-read%20user-top-read'
    url = 'https://accounts.spotify.com/authorize?client_id=' + client_id +'&response_type=code&redirect_uri=http://0.0.0.0:5000' + '&' + scopes +'&show_dialog=true'
    res = requests.get(url)


"""
Gets an access and refresh token from Spotify based on our app and a consenting user
"""
def new_get_access_token():
    code = requests.get('http://0.0.0.0:5000/get_auth_code')
    print(code.text)
    token = requests.post('https://accounts.spotify.com/api/token', data={'grant_type': 'authorization_code', 'code': code.text, 'redirect_uri': 'http://0.0.0.0:5000', 'client_id': client_id, 'client_secret': client_secret})
    global access_token, refresh_token, headers_data
    token = token.json()
    access_token = token["access_token"]
    refresh_token = token["refresh_token"]
    headers_data = {'Authorization' : 'Bearer ' + access_token}
    return access_token, headers_data

"""
Gets the text version of a spotify track from its track id.
"""
def get_track(track_id):
    req = requests.get('https://api.spotify.com/v1/tracks/' + track_id, headers={'Authorization' : 'Bearer ' + access_token})
    return req.text


"""
Gets a list of avaliable Spotify genres
"""
def get_genres():
    req = requests.get('https://api.spotify.com/v1/recommendations/available-genre-seeds', headers={'Authorization' : 'Bearer ' + access_token})
    return req.text


"""
Gets recommendations of Spotify tracks based on 'tunable track attributes' (as defined by Spotify)
Returns an array of tracks.
"""
def get_tracks_by_attributes(seed_track_id, target_values):
    values_str = ''
    for key, value in target_values.items():
        values_str = values_str + 'target_' + str(key) + '=' + str(value) + '&'
    req = 'https://api.spotify.com/v1/recommendations?'
    req = req + 'seed_tracks=' + seed_track_id
    global headers_data
    req = requests.get(req, headers=(headers_data))
    req = req.json()
    tracks = req["tracks"]
    track_ids = []
    for track in tracks:
        track_ids.append(track["id"])
    return track_ids

"""
Finds a good seed track, based on the user's preferences and target values.
Returns a single track id
"""
def find_good_seed(target_values):
    top = get_top_tracks()
    return match_target(top, target_values)


"""
Gets a tracks 'tunable attributes' provided a list of attributes 
"""
def get_attributes(track_id, attributes):
    global headers_data
    req = requests.get('https://api.spotify.com/v1/audio-features/' + track_id, headers=headers_data)
    req = req.json()
    res = {}
    for attr in attributes:
        res[attr] = req[attr]
    return res



"""
Scans a list of track ids, calulating deviations from target values of tunable attributes
"""
def get_dev(tracks, target_values):
    out = {}
    for track_id in tracks:
        print('Calculating deviations for track: ' + track_id)
        values = get_attributes(track_id, list(target_values.keys()))
        deviations = []
        for attr, val in values.items():
            print(attr + ' target value is: ' + str(target_values[attr]))
            print(attr + ' actual value is: ' + str(val))
            dev = target_values[attr] - val
            deviations.append(dev)
        sum_dev = 0
        for dev in deviations:
            sum_dev = sum_dev = abs(dev)
        out[track_id] = sum_dev
    return out
        


"""
Scans a list of track ids, looking for the song that best matches target attributes
"""
def match_target(tracks, target_values):
    devs = get_dev(tracks, target_values)
    return min(devs, key=devs.get)


"""
Gets a users top tracks and stores them in a list
"""
def get_top_tracks():
    global headers_data
    req = requests.get('https://api.spotify.com/v1/me/top/tracks?limit=50', headers=headers_data)
    req = req.json()
    # print(req["items"][0]["id"])
    track_ids = []
    for track in req["items"]:
        track_ids.append(track["id"])
    # print(track_ids)
    return track_ids




tracks = [{"id": '06AKEBrKUckW0KREUWRnvT'}, {"id": "6rqhFgbbKwnb9MLmUQDhG6"}]
target_values = {'valence' : 0, 'energy': 0.8}
new_get_access_token()
print(get_tracks_by_attributes(find_good_seed(target_values), target_values))






    