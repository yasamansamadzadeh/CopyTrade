# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from apps.trade.models import Follow


@login_required(login_url="/login/")
def index(request):
    accounts = {}
    if hasattr(request.user, 'trader'):
        for account in request.user.trader.accounts.all():
            accounts[account.type] = accounts.get(account.type, []) + [account]

    follow = Follow.objects.filter(slave=request.user.trader).first()

    context = {
        'segment': 'index',
        'accounts': accounts,
        'is_master': hasattr(request.user, 'trader') and request.user.trader.is_master,
        'followers': Follow.objects.filter(master=request.user.trader).count(),
        'current_master': follow.master if follow else None,
    }

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
