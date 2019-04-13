from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

def modify_question_status(model, url):
  def modify_status(request, status, id, message_func=None):
    obj = get_object_or_404(model, pk=id)
    obj.status = status
    obj.save()
    if message_func:
      message = message_func(obj)
    else:
      message = "%s's %s was %s" % (obj.requester_name, obj._meta.verbose_name, obj.get_status_display())
    messages.add_message(request, messages.SUCCESS, message)
    return redirect(url)
  return modify_status