from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^change_password/$', views.ChangePasswdView.as_view(), name='change_password'),
    url(r'^answer/$', views.AnswerView.as_view(), name='answer'),
    url(r'^approval/$', views.ApprovalView.as_view(), name='approval'),
    url(r'^approval/(?P<id>\d+)/$', views.ApprovalPassView.as_view(), name='approval_pass'),
]