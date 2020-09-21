
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {})


# def confForm(request):
#     return render(request, 'source_form.html', {})