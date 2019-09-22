from django.shortcuts import render
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .models import Vocab
from classes.models import ClassFile
import json

def index(request):

    ### FOR FILES TAB ###
    class_files = ClassFile.objects.filter(for_class='Greek')

    #for files in class_files:
    #    print json.dumps(files, default=lambda x: x.__dict__)

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
        # TODO: Convert QuerySet to list
        "greekVocab_json": list(greek_list.values()),
        "classFiles": class_files,
    }
    print(context["greekVocab"])
    print(context["greekVocab_json"])

    ## CONTINUATION OF FILES TAB ###
    context['classname'] = 'Greek'
    context['class_files'] = ClassFile.objects.filter(for_class="Greek")
    context['page_title'] = '%s Files' % (class_files)

    return render(request, 'greek_helper/index.html', context=context)

def changeChapter(request):

    if request.is_ajax():
        chapter = request.GET['chapter']
    try:
        greek_list = Vocab.objects.filter(chapter=chapter)

        # SERIALIZE METHOD:
        json_greek_list = serializers.serialize('json', greek_list)
        return HttpResponse(json_greek_list, content_type='application/json')
    except ObjectDoesNotExist:
        return HttpResponse('Error from ajax call')
