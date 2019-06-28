from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from aputils.decorators import group_required
from .forms import ClassFileForm
from .models import ClassFile, CLASS_CHOICES_ALL, CLASS_CHOICES_ALL_ITEMS


def is_classfiles_admin(user):
  return user.has_group(['training_assistant', 'special_projects'])


def upload(request):
  if request.method == 'POST':
    if is_classfiles_admin(request.user) or request.POST.get('for_class') in CLASS_CHOICES_ALL_ITEMS:
      form = ClassFileForm(request.POST, request.FILES, limit_choices=False)
      if form.is_valid():
        form.save()
    return redirect(reverse('classes:index'))


@group_required(['training_assistant', 'special_projects'])
def delete_file(request, pk):
  ClassFile.objects.get(id=pk).delete()
  return redirect(reverse('classes:index'))


def class_files(request, classname=None):
  ctx = {
      'classname': classname,
  }

  if request.method == 'GET':
    if not classname and is_classfiles_admin(request.user):
      ctx['page_title'] = 'Class Files Administration'
      ctx['class_files'] = ClassFile.objects.all()
      ctx['form'] = ClassFileForm(limit_choices=False)
      ctx['delete'] = True
    else:
      classname = classname or 'Greek'
      ctx['classname'] = classname
      if classname in CLASS_CHOICES_ALL_ITEMS:
        ctx['form'] = ClassFileForm(limit_choices=CLASS_CHOICES_ALL)
      ctx['class_files'] = ClassFile.objects.filter(for_class=classname)
      ctx['page_title'] = '%s Files' % (classname)

  return render(request, 'classes/class_files.html', ctx)
