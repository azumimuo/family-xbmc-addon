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

import os
import sys
import imp
import json
import pkgutil
import urlparse
import time
import threading

from resources.lib.extensions import database

class Provider(object):

	DatabaseName = 'providers'
	DatabaseFailure = 'failure'

	# If enabled is false, retrieves all providers, even if they are disbaled in the settings.
	# If local is false, excludes local providers.
	# If object is true, it will create an instance of the class.

	Providers = []

	# Categories - must have the same value as the directory name
	CategoryUnknown = None
	CategoryUniversal = 'universal'
	CategoryEnglish = 'english'
	CategoryGerman = 'german'
	CategoryFrench = 'french'
	CategoryRussian = 'russian'
	CategoryPolish = 'polish'
	CategoryKorean = 'korean'
	Categories = [CategoryUniversal, CategoryEnglish, CategoryGerman, CategoryFrench, CategoryRussian, CategoryPolish, CategoryKorean]

	# Types - must have the same value as the directory name
	TypeUnknown = None
	TypeLocal = 'local'
	TypeDirect = 'direct'
	TypeTorrent = 'torrent'
	TypeUsenet = 'usenet'
	TypeHoster = 'hoster'

	# Modes - must have the same value as the directory name
	ModeUnknown = None
	ModeOpen = 'open'
	ModeMember = 'member'

	# Groups
	GroupUnknown = None
	GroupMovies = 'movies'
	GroupTvshows = 'tvshows'
	GroupAll = 'all'

	PerformanceSlow = 'slow'
	PerformanceMedium = 'medium'
	PerformanceFast = 'fast'

	@classmethod
	def __name(self, data, setting):
		name = ''
		if data:
			dummy = True
			index = 0
			setting = setting.lower()
			while dummy:
				index = data.find(setting, index)
				if index < 0: break
				dummy = 'visible="false"' in data[index : data.find('/>', index)]
				index += 1
			if dummy: index = -1

			if index >= 0:
				index = data.find('label="', index)
				if index >= 0:
					name = data[index + 7 : data.find('" ', index)]
					if name.isdigit():
						from resources.lib.extensions import interface
						name = interface.Translation.string(int(name))
		return name

	@classmethod
	def __domain(self, link):
		domain = urlparse.urlparse(link).netloc
		index = domain.rfind('.')
		if index >= 0:
			index = domain.rfind('.', 0, index)
			if index >= 0:
				return domain[index + 1:]
		return domain

	@classmethod
	def initialize(self):
		from resources.lib.extensions import tools
		try:
			self.Providers = []

			from resources.lib.extensions import handler
			handleDirect = handler.Handler(type = handler.Handler.TypeDirect)
			handleTorrent = handler.Handler(type = handler.Handler.TypeTorrent)
			handleUsenet = handler.Handler(type = handler.Handler.TypeUsenet)
			handleHoster = handler.Handler(type = handler.Handler.TypeHoster)

			failures = self.failureList()

			root = os.path.join(tools.System.path(), 'resources')
			data = tools.Settings.data()

			path1 = [os.path.join(root, 'lib', 'sources')]
			for package1, name1, pkg1 in pkgutil.walk_packages(path1):
				path2 = [os.path.join(path1[0], name1)]
				for package2, name2, pkg2 in pkgutil.walk_packages(path2):
					path3 = [os.path.join(path2[0], name2)]
					for package3, name3, pkg3 in pkgutil.walk_packages(path3):
						path4 = [os.path.join(path3[0], name3)]
						if tools.Settings.getBoolean('providers.%s.%s.%s.enabled' % (name1, name2, name3)): # Only those that are enabled. Drastically reduces provider initialization time.
							for package4, name4, pkg4 in pkgutil.walk_packages(path4):
								if not pkg4:
									try:
										type = name2

										try:
											if type == handler.Handler.TypeDirect:
												if not handleDirect.supported(): continue
											elif type == handler.Handler.TypeTorrent:
												if not handleTorrent.supported(): continue
											elif type == handler.Handler.TypeUsenet:
												if not handleUsenet.supported(): continue
											elif type == handler.Handler.TypeHoster:
												if not handleHoster.supported(): continue
										except: pass

										id = name4
										file = name4 + '.py'
										directory = path4[0]
										path = os.path.join(directory, file)

										classPointer = imp.load_source(id, path)
										object = classPointer.source()

										try: pack = object.pack
										except: pack = False

										setting = '.'.join(['providers', name1, type, name3, id])
										settingcategory = '.'.join(['providers', name1, type, name3, 'enabled'])
										enabled1 = tools.Settings.getBoolean(settingcategory)
										enabled2 = tools.Settings.getBoolean(setting)
										enabled3 = not id in failures

										try:
											functionMovie = getattr(object, 'movie', None)
											groupMovies = True if callable(functionMovie) else False
										except:
											groupMovies = False

										try:
											functionTvshow = getattr(object, 'tvshow', None)
											functionEpisode = getattr(object, 'episode', None)
											groupTvshows = True if callable(functionTvshow) or callable(functionEpisode) else False
										except:
											groupTvshows = False

										if groupMovies and groupTvshows: group = self.GroupAll
										elif groupMovies: group = self.GroupMovies
										elif groupTvshows: group = self.GroupTvshows
										else: group = self.GroupUnknown

										link = None
										domain = None
										links = []
										domains = []
										language = None
										languages = []

										if hasattr(object, 'domains') and isinstance(object.domains, (list, tuple)) and len(object.domains) > 0:
											domains = object.domains
											for i in range(len(domains)):
												if domains[i].startswith('http'):
													domains[i] = self.__domain(domains[i])

										if hasattr(object, 'language') and isinstance(object.language, (list, tuple)) and len(object.language) > 0:
											languages = object.language
											language = languages[0]

										if hasattr(object, 'base_link'):
											link = object.base_link
										if link == None and len(domains) > 0:
											link = domains[0]

										if not link == None:
											if not link.startswith('http'):
												link = 'http://' + link
											links.append(link)
											domain = self.__domain(link)
											domains.append(domain)

										for d in domains:
											if not d.startswith('http'):
												d = 'http://' + d
											links.append(d)
										if domain == None and len(domains) > 0:
											domain = domains[0]

										# Remove duplicates
										links = list(set(links))
										domains = list(set(domains))

										source = {}

										source['category'] = name1
										source['type'] = type
										source['mode'] = name3
										source['group'] = group

										source['link'] = link
										source['links'] = links
										source['domain'] = domain
										source['domains'] = domains

										source['language'] = language
										source['languages'] = languages

										source['id'] = id
										source['name'] = self.__name(data, setting)
										source['pack'] = pack
										source['setting'] = setting
										source['settingcategory'] = settingcategory
										source['selected'] = enabled1 and enabled2
										source['enabled'] = enabled1 and enabled2 and enabled3

										source['file'] = file
										source['directory'] = directory
										source['path'] = path

										source['class'] = classPointer
										source['object'] = object

										self.Providers.append(source)
									except Exception as error:
										tools.Logger.log('A provider could not be loaded (%s): %s.' % (str(name4), str(error)))
		except Exception as error:
			tools.Logger.log('The providers could not be loaded (%s).' % str(error))
		return self.Providers

	# description can be id, name, file, or setting.
	@classmethod
	def provider(self, description, enabled = True, local = True):
		description = description.lower().replace(' ', '') # Important for "local library".
		sources = self.providers(enabled = enabled, local = local)
		for source in sources:
			if source['id'] == description or source['name'] == description or source['setting'] == description or source['file'] == description:
				return source
		return None

	@classmethod
	def providers(self, enabled = True, local = True):
		# Extremley important. Only detect providers the first time.
		# If the providers are searched every time, this creates a major overhead and slow-down during the prechecks: sources.sourcesResolve() through the networker.
		if len(self.Providers) <= 0:
			self.initialize()

		sources = []
		for i in range(len(self.Providers)):
			source = self.Providers[i]
			if enabled and not source['enabled']:
				continue
			if not local and source['type'] == self.TypeLocal:
				continue
			sources.append(source)

		return sources

	@classmethod
	def providersMovies(self, enabled = True, local = True):
		sources = self.providers(enabled = enabled, local = local)
		return [i for i in sources if i['group'] == self.GroupMovies or i['group'] == self.GroupAll]

	@classmethod
	def providersTvshows(self, enabled = True, local = True):
		sources = self.providers(enabled = enabled, local = local)
		return [i for i in sources if i['group'] == self.GroupTvshows or i['group'] == self.GroupAll]

	@classmethod
	def providersAll(self, enabled = True, local = True):
		sources = self.providers(enabled = enabled, local = local)
		return [i for i in sources if i['group'] == self.GroupAll]

	@classmethod
	def providersTorrent(self, enabled = True):
		sources = self.providers(enabled = enabled)
		return [i for i in sources if i['type'] == self.TypeTorrent]

	@classmethod
	def providersUsenet(self, enabled = True):
		sources = self.providers(enabled = enabled)
		return [i for i in sources if i['type'] == self.TypeUsenet]

	@classmethod
	def providersHoster(self, enabled = True):
		sources = self.providers(enabled = enabled)
		return [i for i in sources if i['type'] == self.TypeHoster]

	@classmethod
	def names(self, enabled = True, local = True):
		sources = self.providers(enabled = enabled, local = local)
		return [i['name'] for i in sources]

	@classmethod
	def _failureInitialize(self):
		data = database.Database(name = self.DatabaseName)
		data._create('CREATE TABLE IF NOT EXISTS %s (id TEXT, count INTEGER, time INTEGER, UNIQUE(id));' % self.DatabaseFailure)
		return data

	@classmethod
	def failureClear(self):
		database.Database(name = self.DatabaseName)._drop(self.DatabaseFailure)

	@classmethod
	def failureEnabled(self):
		from resources.lib.extensions import tools
		return tools.Settings.getBoolean('scraping.failure.enabled')

	@classmethod
	def failureList(self):
		result = []
		if self.failureEnabled():
			from resources.lib.extensions import tools

			thresholdCount = tools.Settings.getInteger('scraping.failure.count')
			thresholdTime = tools.Settings.getInteger('scraping.failure.time')
			if thresholdTime > 0:
				thresholdTime = thresholdTime * 86400 # Convert to seconds.
				thresholdTime = tools.Time.timestamp() - thresholdTime

			data = self._failureInitialize()
			result = data._selectValues('SELECT id FROM %s WHERE NOT (count < %d OR time < %d);' % (self.DatabaseFailure, thresholdCount, thresholdTime))
		return result

	@classmethod
	def failureUpdate(self, finished, unfinished):
		if self.failureEnabled():
			from resources.lib.extensions import tools

			data = self._failureInitialize()
			current = data._selectValues('SELECT id FROM %s;' % self.DatabaseFailure)
			timestamp = tools.Time.timestamp()

			for id in finished:
				if id in current:
					data._update('UPDATE %s SET count = 0, time = %d WHERE id = "%s";' % (self.DatabaseFailure, timestamp, id), commit = False)
				else:
					data._insert('INSERT INTO %s (id, count, time) VALUES ("%s", 0, %d);' % (self.DatabaseFailure, id, timestamp), commit = False)

			for id in unfinished:
				if id in current:
					data._update('UPDATE %s SET count = count + 1, time = %d WHERE id = "%s";' % (self.DatabaseFailure, timestamp, id), commit = False)
				else:
					data._insert('INSERT INTO %s (id, count, time) VALUES ("%s", 1, %d);' % (self.DatabaseFailure, id, timestamp), commit = False)

			data._commit()

	# mode: manual or automatic
	@classmethod
	def sortDialog(self, mode, slot):
		from resources.lib.extensions import tools
		from resources.lib.extensions import interface

		interface.Loader.show()
		providers = self.providers(enabled = True, local = False)
		items = [interface.Format.fontBold(33112)]
		items += [i['name'] for i in providers]
		interface.Loader.hide()

		index = interface.Dialog.options(title = 33196, items = items)
		if index < 0: return False
		elif index == 0: provider = ''
		else: provider = items[index]

		id = 'playback.%s.sort.provider%d' % (mode, int(slot))
		tools.Settings.set(id = id, value = provider)

		slot = tools.Settings.CategoryManual if mode == 'manual' else tools.Settings.CategoryAutomation
		tools.Settings.launch(slot)

		return True

	@classmethod
	def presetDialog(self, slot):
		from resources.lib.extensions import tools
		from resources.lib.extensions import interface

		slot = int(slot)
		slotValues = 'providers.presets.values%d' % slot
		slotPreset = 'providers.presets.preset%d' % slot

		current = tools.Settings.getString(slotValues).decode('base64')
		if not current == None and not current == '':
			option = interface.Dialog.option(title = 33682, message = 33684, labelConfirm = 33686, labelDeny = 33685)
		else:
			option = True

		if option:
			name = tools.Settings.getString(slotPreset)
			if not name == None and not name == '':
				index = name.find(' (')
				if index >= 0:
					name = name[:index]
			interface.Loader.hide()
			name = interface.Dialog.input(title = 33687, type = interface.Dialog.InputAlphabetic, default = name)
			if name == None or name == '':
				tools.Settings.set(slotValues, '')
				tools.Settings.set(slotPreset, '')
				interface.Dialog.notification(title = 33692, message = 33689, icon = interface.Dialog.IconSuccess)
				tools.Settings.launch(category = tools.Settings.CategoryProviders)
				interface.Loader.hide()
				return False
			interface.Loader.show()

		interface.Loader.show()
		providers = self.providers(enabled = False, local = True)
		categories = list(set([i['settingcategory'] for i in providers]))

		if option:
			items = []
			for i in providers:
				if i['selected']:
					items.append(i['setting'])

			name = '%s (%d)' % (name, len(items))
			tools.Settings.set(slotPreset, name)

			categoriesSelected = [i for i in categories if tools.Settings.getBoolean(i)]
			items = {'categories' : categoriesSelected, 'providers' : items}
			items = json.dumps(items)

			# Encode it to base64, since the quotes and brackets in the JSON intefer with the settings XML, causing weird problems when Kodi reads the settings.
			# Remove new lines, since base64 encoding adds new lines: http://stackoverflow.com/questions/30647219/remove-the-new-line-n-from-base64-encoded-strings-in-python3
			items = items.encode('base64').replace('\n', '')

			tools.Settings.set(slotValues, items)

			interface.Dialog.notification(title = 33692, message = 33688, icon = interface.Dialog.IconSuccess)
		else:
			for i in categories: tools.Settings.set(i, False)
			for i in providers: tools.Settings.set(i['setting'], False)

			current = json.loads(current)
			currentCategories = current['categories']
			currentProviders = current['providers']
			for i in currentCategories: tools.Settings.set(i, True)
			for i in currentProviders: tools.Settings.set(i, True)

			interface.Dialog.notification(title = 33692, message = 33690, icon = interface.Dialog.IconSuccess)

		tools.Settings.launch(category = tools.Settings.CategoryProviders)
		interface.Loader.hide()

		return True

	@classmethod
	def language(self):
		from resources.lib.extensions import tools
		if tools.Language.customization():
			language = tools.Settings.getString('scraping.foreign.language')
		else:
			language = tools.Language.Alternative
		return tools.Language.code(language)

	@classmethod
	def languageSelect(self):
		from resources.lib.extensions import tools
		from resources.lib.extensions import interface
		id = 'scraping.foreign.language'
		items = tools.Settings.raw(id, 'values').split('|')
		choice = interface.Dialog.select(title = 33787, items = items)
		if choice >= 0: tools.Settings.set(id, items[choice])

	@classmethod
	def _optimizationPerformance(self, performance):
		from resources.lib.extensions import interface
		if performance == self.PerformanceSlow: return interface.Translation.string(33997)
		elif performance == self.PerformanceFast: return interface.Translation.string(33998)
		else: return interface.Translation.string(33999)

	@classmethod
	def optimizationDevice(self):
		from resources.lib.extensions import tools
		from resources.lib.extensions import interface
		from resources.lib.extensions import convert
		try:
			hardware = tools.Hardware.performance()
			hardwareProcessors = tools.Hardware.processors()
			hardwareMemory = tools.Hardware.memory()
			hardwareMemory = convert.ConverterSize(value = hardwareMemory).stringOptimal()

			labels = []
			label = self._optimizationPerformance(hardware)
			if hardwareProcessors: labels.append(str(hardwareProcessors) + ' ' + interface.Translation.string(35003))
			if hardwareMemory: labels.append(str(hardwareMemory) + ' ' + interface.Translation.string(35004))
			if len(labels) > 0: label += ' (%s)' % (', '.join(labels))

			if hardware == tools.Hardware.PerformanceFast: timeout = 10
			elif hardware == tools.Hardware.PerformanceMedium: timeout = 15
			else: timeout = 20

			return (timeout, label)
		except:
			tools.Logger.error()
			return (10, interface.Translation.string(33387))

	@classmethod
	def optimizationConnection(self, iterations = 3):
		from resources.lib.extensions import tools
		from resources.lib.extensions import interface
		from resources.lib.extensions import speedtest
		try:
			minimum = 0
			maximum = 9999999999
			latency = maximum
			download = minimum
			latencyLabel = None
			downloadLabel = None

			for i in range(iterations):
				speedtester = speedtest.SpeedTesterGlobal()
				speedtester.performance()
				if speedtester.latency() < latency:
					latency = speedtester.latency()
				if speedtester.download() > download:
					download = speedtester.download()

			if latency == maximum: latency = None
			if download == minimum: download = None
			speedtester = speedtest.SpeedTesterGlobal()
			speedtester.latencySet(latency)
			speedtester.downloadSet(download)
			performance = speedtester.performance(test = False)

			labels = []
			label = self._optimizationPerformance(performance)
			download = speedtester.formatDownload(unknown = None)
			latency = speedtester.formatLatency(unknown = None)
			if download: labels.append(download)
			if latency: labels.append(latency)
			if len(labels) > 0: label += ' (%s)' % (', '.join(labels))

			if performance == speedtest.SpeedTester.PerformanceFast: timeout = 10
			elif performance == speedtest.SpeedTester.PerformanceMedium: timeout = 15
			else: timeout = 20

			return (timeout, label)
		except:
			tools.Logger.error()
			return (10, interface.Translation.string(33387))

	@classmethod
	def optimizationProviders(self):
		from resources.lib.extensions import tools
		from resources.lib.extensions import interface
		try:
			providersMovies = len(self.providersMovies(enabled = True, local = False))
			providersTvshows = len(self.providersTvshows(enabled = True, local = False))
			providers = max(providersMovies, providersTvshows)

			label = '%s (' + str(providers) + ' ' + interface.Translation.string(32301) + ')'
			if providers <= 10:
				timeout = 10
				label = label % interface.Translation.string(35000)
			elif providers <= 20:
				timeout = 15
				label = label % interface.Translation.string(35001)
			elif providers <= 30:
				timeout = 20
				label = label % interface.Translation.string(35001)
			elif providers <= 40:
				timeout = 25
				label = label % interface.Translation.string(35002)
			else:
				timeout = 30
				label = label % interface.Translation.string(35002)

			return (timeout, label)
		except:
			tools.Logger.error()
			return (10, interface.Translation.string(33387))

	@classmethod
	def optimizationForeign(self):
		from resources.lib.extensions import tools
		from resources.lib.extensions import interface
		try:
			timeout = 0

			if self.language() == tools.Language.EnglishCode:
				timeout = 0
				label = interface.Translation.string(33342)
			else:
				timeout = 15
				label = interface.Translation.string(33341)

			return (timeout, label)
		except:
			tools.Logger.error()
			return (10, interface.Translation.string(33387))

	# Cannot be static, since it uses a member variable
	def optimization(self, title = 33996, introduction = True, settings = False):
		try:
			from resources.lib.extensions import tools
			from resources.lib.extensions import interface

			if introduction:
				choice = interface.Dialog.option(title = title, message = 35005)
				if not choice:
					if settings: tools.Settings.launch(tools.Settings.CategoryScraping)
					return False

			dialog = interface.Dialog.progress(title = title, message = 35006)
			dots = ''

			self.resultTimeout = 0
			self.resultLabels = []
			resultNames = [35012, 33404, 32345, 35013]
			def results(function):
				result = function()
				self.resultTimeout += result[0]
				self.resultLabels.append(result[1])

			index = 0
			thread = None
			label = None
			functions = [self.optimizationDevice, self.optimizationConnection, self.optimizationProviders, self.optimizationForeign]
			labels = [35007, 35008, 35009, 35010]
			message = interface.Translation.string(35006)

			while True:
				# NB: Do not check for abort here. This will cause the speedtest to close automatically in the configuration wizard.
				if dialog.iscanceled():
					if settings: tools.Settings.launch(tools.Settings.CategoryScraping)
					return False

				if thread == None or not thread.is_alive():
					if index >= len(functions): break
					thread = threading.Thread(target = results, args = (functions[index],))
					thread.start()
					label = interface.Translation.string(labels[index])
					index += 1

				progress = int(((index - 1) / float(len(functions))) * 100)
				dialog.update(progress, message, '     %s %s' % (label, dots))

				dots += '.'
				if len(dots) > 3: dots = ''
				time.sleep(0.5)

			message = interface.Translation.string(35011) % self.resultTimeout
			for i in range(len(self.resultLabels)):
				message += '%s     %s: %s' % (interface.Format.newline(), interface.Translation.string(resultNames[i]), self.resultLabels[i])
			message += interface.Format.newline() + interface.Translation.string(33968)

			dialog.close()
			choice = interface.Dialog.option(title = title, message = message, labelDeny = 33926, labelConfirm = 33925)
			if choice:
				self.resultTimeout = int(interface.Dialog.input(title = title, type = interface.Dialog.InputNumeric, default = str(self.resultTimeout)))
				if self.resultTimeout < 5: self.resultTimeout = 5
				elif self.resultTimeout > 300: self.resultTimeout = 300

			tools.Settings.set('scraping.providers.timeout', self.resultTimeout)
			if settings: tools.Settings.launch(tools.Settings.CategoryScraping)
			return True
		except:
			tools.Logger.error()
