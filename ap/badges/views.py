from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.template import RequestContext
from django.template import loader, Context
from django.core.urlresolvers import reverse,reverse_lazy
from django.shortcuts import render
from django.db.models import Q
from django.views.generic import ListView
from .models import Badge, BadgePrintSettings
from accounts.models import User, Trainee
from terms.models import Term
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from .forms import BadgeForm, BadgeUpdateForm, BadgePrintForm, BadgePrintSettingsUpdateForm
import datetime
from .util import _image_upload_path, resize_image
from django.http import HttpResponse
from terms.models import Term
import re

class index(ListView):
  model = Badge
  template_name = "badge_list.html"

def batch(request):
  if request.method == 'POST':
    b = Badge(type='T')
    b.original = request.FILES['file']
    b.avatar = request.FILES['file']

    # grab the trainee name. filename in form of:
    # /path/to/Ellis_Armad.jpg or /path/to/Ellis_Armad_1.jpg
    name = b.original.name.split('/')[-1].split('.')[0].split('_')[0]
    nameList = re.sub("([a-z])([A-Z])","\g<1> \g<2>", name).split(' ')

    first = nameList[-1]
    last = nameList[0]
    middle = ''
    if len(nameList) > 2:
      middle = nameList[1]
    try:
      badge = Badge.objects.get(Q(deactivated=False),
                Q(firstname__exact=first),
                Q(middlename__exact=middle),
                Q(lastname__exact=last))
      if badge:
        print 'Found badge, updating image', badge
        badge.original = b.original
        badge.avatar = b.avatar
        badge.save()
    except Badge.DoesNotExist:
      print "Error Badge does not exist"
      # Create badge
      b.firstname = first
      b.middlename = middle
      b.lastname = last
      b.term_created = Term.current_term()
      b.save()
      print "Trainee", b.firstname, "saved!"

    except Badge.MultipleObjectsReturned:
      print 'Error: more than one trainee found!'
      return HttpResponseBadRequest('More than one trainee found, will not update badge picture.')

  return render(request, 'badges/batch.html')

def badgeprintout(request):
  return render(request, 'badges/print.html', {'object_list': Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(deactivated__exact=False))})

def pictureRange(begin, end):
  if begin>end:
    return []

  pictureRangeArray = []
  for num in range(int(begin-end)/8):
    pictureRangeArray = pictureRangeArray.append(begin+num*8)

  return pictureRangeArray

def printSelectedChoicesOnly(Badge, request, context):
  print 'ids to print', request.POST.getlist('choice')
  copies = int(request.POST.get('copies', 1))

  if 'choice' in request.POST:
    pk_list = request.POST.getlist('choice')
    objects = Badge.objects.filter(id__in=pk_list)

    # Super inefficient sorting. Port to PSQL in future
    objects = dict([(str(obj.id), obj) for obj in objects])
    sorted_objects = [objects[id] for id in pk_list]

    context['object_list'] = sorted_objects * copies

class BadgePrintFrontView(ListView):

  model = Badge

  def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)

  def get_template_names(self):
    return ['badges/print.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(type__exact='T') & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintFrontView, self).get_context_data(**kwargs)
    printSelectedChoicesOnly(Badge, self.request, context)

    return context

class BadgePrintMassFrontView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/print.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(type__exact='T') & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintMassFrontView, self).get_context_data(**kwargs)

    numTrainees = Trainee.objects.filter().all().count()
    #Signifies the range of pictures to place on the right side
    context['need_bottom_rightside'] = pictureRange(6, numTrainees)
    #Signifies the range of pictures to place on the left side
    context['need_bottom_leftside'] = pictureRange(7, numTrainees)

    return context

# Dynamically generate css to add in customizable settings
def badgeSettingsCSS(request):
  # do custom element positionting.
  response = HttpResponse(content_type='text/css')
  context = {}
  context['badge_print_settings'] = BadgePrintSettings.objects.first()

  t = loader.get_template('css/badgeSettings.css')
  response.write(t.render(context))
  return response

class BadgePrintBostonFrontView(ListView):

  model = Badge

  def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)

  def get_template_names(self):
    return ['badges/printboston.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(type__exact='X') & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintBostonFrontView, self).get_context_data(**kwargs)
    printSelectedChoicesOnly(Badge, self.request, context)
    return context

class BadgePrintMassBostonFrontView(ListView):

  model = Badge

  def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)

  def get_template_names(self):
    return ['badges/printboston.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(type__exact='X') & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintMassBostonFrontView, self).get_context_data(**kwargs)
    printSelectedChoicesOnly(Badge, self.request, context)
    return context


class BadgePrintAllInclusiveFrontView(ListView):

  model = Badge

  def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)

  def get_template_names(self):
    return ['badges/printallinclusive.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.all()

  def get_context_data(self, **kwargs):
    context = super(BadgePrintAllInclusiveFrontView, self).get_context_data(**kwargs)
    printSelectedChoicesOnly(Badge, self.request, context)

    return context

class BadgePrintBostonBackView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printbostonback.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintBostonBackView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(8)]
    return context

class BadgePrintGeneralBackView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printgeneralback.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintGeneralBackView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(16)]
    return context

def facebookOrder(queryset):
  return queryset.order_by('lastname', 'firstname')

class BadgePrintFacebookView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printfbpdf.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(deactivated__exact=False))

  # Praise the Lord!!!!!!!
  def get_context_data(self, **kwargs):
    context = super(BadgePrintFacebookView, self).get_context_data(**kwargs)

    termObject = Term().current_term()
    context['current_term'] = termObject

    if termObject.season == "Spring":
      yearone = termObject.year
      yeartwo = termObject.year - 1
      yearthree = termObject.year - 1
      yearfour = termObject.year - 2
      firstseason  = 'Spring'
      secondseason = 'Fall'
      thirdseason  = 'Spring'
      fourthseason = 'Fall'

    else:
      yearone = termObject.year
      yeartwo = termObject.year
      yearthree = termObject.year - 1
      yearfour = termObject.year -1
      firstseason  = 'Fall'
      secondseason = 'Spring'
      thirdseason  = 'Fall'
      fourthseason = 'Spring'

    def grouped(l, n):
      for i in xrange(0, len(l), n):
        yield l[i:i+n]

    context['trainees'] = [
      {
        'header': 'First-Term Brothers',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearone, season=firstseason), gender__exact='M') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'First-Term Sisters',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearone, season=firstseason), gender__exact='F') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'Second-Term Brothers',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yeartwo, season=secondseason), gender__exact='M') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'Second-Term Sisters',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yeartwo, season=secondseason), gender__exact='F') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'Third-Term Brothers',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearthree, season=thirdseason), gender__exact='M') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'Third-Term Sisters',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearthree, season=thirdseason), gender__exact='F') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'Fourth-Term Brothers',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearfour, season=fourthseason), gender__exact='M') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'Fourth-Term Sisters',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearfour, season=fourthseason), gender__exact='F') & Q(type__exact='T') & Q(deactivated=False))), 6),
      },
      {
        'header': 'First-Term Brothers',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearone, season=firstseason), gender__exact='M') & Q(type='X') & Q(deactivated=False))), 6),
        'type': 'XB',
      },
      {
        'header': 'First-Term Sisters',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yearone, season=firstseason), gender__exact='F') & Q(type='X') & Q(deactivated=False))), 6),
        'type': 'XB',
      },
      {
        'header': 'Second-Term Brothers',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yeartwo, season=secondseason), gender__exact='M') & Q(type='X') & Q(deactivated=False))), 6),
        'type': 'XB',
      },
      {
        'header': 'Second-Term Sisters',
        'trainee_list': grouped(facebookOrder(Badge.objects.filter(Q(term_created=Term.objects.get(year=yeartwo, season=secondseason), gender__exact='F') & Q(type='X') & Q(deactivated=False))), 6),
        'type': 'XB',
      },
    ]

    return context

# class BadgePrintFrontView(ListView):

#   model = Badge

#   def post(self, request, *args, **kwargs):
#     return self.get(request, *args, **kwargs)

#   def get_template_names(self):
#     return ['badges/print.html']

#   def get_queryset(self, **kwargs):
#     return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(type__exact='T'))

#   def get_context_data(self, **kwargs):
#     context = super(BadgePrintFrontView, self).get_context_data(**kwargs)

#     print 'ids to print', self.request.POST.getlist('choice')

#     if 'choice' in self.request.POST:
#       pk_list = self.request.POST.getlist('choice')
#       objects = Badge.objects.filter(id__in=pk_list)

#       # Super inefficient sorting. Port to PSQL in future
#       objects = dict([(str(obj.id), obj) for obj in objects])
#       sorted_objects = [objects[id] for id in pk_list]

#       context['object_list'] = sorted_objects

#     return context

class BadgePrintStaffView(ListView):

  model = Badge

  def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)

  def get_template_names(self):
    return ['badges/printstaff.html']


  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & (Q(type__exact='S') | Q(type__exact='XS')) & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintStaffView, self).get_context_data(**kwargs)
    printSelectedChoicesOnly(Badge, self.request, context)

    return context

class BadgePrintShorttermView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printshortterm.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(term_created__exact=Term.current_term())

  def get_context_data(self, **kwargs):
    context = super(BadgePrintShorttermView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(8)]
    return context

class BadgeTermView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/view_first_term.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.select_related().filter(Q(term_created__exact=Term.current_term()) & Q(deactivated__exact=False) & Q(type__exact='T'))

  def get_context_data(self, **kwargs):
    context = super(BadgeTermView, self).get_context_data(**kwargs)
    context['type'] = "1T";
    return context

class BadgeXBTermView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/view_xb.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.select_related().filter(Q(term_created__exact=Term.current_term()) & Q(deactivated__exact=False) & Q(type__exact='X'))

  def get_context_data(self, **kwargs):
    context = super(BadgeXBTermView, self).get_context_data(**kwargs)
    context['type'] = "XB";
    return context

class BadgeStaffView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/view_staff.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.select_related().filter((Q(type__exact='S') | Q(type__exact='XS')) & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgeStaffView, self).get_context_data(**kwargs)
    context['type'] = "S";
    return context

class BadgeListView(ListView):
  model = Badge
  queryset = Badge.objects.select_related()
  template_name = 'badges/view_all.html'

  def get_context_data(self, **kwargs):
    context = super(BadgeListView, self).get_context_data(**kwargs)
    context['type'] = "All";
    return context

class BadgeCreateView(CreateView):
  form_class = BadgeForm
  model = Badge
  success_url='/badges/view/current'

  def get_context_data(self, **kwargs):
    context = super(BadgeCreateView, self).get_context_data(**kwargs)
    return context

class BadgeUpdateView(UpdateView):
  model = Badge
  template_name = 'badges/badge_detail.html'
  form_class = BadgeUpdateForm

  # This makes sure to return to the original detail_list page after update (e.g. current or all)
  def get_success_url(self):
    args = self.get_form_kwargs()['data']
    print 'args', args
    return_url = ''
    if 'return_url' in args:
      return_url = args['return_url']
    if not return_url or return_url == '':
      return '/badges/view/current'
    else:
      return return_url

  def get_context_data(self, **kwargs):
    context = super(BadgeUpdateView, self).get_context_data(**kwargs)
    return context

class BadgeDeleteView(DeleteView):
  model = Badge
  template_name = 'badges/badge_delete.html'
  success_url='/badges/view/current'

class BadgePrintUsherView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printusher.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(Q(term_created__exact=Term.current_term()) & Q(deactivated__exact=False))

  def get_context_data(self, **kwargs):
    context = super(BadgePrintUsherView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(8)]
    return context

class BadgePrintTempView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printtemp.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(term_created__exact=Term.current_term())

  def get_context_data(self, **kwargs):
    context = super(BadgePrintTempView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(50)]
    return context

class BadgePrintVisitorView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printvisitor.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(term_created__exact=Term.current_term())

  def get_context_data(self, **kwargs):
    context = super(BadgePrintVisitorView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(50)]
    return context

class BadgePrintVisitorXBView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printvisitorxb.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(term_created__exact=Term.current_term())

  def get_context_data(self, **kwargs):
    context = super(BadgePrintVisitorXBView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(50)]
    return context

class BadgePrintOfficeView(ListView):

  model = Badge

  def get_template_names(self):
    return ['badges/printoffice.html']

  def get_queryset(self, **kwargs):
    return Badge.objects.filter(term_created__exact=Term.current_term())

  def get_context_data(self, **kwargs):
    context = super(BadgePrintOfficeView, self).get_context_data(**kwargs)
    context['loop_times'] = [i+1 for i in range(8)]
    return context

def genpdf(request):
  return render(request, 'badges/print.html')

def remakeMassAvatar(request):
  allBadges = Badge.objects.all()
  print allBadges

  for badge in allBadges:
    resize_image(badge.original)
    name = badge.original.path.split('media')
    badge.avatar = "media" + name[1] + ".avatar"
    print badge.avatar
    badge.save()
  return HttpResponse("Successfully remake avatars!")


class BadgePrintSettingsUpdateView(UpdateView):
  model = BadgePrintSettings
  template_name = 'badges/badge_print_settings.html'
  form_class = BadgePrintSettingsUpdateForm
  success_url='/badges/view/current'

  def get_object(self, queryset=None):
    if BadgePrintSettings.objects.count() == 0:
      setting = BadgePrintSettings(banner_color='#191CFA')
      setting.save()
    else:
      setting = BadgePrintSettings.objects.first()

    return setting

  def get_context_data(self, **kwargs):
    context = super(BadgePrintSettingsUpdateView, self).get_context_data(**kwargs)
    return context
