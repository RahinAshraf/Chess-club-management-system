from django.shortcuts import render
from django.http import HttpResponse, response

# Create your views here.

def home(request):
    return render(request, 'home.html')
    #response = HttpResponse("Welcome")
    #return response


