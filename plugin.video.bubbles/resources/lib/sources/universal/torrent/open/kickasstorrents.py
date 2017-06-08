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
		self.domains = ['kat.how', 'kickasstorrents.video', 'kickasstorrents.to', 'katcr.to', 'kat.am',  'kickass.cd', 'kickass.ukbypass.pro', 'kickass.unlockproject.review'] # Most of these links seem to have a different page layout than kat.how.
		self.base_link = 'https://kat.how' # Link must have the name for provider verification.
		self.search_link = '/usearch/%s/?field=seeders&sorder=desc'

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

			page = 0 # Pages start at 0
			added = False

			#while True:
			while page == 0: # KickassTorrents currently has a problem to view any other page than page 1 while sorted by seeders. Only view first page.
				urlNew = url % (urllib.quote_plus(query))
				html = client.request(urlNew)

				# KickassTorrents has major mistakes in their HTML. manually remove parts to create new HTML.
				indexStart = html.find('<', html.find('<!-- Start of Loop -->') + 1)
				indexEnd = html.rfind('<!-- End of Loop -->')
				html = html[indexStart : indexEnd]

				html = html.replace('<div class="markeredBlock', '</div><div class="markeredBlock') # torrentname div tag not closed.
				html = html.replace('</span></td>', '</td>') # Dangling </span> closing tag.

				html = BeautifulSoup(html)

				page += 1
				added = False

				htmlRows = html.find_all('tr', recursive = False) # Do not search further down the tree (just the direct children).
				for i in range(len(htmlRows)):
					htmlRow = htmlRows[i]
					if 'firstr' in htmlRow['class']: # Header.
						continue
					htmlColumns = htmlRow.find_all('td')
					htmlInfo = htmlColumns[0]

					# Name
					htmlName = htmlInfo.find_all('a', class_ = 'cellMainLink')[0].getText().strip()

					# Size
					htmlSize = htmlColumns[1].getText().replace('&nbsp;', ' ')

					# Link
					htmlLink = ''
					htmlLinks = htmlInfo.find_all('a')
					for j in range(len(htmlLinks)):
						link = htmlLinks[j]
						if link.has_attr('href'):
							link = link['href']
							if link.startswith('magnet:'):
								htmlLink = link
								break

					# Seeds
					htmlSeeds = int(htmlColumns[3].getText())

					# Metadata
					meta = metadata.Metadata(name = htmlName, title = title, year = year, season = season, episode = episode, pack = pack, link = htmlLink, size = htmlSize, seeds = htmlSeeds)

					# Ignore
					if meta.ignore(True):
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
