from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from apps.trade.models import Trader, Follow


@csrf_exempt
@login_required(login_url="/login/")
def masters(request):

    context = {
        'segment': 'masters',
        'masters': Trader.objects.filter(is_master=True),
        'is_master': hasattr(request.user, 'trader') and request.user.trader.is_master,
    }

    if request.method == 'POST':
        master_id = request.POST.dict()['master_id']
        master = Trader.objects.get(id=master_id)
        Follow.objects.filter(slave=request.user.trader).delete()
        Follow.objects.create(master=master, slave=request.user.trader)

    html_template = loader.get_template('trade/masters.html')
    return HttpResponse(html_template.render(context, request))
