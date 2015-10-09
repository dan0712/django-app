__author__ = 'cristian'
from django.views.generic import View
from django.http import HttpResponse
import json
from django.db import models

# Create your models here.

class Song(models.Model):
    artist = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    duration = models.IntegerField()
    popularity = models.IntegerField()


# Create your views here.
class SongView(View):

    def get(self, request, *args, **kwargs):
        artist = request.GET.get("artist", None)
        title = request.GET.get("title", None)
        sort_by = request.GET.get("sort_by", None)
        order = request.GET.get("order", None)

        if (order is not None) and (order not in ["asc", "desc"]):
            return HttpResponse('{"error": "Bad Request"}', content_type="application/json", status=400)

        if (sort_by is not None) and (order not in ["artist", "title", "popularity", "duration"]):
            return HttpResponse('{"error": "Bad Request"}', content_type="application/json", status=400)

        if order is None:
            order = "asc"

        if sort_by is None:
            sort_by = "id"

        query_set = Song.objects

        if title is not None:
            query_set = query_set.filter(title=title)

        if artist is not None:
            query_set = query_set.filter(artist=artist)

        objects = query_set.order_by(sort_by).limit(10)

        ret = []

        for song in objects.all():
            ret.append({"id": song.id, "title": song.title, "artist": song.artist})

        if order == "desc":
            ret.reverse()

        return HttpResponse(json.dumps(ret), content_type="application/json")