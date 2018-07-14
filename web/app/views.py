from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .Info.info import Info
import json
# Create your views here.


def index(request):
    return render(request, 'app/index.html')


@csrf_exempt
def check(request):
    url = request.POST.getlist('link')[0]
    # print(url)
    if url and 'http' in url:
        try:
            info = Info(url)
        except:
            pass
        else:
            res = {
                'title': info.get_title(),
                'origin': info.get_origin(),
                'time': info.get_time(),
                'keyword': info.get_keyword(),
                'type': info.get_predict(),
                'passages_count': info.get_passages_counts(),
                'count': info.get_count(),
                'code': 4
            }
            print(res)
            return HttpResponse(json.dumps(res), 'application/json')
    return HttpResponse(json.dumps({'code': 'erro'}), 'application/json')