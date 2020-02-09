from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    context = {}
    return render(request, 'game/index.html', context)


def skys_of_denmark(request):
    import datetime
    from .models import Sky
    from random import randrange

    now = datetime.datetime.now()
    today = Sky.objects.filter(day=now.day, month=now.month)
    if today.count() == 0:
        Sky(color=randrange(120, 200), day=now.day, month=now.month).save()
        tomorrow = now + datetime.timedelta(days=1)
        Sky(color=randrange(120, 200), day=tomorrow.day, month=tomorrow.month).save()
        if now.day == 1:
            yesterday = now - datetime.timedelta(days=1)
            Sky.objects.filter(month=yesterday.month).delete()

    days = Sky.objects.order_by("day")
    if days.count() != now.day:
        days_nb = [d.day for d in days]
        for i in range(1, now.day):
            if i not in days_nb:
                Sky(color=randrange(120, 200), day=i, month=now.month).save()
        days= Sky.objects.order_by("-day")

    context = {
        'skys':days[1:],
        'tomorrow': days[0]
    }

    return render(request, 'game/skys_of_denmark.html', context)
