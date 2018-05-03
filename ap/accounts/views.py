from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView, UpdateView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin

from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Trainee, User, TrainingAssistant, UserMeta
from .forms import UserForm, EmailForm, SwitchUserForm
from .serializers import UserSerializer, TraineeSerializer, TrainingAssistantSerializer

from aputils.auth import login_user


class CurUserOnlyDetailView(SingleObjectMixin):
  def get_object(self, *args, **kwargs):
    obj = super(CurUserOnlyDetailView, self).get_object(*args, **kwargs)
    if obj != self.request.user:
      raise PermissionDenied()
    else:
      return obj


class UserDetailView(CurUserOnlyDetailView, DetailView):
  model = User
  context_object_name = 'user'
  template_name = 'accounts/user_detail.html'


class UserUpdateView(CurUserOnlyDetailView, UpdateView):
  model = User
  form_class = UserForm
  template_name = 'accounts/update_user.html'

  def get_success_url(self):
    messages.success(self.request, "User Information Updated Successfully!")
    return reverse_lazy('user_detail', kwargs={'pk': self.kwargs['pk']})


class EmailUpdateView(CurUserOnlyDetailView, UpdateView):
  model = User
  form_class = EmailForm
  template_name = 'accounts/email_change.html'

  def get_success_url(self):
    messages.success(self.request, "Email Updated Successfully!")
    return reverse_lazy('user-detail', kwargs={'pk': self.kwargs['pk']})


# class SwitchUserView(GroupRequiredMixin, TemplateView):
class SwitchUserView(SuccessMessageMixin, FormView):
  template_name = 'accounts/switch_user.html'
  context_object_name = 'context'
  form_class = SwitchUserForm
  success_url = reverse_lazy('home')
  success_message = "Successfully switched to %(user_id)s"

  def form_valid(self, form):
    user = form.cleaned_data['user_id']
    logout(self.request)
    login_user(self.request, user)
    return super(SwitchUserView, self).form_valid(form)


class AllTrainees(ListView):
  model = Trainee
  template_name = 'accounts/trainees_table.html'

  def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    if self.request.method == 'POST':
      val = self.request.POST.get('change')
      email = self.request.POST.get('pk')
      f = self.request.POST.get('f')
      if f == 'Firstname':
        Trainee.objects.filter(email=email).update(firstname=val)
      elif f == 'Lastname':
        Trainee.objects.filter(email=email).update(lastname=val)
      elif f == 'Phone':
        t = Trainee.objects.filter(email=email)
        UserMeta.objects.filter(user=t.first()).update(phone=val)
      elif f == 'Email':
        Trainee.objects.filter(email=email).update(email=email)
      elif f == 'On self attendance':
        t = Trainee.objects.filter(email=email).first()
        if val == "True":
          t.self_attendance = False
        else:
          t.self_attendance = True
        t.save()

    context = super(AllTrainees, self).get_context_data(**kwargs)
    context['list_of_trainees'] = Trainee.objects.filter(is_active=True).select_related('team', 'locality', 'house')
    return context


""" API Views """


class UserViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer


class TraineeViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Trainee.objects.filter(is_active=True).prefetch_related('groups', 'terms_attended', 'locality')
  serializer_class = TraineeSerializer


class TrainingAssistantViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = TrainingAssistant.objects.filter(is_active=True)
  serializer_class = TrainingAssistantSerializer


class TraineesByGender(generics.ListAPIView):
  serializer_class = TraineeSerializer
  model = Trainee

  def get_queryset(self):
    gender = self.kwargs['gender']
    return Trainee.objects.filter(gender=gender).prefetch_related('groups', 'terms_attended', 'locality')


class TraineesByTerm(APIView):
  model = Trainee

  def get(self, request, format=None, **kwargs):
    term = int(kwargs['term'])
    trainees = [trainee for trainee in list(Trainee.objects.all().prefetch_related('groups', 'terms_attended', 'locality')) if trainee.current_term == term]
    serializer = TraineeSerializer(trainees, many=True)
    return Response(serializer.data)


class TraineesByTeam(generics.ListAPIView):
  serializer_class = TraineeSerializer
  model = Trainee

  def get_queryset(self):
    team = self.kwargs['pk']
    return Trainee.objects.filter(team__id=team).prefetch_related('groups', 'terms_attended', 'locality')


class TraineesByTeamType(generics.ListAPIView):
  serializer_class = TraineeSerializer
  model = Trainee

  def get_queryset(self):
    type = self.kwargs['type'].upper()
    return Trainee.objects.filter(team__type=type).prefetch_related('groups', 'terms_attended', 'locality')


class TraineesByHouse(generics.ListAPIView):
  serializer_class = TraineeSerializer
  model = Trainee

  def get_queryset(self):
    house = self.kwargs['pk']
    return Trainee.objects.filter(house__id=house).filter(is_active=True)


class TraineesByLocality(generics.ListAPIView):
  serializer_class = TraineeSerializer
  model = Trainee

  def get_queryset(self):
    locality = self.kwargs['pk']
    return Trainee.objects.filter(locality__id=locality).filter(is_active=True)


class TraineesHouseCoordinators(generics.ListAPIView):
  serializer_class = TraineeSerializer
  model = Trainee

  def get_queryset(self):
    trainees = Trainee.objects.filter(is_active=True)
    return filter(lambda x: x.HC_status(), trainees)
