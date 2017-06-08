# -*- coding: utf-8 -*-

'''
	Bubbles Add-on
	Copyright (C) 2016 Bubbles, Exodus

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


import os,sys,urlparse,urllib,json,re

from resources.lib.modules import control
from resources.lib.modules import trakt
from resources.lib.modules import views
from resources.lib.extensions import tools
from resources.lib.extensions import search
from resources.lib.extensions import interface
from resources.lib.extensions import downloader
from resources.lib.extensions import debrid
from resources.lib.extensions import handler
from resources.lib.extensions import torrent
from resources.lib.extensions import speedtest
from resources.lib.extensions import metadata as metadatax
from resources.lib.extensions import history as historyx

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

addonFanart = control.addonFanart()

traktIndicators = trakt.getTraktIndicatorsInfo()

queueMenu = control.lang(32065).encode('utf-8')


class navigator:

	def __init__(self, type = tools.Media.TypeNone, kids = tools.Selection.TypeUndefined):
		self.type = type
		self.kids = kids

	def parameterize(self, action, type = None, kids = None, lite = None):
		if type == None: type = self.type
		if not type == None: action += '&type=%s' % type

		if kids == None: kids = self.kids
		if not kids == None: action += '&kids=%d' % kids

		if not lite == None: action += '&lite=%d' % lite

		return action

	def kidsOnly(self):
		return self.kids == tools.Selection.TypeInclude

	def root(self):
		if self.kidsRedirect(): return

		if tools.Settings.getBoolean('interface.menu.movies'):
			self.addDirectoryItem(32001, self.parameterize('movieNavigator', type = tools.Media.TypeMovie), 'movies.png', 'DefaultMovies.png')
		if tools.Settings.getBoolean('interface.menu.shows'):
			self.addDirectoryItem(32002, self.parameterize('tvNavigator', type = tools.Media.TypeShow), 'tvshows.png', 'DefaultTVShows.png')
		if tools.Settings.getBoolean('interface.menu.documentaries'):
			self.addDirectoryItem(33470, self.parameterize('documentariesNavigator', type = tools.Media.TypeDocumentary), 'documentaries.png', 'DefaultVideo.png')
		if tools.Settings.getBoolean('interface.menu.shorts'):
			self.addDirectoryItem(33471, self.parameterize('shortsNavigator', type = tools.Media.TypeShort), 'shorts.png', 'DefaultVideo.png')
		if tools.Settings.getBoolean('interface.menu.kids'):
			self.addDirectoryItem(33429, self.parameterize('kidsNavigator', kids = tools.Selection.TypeInclude), 'kids.png', 'DefaultVideo.png')

		if tools.Settings.getBoolean('interface.menu.favourites'):
			self.addDirectoryItem(33000, 'favouritesNavigator', 'favourites.png', 'DefaultFavourite.png')
		if tools.Settings.getBoolean('interface.menu.arrivals'):
			self.addDirectoryItem(33490, self.parameterize('arrivalsNavigator'), 'new.png', 'DefaultAddSource.png')
		if tools.Settings.getBoolean('interface.menu.search'):
			self.addDirectoryItem(32010, 'searchNavigator', 'search.png', 'DefaultAddonsSearch.png')

		self.addDirectoryItem(32008, 'toolsNavigator', 'tools.png', 'DefaultAddonProgram.png')

		self.endDirectory()
		interface.traktApi()


	def movies(self, lite = False):

		if not self.kidsOnly() and lite == False:
			self.addDirectoryItem(33000, self.parameterize('movieFavouritesNavigator', lite = True), 'favourites.png', 'DefaultFavourite.png')
		self.addDirectoryItem(33490, self.parameterize('movieArrivals'), 'new.png', 'DefaultAddSource.png')

		self.addDirectoryItem(33001, self.parameterize('moviesCategories'), 'categories.png', 'DefaultTags.png')
		self.addDirectoryItem(33002, self.parameterize('moviesLists'), 'lists.png', 'DefaultVideoPlaylists.png')

		self.addDirectoryItem(32013, self.parameterize('moviesPeople'), 'people.png', 'DefaultActor.png')

		if lite == False:
			self.addDirectoryItem(32010, self.parameterize('moviesSearchNavigator'), 'search.png', 'DefaultAddonsSearch.png')

		self.endDirectory()
		torrent.torrentSt()


	def movieFavourites(self, lite = False):

		self.addDirectoryItem(32315, self.parameterize('traktmoviesNavigator'), 'trakt.png', 'DefaultAddonWebSkin.png')
		self.addDirectoryItem(32034, self.parameterize('imdbmoviesNavigator'), 'imdb.png', 'DefaultAddonWebSkin.png')

		self.addDirectoryItem(32036, self.parameterize('historyNavigator'), 'history.png', 'DefaultYear.png')

		if lite == False:
			self.addDirectoryItem(32031, self.parameterize('movieNavigator', lite = True), 'discover.png', 'DefaultMovies.png')

		self.endDirectory()


	def tvshows(self, lite = False):

		if not self.kidsOnly() and lite == False:
			self.addDirectoryItem(33000, self.parameterize('tvFavouritesNavigator', lite = True), 'favourites.png', 'DefaultFavourite.png')
		self.addDirectoryItem(33490, self.parameterize('tvArrivals'), 'new.png', 'DefaultAddSource.png')

		self.addDirectoryItem(33001, self.parameterize('tvCategories'), 'categories.png', 'DefaultTags.png')
		self.addDirectoryItem(33002, self.parameterize('tvLists'), 'lists.png', 'DefaultVideoPlaylists.png')

		self.addDirectoryItem(32013, self.parameterize('tvPeople'), 'people.png', 'DefaultTags.png')

		if lite == False:
			self.addDirectoryItem(32010, self.parameterize('tvSearchNavigator'), 'search.png', 'DefaultAddonsSearch.png')

		self.endDirectory()
		torrent.torrentSt()


	def tvFavourites(self, lite = False):

		self.addDirectoryItem(32315, self.parameterize('trakttvNavigator'), 'trakt.png', 'DefaultAddonWebSkin.png')
		self.addDirectoryItem(32034, self.parameterize('imdbtvNavigator'), 'imdb.png', 'DefaultAddonWebSkin.png')

		if not self.kidsOnly(): # Calendar does not have rating, so do not show for kids.
			self.addDirectoryItem(32027, self.parameterize('tvCalendars'), 'calendar.png', 'DefaultYear.png')

		self.addDirectoryItem(32036, self.parameterize('historyNavigator'), 'history.png', 'DefaultYear.png')

		if lite == False:
			self.addDirectoryItem(32031, self.parameterize('tvNavigator', lite = True), 'discover.png', 'DefaultTVShows.png')

		self.endDirectory()


	def tools(self):
		self.addDirectoryItem(33011, 'settings', 'settings.png', 'DefaultAddonProgram.png')

		self.addDirectoryItem(33502, 'servicesNavigator', 'services.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(32009, 'downloads', 'downloads.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33719, 'networkNavigator', 'network.png', 'DefaultAddonProgram.png')

		self.addDirectoryItem(33014, 'providersNavigator', 'provider.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(32346, 'accountsNavigator', 'account.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33017, 'verificationNavigator', 'verification.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33720, 'extensionsNavigator', 'extensions.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33406, 'lightpackNavigator', 'lightpack.png', 'DefaultAddonProgram.png')

		self.addDirectoryItem(33773, 'backupNavigator', 'backup.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33012, 'viewsNavigator', 'views.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33013, 'clearNavigator', 'clear.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33467, 'systemNavigator', 'system.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33344, 'informationNavigator', 'information.png', 'DefaultAddonProgram.png')

		self.addDirectoryItem(interface.Format.color(33505, 'FFB700'), 'donationsNavigator', 'donations.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)

		self.endDirectory()
		torrent.torrentSt()

	def historyNavigator(self):
		self.addDirectoryItem(33481, self.parameterize('historyStream', type = self.type), 'historystreams.png', 'DefaultYear.png')
		if self.type in [None, tools.Media.TypeMovie]:
			self.addDirectoryItem(32001, self.parameterize('historyType', type = tools.Media.TypeMovie), 'historymovies.png', 'DefaultYear.png')
		if self.type in [None, tools.Media.TypeDocumentary]:
			self.addDirectoryItem(33470, self.parameterize('historyType', type = tools.Media.TypeDocumentary), 'historydocumentaries.png', 'DefaultYear.png')
		if self.type in [None, tools.Media.TypeShort]:
			self.addDirectoryItem(33471, self.parameterize('historyType', type = tools.Media.TypeShort), 'historyshorts.png', 'DefaultYear.png')
		if self.type in [None, tools.Media.TypeShow, tools.Media.TypeSeason, tools.Media.TypeEpisode]:
			self.addDirectoryItem(32002, self.parameterize('historyType', type = tools.Media.TypeShow), 'historytvshows.png', 'DefaultYear.png')
			self.addDirectoryItem(32054, self.parameterize('historyType', type = tools.Media.TypeSeason), 'historytvshows.png', 'DefaultYear.png')
			self.addDirectoryItem(32326, self.parameterize('historyType', type = tools.Media.TypeEpisode), 'historytvshows.png', 'DefaultYear.png')
		self.endDirectory()

	def historyType(self):
		items = []
		ids = []

		type = self.type
		if type in [tools.Media.TypeSeason, tools.Media.TypeEpisode]:
			type = tools.Media.TypeShow
		histories = historyx.History().retrieve(type = type, kids = self.kids)

		for history in histories:
			metadata = tools.Converter.dictionary(history[4])
			id = str(metadata['imdb'])
			if not id in ids:
				items.append(metadata)
				ids.append(id)

		for i in range(len(items)):
			if 'duration' in items[i]:
				try: items[i]['duration'] = int(int(items[i]['duration']) / 60.0)
				except: pass

		if self.type in [tools.Media.TypeMovie, tools.Media.TypeDocumentary, tools.Media.TypeShort]:
			from resources.lib.indexers import movies
			movies.movies(type = self.type, kids = self.kids).movieDirectory(items = items, next = False)
		elif self.type in [tools.Media.TypeShow]:
			for i in range(len(items)):
				items[i]['title'] = items[i]['tvshowtitle']
				items[i]['rating'] = None # Episode rating, not show's rating.
				items[i]['duration'] = None
			from resources.lib.indexers import tvshows
			tvshows.tvshows(kids = self.kids).tvshowDirectory(items = items, next = False)
		elif self.type in [tools.Media.TypeSeason]:
			for i in range(len(items)):
				items[i]['title'] = items[i]['tvshowtitle']
				items[i]['rating'] = None # Episode rating, not season's rating.
				items[i]['duration'] = None
				if 'poster' in items[i]: items[i]['thumb'] = items[i]['poster']
			from resources.lib.indexers import seasons
			seasons.seasons(kids = self.kids).seasonDirectory(items = items)
		if self.type in [tools.Media.TypeEpisode]:
			from resources.lib.indexers import episodes
			episodes.episodes(type = self.type, kids = self.kids).episodeDirectory(items = items)

	def historyStream(self):
		media = tools.Media()
		histories = historyx.History().retrieve(type = self.type, kids = self.kids)
		for history in histories:
			type = history[0]
			kids = history[1]
			time = history[2]
			link = history[3]
			metadata = tools.Converter.dictionary(history[4])
			item = tools.Converter.dictionary(history[5])
			if isinstance(item, list):
				item = item[0]

			if type == tools.Media.TypeMovie:
				icon = 'historymovies.png'
			elif type == tools.Media.TypeShow:
				icon = 'historytvshows.png'
			elif type == tools.Media.TypeDocumentary:
				icon = 'historydocumentaries.png'
			elif type == tools.Media.TypeShort:
				icon = 'historyshorts.png'
			else:
				continue

			manualEnabled = downloader.Downloader(downloader.Downloader.TypeManual).enabled(notification = False, full = True)
			cacheEnabled = downloader.Downloader(downloader.Downloader.TypeCache).enabled(notification = False, full = True)

			sysmeta = urllib.quote_plus(json.dumps(metadata))

			poster = metadata['poster'] if 'poster' in metadata else metadata['poster2'] if 'poster2' in metadata else metadata['poster3'] if 'poster3' in metadata else '0'
			fanart = metadata['fanart'] if 'fanart' in metadata else metadata['fanart2'] if 'fanart2' in metadata else metadata['fanart3'] if 'fanart3' in metadata else '0'
			banner = metadata['banner'] if 'banner' in metadata else '0'
			thumb = metadata['thumb'] if 'thumb' in metadata else poster

			if poster == '0': poster = control.addonPoster()
			if banner == '0' and poster == '0': banner = control.addonBanner()
			elif banner == '0': banner = poster
			if thumb == '0' and fanart == '0': thumb = control.addonFanart()
			elif thumb == '0': thumb = fanart
			if control.setting('interface.fanart') == 'true' and not fanart == '0': pass
			else: fanart = control.addonFanart()

			sysimage = urllib.quote_plus(poster.encode('utf-8'))

			try:
				item['information'] = metadata # Used by Quasar. Do not use the name 'metadata', since that is checked in sourcesResolve().

				syssource = urllib.quote_plus(json.dumps([item]))
				local = 'local' in item and item['local']
				if not local and tools.Settings.getBoolean('downloads.cache.enabled'):
					sysurl = '%s?action=cacheItem&handleMode=%s&source=%s&metadata=%s' % (sysaddon, handler.Handler.ModeDefault, syssource, sysmeta)
				else:
					sysurl = '%s?action=playItem&handleMode=%s&source=%s&metadata=%s' % (sysaddon, handler.Handler.ModeDefault, syssource, sysmeta)
				sysurl = self.parameterize(sysurl, type = type, kids = kids)

				# ITEM

				title = tools.Media.titleUniversal(metadata = metadata)
				meta = metadatax.Metadata(title = title, name = item['file'] if 'file' in item else None, source = item)

				labelTop = title
				labelBottom = meta.information(format = True, information = metadatax.Metadata.InformationEssential)

				provider = item['provider']
				if not provider == None and not provider == '':
					labelBottom += interface.Format.separator() + provider.upper()
				else:
					source = item['source']
					if not source == None and not source == '':
						labelBottom += interface.Format.separator() + source.upper()

				# Spaces needed, otherwise the second line is cut off when shorter than the first line
				spaceTop = 0
				spaceBottom = 0
				lengthTop = len(re.sub('\\[(.*?)\\]', '', labelTop))
				lengthBottom = len(re.sub('\\[(.*?)\\]', '', labelBottom))
				if lengthBottom > lengthTop:
					spaceTop = int((lengthBottom - lengthTop) * 3) # Try with Confluence.
				else:
					spaceBottom = int((lengthBottom - lengthTop) * 3) # Try with Confluence.
				spaceTop = ' ' * max(7, spaceTop)
				spaceBottom = ' ' * max(7, spaceBottom)
				label = labelTop + spaceTop + interface.Format.fontNewline() + labelBottom + spaceBottom

				listItem = control.item(label = label)

				listItem.setArt({'icon': thumb, 'thumb': thumb, 'poster': poster, 'banner': banner})
				if not fanart == None: listItem.setProperty('Fanart_Image', fanart)

				listItem.setInfo(type = 'Video', infoLabels = metadata)
				if 'info' in item:
					width, height = meta.videoQuality(True)
					listItem.addStreamInfo('video', {'codec': meta.videoCodec(True), 'width' : width, 'height': height})
					listItem.addStreamInfo('audio', {'codec': meta.audioCodec(True), 'channels': meta.audioChannels(True)})

				# CONTEXT MENU

				contextMenu = []
				contextWith = handler.Handler(item['source']).supportedCount(item) > 1

				contextLabel = interface.Translation.string(33379)
				contextCommand = '%s?action=showDetails&source=%s&metadata=%s' % (sysaddon, syssource, sysmeta)
				contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

				contextLabel = interface.Translation.string(33031)
				contextCommand = '%s?action=copyLink&source=%s&resolve=true' % (sysaddon, syssource)
				contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

				contextLabel = interface.Translation.string(32070)
				contextCommand = '%s?action=traktManager&refresh=0&' % sysaddon
				if 'tvdb' in metadata:
					contextCommand += 'tvdb=%s' % metadata['tvdb']
					if 'season' in metadata:
						contextCommand += '&season=%s' % str(metadata['season'])
					if 'episode' in metadata:
						contextCommand += '&episode=%s' % str(metadata['episode'])
				else:
					contextCommand += 'imdb=%s' % metadata['imdb']
				contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

				if not local:

					if manualEnabled:
						# Download Manager
						if not self.kidsOnly() and control.setting('downloads.manual.enabled') == 'true':
							contextLabel = interface.Translation.string(33585)
							contextCommand = '%s?action=downloadsManager' % (sysaddon)
							contextMenu.append((contextLabel, 'Container.Update(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

						# Download With
						if contextWith:
							contextLabel = interface.Translation.string(33562)
							contextCommand = '%s?action=download&downloadType=%s&handleMode=%s&image=%s&source=%s&metadata=%s' % (sysaddon, downloader.Downloader.TypeManual, handler.Handler.ModeSelection, sysimage, syssource, sysmeta)
							contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

						# Download
						contextLabel = interface.Translation.string(33051)
						contextCommand = '%s?action=download&downloadType=%s&handleMode=%s&image=%s&source=%s&metadata=%s' % (sysaddon, downloader.Downloader.TypeManual, handler.Handler.ModeDefault, sysimage, syssource, sysmeta)
						contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

					if cacheEnabled:
						# Cache With
						if contextWith:
							contextLabel = interface.Translation.string(33563)
							contextCommand = '%s?action=cacheItem&handleMode=%s&source=%s&metadata=%s' % (sysaddon, handler.Handler.ModeSelection, syssource, sysmeta)
							contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

						# Cache
						contextLabel = interface.Translation.string(33016)
						contextCommand = '%s?action=cacheItem&handleMode=%s&source=%s&metadata=%s' % (sysaddon, handler.Handler.ModeDefault, syssource, sysmeta)
						contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

					# Play With
					if contextWith:
						contextLabel = interface.Translation.string(33561)
						contextCommand = '%s?action=playItem&handleMode=%s&source=%s&metadata=%s' % (sysaddon, handler.Handler.ModeSelection, syssource, sysmeta)
						contextMenu.append((contextLabel, 'RunPlugin(%s)' % self.parameterize(contextCommand, type = type, kids = kids)))

				listItem.addContextMenuItems(contextMenu)

				# ADD ITEM
				control.addItem(handle = syshandle, url = sysurl, listitem = listItem, isFolder = False)
			except:
				tools.Logger.error()

		control.content(syshandle, 'files')
		control.directory(syshandle, cacheToDisc = True)

	def search(self):
		self.addDirectoryItem(32001, self.parameterize('movieSearch', type = tools.Media.TypeMovie), 'searchmovies.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(32002, self.parameterize('tvSearch', type = tools.Media.TypeShow), 'searchtvshows.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(33470, self.parameterize('movieSearch', type = tools.Media.TypeDocumentary), 'searchdocumentaries.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(33471, self.parameterize('movieSearch', type = tools.Media.TypeShort), 'searchshorts.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(32013, self.parameterize('person'), 'searchpeople.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(33038, self.parameterize('searchRecent'), 'searchhistory.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def searchRecent(self):
		searches = search.Searches().retrieveAll(kids = self.kids)
		for item in searches:
			if item[0] == search.Searches.TypeMovies:
				icon = 'searchmovies.png'
				action = self.parameterize('movieSearch', type = tools.Media.TypeMovie)
			elif item[0] == search.Searches.TypeShows:
				icon = 'searchtvshows.png'
				action = self.parameterize('tvSearch', type = tools.Media.TypeShow)
			elif item[0] == search.Searches.TypeDocumentaries:
				icon = 'searchdocumentaries.png'
				action = self.parameterize('movieSearch', type = tools.Media.TypeDocumentary)
			elif item[0] == search.Searches.TypeShorts:
				icon = 'searchshorts.png'
				action = self.parameterize('movieSearch', type = tools.Media.TypeShort)
			elif item[0] == search.Searches.TypePeople:
				icon = 'searchpeople.png'
				action = self.parameterize('person')
			else:
				continue

			if item[2]:
				icon = 'searchkids.png'

			self.addDirectoryItem(item[1], '%s&terms=%s' % (action, urllib.quote_plus(item[1])), icon, 'DefaultAddonsSearch.png')
		self.endDirectory()

	def searchRecentMovies(self):
		searches = search.Searches().retrieveMovies(kids = self.kids)
		for item in searches:
			self.addDirectoryItem(item[0], self.parameterize('movieSearch&terms=%s' % urllib.quote_plus(item[0]), type = tools.Media.TypeMovie), 'searchmovies.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def searchRecentShows(self):
		searches = search.Searches().retrieveShows(kids = self.kids)
		for item in searches:
			self.addDirectoryItem(item[0], self.parameterize('tvSearch&terms=%s' % urllib.quote_plus(item[0]), type = tools.Media.TypeShow), 'searchtvshows.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def searchRecentDocumentaries(self):
		searches = search.Searches().retrieveDocumentaries(kids = self.kids)
		for item in searches:
			self.addDirectoryItem(item[0], self.parameterize('movieSearch&terms=%s' % urllib.quote_plus(item[0]), type = tools.Media.TypeDocumentary), 'searchdocumentaries.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def searchRecentShorts(self):
		searches = search.Searches().retrieveShorts(kids = self.kids)
		for item in searches:
			self.addDirectoryItem(item[0], self.parameterize('movieSearch&terms=%s' % urllib.quote_plus(item[0]), type = tools.Media.TypeShort), 'searchshorts.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def backupNavigator(self):
		self.addDirectoryItem(33774, 'backupRestore', 'backuprestore.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33776, 'backupAll', 'backupall.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33011, 'backupSettings', 'backupsettings.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33775, 'backupDatabases', 'backupdatabases.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.endDirectory()

	def viewsNavigator(self):
		self.addDirectoryItem(33001, 'viewsCategoriesNavigator', 'viewscategories.png', 'DefaultHardDisk.png')
		self.addDirectoryItem(33013, 'clearViews', 'viewsclear.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.endDirectory()

	def viewsCategoriesNavigator(self):
		# NB: Handle is -1 (invalid) when called like this. Open up a dialog instead
		control.idle()
		items = [
			(control.lang(32001).encode('utf-8'), 'movies'),
			(control.lang(33491).encode('utf-8'), 'documentaries'),
			(control.lang(33471).encode('utf-8'), 'shorts'),
			(control.lang(32002).encode('utf-8'), 'shows'),
			(control.lang(32054).encode('utf-8'), 'seasons'),
			(control.lang(32038).encode('utf-8'), 'episodes'),
		]
		select = interface.Dialog.options(title = 33012, items = [i[0] for i in items])
		if select == -1: return
		self.views(content = items[select][1])

		'''self.addDirectoryItem(32001, 'views&content=movies', 'viewsmovies.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33491, 'views&content=documentaries', 'viewsdocumentaries.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33471, 'views&content=shorts', 'viewsshorts.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(32002, 'views&content=shows', 'viewstvshows.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(32054, 'views&content=seasons', 'viewstvshows.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.addDirectoryItem(32326, 'views&content=episodes', 'viewstvshows.png', 'DefaultHardDisk.png', isAction = True, isFolder = False)
		self.endDirectory()'''

	def views(self, content):
		try:
			title = control.lang(32059).encode('utf-8')
			url = '%s?action=addView&content=%s' % (sys.argv[0], content)

			item = control.item(label=title)
			item.setInfo(type='Video', infoLabels = {'title': title})

			iconIcon, iconThumb, iconPoster, iconBanner = interface.Icon.pathAll(icon = 'views.png', default = 'DefaultProgram.png')
			item.setArt({'icon': iconIcon, 'thumb': iconThumb, 'poster': iconPoster, 'banner': iconBanner})

			fanart = control.addonFanart()
			item.setProperty('Fanart_Image', fanart)

			control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=False)
			control.content(int(sys.argv[1]), views.convertView(content))
			control.directory(int(sys.argv[1]), cacheToDisc=True)

			views.setView(content, {})
		except:
			tools.Logger.error()
			return

	def clearNavigator(self):
		self.addDirectoryItem(33029, 'clearAll', 'clear.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33014, 'clearProviders', 'clearproviders.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33353, 'clearWebcache', 'clearcache.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(32036, 'clearHistory', 'clearhistory.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33041, 'clearSearches', 'clearsearches.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(32009, 'clearDownloads', 'cleardownloads.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33466, 'clearTemporary', 'cleartemporary.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33012, 'clearViews', 'clearviews.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def _clearConfirm(self):
		interface.Loader.hide()
		result = interface.Dialog.option(title = 33013, message = 33042)
		if result: interface.Loader.show()
		return result

	def _clearNotify(self):
		interface.Loader.hide()
		interface.Dialog.notification(title = 33013, message = 33043, icon = interface.Dialog.IconSuccess)

	def clearAll(self):
		if self._clearConfirm():
			self.clearProviders(confirm = False)
			self.clearWebcache(confirm = False)
			self.clearHistory(confirm = False)
			self.clearSearches(confirm = False)
			self.clearDownloads(confirm = False, automatic = True)
			self.clearTemporary(confirm = False)
			self.clearViews(confirm = False)
			self._clearNotify()

	def clearProviders(self, confirm = True):
		if not confirm or self._clearConfirm():
			from resources.lib.sources import sources
			from resources.lib.sources import provider
			sources().clearSources(confirm = False)
			provider.Provider.failureClear()
			if confirm: self._clearNotify()

	def clearWebcache(self, confirm = True):
		if not confirm or self._clearConfirm():
			from resources.lib.modules import cache
			cache.cache_clear()
			if confirm: self._clearNotify()

	def clearHistory(self, confirm = True):
		if not confirm or self._clearConfirm():
			historyx.History().clear(confirm = False)
			if confirm: self._clearNotify()

	def clearSearches(self, confirm = True):
		if not confirm or self._clearConfirm():
			search.Searches().clear(confirm = False)
			if confirm: self._clearNotify()

	def clearDownloads(self, confirm = True, automatic = False):
		from resources.lib.extensions import downloader
		if automatic:
			if not confirm or self._clearConfirm():
				downloader.Downloader(downloader.Downloader.TypeManual).clear(status = downloader.Downloader.StatusAll, automatic = True)
				downloader.Downloader(downloader.Downloader.TypeCache).clear(status = downloader.Downloader.StatusAll, automatic = True)
				if confirm: self._clearNotify()
		else:
			self.addDirectoryItem(33290, 'downloadsClear&type=%s' % downloader.Downloader.TypeManual, 'clearmanual.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem(33016, 'downloadsClear&type=%s' % downloader.Downloader.TypeCache, 'clearcache.png', 'DefaultAddonProgram.png')
			self.endDirectory()

	def clearTemporary(self, confirm = True):
		if not confirm or self._clearConfirm():
			tools.System.temporaryClear()
			if confirm: self._clearNotify()

	def clearViews(self, confirm = True):
		if not confirm or self._clearConfirm():
			from resources.lib.modules import views
			views.clearViews()
			if confirm: self._clearNotify()

	def addDirectoryItem(self, name, query, thumb, icon, queue = False, isAction = True, isFolder = True, iconSpecial = interface.Icon.SpecialNone):
		try: name = control.lang(name).encode('utf-8')
		except: pass
		url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
		cm = []
		if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
		item = control.item(label=name)
		item.addContextMenuItems(cm)

		iconIcon, iconThumb, iconPoster, iconBanner = interface.Icon.pathAll(icon = thumb, default = icon, special = iconSpecial)
		item.setArt({'icon': iconIcon, 'thumb': iconThumb, 'poster': iconPoster, 'banner': iconBanner})

		if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

	def endDirectory(self):
		control.content(syshandle, 'addons')
		control.directory(syshandle, cacheToDisc=True)

	def favouritesNavigator(self):
		self.addDirectoryItem(32001, self.parameterize('movieFavouritesNavigator', type = tools.Media.TypeMovie), 'moviesfavourites.png', 'DefaultFavourite.png')
		self.addDirectoryItem(32002, self.parameterize('tvFavouritesNavigator', type = tools.Media.TypeShow), 'tvshowsfavourites.png', 'DefaultFavourite.png')
		self.addDirectoryItem(33470, self.parameterize('movieFavouritesNavigator', type = tools.Media.TypeDocumentary), 'documentariesfavourites.png', 'DefaultFavourite.png')
		self.addDirectoryItem(33471, self.parameterize('movieFavouritesNavigator', type = tools.Media.TypeShort), 'shortsfavourites.png', 'DefaultFavourite.png')
		self.addDirectoryItem(32036, self.parameterize('historyNavigator', type = None), 'historyfavourites.png', 'DefaultFavourite.png')
		self.endDirectory()

	def arrivalsNavigator(self):
		self.addDirectoryItem(32001, self.parameterize('movieArrivals', type = tools.Media.TypeMovie), 'moviesnew.png', 'DefaultAddSource.png')
		self.addDirectoryItem(32002, self.parameterize('tvArrivals', type = tools.Media.TypeShow), 'tvshowsnew.png', 'DefaultAddSource.png')
		self.addDirectoryItem(33470, self.parameterize('movieArrivals', type = tools.Media.TypeDocumentary), 'documentariesnew.png', 'DefaultAddSource.png')
		self.addDirectoryItem(33471, self.parameterize('movieArrivals', type = tools.Media.TypeShort), 'shortsnew.png', 'DefaultAddSource.png')
		self.endDirectory()

	def systemNavigator(self):
		self.addDirectoryItem(33344, 'systemInformation', 'systeminformation.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33472, 'systemManager', 'systemmanager.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33719, 'networkInformation', 'systemnetwork.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33468, 'systemClean', 'systemclear.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def informationNavigator(self):
		self.addDirectoryItem(33354, 'openLink&link=%s' % tools.Settings.getString('link.website', raw = True), 'network.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33412, 'openLink&link=%s' % tools.Settings.getString('link.repository', raw = True), 'cache.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33239, 'openLink&link=%s' % tools.Settings.getString('link.help', raw = True), 'help.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33377, 'openLink&link=%s' % tools.Settings.getString('link.issues', raw = True), 'bulb.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33411, 'openLink&link=%s' % tools.Settings.getString('link.forum', raw = True), 'languages.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33355, 'openLink&link=%s' % tools.Settings.getString('link.bugs', raw = True), 'bug.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33356, 'openLink&link=%s' % tools.Settings.getString('link.polls', raw = True), 'popular.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33768, 'informationPremium', 'favourites.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33503, 'informationChangelog', 'changelog.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33037, 'informationSplash', 'splash.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33358, 'informationAbout', 'information.png', 'DefaultAddonProgram.png')
		self.endDirectory()

	def donationsNavigator(self):
		self.addDirectoryItem(interface.Format.color('Bitcoin', 'F7931A'), 'donationsCrypto&currency=%s' % tools.Donations.CurrencyBitcoin, 'donationsbitcoin.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)
		self.addDirectoryItem(interface.Format.color('Ethereum', '62688F'), 'donationsCrypto&currency=%s' % tools.Donations.CurrencyEthereum, 'donationsethereum.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)
		self.addDirectoryItem(interface.Format.color('Litecoin', 'BEBEBE'), 'donationsCrypto&currency=%s' % tools.Donations.CurrencyLitecoin, 'donationslitecoin.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)
		self.addDirectoryItem(interface.Format.color('Dash', '1C75BC'), 'donationsCrypto&currency=%s' % tools.Donations.CurrencyDash, 'donationsdash.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)
		self.addDirectoryItem(interface.Format.color('Augur', '602952'), 'donationsCrypto&currency=%s' % tools.Donations.CurrencyAugur, 'donationsaugur.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)
		self.addDirectoryItem(interface.Format.color('Golem', '00AFBF'), 'donationsCrypto&currency=%s' % tools.Donations.CurrencyGolem, 'donationsgolem.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)
		self.addDirectoryItem(interface.Format.color('Dogecoin', 'BA9F33'), 'donationsCrypto&currency=%s' % tools.Donations.CurrencyDogecoin, 'donationsdogecoin.png', 'DefaultAddonProgram.png', iconSpecial = interface.Icon.SpecialDonations)
		self.endDirectory()

	def informationPremium(self):
		full = interface.Translation.string(33458)
		limited = interface.Translation.string(33459)
		minimal = interface.Translation.string(33460)

		self.addDirectoryItem('Premiumize (%s)' % full, 'openLink&link=%s' % debrid.Premiumize.website(), 'premiumize.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('RealDebrid (%s)' % limited, 'openLink&link=%s' % debrid.RealDebrid.website(), 'realdebrid.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('EasyNews (%s)' % limited, 'openLink&link=%s' % debrid.EasyNews.website(), 'easynews.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('AllDebrid (%s)' % minimal, 'openLink&link=%s' % debrid.AllDebrid.website(), 'alldebrid.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('RapidPremium (%s)' % minimal, 'openLink&link=%s' % debrid.RapidPremium.website(), 'rapidpremium.png', 'DefaultAddonProgram.png')
		self.endDirectory()

	def traktAccount(self):
		credentials = trakt.getTraktCredentialsInfo()
		if not credentials:
			if interface.Dialog.option(title = 33339, message = 33646, labelConfirm = 33011, labelDeny = 33486):
				tools.Settings.launch(category = tools.Settings.CategoryAccounts)
		return credentials

	def imdbAccount(self):
		credentials = False if control.setting('accounts.informants.imdb.enabled') == 'false' or control.setting('accounts.informants.imdb.user') == '' else True
		if not credentials:
			if interface.Dialog.option(title = 33339, message = 33647, labelConfirm = 33011, labelDeny = 33486):
				tools.Settings.launch(category = tools.Settings.CategoryAccounts)
		return credentials

	def traktmovies(self):
		if self.traktAccount():
			self.addDirectoryItem(32036, self.parameterize('movies&url=trakthistory'), 'trakthistory.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(32032, self.parameterize('movies&url=traktcollection'), 'traktcollections.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(33662, self.parameterize('movies&url=traktrecommendations'), 'traktfeatured.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(33002, self.parameterize('traktmovieslistsNavigator'), 'traktlists.png', 'DefaultAddonWebSkin.png')
			self.endDirectory()

	def traktmovieslists(self):
		if self.traktAccount():
			self.addDirectoryItem(32520, self.parameterize('traktListAdd'), 'traktadd.png', 'DefaultVideoPlaylists.png')
			self.addDirectoryItem(32033, self.parameterize('movies&url=traktwatchlist'), 'traktwatch.png', 'DefaultVideoPlaylists.png')

			if self.type == tools.Media.TypeDocumentary: label = 33663
			elif self.type == tools.Media.TypeShort: label = 33664
			else: label = 32039
			self.addDirectoryItem(label, self.parameterize('movieUserlists'), 'traktlists.png', 'DefaultVideoPlaylists.png')

			self.endDirectory()

	def imdbmovies(self):
		if self.imdbAccount():
			self.addDirectoryItem(32032, self.parameterize('movies&url=imdbwatchlist'), 'imdbcollections.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(32033, self.parameterize('movies&url=imdbwatchlist2'), 'imdblists.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(32035, self.parameterize('movies&url=featured'), 'imdbfeatured.png', 'DefaultAddonWebSkin.png')
			self.endDirectory()

	def trakttv(self):
		if self.traktAccount():
			self.addDirectoryItem(32037, self.parameterize('calendar&url=progress'), 'traktprogress.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(32027, self.parameterize('calendar&url=mycalendar'), 'traktcalendar.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(32036, self.parameterize('calendar&url=trakthistory'), 'trakthistory.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(32032, self.parameterize('tvshows&url=traktcollection'), 'traktcollections.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(33662, self.parameterize('tvshows&url=traktrecommendations'), 'traktfeatured.png', 'DefaultAddonWebSkin.png')
			self.addDirectoryItem(33002, self.parameterize('trakttvlistsNavigator'), 'traktlists.png', 'DefaultAddonWebSkin.png')
			self.endDirectory()

	def trakttvlists(self):
		if self.traktAccount():
			self.addDirectoryItem(32520, self.parameterize('traktListAdd'), 'traktadd.png', 'DefaultVideoPlaylists.png')
			self.addDirectoryItem(32033, self.parameterize('tvshows&url=traktwatchlist'), 'traktwatch.png', 'DefaultVideoPlaylists.png')
			self.addDirectoryItem(32040, self.parameterize('tvUserlists'), 'traktlists.png', 'DefaultVideoPlaylists.png')
			self.addDirectoryItem(33665, self.parameterize('seasonUserlists'), 'traktlists.png', 'DefaultVideoPlaylists.png')
			self.addDirectoryItem(32041, self.parameterize('episodeUserlists'), 'traktlists.png', 'DefaultVideoPlaylists.png')
			self.endDirectory()

	def imdbtv(self):
		if self.imdbAccount():
			self.addDirectoryItem(32032, self.parameterize('tvshows&url=imdbwatchlist'), 'imdbcollections.png', 'DefaultTVShows.png')
			self.addDirectoryItem(32033, self.parameterize('tvshows&url=imdbwatchlist2'), 'imdblists.png', 'DefaultTVShows.png')
			self.addDirectoryItem(32035, self.parameterize('tvshows&url=featured'), 'imdbfeatured.png', 'DefaultTVShows.png')
			self.endDirectory()

	def moviesCategories(self):
		self.addDirectoryItem(32011, self.parameterize('movieGenres'), 'genres.png', 'DefaultGenre.png')
		self.addDirectoryItem(32012, self.parameterize('movieYears'), 'calendar.png', 'DefaultYear.png')
		if self.type == tools.Media.TypeMovie:
			self.addDirectoryItem(33504, self.parameterize('movieCollections'), 'collections.png', 'DefaultSets.png')
			self.addDirectoryItem(32007, self.parameterize('channels'), 'network.png', 'DefaultNetwork.png')
		self.addDirectoryItem(32014, self.parameterize('movieLanguages'), 'languages.png', 'DefaultCountry.png')
		self.addDirectoryItem(32013, self.parameterize('moviePersons'), 'people.png', 'DefaultActor.png')
		self.addDirectoryItem(32015, self.parameterize('movieCertificates'), 'certificates.png', 'DefaultFile.png')
		self.addDirectoryItem(33437, self.parameterize('movieAge'), 'age.png', 'DefaultYear.png')
		self.endDirectory()

	def moviesLists(self):
		self.addDirectoryItem(33004, self.parameterize('movies&url=new'), 'new.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33571, self.parameterize('movies&url=home'), 'home.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33005, self.parameterize('movies&url=rating'), 'rated.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(32018, self.parameterize('movies&url=popular'), 'popular.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33008, self.parameterize('movies&url=oscars'), 'awards.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33010, self.parameterize('movies&url=boxoffice'), 'tickets.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33006, self.parameterize('movies&url=theaters'), 'premiered.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33007, self.parameterize('movies&url=trending'), 'trending.png', 'DefaultVideoPlaylists.png')
		self.endDirectory()

	def moviesPeople(self):
		self.addDirectoryItem(33003, self.parameterize('moviePersons'), 'browse.png', 'DefaultAddonContextItem.png')
		self.addDirectoryItem(32010, self.parameterize('moviePerson'), 'search.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def moviesSearchNavigator(self):
		self.addDirectoryItem(33039, self.parameterize('movieSearch'), 'searchtitle.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(33040, self.parameterize('movieSearch'), 'searchdescription.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(32013, self.parameterize('moviePerson'), 'searchpeople.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(33038, self.parameterize('searchRecentMovies'), 'searchhistory.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def tvCategories(self):
		self.addDirectoryItem(32011, self.parameterize('tvGenres'), 'genres.png', 'DefaultGenre.png')
		self.addDirectoryItem(32012, self.parameterize('tvYears'), 'calendar.png', 'DefaultYear.png')
		self.addDirectoryItem(32016, self.parameterize('tvNetworks'), 'networks.png', 'DefaultNetwork.png')
		self.addDirectoryItem(32014, self.parameterize('tvLanguages'), 'languages.png', 'DefaultCountry.png')
		self.addDirectoryItem(32013, self.parameterize('tvPersons'), 'people.png', 'DefaultActor.png')
		self.addDirectoryItem(32015, self.parameterize('tvCertificates'), 'certificates.png', 'DefaultFile.png')
		self.addDirectoryItem(33437, self.parameterize('tvAge'), 'age.png', 'DefaultYear.png')
		self.endDirectory()

	def tvLists(self):
		self.addDirectoryItem(33004, self.parameterize('calendar&url=added'), 'new.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33571, self.parameterize('tvHome'), 'home.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33005, self.parameterize('tvshows&url=rating'), 'rated.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(32018, self.parameterize('tvshows&url=popular'), 'popular.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33008, self.parameterize('tvshows&url=emmies'), 'awards.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33009, self.parameterize('tvshows&url=airing'), 'aired.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33006, self.parameterize('tvshows&url=premiere'), 'premiered.png', 'DefaultVideoPlaylists.png')
		self.addDirectoryItem(33007, self.parameterize('tvshows&url=trending'), 'trending.png', 'DefaultVideoPlaylists.png')
		self.endDirectory()

	def tvPeople(self):
		self.addDirectoryItem(33003, self.parameterize('tvPersons'), 'browse.png', 'DefaultAddonContextItem.png')
		self.addDirectoryItem(32010, self.parameterize('tvPerson'), 'search.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def tvSearchNavigator(self):
		self.addDirectoryItem(33039, self.parameterize('tvSearch'), 'searchtitle.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(33040, self.parameterize('tvSearch'), 'searchdescription.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(32013, self.parameterize('tvPerson'), 'searchpeople.png', 'DefaultAddonsSearch.png')
		self.addDirectoryItem(33038, self.parameterize('searchRecentShows'), 'searchhistory.png', 'DefaultAddonsSearch.png')
		self.endDirectory()

	def verificationNavigator(self):
		self.addDirectoryItem(32346, 'verificationAccounts', 'verificationaccount.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33014, 'verificationProviders', 'verificationprovider.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def networkNavigator(self):
		self.addDirectoryItem(33030, 'speedtestNavigator', 'networkspeed.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33344, 'networkInformation', 'networkinformation.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33801, 'vpnNavigator', 'networkvpn.png', 'DefaultAddonProgram.png')
		self.endDirectory()

	def speedtestNavigator(self):
		self.addDirectoryItem(33509, 'speedtestGlobal', 'speedglobal.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33566, 'speedtestPremiumize', 'speedpremiumize.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33567, 'speedtestRealDebrid', 'speedrealdebrid.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33794, 'speedtestEasyNews', 'speedeasynews.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33851, 'speedtestComparison', 'speedcomparison.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33846, 'speedtestParticipation', 'speedparticipation.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		if speedtest.SpeedTester.voucherValid():
			self.addDirectoryItem(33876, 'speedtestVoucher', 'speedvoucher.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def vpnNavigator(self):
		self.addDirectoryItem(33017, 'vpnVerification', 'vpnverification.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33802, 'vpnConfiguration', 'vpnconfiguration.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33011, 'vpnSettings', 'vpnsettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		if debrid.Premiumize().accountValid():
			self.addDirectoryItem(33566, 'premiumizeVpn', 'vpnpremiumize.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		if debrid.EasyNews().accountValid():
			self.addDirectoryItem(33794, 'easynewsVpn', 'vpneasynews.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def providersNavigator(self):
		self.addDirectoryItem(33017, 'verificationProviders', 'providerverification.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(35016, 'providersOptimization', 'providerconfiguration.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33013, 'clearSources', 'providerclear.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33011, 'providersSettings', 'providersettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def accountsNavigator(self):
		self.addDirectoryItem(33566, 'premiumizeAccount', 'accountpremiumize.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33567, 'realdebridAccount', 'accountrealdebrid.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33794, 'easynewsAccount', 'accounteasynews.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33017, 'verificationAccounts', 'accountverification.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33011, 'accountsSettings', 'accountsettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def downloads(self, type = None):
		if type == None:
			self.addDirectoryItem(33290, 'downloads&downloadType=%s' % downloader.Downloader.TypeManual, 'downloadsmanual.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem(33016, 'downloads&downloadType=%s' % downloader.Downloader.TypeCache, 'downloadscache.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem('Premiumize', 'premiumizeDownloadsNavigator', 'downloadspremiumize.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem('RealDebrid', 'realdebridDownloadsNavigator', 'downloadsrealdebrid.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem('Quasar', 'quasarNavigator', 'downloadsquasar.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem(33011, 'downloadsSettings', 'downloadssettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.endDirectory()
		else:
			#	if control.setting('downloads.%s.enabled' % type) == 'true':
			if downloader.Downloader(type).enabled(notification = True): # Do not use full check, since the download directory might be temporarley down (eg: network), and you still want to access the downloads.
				if control.setting('downloads.%s.path.selection' % type) == '0':
					path = control.setting('downloads.%s.path.combined' % type)
					if tools.File.exists(path):
						action = path
						actionIs = False
					else:
						action = 'downloadsBrowse&downloadType=%s&downloadError=%d' % (type, int(True))
						actionIs = True
				else:
					action = 'downloadsBrowse&downloadType=%s' % type
					actionIs = True
				self.addDirectoryItem(33297, 'downloadsList&downloadType=%s' % type, '%slist.png' % type, 'DefaultAddonProgram.png')
				self.addDirectoryItem(33003, action, '%sbrowse.png' % type, 'DefaultAddonProgram.png', isAction = actionIs)
				self.addDirectoryItem(33013, 'downloadsClear&downloadType=%s' % type, '%sclear.png' % type, 'DefaultAddonProgram.png')
				self.addDirectoryItem(33011, 'downloadsSettings&downloadType=%s' % type, '%ssettings.png' % type, 'DefaultAddonProgram.png', isAction = True, isFolder = False)
				self.endDirectory()
			else:
				pass
				#downloader.Downloader(type).enabled(notification = True, full = True)

	def downloadsBrowse(self, type = None, error = False):
		if error:
			downloader.Downloader(type).notificationLocation()
		else:
			path = control.setting('downloads.%s.path.movies' % type)
			if tools.File.exists(path):
				action = path
				actionIs = False
			else:
				action = 'downloadsBrowse&downloadType=%s&downloadError=%d' % (type, int(True))
				actionIs = True
			self.addDirectoryItem(32001, action, '%smovies.png' % type, 'DefaultAddonProgram.png', isAction = actionIs)

			path = control.setting('downloads.%s.path.tvshows' % type)
			if tools.File.exists(path):
				action = path
				actionIs = False
			else:
				action = 'downloadsBrowse&downloadType=%s&downloadError=%d' % (type, int(True))
				actionIs = True
			self.addDirectoryItem(32002, action, '%stvshows.png' % type, 'DefaultAddonProgram.png', isAction = actionIs)

			self.endDirectory()

	def downloadsList(self, type):
		self.addDirectoryItem(33029, 'downloadsList&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusAll), '%slist.png' % type, 'DefaultAddonProgram.png')
		self.addDirectoryItem(33291, 'downloadsList&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusBusy), '%sbusy.png' % type, 'DefaultAddonProgram.png')
		self.addDirectoryItem(33292, 'downloadsList&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusPaused), '%spaused.png' % type, 'DefaultAddonProgram.png')
		self.addDirectoryItem(33294, 'downloadsList&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusCompleted), '%scompleted.png' % type, 'DefaultAddonProgram.png')
		self.addDirectoryItem(33295, 'downloadsList&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusFailed), '%sfailed.png' % type, 'DefaultAddonProgram.png')
		self.endDirectory()

	def downloadsClear(self, type):
		self.addDirectoryItem(33029, 'downloadsClear&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusAll), 'clearlist.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33291, 'downloadsClear&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusBusy), 'clearbusy.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33292, 'downloadsClear&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusPaused), 'clearpaused.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33294, 'downloadsClear&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusCompleted), 'clearcompleted.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33295, 'downloadsClear&downloadType=%s&downloadStatus=%s' % (type, downloader.Downloader.StatusFailed), 'clearfailed.png', 'DefaultAddonProgram.png')
		self.endDirectory()

	def servicesNavigator(self):
		self.addDirectoryItem('Premiumize', 'premiumizeNavigator', 'premiumize.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('RealDebrid', 'realdebridNavigator', 'realdebrid.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('EasyNews', 'easynewsNavigator', 'easynews.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('Quasar', 'quasarNavigator', 'quasar.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('Trakt', 'traktNavigator', 'trakt.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('UrlResolver', 'urlresolverNavigator', 'urlresolver.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem('MetaHandler', 'metahandlerNavigator', 'metahandler.png', 'DefaultAddonProgram.png')
		self.endDirectory()

	def premiumizeNavigator(self):
		valid = debrid.Premiumize().accountValid()
		if valid:
			self.addDirectoryItem(32009, 'premiumizeDownloadsNavigator&lite=1', 'premiumizedownloads.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem(33339, 'premiumizeAccount', 'premiumizeaccount.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33030, 'speedtestPremiumize', 'premiumizespeed.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33354, 'premiumizeWebsite', 'premiumizeweb.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		if valid:
			self.addDirectoryItem(33013, 'premiumizeClear', 'premiumizeclear.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33011, 'premiumizeSettings', 'premiumizesettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def premiumizeDownloadsNavigator(self, lite = False):
		valid = debrid.Premiumize().accountValid()
		if valid:
			self.addDirectoryItem(33297, 'premiumizeList', 'premiumizelist.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33344, 'premiumizeInformation', 'premiumizeinformation.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		if not lite:
			if valid: self.addDirectoryItem(33013, 'premiumizeClear', 'premiumizeclear.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33011, 'premiumizeSettings', 'premiumizesettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def realdebridNavigator(self):
		valid = debrid.RealDebrid().accountValid()
		if valid:
			self.addDirectoryItem(32009, 'realdebridDownloadsNavigator&lite=1', 'realdebriddownloads.png', 'DefaultAddonProgram.png')
			self.addDirectoryItem(33339, 'realdebridAccount', 'realdebridaccount.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33030, 'speedtestRealDebrid', 'realdebridspeed.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33354, 'realdebridWebsite', 'realdebridweb.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		if valid:
			self.addDirectoryItem(33013, 'realdebridClear', 'realdebridclear.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33011, 'realdebridSettings', 'realdebridsettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def realdebridDownloadsNavigator(self, lite = False):
		valid = debrid.RealDebrid().accountValid()
		if valid:
			self.addDirectoryItem(33297, 'realdebridList', 'realdebridlist.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33344, 'realdebridInformation', 'realdebridinformation.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		if not lite:
			if valid: self.addDirectoryItem(33013, 'realdebridClear', 'realdebridclear.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33011, 'realdebridSettings', 'realdebridsettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def easynewsNavigator(self):
		if debrid.EasyNews().accountValid():
			self.addDirectoryItem(33339, 'easynewsAccount', 'easynewsaccount.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33030, 'speedtestEasyNews', 'easynewsspeed.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33354, 'easynewsWebsite', 'easynewsweb.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def quasarNavigator(self):
		if tools.Quasar.connected():
			self.addDirectoryItem(33256, 'quasarLaunch', 'quasarlaunch.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33477, 'quasarInterface', 'quasarweb.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33011, 'quasarSettings', 'quasarsettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		else:
			self.addDirectoryItem(33474, 'quasarInstall', 'quasarinstall.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def traktNavigator(self):
		if tools.Trakt.installed():
			self.addDirectoryItem(33256, 'traktLaunch', 'traktlaunch.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33354, 'traktWebsite', 'traktweb.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33011, 'traktSettings', 'traktsettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		else:
			self.addDirectoryItem(33474, 'traktInstall', 'traktinstall.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def urlresolverNavigator(self):
		if tools.UrlResolver.installed():
			self.addDirectoryItem(33011, 'urlresolverSettings', 'urlresolversettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		else:
			self.addDirectoryItem(33474, 'urlresolverInstall', 'urlresolverinstall.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def metahandlerNavigator(self):
		if tools.MetaHandler.installed():
			self.addDirectoryItem(33011, 'metahandlerSettings', 'metahandlersettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		else:
			self.addDirectoryItem(33474, 'metahandlerInstall', 'metahandlerinstall.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def extensionsNavigator(self):
		self.addDirectoryItem(33721, 'extensionsAvailableNavigator', 'extensionsavailable.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(33722, 'extensionsInstalledNavigator', 'extensionsinstalled.png', 'DefaultAddonProgram.png')
		self.endDirectory()

	def extensionsAvailableNavigator(self):
		extensions = tools.Extensions.list()
		for extension in extensions:
			if not extension['installed']:
				self.addDirectoryItem(extension['name'], 'extensions&id=%s' % extension['id'], extension['icon'], 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def extensionsInstalledNavigator(self):
		extensions = tools.Extensions.list()
		for extension in extensions:
			if extension['installed']:
				self.addDirectoryItem(extension['name'], 'extensions&id=%s' % extension['id'], extension['icon'], 'DefaultAddonProgram.png')
		self.endDirectory()

	def lightpackNavigator(self):
		if tools.Lightpack().enabled():
			self.addDirectoryItem(33407, 'lightpackSwitchOn', 'lightpackon.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33408, 'lightpackSwitchOff', 'lightpackoff.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
			self.addDirectoryItem(33409, 'lightpackAnimate', 'lightpackanimate.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.addDirectoryItem(33011, 'lightpackSettings', 'lightpacksettings.png', 'DefaultAddonProgram.png', isAction = True, isFolder = False)
		self.endDirectory()

	def kidsRedirect(self):
		if tools.Kids.locked():
			self.kidsNavigator()
			return True
		return False

	def kidsNavigator(self):
		kids = tools.Selection.TypeInclude
		if tools.Settings.getBoolean('interface.menu.movies'):
			self.addDirectoryItem(32001, self.parameterize('movieNavigator', type = tools.Media.TypeMovie, kids = kids), 'movies.png', 'DefaultMovies.png')
		if tools.Settings.getBoolean('interface.menu.shows'):
			self.addDirectoryItem(32002, self.parameterize('tvNavigator', type = tools.Media.TypeShow, kids = kids), 'tvshows.png', 'DefaultTVShows.png')
		if tools.Settings.getBoolean('interface.menu.documentaries'):
			self.addDirectoryItem(33470, self.parameterize('documentariesNavigator', type = tools.Media.TypeDocumentary, kids = kids), 'documentaries.png', 'DefaultVideo.png')
		if tools.Settings.getBoolean('interface.menu.shorts'):
			self.addDirectoryItem(33471, self.parameterize('shortsNavigator', type = tools.Media.TypeShort, kids = kids), 'shorts.png', 'DefaultVideo.png')

		if tools.Settings.getBoolean('interface.menu.arrivals'):
			self.addDirectoryItem(33490, self.parameterize('arrivalsNavigator', kids = kids), 'new.png', 'DefaultAddSource.png')
		if tools.Settings.getBoolean('interface.menu.search'):
			self.addDirectoryItem(32010, self.parameterize('searchNavigator', kids = kids), 'search.png', 'DefaultAddonsSearch.png')

		if tools.Kids.lockable():
			self.addDirectoryItem(33442, 'kidsLock', 'lock.png', 'DefaultAddonService.png')
		elif tools.Kids.unlockable():
			self.addDirectoryItem(33443, 'kidsUnlock', 'unlock.png', 'DefaultAddonService.png')

		self.endDirectory()
