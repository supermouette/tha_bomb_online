from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False
    context = {"user": user}
    return render(request, 'game/index.html', context)


def skys_of_denmark(request):
    import datetime
    from .models import Sky
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
        Sky(color=randrange(120, 200), day=now.day, month=now.month, year=now.year).save()

    tomorrow = now + datetime.timedelta(days=1)

    if Sky.objects.filter(day=tomorrow.day, month=tomorrow.month).count() == 0: # add object for tomorrow
        Sky(color=randrange(120, 200), day=tomorrow.day, month=tomorrow.month, year=tomorrow.year).save()

    # check for other days
    days = Sky.objects.order_by("-day")
    if days.count() != now.day + 1:
        days_nb = [d.day for d in days]
        for i in range(1, now.day):
            if i not in days_nb:
                Sky(color=randrange(120, 200), day=i, month=now.month, year=now.year).save()
        days = Sky.objects.order_by("-day")

    context = {
        'skys':days[1:],
        'tomorrow': days[0],
        'user': user,
    }

    return render(request, 'game/skys_of_denmark.html', context)
