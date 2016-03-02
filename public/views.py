from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from ipware.ip import get_ip
from public.analytics_api import get_flow, get_ga_service, GoogleApiException
from StringIO import StringIO
from traceback import print_exc

import logging

_LOG = logging.getLogger(__name__)

def index(request):
	return render(request, 'public/index.html', { 'ip': get_ip(request) })

def about(request):
	return render(request, 'public/about.html')

def install(request):
	flow =_get_flow(request, 'install_callback')
	return HttpResponseRedirect(flow.step1_get_authorize_url())

def install_callback(request):
	error = request.GET.get('error', None)
	if error == 'access_denied':
		return HttpResponseRedirect(reverse('public:access_required'))
	oauth_code = request.GET['code']
	flow =_get_flow(request, 'install_callback')
	credentials = flow.step2_exchange(oauth_code)
	request.session['oauth_credentials'] = credentials.to_json()
	redirect_url = reverse('public:install_select_accounts')
	return HttpResponseRedirect(redirect_url)

def access_required(request):
	return render(request, 'public/errors/access_required.html')

def install_select_accounts(request):
	service = _get_ga_service(request)
	accounts = service.get_accounts()
	if not accounts:
		return HttpResponseRedirect(reverse('public:no_account'))
	return render(request, 'public/select_accounts.html', {
		'accounts': accounts, 'ip': get_ip(request)
	})

def no_account(request):
	return render(request, 'public/errors/no_account.html')

def install_complete(request):
	account_ids = request.POST.getlist('accounts')
	installed, failed, failed_reasons = [], [], []
	with ThreadPoolExecutor(max_workers=3) as executor:
		futures = [
			executor.submit(_install_or_update_filter, request, account_id)
			for account_id in account_ids
		]
		for i, future in enumerate(as_completed(futures)):
			account_id = account_ids[i]
			try:
				future.result()
			except Exception as e:
				if isinstance(e, GoogleApiException):
					reason = e.reason
				else:
					reason = ''
				traceback = StringIO()
				print_exc(file=traceback)
				mail_admins(
					'Received exception installing filters',
					traceback.getvalue()
				)
				_LOG.exception('Received exception installing filters.')
				failed.append(account_id)
				failed_reasons.append(reason)
			else:
				installed.append(account_id)
	request.session['installed'] = installed
	request.session['failed'] = failed
	request.session['failed_reasons'] = failed_reasons
	return HttpResponse(reverse('public:install_success'))

def _install_or_update_filter(request, account_id):
	account = _get_ga_service(request).get_account(account_id)
	filters = account.get_filters()
	filters_with_name = [
		filter_ for filter_ in filters if filter_.name == _FILTER_NAME
	]
	args = (_FILTER_NAME, 'GEO_IP_ADDRESS', get_ip(request), 'GEO_IP_ADDRESS')
	if filters_with_name:
		for filter_ in filters_with_name:
			filter_.make_exclude_filter(*args)
	else:
		filter_ = account.create_exclude_filter(*args)
		for property_ in account.get_properties():
			for view in property_.get_views():
				view.apply_filter(filter_)

_FILTER_NAME = 'Home IP (via excludemyip.com)'

def install_success(request):
	service = _get_ga_service(request)
	get_accounts = lambda ids: [service.get_account(id) for id in ids]
	failed = get_accounts(request.session['failed'])
	failed_reasons = request.session['failed_reasons']
	return render(request, 'public/success.html', {
		'installed': get_accounts(request.session['installed']),
		'failed': zip(failed, failed_reasons)
	})

_FILTERS = (
	('Referral Spam 1 (via ASpamBlocker.com)', 'semalt|anticrawler|best-seo-offer|best-seo-solution|buttons-for-website|buttons-for-your-website|7makemoneyonline|-musicas*-gratis|kambasoft|savetubevideo|ranksonic|medispainstitute|offers.bycontext|100dollars-seo|sitevaluation|dailyrank'),
	('Referral Spam 2 (via ASpamBlocker.com)', 'videos-for-your-business|success-seo|rankscanner|doktoronline.no|adviceforum.info|video--production|sharemyfile.ru|seo-platform|justprofit.xyz|127.0.0.1|nexus.search-helper.ru|rankings-analytics.com|dbutton.net|o00.in|wordpress-crew.net'),
	('Referral Spam 3 (via ASpamBlocker.com)', 'fast-wordpress-start.com|top1-seo-service.com|^scripted.com|uptimechecker.com|uptimebot.net|rankings-analytics.com')
)

def _get_ga_service(request):
	return get_ga_service(request.session['oauth_credentials'])

def _get_flow(request, callback):
	callback_uri = request.build_absolute_uri(reverse('public:' + callback))
	return get_flow(callback_uri)