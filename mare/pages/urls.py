from django.urls import path
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("sobre/", views.sobre, name="sobre"),
    path("privacidade/", views.privacidade, name="privacidade"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("calendario/<int:year>/", views.calendar_year, name="calendar_year"),
    path("dia/<int:year>-<int:month>-<int:day>/", views.day_detail, name="day_detail"),
]
