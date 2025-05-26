from tabnanny import verbose
from django.db import models


class Track(models.Model):
    title = models.CharField()
    artists = models.CharField()
    track_id = models.CharField()
    album_or_playlist_id = models.CharField()
    is_album = models.CharField()
    
    def __str__(self):
        return self.title

class Head(models.Model):
    title = models.CharField()
    artists = models.CharField()
    head_id = models.CharField()
    is_album = models.CharField()

    def __str__(self):
        return self.title