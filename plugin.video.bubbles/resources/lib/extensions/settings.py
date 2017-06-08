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

from resources.lib.extensions import tools
from resources.lib.extensions import interface
from resources.lib.extensions import debrid
from resources.lib.extensions import verification
from resources.lib.extensions import provider
from resources.lib.extensions import vpn
from resources.lib.extensions import speedtest
from resources.lib.modules import trakt

class Selection(object):

	##############################################################################
	# SHOW
	##############################################################################

	@classmethod
	def show(self):
		choice = interface.Dialog.option(title = 33011, message = 33929, labelConfirm = 33893, labelDeny = 33894)
		if choice: return Wizard.show()
		else: return Advanced.show()

class Advanced(object):

	##############################################################################
	# SHOW
	##############################################################################

	@classmethod
	def show(self, category = None, section = None):
		return tools.Settings.launch(category = category, section = section)

class Wizard(object):

	ChoiceLeft = True
	ChoiceRight = False

	OptionContinue = 'continue'
	OptionCancelStep = 'cancelstep'
	OptionCancelWizard = 'cancelwizard'

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		pass

	##############################################################################
	# SHOW
	##############################################################################

	@classmethod
	def _sleep(self, seconds):
		tools.Time.sleep(seconds)

	@classmethod
	def _option(self, message, left, right):
		return interface.Dialog.option(title = 33895, message = message, labelConfirm = left, labelDeny = right)

	@classmethod
	def _input(self, default = None):
		return interface.Dialog.input(title = 33895, type = interface.Dialog.InputAlphabetic, default = default)

	@classmethod
	def _cancel(self):
		choice = self._option(33975, 33976, 33977)
		if choice == self.ChoiceLeft: return self.OptionCancelWizard
		else: return self.OptionCancelStep

	@classmethod
	def _showWelcome(self, launch = False):
		'''choice = self._option(33930, 33342, 33341)
		if choice == self.ChoiceLeft: return self.OptionCancelWizard
		else: return self.OptionContinue'''

		if launch and not tools.Settings.getString('internal.launch.initial') == '':
			# NB: This should be removed in later versions.
			message = 'Welcome to Bubbles 2. Many things have changed in the new version which might cause compatibility issues with your current settings. It is highley recommended to completely clear your Bubbles settings to ensure that everything is working properly.'
			self._option(message, 33743, 33821)
			message = 'Do you want to continue clearing your old settings and files and start with a clean slate? This will clear your accounts, settings, providers, and metadata.'
			choice = self._option(message, 33342, 33341)
			if not choice:
				tools.System.clean(confirm = False)
				message = 'Your Bubbles installation is now clean and ready for a new configuration.'
				self._option(message, 33743, 33821)
			choice = self._option(33930, 33342, 33341)
			if choice == self.ChoiceLeft: return self.OptionCancelWizard
			else: return self.OptionContinue
		else:
			choice = self._option(33930, 33342, 33341)
			if choice == self.ChoiceLeft: return self.OptionCancelWizard
			else: return self.OptionContinue

	@classmethod
	def _showFinish(self):
		choice = self._option(33974, 33505, 33832)
		if choice == self.ChoiceLeft:
			# Do not use navigator().donationsNavigator().
			# This will not update Kodi's directory.
			tools.Donations.show()
		else:
			return self.OptionContinue

	@classmethod
	def _showLanguage(self):
		choice = self._option(33964, 33743, 33821)
		if choice == self.ChoiceLeft: return self._cancel()

		id = 'general.language.primary'
		language = tools.Settings.getString(id)
		language = interface.Translation.string(35046) if language == 'None' else language
		message = interface.Translation.string(35041) % language
		choice = self._option(message, 35045, 35044)
		if choice == self.ChoiceLeft:
			items = tools.Settings.raw(id, 'values').split('|')
			choice = interface.Dialog.select(title = 33895, items = items)
			if choice >= 0: tools.Settings.set(id, items[choice])

		id = 'general.language.secondary'
		language = tools.Settings.getString(id)
		language = interface.Translation.string(35046) if language == 'None' else language
		message = interface.Translation.string(35042) % language
		choice = self._option(message, 35045, 35044)
		if choice == self.ChoiceLeft:
			items = tools.Settings.raw(id, 'values').split('|')
			choice = interface.Dialog.select(title = 33895, items = items)
			if choice >= 0: tools.Settings.set(id, items[choice])

		id = 'general.language.tertiary'
		language = tools.Settings.getString(id)
		language = interface.Translation.string(35046) if language == 'None' else language
		message = interface.Translation.string(35043) % language
		choice = self._option(message, 35045, 35044)
		if choice == self.ChoiceLeft:
			items = tools.Settings.raw(id, 'values').split('|')
			choice = interface.Dialog.select(title = 33895, items = items)
			if choice >= 0: tools.Settings.set(id, items[choice])

	@classmethod
	def _showTrakt(self):
		choice = self._option(33931, 33897, 33898)
		if choice == self.ChoiceLeft: return self.OptionCancelStep
		choice = self._option(33932, 33899, 33900)
		if choice == self.ChoiceLeft:
			tools.System.openLink(tools.Settings.getString('link.trakt', raw = True))
			choice = self._option(33981, 33743, 33898)
			if choice == self.ChoiceLeft: return self._cancel()
		while True:
			tools.Settings.set('accounts.informants.trakt.enabled', True) # Has to be enabled before verification, since trakt.py uses it internally.
			authentication = trakt.authTrakt(openSettings = False)
			interface.Loader.show()
			# Kodi has a problem to set settings, and immediately read them afterwards. It always retruns the old value.
			# Instead, pass the new login information manually.
			valid = trakt.verify(authentication = authentication)
			interface.Loader.hide()
			if valid:
				choice = self._option(33933, 33743, 33821)
				if choice == self.ChoiceLeft: return self._cancel()
				return self.OptionContinue
			else:
				tools.Settings.set('accounts.informants.trakt.enabled', False)
				choice = self._option(33979, 33743, 33902)
				if choice == self.ChoiceLeft: return self._cancel()
		return self.OptionContinue

	@classmethod
	def _showFanart(self):
		choice = self._option(33934, 33897, 33898)
		if choice == self.ChoiceLeft: return self.OptionCancelStep
		choice = self._option(33935, 33899, 33900)
		if choice == self.ChoiceLeft:
			tools.System.openLink(tools.Settings.getString('link.fanart', raw = True))
			choice = self._option(33982, 33743, 33898)
			if choice == self.ChoiceLeft: return self._cancel()
		api = tools.Settings.getString('accounts.artwork.fanart.api')
		while True:
			choice = self._option(33936, 33743, 33901)
			if choice == self.ChoiceLeft: return self._cancel()
			api = self._input(default = api)
			interface.Loader.show()
			valid = verification.Verification()._verifyAccountsFanart(checkDisabled = False, key = api) == verification.Verification.StatusOperational
			interface.Loader.hide()
			if valid:
				tools.Settings.set('accounts.artwork.fanart.enabled', True)
				tools.Settings.set('accounts.artwork.fanart.api', api)
				choice = self._option(33938, 33743, 33821)
				if choice == self.ChoiceLeft: return self._cancel()
				return self.OptionContinue
			else:
				tools.Settings.set('accounts.artwork.fanart.enabled', False)
				choice = self._option(33980, 33743, 33902)
				if choice == self.ChoiceLeft: return self._cancel()
		return self.OptionContinue

	@classmethod
	def _showPremiumize(self):
		choice = self._option(33939, 33897, 33898)
		if choice == self.ChoiceLeft: return self.OptionCancelStep
		choice = self._option(33940, 33899, 33900)
		if choice == self.ChoiceLeft:
			tools.System.openLink(tools.Settings.getString('link.premiumize', raw = True))
			choice = self._option(33986, 33743, 33898)
			if choice == self.ChoiceLeft: return self._cancel()
		user = userOriginal = tools.Settings.getString('accounts.debrid.premiumize.user')
		pin = pinOriginal = tools.Settings.getString('accounts.debrid.premiumize.pin')
		while True:
			choice = self._option(33941, 33743, 33903)
			if choice == self.ChoiceLeft: return self._cancel()
			user = self._input(default = user)
			choice = self._option(33942, 33743, 33904)
			if choice == self.ChoiceLeft: return self._cancel()
			pin = self._input(default = pin)
			interface.Loader.show()
			tools.Settings.set('accounts.debrid.premiumize.enabled', True)
			tools.Settings.set('accounts.debrid.premiumize.user', user)
			tools.Settings.set('accounts.debrid.premiumize.pin', pin)
			valid = debrid.Premiumize().accountVerify()
			interface.Loader.hide()
			if valid:
				tools.Settings.set('providers.universal.premium.member.premiumize', True)
				choice = self._option(33944, 33743, 33821)
				if choice == self.ChoiceLeft: return self._cancel()
				return self.OptionContinue
			else:
				tools.Settings.set('accounts.debrid.premiumize.enabled', False)
				tools.Settings.set('accounts.debrid.premiumize.user', userOriginal)
				tools.Settings.set('accounts.debrid.premiumize.pin', pinOriginal)
				choice = self._option(33989, 33743, 33902)
				if choice == self.ChoiceLeft: return self._cancel()
		return self.OptionContinue

	@classmethod
	def _showRealDebrid(self):
		choice = self._option(33945, 33897, 33898)
		if choice == self.ChoiceLeft: return self.OptionCancelStep
		choice = self._option(33946, 33899, 33900)
		if choice == self.ChoiceLeft:
			tools.System.openLink(tools.Settings.getString('link.realdebrid', raw = True))
			choice = self._option(33987, 33743, 33898)
			if choice == self.ChoiceLeft: return self._cancel()
		while True:
			tools.Settings.set('accounts.debrid.realdebrid.enabled', True)
			debrid.RealDebridInterface().accountAuthentication(openSettings = False)
			interface.Loader.show()
			valid = debrid.RealDebrid().accountVerify()
			interface.Loader.hide()
			if valid:
				tools.Settings.set('providers.universal.premium.member.realdebrid', True)
				choice = self._option(33947, 33743, 33821)
				if choice == self.ChoiceLeft: return self._cancel()
				return self.OptionContinue
			else:
				tools.Settings.set('accounts.debrid.realdebrid.enabled', False)
				choice = self._option(33990, 33743, 33902)
				if choice == self.ChoiceLeft: return self._cancel()
		return self.OptionContinue

	@classmethod
	def _showEasyNews(self):
		choice = self._option(33948, 33897, 33898)
		if choice == self.ChoiceLeft: return self.OptionCancelStep
		choice = self._option(33949, 33899, 33900)
		if choice == self.ChoiceLeft:
			tools.System.openLink(tools.Settings.getString('link.easynews', raw = True))
			choice = self._option(33988, 33743, 33898)
			if choice == self.ChoiceLeft: return self._cancel()
		user = userOriginal = tools.Settings.getString('accounts.debrid.easynews.user')
		password = passwordOriginal = tools.Settings.getString('accounts.debrid.easynews.pass')
		while True:
			choice = self._option(33950, 33743, 33994)
			if choice == self.ChoiceLeft: return self._cancel()
			user = self._input(default = user)
			choice = self._option(33951, 33743, 33995)
			if choice == self.ChoiceLeft: return self._cancel()
			password = self._input(default = password)
			interface.Loader.show()
			tools.Settings.set('accounts.debrid.easynews.enabled', True)
			tools.Settings.set('accounts.debrid.easynews.user', user)
			tools.Settings.set('accounts.debrid.easynews.pass', password)
			valid = debrid.EasyNews().accountVerify()
			interface.Loader.hide()
			if valid:
				tools.Settings.set('providers.universal.premium.member.easynews', True)
				choice = self._option(33953, 33743, 33821)
				if choice == self.ChoiceLeft: return self._cancel()
				return self.OptionContinue
			else:
				tools.Settings.set('accounts.debrid.easynews.enabled', False)
				tools.Settings.set('accounts.debrid.easynews.user', userOriginal)
				tools.Settings.set('accounts.debrid.easynews.pass', passwordOriginal)
				choice = self._option(33991, 33743, 33902)
				if choice == self.ChoiceLeft: return self._cancel()
		return self.OptionContinue

	@classmethod
	def _showProviders(self):
		tools.Settings.set('providers.universal.local.open.enabled', True)
		tools.Settings.set('providers.universal.premium.member.enabled', True)

		tools.Settings.set('streaming.torrent.enabled', True)
		tools.Settings.set('streaming.torrent.premiumize.enabled', True)
		tools.Settings.set('streaming.torrent.realdebrid.enabled', True)
		tools.Settings.set('streaming.usenet.enabled', True)
		tools.Settings.set('streaming.usenet.premiumize.enabled', True)
		tools.Settings.set('streaming.hoster.enabled', True)
		tools.Settings.set('streaming.hoster.urlresolver.enabled', True)
		tools.Settings.set('streaming.hoster.premiumize.enabled', True)
		tools.Settings.set('streaming.hoster.realdebrid.enabled', True)
		tools.Settings.set('streaming.hoster.alldebrid.enabled', True)
		tools.Settings.set('streaming.hoster.rapidpremium.enabled', True)

		choice = self._option(33954, 33743, 33821)
		if choice == self.ChoiceLeft: return self._cancel()
		choice = self._option(33955, 33743, 33821)
		if choice == self.ChoiceLeft: return self._cancel()

		choice = self._option(33956, 33906, 33905)
		enable = choice == self.ChoiceRight
		for category in provider.Provider.Categories:
			try: tools.Settings.set('providers.%s.torrent.member.enabled' % category, enable)
			except: pass
			try: tools.Settings.set('providers.%s.torrent.open.enabled' % category, enable)
			except: pass

		choice = self._option(33957, 33908, 33907)
		enable = choice == self.ChoiceRight
		for category in provider.Provider.Categories:
			try: tools.Settings.set('providers.%s.usenet.member.enabled' % category, enable)
			except: pass
			try: tools.Settings.set('providers.%s.usenet.open.enabled' % category, enable)
			except: pass

		languages = [l[1].lower() for l in tools.Language.settings()]
		choice = self._option(33958, 33910, 33909)
		enable = choice == self.ChoiceRight
		for category in provider.Provider.Categories:
			if category == provider.Provider.CategoryUniversal or category in languages:
				try: tools.Settings.set('providers.%s.hoster.member.enabled' % category, enable)
				except: pass
				try: tools.Settings.set('providers.%s.hoster.open.enabled' % category, enable)
				except: pass

		return self.OptionContinue

	@classmethod
	def _showScraping(self):
		choice = self._option(33965, 33923, 33924)
		enable = choice == self.ChoiceRight
		tools.Settings.set('scraping.failure.enabled', enable)

		choice = self._option(33966, 33743, 33821)
		if choice == self.ChoiceLeft: return self._cancel()
		choice = self._option(33967, 33564, 33800)
		if choice == self.ChoiceRight:
			provider.Provider().optimization(title = 33895, introduction = False)

		return self.OptionContinue

	@classmethod
	def _showVpn(self):
		choice = self._option(33969, 33743, 33821)
		if choice == self.ChoiceLeft: return self._cancel()
		choice = self._option(33970, 33743, 33821)
		if choice == self.ChoiceLeft: return self._cancel()
		choice = self._option(33971, 33897, 33927)
		if choice == self.ChoiceLeft: return self.OptionCancelStep
		vpn.Vpn().configuration(settings = False, title = 33895, finish = 33821, introduction = False)
		return self.OptionContinue

	@classmethod
	def _showSpeedTest(self):
		choice = self._option(33972, 33743, 33821)
		if choice == self.ChoiceLeft: return self._cancel()
		choice = self._option(33973, 33897, 33928)
		if choice == self.ChoiceLeft: return self.OptionCancelStep
		speedtest.SpeedTesterGlobal().show()

	@classmethod
	def show(self, launch = False):
		if self._showWelcome(launch = launch) == self.OptionCancelWizard:
			return False

		if self._showLanguage() == self.OptionCancelWizard:
			return False
		if self._showTrakt() == self.OptionCancelWizard:
			return False
		if self._showFanart() == self.OptionCancelWizard:
			return False
		if self._showPremiumize() == self.OptionCancelWizard:
			return False
		if self._showRealDebrid() == self.OptionCancelWizard:
			return False
		if self._showEasyNews() == self.OptionCancelWizard:
			return False
		if self._showProviders() == self.OptionCancelWizard:
			return False
		if self._showScraping() == self.OptionCancelWizard:
			return False
		if self._showVpn() == self.OptionCancelWizard:
			return False
		if self._showSpeedTest() == self.OptionCancelWizard:
			return False

		self._showFinish()

	@classmethod
	def launchInitial(self):
		if not tools.Settings.getBoolean('internal.wizard.initialzed'):
			self.show(launch = True)
			tools.Settings.set('internal.wizard.initialzed', True)
