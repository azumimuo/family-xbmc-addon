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

import re,urllib,urlparse,xbmc
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.extensions import metadata
from resources.lib.extensions import tools
from resources.lib.externals.beautifulsoup import BeautifulSoup

class source:
	def __init__(self):
		self.pack = True # Checked by provider.py
		self.priority = 0
		self.language = ['un']
		self.domains = ['nzbclub.com']
		self.base_link = 'https://www.nzbclub.com'
		self.search_link = '/search.aspx?q=%s&st=5&page=%d' # st=5 sorts by relevance/score
		self.download_link = '/nzb_get/'

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

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			year = int(data['year']) if 'year' in data and not data['year'] == None else None
			season = int(data['season']) if 'season' in data and not data['season'] == None else None
			episode = int(data['episode']) if 'episode' in data and not data['episode'] == None else None
			pack = data['pack'] if 'pack' in data else False

			if 'tvshowtitle' in data:
				if pack: query = '%s %d' % (title, season)
				else: query = '%s S%02dE%02d' % (title, season, episode)
			else:
				query = '%s %d' % (title, year)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

			url = urlparse.urljoin(self.base_link, self.search_link)

			page = 1 # Pages start at 1
			added = False

			timerEnd = tools.Settings.getInteger('scraping.providers.timeout') - 8
			timer = tools.Time(start = True)

			while True:
				# Stop searching 8 seconds before the provider timeout, otherwise might continue searching, not complete in time, and therefore not returning any links.
				if timer.elapsed() > timerEnd:
					break

				urlNew = url % (urllib.quote_plus(query), page)
				html = BeautifulSoup(client.request(urlNew))

				page += 1
				added = False

				htmlTable = html.find_all('span', id = 'ui_searchResult')[0]
				htmlRows = htmlTable.find_all('div', class_ = 'panel-body')

				for i in range(len(htmlRows)):
					htmlRow = htmlRows[i].find_all('div', class_ = 'media', recursive = False)[0].find_all('div', class_ = 'row', recursive = False)[0]
					htmlColumns = htmlRow.find_all('div', recursive = False) # Use children and no further.
					htmlInfo = htmlColumns[0]

					# Name
					htmlName = htmlInfo.find_all('a', class_ = 'text-primary')
					if len(htmlName) == 0: # 'Dangerous' items (encrypted or incompelte - see below at the ignore section) have a text-muted class and are already filtered out here.
						continue
					else:
						htmlName = htmlName[0].getText()

					# Size
					htmlSize = htmlColumns[1].getText().replace('&nbsp;', ' ')
					htmlSize = htmlSize.splitlines()[0] # Otherwise the find function does not work.
					indexEnd = htmlSize.find(' ', htmlSize.find(' ') + 1) # Second index
					htmlSize = htmlSize[: indexEnd]

					# Link
					htmlId = htmlColumns[3].find_all('div', class_ = 'author-info')[0].find_all('div')
					for id in htmlId:
						if id.has_attr('collectionid'):
							htmlId = id['collectionid']
							break
					htmlLink = self.base_link + self.download_link + htmlId

					# Age
					htmlAge = htmlColumns[2].getText()
					htmlAge = int(htmlAge[: htmlAge.find(' ')])

					# Metadata
					meta = metadata.Metadata(name = htmlName, title = title, year = year, season = season, episode = episode, pack = pack, link = htmlLink, size = htmlSize, age = htmlAge)

					# Ignore
					if meta.ignore(False):
						continue

					htmlDanger = htmlInfo.find_all('small')[1].find_all('span', _class = 'text-danger')
					ignore = False
					for danger in htmlDanger:
						danger = danger['title']
						if danger.startswith('incomplete'): # Ignore files marked as incomplete.
							ignore = True
						if danger.find('password') >= 0 or htmlDanger.find('encrypted') >= 0: # Ignore password-protected files
							ignore = True
					if ignore:
						continue

					# Add
					# Some NZBs have the wrong size (often a few KB) indicated on the site, but are in reaility bigger. Hence, do not show the size of NZBs below 20MB, but still add them.
					sources.append({'url' : htmlLink, 'debridonly' : False, 'direct' : False, 'source' : 'usenet', 'language' : self.language[0], 'quality':  meta.videoQuality(), 'info' : meta.information(sizeLimit = 20971520), 'file' : htmlName})
					added = True

				if not added: # Last page reached with a working torrent
					break

			return sources
		except:
			return sources

	def resolve(self, url):
		return url
