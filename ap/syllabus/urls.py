from django.conf.urls import patterns, url

from syllabus.views import AboutView, SyllabusDetailView, HomeView
from syllabus.models import Syllabus
#from terms.models import Term
#from terms import views

urlpatterns = patterns('',

	url(r'^$', HomeView.as_view(), name='home-view'),

	# list of syllabi
	url(r'^1styear/$', AboutView.as_view(model=Syllabus, 
					context_object_name="list"), name='classlist-view'),
		
	# list of sessions in syllabus
	# TO DO: make sure the \D+ actually matches up with a class code.
	url(r'^1styear/(\D+)/$', 
		SyllabusDetailView.as_view(model=Syllabus, context_object_name="syl_list"), 
		name='detail-view'),	
)
