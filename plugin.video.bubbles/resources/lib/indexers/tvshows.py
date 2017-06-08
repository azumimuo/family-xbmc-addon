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


from resources.lib.modules import trakt
from resources.lib.modules import cleantitle
from resources.lib.modules import cleangenre
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import workers
from resources.lib.modules import views

# [BUBBLESCODE]
from resources.lib.extensions import tools
from resources.lib.extensions import interface
from resources.lib.externals.beautifulsoup import BeautifulSoup
# [/BUBBLESCODE]

import os,sys,re,json,urllib,urlparse,datetime

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')


class tvshows:

	def __init__(self, type = tools.Media.TypeShow, kids = tools.Selection.TypeUndefined):
		self.count = 60

		self.type = type

		self.kids = kids
		self.certificates = None
		self.restriction = 0

		if self.kidsOnly():
			self.certificates = []
			self.restriction = tools.Settings.getInteger('general.kids.restriction')
			if self.restriction >= 0:
				self.certificates.append('TV-Y')
			if self.restriction >= 1:
				self.certificates.append('TV-Y7')
			if self.restriction >= 2:
				self.certificates.append('TV-PG')
			if self.restriction >= 3:
				self.certificates.append('TV-14')
			self.certificates = ','.join(self.certificates).replace('-', '_').lower()
			self.certificates = '&certificates=us:' + self.certificates
		else:
			self.certificates = ''

		self.list = []

		self.imdb_link = 'http://www.imdb.com'
		self.trakt_link = 'http://api-v2launch.trakt.tv'
		self.tvmaze_link = 'http://www.tvmaze.com'
		self.tvdb_key = 'MDk1NUY1N0Q5QTlENEZEQw=='
		self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

		# [BUBBLESCODE]

		self.trakt_user = control.setting('accounts.informants.trakt.user').strip() if control.setting('accounts.informants.trakt.enabled') else ''
		self.imdb_user = control.setting('accounts.informants.imdb.user').replace('ur', '') if control.setting('accounts.informants.imdb.enabled') else ''
		self.fanart_tv_user = control.setting('accounts.artwork.fanart.api') if control.setting('accounts.artwork.fanart.enabled') else ''
		self.user = self.fanart_tv_user + str('')

		# [/BUBBLESCODE]
		self.lang = control.apiLanguage()['tvdb']

		self.search_link = 'http://api-v2launch.trakt.tv/search?type=show&limit=20&page=1&query='
		self.tvmaze_info_link = 'http://api.tvmaze.com/shows/%s'
		self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key.decode('base64'), '%s', self.lang)
		self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'
		self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'
		self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
		self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
		self.tvdb_image = 'http://thetvdb.com/banners/'

		self.persons_link = 'http://www.imdb.com/search/name?count=100&name='
		self.personlist_link = 'http://www.imdb.com/search/name?count=100&gender=male,female'
		self.featured_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=100,&production_status=released&release_date=date[365],date[60]&sort=moviemeter,asc&count=%d&start=1%s' % (self.count, self.certificates)
		self.popular_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=100,&release_date=,date[0]&sort=moviemeter,asc&count=%d&start=1%s' % (self.count, self.certificates)
		self.airing_link = 'http://www.imdb.com/search/title?title_type=tv_episode&release_date=date[1],date[0]&sort=moviemeter,asc&count=%d&start=1%s' % (self.count, self.certificates)
		self.active_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=10,&production_status=active&sort=moviemeter,asc&count=%d&start=1%s' % (self.count, self.certificates)
		self.premiere_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=10,&release_date=date[60],date[0]&sort=moviemeter,asc&count=%d&start=1%s' % (self.count, self.certificates)

		if self.kidsOnly():
			self.rating_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=10000,&release_date=,date[0]&sort=user_rating,desc&count=%d&start=1%s' % (self.count, self.certificates)
		else:
			self.rating_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=50000,&release_date=,date[0]&sort=user_rating,desc&count=%d&start=1%s' % (self.count, self.certificates)

		self.views_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&release_date=,date[0]&sort=num_votes,desc&count=%d&start=1%s' % (self.count, self.certificates)
		self.person_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&role=%s&sort=year,desc&count=%d&start=1%s' % ('%s', self.count, self.certificates)
		self.genre_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=%s&sort=moviemeter,asc&count=%d&start=1%s' % ('%s', self.count, self.certificates)
		self.certification_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&certificates=us:%s&sort=moviemeter,asc&count=%d&start=1%s' % ('%s', self.count, self.certificates)
		self.trending_link = 'http://api-v2launch.trakt.tv/shows/trending?limit=%d&page=1' % self.count

		self.traktlists_link = 'http://api-v2launch.trakt.tv/users/me/lists'
		self.traktlikedlists_link = 'http://api-v2launch.trakt.tv/users/likes/lists?limit=1000000'
		self.traktlist_link = 'http://api-v2launch.trakt.tv/users/%s/lists/%s/items'
		self.traktcollection_link = 'http://api-v2launch.trakt.tv/users/me/collection/shows'
		self.traktwatchlist_link = 'http://api-v2launch.trakt.tv/users/me/watchlist/'
		self.traktrecommendations_link = 'http://api-v2launch.trakt.tv/recommendations/shows?limit=%d' % self.count
		self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
		self.imdblist_link = 'http://www.imdb.com/list/%s/?view=detail&sort=title:asc&title_type=tv_series,mini_series&start=1'
		self.imdblist2_link = 'http://www.imdb.com/list/%s/?view=detail&sort=created:desc&title_type=tv_series,mini_series&start=1'
		self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc' % self.imdb_user
		self.imdbwatchlist2_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user

		self.year_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=100,&production_status=released&year=%s,%s&sort=moviemeter,asc&count=%d&start=1%s' % ('%s', '%s', self.count, self.certificates)
		self.language_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&production_status=released&languages=%s&sort=moviemeter,asc&count=%d&start=1%s' % ('%s', self.count, self.certificates)
		self.emmies_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&production_status=released&groups=emmy_winners&sort=year,desc&count=%d&start=1%s' % (self.count, self.certificates)

	def parameterize(self, action):
		if not self.type == None: action += '&type=%s' % self.type
		if not self.kids == None: action += '&kids=%d' % self.kids
		return action

	def kidsOnly(self):
		return self.kids == tools.Selection.TypeInclude

	def get(self, url, idx=True):
		try:
			try: url = getattr(self, url + '_link')
			except: pass

			try: u = urlparse.urlparse(url).netloc.lower()
			except: pass


			if u in self.trakt_link and '/users/' in url:
				urls = []

				if '/watchlist/' in url:
					urls.append(url + 'shows')
					urls.append(url + 'seasons')
					urls.append(url + 'episodes')
				else:
					urls.append(url)

				lists = []
				for u in urls:
					self.list = []
					try:
						if not '/users/me/' in url: raise Exception()
						if trakt.getActivity() > cache.timeout(self.trakt_list, u, self.trakt_user): raise Exception()
						lists += cache.get(self.trakt_list, 0, u, self.trakt_user)
					except:
						lists += cache.get(self.trakt_list, 0, u, self.trakt_user)
				self.list = lists

				if '/users/me/' in url and not '/watchlist/' in url:
					self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['title'].lower()))

				if idx == True: self.worker()

			elif u in self.trakt_link and self.search_link in url:
				self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)
				if idx == True: self.worker(level=0)

			elif u in self.trakt_link:
				self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
				if idx == True: self.worker()


			elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
				self.list = cache.get(self.imdb_list, 0, url)
				if idx == True: self.worker()

			elif u in self.imdb_link:
				self.list = cache.get(self.imdb_list, 24, url)
				if idx == True: self.worker()


			elif u in self.tvmaze_link:
				self.list = cache.get(self.tvmaze_list, 168, url)
				if idx == True: self.worker()

			if len(self.list) == 0 and self.search_link in url:
				interface.Dialog.notification(title = 32010, message = 33049, icon = interface.Dialog.IconInformation)

			if self.kidsOnly():
				self.list = [i for i in self.list if 'mpaa' in i and tools.Kids.allowed(i['mpaa'])]

			if idx == True: self.tvshowDirectory(self.list)
			return self.list
		except:
			pass


	# [BUBBLESCODE]
	def search(self, terms = None):
		try:
			# NB: Sleeping here for a while seems to fix the problem of search results not showing.
			# Sleeping for 200ms seems not to be enough. 500ms also is sometimes to little.  800ms works most of the time, but still the results sometimes do not show.
			#control.idle()
			control.sleep(1000)

			from resources.lib.extensions import search

			if terms:
				if (terms == None or terms == ''): return
				search.Searches().updateShows(terms)
			else:
				t = control.lang(32010).encode('utf-8')
				k = control.keyboard('', t) ; k.doModal()
				terms = k.getText() if k.isConfirmed() else None
				if (terms == None or terms == ''): return
				search.Searches().insertShows(terms, self.kids)

			url = self.search_link + urllib.quote_plus(terms)
			url = '%s?action=tvshowPage&url=%s' % (sys.argv[0], urllib.quote_plus(url))
			url = self.parameterize(url)
			control.execute('Container.Update(%s)' % url)
		except:
			return
	# [/BUBBLESCODE]


	# [BUBBLESCODE]
	def person(self, terms = None):
		try:
			# NB: Sleeping here for a while seems to fix the problem of search results not showing.
			# Sleeping for 200ms seems not to be enough. 500ms also is sometimes to little.  800ms works most of the time, but still the results sometimes do not show.
			#control.idle()
			control.sleep(1000)

			from resources.lib.extensions import search

			if terms:
				if (terms == None or terms == ''): return
				search.Searches().updatePeople(terms)
			else:
				t = control.lang(32010).encode('utf-8')
				k = control.keyboard('', t) ; k.doModal()
				terms = k.getText() if k.isConfirmed() else None
				if (terms == None or terms == ''): return
				search.Searches().insertPeople(terms, self.kids)

			url = self.persons_link + urllib.quote_plus(terms)
			url = '%s?action=tvPersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
			url = self.parameterize(url)
			control.execute('Container.Update(%s)' % url)
		except:
			return
	# [/BUBBLESCODE]

	def genres(self):
		genres = []

		if not self.kidsOnly() or self.restriction >= 0:
			genres.extend([
				('Adventure', 'adventure'),
				('Animation', 'animation'),
				('Biography', 'biography'),
				('Comedy', 'comedy'),
				('Drama', 'drama'),
				('Family', 'family'),
				('Fantasy', 'fantasy'),
				('Game Show', 'game_show'),
				('History', 'history'),
				('Music ', 'music'),
				('Musical', 'musical'),
				('Sport', 'sport'),
			])
		if not self.kidsOnly() or self.restriction >= 1:
			genres.extend([
				('Mystery', 'mystery'),
				('Romance', 'romance'),
				('Science Fiction', 'sci_fi'),
			])
		if not self.kidsOnly() or self.restriction >= 2:
			genres.extend([
				('Action', 'action'),
				('Crime', 'crime'),
				('News', 'news'),
				('Reality Shows', 'reality_tv'),
				('Talk Show', 'talk_show'),
				('Thriller', 'thriller'),
				('Western', 'western'),
			])
		if not self.kidsOnly() or self.restriction >= 3:
			genres.extend([
				('Horror', 'horror'),
				('War', 'war'),
				('Film Noir', 'film_noir'),
			])

		genres = sorted(genres, key=lambda x: x[0])

		for i in genres: self.list.append({'name': cleangenre.lang(i[0], self.lang), 'url': self.genre_link % i[1], 'image': 'genres.png', 'action': self.parameterize('tvshows')})
		self.addDirectory(self.list)
		return self.list


	def networks(self):
		networks = []

		if not self.kidsOnly() or self.restriction >= 0:
			networks.extend([
				('Cartoon Network', '/networks/11/cartoon-network'),
				('Disney Channel', '/networks/78/disney-channel'),
				('Disney XD', '/networks/25/disney-xd'),
				('Nickelodeon', '/networks/27/nickelodeon'),
			])
		if not self.kidsOnly() or self.restriction >= 1:
			networks.extend([
				('Animal Planet', '/networks/92/animal-planet'),
			])
		if not self.kidsOnly() or self.restriction >= 2:
			networks.extend([
				('National Geographic', '/networks/42/national-geographic-channel'),
			])
		if not self.kidsOnly() or self.restriction >= 3:
			networks.extend([
				('Discovery Channel', '/networks/66/discovery-channel'),
				('History Channel', '/networks/53/history'),
				('MTV', '/networks/22/mtv'),
			])
		if not self.kidsOnly():
			networks.extend([
				('A&E', '/networks/29/ae'),
				('ABC', '/networks/3/abc'),
				('AMC', '/networks/20/amc'),
				('AT-X', '/networks/167/at-x'),
				('Adult Swim', '/networks/10/adult-swim'),
				('Amazon', '/webchannels/3/amazon'),
				('Audience', '/networks/31/audience-network'),
				('BBC America', '/networks/15/bbc-america'),
				('BBC Four', '/networks/51/bbc-four'),
				('BBC One', '/networks/12/bbc-one'),
				('BBC Three', '/webchannels/71/bbc-three'),
				('BBC Two', '/networks/37/bbc-two'),
				('BET', '/networks/56/bet'),
				('Bravo', '/networks/52/bravo'),
				('CBC', '/networks/36/cbc'),
				('CBS', '/networks/2/cbs'),
				('CTV', '/networks/48/ctv'),
				('CW', '/networks/5/the-cw'),
				('CW Seed', '/webchannels/13/cw-seed'),
				('Channel 4', '/networks/45/channel-4'),
				('Channel 5', '/networks/135/channel-5'),
				('Cinemax', '/networks/19/cinemax'),
				('Comedy Central', '/networks/23/comedy-central'),
				('Crackle', '/webchannels/4/crackle'),
				('Discovery ID', '/networks/89/investigation-discovery'),
				('E! Entertainment', '/networks/43/e'),
				('E4', '/networks/41/e4'),
				('FOX', '/networks/4/fox'),
				('FX', '/networks/13/fx'),
				('Freeform', '/networks/26/freeform'),
				('HBO', '/networks/8/hbo'),
				('HGTV', '/networks/192/hgtv'),
				('Hallmark', '/networks/50/hallmark-channel'),
				('ITV', '/networks/35/itv'),
				('Lifetime', '/networks/18/lifetime'),
				('NBC', '/networks/1/nbc'),
				('Netflix', '/webchannels/1/netflix'),
				('PBS', '/networks/85/pbs'),
				('Showtime', '/networks/9/showtime'),
				('Sky1', '/networks/63/sky-1'),
				('Starz', '/networks/17/starz'),
				('Sundance', '/networks/33/sundance-tv'),
				('Syfy', '/networks/16/syfy'),
				('TBS', '/networks/32/tbs'),
				('TLC', '/networks/80/tlc'),
				('TNT', '/networks/14/tnt'),
				('TV Land', '/networks/57/tvland'),
				('Travel Channel', '/networks/82/travel-channel'),
				('TruTV', '/networks/84/trutv'),
				('USA', '/networks/30/usa-network'),
				('VH1', '/networks/55/vh1'),
				('WGN', '/networks/28/wgn-america'),
			])

		networks = sorted(networks, key=lambda x: x[0])

		for i in networks: self.list.append({'name': i[0], 'url': self.tvmaze_link + i[1], 'image': 'networks.png', 'action': self.parameterize('tvshows')})
		self.addDirectory(self.list)
		return self.list


	def languages(self):
		languages = [
		('Afrikaans', 'af'),
		('Arabic', 'ar'),
		('Bulgarian', 'bg'),
		('Chinese', 'zh'),
		('Croatian', 'hr'),
		('Dutch', 'nl'),
		('English', 'en'),
		('Finnish', 'fi'),
		('French', 'fr'),
		('German', 'de'),
		('Greek', 'el'),
		('Hebrew', 'he'),
		('Hindi ', 'hi'),
		('Hungarian', 'hu'),
		('Icelandic', 'is'),
		('Italian', 'it'),
		('Japanese', 'ja'),
		('Korean', 'ko'),
		('Norwegian', 'no'),
		('Persian', 'fa'),
		('Polish', 'pl'),
		('Portuguese', 'pt'),
		('Punjabi', 'pa'),
		('Romanian', 'ro'),
		('Russian', 'ru'),
		('Spanish', 'es'),
		('Swedish', 'sv'),
		('Turkish', 'tr'),
		('Ukrainian', 'uk')
		]

		for i in languages: self.list.append({'name': str(i[0]), 'url': self.language_link % i[1], 'image': 'languages.png', 'action': self.parameterize('tvshows')})
		self.addDirectory(self.list)
		return self.list


	def certifications(self):
		certificates = []

		if not self.kidsOnly() or self.restriction >= 0:
			certificates.append(('Child Audience (Y)', 'TV-Y'))
		if not self.kidsOnly() or self.restriction >= 1:
			certificates.append(('Young Audience (Y7)', 'TV-Y7'))
		if not self.kidsOnly() or self.restriction >= 2:
			certificates.append(('Parental Guidance (PG)', 'TV-PG'))
		if not self.kidsOnly() or self.restriction >= 3:
			certificates.append(('Youth Audience (14)', 'TV-14'))
		if not self.kidsOnly():
			certificates.append(('Mature Audience (MA)', 'TV-MA'))

		for i in certificates: self.list.append({'name': str(i[0]), 'url': self.certification_link % str(i[1]).replace('-', '_').lower(), 'image': 'certificates.png', 'action': self.parameterize('tvshows')})
		self.addDirectory(self.list)
		return self.list

	def age(self):
		certificates = []

		if not self.kidsOnly() or self.restriction >= 0:
			certificates.append(('Minor (1+)', 'TV-Y'))
		if not self.kidsOnly() or self.restriction >= 1:
			certificates.append(('Young (7+)', 'TV-Y7'))
		if not self.kidsOnly() or self.restriction >= 2:
			certificates.append(('Teens (13+)', 'TV-PG'))
		if not self.kidsOnly() or self.restriction >= 3:
			certificates.append(('Youth (16+)', 'TV-14'))
		if not self.kidsOnly():
			certificates.append(('Mature (18+)', 'TV-MA'))

		for i in certificates: self.list.append({'name': str(i[0]), 'url': self.certification_link % str(i[1]).replace('-', '_').lower(), 'image': 'age.png', 'action': self.parameterize('tvshows')})
		self.addDirectory(self.list)
		return self.list


	def years(self):
		year = (self.datetime.strftime('%Y'))

		for i in range(int(year)-0, int(year)-100, -1): self.list.append({'name': str(i), 'url': self.year_link % (str(i), str(i)), 'image': 'calendar.png', 'action': self.parameterize('tvshows')})
		self.addDirectory(self.list)
		return self.list


	def persons(self, url):
		if url == None:
			self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
		else:
			self.list = cache.get(self.imdb_person_list, 1, url)

		# [BUBBLESCODE]
		if len(self.list) == 0:
			interface.Dialog.notification(title = 32010, message = 33049, icon = interface.Dialog.IconInformation)
		# [/BUBBLESCODE]

		for i in range(0, len(self.list)): self.list[i].update({'action': self.parameterize('tvshows')})
		self.addDirectory(self.list)
		return self.list


	def userlists(self, mode = None):
		if not mode == None:
			mode = mode.lower().strip()
		userlists = []

		if mode == None or mode == 'trakt':
			try:
				if trakt.getTraktCredentialsInfo() == False: raise Exception()
				activity = trakt.getActivity()
			except: pass

			try:
				if trakt.getTraktCredentialsInfo() == False: raise Exception()
				self.list = []
				lists = []

				try:
					if activity > cache.timeout(self.trakt_user_list, self.traktlists_link, self.trakt_user): raise Exception()
					lists += cache.get(self.trakt_user_list, 3, self.traktlists_link, self.trakt_user)
				except:
					lists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)

				for i in range(len(lists)): lists[i].update({'image': 'traktlists.png'})
				userlists += lists
			except: pass

		if mode == None or mode == 'imdb':
			try:
				if self.imdb_user == '': raise Exception()
				self.list = []
				lists = cache.get(self.imdb_user_list, 0, self.imdblists_link)
				for i in range(len(lists)): lists[i].update({'image': 'imdblists.png'})
				userlists += lists
			except: pass

		if mode == None or mode == 'trakt':
			try:
				if trakt.getTraktCredentialsInfo() == False: raise Exception()
				self.list = []
				lists = []

				try:
					if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link, self.trakt_user): raise Exception()
					lists += cache.get(self.trakt_user_list, 3, self.traktlikedlists_link, self.trakt_user)
				except:
					lists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)

				for i in range(len(lists)): lists[i].update({'image': 'traktlists.png'})
				userlists += lists
			except: pass

		self.list = []

		# Filter the user's own lists that were
		for i in range(len(userlists)):
			contains = False
			adapted = userlists[i]['url'].replace('/me/', '/%s/' % self.trakt_user)
			for j in range(len(self.list)):
				if adapted == self.list[j]['url'].replace('/me/', '/%s/' % self.trakt_user):
					contains = True
					break
			if not contains:
				self.list.append(userlists[i])

		for i in range(len(self.list)): self.list[i].update({'action': self.parameterize('tvshows')})

		# Watchlist
		if (mode == None or mode == 'trakt') and trakt.getTraktCredentialsInfo():
			watchlist = self.traktwatchlist_link + 'shows'
			self.list.insert(0, {'name' : interface.Translation.string(32033), 'url' : watchlist, 'context' : watchlist, 'image': 'traktwatch.png', 'action': self.parameterize('tvshows')})

		self.addDirectory(self.list)
		return self.list


	def trakt_list(self, url, user):
		try:
			dupes = []

			q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
			q.update({'extended': 'full,images'})
			q = (urllib.urlencode(q)).replace('%2C', ',')
			u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

			result = trakt.getTrakt(u)
			result = json.loads(result)

			items = []
			for i in result:
				try: items.append(i['show'])
				except: pass
			if len(items) == 0:
				items = result
		except:
			return

		try:
			q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
			if not int(q['limit']) == len(items): raise Exception()
			q.update({'page': str(int(q['page']) + 1)})
			q = (urllib.urlencode(q)).replace('%2C', ',')
			next = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q
			next = next.encode('utf-8')
		except:
			next = ''

		for item in items:
			try:
				title = item['title']
				title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
				title = client.replaceHTMLCodes(title)
				title = title.encode('utf-8')

				year = item['year']
				year = re.sub('[^0-9]', '', str(year))
				year = year.encode('utf-8')

				if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

				imdb = item['ids']['imdb']
				if imdb == None or imdb == '': imdb = '0'
				else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
				imdb = imdb.encode('utf-8')

				tvdb = item['ids']['tvdb']
				tvdb = re.sub('[^0-9]', '', str(tvdb))
				tvdb = tvdb.encode('utf-8')

				if tvdb == None or tvdb == '' or tvdb in dupes: raise Exception()
				dupes.append(tvdb)

				try: premiered = item['first_aired']
				except: premiered = '0'
				try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
				except: premiered = '0'
				premiered = premiered.encode('utf-8')

				try: studio = item['network']
				except: studio = '0'
				if studio == None: studio = '0'
				studio = studio.encode('utf-8')

				try: genre = item['genres']
				except: genre = '0'
				genre = [i.title() for i in genre]
				if genre == []: genre = '0'
				genre = ' / '.join(genre)
				genre = genre.encode('utf-8')

				try: duration = str(item['runtime'])
				except: duration = '0'
				if duration == None: duration = '0'
				duration = duration.encode('utf-8')

				try: rating = str(item['rating'])
				except: rating = '0'
				if rating == None or rating == '0.0': rating = '0'
				rating = rating.encode('utf-8')

				try: votes = str(item['votes'])
				except: votes = '0'
				try: votes = str(format(int(votes),',d'))
				except: pass
				if votes == None: votes = '0'
				votes = votes.encode('utf-8')

				try: mpaa = item['certification']
				except: mpaa = '0'
				if mpaa == None: mpaa = '0'
				mpaa = mpaa.encode('utf-8')

				try: plot = item['overview']
				except: plot = '0'
				if plot == None: plot = '0'
				plot = client.replaceHTMLCodes(plot)
				plot = plot.encode('utf-8')

				self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'next': next})
			except:
				pass

		return self.list


	def trakt_user_list(self, url, user):
		try:
			result = trakt.getTrakt(url)
			items = json.loads(result)
		except:
			pass

		for item in items:
			try:
				try: name = item['list']['name']
				except: name = item['name']
				name = client.replaceHTMLCodes(name)
				name = name.encode('utf-8')

				try: url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
				except: url = ('me', item['ids']['slug'])
				url = self.traktlist_link % url
				url = url.encode('utf-8')

				self.list.append({'name': name, 'url': url, 'context': url})
			except:
				pass

		self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['name'].lower()))
		return self.list


	def imdb_list(self, url):
		try:
			dupes = []

			for i in re.findall('date\[(\d+)\]', url):
				url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

			def imdb_watchlist_id(url):
				return client.parseDOM(client.request(url).decode('iso-8859-1').encode('utf-8'), 'meta', ret='content', attrs = {'property': 'pageId'})[0]

			if url == self.imdbwatchlist_link:
				# [BUBBLESCODE]

				#url = cache.get(imdb_watchlist_id, 8640, url)
				url = cache.get(imdb_watchlist_id, 0, url) # Seems like IMDB takes a lot longer to load lists.

				# [/BUBBLESCODE]
				url = self.imdblist_link % url

			elif url == self.imdbwatchlist2_link:
				# [BUBBLESCODE]

				#url = cache.get(imdb_watchlist_id, 8640, url)
				url = cache.get(imdb_watchlist_id, 0, url) # Seems like IMDB takes a lot longer to load lists.

				# [/BUBBLESCODE]
				url = self.imdblist2_link % url

			result = client.request(url)

			result = result.replace('\n','')
			result = result.decode('iso-8859-1').encode('utf-8')

			items = client.parseDOM(result, 'div', attrs = {'class': 'lister-item mode-advanced'})
			items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
		except:
			return

		try:
			next = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'lister-page-next.+?'})

			if len(next) == 0:
				next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
				next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
				next = [i[0] for i in next if 'Next' in i[1]]

			next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next[0]).query)
			next = client.replaceHTMLCodes(next)
			next = next.encode('utf-8')
		except:
			next = ''

		for item in items:
			try:
				title = client.parseDOM(item, 'a')[1]
				title = client.replaceHTMLCodes(title)
				title = title.encode('utf-8')

				year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
				year += client.parseDOM(item, 'span', attrs = {'class': 'year_type'})
				year = re.findall('(\d{4})', year[0])[0]
				year = year.encode('utf-8')

				if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

				imdb = client.parseDOM(item, 'a', ret='href')[0]
				imdb = re.findall('(tt\d*)', imdb)[0]
				imdb = imdb.encode('utf-8')

				if imdb in dupes: raise Exception()
				dupes.append(imdb)

				# [BUBBLESCODE]
				# parseDOM cannot handle elements without a closing tag.

				#try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
				#except: poster = '0'

				try:
					html = BeautifulSoup(item)
					poster = html.find_all('img')[0]['loadlate']
				except:
					poster = '0'
				# [/BUBBLESCODE]

				if '/nopicture/' in poster: poster = '0'
				poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
				poster = client.replaceHTMLCodes(poster)
				poster = poster.encode('utf-8')

				rating = '0'
				try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
				except: pass
				try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
				except: rating = '0'
				try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
				except: pass
				if rating == '' or rating == '-': rating = '0'
				rating = client.replaceHTMLCodes(rating)
				rating = rating.encode('utf-8')

				plot = '0'
				try: plot = client.parseDOM(item, 'p', attrs = {'class': 'text-muted'})[0]
				except: pass
				try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
				except: pass
				plot = plot.rsplit('<span>', 1)[0].strip()
				plot = re.sub('<.+?>|</.+?>', '', plot)
				if plot == '': plot = '0'
				plot = client.replaceHTMLCodes(plot)
				plot = plot.encode('utf-8')

				self.list.append({'title': title, 'originaltitle': title, 'year': year, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': '0', 'poster': poster, 'next': next})
			except:
				pass

		return self.list


	def imdb_person_list(self, url):
		try:
			result = client.request(url)
			result = result.decode('iso-8859-1').encode('utf-8')
			items = client.parseDOM(result, 'tr', attrs = {'class': '.+? detailed'})
		except:
			return

		for item in items:
			try:
				name = client.parseDOM(item, 'a', ret='title')[0]
				name = client.replaceHTMLCodes(name)
				name = name.encode('utf-8')

				url = client.parseDOM(item, 'a', ret='href')[0]
				url = re.findall('(nm\d*)', url, re.I)[0]
				url = self.person_link % url
				url = client.replaceHTMLCodes(url)
				url = url.encode('utf-8')

				image = client.parseDOM(item, 'img', ret='src')[0]
				if not ('._SX' in image or '._SY' in image): raise Exception()
				image = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
				image = client.replaceHTMLCodes(image)
				image = image.encode('utf-8')

				self.list.append({'name': name, 'url': url, 'image': image})
			except:
				pass

		return self.list


	def imdb_user_list(self, url):
		try:
			result = client.request(url)
			result = result.decode('iso-8859-1').encode('utf-8')
			items = client.parseDOM(result, 'div', attrs = {'class': 'list_name'})
		except:
			pass

		for item in items:
			try:
				name = client.parseDOM(item, 'a')[0]
				name = client.replaceHTMLCodes(name)
				name = name.encode('utf-8')

				url = client.parseDOM(item, 'a', ret='href')[0]
				url = url.split('/list/', 1)[-1].replace('/', '')
				url = self.imdblist_link % url
				url = client.replaceHTMLCodes(url)
				url = url.encode('utf-8')

				self.list.append({'name': name, 'url': url, 'context': url})
			except:
				pass

		self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['name'].lower()))
		return self.list


	def tvmaze_list(self, url):
		try:
			result = client.request(url)
			result = client.parseDOM(result, 'section', attrs = {'id': 'this-seasons-shows'})

			items = client.parseDOM(result, 'li')
			items = [client.parseDOM(i, 'a', ret='href') for i in items]
			items = [i[0] for i in items if len(i) > 0]
			items = [re.findall('/(\d+)/', i) for i in items]
			items = [i[0] for i in items if len(i) > 0]
			items = items[:50]
		except:
			return

		def items_list(i):
			try:
				url = self.tvmaze_info_link % i

				item = client.request(url)
				item = json.loads(item)

				title = item['name']
				title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
				title = client.replaceHTMLCodes(title)
				title = title.encode('utf-8')

				year = item['premiered']
				year = re.findall('(\d{4})', year)[0]
				year = year.encode('utf-8')

				if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

				imdb = item['externals']['imdb']
				if imdb == None or imdb == '': imdb = '0'
				else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
				imdb = imdb.encode('utf-8')

				tvdb = item['externals']['thetvdb']
				tvdb = re.sub('[^0-9]', '', str(tvdb))
				tvdb = tvdb.encode('utf-8')

				if tvdb == None or tvdb == '': raise Exception()

				try: poster = item['image']['original']
				except: poster = '0'
				if poster == None or poster == '': poster = '0'
				poster = poster.encode('utf-8')

				premiered = item['premiered']
				try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
				except: premiered = '0'
				premiered = premiered.encode('utf-8')

				try: studio = item['network']['name']
				except: studio = '0'
				if studio == None: studio = '0'
				studio = studio.encode('utf-8')

				try: genre = item['genres']
				except: genre = '0'
				genre = [i.title() for i in genre]
				if genre == []: genre = '0'
				genre = ' / '.join(genre)
				genre = genre.encode('utf-8')

				try: duration = item['runtime']
				except: duration = '0'
				if duration == None: duration = '0'
				duration = str(duration)
				duration = duration.encode('utf-8')

				try: rating = item['rating']['average']
				except: rating = '0'
				if rating == None or rating == '0.0': rating = '0'
				rating = str(rating)
				rating = rating.encode('utf-8')

				try: plot = item['summary']
				except: plot = '0'
				if plot == None: plot = '0'
				plot = re.sub('<.+?>|</.+?>|\n', '', plot)
				plot = client.replaceHTMLCodes(plot)
				plot = plot.encode('utf-8')

				try: content = item['type'].lower()
				except: content = '0'
				if content == None or content == '': content = '0'
				content = content.encode('utf-8')

				self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'content': content})
			except:
				pass

		try:
			threads = []
			for i in items: threads.append(workers.Thread(items_list, i))
			[i.start() for i in threads]
			[i.join() for i in threads]

			filter = [i for i in self.list if i['content'] == 'scripted']
			filter += [i for i in self.list if not i['content'] == 'scripted']
			self.list = filter

			return self.list
		except:
			return


	def worker(self, level=1):
		self.meta = []
		total = len(self.list)

		# [BUBBLESCODE]
		self.fanart_tv_headers = {'api-key': 'NzY0YTY1MWJmZmE5YmM3OTRlNzY1OTkzZmY0ZGRkMjI='.decode('base64')}
		# [/BUBBLESCODE]
		if not self.fanart_tv_user == '':
			self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

		for i in range(0, total): self.list[i].update({'metacache': False})

		self.list = metacache.fetch(self.list, self.lang, self.user)

		for r in range(0, total, 40):
			threads = []
			for i in range(r, r+40):
				if i <= total: threads.append(workers.Thread(self.super_info, i))
			[i.start() for i in threads]
			[i.join() for i in threads]

			if self.meta: metacache.insert(self.meta)

		self.list = [i for i in self.list if not i['tvdb'] == '0']

		if self.fanart_tv_user == '':
			for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})


	def super_info(self, i):
		try:
			if self.list[i]['metacache'] == True: raise Exception()

			imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
			tvdb = self.list[i]['tvdb'] if 'tvdb' in self.list[i] else '0'

			if imdb == '0':
				try:
					imdb = trakt.SearchTVShow(urllib.quote_plus(self.list[i]['title']), self.list[i]['year'], full=False)[0]
					imdb = imdb.get('show', '0')
					imdb = imdb.get('ids', {}).get('imdb', '0')
					imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

					if not imdb: imdb = '0'
				except:
					imdb = '0'

			if tvdb == '0' and not imdb == '0':
				url = self.tvdb_by_imdb % imdb

				result = client.request(url, timeout='10')

				try: tvdb = client.parseDOM(result, 'seriesid')[0]
				except: tvdb = '0'

				try: name = client.parseDOM(result, 'SeriesName')[0]
				except: name = '0'
				dupe = re.findall('[***]Duplicate (\d*)[***]', name)
				if dupe: tvdb = str(dupe[0])

				if tvdb == '': tvdb = '0'


			if tvdb == '0':
				url = self.tvdb_by_query % (urllib.quote_plus(self.list[i]['title']))

				years = [str(self.list[i]['year']), str(int(self.list[i]['year'])+1), str(int(self.list[i]['year'])-1)]

				tvdb = client.request(url, timeout='10')
				tvdb = re.sub(r'[^\x00-\x7F]+', '', tvdb)
				tvdb = client.replaceHTMLCodes(tvdb)
				tvdb = client.parseDOM(tvdb, 'Series')
				tvdb = [(x, client.parseDOM(x, 'SeriesName'), client.parseDOM(x, 'FirstAired')) for x in tvdb]
				tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if len(x[1]) > 0 and len(x[2]) > 0]
				tvdb = [x for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1])]
				tvdb = [x[0][0] for x in tvdb if any(y in x[2] for y in years)][0]
				tvdb = client.parseDOM(tvdb, 'seriesid')[0]

				if tvdb == '': tvdb = '0'


			url = self.tvdb_info_link % tvdb
			item = client.request(url, timeout='10')
			if item == None: raise Exception()

			if imdb == '0':
				try: imdb = client.parseDOM(item, 'IMDB_ID')[0]
				except: pass
				if imdb == '': imdb = '0'
				imdb = imdb.encode('utf-8')


			try: title = client.parseDOM(item, 'SeriesName')[0]
			except: title = ''
			if title == '': title = '0'
			title = client.replaceHTMLCodes(title)
			title = title.encode('utf-8')

			try: year = client.parseDOM(item, 'FirstAired')[0]
			except: year = ''
			try: year = re.compile('(\d{4})').findall(year)[0]
			except: year = ''
			if year == '': year = '0'
			year = year.encode('utf-8')

			try: premiered = client.parseDOM(item, 'FirstAired')[0]
			except: premiered = '0'
			if premiered == '': premiered = '0'
			premiered = client.replaceHTMLCodes(premiered)
			premiered = premiered.encode('utf-8')

			try: studio = client.parseDOM(item, 'Network')[0]
			except: studio = ''
			if studio == '': studio = '0'
			studio = client.replaceHTMLCodes(studio)
			studio = studio.encode('utf-8')

			try: genre = client.parseDOM(item, 'Genre')[0]
			except: genre = ''
			genre = [x for x in genre.split('|') if not x == '']
			genre = ' / '.join(genre)
			if genre == '': genre = '0'
			genre = client.replaceHTMLCodes(genre)
			genre = genre.encode('utf-8')

			try: duration = client.parseDOM(item, 'Runtime')[0]
			except: duration = ''
			if duration == '': duration = '0'
			duration = client.replaceHTMLCodes(duration)
			duration = duration.encode('utf-8')

			try: rating = client.parseDOM(item, 'Rating')[0]
			except: rating = ''
			if 'rating' in self.list[i] and not self.list[i]['rating'] == '0':
				rating = self.list[i]['rating']
			if rating == '': rating = '0'
			rating = client.replaceHTMLCodes(rating)
			rating = rating.encode('utf-8')

			try: votes = client.parseDOM(item, 'RatingCount')[0]
			except: votes = ''
			if 'votes' in self.list[i] and not self.list[i]['votes'] == '0':
				votes = self.list[i]['votes']
			if votes == '': votes = '0'
			votes = client.replaceHTMLCodes(votes)
			votes = votes.encode('utf-8')

			try: mpaa = client.parseDOM(item, 'ContentRating')[0]
			except: mpaa = ''
			if mpaa == '': mpaa = '0'
			mpaa = client.replaceHTMLCodes(mpaa)
			mpaa = mpaa.encode('utf-8')

			try: cast = client.parseDOM(item, 'Actors')[0]
			except: cast = ''
			cast = [x for x in cast.split('|') if not x == '']
			try: cast = [(x.encode('utf-8'), '') for x in cast]
			except: cast = []
			if cast == []: cast = '0'

			try: plot = client.parseDOM(item, 'Overview')[0]
			except: plot = ''
			if plot == '': plot = '0'
			plot = client.replaceHTMLCodes(plot)
			plot = plot.encode('utf-8')

			try: poster = client.parseDOM(item, 'poster')[0]
			except: poster = ''
			if not poster == '': poster = self.tvdb_image + poster
			else: poster = '0'
			if 'poster' in self.list[i] and poster == '0': poster = self.list[i]['poster']
			poster = client.replaceHTMLCodes(poster)
			poster = poster.encode('utf-8')

			try: banner = client.parseDOM(item, 'banner')[0]
			except: banner = ''
			if not banner == '': banner = self.tvdb_image + banner
			else: banner = '0'
			banner = client.replaceHTMLCodes(banner)
			banner = banner.encode('utf-8')

			try: fanart = client.parseDOM(item, 'fanart')[0]
			except: fanart = ''
			if not fanart == '': fanart = self.tvdb_image + fanart
			else: fanart = '0'
			fanart = client.replaceHTMLCodes(fanart)
			fanart = fanart.encode('utf-8')


			try:
				artmeta = True
				if self.fanart_tv_user == '': raise Exception()

				art = client.request(self.fanart_tv_art_link % tvdb, headers=self.fanart_tv_headers, timeout='10', error=True)
				try: art = json.loads(art)
				except: artmeta = False
			except:
				pass

			try:
				poster2 = art['tvposter']
				poster2 = [x for x in poster2 if x.get('lang') == 'en'][::-1] + [x for x in poster2 if x.get('lang') == '00'][::-1]
				poster2 = poster2[0]['url'].encode('utf-8')
			except:
				poster2 = '0'

			try:
				fanart2 = art['showbackground']
				fanart2 = [x for x in fanart2 if x.get('lang') == 'en'][::-1] + [x for x in fanart2 if x.get('lang') == '00'][::-1]
				fanart2 = fanart2[0]['url'].encode('utf-8')
			except:
				fanart2 = '0'

			try:
				banner2 = art['tvbanner']
				banner2 = [x for x in banner2 if x.get('lang') == 'en'][::-1] + [x for x in banner2 if x.get('lang') == '00'][::-1]
				banner2 = banner2[0]['url'].encode('utf-8')
			except:
				banner2 = '0'

			try:
				if 'hdtvlogo' in art: clearlogo = art['hdtvlogo']
				else: clearlogo = art['clearlogo']
				clearlogo = [x for x in clearlogo if x.get('lang') == 'en'][::-1] + [x for x in clearlogo if x.get('lang') == '00'][::-1]
				clearlogo = clearlogo[0]['url'].encode('utf-8')
			except:
				clearlogo = '0'

			try:
				if 'hdclearart' in art: clearart = art['hdclearart']
				else: clearart = art['clearart']
				clearart = [x for x in clearart if x.get('lang') == 'en'][::-1] + [x for x in clearart if x.get('lang') == '00'][::-1]
				clearart = clearart[0]['url'].encode('utf-8')
			except:
				clearart = '0'

			item = {'title': title, 'year': year, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'poster2': poster2, 'banner': banner, 'banner2': banner2, 'fanart': fanart, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': cast, 'plot': plot}
			item = dict((k,v) for k, v in item.iteritems() if not v == '0')
			self.list[i].update(item)

			if artmeta == False: raise Exception()

			meta = {'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}
			self.meta.append(meta)
		except:
			pass


	def tvshowDirectory(self, items, next = True):
		if items == None or len(items) == 0: control.idle() ; sys.exit()

		sysaddon = sys.argv[0]

		syshandle = int(sys.argv[1])

		addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

		addonFanart, settingFanart = control.addonFanart(), tools.Settings.getBoolean('interface.fanart')

		traktCredentials = trakt.getTraktCredentialsInfo()

		try: isOld = False ; control.item().getArt('type')
		except: isOld = True

		indicators = playcount.getTVShowIndicators(refresh=True) if action == 'tvshows' else playcount.getTVShowIndicators()

		flatten = True if control.setting('interface.tvshows.flatten') == 'true' else False

		traktHas = trakt.getTraktIndicatorsInfo() == True
		watchedMenu = control.lang(32068).encode('utf-8') if traktHas else control.lang(32066).encode('utf-8')
		unwatchedMenu = control.lang(32069).encode('utf-8') if traktHas else control.lang(32067).encode('utf-8')

		unwatchedEnabled = tools.Settings.getBoolean('interface.tvshows.unwatched.enabled')
		unwatchedLimit = tools.Settings.getBoolean('interface.tvshows.unwatched.limit')

		queueMenu = control.lang(32065).encode('utf-8')

		traktManagerMenu = control.lang(32070).encode('utf-8')

		nextMenu = control.lang(32053).encode('utf-8')

		media = tools.Media()

		for i in items:
			try:
				label = None
				try: label = media.title(tools.Media.TypeShow, title = i['title'], year = i['year'])
				except: pass
				if label == None:
					label = i['title']

				try: systitle = sysname = urllib.quote_plus(i['originaltitle'])
				except: systitle = sysname = urllib.quote_plus(i['title'])

				sysimage = urllib.quote_plus(i['poster'])
				imdb, tvdb, year = i['imdb'], i['tvdb'], i['year']

				meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
				meta.update({'mediatype': 'tvshow'})
				meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})

				# Bubbles
				# Remove default time, since this might mislead users. Rather show no time.
				#if not 'duration' in i: meta.update({'duration': '60'})
				#elif i['duration'] == '0': meta.update({'duration': '60'})

				try: meta.update({'duration': str(int(meta['duration']) * 60)})
				except: pass
				try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
				except: pass

				try:
					overlay = int(playcount.getTVShowOverlay(indicators, tvdb))
					if overlay == 7: meta.update({'playcount': 1, 'overlay': 7})
					else: meta.update({'playcount': 0, 'overlay': 6})
				except:
					overlay = None

				if flatten == True:
					url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (sysaddon, systitle, year, imdb, tvdb)
				else:
					url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (sysaddon, systitle, year, imdb, tvdb)
				url = self.parameterize(url)

				cm = []

				cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

				if not traktHas:
					link = self.parameterize('%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&query=7' % (sysaddon, systitle, imdb, tvdb))
					cm.append((watchedMenu, 'RunPlugin(%s)' % link))

					link = self.parameterize('%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&query=6' % (sysaddon, systitle, imdb, tvdb))
					cm.append((unwatchedMenu, 'RunPlugin(%s)' % link))

				if traktCredentials == True:
					link = self.parameterize('%s?action=traktManager&tvdb=%s' % (sysaddon, tvdb))
					cm.append((traktManagerMenu, 'RunPlugin(%s)' % link))

				if not self.kidsOnly() and control.setting('downloads.manual.enabled') == 'true':
					cm.append((control.lang(33585).encode('utf-8'), 'Container.Update(%s?action=downloadsManager)' % (sysaddon)))

				if isOld == True:
					cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))

				item = control.item(label = label)

				if unwatchedEnabled and not overlay == None and not overlay == 7:
					try:
						count = playcount.getShowCount(indicators, tvdb, unwatchedLimit)
						if count:
							item.setProperty('TotalEpisodes', str(count['total']))
							item.setProperty('WatchedEpisodes', str(count['watched']))
							item.setProperty('UnWatchedEpisodes', str(count['unwatched']))
					except:
						pass

				art = {}

				poster = '0'
				if poster == '0' and 'poster3' in i: poster = i['poster3']
				if poster == '0' and 'poster2' in i: poster = i['poster2']
				if poster == '0' and 'poster' in i: poster = i['poster']

				icon = '0'
				if icon == '0' and 'icon3' in i: icon = i['icon3']
				if icon == '0' and 'icon2' in i: icon = i['icon2']
				if icon == '0' and 'icon' in i: icon = i['icon']

				thumb = '0'
				if thumb == '0' and 'thumb3' in i: thumb = i['thumb3']
				if thumb == '0' and 'thumb2' in i: thumb = i['thumb2']
				if thumb == '0' and 'thumb' in i: thumb = i['thumb']

				banner = '0'
				if banner == '0' and 'banner3' in i: banner = i['banner3']
				if banner == '0' and 'banner2' in i: banner = i['banner2']
				if banner == '0' and 'banner' in i: banner = i['banner']

				fanart = '0'
				if settingFanart:
					if fanart == '0' and 'fanart3' in i: fanart = i['fanart3']
					if fanart == '0' and 'fanart2' in i: fanart = i['fanart2']
					if fanart == '0' and 'fanart' in i: fanart = i['fanart']

				clearlogo = '0'
				if clearlogo == '0' and 'clearlogo' in i: clearlogo = i['clearlogo']

				clearart = '0'
				if clearart == '0' and 'clearart' in i: clearart = i['clearart']

				if poster == '0': poster = addonPoster
				if icon == '0': icon = poster
				if thumb == '0': thumb = poster
				if banner == '0': banner = addonBanner
				if fanart == '0': fanart = addonFanart

				if not poster == '0' and not poster == None: art.update({'poster' : poster, 'tvshow.poster' : poster, 'season.poster' : poster})
				if not icon == '0' and not icon == None: art.update({'icon' : icon})
				if not thumb == '0' and not thumb == None: art.update({'thumb' : thumb})
				if not banner == '0' and not banner == None: art.update({'banner' : banner})
				if not clearlogo == '0' and not clearlogo == None: art.update({'clearlogo' : clearlogo})
				if not clearart == '0' and not clearart == None: art.update({'clearart' : clearart})
				if not fanart == '0' and not fanart == None: item.setProperty('Fanart_Image', fanart)

				item.setArt(art)
				item.addContextMenuItems(cm)
				item.setInfo(type='Video', infoLabels = meta)

				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				pass

		if next:
			try:
				url = items[0]['next']
				if url == '': raise Exception()

				url = '%s?action=tvshowPage&url=%s' % (sysaddon, urllib.quote_plus(url))

				item = control.item(label=nextMenu)

				item.setProperty('nextpage', 'true') # Used by skin.bubbles.aeon.nox

				iconIcon, iconThumb, iconPoster, iconBanner = interface.Icon.pathAll(icon = 'next.png', default = 'DefaultFolder.png')
				item.setArt({'icon': iconIcon, 'thumb': iconThumb, 'poster': iconPoster, 'banner': iconBanner})

				if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				pass

		control.content(syshandle, 'tvshows')
		control.directory(syshandle, cacheToDisc=True)
		views.setView('shows', {'skin.estuary': 55, 'skin.confluence': 500})

	def addDirectory(self, items, queue=False):
		if items == None or len(items) == 0: control.idle() ; sys.exit()

		sysaddon = sys.argv[0]

		syshandle = int(sys.argv[1])

		addonFanart = control.addonFanart()
		addonThumb = control.addonThumb()

		queueMenu = control.lang(32065).encode('utf-8')

		for i in items:
			try:
				name = i['name']

				url = '%s?action=%s' % (sysaddon, i['action'])
				try: url += '&url=%s' % urllib.quote_plus(i['url'])
				except: pass

				cm = []

				if queue == True:
					cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

				item = control.item(label=name)

				if i['image'].startswith('http'):
					iconIcon = iconThumb = iconPoster = iconBanner = i['image']
				else:
					iconIcon, iconThumb, iconPoster, iconBanner = interface.Icon.pathAll(icon = i['image'], default = addonThumb)
				item.setArt({'icon': iconIcon, 'thumb': iconThumb, 'poster': iconPoster, 'banner': iconBanner})

				if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

				item.addContextMenuItems(cm)

				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				pass

		control.content(syshandle, 'addons')
		control.directory(syshandle, cacheToDisc=True)
