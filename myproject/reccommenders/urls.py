from django.conf.urls import url

from recommender import views

urlpatterns = [
    url(r'^chart/', views.chart, name='chart'),
   
    url(r'^sim/user/(?P<user_id>\w+)/(?P<sim_method>\w+)/$',
        views.similar_users, name='similar_users'),
    url(r'^cb/item/(?P<content_id>\w+)/$',
        views.similar_content, name='similar_content'),
    url(r'^cb/user/(?P<user_id>\w+)/$',
        views.recs_cb, name='recs_cb'),
    url(r'^cf/user/(?P<user_id>\w+)/$',
        views.recs_cf, name='recs_cb'),
    url(r'^funk/user/(?P<user_id>\w+)/$',
        views.recs_funksvd, name='recs_funksvd'),
   
    url(r'^bpr/user/(?P<user_id>\w+)/$',
        views.recs_bpr, name='recs_fwls'),
  
]