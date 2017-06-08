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


import re,sys,json,time,xbmc,xbmcvfs
import hashlib,os,zlib,base64,codecs,xmlrpclib,threading

try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import playcount

from resources.lib.extensions import tools
from resources.lib.extensions import interface
from resources.lib.extensions import downloader
from resources.lib.extensions import debrid
from resources.lib.extensions import handler

# If the player automatically closes/crashes because the EOF was reached while still downloading, the player instance is never deleted.
# Now the player keeps a constant lock on the played file and the file cannot be deleted (manually, or by the downloader). The lock is only release when Kodi exits.
# Use a thread and forcefully delete the instance. Although this is still no garantuee that Kodi will release the lock on the file, but it seems to work most of the time.
def playerDelete(instance):
	time.sleep(1)
	# Do not just use "del instance", since this will only call __del__() if the reference count drops to 0. Kodi still has a reference to the instance.
	try: instance.__del__()
	except: pass
	try: del instance
	except: pass

class player(xbmc.Player):

	# Statuses
	StatusIdle = 0
	StatusPlaying = 1
	StatusPaused = 2
	StatusStopped = 3
	StatusEnded = 4

	# Download
	DownloadThresholdStart = 0.01 # If the difference between the download and the playback progress is lower than this percentage, buffering will start.
	DownloadThresholdStop = DownloadThresholdStart * 2 # If the difference between the download and the playback progress is higher than this percentage, buffering will stop.
	DownloadMinimum = 1048576 # 1 MB. The minimum number of bytes that must be available to avoid buffering. If the value is too small, the player with automatically stop/crash due to insufficient data available.
	DownloadFuture = 102400 # 100 KB. The number of bytes to read and update the progress with. Small values increase disk access, large values causes slow/jumpy progress.
	DownloadChunk = 8 # 8 B. The number of null bytes that are considered the end of file.
	DownloadNull = '\x00' * DownloadChunk

	def __init__ (self):
		xbmc.Player.__init__(self)
		self.status = self.StatusIdle

	def __del__(self):
		self._downloadClear(delete = False)
		try: xbmc.Player.__del__(self)
		except: pass


	def run(self, title, year, season, episode, imdb, tvdb, url, meta, downloadType = None, downloadId = None, handle = None):
		try:
			control.sleep(200)

			self.totalTime = 0 ; self.currentTime = 0

			self.content = 'movie' if season == None or episode == None else 'episode'

			self.title = title
			self.year = year
			self.name = tools.Media.titleUniversal(metadata = meta)
			self.season = '%01d' % int(season) if self.content == 'episode' else None
			self.episode = '%01d' % int(episode) if self.content == 'episode' else None

			self.DBID = None
			self.imdb = imdb if not imdb == None else '0'
			self.tvdb = tvdb if not tvdb == None else '0'
			self.ids = {'imdb': self.imdb, 'tvdb': self.tvdb}
			self.ids = dict((k,v) for k, v in self.ids.iteritems() if not v == '0')

			self.offset = bookmarks().get(self.name, self.year)

			poster, thumb, meta = self.getMeta(meta)

			item = control.item(path=url)
			item.setArt({'icon': thumb, 'thumb': thumb, 'poster': poster, 'tvshow.poster': poster, 'season.poster': poster})
			item.setInfo(type='Video', infoLabels = meta)

			# Bubbles
			self.url = url
			self.item = item
			self.timeTotal = 0
			self.timeCurrent = 0
			self.timeProgress = 0
			self.sizeTotal = 0
			self.sizeCurrent = 0
			self.sizeProgress = 0
			self.dialog = None

			self.downloadCheck = False
			if downloadType and downloadId:
				self.file = xbmcvfs.File(url)
				self.download = downloader.Downloader(type = downloadType, id = downloadId)
				self.bufferCounter = 0
				self.bufferShow = True

				# Already check here, so that the player waits when the download is still queued/initialized.
				if not self._downloadCheck():
					return
			else:
				self.file = None
				self.download = None
				self.bufferCounter = None
				self.bufferShow = None

			self.handle = handle

			# Check debrid links
			from resources.lib.extensions import debrid
			debrid.valt()

			if 'plugin' in control.infoLabel('Container.PluginName'):
				xbmc.executebuiltin('Dialog.Close(notification,true)') # Hide the caching/download notification if still showing.
				self.play(url, item)
			self.keepPlaybackAlive()

			control.resolve(int(sys.argv[1]), True, item)
			control.window.setProperty('script.trakt.ids', json.dumps(self.ids))
			control.window.clearProperty('script.trakt.ids')
		except:
			tools.Logger.error()

	def getMeta(self, meta):
		try:
			poster = '0'
			if 'poster3' in meta: poster = meta['poster3']
			elif 'poster2' in meta: poster = meta['poster2']
			elif 'poster' in meta: poster = meta['poster']

			thumb = '0'
			if 'thumb3' in meta: thumb = meta['thumb3']
			elif 'thumb2' in meta: thumb = meta['thumb2']
			elif 'thumb' in meta: thumb = meta['thumb']

			if poster == '0': poster = control.addonPoster()
			if thumb == '0': thumb = control.addonThumb()

			return (poster, thumb, meta)
		except:
			pass

		try:
			if not self.content == 'movie': raise Exception()

			meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "originaltitle", "year", "genre", "studio", "country", "runtime", "rating", "votes", "mpaa", "director", "writer", "plot", "plotoutline", "tagline", "thumbnail", "file"]}, "id": 1}' % (self.year, str(int(self.year)+1), str(int(self.year)-1)))
			meta = unicode(meta, 'utf-8', errors='ignore')
			meta = json.loads(meta)['result']['movies']

			t = cleantitle.get(self.title)
			meta = [i for i in meta if self.year == str(i['year']) and (t == cleantitle.get(i['title']) or t == cleantitle.get(i['originaltitle']))][0]

			for k, v in meta.iteritems():
				if type(v) == list:
					try: meta[k] = str(' / '.join([i.encode('utf-8') for i in v]))
					except: meta[k] = ''
				else:
					try: meta[k] = str(v.encode('utf-8'))
					except: meta[k] = str(v)

			if not 'plugin' in control.infoLabel('Container.PluginName'):
				self.DBID = meta['movieid']

			poster = thumb = meta['thumbnail']

			return (poster, thumb, meta)
		except:
			pass

		try:
			if not self.content == 'episode': raise Exception()

			meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "year", "thumbnail", "file"]}, "id": 1}' % (self.year, str(int(self.year)+1), str(int(self.year)-1)))
			meta = unicode(meta, 'utf-8', errors='ignore')
			meta = json.loads(meta)['result']['tvshows']

			t = cleantitle.get(self.title)
			meta = [i for i in meta if self.year == str(i['year']) and t == cleantitle.get(i['title'])][0]

			tvshowid = meta['tvshowid'] ; poster = meta['thumbnail']

			meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params":{ "tvshowid": %d, "filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["title", "season", "episode", "showtitle", "firstaired", "runtime", "rating", "director", "writer", "plot", "thumbnail", "file"]}, "id": 1}' % (tvshowid, self.season, self.episode))
			meta = unicode(meta, 'utf-8', errors='ignore')
			meta = json.loads(meta)['result']['episodes'][0]

			for k, v in meta.iteritems():
				if type(v) == list:
					try: meta[k] = str(' / '.join([i.encode('utf-8') for i in v]))
					except: meta[k] = ''
				else:
					try: meta[k] = str(v.encode('utf-8'))
					except: meta[k] = str(v)

			if not 'plugin' in control.infoLabel('Container.PluginName'):
				self.DBID = meta['episodeid']

			thumb = meta['thumbnail']

			return (poster, thumb, meta)
		except:
			pass


		poster, thumb, meta = '', '', {'title': self.name}
		return (poster, thumb, meta)


	def _debridClear(self):
		if self.handle:
			if not isinstance(self.handle, basestring):
				self.handle = self.handle.id()
			self.handle = self.handle.lower()

			if self.handle == handler.HandlePremiumize().id():
				debrid.Premiumize().deletePlayback()
			elif self.handle == handler.HandleRealDebrid().id():
				debrid.RealDebrid().deletePlayback()

	def _downloadStop(self):
		self._downloadClear(delete = False)
		if not self.download == None:
			self.download.stop(cacheOnly = True)

	def _downloadClear(self, delete = True):
		try: self.file.close()
		except: pass
		try: self.dialog.close()
		except: pass

		if delete:
			thread = threading.Thread(target = playerDelete, args = (self,))
			thread.start()

	# Bubbles
	def _downloadUpdateSize(self):
		try:
			self.file.seek(self.sizeCurrent, 0)
			data = self.file.read(self.DownloadChunk)
			while not data == self.DownloadNull:
				self.sizeCurrent += self.DownloadFuture
				self.file.seek(self.sizeCurrent, 0)
				data = self.file.read(self.DownloadChunk)

			self.sizeTotal = max(self.sizeTotal, self.file.size())
			if self.sizeTotal > 0:
				self.sizeProgress = self.sizeCurrent / float(self.sizeTotal)
		except:
			pass
		return self.sizeProgress

	def _downloadUpdateTime(self):
		try: self.timeCurrent = max(self.timeCurrent, self.getTime())
		except: pass
		try: self.timeTotal = max(self.timeTotal, self.getTotalTime())
		except: pass

		if self.timeTotal > 0:
			self.timeProgress = self.timeCurrent / float(self.timeTotal)
		return self.timeProgress

	def _downloadProgressDifference(self):
		progressSize = self._downloadUpdateSize()
		progressTime = self._downloadUpdateTime()
		return max(0, progressSize - progressTime), progressSize

	def _downloadProgress(self):
		progress = ''
		if not self.download == None:
			progress = interface.Format.fontBold(interface.Translation.string(32403) + ': ')
			self.download.refresh()
			progress += self.download.progress()
			progress += ' - ' + self.download.speed() + interface.Format.newline()
		return progress

	# Bubbles
	def _downloadCheck(self):
		if self.download == None:
			return False

		# Ensures that only one process can access this function at a time. Otherwise this function is executed multiple times at the same time.
		if self.downloadCheck:
			return False

		# If the user constantly cancels the buffering dialog, the dialog will not be shown for the rest of the playback.
		if not self.bufferShow:
			return False

		try:
			self.downloadCheck = True

			# Close all old and other dialogs.
			xbmc.executebuiltin('Dialog.Close(progressdialog,true)')
			xbmc.executebuiltin('Dialog.Close(extendedprogressdialog,true)')
			time.sleep(0.2) # Wait for the dialogs to close.

			# NB: The progress dialog pops up when the download is at 100%. Chack for the download progress (progressSize < 1).
			progressDifference, progressSize = self._downloadProgressDifference()
			if progressSize < 1 and progressDifference < self.DownloadThresholdStart or self.sizeCurrent < self.DownloadMinimum:
				paused = False
				try:
					if self.isPlaying():
						self.pause()
						paused = True
				except: pass

				title = interface.Translation.string(33368)
				message = interface.Translation.string(33369)
				self.dialog = interface.Dialog.progress(title = title, message = self._downloadProgress() + message, background = False)

				progressMinimum = progressDifference
				progressRange = self.DownloadThresholdStop - progressMinimum
				while progressSize < 1 and progressDifference < self.DownloadThresholdStop or self.sizeCurrent < self.DownloadMinimum:
					progress = max(1, int(((progressDifference - progressMinimum) / float(progressRange)) * 99))
					self.dialog.update(progress, self._downloadProgress() + message)
					if self.dialog.iscanceled(): break
					time.sleep(1)
					if self.dialog.iscanceled(): break
					progressDifference, progressSize = self._downloadProgressDifference()
				self.dialog.update(100, message)
				self.dialog.close()
				time.sleep(0.2)

				import xbmc
				xbmc.log("RRRRRRRRRRRRRRRRRRRRRRRRRRRRR: "+str(self.bufferCounter)+"  "+str(self.bufferCounter % 3),xbmc.LOGERROR)

				if self.dialog.iscanceled():
					self.bufferCounter += 1
					if self.bufferCounter % 3 == 0:
						if interface.Dialog.option(title = 33368, message = 33744):
							self.bufferShow = False

				try:
					if paused:
						self.pause() # Unpause
				except: pass

			self.downloadCheck = False
			return True
		except:
			self.downloadCheck = False
			return False

	def keepPlaybackAlive(self):
		self._downloadCheck()

		pname = '%s.player.overlay' % control.addonInfo('id')
		control.window.clearProperty(pname)

		if self.content == 'movie':
			overlay = playcount.getMovieOverlay(playcount.getMovieIndicators(), self.imdb)
		elif self.content == 'episode':
			overlay = playcount.getEpisodeOverlay(playcount.getTVShowIndicators(), self.imdb, self.tvdb, self.season, self.episode)
		else:
			overlay = '6'

		dots = ''
		title = ''
		message = ''
		background = False
		progressDialog = None

		title = interface.Translation.string(33451)
		message = interface.Translation.string(33452)
		message = interface.Format.fontBold(message)
		background = tools.Settings.getInteger('interface.stream.progress') == 1
		interface.Loader.hide()
		progressDialog = interface.Dialog.progress(background = background, title = title, message = message)

		timeout = 90 # 60 too little for slow connections, eg over VPN.
		for i in range(0, timeout):
			if self.isPlayingVideo(): break
			if self.download == None:
				try: canceled = progressDialog.iscanceled()
				except: canceled = False
				if canceled: break

				label = message + ' ' + dots
				dots += '.'
				if len(dots) > 3: dots = ''

				progress = 50 + int((i / float(timeout)) * 50) # Only half the progress, since the other half is from sources __init__.py.
				if background: progressDialog.update(progress, title, label)
				else: progressDialog.update(progress, label)
			else:
				self._downloadCheck()
			xbmc.sleep(500)

		try: canceled = progressDialog.iscanceled()
		except: canceled = False

		try:
			if not canceled:
				progressDialog.update(100, '') # Must be set to 100 for background dialog, otherwise it shows up in a later dialog.
		except: pass

		try: progressDialog.close()
		except: pass

		if canceled:
			self.stop()
			return

		# Kodi often starts playback where isPlaying() is true and isPlayingVideo() is false, since the video loading is still in progress, whereas the play is already started.
		# Only show the notification if the player is not able to load the file at all.
		if not self.isPlaying() and not self.isPlayingVideo():
			interface.Dialog.notification(title = 33448, message = 33450, icon = interface.Dialog.IconError)

		# NB: Overlay is 7 when movie stopped and resumed, causing the movie to be never added to Trakt.
		'''if overlay == '7':

			while self.isPlayingVideo():
				try:
					self.totalTime = self.getTotalTime()
					self.currentTime = self.getTime()
				except:
					pass

				if self.download == None:
					xbmc.sleep(2000)
				else:
					for i in range(4):
						self._downloadCheck()
						xbmc.sleep(500)


		elif self.content == 'movie':'''
		if self.content == 'movie':
			while self.isPlayingVideo():
				try:
					self.totalTime = self.getTotalTime()
					self.currentTime = self.getTime()

					watcher = (self.currentTime / self.totalTime >= .8)
					property = control.window.getProperty(pname)

					if watcher == True and not property == '7':
						control.window.setProperty(pname, '7')
						playcount.markMovieDuringPlayback(self.imdb, '7')

					elif watcher == False and not property == '6':
						control.window.setProperty(pname, '6')
						playcount.markMovieDuringPlayback(self.imdb, '6')
				except:
					pass

				if self.download == None:
					xbmc.sleep(2000)
				else:
					for i in range(4):
						self._downloadCheck()
						xbmc.sleep(500)


		elif self.content == 'episode':

			while self.isPlayingVideo():
				try:
					self.totalTime = self.getTotalTime()
					self.currentTime = self.getTime()

					watcher = (self.currentTime / self.totalTime >= .8)
					property = control.window.getProperty(pname)

					if watcher == True and not property == '7':
						control.window.setProperty(pname, '7')
						playcount.markEpisodeDuringPlayback(self.imdb, self.tvdb, self.season, self.episode, '7')

					elif watcher == False and not property == '6':
						control.window.setProperty(pname, '6')
						playcount.markEpisodeDuringPlayback(self.imdb, self.tvdb, self.season, self.episode, '6')
				except:
					pass

				if self.download == None:
					xbmc.sleep(2000)
				else:
					for i in range(4):
						self._downloadCheck()
						xbmc.sleep(500)


		control.window.clearProperty(pname)


	def libForPlayback(self):
		try:
			if self.DBID == None: raise Exception()

			if self.content == 'movie':
				rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)
			elif self.content == 'episode':
				rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)

			control.jsonrpc(rpc) ; control.refresh()
		except:
			pass


	def idleForPlayback(self):
		for i in range(0, 200):
			if control.condVisibility('Window.IsActive(busydialog)') == 1: control.idle()
			else: break
			control.sleep(100)


	def onPlayBackStarted(self):
		self.status = self.StatusPlaying
		control.execute('Dialog.Close(all,true)')
		if not self.offset == '0': self.seekTime(float(self.offset))
		subtitles().get(self.name, self.imdb, self.season, self.episode)
		self.idleForPlayback()


	def onPlayBackPaused(self):
		self.status = self.StatusPaused


	def onPlayBackResumed(self):
		self.status = self.StatusPlaying


	def onPlayBackStopped(self):
		self.status = self.StatusStopped

		bookmarks().reset(self.currentTime, self.totalTime, self.name, self.year)
		self._downloadStop()
		self._debridClear()


	def onPlayBackEnded(self):
		self.status = self.StatusEnded

		self.libForPlayback()
		self.onPlayBackStopped()

		self._downloadClear()
		self._debridClear()


class subtitles:
	def get(self, name, imdb, season, episode):
		try:
			if not control.setting('subtitles.enabled') == 'true': raise Exception()


			langDict = {'Afrikaans': 'afr', 'Albanian': 'alb', 'Arabic': 'ara', 'Armenian': 'arm', 'Basque': 'baq', 'Bengali': 'ben', 'Bosnian': 'bos', 'Breton': 'bre', 'Bulgarian': 'bul', 'Burmese': 'bur', 'Catalan': 'cat', 'Chinese': 'chi', 'Croatian': 'hrv', 'Czech': 'cze', 'Danish': 'dan', 'Dutch': 'dut', 'English': 'eng', 'Esperanto': 'epo', 'Estonian': 'est', 'Finnish': 'fin', 'French': 'fre', 'Galician': 'glg', 'Georgian': 'geo', 'German': 'ger', 'Greek': 'ell', 'Hebrew': 'heb', 'Hindi': 'hin', 'Hungarian': 'hun', 'Icelandic': 'ice', 'Indonesian': 'ind', 'Italian': 'ita', 'Japanese': 'jpn', 'Kazakh': 'kaz', 'Khmer': 'khm', 'Korean': 'kor', 'Latvian': 'lav', 'Lithuanian': 'lit', 'Luxembourgish': 'ltz', 'Macedonian': 'mac', 'Malay': 'may', 'Malayalam': 'mal', 'Manipuri': 'mni', 'Mongolian': 'mon', 'Montenegrin': 'mne', 'Norwegian': 'nor', 'Occitan': 'oci', 'Persian': 'per', 'Polish': 'pol', 'Portuguese': 'por,pob', 'Portuguese(Brazil)': 'pob,por', 'Romanian': 'rum', 'Russian': 'rus', 'Serbian': 'scc', 'Sinhalese': 'sin', 'Slovak': 'slo', 'Slovenian': 'slv', 'Spanish': 'spa', 'Swahili': 'swa', 'Swedish': 'swe', 'Syriac': 'syr', 'Tagalog': 'tgl', 'Tamil': 'tam', 'Telugu': 'tel', 'Thai': 'tha', 'Turkish': 'tur', 'Ukrainian': 'ukr', 'Urdu': 'urd'}

			codePageDict = {'ara': 'cp1256', 'ar': 'cp1256', 'ell': 'cp1253', 'el': 'cp1253', 'heb': 'cp1255', 'he': 'cp1255', 'tur': 'cp1254', 'tr': 'cp1254', 'rus': 'cp1251', 'ru': 'cp1251'}

			quality = ['bluray', 'hdrip', 'brrip', 'bdrip', 'dvdrip', 'webrip', 'hdtv']

			settingsLanguages = tools.Language.settings()

			langs = []
			try:
				lang = control.setting('subtitles.language.primary')
				if lang.lower() == tools.Language.Automatic:
					if len(settingsLanguages) == 0:
						lang = tools.Language.EnglishName
					else:
						lang = settingsLanguages[0][1]
				if not lang in langDict:
					lang = tools.Language.EnglishName

				try: langs = langDict[lang].split(',')
				except: langs.append(langDict[lang])
			except:
				tools.Logger.error()
				pass
			try:
				lang = control.setting('subtitles.language.secondary')
				if lang.lower() == tools.Language.Automatic:
					if len(settingsLanguages) == 0:
						lang = tools.Language.EnglishName
					elif len(settingsLanguages) == 1:
						lang = settingsLanguages[0][1]
					elif len(settingsLanguages) == 2 and not settingsLanguages[1][1] in langs:
						lang = settingsLanguages[1][1]
					elif len(settingsLanguages) == 3:
						lang = settingsLanguages[2][1]
					else:
						lang = settingsLanguages[0][1]
				if not lang in langDict:
					lang = tools.Language.EnglishName

				try: langs = langs + langDict[lang].split(',')
				except: langs.append(langDict[lang])
			except: pass

			try: subLang = xbmc.Player().getSubtitles()
			except: subLang = ''
			if subLang == langs[0]: raise Exception()

			server = xmlrpclib.Server('http://api.opensubtitles.org/xml-rpc', verbose=0)
			token = server.LogIn('', '', 'en', 'XBMC_Subtitles_v1')['token']

			sublanguageid = ','.join(langs) ; imdbid = re.sub('[^0-9]', '', imdb)

			if not (season == None or episode == None):
				result = server.SearchSubtitles(token, [{'sublanguageid': sublanguageid, 'imdbid': imdbid, 'season': season, 'episode': episode}])['data']
				fmt = ['hdtv']
			else:
				result = server.SearchSubtitles(token, [{'sublanguageid': sublanguageid, 'imdbid': imdbid}])['data']
				try: vidPath = xbmc.Player().getPlayingFile()
				except: vidPath = ''
				fmt = re.split('\.|\(|\)|\[|\]|\s|\-', vidPath)
				fmt = [i.lower() for i in fmt]
				fmt = [i for i in fmt if i in quality]

			filter = []
			result = [i for i in result if i['SubSumCD'] == '1']

			for lang in langs:
				filter += [i for i in result if i['SubLanguageID'] == lang and any(x in i['MovieReleaseName'].lower() for x in fmt)]
				filter += [i for i in result if i['SubLanguageID'] == lang and any(x in i['MovieReleaseName'].lower() for x in quality)]
				filter += [i for i in result if i['SubLanguageID'] == lang]

			try: lang = xbmc.convertLanguage(filter[0]['SubLanguageID'], xbmc.ISO_639_1)
			except: lang = filter[0]['SubLanguageID']

			content = [filter[0]['IDSubtitleFile'],]
			content = server.DownloadSubtitles(token, content)
			content = base64.b64decode(content['data'][0]['data'])
			content = str(zlib.decompressobj(16+zlib.MAX_WBITS).decompress(content))

			subtitle = tools.System.temporary(directory = 'subtitles', file = '%s.%s.srt' % (name, lang)) # Keep the file name with language between dots, because Kodi uses this format to detect the language if the SRT.

			codepage = codePageDict.get(lang, '')
			if codepage and control.setting('subtitles.foreign') == 'true':
				try:
					content_encoded = codecs.decode(content, codepage)
					content = codecs.encode(content_encoded, 'utf-8')
				except:
					pass

			file = control.openFile(subtitle, 'w')
			file.write(str(content))
			file.close()

			xbmc.sleep(1000)
			xbmc.Player().setSubtitles(subtitle)
		except:
			pass


class bookmarks:
	def get(self, name, year='0'):
		try:
			year = str(year)
			offset = '0'

			if not control.setting('general.bookmarks') == 'true': raise Exception()

			idFile = hashlib.md5()
			for i in name: idFile.update(str(i))
			for i in year: idFile.update(str(i))
			idFile = str(idFile.hexdigest())

			dbcon = database.connect(control.bookmarksFile)
			dbcur = dbcon.cursor()
			dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
			match = dbcur.fetchone()
			self.offset = str(match[1])
			dbcon.commit()

			if self.offset == '0': raise Exception()

			minutes, seconds = divmod(float(self.offset), 60) ; hours, minutes = divmod(minutes, 60)
			label = '%02d:%02d:%02d' % (hours, minutes, seconds)
			label = (control.lang(32502) % label).encode('utf-8')

			try: yes = control.dialog.contextmenu([label, control.lang(32501).encode('utf-8'), ])
			except: yes = control.yesnoDialog(label, '', '', str(name), control.lang(32503).encode('utf-8'), control.lang(32501).encode('utf-8'))

			if yes: self.offset = '0'

			return self.offset
		except:
			return offset


	def reset(self, currentTime, totalTime, name, year='0'):
		try:
			year = str(year)
			if not control.setting('general.bookmarks') == 'true': raise Exception()

			timeInSeconds = str(currentTime)
			ok = int(currentTime) > 180 and (currentTime / totalTime) <= .92

			idFile = hashlib.md5()
			for i in name: idFile.update(str(i))
			for i in year: idFile.update(str(i))
			idFile = str(idFile.hexdigest())

			control.makeFile(control.dataPath)
			dbcon = database.connect(control.bookmarksFile)
			dbcur = dbcon.cursor()
			dbcur.execute("CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
			dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
			if ok: dbcur.execute("INSERT INTO bookmark Values (?, ?)", (idFile, timeInSeconds))
			dbcon.commit()
		except:
			pass
