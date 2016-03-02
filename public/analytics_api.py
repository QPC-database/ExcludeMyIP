from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client import client
from os.path import join, dirname, pardir

import httplib2
import json

_GOOGLE_API_CREDENTIALS = \
	join(dirname(__file__), pardir, 'conf', 'google_api_credentials.json')

def get_flow(callback_uri):
	flow = client.flow_from_clientsecrets(
		_GOOGLE_API_CREDENTIALS, redirect_uri=callback_uri.rstrip('/'),
		scope='https://www.googleapis.com/auth/analytics.edit'
	)
	return flow

def get_ga_service(oauth_credentials):
	credentials = client.OAuth2Credentials.from_json(oauth_credentials)
	http_auth = credentials.authorize(httplib2.Http())
	return GAService(build('analytics', 'v3', http=http_auth).management())

class GoogleApiException(Exception):
	def __init__(self, cause):
		self.cause = cause
	@property
	def reason(self):
		try:
			return self._data['error']['errors'][0]['reason']
		except (ValueError, KeyError, IndexError, TypeError):
			return ''
	@property
	def message(self):
		try:
			return self._data['error']['message']
		except (ValueError, KeyError, IndexError, TypeError):
			return ''
	@property
	def _data(self):
		return json.loads(self.cause.content.decode('utf-8'))
	def __str__(self):
		return str(self.cause)

class GAObject(object):
	def __init__(self, management):
		self.management = management
	def execute(self, command):
		try:
			return command.execute()
		except HttpError as e:
			raise GoogleApiException(e)
	def get_items(self, command):
		return self.execute(command).get('items')

class GAService(GAObject):
	def __init__(self, management):
		super(GAService, self).__init__(management)
		self._cached_accounts = None
	def get_account(self, account_id):
		accounts_by_id = { acct.id: acct for acct in self.get_accounts() }
		return accounts_by_id[account_id]
	def get_accounts(self):
		if self._cached_accounts is not None:
			return self._cached_accounts
		try:
			ga_accounts = self.get_items(self.management.accounts().list())
		except GoogleApiException as e:
			if e.message == u'User does not have any Google Analytics account.':
				ga_accounts = []
			else:
				raise
		result = [
			Account(self.management, account.get('id'), account.get('name'))
			for account in ga_accounts
		]
		self._cached_accounts = result
		return result

class Account(GAObject):
	def __init__(self, management, id_, name):
		super(Account, self).__init__(management)
		self.id = id_
		self.name = name
	def get_properties(self):
		ga_properties = self.get_items(
			self.management.webproperties().list(accountId=self.id)
		)
		return [
			WebProperty(self.management, self, prop.get('id'), prop.get('name'))
			for prop in ga_properties
		]
	def get_filters(self):
		ga_filters = self.get_items(
			self.management.filters().list(accountId=self.id)
		)
		return [
			Filter(self.management, self, filter_.get('id'), filter_.get('name'))
			for filter_ in ga_filters
		]
	def create_exclude_filter(self, name, field, expression, match_type):
		response = self.execute(self.management.filters().insert(
			accountId=self.id, body={
				'name': name, 'type': 'EXCLUDE',
				'excludeDetails': {
					'field': field, 'expressionValue': expression,
					'matchType': match_type, 'caseSensitive': False
				}
			}
		))
		return Filter(
			self.management, self, response.get('id'), response.get('name')
		)
	def __str__(self):
		return '%s(%s)' % (self.__class__.__name__, self.name)

class Filter(GAObject):
	def __init__(self, management, account, id_, name):
		super(Filter, self).__init__(management)
		self.account = account
		self.id = id_
		self.name = name
	def make_exclude_filter(self, name, field, expression, match_type):
		self.execute(self.management.filters().patch(
			accountId=self.account.id, filterId=self.id, body={
				'name': name, 'type': 'EXCLUDE',
				'excludeDetails': {
					'field': field, 'expressionValue': expression,
					'matchType': match_type, 'caseSensitive': False
				}
			}
		))
	def __str__(self):
		return '%s(%s)' % (self.__class__.__name__, self.name)

class WebProperty(GAObject):
	def __init__(self, management, account, id_, name):
		super(WebProperty, self).__init__(management)
		self.account = account
		self.id = id_
		self.name = name
	def get_views(self):
		ga_views = self.get_items(
			self.management.profiles()
				.list(accountId=self.account.id, webPropertyId=self.id)
		)
		return [
			View(self.management, self, view.get('id'), view.get('name'))
			for view in ga_views
		]
	def __str__(self):
		return '%s(%s in %s)' % (
			self.__class__.__name__, self.name, self.account.name
		)

class View(GAObject):
	def __init__(self, management, property_, id_, name):
		super(View, self).__init__(management)
		self.property = property_
		self.id = id_
		self.name = name
	def apply_filter(self, filter_):
		self.execute(self.management.profileFilterLinks().insert(
			accountId=self.property.account.id,
			webPropertyId=self.property.id,
			profileId=self.id,
			body={
				'filterRef': {
					'id': filter_.id
				}
			}
		))
	def __str__(self):
		return '%s(%s in %s)' % (
			self.__class__.__name__, self.name, self.property.name
		)