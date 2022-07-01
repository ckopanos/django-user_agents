from django.urls import path
from tests import views

urlpatterns = [
    path("", views.index, name="index"),
    path("template-tags", views.template_tags, name="template-tags"),
]
