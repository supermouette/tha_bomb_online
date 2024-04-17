from django.shortcuts import render, redirect
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
        if not request.user.is_superuser:
            return HttpResponse(status=401)
        raw_imgs = request.FILES.getlist("photo")
        for raw in raw_imgs:
            with open(img_path + str(raw), "wb+") as destination:
                for chunk in raw.chunks():
                    destination.write(chunk)

    paths = [
        p
        for p in os.listdir(img_path)
        if not str(p).endswith("_map.png")
        and not str(p).endswith("_small.webp")
        and not str(p).endswith("_map_small.png")
    ]
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

        try:
            for key in exif["GPSInfo"].keys():
                decode = ExifTags.GPSTAGS.get(key, key)
                gps_raw[decode] = exif["GPSInfo"][key]
            lat = sum([float(e) / 60**i for i, e in enumerate(gps_raw["GPSLatitude"])])
            long = sum(
                [float(e) / 60**i for i, e in enumerate(gps_raw["GPSLongitude"])]
            )
            alt = gps_raw["GPSAltitude"]
            map = p.split(".")[0] + "_map.png"
            map_small = p.split(".")[0] + "_map_small.png"
            small = p.split(".")[0] + "_small.webp"
            if request.method == "POST" and p in [str(s) for s in raw_imgs]:
                for size, map_name, zoom in [(640, map, 12), (200, map_small, 12)]:
                    url_static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&size={size}x{size}&key={settings.MAPS_KEY}&markers={lat},{long}"
                    res_static_map = requests.get(url_static_map, stream=True)
                    with open(img_path + os.sep + map_name, "wb") as f:
                        shutil.copyfileobj(res_static_map.raw, f)
                full_size = img.size
                small_img = img.resize(
                    (full_size[0] // 4, full_size[1] // 4), Image.Resampling.LANCZOS
                )
                small_img.save(img_path + os.sep + small)

        except (ZeroDivisionError, KeyError):
            lat, long, alt, map, map_small, small = nan, nan, None, None, None, None

        gps = {"lat": lat, "long": long, "alt": alt}
        imgs.append(
            {
                "path": p,
                "datetime": exif.get("DateTime", "zzz zzz"),
                "gps": gps,
                "map": map,
                "map_small": map_small,
                "small": small,
            }
        )

    imgs.sort(key=lambda x: x.get("datetime"))

    imgs_by_days = []
    last_date = None
    for img in imgs[::-1]:
        date, time = img["datetime"].split(" ")
        date = "/".join(date.split(":")[::-1])  # sry
        if date == last_date:
            imgs_by_days[-1]["imgs"].append({**img, "time": time})
        else:
            imgs_by_days.append({"date": date, "imgs": [{**img, "time": time}]})
            last_date = date

    return render(
        request, "japan/index.html", {"user": request.user, "date_imgs": imgs_by_days}
    )

def reset_skies_of_japan(request):
    from os import listdir, path, remove, sep
    if not request.user.is_superuser:
        return HttpResponse(status=401)
    
    img_path = settings.MEDIA_ROOT + "japan/"
    for filename in listdir(img_path):
        if path.isfile(img_path+sep+filename):
            remove(img_path+sep+filename)
    return redirect('japan')

