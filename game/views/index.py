from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.exceptions import BadRequest
from django.db.models.functions import ExtractHour, TruncDate, Concat, Cast
from django.db.models import Count, Case, When, Value, CharField
from django.views.decorators.csrf import csrf_exempt

import datetime
import json


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
    Sky.objects.filter(year__lt=now.year).delete()
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
    for img in imgs:
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
        if path.isfile(img_path + sep + filename):
            remove(img_path + sep + filename)
    return redirect("japan")


def friends(request):
    from game.models import Friend

    context = {"friends": Friend.objects.order_by("-popularity")}
    return render(request, "game/friends.html", context)


def friend_add_popularity(request, friend_id):
    from game.models import Friend

    f = get_object_or_404(Friend, pk=friend_id)
    f.popularity += 1
    f.save()
    return HttpResponse(f.popularity)


def offspring(request):
    from game.models import NameToGuess, NameProposition

    if request.user.is_authenticated:
        user = request.user
    else:
        user = False

    currentDate = datetime.date.today()

    name_to_guess_query = list(NameToGuess.objects.filter(guess_date=currentDate))
    names_guessed = list(NameToGuess.objects.filter(guess_date__lt=currentDate))

    bet_range = [
        ("Décembre", "12", "2025", [str(i).rjust(2, "0") for i in range(1, 32)]),
        (
            "Janvier",
            "01",
            "2026",
            [str(i).rjust(2, "0") if i <= 25 else "" for i in range(1, 32)],
        ),
    ]

    if len(name_to_guess_query) == 0:
        guess_context = {
            "guess_is_active": False,
            "names_guessed": names_guessed,
            "bet_range": bet_range,
        }
    else:
        name_to_guess = name_to_guess_query[0].name
        guess_context = {
            "guess_is_active": True,
            "guess_word_length_range": range(len(name_to_guess)),
            "guess_max_try_range": range(5),
            "guess_first_letter": name_to_guess[0].upper(),
            "names_guessed": names_guessed,
            "bet_range": bet_range,
        }

    context = {
        "user": user,
        **guess_context,
        "name_suggestion": list(NameProposition.objects.all()),
    }
    return render(request, "offspring/index.html", context)


def guess_name(request, guessed_name: str):
    from game.models import NameToGuess

    currentDate = datetime.date.today()
    name_list = list(NameToGuess.objects.filter(guess_date=currentDate))
    if len(name_list) != 1:
        raise BadRequest("No name to guess today")

    name_obj = name_list[0]
    correct_name = name_obj.name.upper()
    guessed_name = guessed_name.upper()
    jsonResponse = {}

    if len(correct_name) != len(guessed_name):
        raise BadRequest("guess has incorrect length")

    histogram_correct = {}
    for letter in correct_name:
        histogram_correct[letter] = histogram_correct.get(letter, 0) + 1

    answer = []
    for i in range(len(guessed_name)):
        if guessed_name[i] == correct_name[i]:
            answer.append("2")
            histogram_correct[guessed_name[i]] -= 1
        else:
            answer.append("0")

    for i in range(len(guessed_name)):
        if (
            guessed_name[i] != correct_name[i]
            and histogram_correct.get(guessed_name[i], 0) > 0
        ):
            answer[i] = "1"
            histogram_correct[guessed_name[i]] -= 1

    jsonResponse["result"] = "".join(answer)

    if correct_name == guessed_name:
        name_obj.nb_guessed += 1
        name_obj.save()

    return JsonResponse(jsonResponse)


def make_suggestion(request, suggested_name):
    from game.models import NameProposition

    if NameProposition.objects.filter(name=suggested_name).count() > 0:
        raise BadRequest("Already suggested")

    NameProposition.objects.create(name=suggested_name)
    return HttpResponse()


def upvote_suggestion(request, suggested_name):
    from game.models import NameProposition

    suggestion = get_object_or_404(NameProposition, name=suggested_name)

    suggestion.popularity += 1
    suggestion.save()

    return JsonResponse({"new_popularity": suggestion.popularity})


@csrf_exempt
def place_bet(request):
    from game.models import ArrivalBet

    body = json.loads(request.body)
    bet = ArrivalBet.objects.create(
        name=body["name"], name_hash=body["name_hash"], date_bet=body["date_bet"]
    )
    bet.save()

    return HttpResponse()


def get_histogram_bet(request, name_hash):
    from game.models import ArrivalBet

    histogram = (
        ArrivalBet.objects.annotate(
            date_day=TruncDate("date_bet"),
            hour=ExtractHour("date_bet"),
        )
        .annotate(
            time_bucket=Case(
                When(hour__gte=0, hour__lt=6, then=Value("00h–06h")),
                When(hour__gte=6, hour__lt=12, then=Value("06h–12h")),
                When(hour__gte=12, hour__lt=18, then=Value("12h–18h")),
                default=Value("18h–00h"),
                output_field=CharField(),
            )
        )
        .annotate(
            date_bucket=Concat(
                Cast("date_day", CharField()),  # converts date to text
                Value("_"),
                "time_bucket",
                output_field=CharField(),
            )
        )
        .values("date_bucket")
        .annotate(count=Count("id"))
        .order_by("date_bucket")
    )

    user_bets = ArrivalBet.objects.filter(name_hash=name_hash)
    user_bet_id = None
    if len(user_bets) > 0:
        user_bet = user_bets[0]
        if user_bet.date_bet.hour < 6:
            user_bin = "00h–06h"
        elif user_bet.date_bet.hour < 12:
            user_bin = "06h–12h"
        elif user_bet.date_bet.hour < 18:
            user_bin = "12h–18h"
        else:
            user_bin = "18h–00h"
        user_bet_id = str(user_bet.date_bet) + user_bin
    else:
        date_bet = None

    return JsonResponse({"histogram": list(histogram), "user_bet_id": user_bet_id})
