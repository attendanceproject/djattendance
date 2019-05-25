from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpResponse
from .models import Vocab

def index(request):

    # Vocab is filtered by chapter
    chapters = []
    for c in range(1, 17):
        chapters.append(c)

    greek_list = []
    english_list = []

    greek_list = list(Vocab.objects.filter(chapter="1"))
    print greek_list

    context={
        "chapters": chapters,
        "greekVocab": greek_list,
        "english": english_list,
    }

    return render(request, 'greek_helper/vocab_list.html', context=context)