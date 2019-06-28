from django.shortcuts import render
from django.views.generic import ListView
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .models import Vocab
import json

def index(request):

    ### FOR FILES TAB ###

          
    ### FOR VOCAB LIST TAB ###

    # By default, the page loads vocabs in chapter 1
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

def changeChapter(request):

    vocab = []
    if request.is_ajax():
        chapter = request.GET['chapter']
    try:
        greek_list = Vocab.objects.filter(chapter=chapter)

        # SERIALIZE METHOD:
        json_greek_list = serializers.serialize('json', greek_list)
        return HttpResponse(json_greek_list, content_type='application/json')
    except ObjectDoesNotExist:
        return HttpResponse('Error from ajax call')
