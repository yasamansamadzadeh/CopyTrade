from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from apps.trade.models import Trader, Follow


@csrf_exempt
@login_required(login_url="/login/")
def masters(request):
    context = {
        'segment': 'masters',
        'masters': Trader.objects.filter(is_master=True).annotate(
            is_followed=Exists(Follow.objects.filter(master=OuterRef('pk'), slave=request.user.trader))),
        'is_master': hasattr(request.user, 'trader') and request.user.trader.is_master,
    }

    if request.method == 'POST':
        action = request.POST.dict()['action']
        master_id = request.POST.dict()['master_id']
        master = Trader.objects.get(id=master_id, is_master=True)
        if action == 'follow':
            if not Follow.objects.filter(master=master, slave=request.user.trader).exists():
                Follow.objects.create(master=master, slave=request.user.trader)
        elif action == 'unfollow':
            Follow.objects.filter(master=master, slave=request.user.trader).delete()

    html_template = loader.get_template('trade/masters.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def orders(request):
    orders = {}
    if hasattr(request.user, 'trader'):
        for order in request.user.trader.orders.all():
            orders[order.status] = orders.get(order.status, []) + [order]

    context = {
        'segment': 'orders',
        'orders': orders,
    }

    html_template = loader.get_template('trade/orders.html')
    return HttpResponse(html_template.render(context, request))
