from django.conf.urls import url

from home import views

urlpatterns = [
    url(r'^$', views.index, name='index_home'),
    url(r'^app.json$', views.timetable, name='timetable'),
    url(r'^glossary$', views.tv_series_list, name='tv_series_list'),
    url(r'^list$', views.list, name='list'),

    url(r'^requestadaptation$', views.requestAdaptation, name='requestadaptation'),

    url(r'linkGameRanking', views.linkGameRanking, name='linkGameRanking'),

    url(r'adaptationList$', views.adaptation_list, name='adaptation_list'),
    url(r'^adaptationform$', views.adaptation_form, name='adaptation_form'),
    url(r'^adaptationdetail/(?P<id>\d+)$', views.adaptation_detail, name='adaptation_detail'),
    url(r'^valid/(?P<id>\d+)$', views.valid, name='valid'),
    url(r'^adapted/(?P<id>\d+)$', views.adapted, name='adapted'),
    url(r'^delete/(?P<id>\d+)$', views.delete, name='delete'),

    url(r'^adaptationapi$', views.adaptationapi, name='adaptationapi'),

    url(r'^adaptlistapi$', views.adaptlistapi, name='adaptlistapi'),
    url(r'^adaptidlistapi$', views.adaptidlistapi, name='adaptlistapi'),

    url(r'^v2ray$', views.v2ray, name='v2ray'),

    url(r'^donate$', views.donate, name='donate'),

    url(r'^colorthemelist$', views.color_theme, name='colorthemelist'),
    url(r'^colorthemefunction$', views.color_theme_function, name='colorthemefunction'),

    url(r'^getcolor$', views.getColor, name='getcolor'),
    url(r'^sendemail$', views.sendEmail, name='sendemail'),
]
