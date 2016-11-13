from django.conf.urls import url

from sample.views import authorize_at_core, auth_callback, index, landing, logout

urlpatterns = [
    # The admin urls and the standard index page url
    url(r'^landing', landing, name='landing'),
    url(r'^authorize_at_core/', authorize_at_core, name='authorize_at_core'),
    url(r'^auth_callback/', auth_callback, name='auth_callback'),
    url(r'^index/', index, name='index'),
    url(r'^logout/', logout, name='logout'),
]
