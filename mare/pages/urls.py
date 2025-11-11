from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("sobre/", views.sobre, name="sobre"),
    path("privacidade/", views.privacidade, name="privacidade"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("calendario/<int:year>/", views.calendar_year, name="calendar_year"),
    path("dia/<int:year>-<int:month>-<int:day>/", views.day_detail, name="day_detail"),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("pages/icones/favicon.ico"), permanent=True)),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
