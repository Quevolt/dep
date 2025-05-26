from ast import List
from django.shortcuts import render
from .models import Track, Head
from dotenv import load_dotenv
import yandex_music
import pprint
import time
import os
import re

load_dotenv()
TOKEN = os.getenv('yandex_token')
yra = yandex_music.Client(TOKEN).init()
os.makedirs(r"DjangoApp\static\tracks\covers", exist_ok=True)
os.makedirs(r"DjangoApp\static\heads", exist_ok=True)
def downloading(x, is_album):
    if is_album:
        path = rf"DjangoApp\static\heads\{x.id}.jpg"
        if not os.path.isfile(path):
            x.download_cover(path, size='200x200')
        return True
    else:
        path = rf"DjangoApp\static\heads\{x.kind}.jpg"
        if not os.path.isfile(path):
            if hasattr(x, "cover"):
                x.cover.download(path, size='200x200')
                return True
            else:
                x.download_og_image(path, size='200x200')
                return True
        return True
    return False
        
def get_artists(x):
    if hasattr(x, "artists"):
        return ' - ' + ', '.join(artist.name for artist in x.artists)
    elif hasattr(x, "owner"):
        return ' - ' + x.owner.name
    return None

def waiting():
    track1 = list(Track.objects.all().order_by('-id'))[0]
    track2 = list(Track.objects.all().order_by('-id'))[-1]
    while (not os.path.isfile(rf'DjangoApp\static\tracks\covers\{track1.track_id}.jpg') and not os.path.isfile(rf'DjangoApp\static\tracks\covers\{track2.track_id}.jpg')):
        pass
    print('все ЗАГРУЖЕНО')
    return True


def index(request):
    tracks = Track.objects.all()
    head = Head.objects.all()
    if request.method == 'POST':
        for t in tracks:
            t.delete()
        for h in head:
            h.delete()
        res = request._post.dict()["idf"]
        
        if res[:30:] == "https://music.yandex.ru/album/":
            id = re.search(r'album/\d+\d?', res).group()[6::]
            album = yra.albums_with_tracks(id)
            downloading(album, True)
            artists = get_artists(album)
            Head.objects.create(title=album.title, artists=artists[3::], head_id=album.id, is_album="1")
            for i in album.volumes:
                for volume in i:
                    artists = get_artists(volume)
                    Track.objects.create(title=volume.title, artists=artists, track_id=volume.id, album_or_playlist_id=id, is_album="1")
            
                
        elif (res[:30:] == "https://music.yandex.ru/users/") and "playlists" in res:
            id = re.search(r'playlists/\d+\d?', res).group()[10::]
            user_id = re.search(r'users/\S+/playlists', res).group()[6:-10:]
            playlist = yra.users_playlists(kind=id, user_id=user_id)
            downloading(playlist, False)
            artists = get_artists(playlist)
            Head.objects.create(title=playlist.title, artists=artists[3::], head_id=playlist.kind, is_album="0")
            for i in playlist.tracks:
                path = rf"DjangoApp\static\tracks\covers\{i.track.id}.jpg"
                if not os.path.isfile(path):
                    i.track.download_cover(path, size='50x50')
                artists = get_artists(i.track)
                Track.objects.create(title=i.track.title, artists=artists, track_id=i.track_id, album_or_playlist_id=id, is_album="0")
            а = waiting()
        return render(request, 'DjangoApp/empty.html')
    tracks_html = []
    n = 0
    try:
        head_html = head[0]
    except Exception as e:
        print("get запрос для получения csrf ", e)
        head_html = ""
    for track in tracks:
        n += 1
        if track.is_album == "1":
            tmp = f"{{\"title\": \"<div class='qe'><div class='playlist_poster' id='number'>{n}</div>    <div class='diva'><div class='am'>{track.title}</div> <p style='line-height: 1.5;'>{track.artists[3::]}</p></div></div>\", \"file\": \"static/tracks/{track.track_id}.mp3\", \"poster\": \"static/heads/{track.album_or_playlist_id}.jpg\", \"id\": \"{track.track_id}\"}}, "
        else:
            tmp = f"{{\"title\": \"<div class='qe'><img src='/static/tracks/covers/{track.track_id}.jpg' class='playlist_poster'>    <div class='diva'><div class='am'>{track.title}</div> <p style='line-height: 1.5;'>{track.artists[3::]}</p></div></diva>\", \"file\": \"static/tracks/{track.track_id}.mp3\", \"poster\": \"static/tracks/covers/{track.track_id}.jpg\", \"id\": \"{track.track_id}\"}}, "
        tracks_html.append(tmp)
    return render(request, 'DjangoApp/index.html', {"tracks": tracks_html, "head": head_html})

def main(request):
    if request.method == 'POST':
        id = request._post.dict()["id"]
        track = yra.tracks(id)[0]
        codec, bik = track.get_download_info()[0]["codec"], track.get_download_info()[0]["bitrate_in_kbps"]
        track.download(rf"DjangoApp\static\tracks\{id}.mp3", codec=codec, bitrate_in_kbps=bik)
        while not os.path.isfile(rf'DjangoApp\static\tracks\{id}.mp3'):
            time.sleep(0.1)
        return render(request, 'DjangoApp/empty.html')