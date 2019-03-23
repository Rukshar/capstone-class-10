from ..db.objects import Base, Songs, Votes, Round, IPAddress
from tinytag import TinyTag
import os
import re


def populate(session, music_folder, accepted_file_extensions=['.mp3', '.m4a']):
    rename_songs(music_folder, accepted_file_extensions)

    songs = os.listdir(music_folder)
    songs_list = []
    for song in songs:
        if song[-4:] in accepted_file_extensions:
            song_path = os.path.join(music_folder, song)

            # TinyTag doesn't play nicely with WindowsPath
            tag = TinyTag.get(song_path)
            songs_list.append((tag.title, tag.artist, song, float(tag.duration)))

    for (song, artist, filename, duration) in songs_list:
        session.add(Songs(song, artist, filename, duration))

    session.flush()
    session.commit()

    return None


def rename_songs(music_folder, accepted_file_extensions=['.mp3', '.m4a']):
    """
    Lower filenames and add underscores. Clean other special characters from filenames
    :param music_folder: path to music folder
    :param accepted_file_extensions: which file extensions are allowed
    :return: None
    """

    songs = os.listdir(music_folder)
    for song in songs:
        if song[-4:] in accepted_file_extensions:
            new_song_name = song.lower().replace(' ', '_')

            #remove special characters
            new_song_name = re.sub('[^A-Za-z0-9\-\_\.]+', '', new_song_name)
            old_song = os.path.join(music_folder, song)
            new_song = os.path.join(music_folder, new_song_name)
            os.rename(old_song, new_song)
