from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpResponse
from .models import Vocab

def index(request):

    # Vocab is filtered by chapter
    chapters = []
    for c in range(1, 17):
        chapters.append(c)

    chap = 1
    greek_list = []
    english_list = []

    # The greek helper page will initially load chapter 1
    greek_list = list(Vocab.objects.all().filter(chapter=chap))
    print greek_list

    greek = Vocab.objects.all()
    eng = []
    for g in greek:
        e = VocabForm(instance = g)
        eng.append({'id': g.id, 'form': form})

    print eng

    context={
        "chapters": chapters,
        "greekVocab": list(greek_list),
        "english": english_list,
    }

    return render(request, 'greek_helper/vocab_list.html', context=context)