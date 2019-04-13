from django.conf.urls import url
from apimport import views


urlpatterns = [
  # url(r'^$', views.index, name='index'),
  url(r'^$', views.CreateTermView.as_view(), name='term_details'),
  url(r'process-csv$', views.ProcessCsvData.as_view(), name='process_csv'),
  url(r'save-data$', views.save_data, name='save_data'),
  url(r'process-row$', views.process_row, name='process-row')
]
