from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpResponse
from .models import Vocab

def index(request):

    greek_list = []
    english_list = []

    # By default, Greek page loads vocabs in chapter 1
    greek_list = Vocab.objects.filter(chapter=1)

    # Vocab landing page is filtered by chapter
    chapters = []
    for c in range(1, 17):
        chapters.append(c)

    context={
        "chapters": chapters,
        "greekVocab": greek_list,
    }

    return render(request, 'greek_helper/vocab_list.html', context=context)