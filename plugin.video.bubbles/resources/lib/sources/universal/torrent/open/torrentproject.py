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
from resources.lib.modules import client
from resources.lib.extensions import metadata
from resources.lib.extensions import tools
from resources.lib.extensions import network
from resources.lib.externals.beautifulsoup import BeautifulSoup

class source:

	def __init__(self):
		self.pack = True # Checked by provider.py
		self.priority = 0
		self.language = ['un']
		self.domains = ['torrentproject.se', 'torrentproject-se.unblocked.cool', 'torrentproject-se.proxydude.xyz', 'torrentproject4-se.unblocked.lol']
		self.base_link = 'https://torrentproject.se'
		self.search_link = '/?hl=en&safe=on&num=100&start=%d&orderby=seeders&s=%s&filter=2000'

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
			querySplit = query.split()

			url = urlparse.urljoin(self.base_link, self.search_link)

			page = 0 # Pages start at 0
			added = False

			timerEnd = tools.Settings.getInteger('scraping.providers.timeout') - 8
			timer = tools.Time(start = True)

			while True:
				# Stop searching 8 seconds before the provider timeout, otherwise might continue searching, not complete in time, and therefore not returning any links.
				if timer.elapsed() > timerEnd:
					break

				urlNew = url % (page, urllib.quote_plus(query))
				html = BeautifulSoup(client.request(urlNew))

				page += 1
				added = False

				htmlTable = html.find_all('div', id = 'ires')[0].find_all('ol', recursive = False)[0]
				htmlRows = htmlTable.find_all('li', recursive = False) # Do not search further down the tree (just the direct children), because that will also retrieve the header row.

				for i in range(len(htmlRows)):
					row1 = htmlRows[i].find_all('h3', class_ = 'r')[0]
					row2 = htmlRows[i].find_all('div', class_ = 'sti')[0]

					# Name
					htmlName = row1.find_all('a', class_ = 'tl', recursive = False)[0].getText().strip()

					# Link
					htmlHash = row1.find_all('a', class_ = 'tl', recursive = False)[0]['href']
					if htmlHash.startswith('/'):
						htmlHash = htmlHash[1:]
					index = htmlHash.find('/')
					if index > 0:
						htmlHash = htmlHash[:index]
					if not tools.Hash.valid(htmlHash):
						continue
					htmlLink = network.Container(htmlHash).torrentMagnet(title = query)

					# Size
					htmlSize = row2.find_all('span', class_ = 'torrent-size')[0].getText().strip()

					# Seeds
					htmlSeeds = int(row2.find_all('span', class_ = 'seeders')[0].find_all('span', class_ = 'gac_b')[0].getText().strip())

					# Metadata
					meta = metadata.Metadata(name = htmlName, title = title, year = year, season = season, episode = episode, pack = pack, link = htmlLink, size = htmlSize, seeds = htmlSeeds)

					# Ignore
					if meta.ignore(True):
						continue

					# Ignore Name
					# TorrentProject has a lot of season packs, foreign titles, and other torrents that should be excluded. If the name does not contain the exact search string, ignore the result.
					if not all(q in htmlName for q in querySplit):
						continue

					# Add
					sources.append({'url' : htmlLink, 'debridonly' : False, 'direct' : False, 'source' : 'torrent', 'language' : self.language[0], 'quality':  meta.videoQuality(), 'info' : meta.information(), 'file' : htmlName})
					added = True

				if not added: # Last page reached with a working torrent
					break

			return sources
		except:
			return sources

	def resolve(self, url):
		return url
