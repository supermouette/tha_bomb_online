from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from game.models import ScrapedData
from django.contrib.auth.models import User
from datetime import datetime
import csv


@csrf_exempt
def scrap(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        username = json_data['user']
        user = User.objects.filter(username=username)[0]
        title = json_data['title']
        price = int(json_data['price'].replace(' ', '').replace('€', ''))
        page_created = datetime.strptime(json_data['page_created'], '%d/%m/%Y à %H:%M')
        page_visited = datetime.now()
        print(user, title, price, page_created, sep=", ")
        scrap = ScrapedData(user=user,
                            title=title,
                            price=price,
                            page_created=page_created,
                            page_visited=page_visited,
                            url=json_data['url'])
        if "ref" in json_data:
            scrap.ref = json_data['ref']
        if "url_img" in json_data:
            scrap.url_img = json_data['url_img']
        scrap.save()
    return HttpResponse(status=200)


@login_required
def house_tracker(request):
    row_list = ScrapedData.objects.filter(user=request.user)
    context = {'user': request.user, 'row_list': row_list}
    return render(request, 'game/house_tracker.html', context)


@login_required
def house_tracker_csv(request):
    row_list = ScrapedData.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="house_tracker.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Price', 'ref', 'Page created', 'Page visited', 'Link'])
    for row in row_list:
        writer.writerow([row.title, row.price, row.ref, row.page_created, row.page_visited, row.url])
    return response
