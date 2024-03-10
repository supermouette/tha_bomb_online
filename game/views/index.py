from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


def index(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False
    context = {"user": user}
    return render(request, "game/index.html", context)


def faq(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False
    context = {"user": user}
    return render(request, "game/faq.html", context)


def blue_ratio(request):
    from game.models import Game

    red = Game.objects.filter(status=Game.RED_WIN).count()
    blue = Game.objects.filter(status=Game.BLUE_WIN).count()
    if red + blue == 0:
        red = blue = 1
    return HttpResponse("{:.2f}".format(blue / (red + blue)))


def skies_of_denmark(request):
    import datetime
    from game.models import Sky
    from random import randrange

    if request.user.is_authenticated:
        user = request.user
    else:
        user = False
    context = {"user": user}

    now = datetime.datetime.now()

    # delete days from previous month
    Sky.objects.filter(month__lt=now.month).exclude(year__gt=now.year).delete()

    today = Sky.objects.filter(day=now.day, month=now.month)
    if today.count() == 0:  # add object for today
        Sky(
            color=randrange(120, 200), day=now.day, month=now.month, year=now.year
        ).save()

    tomorrow = now + datetime.timedelta(days=1)

    if (
        Sky.objects.filter(day=tomorrow.day, month=tomorrow.month).count() == 0
    ):  # add object for tomorrow
        Sky(
            color=randrange(120, 200),
            day=tomorrow.day,
            month=tomorrow.month,
            year=tomorrow.year,
        ).save()

    # check for other days
    days = Sky.objects.order_by("-day")
    if days.count() != now.day + 1:
        days_nb = [d.day for d in days]
        for i in range(1, now.day):
            if i not in days_nb:
                Sky(
                    color=randrange(120, 200), day=i, month=now.month, year=now.year
                ).save()
        days = Sky.objects.order_by("-day")

    context = {
        "skies": days[1:],
        "tomorrow": days[0],
        "user": user,
    }

    return render(request, "game/skies_of_denmark.html", context)


def skies_of_japan(request):
    import os, shutil, requests
    from PIL import Image, ExifTags
    from math import nan

    img_path = settings.MEDIA_ROOT + "japan/"

    if request.method == "POST":
        raw_imgs = request.FILES.getlist("photo")
        for raw in raw_imgs:
            with open(img_path + str(raw), "wb+") as destination:
                for chunk in raw.chunks():
                    destination.write(chunk)

    paths = [p for p in os.listdir(img_path) if not str(p).endswith('_map.png')]
    imgs = []
    for p in paths:
        img = Image.open(img_path + os.sep + p)
        exif = {}
        if img._getexif():
            exif = {
                ExifTags.TAGS[k]: v
                for k, v in img._getexif().items()
                if k in ExifTags.TAGS
            }
        gps_raw = {}
        for key in exif["GPSInfo"].keys():
            decode = ExifTags.GPSTAGS.get(key, key)
            gps_raw[decode] = exif["GPSInfo"][key]
        print(exif)
        try:
            lat = sum([float(e) / 60**i for i, e in enumerate(gps_raw["GPSLatitude"])])
            long = sum([float(e) / 60**i for i, e in enumerate(gps_raw["GPSLongitude"])])
            alt = gps_raw["GPSAltitude"]
            maps = p.split(".")[0]+"_map.png"

            if request.method == "POST" and p in [str(s) for s in raw_imgs]:
                url_static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom=12&size=400x400&key={settings.MAPS_KEY}&markers={lat},{long}"
                res_static_map = requests.get(url_static_map, stream = True)
                with open(img_path+os.sep+maps,'wb') as f:
                    shutil.copyfileobj(res_static_map.raw, f)
                    
        except ZeroDivisionError:
            lat, long, alt, maps = nan, nan, None, None
        
        gps = {"lat": lat, "long": long, "alt": alt}
        imgs.append({"path": p, "datetime": exif.get("DateTime"), "gps": gps, "maps": maps})

    imgs.sort(key=lambda x: x["datetime"])

    return render(request, "japan/index.html", {"user": request.user, "imgs": imgs})
