from django.conf.urls import url

from . import views

urlpatterns = [
    # url(r'^', views.index, name='index'),
    url(r'^build/', views.query_build_records, name='query_build_records'),
]
