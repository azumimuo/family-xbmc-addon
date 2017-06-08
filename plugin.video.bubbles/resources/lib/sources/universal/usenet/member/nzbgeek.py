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

import re,urllib,urlparse,xbmc,json,datetime
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.extensions import metadata
from resources.lib.extensions import tools
from resources.lib.externals.beautifulsoup import BeautifulSoup

class source:
	def __init__(self):
		self.pack = False # Checked by provider.py
		self.priority = 0
		self.language = ['un']
		self.domains = ['api.nzbgeek.info']
		self.base_link = 'https://api.nzbgeek.info'
		self.search_link = '/api?o=json&apikey=%s&minsize=%d'
		self.movie_link = '&t=movie&imdbid=%s'
		self.show_link = '&t=tvsearch&tvdbid=%s&season=%d&ep=%d'
		self.enabled = control.setting('accounts.providers.nzbgeek.enabled') == 'true'
		self.api = control.setting('accounts.providers.nzbgeek.api')

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

			if not (self.enabled and self.api and not self.api == ''):
				raise Exception()

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			year = int(data['year']) if 'year' in data and not data['year'] == None else None
			imdb = data['imdb'].replace('tt', '') if 'imdb' in data else None
			tvdb = data['tvdb'] if 'tvdb' in data else None
			season = int(data['season']) if 'season' in data and not data['season'] == None else None
			episode = int(data['episode']) if 'episode' in data and not data['episode'] == None else None
			pack = data['pack'] if 'pack' in data else False
			if pack: raise Exception() # Currently not supported. Will need a general search.

			url = self.base_link + (self.search_link % (self.api, metadata.Metadata.IgnoreSize))
			if not tvdb == None:
				url += self.show_link % (tvdb, season, episode)
			else:
				url += self.movie_link % (imdb)

			result = json.loads(client.request(url))

			for item in result['channel']['item']:
				jsonName = item['title']

				jsonLink = item['link']
				# Contains HTML enteties such as &amp;
				# Add wrapper to link, otherwise BeautifulSoup gives a lot of warnings.
				jsonLink = '[BUBBLES]' + jsonLink + '[BUBBLES]'
				jsonLink = BeautifulSoup(jsonLink).contents
				jsonLink = jsonLink[0].replace('[BUBBLES]', '')

				jsonAge = item['pubDate']
				jsonAge = jsonAge[jsonAge.find(',') + 2 : jsonAge.find(':') - 3]
				jsonAge = tools.Time.datetime(jsonAge, '%d %b %Y')
				jsonAge = datetime.datetime.today() - jsonAge
				jsonAge = jsonAge.days

				jsonSize = None
				try:
					for attribute in item['attr']:
						attribute = attribute['@attributes']
						if attribute['name'] == 'size':
							jsonSize = int(attribute['value'])
							break
				except:
					pass

				# Metadata
				meta = metadata.Metadata(name = jsonName, title = title, year = year, season = season, episode = episode, pack = pack, link = jsonLink, size = jsonSize, age = jsonAge)

				# Ignore
				if meta.ignore(True):
					continue

				# Add
				sources.append({'url' : jsonLink, 'debridonly' : False, 'direct' : False, 'memberonly' : True, 'source' : 'usenet', 'language' : self.language[0], 'quality':  meta.videoQuality(), 'info' : meta.information(), 'file' : jsonName})

			return sources
		except:
			return sources

	def resolve(self, url):
		return url
