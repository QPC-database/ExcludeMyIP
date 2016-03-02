from django.conf.urls import url
from public.views import index, install, install_callback, access_required, \
	no_account, install_select_accounts, install_complete, install_success, \
	about

urlpatterns = [
   url(r'^$', index, name='index'),
   url(r'^about/$', about, name='about'),
   url(r'^install/$', install, name='install'),
   url(r'^install/callback/$', install_callback, name='install_callback'),
   url(r'^install/access-required/$', access_required, name='access_required'),
   url(r'^install/no-account/$', no_account, name='no_account'),
   url(
	   r'^install/select-accounts/$', install_select_accounts,
	   name='install_select_accounts'
   ),
   url(r'^install/complete/$', install_complete, name='install_complete'),
   url(r'^install/success/$', install_success, name='install_success')
]