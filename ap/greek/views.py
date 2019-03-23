from django.shortcuts import render
from django.http import HttpResponse
from .models import Vocab

# Create your views here.
def index(request):
    
    context={

    }

    return render(request, 'vocab_list.html', context=context)
