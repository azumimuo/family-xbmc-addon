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

import re,urllib,urlparse,time,threading
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.extensions import metadata
from resources.lib.extensions import tools
from resources.lib.extensions import debrid

class source:
	def __init__(self):
		self.pack = True # Checked by provider.py
		self.priority = 0
		self.language = ['un']
		self.domains = ['premiumize.me']
		self.base_link = 'https://www.premiumize.me'
		self.mutex = threading.Lock()
		self.items = []

	def movie(self, imdb, title, localtitle, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtitle, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url == None: return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urllib.urlencode(url)
			return url
		except:
			return

	def _item(self, id, season, episode):
		item = debrid.Premiumize().item(id = id, transfer = False, content = True, season = season, episode = episode)
		try: self.mutex.acquire()
		except: pass
		if item: self.items.append(item)
		try: self.mutex.release()
		except: pass

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if url == None:
				raise Exception()

			premiumize = debrid.Premiumize()

			if not premiumize.accountValid():
				raise Exception()

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			year = int(data['year']) if 'year' in data and not data['year'] == None else None
			season = int(data['season']) if 'season' in data and not data['season'] == None else None
			episode = int(data['episode']) if 'episode' in data and not data['episode'] == None else None
			pack = data['pack'] if 'pack' in data else False

			timerEnd = tools.Settings.getInteger('scraping.providers.timeout') - 3
			timer = tools.Time(start = True)

			threads = []
			ids = []
			items = premiumize._itemsTransfer()
			for item in items:
				if item['transfer']['progress']['completed']['value'] == 1: # Only finished downloads.
					id = item['id']
					if not id in ids:
						meta = metadata.Metadata(name = item['name'], title = title, year = year, season = season, episode = episode, pack = pack)
						if not meta.ignore(size = False):
							ids.append(id)
							threads.append(threading.Thread(target = self._item, args = (id, season, episode)))

			[thread.start() for thread in threads]

			while True:
				if timer.elapsed() > timerEnd:
					break
				if all([not thread.is_alive() for thread in threads]):
					break
				time.sleep(0.5)

			try: self.mutex.acquire()
			except: pass
			items = self.items
			try: self.mutex.release()
			except: pass

			for item in items:
				jsonName = item['video']['name']
				jsonLink = item['video']['link']
				jsonSize = item['video']['size']['bytes']

				# RAR Files
				if jsonLink.lower().endswith('.rar'):
					continue

				# Metadata
				meta = metadata.Metadata(name = jsonName, title = title, year = year, season = season, episode = episode, size = jsonSize)

				# Add
				sources.append({'url' : jsonLink, 'premium' : True, 'debridonly' : True, 'direct' : True, 'memberonly' : True, 'source' : 'Premiumize', 'language' : self.language[0], 'quality':  meta.videoQuality(), 'info' : meta.information(), 'file' : jsonName})

			return sources
		except:
			return sources

	def resolve(self, url):
		return url
