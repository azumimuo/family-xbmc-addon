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
from resources.lib.modules import playcount
from resources.lib.modules import workers
from resources.lib.modules import views
from resources.lib.modules import metacache

from resources.lib.extensions import tools
from resources.lib.extensions import interface

import os,sys,re,json,zipfile,StringIO,urllib,urllib2,urlparse,datetime

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

class episodes:

	def __init__(self, type = tools.Media.TypeShow, kids = tools.Selection.TypeUndefined):
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

		self.trakt_link = 'http://api-v2launch.trakt.tv'
		self.tvmaze_link = 'http://api.tvmaze.com'
		self.tvdb_key = 'MDk1NUY1N0Q5QTlENEZEQw=='
		self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
		self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
		self.today_date = (self.datetime).strftime('%Y-%m-%d')
		self.trakt_user = control.setting('accounts.informants.trakt.user').strip()
		self.lang = control.apiLanguage()['tvdb']

		self.fanart_tv_user = control.setting('accounts.artwork.fanart.api') if control.setting('accounts.artwork.fanart.enabled') else ''
		self.user = self.fanart_tv_user + str('')

		self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key.decode('base64'), '%s', '%s')
		self.tvdb_image = 'http://thetvdb.com/banners/'
		self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'

		self.added_link = 'http://api.tvmaze.com/schedule'
		self.mycalendar_link = 'http://api-v2launch.trakt.tv/calendars/my/shows/date[29]/60/'
		self.trakthistory_link = 'http://api-v2launch.trakt.tv/users/me/history/shows?limit=300'
		self.progress_link = 'http://api-v2launch.trakt.tv/users/me/watched/shows'
		self.hiddenprogress_link = 'http://api-v2launch.trakt.tv/users/hidden/progress_watched?limit=1000&type=show'
		self.calendar_link = 'http://api.tvmaze.com/schedule?date=%s'

		self.traktwatchlist_link = 'http://api-v2launch.trakt.tv/users/me/watchlist/episodes'
		self.traktlists_link = 'http://api-v2launch.trakt.tv/users/me/lists'
		self.traktlikedlists_link = 'http://api-v2launch.trakt.tv/users/likes/lists?limit=1000000'
		self.traktlist_link = 'http://api-v2launch.trakt.tv/users/%s/lists/%s/items'

	def parameterize(self, action):
		if not self.type == None: action += '&type=%s' % self.type
		if not self.kids == None: action += '&kids=%d' % self.kids
		return action

	def kidsOnly(self):
		return self.kids == tools.Selection.TypeInclude

	def get(self, tvshowtitle, year, imdb, tvdb, season=None, episode=None, idx=True):
		from resources.lib.indexers import seasons
		try:
			if idx == True:
				if season == None and episode == None:
					self.list = cache.get(seasons.seasons().tvdb_list, 1, tvshowtitle, year, imdb, tvdb, self.lang, '-1')
				elif episode == None:
					self.list = cache.get(seasons.seasons().tvdb_list, 1, tvshowtitle, year, imdb, tvdb, self.lang, season)
				else:
					self.list = cache.get(seasons.seasons().tvdb_list, 1, tvshowtitle, year, imdb, tvdb, self.lang, '-1')
					num = [x for x,y in enumerate(self.list) if y['season'] == str(season) and  y['episode'] == str(episode)][-1]
					self.list = [y for x,y in enumerate(self.list) if x >= num]

				self.episodeDirectory(self.list)
				return self.list
			else:
				self.list = seasons.seasons().tvdb_list(tvshowtitle, year, imdb, tvdb, 'en', '-1')
				return self.list
		except:
			pass


	def calendar(self, url):
		try:
			try: url = getattr(self, url + '_link')
			except: pass

			if self.trakt_link in url and url == self.progress_link:
				self.blist = cache.get(self.trakt_progress_list, 720, url, self.trakt_user, self.lang)
				self.list = []
				self.list = cache.get(self.trakt_progress_list, 0, url, self.trakt_user, self.lang)
				# Sort according to date
				try: self.list = sorted(self.list, key = lambda k: k['premiered'], reverse = tools.Settings.getInteger('interface.tvshows.special.sort') == 1)
				except: pass

			elif self.trakt_link in url and url == self.mycalendar_link:
				self.blist = cache.get(self.trakt_episodes_list, 720, url, self.trakt_user, self.lang)
				self.list = []
				self.list = cache.get(self.trakt_episodes_list, 0, url, self.trakt_user, self.lang)
				# Sort according to date
				try: self.list = sorted(self.list, key = lambda k: k['premiered'], reverse = tools.Settings.getInteger('interface.tvshows.special.sort') == 1)
				except: pass

			elif self.trakt_link in url and '/users/' in url:
				self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)
				self.list = self.list[::-1]

			elif self.trakt_link in url:
				self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)


			elif self.tvmaze_link in url and url == self.added_link:
				urls = [i['url'] for i in self.calendars(idx=False)][:5]
				self.list = []
				for url in urls:
					self.list += cache.get(self.tvmaze_list, 720, url, True)

			elif self.tvmaze_link in url:
				self.list = cache.get(self.tvmaze_list, 1, url, False)

			self.episodeDirectory(self.list)
			return self.list
		except:
			pass


	def arrivals(self):
		if trakt.getTraktIndicatorsInfo() == True:
			setting = tools.Settings.getInteger('interface.arrivals.shows')
		else:
			setting = 0

		if setting == 0:
			self.calendar(self.added_link)
		elif setting == 1:
			self.home()
		elif setting == 2:
			from resources.lib.indexers import tvshows
			tvshows.tvshows(type = self.type, kids = self.kids).get('airing')
		elif setting == 3:
			self.calendar(self.progress_link)
		elif setting == 4:
			self.calendar(self.mycalendar_link)
		else:
			self.home()


	def home(self):
		date = self.datetime - datetime.timedelta(days = 1)
		url = self.calendar_link % date.strftime('%Y-%m-%d')
		self.list = cache.get(self.tvmaze_list, 1, url, False)
		self.episodeDirectory(self.list)
		return self.list


	def calendars(self, idx=True):
		m = control.lang(32060).encode('utf-8').split('|')
		try: months = [(m[0], 'January'), (m[1], 'February'), (m[2], 'March'), (m[3], 'April'), (m[4], 'May'), (m[5], 'June'), (m[6], 'July'), (m[7], 'August'), (m[8], 'September'), (m[9], 'October'), (m[10], 'November'), (m[11], 'December')]
		except: months = []

		d = control.lang(32061).encode('utf-8').split('|')
		try: days = [(d[0], 'Monday'), (d[1], 'Tuesday'), (d[2], 'Wednesday'), (d[3], 'Thursday'), (d[4], 'Friday'), (d[5], 'Saturday'), (d[6], 'Sunday')]
		except: days = []

		for i in range(0, 30):
			try:
				name = (self.datetime - datetime.timedelta(days = i))
				name = (control.lang(32062) % (name.strftime('%A'), name.strftime('%d %B'))).encode('utf-8')
				for m in months: name = name.replace(m[1], m[0])
				for d in days: name = name.replace(d[1], d[0])
				try: name = name.encode('utf-8')
				except: pass

				url = self.calendar_link % (self.datetime - datetime.timedelta(days = i)).strftime('%Y-%m-%d')

				self.list.append({'name': name, 'url': url, 'image': 'calendar.png', 'action': 'calendar'})
			except:
				pass
		if idx == True: self.addDirectory(self.list)
		return self.list


	def userlists(self):
		userlists = []

		try:
			if trakt.getTraktCredentialsInfo() == False: raise Exception()
			activity = trakt.getActivity()
		except:
			pass

		try:
			if trakt.getTraktCredentialsInfo() == False: raise Exception()
			self.list = []
			try:
				if activity > cache.timeout(self.trakt_user_list, self.traktlists_link, self.trakt_user): raise Exception()
				userlists += cache.get(self.trakt_user_list, 3, self.traktlists_link, self.trakt_user)
			except:
				userlists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)
		except:
			pass

		try:
			if trakt.getTraktCredentialsInfo() == False: raise Exception()
			self.list = []
			try:
				if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link, self.trakt_user): raise Exception()
				userlists += cache.get(self.trakt_user_list, 3, self.traktlikedlists_link, self.trakt_user)
			except:
				userlists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)
		except:
			pass

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

		for i in range(0, len(self.list)): self.list[i].update({'image': 'traktlists.png', 'action': self.parameterize('calendar')})

		# Watchlist
		if trakt.getTraktCredentialsInfo():
			self.list.insert(0, {'name' : interface.Translation.string(32033), 'url' : self.traktwatchlist_link, 'context' : self.traktwatchlist_link, 'image': 'traktwatch.png', 'action': self.parameterize('tvshows')})

		self.addDirectory(self.list, queue=True)
		return self.list


	def trakt_list(self, url, user):
		try:
			for i in re.findall('date\[(\d+)\]', url):
				url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

			q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
			q.update({'extended': 'full,images'})
			q = (urllib.urlencode(q)).replace('%2C', ',')
			u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

			result = trakt.getTrakt(u)
			itemlist = []
			items = json.loads(result)
		except:
			return

		for item in items:
			try:
				if not 'show' in item or not 'episode' in item:
					raise Exception()

				title = item['episode']['title']
				if title == None or title == '': raise Exception()
				title = client.replaceHTMLCodes(title)
				title = title.encode('utf-8')

				season = item['episode']['season']
				season = re.sub('[^0-9]', '', '%01d' % int(season))
				if season == '0': raise Exception()
				season = season.encode('utf-8')

				episode = item['episode']['number']
				episode = re.sub('[^0-9]', '', '%01d' % int(episode))
				if episode == '0': raise Exception()
				episode = episode.encode('utf-8')

				tvshowtitle = item['show']['title']
				if tvshowtitle == None or tvshowtitle == '': raise Exception()
				tvshowtitle = client.replaceHTMLCodes(tvshowtitle)
				tvshowtitle = tvshowtitle.encode('utf-8')

				year = item['show']['year']
				year = re.sub('[^0-9]', '', str(year))
				year = year.encode('utf-8')

				imdb = item['show']['ids']['imdb']
				if imdb == None or imdb == '': imdb = '0'
				else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
				imdb = imdb.encode('utf-8')

				tvdb = item['show']['ids']['tvdb']
				if tvdb == None or tvdb == '': raise Exception()
				tvdb = re.sub('[^0-9]', '', str(tvdb))
				tvdb = tvdb.encode('utf-8')

				premiered = item['episode']['first_aired']
				try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
				except: premiered = '0'
				premiered = premiered.encode('utf-8')

				studio = item['show']['network']
				if studio == None: studio = '0'
				studio = studio.encode('utf-8')

				genre = item['show']['genres']
				genre = [i.title() for i in genre]
				if genre == []: genre = '0'
				genre = ' / '.join(genre)
				genre = genre.encode('utf-8')

				# Bubbles
				if 'duration' in item and not item['duration'] == None and not item['duration'] == '':
					duration = item['duration']
				else:
					try: duration = str(item['show']['runtime'])
					except: duration = '0'
					if duration == None: duration = '0'
					duration = duration.encode('utf-8')

				try: rating = str(item['episode']['rating'])
				except: rating = '0'
				if rating == None or rating == '0.0': rating = '0'
				rating = rating.encode('utf-8')

				try: votes = str(item['show']['votes'])
				except: votes = '0'
				try: votes = str(format(int(votes),',d'))
				except: pass
				if votes == None: votes = '0'
				votes = votes.encode('utf-8')

				# Bubbles
				if 'mpaa' in item and not item['mpaa'] == None and not item['mpaa'] == '':
					mpaa = item['mpaa']
				else:
					mpaa = item['show']['certification']
					if mpaa == None: mpaa = '0'
					mpaa = mpaa.encode('utf-8')

				plot = item['episode']['overview']
				if plot == None or plot == '': plot = item['show']['overview']
				if plot == None or plot == '': plot = '0'
				plot = client.replaceHTMLCodes(plot)
				plot = plot.encode('utf-8')

				# Bubbles
				values = {'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': 'Continuing', 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'thumb': '0'}

				# Bubbles
				if 'airday' in item and not item['airday'] == None and not item['airday'] == '':
					values['airday'] = item['airday']
				if 'airtime' in item and not item['airtime'] == None and not item['airtime'] == '':
					values['airtime'] = item['airtime']
				if 'airzone' in item and not item['airzone'] == None and not item['airzone'] == '':
					values['airzone'] = item['airzone']
				try:
					air = item['show']['airs']
					if not 'airday' in item or item['airday'] == None or item['airday'] == '':
						values['airday'] = air['day'].strip()
					if not 'airtime' in item or item['airtime'] == None or item['airtime'] == '':
						values['airtime'] = air['time'].strip()
					if not 'airzone' in item or item['airzone'] == None or item['airzone'] == '':
						values['airzone'] = air['timezone'].strip()
				except:
					pass

				itemlist.append(values)
			except:
				pass

		itemlist = itemlist[::-1]

		return itemlist


	def trakt_progress_list(self, url, user, lang):
		try:
			url += '?extended=full'
			result = trakt.getTrakt(url)
			result = json.loads(result)
			items = []
		except:
			return

		for item in result:
			try:
				num_1 = 0
				for i in range(0, len(item['seasons'])): num_1 += len(item['seasons'][i]['episodes'])
				num_2 = int(item['show']['aired_episodes'])
				if num_1 >= num_2: raise Exception()

				season = str(item['seasons'][-1]['number'])
				season = season.encode('utf-8')

				episode = str(item['seasons'][-1]['episodes'][-1]['number'])
				episode = episode.encode('utf-8')

				tvshowtitle = item['show']['title']
				if tvshowtitle == None or tvshowtitle == '': raise Exception()
				tvshowtitle = client.replaceHTMLCodes(tvshowtitle)
				tvshowtitle = tvshowtitle.encode('utf-8')

				year = item['show']['year']
				year = re.sub('[^0-9]', '', str(year))
				if int(year) > int(self.datetime.strftime('%Y')): raise Exception()

				imdb = item['show']['ids']['imdb']
				if imdb == None or imdb == '': imdb = '0'
				imdb = imdb.encode('utf-8')

				tvdb = item['show']['ids']['tvdb']
				if tvdb == None or tvdb == '': raise Exception()
				tvdb = re.sub('[^0-9]', '', str(tvdb))
				tvdb = tvdb.encode('utf-8')

				values = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'snum': season, 'enum': episode}

				# Bubbles
				try:
					air = item['show']['airs']
					values['airday'] = air['day'].strip()
					values['airtime'] = air['time'].strip()
					values['airzone'] = air['timezone'].strip()
					values['duration'] = air['runtime']
					values['mpaa'] = air['certification'].strip()
				except:
					pass

				items.append(values)
			except:
				pass

		try:
			result = trakt.getTrakt(self.hiddenprogress_link)
			result = json.loads(result)
			result = [str(i['show']['ids']['tvdb']) for i in result]

			items = [i for i in items if not i['tvdb'] in result]
		except:
			pass

		def items_list(i):
			try:
				item = [x for x in self.blist if x['tvdb'] == i['tvdb'] and x['snum'] == i['snum'] and x['enum'] == i['enum']][0]
				item['action'] = 'episodes'
				self.list.append(item)
				return
			except:
				pass

			try:
				url = self.tvdb_info_link % (i['tvdb'], lang)
				data = urllib2.urlopen(url, timeout=10).read()

				zip = zipfile.ZipFile(StringIO.StringIO(data))
				result = zip.read('%s.xml' % lang)
				artwork = zip.read('banners.xml')
				zip.close()

				result = result.split('<Episode>')
				item = [x for x in result if '<EpisodeNumber>' in x]
				item2 = result[0]

				num = [x for x,y in enumerate(item) if re.compile('<SeasonNumber>(.+?)</SeasonNumber>').findall(y)[0] == str(i['snum']) and re.compile('<EpisodeNumber>(.+?)</EpisodeNumber>').findall(y)[0] == str(i['enum'])][-1]
				item = [y for x,y in enumerate(item) if x > num][0]

				premiered = client.parseDOM(item, 'FirstAired')[0]
				if premiered == '' or '-00' in premiered: premiered = '0'
				premiered = client.replaceHTMLCodes(premiered)
				premiered = premiered.encode('utf-8')

				try: status = client.parseDOM(item2, 'Status')[0]
				except: status = ''
				if status == '': status = 'Ended'
				status = client.replaceHTMLCodes(status)
				status = status.encode('utf-8')

				if status == 'Ended': pass
				elif premiered == '0': raise Exception()
				elif int(re.sub('[^0-9]', '', str(premiered))) > int(re.sub('[^0-9]', '', str(self.today_date))): raise Exception()

				title = client.parseDOM(item, 'EpisodeName')[0]
				if title == '': title = '0'
				title = client.replaceHTMLCodes(title)
				title = title.encode('utf-8')

				season = client.parseDOM(item, 'SeasonNumber')[0]
				season = '%01d' % int(season)
				season = season.encode('utf-8')

				episode = client.parseDOM(item, 'EpisodeNumber')[0]
				episode = re.sub('[^0-9]', '', '%01d' % int(episode))
				episode = episode.encode('utf-8')

				tvshowtitle = i['tvshowtitle']
				imdb, tvdb = i['imdb'], i['tvdb']

				year = i['year']
				try: year = year.encode('utf-8')
				except: pass

				try: poster = client.parseDOM(item2, 'poster')[0]
				except: poster = ''
				if not poster == '': poster = self.tvdb_image + poster
				else: poster = '0'
				poster = client.replaceHTMLCodes(poster)
				poster = poster.encode('utf-8')

				try: banner = client.parseDOM(item2, 'banner')[0]
				except: banner = ''
				if not banner == '': banner = self.tvdb_image + banner
				else: banner = '0'
				banner = client.replaceHTMLCodes(banner)
				banner = banner.encode('utf-8')

				try: fanart = client.parseDOM(item2, 'fanart')[0]
				except: fanart = ''
				if not fanart == '': fanart = self.tvdb_image + fanart
				else: fanart = '0'
				fanart = client.replaceHTMLCodes(fanart)
				fanart = fanart.encode('utf-8')

				try: thumb = client.parseDOM(item, 'filename')[0]
				except: thumb = ''
				if not thumb == '': thumb = self.tvdb_image + thumb
				else: thumb = '0'
				thumb = client.replaceHTMLCodes(thumb)
				thumb = thumb.encode('utf-8')

				if not poster == '0': pass
				elif not fanart == '0': poster = fanart
				elif not banner == '0': poster = banner

				if not banner == '0': pass
				elif not fanart == '0': banner = fanart
				elif not poster == '0': banner = poster

				if not thumb == '0': pass
				elif not fanart == '0': thumb = fanart.replace(self.tvdb_image, self.tvdb_poster)
				elif not poster == '0': thumb = poster

				try: studio = client.parseDOM(item2, 'Network')[0]
				except: studio = ''
				if studio == '': studio = '0'
				studio = client.replaceHTMLCodes(studio)
				studio = studio.encode('utf-8')

				try: genre = client.parseDOM(item2, 'Genre')[0]
				except: genre = ''
				genre = [x for x in genre.split('|') if not x == '']
				genre = ' / '.join(genre)
				if genre == '': genre = '0'
				genre = client.replaceHTMLCodes(genre)
				genre = genre.encode('utf-8')

				# Bubbles
				if 'duration' in i and not i['duration'] == None and not i['duration'] == '':
					duration = i['duration']
				else:
					try: duration = client.parseDOM(item2, 'Runtime')[0]
					except: duration = ''
					if duration == '': duration = '0'
					duration = client.replaceHTMLCodes(duration)
					duration = duration.encode('utf-8')

				try: rating = client.parseDOM(item, 'Rating')[0]
				except: rating = ''
				if rating == '': rating = '0'
				rating = client.replaceHTMLCodes(rating)
				rating = rating.encode('utf-8')

				try: votes = client.parseDOM(item2, 'RatingCount')[0]
				except: votes = '0'
				if votes == '': votes = '0'
				votes = client.replaceHTMLCodes(votes)
				votes = votes.encode('utf-8')

				# Bubbles
				if 'mpaa' in i and not i['mpaa'] == None and not i['mpaa'] == '':
					mpaa = i['mpaa']
				else:
					try: mpaa = client.parseDOM(item2, 'ContentRating')[0]
					except: mpaa = ''
					if mpaa == '': mpaa = '0'
					mpaa = client.replaceHTMLCodes(mpaa)
					mpaa = mpaa.encode('utf-8')

				try: director = client.parseDOM(item, 'Director')[0]
				except: director = ''
				director = [x for x in director.split('|') if not x == '']
				director = ' / '.join(director)
				if director == '': director = '0'
				director = client.replaceHTMLCodes(director)
				director = director.encode('utf-8')

				try: writer = client.parseDOM(item, 'Writer')[0]
				except: writer = ''
				writer = [x for x in writer.split('|') if not x == '']
				writer = ' / '.join(writer)
				if writer == '': writer = '0'
				writer = client.replaceHTMLCodes(writer)
				writer = writer.encode('utf-8')

				try: cast = client.parseDOM(item2, 'Actors')[0]
				except: cast = ''
				cast = [x for x in cast.split('|') if not x == '']
				try: cast = [(x.encode('utf-8'), '') for x in cast]
				except: cast = []

				try: plot = client.parseDOM(item, 'Overview')[0]
				except: plot = ''
				if plot == '':
					try: plot = client.parseDOM(item2, 'Overview')[0]
					except: plot = ''
				if plot == '': plot = '0'
				plot = client.replaceHTMLCodes(plot)
				plot = plot.encode('utf-8')

				# Bubbles
				values = {'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb, 'snum': i['snum'], 'enum': i['enum'], 'action': 'episodes'}
				if 'airday' in i and not i['airday'] == None and not i['airday'] == '':
					values['airday'] = i['airday']
				if 'airtime' in i and not i['airtime'] == None and not i['airtime'] == '':
					values['airtime'] = i['airtime']
				if 'airzone' in i and not i['airzone'] == None and not i['airzone'] == '':
					values['airzone'] = i['airzone']

				self.list.append(values)
			except:
				pass


		items = items[:100]

		threads = []
		for i in items: threads.append(workers.Thread(items_list, i))
		[i.start() for i in threads]
		[i.join() for i in threads]

		return self.list


	def trakt_episodes_list(self, url, user, lang):
		items = self.trakt_list(url, user)
		def items_list(i):
			try:
				item = [x for x in self.blist if x['tvdb'] == i['tvdb'] and x['season'] == i['season'] and x['episode'] == i['episode']][0]
				if item['poster'] == '0': raise Exception()
				self.list.append(item)
				return
			except:
				pass

			try:
				url = self.tvdb_info_link % (i['tvdb'], lang)
				data = urllib2.urlopen(url, timeout=10).read()

				zip = zipfile.ZipFile(StringIO.StringIO(data))
				result = zip.read('%s.xml' % lang)
				artwork = zip.read('banners.xml')
				zip.close()

				result = result.split('<Episode>')
				item = [(re.findall('<SeasonNumber>%01d</SeasonNumber>' % int(i['season']), x), re.findall('<EpisodeNumber>%01d</EpisodeNumber>' % int(i['episode']), x), x) for x in result]
				item = [x[2] for x in item if len(x[0]) > 0 and len(x[1]) > 0][0]
				item2 = result[0]

				premiered = client.parseDOM(item, 'FirstAired')[0]
				if premiered == '' or '-00' in premiered: premiered = '0'
				premiered = client.replaceHTMLCodes(premiered)
				premiered = premiered.encode('utf-8')

				try: status = client.parseDOM(item2, 'Status')[0]
				except: status = ''
				if status == '': status = 'Ended'
				status = client.replaceHTMLCodes(status)
				status = status.encode('utf-8')

				title = client.parseDOM(item, 'EpisodeName')[0]
				if title == '': title = '0'
				title = client.replaceHTMLCodes(title)
				title = title.encode('utf-8')

				season = client.parseDOM(item, 'SeasonNumber')[0]
				season = '%01d' % int(season)
				season = season.encode('utf-8')

				episode = client.parseDOM(item, 'EpisodeNumber')[0]
				episode = re.sub('[^0-9]', '', '%01d' % int(episode))
				episode = episode.encode('utf-8')

				tvshowtitle = i['tvshowtitle']
				imdb, tvdb = i['imdb'], i['tvdb']

				year = i['year']
				try: year = year.encode('utf-8')
				except: pass

				try: poster = client.parseDOM(item2, 'poster')[0]
				except: poster = ''
				if not poster == '': poster = self.tvdb_image + poster
				else: poster = '0'
				poster = client.replaceHTMLCodes(poster)
				poster = poster.encode('utf-8')

				try: banner = client.parseDOM(item2, 'banner')[0]
				except: banner = ''
				if not banner == '': banner = self.tvdb_image + banner
				else: banner = '0'
				banner = client.replaceHTMLCodes(banner)
				banner = banner.encode('utf-8')

				try: fanart = client.parseDOM(item2, 'fanart')[0]
				except: fanart = ''
				if not fanart == '': fanart = self.tvdb_image + fanart
				else: fanart = '0'
				fanart = client.replaceHTMLCodes(fanart)
				fanart = fanart.encode('utf-8')

				try: thumb = client.parseDOM(item, 'filename')[0]
				except: thumb = ''
				if not thumb == '': thumb = self.tvdb_image + thumb
				else: thumb = '0'
				thumb = client.replaceHTMLCodes(thumb)
				thumb = thumb.encode('utf-8')

				if not poster == '0': pass
				elif not fanart == '0': poster = fanart
				elif not banner == '0': poster = banner

				if not banner == '0': pass
				elif not fanart == '0': banner = fanart
				elif not poster == '0': banner = poster

				if not thumb == '0': pass
				elif not fanart == '0': thumb = fanart.replace(self.tvdb_image, self.tvdb_poster)
				elif not poster == '0': thumb = poster

				try: studio = client.parseDOM(item2, 'Network')[0]
				except: studio = ''
				if studio == '': studio = '0'
				studio = client.replaceHTMLCodes(studio)
				studio = studio.encode('utf-8')

				try: genre = client.parseDOM(item2, 'Genre')[0]
				except: genre = ''
				genre = [x for x in genre.split('|') if not x == '']
				genre = ' / '.join(genre)
				if genre == '': genre = '0'
				genre = client.replaceHTMLCodes(genre)
				genre = genre.encode('utf-8')

				# Bubbles
				if 'duration' in i and not i['duration'] == None and not i['duration'] == '':
					duration = i['duration']
				else:
					try: duration = client.parseDOM(item2, 'Runtime')[0]
					except: duration = ''
					if duration == '': duration = '0'
					duration = client.replaceHTMLCodes(duration)
					duration = duration.encode('utf-8')

				try: rating = client.parseDOM(item, 'Rating')[0]
				except: rating = ''
				if rating == '': rating = '0'
				rating = client.replaceHTMLCodes(rating)
				rating = rating.encode('utf-8')

				try: votes = client.parseDOM(item2, 'RatingCount')[0]
				except: votes = '0'
				if votes == '': votes = '0'
				votes = client.replaceHTMLCodes(votes)
				votes = votes.encode('utf-8')

				# Bubbles
				if 'mpaa' in i and not i['mpaa'] == None and not i['mpaa'] == '':
					mpaa = i['mpaa']
				else:
					try: mpaa = client.parseDOM(item2, 'ContentRating')[0]
					except: mpaa = ''
					if mpaa == '': mpaa = '0'
					mpaa = client.replaceHTMLCodes(mpaa)
					mpaa = mpaa.encode('utf-8')

				try: director = client.parseDOM(item, 'Director')[0]
				except: director = ''
				director = [x for x in director.split('|') if not x == '']
				director = ' / '.join(director)
				if director == '': director = '0'
				director = client.replaceHTMLCodes(director)
				director = director.encode('utf-8')

				try: writer = client.parseDOM(item, 'Writer')[0]
				except: writer = ''
				writer = [x for x in writer.split('|') if not x == '']
				writer = ' / '.join(writer)
				if writer == '': writer = '0'
				writer = client.replaceHTMLCodes(writer)
				writer = writer.encode('utf-8')

				try: cast = client.parseDOM(item2, 'Actors')[0]
				except: cast = ''
				cast = [x for x in cast.split('|') if not x == '']
				try: cast = [(x.encode('utf-8'), '') for x in cast]
				except: cast = []

				try: plot = client.parseDOM(item, 'Overview')[0]
				except: plot = ''
				if plot == '':
					try: plot = client.parseDOM(item2, 'Overview')[0]
					except: plot = ''
				if plot == '': plot = '0'
				plot = client.replaceHTMLCodes(plot)
				plot = plot.encode('utf-8')

				# Bubbles
				values = {'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb}

				# Bubbles
				if 'airday' in i and not i['airday'] == None and not i['airday'] == '':
					values['airday'] = i['airday']
				if 'airtime' in i and not i['airtime'] == None and not i['airtime'] == '':
					values['airtime'] = i['airtime']
				if 'airzone' in i and not i['airzone'] == None and not i['airzone'] == '':
					values['airzone'] = i['airzone']
				try:
					air = i['show']['airs']
					if not 'airday' in i or i['airday'] == None or i['airday'] == '':
						values['airday'] = air['day'].strip()
					if not 'airtime' in i or i['airtime'] == None or i['airtime'] == '':
						values['airtime'] = air['time'].strip()
					if not 'airzone' in i or i['airzone'] == None or i['airzone'] == '':
						values['airzone'] = air['timezone'].strip()
				except:
					pass

				self.list.append(values)
			except:
				pass


		items = items[:100]

		threads = []
		for i in items: threads.append(workers.Thread(items_list, i))
		[i.start() for i in threads]
		[i.join() for i in threads]

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


	def tvmaze_list(self, url, limit):
		try:
			result = client.request(url)

			itemlist = []
			items = json.loads(result)
		except:
			return

		for item in items:
			try:
				if not 'english' in item['show']['language'].lower(): raise Exception()

				if limit == True and not 'scripted' in item['show']['type'].lower(): raise Exception()

				title = item['name']
				if title == None or title == '': raise Exception()
				title = client.replaceHTMLCodes(title)
				title = title.encode('utf-8')

				season = item['season']
				season = re.sub('[^0-9]', '', '%01d' % int(season))
				if season == '0': raise Exception()
				season = season.encode('utf-8')

				episode = item['number']
				episode = re.sub('[^0-9]', '', '%01d' % int(episode))
				if episode == '0': raise Exception()
				episode = episode.encode('utf-8')

				tvshowtitle = item['show']['name']
				if tvshowtitle == None or tvshowtitle == '': raise Exception()
				tvshowtitle = client.replaceHTMLCodes(tvshowtitle)
				tvshowtitle = tvshowtitle.encode('utf-8')

				year = item['show']['premiered']
				year = re.findall('(\d{4})', year)[0]
				year = year.encode('utf-8')

				imdb = item['show']['externals']['imdb']
				if imdb == None or imdb == '': imdb = '0'
				else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
				imdb = imdb.encode('utf-8')

				tvdb = item['show']['externals']['thetvdb']
				if tvdb == None or tvdb == '': raise Exception()
				tvdb = re.sub('[^0-9]', '', str(tvdb))
				tvdb = tvdb.encode('utf-8')

				poster = '0'
				try: poster = item['show']['image']['original']
				except: poster = '0'
				if poster == None or poster == '': poster = '0'
				poster = poster.encode('utf-8')

				try: thumb1 = item['show']['image']['original']
				except: thumb1 = '0'
				try: thumb2 = item['image']['original']
				except: thumb2 = '0'
				if thumb2 == None or thumb2 == '0': thumb = thumb1
				else: thumb = thumb2
				if thumb == None or thumb == '': thumb = '0'
				thumb = thumb.encode('utf-8')

				premiered = item['airdate']
				try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
				except: premiered = '0'
				premiered = premiered.encode('utf-8')

				try: studio = item['show']['network']['name']
				except: studio = '0'
				if studio == None: studio = '0'
				studio = studio.encode('utf-8')

				try: genre = item['show']['genres']
				except: genre = '0'
				genre = [i.title() for i in genre]
				if genre == []: genre = '0'
				genre = ' / '.join(genre)
				genre = genre.encode('utf-8')

				# Bubbles
				if 'duration' in item and not item['duration'] == None and not item['duration'] == '':
					duration = item['duration']
				else:
					try: duration = item['show']['runtime']
					except: duration = '0'
					if duration == None: duration = '0'
					duration = str(duration)
					duration = duration.encode('utf-8')

				try: rating = item['show']['rating']['average']
				except: rating = '0'
				if rating == None or rating == '0.0': rating = '0'
				rating = str(rating)
				rating = rating.encode('utf-8')

				try: plot = item['show']['summary']
				except: plot = '0'
				if plot == None: plot = '0'
				plot = re.sub('<.+?>|</.+?>|\n', '', plot)
				plot = client.replaceHTMLCodes(plot)
				plot = plot.encode('utf-8')

				# Bubbles
				values = {'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': 'Continuing', 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'thumb': thumb}

				if 'airday' in item and not item['airday'] == None and not item['airday'] == '':
					values['airday'] = item['airday']
				if 'airtime' in item and not item['airtime'] == None and not item['airtime'] == '':
					values['airtime'] = item['airtime']
				if 'airzone' in item and not item['airzone'] == None and not item['airzone'] == '':
					values['airzone'] = item['airzone']
				try:
					air = item['show']['airs']
					if not 'airday' in item or item['airday'] == None or item['airday'] == '':
						values['airday'] = air['day'].strip()
					if not 'airtime' in item or item['airtime'] == None or item['airtime'] == '':
						values['airtime'] = air['time'].strip()
					if not 'airzone' in item or item['airzone'] == None or item['airzone'] == '':
						values['airzone'] = air['timezone'].strip()
				except:
					pass

				itemlist.append(values)
			except:
				pass

		itemlist = itemlist[::-1]

		return itemlist


	def episodeDirectory(self, items):
		if items == None or len(items) == 0:
			control.idle()
			sys.exit()

		sysaddon = sys.argv[0]

		syshandle = int(sys.argv[1])

		addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

		addonFanart, settingFanart = control.addonFanart(), tools.Settings.getBoolean('interface.fanart')

		traktCredentials = trakt.getTraktCredentialsInfo()

		try: isOld = False ; control.item().getArt('type')
		except: isOld = True

		isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

		indicators = playcount.getTVShowIndicators(refresh=True)

		try: multi = [i['tvshowtitle'] for i in items]
		except: multi = []
		multi = len([x for y,x in enumerate(multi) if x not in multi[:y]])
		multi = True if multi > 1 else False

		try: sysaction = items[0]['action']
		except: sysaction = ''

		isFolder = False if not sysaction == 'episodes' else True

		playbackMenu = control.lang(32063).encode('utf-8') if control.setting('playback.automatic.enabled') == 'true' else control.lang(32064).encode('utf-8')

		traktHas = trakt.getTraktIndicatorsInfo() == True
		watchedMenu = control.lang(32068).encode('utf-8') if traktHas else control.lang(32066).encode('utf-8')
		unwatchedMenu = control.lang(32069).encode('utf-8') if traktHas else control.lang(32067).encode('utf-8')

		unwatchedEnabled = tools.Settings.getBoolean('interface.tvshows.unwatched.enabled')
		unwatchedLimit = tools.Settings.getBoolean('interface.tvshows.unwatched.limit')

		airEnabled = tools.Settings.getBoolean('interface.tvshows.air.enabled')
		if airEnabled:
			airZone = tools.Settings.getInteger('interface.tvshows.air.zone')
			airLocation = tools.Settings.getInteger('interface.tvshows.air.location')
			airFormat = tools.Settings.getInteger('interface.tvshows.air.format')
			airAbbreviation = tools.Settings.getBoolean('interface.tvshows.air.abbreviation')
			airBold = tools.Settings.getBoolean('interface.tvshows.air.bold')
			airLabel = interface.Format.bold(interface.Translation.string(35032) + ': ')

		queueMenu = control.lang(32065).encode('utf-8')

		traktManagerMenu = control.lang(32070).encode('utf-8')

		tvshowBrowserMenu = control.lang(32071).encode('utf-8')

		media = tools.Media()

		for i in items:
			try:
				if not 'label' in i:
					i['label'] = i['title']
				if i['label'] == None or i['label'] == '' or i['label'] == '0':
					i['label'] = '%s %d' % (layoutEpisodeLong, int(i['episode']))

				label = None
				try: label = media.title(tools.Media.TypeEpisode, title = i['label'], season = i['season'], episode = i['episode'])
				except: pass
				if label == None:
					label = i['label']

				if multi == True and not label in i['tvshowtitle'] and not i['tvshowtitle'] in label:
					label = '%s - %s' % (i['tvshowtitle'], label)

				imdb, tvdb, year, season, episode, premiered = i['imdb'], i['tvdb'], i['year'], i['season'], i['episode'], i['premiered']

				# Make new episodes italicself.
				date = tools.Time.datetime(premiered, format = '%Y-%m-%d')
				current = datetime.datetime.now()
				if current <= date or current.date() == date.date():
					label = '[I]' + label + '[/I]'

				systitle = urllib.quote_plus(i['title'])
				systvshowtitle = urllib.quote_plus(i['tvshowtitle'])
				syspremiered = urllib.quote_plus(i['premiered'])

				meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
				meta.update({'mediatype': 'episode'})
				meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, systvshowtitle)})

				# Bubbles
				# Remove default time, since this might mislead users. Rather show no time.
				#if not 'duration' in i: meta.update({'duration': '60'})
				#elif i['duration'] == '0': meta.update({'duration': '60'})

				try: meta.update({'duration': str(int(meta['duration']) * 60)})
				except: pass
				try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
				except: pass
				try: meta.update({'title': i['label']})
				except: pass
				try: meta.update({'year': date.year}) # Kodi uses the year (the year the show started) as the year for the episode. Change it from the premiered date.
				except: pass

				if airEnabled:
					air = []
					airday = None
					airtime = None
					if 'airday' in meta and not meta['airday'] == None and not meta['airday'] == '':
						airday = meta['airday']
					if 'airtime' in meta and not meta['airtime'] == None and not meta['airtime'] == '':
						airtime = meta['airtime']
						if 'airzone' in meta and not meta['airzone'] == None and not meta['airzone'] == '':
							if airLocation == 1: zoneTo = meta['airzone']
							elif airLocation == 2: zoneTo = tools.Time.ZoneUtc
							else: zoneTo = tools.Time.ZoneLocal
							airtime = tools.Time.local(stringTime = meta['airtime'], stringDay = airday, zoneFrom = meta['airzone'], zoneTo = zoneTo)
							if airday:
								airday = airtime[1]
								airtime = airtime[0]
					if airday:
						if airAbbreviation:
							try: airday = airday[:3]
							except: pass
						air.append(airday)
					if airtime: air.append(airtime)
					if len(air) > 0:
						if airFormat == 0: air = airtime
						elif airFormat == 1: air = airday
						elif airFormat == 2: air = air = ' '.join(air)

						if airLocation == 0 or airLocation == 1:
							air = '[%s]' % air

						if airBold: air = interface.Format.bold(air)

						if airLocation == 0: label = '%s %s' % (air, label)
						elif airLocation == 1: label = '%s %s' % (label, air)
						elif airLocation == 2: meta['plot'] = '%s%s\r\n%s' % (airLabel, air, meta['plot'])
						elif airLocation == 3: meta['plot'] = '%s%s\r\n%s' % (airLabel, meta['plot'], air)

					airEnabled = tools.Settings.getBoolean('interface.tvshows.air.enabled')
					if airEnabled:
						airZone = tools.Settings.getInteger('interface.tvshows.air.zone')
						airLocation = tools.Settings.getInteger('interface.tvshows.air.location')
						airFormat = tools.Settings.getInteger('interface.tvshows.air.format')
						airAbbreviation = tools.Settings.getBoolean('interface.tvshows.air.abbreviation')
						airBold = tools.Settings.getBoolean('interface.tvshows.air.bold')

				sysmeta = urllib.quote_plus(json.dumps(meta))

				url = self.parameterize('%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta, self.systime))
				sysurl = urllib.quote_plus(url)

				path = self.parameterize('%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered))

				if isFolder == True:
					url = self.parameterize('%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s' % (sysaddon, systvshowtitle, year, imdb, tvdb, season, episode))


				cm = []

				cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

				if multi == True:
					link = self.parameterize('%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (sysaddon, systvshowtitle, year, imdb, tvdb))
					cm.append((tvshowBrowserMenu, 'Container.Update(%s,return)' % link))

				try:
					overlay = int(playcount.getEpisodeOverlay(indicators, imdb, tvdb, season, episode))
					if overlay == 7:
						if not traktHas:
							link = self.parameterize('%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=6' % (sysaddon, imdb, tvdb, season, episode))
							cm.append((unwatchedMenu, 'RunPlugin(%s)' % link))
						meta.update({'playcount': 1, 'overlay': 7})
					else:
						if not traktHas:
							link = self.parameterize('%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=7' % (sysaddon, imdb, tvdb, season, episode))
							cm.append((watchedMenu, 'RunPlugin(%s)' % link))
						meta.update({'playcount': 0, 'overlay': 6})
				except:
					overlay = None

				if traktCredentials == True:
					link = self.parameterize('%s?action=traktManager&tvdb=%s&season=%s&episode=%s' % (sysaddon, tvdb, season, episode))
					cm.append((traktManagerMenu, 'RunPlugin(%s)' % link))

				if not self.kidsOnly() and control.setting('downloads.manual.enabled') == 'true':
					cm.append((control.lang(33585).encode('utf-8'), 'Container.Update(%s?action=downloadsManager)' % (sysaddon)))

				if isFolder == False:
					cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

				if isOld == True:
					cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))


				item = control.item(label=label)

				if multi and unwatchedEnabled and not overlay == None and not overlay == 7:
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
				item.setProperty('IsPlayable', isPlayable)
				item.setInfo(type='Video', infoLabels = meta)

				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
			except:
				tools.Logger.error
				pass

		# Bubbles
		# Show multi as show, in order to display unwatched count.
		if multi:
			control.content(syshandle, 'tvshows')
			control.directory(syshandle, cacheToDisc=True)
			views.setView('shows', {'skin.estuary': 55, 'skin.confluence': 500})
		else:
			control.content(syshandle, 'episodes')
			control.directory(syshandle, cacheToDisc=True)
			views.setView('episodes', {'skin.estuary': 55, 'skin.confluence': 504})

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

		interface.traktApi()
