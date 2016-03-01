from django.conf.urls import url
from public.views import index

urlpatterns = [
	url(r'^$', index, name='index')
]