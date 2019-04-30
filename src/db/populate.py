from src.db.objects import Base, Songs, Votes, Round, IPAddress


def populate(session, spotify_obj, username, source_playlist_id):
    playlist_switch = True
    offset=0
    limit=100
    while playlist_switch:
        playlist = spotify_obj.user_playlist_tracks(username,
                                                    source_playlist_id,
                                                    offset=offset,
                                                    limit=limit
                                                    )
        session.flush()
        session.commit()

        for song in playlist['items']:
            title = song['track']['name'][0:100]
            artist = song['track']['artists'][0]['name'][0:100]
            song_uri = song['track']['uri']
            duration = song['track']['duration_ms'] / 1000
            session.add(Songs(title, artist, song_uri, duration))

        if playlist['next'] is None:
            playlist_switch = False
        else:
            offset += limit

    return None

