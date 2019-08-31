"""
@file:   urls.py
@date:   2019/07/30
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^questions/$', views.QuestionsList.as_view(), name="questions"),
    url(r'^questions/(?P<id>\d+)/$', views.QuestionDetail.as_view(), name="question_detail"),
    url(r'^question/$', views.Question.as_view(), name="question"),
    url(r'^paginator/$', views.listing, name='paginator'),
]