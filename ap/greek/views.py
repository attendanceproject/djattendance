from django.shortcuts import render
from django.http import HttpResponse
from .models import Vocab

def index(request):

    greek_list = []
    english_list = []

    # greekVocab = list(Vocab.greek)
    # print greekVocab
    for e in Vocab.objects.all():
        greek_list.append(e)
        # print(e.greek)

    context={
        "greekVocab": list(greek_list),
    }

    return render(request, 'greek_helper/vocab_list.html', context=context)
