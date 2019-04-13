from datetime import date, datetime, time

from django.forms.models import modelformset_factory
from django.shortcuts import render
from django.http import HttpResponse
from django.template.context_processors import csrf
from aputils.decorators import group_required

from absent_trainee_roster.models import Entry, Roster
from absent_trainee_roster.forms import AbsentTraineeForm, NewEntryFormSet

from absent_trainee_roster.utils import generate_pdf, send_absentee_report

EntryFormSet = modelformset_factory(Entry, AbsentTraineeForm, formset=NewEntryFormSet, max_num=1000, extra=1, can_delete=True)


@group_required(['training_assistant', 'HC', 'absent_trainee_roster'])
def absent_trainee_form(request):
  today = date.today()
  user = request.user
  is_HC = user.HC_status()
  is_absentee_service_trainee = user.groups.filter(name='absent_trainee_roster').exists()
  # get today's roster. create it if it doesn't exist.
  if Roster.objects.filter(date=today).exists():
    roster = Roster.objects.get(date=today)
  else:
    roster = Roster.objects.create_roster(date=today)

  if request.method == 'POST':
    # If HC submits any type of form, counts it as reported (empty form)
    if is_HC:
      roster.unreported_houses.remove(request.user.house)

    formset = EntryFormSet(request.POST, request.FILES, user=request.user)
    if formset.is_valid():
      for form in formset.forms:
        if form.is_valid() and form.cleaned_data:  # only save entry if it's not empty
          entry = form.save(commit=False)

          entry.roster = roster
          if is_absentee_service_trainee:
            roster.unreported_houses.remove(entry.absentee.house)
            entry.save()

      # This should handle add/update/deletion automatically
      formset.save()

      # Refetch formset so total/initial count is calculated correctly
      if is_absentee_service_trainee:
        formset = EntryFormSet(user=request.user, queryset=roster.entry_set.all())
      else:
        formset = EntryFormSet(user=request.user, queryset=roster.entry_set.filter(absentee__house=request.user.house))

    roster.notes = request.POST.get('notes') if request.POST.get('notes') else ''
    roster.save()

  else:
    # shows existing entries from user's house, i.e. if form was already submitted and user revisits the page
    if is_absentee_service_trainee:
      formset = EntryFormSet(user=request.user, queryset=roster.entry_set.all())
    else:
      formset = EntryFormSet(user=request.user, queryset=roster.entry_set.filter(absentee__house=request.user.house))

  bro_unreported = roster.unreported_houses.filter(gender='B')
  sis_unreported = roster.unreported_houses.filter(gender='S')

  if request.user.house in bro_unreported | sis_unreported:
    stat = "Unsubmitted"
  else:
    stat = "Submitted"

  read_only = True
  if time(6) <= datetime.now().time() <= time(8, 05):
    read_only = False

  if datetime.today().weekday() == 6:
    if time(6) <= datetime.now().time() <= time(8, 20):
      read_only = False
  c = {
      'formset': formset,
      'user': request.user,
      'bro_unreported': bro_unreported,
      'sis_unreported': sis_unreported,
      'roster': roster,
      'read_only': read_only,
      'is_absentee_service_trainee': is_absentee_service_trainee,
      'status': stat,
  }
  c.update(csrf(request))

  return render(request, 'absent_trainee_roster/absent_trainee_form.html', c)


@group_required(['training_assistant', 'absent_trainee_roster'])
def pdf_report(request, year, month, day):
  return generate_pdf(year, month, day)


@group_required(['training_assistant', 'absent_trainee_roster'])
def email(request):
  today = date.today()
  send_absentee_report(today.year, today.month, today.day)
  return HttpResponse("Email was sent")


@group_required(['training_assistant', 'absent_trainee_roster'])
def email_on_date(request, year, month, day):
  send_absentee_report(year, month, day)
  return HttpResponse("Email was sent for %s-%s-%s" % (month, day, year))
