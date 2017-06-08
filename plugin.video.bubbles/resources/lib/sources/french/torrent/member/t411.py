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

import re,urllib,urlparse,json
from resources.lib.modules import client
from resources.lib.extensions import metadata
from resources.lib.extensions import tools

class source:

	def __init__(self):
		self.pack = True # Checked by provider.py
		self.priority = 0
		self.language = ['fr']
		self.domains = ['api.t411.al']
		self.base_link = 'https://api.t411.al'
		self.login_link = '/auth'
		self.search_link = '/torrents/search/%s?limit=5000'
		self.download_link = '/torrents/download/%s'
		self.category_movie = ['455', '631', '633', '634', '635']
		self.category_show = ['433', '637', '639']

		self.enabled = tools.Settings.getBoolean('accounts.providers.t411.enabled')
		self.username = tools.Settings.getString('accounts.providers.t411.user')
		self.password = tools.Settings.getString('accounts.providers.t411.pass')

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

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if url == None:
				raise Exception()

			if not self.enabled or self.username == '' or self.password == '':
				raise Exception()

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			year = int(data['year']) if 'year' in data and not data['year'] == None else None
			season = int(data['season']) if 'season' in data and not data['season'] == None else None
			episode = int(data['episode']) if 'episode' in data and not data['episode'] == None else None
			pack = data['pack'] if 'pack' in data else False

			category = self.category_show if 'tvshowtitle' in data else self.category_movie

			if 'tvshowtitle' in data:
				if pack: query = '%s %d' % (title, season)
				else: query = '%s S%02dE%02d' % (title, season, episode)
			else:
				query = '%s %d' % (title, year)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
			querySplit = query.split()

			# Login
			login = self.base_link + self.login_link
			post = urllib.urlencode({'username': self.username, 'password': self.password})
			result = client.request(login, post = post)
			result = json.loads(result)
			headers = {'Authorization' : result['token']}

			url = urlparse.urljoin(self.base_link, self.search_link % query)
			result = client.request(url, headers = headers)
			result = json.loads(result)
			items = result['torrents']

			for item in items:
				if item['category'] in category:
					jsonId = item['id']
					jsonName = item['name']

					try: jsonSeeds = int(item['seeders'])
					except: jsonSeeds = 0

					jsonLink = self.base_link + self.download_link
					jsonLink = jsonLink % jsonId
					if not headers == None:
						jsonLink += '|' + urllib.urlencode(headers)

					try: jsonSize = int(item['size'])
					except: jsonSize = None

					# Metadata
					meta = metadata.Metadata(name = jsonName, title = title, year = year, season = season, episode = episode, pack = pack, link = jsonLink, size = jsonSize, seeds = jsonSeeds)

					# Ignore
					if meta.ignore(True):
						continue

					# Add
					sources.append({'url' : jsonLink, 'debridonly' : False, 'direct' : False, 'source' : 'torrent', 'language' : self.language[0], 'quality':  meta.videoQuality(), 'info' : meta.information(), 'file' : jsonName})

			return sources
		except:
			return sources

	def resolve(self, url):
		return url
