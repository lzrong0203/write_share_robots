from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("<b>Hello, world. You're at the polls index.</b>")
