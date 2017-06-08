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

import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import xbmcgui
import numbers
import json
import time
import datetime
import calendar
import subprocess
import webbrowser
import sys
import os
import stat
import uuid
import hashlib
import shutil
import imp
import pkgutil
import re
import urlparse
import urllib
import platform
import zipfile
import threading

from resources.lib.externals import pytz
from resources.lib.externals.unidecode import unidecode

class Time(object):

	# Use time.clock() instead of time.time() for processing time.
	# NB: Do not use time.clock(). Gives the wrong answer in timestamp() AND runs very fast in Linux. Hence, in the stream finding dialog, for every real second, Linux progresses 5-6 seconds.
	# http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
	# https://www.tutorialspoint.com/python/time_clock.htm

	ZoneUtc = 'utc'
	ZoneLocal = 'local'

	def __init__(self, start = False):
		self.mStart = None
		if start: self.start()

	def start(self):
		self.mStart = time.time()
		return self.mStart

	def restart(self):
		return self.start()

	def elapsed(self, milliseconds = False):
		if self.mStart == None:
			self.mStart = time.time()
		if milliseconds: return int((time.time() - self.mStart) * 1000)
		else: return int(time.time() - self.mStart)

	def expired(self, expiration):
		return self.elapsed() >= expiration

	@classmethod
	def sleep(self, seconds):
		time.sleep(seconds)

	# UTC timestamp
	@classmethod
	def timestamp(self, fixedTime = None):
		if fixedTime == None:
			# Do not use time.clock(), gives incorrect result for search.py
			return int(time.time())
		else:
			return int(time.mktime(fixedTime.timetuple()))

	# datetime object from string
	@classmethod
	def datetime(self, string, format = '%Y-%m-%d %H:%M:%S'):
		try:
			return datetime.datetime.strptime(string, format)
		except:
			# Older Kodi Python versions do not have the strptime function.
			# http://forum.kodi.tv/showthread.php?tid=112916
			return datetime.datetime.fromtimestamp(time.mktime(time.strptime(string, format)))

	@classmethod
	def localZone(self):
		if time.daylight:
			offsetHour = time.altzone / 3600
		else:
			offsetHour = time.timezone / 3600
		return 'Etc/GMT%+d' % offsetHour

	@classmethod
	def local(self, stringTime, stringDay = None, format = '%H:%M', zoneFrom = ZoneUtc, zoneTo = ZoneLocal):
		result = ''
		try:
			# If only time is given, the date will be set to 1900-01-01 and there are conversion problems if this goes down to 1899.
			if format == '%H:%M':
				# Use current datetime (now) in order to accomodate for daylight saving time.
				stringTime = '%s %s' % (datetime.datetime.now().strftime('%Y-%m-%d'), stringTime)
				formatNew = '%Y-%m-%d %H:%M'
			else:
				formatNew = format

			if zoneFrom == self.ZoneUtc: zoneFrom = pytz.timezone('UTC')
			elif zoneFrom == self.ZoneLocal: zoneFrom = pytz.timezone(self.localZone())
			else: zoneFrom = pytz.timezone(zoneFrom)

			if zoneTo == self.ZoneUtc: zoneTo = pytz.timezone('UTC')
			elif zoneTo == self.ZoneLocal: zoneTo = pytz.timezone(self.localZone())
			else: zoneTo = pytz.timezone(zoneTo)

			timeobject = self.datetime(string = stringTime, format = formatNew)

			if stringDay:
				stringDay = stringDay.lower()
				if stringDay.startswith('mon'): weekday = 0
				elif stringDay.startswith('tue'): weekday = 1
				elif stringDay.startswith('wed'): weekday = 2
				elif stringDay.startswith('thu'): weekday = 3
				elif stringDay.startswith('fri'): weekday = 4
				elif stringDay.startswith('sat'): weekday = 5
				else: weekday = 6
				timeobject += datetime.timedelta(days = (7 - weekday))

			timeobject = zoneFrom.localize(timeobject)
			timeobject = timeobject.astimezone(zoneTo)

			stringTime = timeobject.strftime(format)
			if stringDay:
				stringDay = calendar.day_name[timeobject.weekday()]
				return (stringTime, stringDay)
			else:
				return stringTime
		except:
			Logger.error()
			return stringTime

class Language(object):

	# Cases
	CaseCapital = 0
	CaseUpper = 1
	CaseLower = 2

	Automatic = 'automatic'
	Alternative = 'alternative'

	UniversalName = 'Universal'
	UniversalCode = 'un'

	EnglishName = 'English'
	EnglishCode = 'en'

	Names = [UniversalName, 'Abkhaz', 'Afar', 'Afrikaans', 'Akan', 'Albanian', 'Amharic', 'Arabic', 'Aragonese', 'Armenian', 'Assamese', 'Avaric', 'Avestan', 'Aymara', 'Azerbaijani', 'Bambara', 'Bashkir', 'Basque', 'Belarusian', 'Bengali', 'Bihari', 'Bislama', 'Bokmal', 'Bosnian', 'Breton', 'Bulgarian', 'Burmese', 'Catalan', 'Chamorro', 'Chechen', 'Chichewa', 'Chinese', 'Chuvash', 'Cornish', 'Corsican', 'Cree', 'Croatian', 'Czech', 'Danish', 'Divehi', 'Dutch', 'Dzongkha', EnglishName, 'Esperanto', 'Estonian', 'Ewe', 'Faroese', 'Fijian', 'Finnish', 'French', 'Fula', 'Gaelic', 'Galician', 'Ganda', 'Georgian', 'German', 'Greek', 'Guarani', 'Gujarati', 'Haitian', 'Hausa', 'Hebrew', 'Herero', 'Hindi', 'Hiri Motu', 'Hungarian', 'Icelandic', 'Ido', 'Igbo', 'Indonesian', 'Interlingua', 'Interlingue', 'Inuktitut', 'Inupiaq', 'Irish', 'Italian', 'Japanese', 'Javanese', 'Kalaallisut', 'Kannada', 'Kanuri', 'Kashmiri', 'Kazakh', 'Khmer', 'Kikuyu', 'Kinyarwanda', 'Kirundi', 'Komi', 'Kongo', 'Korean', 'Kurdish', 'Kwanyama', 'Kyrgyz', 'Lao', 'Latin', 'Latvian', 'Limburgish', 'Lingala', 'Lithuanian', 'Luba-Katanga', 'Luxembourgish', 'Macedonian', 'Malagasy', 'Malay', 'Malayalam', 'Maltese', 'Manx', 'Maori', 'Marathi', 'Marshallese', 'Mongolian', 'Nauruan', 'Navajo', 'Ndonga', 'Nepali', 'Northern Ndebele', 'Northern Sami', 'Norwegian', 'Nuosu', 'Nynorsk', 'Occitan', 'Ojibwe', 'Oriya', 'Oromo', 'Ossetian', 'Pali', 'Pashto, Pushto', 'Persian', 'Polish', 'Portuguese', 'Punjabi', 'Quechua', 'Romanian', 'Romansh', 'Russian', 'Samoan', 'Sango', 'Sanskrit', 'Sardinian', 'Serbian', 'Shona', 'Sindhi', 'Sinhalese', 'Slavonic', 'Slovak', 'Slovene', 'Somali', 'Southern Ndebele', 'Southern Sotho', 'Spanish', 'Sundanese', 'Swahili', 'Swati', 'Swedish', 'Tagalog', 'Tahitian', 'Tajik', 'Tamil', 'Tatar', 'Telugu', 'Thai', 'Tibetan', 'Tigrinya', 'Tonga', 'Tsonga', 'Tswana', 'Turkish', 'Turkmen', 'Twi', 'Ukrainian', 'Urdu', 'Uyghur', 'Uzbek', 'Venda', 'Vietnamese', 'Volapuk', 'Walloon', 'Welsh', 'Western Frisian', 'Wolof', 'Xhosa', 'Yiddish', 'Yoruba', 'Zhuang', 'Zulu']
	Codes = [UniversalCode, 'ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae', 'ay', 'az', 'bm', 'ba', 'eu', 'be', 'bn', 'bh', 'bi', 'nb', 'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw', 'co', 'cr', 'hr', 'cs', 'da', 'dv', 'nl', 'dz', EnglishCode, 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'ff', 'gd', 'gl', 'lg', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'is', 'io', 'ig', 'id', 'ia', 'ie', 'iu', 'ik', 'ga', 'it', 'ja', 'jv', 'kl', 'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'rn', 'kv', 'kg', 'ko', 'ku', 'kj', 'ky', 'lo', 'la', 'lv', 'li', 'ln', 'lt', 'lu', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'gv', 'mi', 'mr', 'mh', 'mn', 'na', 'nv', 'ng', 'ne', 'nd', 'se', 'no', 'ii', 'nn', 'oc', 'oj', 'or', 'om', 'os', 'pi', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'rm', 'ru', 'sm', 'sg', 'sa', 'sc', 'sr', 'sn', 'sd', 'si', 'cu', 'sk', 'sl', 'so', 'nr', 'st', 'es', 'su', 'sw', 'ss', 'sv', 'tl', 'ty', 'tg', 'ta', 'tt', 'te', 'th', 'bo', 'ti', 'to', 'ts', 'tn', 'tr', 'tk', 'tw', 'uk', 'ur', 'ug', 'uz', 've', 'vi', 'vo', 'wa', 'cy', 'fy', 'wo', 'xh', 'yi', 'yo', 'za', 'zu']

	@classmethod
	def customization(self):
		return Settings.getBoolean('general.language.customization')

	@classmethod
	def settings(self, single = False):
		languages = []

		language = Settings.getString('general.language.primary')
		if not language == 'None':
			language = self.language(language)
			if language:
				if single: return language
				if not language in languages: languages.append(language)

		language = Settings.getString('general.language.secondary')
		if not language == 'None':
			language = self.language(language)
			if language:
				if single: return language
				if not language in languages: languages.append(language)

		language = Settings.getString('general.language.tertiary')
		if not language == 'None':
			language = self.language(language)
			if language:
				if single: return language
				if not language in languages: languages.append(language)

		if len(languages) == 0: languages.append(self.language(self.EnglishCode))

		if single: return languages[0]
		else: return languages

	@classmethod
	def isUniversal(self, nameOrCode):
		if nameOrCode == None: return False
		elif type(nameOrCode) is tuple: nameOrCode = nameOrCode[0]
		nameOrCode = nameOrCode.lower()
		return nameOrCode == self.UniversalCode.lower() or nameOrCode == self.UniversalName.lower()

	@classmethod
	def isEnglish(self, nameOrCode):
		if nameOrCode == None: return False
		elif type(nameOrCode) is tuple: nameOrCode = nameOrCode[0]
		nameOrCode = nameOrCode.lower()
		return nameOrCode == self.EnglishCode.lower() or nameOrCode == self.EnglishName.lower()

	@classmethod
	def languages(self):
		result = []
		for i in range(len(self.Codes)):
			result.append((self.Codes[i], self.Names[i]))
		return result

	@classmethod
	def names(self, case = CaseCapital):
		if case == self.CaseUpper:
			return [i.upper() for i in self.Names]
		elif case == self.CaseLower:
			return [i.lower() for i in self.Names]
		else:
			return self.Names

	@classmethod
	def codes(self, case = CaseLower):
		if case == self.CaseCapital:
			return [i.capitalize() for i in self.Codes]
		elif case == self.CaseUpper:
			return [i.upper() for i in self.Codes]
		else:
			return self.Codes

	@classmethod
	def language(self, nameOrCode):
		if nameOrCode == None: return None
		elif type(nameOrCode) is tuple: nameOrCode = nameOrCode[0]
		nameOrCode = nameOrCode.lower().strip()

		if self.Automatic in nameOrCode:
			return self.settings(single = True)
		elif self.Alternative in nameOrCode:
			languages = self.settings()
			for language in languages:
				if not language[0] == self.EnglishCode:
					return language
			return languages[0]

		# NB & TODO: Very bad, but easy implementation to compares ISO 639-1 and ISO 639-2 codes. This does not work properley for languages, and a proper map for ISO 639-2 must be added.
		if isinstance(nameOrCode, basestring) and len(nameOrCode) == 3:
			if nameOrCode == 'ger':
					return self.language('de')
			else:
				code = None
				for i in range(len(self.Codes)):
					code = self.Codes[i]
					if nameOrCode.startswith(code) or (code[0] == nameOrCode[0] and code[1] == nameOrCode[2]):
						return (self.Codes[i], self.Names[i])

		for i in range(len(self.Codes)):
			if self.Codes[i] == nameOrCode:
				return (self.Codes[i], self.Names[i])

		for i in range(len(self.Codes)):
			if self.Names[i].lower() == nameOrCode:
				return (self.Codes[i], self.Names[i])

		return None

	@classmethod
	def name(self, nameOrCode):
		if nameOrCode == None: return None
		elif type(nameOrCode) is tuple: nameOrCode = nameOrCode[0]
		nameOrCode = nameOrCode.lower().strip()

		if self.Automatic in nameOrCode:
			return self.settings(single = True)[1]
		elif self.Alternative in nameOrCode:
			languages = self.settings()
			for language in languages:
				if not language[0] == self.EnglishCode:
					return language[1]
			return languages[0][1]

		# NB & TODO: Very bad, but easy implementation to compares ISO 639-1 and ISO 639-2 codes. This does not work properley for languages, and a proper map for ISO 639-2 must be added.
		if isinstance(nameOrCode, basestring) and len(nameOrCode) == 3:
			if nameOrCode == 'ger':
					return self.name('de')
			else:
				code = None
				for i in range(len(self.Codes)):
					code = self.Codes[i]
					if nameOrCode.startswith(code) or (code[0] == nameOrCode[0] and code[1] == nameOrCode[2]):
						return self.Names[i]

		for i in range(len(self.Codes)):
			if self.Codes[i] == nameOrCode:
				return self.Names[i]

		for i in range(len(self.Codes)):
			if self.Names[i].lower() == nameOrCode:
				return self.Names[i]

		return None

	@classmethod
	def code(self, nameOrCode):
		if nameOrCode == None: return None
		elif type(nameOrCode) is tuple: nameOrCode = nameOrCode[0]
		nameOrCode = nameOrCode.lower().strip()

		if self.Automatic in nameOrCode:
			return self.settings(single = True)[0]
		elif self.Alternative in nameOrCode:
			languages = self.settings()
			for language in languages:
				if not language[0] == self.EnglishCode:
					return language[0]
			return languages[0][0]

		# NB & TODO: Very bad, but easy implementation to compares ISO 639-1 and ISO 639-2 codes. This does not work properley for languages, and a proper map for ISO 639-2 must be added.
		if isinstance(nameOrCode, basestring) and len(nameOrCode) == 3:
			if nameOrCode == 'ger':
					return self.code('de')
			else:
				code = None
				for i in range(len(self.Codes)):
					code = self.Codes[i]
					if nameOrCode.startswith(code) or (code[0] == nameOrCode[0] and code[1] == nameOrCode[2]):
						return self.Codes[i]

		for i in range(len(self.Names)):
			if self.Names[i].lower() == nameOrCode:
				return self.Codes[i]

		for i in range(len(self.Codes)):
			if self.Codes[i] == nameOrCode:
				return self.Codes[i]

		return None

class Hash(object):

	@classmethod
	def random(self):
		return str(uuid.uuid4().hex).upper()

	@classmethod
	def sha1(self, data):
		return hashlib.sha1(data).hexdigest().upper()

	@classmethod
	def sha256(self, data):
		return hashlib.sha256(data).hexdigest().upper()

	@classmethod
	def md5(self, data):
		return hashlib.md5(data).hexdigest().upper()

	@classmethod
	def valid(self, hash, length = 40):
		return hash and len(hash) == length and bool(re.match('^[a-fA-F0-9]+', hash))

class Video(object):

	Extensions = ['mp4', 'mpg', 'mpeg', 'mp2', 'm4v', 'm2v', 'mkv', 'avi', 'flv', 'asf', '3gp', '3g2', 'wmv', 'mov', 'qt', 'webm', 'vob']

	@classmethod
	def extensions(self):
		return self.Extensions

	@classmethod
	def extensionValid(self, extension):
		extension = extension.replace('.', '').replace(' ', '').lower()
		return extension in self.Extensions

class Audio(object):

	# Values must correspond to settings.
	StartupNone = 0
	Startup1 = 1
	Startup2 = 2
	Startup3 = 3
	Startup4 = 4
	Startup5 = 5

	@classmethod
	def startup(self, type = None):
		if type == None:
			type = Settings.getInteger('general.launch.sound')
		if type == 0 or type == None:
			return False
		else:
			path = os.path.join(System.pathResources(), 'resources', 'media', 'audio', 'startup', 'startup%d' % type, 'Bubbles')
			return self.play(path = path, notPlaying = True)

	@classmethod
	def play(self, path, notPlaying = True):
		player = xbmc.Player()
		if not notPlaying or not player.isPlaying():
			player.play(path)
			return True
		else:
			return False

# Kodi's thumbnail cache
class Thumbnail(object):

	Directory = 'special://thumbnails'

	@classmethod
	def hash(self, path):
		try:
			path = path.lower()
			bs = bytearray(path.encode())
			crc = 0xffffffff
			for b in bs:
				crc = crc ^ (b << 24)
				for i in range(8):
					if crc & 0x80000000:
						crc = (crc << 1) ^ 0x04C11DB7
					else:
						crc = crc << 1
				crc = crc & 0xFFFFFFFF
			return '%08x' % crc
		except:
			return None

	@classmethod
	def delete(self, path):
		name = self.hash(path)
		if name == None:
			return None
		name += '.jpg'
		file = None
		directories, files = File.listDirectory(self.Directory)
		for f in files:
			if f == name:
				file = os.path.join(self.Directory, f)
				break
		for d in directories:
			dir = os.path.join(self.Directory, d)
			directories2, files2 = File.listDirectory(dir)
			for f in files2:
				if f == name:
					file = os.path.join(dir, f)
					break
			if not file == None:
				break
		if not file == None:
			File.delete(file, force = True)

class Selection(object):

	# Must be integers
	TypeExclude = -1
	TypeUndefined = 0
	TypeInclude = 1

class Kids(object):

	Restriction7 = 0
	Restriction13 = 1
	Restriction16 = 2
	Restriction18 = 3

	@classmethod
	def enabled(self):
		return Settings.getBoolean('general.kids.enabled')

	@classmethod
	def restriction(self):
		return Settings.getInteger('general.kids.restriction')

	@classmethod
	def password(self, hash = True):
		password = Settings.getString('general.kids.password')
		if hash and not(password == None or password == ''): password = Hash.md5(password).lower()
		return password

	@classmethod
	def passwordEmpty(self):
		password = self.password()
		return password == None or password == ''

	@classmethod
	def verify(self, password):
		return not self.enabled() or self.passwordEmpty() or password.lower() == self.password().lower()

	@classmethod
	def locked(self):
		return Settings.getBoolean('general.kids.locked')

	@classmethod
	def lockable(self):
		return not self.passwordEmpty() and not self.locked()

	@classmethod
	def unlockable(self):
		return not self.passwordEmpty() and self.locked()

	@classmethod
	def lock(self):
		if self.locked():
			return True
		else:
			from resources.lib.extensions import interface # Circular import.
			Settings.set('general.kids.locked', True)
			System.restart() # Kodi still keeps the old menus in cache (when going BACK). Clear them by restarting the addon.
			interface.Dialog.confirm(title = 33438, message = 33445)
			return True

	@classmethod
	def unlock(self, internal = False):
		if self.locked():
			from resources.lib.extensions import interface # Circular import.
			password = self.password()
			if password and not password == '':
				match = interface.Dialog.inputPassword(title = 33440, verify = password)
				if not match:
					interface.Dialog.confirm(title = 33440, message = 33441)
					return False
			Settings.set('general.kids.locked', False)
			System.restart() # Kodi still keeps the old menus in cache (when going BACK). Clear them by restarting the addon.
			if not internal:
				interface.Dialog.confirm(title = 33438, message = 33444)
			return True
		else:
			return True

	@classmethod
	def allowed(self, certificate):
		if certificate == None or certificate == '':
			return False

		certificate = certificate.lower().replace(' ', '').replace('-', '').replace('_', '').strip()
		restriction = self.restriction()

		if (certificate  == 'g' or certificate  == 'tvy'):
			return True
		elif (certificate == 'pg' or certificate == 'tvy7') and restriction >= 1:
			return True
		elif (certificate == 'pg13' or certificate == 'tvpg') and restriction >= 2:
			return True
		elif (certificate == 'r' or certificate == 'tv14') and restriction >= 3:
			return True
		return False

class Converter(object):

	Base64 = 'base64'

	@classmethod
	def boolean(self, value, string = False):
		if string:
			return 'true' if value else 'false'
		else:
			if value == True or value == False:
				return value
			elif isinstance(value, numbers.Number):
				return value > 0
			elif isinstance(value, basestring):
				value = value.lower()
				return value == 'true' or value == 'yes' or value == 't' or value == 'y' or value == '1'
			else:
				return False

	@classmethod
	def dictionary(self, jsonData):
		try:
			if jsonData == None:
				return None

			jsonData = json.loads(jsonData)

			# In case the quotes in the string were escaped, causing the first json.loads to return a unicode string.
			try: jsonData = json.loads(jsonData)
			except: pass

			return jsonData
		except:
			return None

	@classmethod
	def unicode(self, string, umlaut = False):
		try:
			if string == None:
				return string
			if umlaut:
				try: string = string.replace(unichr(196), 'AE').replace(unichr(203), 'EE').replace(unichr(207), 'IE').replace(unichr(214), 'OE').replace(unichr(220), 'UE').replace(unichr(228), 'ae').replace(unichr(235), 'ee').replace(unichr(239), 'ie').replace(unichr(246), 'oe').replace(unichr(252), 'ue')
				except: pass
			return unidecode(string.decode('utf-8'))
		except:
			try: return string.encode('ascii', 'ignore')
			except: return string

	@classmethod
	def base64From(self, data, iterations = 1):
		data = str(data)
		for i in range(iterations):
			data = data.decode(self.Base64)
		return data

	@classmethod
	def base64To(self, data, iterations = 1):
		data = str(data)
		for i in range(iterations):
			data = data.encode(self.Base64)
		return data

	@classmethod
	def jsonFrom(self, data):
		return json.loads(data)

	@classmethod
	def jsonTo(self, data):
		return json.dumps(data)

class Cache(object):

	# Example: cacheNamed(functionPointer, 30, val1, val2)
	# If timeout <= 0 or None, will force new retrieval.
	@classmethod
	def cache(self, function, timeout, *arguments):
		from resources.lib.modules import cache
		return cache.get(function, timeout, *arguments)

	# Example: cacheNamed(functionPointer, 30, par1 = val1, par2 = val2)
	# If timeout <= 0 or None, will force new retrieval.
	# NB: DO NOT USE THIS FUNCTION. It seems that this function often does not work. Sometimes it does. Rather cache() and pass the function manually like in debrid.Premiumize.
	'''@classmethod
	def cacheNamed(self, function, timeout, **arguments):
		def cacheNamed(**arguments):
			return function(**arguments)
		return self.cache(cacheNamed, timeout, dict(**arguments)) # arguments must be converted to dict, since cache.get only takes unnamed parameters.
	'''

class Logger(object):

	TypeNotice = xbmc.LOGNOTICE
	TypeError = xbmc.LOGERROR
	TypeSevere = xbmc.LOGSEVERE
	TypeFatal = xbmc.LOGFATAL
	TypeDefault = TypeNotice

	@classmethod
	def log(self, message, message2 = None, message3 = None, message4 = None, message5 = None, name = True, parameters = None, level = TypeDefault):
		divider = ' '
		message = str(message)
		if message2: message += divider + str(message2)
		if message3: message += divider + str(message3)
		if message4: message += divider + str(message4)
		if message5: message += divider + str(message5)
		if name:
			nameValue = System.name().upper()
			if not name == True:
				nameValue += ' ' + name
			if parameters:
				nameValue += ' ['
				if isinstance(parameters, basestring):
					nameValue += parameters
				else:
					nameValue += ', '.join([str(parameter) for parameter in parameters])
				nameValue += ']'
			nameValue += ': '
			message = nameValue + message
		xbmc.log(message, level)

	@classmethod
	def error(self, message = None, exception = True):
		if exception:
			type, value, traceback = sys.exc_info()
			filename = traceback.tb_frame.f_code.co_filename
			linenumber = traceback.tb_lineno
			name = traceback.tb_frame.f_code.co_name
			errortype = type.__name__
			errormessage = value.message
			if message:
				message += ' -> '
			else:
				message = ''
			message += str(errortype) + ' -> ' + errormessage
			parameters = [filename, linenumber, name]
		else:
			parameters = None
		self.log(message, name = 'ERROR', parameters = parameters, level = self.TypeError)

class File(object):

	PrefixSpecial = 'special://'
	PrefixSamba = 'smb://'

	DirectoryHome = PrefixSpecial + 'home'
	DirectoryTemporary = PrefixSpecial + 'temp'

	@classmethod
	def translate(self, path):
		if path.startswith(self.PrefixSpecial):
			path = xbmc.translatePath(path)
		return path

	@classmethod
	def name(self, path):
		name = os.path.basename(os.path.splitext(path)[0])
		if name == '': name = None
		return name

	@classmethod
	def makeDirectory(self, path):
		return xbmcvfs.mkdirs(path)

	@classmethod
	def translatePath(self, path):
		return xbmc.translatePath(path)

	@classmethod
	def joinPath(self, path, *paths):
		return os.path.join(path, *paths)

	@classmethod
	def exists(self, path): # Directory must end with slash
		# Do not use xbmcvfs.exists, since it returns true for http links.
		if path.startswith('http:') or path.startswith('https:') or path.startswith('ftp:') or path.startswith('ftps:'):
			return os.path.exists(path)
		else:
			return xbmcvfs.exists(path)

	@classmethod
	def existsDirectory(self, path):
		if not path.endswith('/') and not path.endswith('\\'):
			path += '/'
		return xbmcvfs.exists(path)

	# If samba file or directory.
	@classmethod
	def samba(self, path):
		return path.startswith(self.PrefixSamba)

	# If network (samba or any other non-local supported Kodi path) file or directory.
	# Path must point to a valid file or directory.
	@classmethod
	def network(self, path):
		return self.samba(path) or (self.exists(path) and not os.path.exists(path))

	@classmethod
	def delete(self, path, force = True):
		try:
			# For samba paths
			try:
				if self.exists(path):
					xbmcvfs.delete(path)
			except:
				pass

			# All with force
			try:
				if self.exists(path):
					if force: os.chmod(path, stat.S_IWRITE) # Remove read only.
					return os.remove(path) # xbmcvfs often has problems deleting files
			except:
				pass

			return not self.exists(path)
		except:
			return False

	@classmethod
	def deleteDirectory(self, path, force = True):
		try:
			# For samba paths
			try:
				if self.existsDirectory(path):
					xbmcvfs.rmdir(path)
					if not self.existsDirectory(path):
						return True
			except:
				pass

			try:
				if self.existsDirectory(path):
					shutil.rmtree(path)
					if not self.existsDirectory(path):
						return True
			except:
				pass

			# All with force
			try:
				if self.existsDirectory(path):
					if force: os.chmod(path, stat.S_IWRITE) # Remove read only.
					os.rmdir(path)
					if not self.existsDirectory(path):
						return True
			except:
				pass

			# Try individual delete
			try:
				if self.existsDirectory(path):
					directories, files = self.listDirectory(path)
					for i in files:
						self.delete(os.path.join(path, i), force = force)
					for i in directories:
						self.deleteDirectory(os.path.join(path, i), force = force)
					try: xbmcvfs.rmdir(path)
					except: pass
					try: shutil.rmtree(path)
					except: pass
					try: os.rmdir(path)
					except: pass
			except:
				Logger.error()
				pass

			return not self.existsDirectory(path)
		except:
			Logger.error()
			return False

	@classmethod
	def size(self, path):
		return xbmcvfs.File(path).size()

	@classmethod
	def writeNow(self, path, value):
		file = xbmcvfs.File(path, 'w')
		result = file.write(str(value))
		file.close()
		return result

	# Returns: directories, files
	@classmethod
	def listDirectory(self, path):
		return xbmcvfs.listdir(path)

	@classmethod
	def copy(self, pathFrom, pathTo, bytes = None, overwrite = False):
		if overwrite and xbmcvfs.exists(pathTo):
			try: xbmcvfs.delete(pathTo)
			except: pass
		if bytes == None:
			return xbmcvfs.copy(pathFrom, pathTo)
		else:
			try:
				fileFrom = xbmcvfs.File(pathFrom)
				fileTo = xbmcvfs.File(pathTo, 'w')
				chunk = min(bytes, 1048576) # 1 MB
				while bytes > 0:
					size = min(bytes, chunk)
					fileTo.write(fileFrom.read(size))
					bytes -= size
				fileFrom.close()
				fileTo.close()
				return True
			except:
				return False

	# Not for samba paths
	@classmethod
	def move(self, pathFrom, pathTo, replace = True):
		if pathFrom == pathTo:
			return False
		if replace:
			try: os.remove(pathTo)
			except: pass
		try:
			shutil.move(pathFrom, pathTo)
			return True
		except:
			return False

class System(object):

	StartupScript = 'special://masterprofile/autoexec.py'

	PluginPrefix = 'plugin://'

	BubblesAddon = 'plugin.video.bubbles'
	BubblesArtwork = 'script.bubbles.artwork'
	BubblesBinaries = 'script.bubbles.binaries'
	BubblesResources = 'script.bubbles.resources'
	BubblesIcons = 'script.bubbles.icons'
	BubblesSkins = 'script.bubbles.skins'

	@classmethod
	def sleep(self, milliseconds):
		time.sleep(int(milliseconds / 1000))

	# If the developers option is enabled.
	@classmethod
	def developers(self):
		return Settings.getString('general.developers.code') == 'opensesame'

	# Simulated restart of the addon.
	@classmethod
	def restart(self, sleep = True):
		System.execute('Container.Update(path,replace)')
		System.execute('ActivateWindow(Home)')
		System.execute('RunAddon(%s)' % self.BubblesAddon)
		if sleep: time.sleep(2)

	@classmethod
	def path(self, id = BubblesAddon):
		try: addon = xbmcaddon.Addon(id)
		except: addon = None
		if addon == None:
			return ''
		else:
			return File.translatePath(addon.getAddonInfo('path').decode('utf-8'))

	@classmethod
	def pathArtwork(self):
		return self.path(self.BubblesArtwork)

	@classmethod
	def pathBinaries(self):
		return self.path(self.BubblesBinaries)

	@classmethod
	def pathIcons(self):
		return self.path(self.BubblesIcons)

	@classmethod
	def pathResources(self):
		return self.path(self.BubblesResources)

	@classmethod
	def pathSkins(self):
		return self.path(self.BubblesSkins)

	# OS user home directory
	@classmethod
	def pathHome(self):
		try: return os.path.expanduser('~')
		except: return None

	@classmethod
	def addon(self, value):
		return xbmcaddon.Addon(self.BubblesAddon).getAddonInfo(value)

	@classmethod
	def id(self):
		return xbmcaddon.Addon(self.BubblesAddon).getAddonInfo('id')

	@classmethod
	def name(self):
		return xbmcaddon.Addon(self.BubblesAddon).getAddonInfo('name')

	@classmethod
	def author(self):
		return xbmcaddon.Addon(self.BubblesAddon).getAddonInfo('author')

	@classmethod
	def version(self):
		return xbmcaddon.Addon(self.BubblesAddon).getAddonInfo('version')

	@classmethod
	def profile(self):
		return File.translatePath(xbmcaddon.Addon(self.BubblesAddon).getAddonInfo('profile').decode('utf-8'))

	@classmethod
	def description(self):
		return xbmcaddon.Addon(self.BubblesAddon).getAddonInfo('description')

	@classmethod
	def disclaimer(self):
		return xbmcaddon.Addon(self.BubblesAddon).getAddonInfo('disclaimer')

	# Checks if an addon is installed
	@classmethod
	def installed(self, id = BubblesAddon):
		try:
			addon = xbmcaddon.Addon(id)
			id = addon.getAddonInfo('id')
			return not id == None and not id == ''
		except:
			return False

	@classmethod
	def execute(self, command):
		return xbmc.executebuiltin(command)

	@classmethod
	def executeScript(self, script, parameters = []):
		command = 'RunScript(' + script
		for parameter in parameters:
			command += ',' + str(parameter)
		command += ')'
		return self.execute(command)

	@classmethod
	def stopScript(self, script):
		return self.execute('StopScript(%s)' % script)

	# action can be passed manually, or as a value in the parameters dictionary.
	@classmethod
	def executePlugin(self, action = None, parameters = {}):
		if action: parameters['action'] = action
		if not parameters == None and not parameters == '' and not parameters == {}:
			if not isinstance(parameters, basestring):
				parameters = urllib.urlencode(parameters)
			if not parameters.startswith('?'):
				parameters = '?' + parameters
		else:
			parameters = ''
		return self.execute('RunPlugin(%s%s/%s)' % (self.PluginPrefix, self.BubblesAddon, parameters))

	@classmethod
	def executeJson(self, query):
		return xbmc.executeJSONRPC(query)

	@classmethod
	def window(self, action = None, parameters = {}):
		if action: parameters['action'] = action
		if not parameters == None and not parameters == '' and not parameters == {}:
			if not isinstance(parameters, basestring):
				parameters = urllib.urlencode(parameters)
			if not parameters.startswith('?'):
				parameters = '?' + parameters
		else:
			parameters = ''
		return System.execute('ActivateWindow(10025,%s%s/%s,return)' % (self.PluginPrefix, self.BubblesAddon, parameters))

	@classmethod
	def temporary(self, directory = None, file = None, bubbles = True, make = True, clear = False):
		path = File.translatePath('special://temp/')
		if bubbles: path = os.path.join(path, System.name().lower())
		if directory: path = os.path.join(path, directory)
		if clear: File.deleteDirectory(path, force = True)
		if make: File.makeDirectory(path)
		if file: path = os.path.join(path, file)
		return path

	@classmethod
	def temporaryRandom(self, directory = None, extension = 'dat', bubbles = True, make = True, clear = False):
		if extension and not extension == '' and not extension.startswith('.'):
			extension = '.' + extension
		file = Hash.random() + extension
		path = self.temporary(directory = directory, file = file, bubbles = bubbles, make = make, clear = clear)
		while File.exists(path):
			file = Hash.random() + extension
			path = self.temporary(directory = directory, file = file, bubbles = bubbles, make = make, clear = clear)
		return path

	@classmethod
	def temporaryClear(self):
		return File.deleteDirectory(self.temporary(make = False))

	@classmethod
	def openLink(self, link, popup = True, front = True):
		from resources.lib.extensions import interface # Circular import.
		interface.Loader.show() # Needs some time to load. Show busy.
		try:
			success = False
			if sys.platform == 'darwin': # OS X
				try:
					subprocess.Popen(['open', link])
					success = True
				except: pass
			if not success:
				webbrowser.open(link, autoraise = front, new = 2) # new = 2 opens new tab.
		except:
			from resources.lib.extensions import clipboard
			clipboard.Clipboard.copyLink(link, popup)
		interface.Loader.hide()

	@classmethod
	def launch(self):
		thread = threading.Thread(target = self._launch)
		thread.start()

	@classmethod
	def _launch(self):
		name = 'bubbleslaunch'
		value = xbmcgui.Window(10000).getProperty(name)
		first = not value or value == '' # First launch
		try: idle = (Time.timestamp() - int(value)) > 10800 # If the last launch was more than 3 hours ago.
		except: idle = True
		if first or idle:
			from resources.lib.extensions import interface
			from resources.lib.extensions import debrid
			from resources.lib.extensions import settings
			from resources.lib.extensions import vpn
			from resources.lib.modules import control

			# Edit the auto launch script.
			self.launchAutomatic()

			# Lightpack
			System.execute('RunPlugin(%s?action=lightpackAnimate&force=0)' % sys.argv[0])

			# Clear Temporary
			System.temporaryClear()

			# Splash
			interface.Splash.popup()

			# Sound
			Audio.startup()

			# Initial Launch
			self.launchInitial()

			# Initial Launch
			settings.Wizard().launchInitial()

			# VPN
			vpn.Vpn().launch(vpn.Vpn.ExecutionBubbles)

			# Quasar
			Quasar.connect()

			# Intialize Premiumize
			debrid.Premiumize().initialize()

			# Clear debrid files
			debrid.Premiumize().deleteLaunch()
			debrid.RealDebrid().deleteLaunch()

			# Copy the select theme background as fanart to the root folder.
			# Ensures that the selected theme also shows outside the addon.
			# Requires first a Bubbles restart (to replace the old fanart) and then a Kodi restart (to load the new fanart, since the old one was still in memory).
			fanartTo = os.path.join(System.path(), 'fanart.jpg')
			Thumbnail.delete(fanartTo) # Delete from cache
			File.delete(fanartTo) # Delete old fanart
			fanartFrom = control.addonFanart()
			if not fanartFrom == None:
				fanartTo = os.path.join(System.path(), 'fanart.jpg')
				File.copy(fanartFrom, fanartTo, overwrite = True)

		xbmcgui.Window(10000).setProperty(name, str(Time.timestamp()))

	@classmethod
	def launchInitial(self):
		if not Settings.getBoolean('internal.launch.initialzed'):
			# Check Hardware
			# Leave for now, since it is adjusted by the configurations wizard. If this is enabled again, make sure to not show it on every launch, only the first.
			'''if Hardware.slow():
				from resources.lib.extensions import interface
				if interface.Dialog.option(title = 33467, message = 33700, labelConfirm = 33011, labelDeny = 33701):
					Settings.launch()'''
			Settings.set('internal.launch.initialzed', False)

	@classmethod
	def launchAutomatic(self):
		identifier = 'BUBBLESLAUNCH'
		if Settings.getBoolean('general.launch.automatic'):
			self.automaticInsert(identifier = identifier, command = 'action=launch')
		else:
			self.automaticRemove(identifier = identifier)

	@classmethod
	def _automaticIdentifier(self, identifier):
		identifier = identifier.upper()
		return ('#[%s]' % identifier, '#[/%s]' % identifier)

	# Checks if a command is in the Kodi startup script.
	@classmethod
	def automaticContains(self, identifier):
		if xbmcvfs.exists(self.StartupScript):
			identifiers = self._automaticIdentifier(identifier)
			file = xbmcvfs.File(self.StartupScript, 'r')
			data = file.read()
			file.close()
			if identifiers[0] in data and identifiers[1] in data:
				return True
		return False

	# Inserts a command into the Kodi startup script.
	@classmethod
	def automaticInsert(self, identifier, command):
		identifiers = self._automaticIdentifier(identifier)
		data = ''
		contains = False

		if xbmcvfs.exists(self.StartupScript):
			file = xbmcvfs.File(self.StartupScript, 'r')
			data = file.read()
			file.close()
			if identifiers[0] in data and identifiers[1] in data:
				contains = True

		if contains:
			return False
		else:
			id = self.id()
			module = identifier.lower() + 'xbmc'
			command = command.replace(self.PluginPrefix, '').replace(id, '')
			while command.startswith('/') or command.startswith('?'):
				command = command[1:]
			command = self.PluginPrefix + id + '/?' + command
			content = '%s\n%s\nimport xbmc as %s\nif %s.getCondVisibility("System.HasAddon(%s)") == 1: %s.executebuiltin("RunPlugin(%s)")\n%s' % (data, identifiers[0], module, module, id, module, command, identifiers[1])
			file = xbmcvfs.File(self.StartupScript, 'w')
			file.write(content)
			file.close()
			return True

	# Removes a command from the Kodi startup script.
	@classmethod
	def automaticRemove(self, identifier):
		identifiers = self._automaticIdentifier(identifier)
		data = ''
		contains = False
		indexStart = 0
		indexEnd = 0
		if xbmcvfs.exists(self.StartupScript):
			file = xbmcvfs.File(self.StartupScript, 'r')
			data = file.read()
			file.close()
			if data and not data == '':
				data += '\n'
				indexStart = data.find(identifiers[0])
				if indexStart >= 0:
					indexEnd = data.find(identifiers[1]) + len(identifiers[1])
					contains = True

		if contains:
			data = data[:indexStart] + data[indexEnd:]
			file = xbmcvfs.File(self.StartupScript, 'w')
			file.write(data)
			file.close()
			return True
		else:
			return False

	#	[
	#		['title' : 'Category 1', 'items' : [{'title' : 'Name 1', 'value' : 'Value 1', 'link' : True}, {'title' : 'Name 2', 'value' : 'Value 2'}]]
	#		['title' : 'Category 2', 'items' : [{'title' : 'Name 3', 'value' : 'Value 3', 'link' : False}, {'title' : 'Name 4', 'value' : 'Value 4'}]]
	#	]
	@classmethod
	def information(self):
		from resources.lib.extensions import convert

		items = []

		# System
		system = self.informationSystem()
		subitems = []
		subitems.append({'title' : 'Name', 'value' : system['name']})
		subitems.append({'title' : 'Version', 'value' : system['version']})
		if not system['codename'] == None: subitems.append({'title' : 'Codename', 'value' : system['codename']})
		subitems.append({'title' : 'Family', 'value' : system['family']})
		subitems.append({'title' : 'Architecture', 'value' : system['architecture']})
		subitems.append({'title' : 'Processors', 'value' : str(Hardware.processors())})
		subitems.append({'title' : 'Memory', 'value' : convert.ConverterSize(value =  Hardware.memory()).stringOptimal()})
		items.append({'title' : 'System', 'items' : subitems})

		# Python
		system = self.informationPython()
		subitems = []
		subitems.append({'title' : 'Version', 'value' : system['version']})
		subitems.append({'title' : 'Implementation', 'value' : system['implementation']})
		subitems.append({'title' : 'Architecture', 'value' : system['architecture']})
		items.append({'title' : 'Python', 'items' : subitems})

		# Kodi
		system = self.informationKodi()
		subitems = []
		subitems.append({'title' : 'Name', 'value' : system['name']})
		subitems.append({'title' : 'Version', 'value' : system['version']})
		items.append({'title' : 'Kodi', 'items' : subitems})

		# Addon
		system = self.informationAddon()
		subitems = []
		subitems.append({'title' : 'Name', 'value' : system['name']})
		subitems.append({'title' : 'Author', 'value' : system['author']})
		subitems.append({'title' : 'Version', 'value' : system['version']})
		items.append({'title' : 'Addon', 'items' : subitems})

		from resources.lib.extensions import interface
		return interface.Dialog.information(title = 33467, items = items)

	@classmethod
	def informationSystem(self):
		system = platform.system().capitalize()
		version = platform.release().capitalize()

		distribution = platform.dist()
		distributionHas = not distribution == None and not distribution[0] == None and not distribution[0] == ''
		distributionName = distribution[0].capitalize() if distributionHas else None
		distributionVersion = distribution[1].capitalize() if distributionHas and not distribution[1] == None and not distribution[1] == '' else None
		distributionCodename = distribution[2].capitalize() if distributionHas and not distribution[2] == None and not distribution[2] == '' else None

		return {
			'family' : system,
			'name' : distributionName if distributionHas else system,
			'codename' : distributionCodename if distributionHas else None,
			'version' : distributionVersion if distributionHas else version,
			'architecture' : '64 bit' if '64' in platform.processor() else '32 bit',
		}

	@classmethod
	def informationPython(self):
		return {
			'implementation' : platform.python_implementation(),
			'version' : platform.python_version(),
			'architecture' : '64 bit' if '64' in platform.architecture() else '32 bit',
		}

	@classmethod
	def informationKodi(self):
		spmc = 'spmc' in xbmc.translatePath('special://xbmc').lower() or 'spmc' in xbmc.translatePath('special://logpath').lower()
		version = xbmc.getInfoLabel('System.BuildVersion')
		index = version.find(' ')
		if index >= 0: version = version[:index].strip()
		return {
			'name' : 'SPMC' if spmc else 'Kodi',
			'version' : version,
		}

	@classmethod
	def informationAddon(self):
		return {
			'name' : self.name(),
			'author' : self.author(),
			'version' : self.version(),
		}

	@classmethod
	def manager(self):
		self.execute('ActivateWindow(systeminfo)')

	@classmethod
	def clean(self, confirm = True):
		from resources.lib.extensions import interface
		if confirm:
			choice = interface.Dialog.option(title = 33468, message = 33469)
		else:
			choice = True
		if choice:
			path = File.translate(File.PrefixSpecial + 'masterprofile/addon_data/' + System.id())
			File.deleteDirectory(path = path, force = True)
			self.temporaryClear()

class Settings(object):

	ParameterDefault = 'default'

	CategoryGeneral = 0
	CategoryInterface = 1
	CategoryScraping = 2
	CategoryProviders = 3
	CategoryAccounts = 4
	CategoryManual = 5
	CategoryAutomation = 6
	CategoryStreaming = 7
	CategoryDownloads = 8
	CategorySubtitles = 9
	CategoryLightpack = 10

	@classmethod
	def launch(self, category = None, section = None):
		from resources.lib.extensions import interface
		interface.Loader.hide()
		System.execute('Addon.OpenSettings(%s)' % System.id())
		if not category == None:
			System.execute('SetFocus(%i)' % (int(category) + 100))
		if not section == None:
			System.execute('SetFocus(%i)' % (int(section) + 200))

	@classmethod
	def data(self):
		data = None
		path = os.path.join(System.path(), 'resources', 'settings.xml')
		with open(path, 'r') as file:
			data = file.read()
		return data

	@classmethod
	def set(self, id, value):
		if value is True or value is False: # Use is an not ==, becasue checks type as well. Otherwise int/float might also be true.
			value = Converter.boolean(value, string = True)
		else:
			value = str(value)
		xbmcaddon.Addon(System.BubblesAddon).setSetting(id = id, value = value)

	# wait : number of seconds to sleep after command, since it takes a while to send.
	@classmethod
	def external(self, values, wait = 0.1):
		System.executePlugin(action = 'settingsExternal', parameters = values)
		Time.sleep(wait)

	# values is a dictionary.
	@classmethod
	def externalSave(self, values):
		if 'action' in values: del values['action']
		for id, value in values.iteritems():
			self.set(id = id, value = value, external = False)

	# Retrieve the values directly from the original settings instead of the saved user XML.
	# This is for internal values/settings that have a default value. If these values change, they are not propagate to the user XML, since the value was already set from a previous version.
	@classmethod
	def raw(self, id, parameter = ParameterDefault):
		try:
			data = self.data()
			indexStart = data.find(id)
			if indexStart < 0: return None
			indexEnd = data.find('/>', indexStart)
			if indexEnd < 0: return None
			data = data[indexStart : indexEnd]
			indexStart = data.find(parameter)
			if indexStart < 0: return None
			indexStart = data.find('"', indexStart) + 1
			indexEnd = data.find('"', indexStart)
			return data[indexStart : indexEnd]
		except:
			return None

	@classmethod
	def get(self, id, raw = False):
		if raw:
			return self.raw(id)
		else:
			return xbmcaddon.Addon(System.BubblesAddon).getSetting(id)

	@classmethod
	def getString(self, id, raw = False):
		return self.get(id = id, raw = raw)

	@classmethod
	def getBoolean(self, id, raw = False):
		return Converter.boolean(self.get(id = id, raw = raw))

	@classmethod
	def getBool(self, id, raw = False):
		return self.getBoolean(id = id, raw = raw)

	@classmethod
	def getNumber(self, id, raw = False):
		return self.getDecimal(id = id, raw = raw)

	@classmethod
	def getDecimal(self, id, raw = False):
		value = self.get(id = id, raw = raw)
		try: return float(value)
		except: return 0

	@classmethod
	def getFloat(self, id, raw = False):
		return self.getDecimal(id = id, raw = raw)

	@classmethod
	def getInteger(self, id, raw = False):
		value = self.get(id = id, raw = raw)
		try: return int(value)
		except: return 0

	@classmethod
	def getInt(self, id, raw = False):
		return self.getInteger(id = id, raw = raw)

###################################################################
# MEDIA
###################################################################

class Media(object):

	TypeNone = None
	TypeMovie = 'movie'
	TypeDocumentary = 'documentary'
	TypeShort = 'short'
	TypeShow = 'show'
	TypeSeason = 'season'
	TypeEpisode = 'episode'

	NameSeasonLong = xbmcaddon.Addon(System.BubblesAddon).getLocalizedString(32055).encode('utf-8')
	NameSeasonShort = NameSeasonLong[0].upper()
	NameEpisodeLong = xbmcaddon.Addon(System.BubblesAddon).getLocalizedString(33028).encode('utf-8')
	NameEpisodeShort = NameEpisodeLong[0].upper()

	OrderTitle = 0
	OrderTitleYear = 1
	OrderYearTitle = 2
	OrderSeason = 3
	OrderEpisode = 4
	OrderSeasonEpisode = 5
	OrderEpisodeTitle = 6
	OrderSeasonEpisodeTitle = 7

	Default = 0

	DefaultMovie = 4
	DefaultDocumentary = 4
	DefaultShort = 4
	DefaultShow = 0
	DefaultSeason = 0
	DefaultEpisode = 6

	DefaultAeonNoxMovie = 0
	DefaultAeonNoxDocumentary = 0
	DefaultAeonNoxShort = 0
	DefaultAeonNoxShow = 0
	DefaultAeonNoxSeason = 0
	DefaultAeonNoxEpisode = 0

	FormatsTitle = [
		(OrderTitle,		'%s'),
		(OrderTitleYear,	'%s %d'),
		(OrderTitleYear,	'%s. %d'),
		(OrderTitleYear,	'%s - %d'),
		(OrderTitleYear,	'%s (%d)'),
		(OrderTitleYear,	'%s [%d]'),
		(OrderYearTitle,	'%d %s'),
		(OrderYearTitle,	'%d. %s'),
		(OrderYearTitle,	'%d - %s'),
		(OrderYearTitle,	'(%d) %s'),
		(OrderYearTitle,	'[%d] %s'),
	]

	FormatsSeason = [
		(OrderSeason,	NameSeasonLong + ' %01d'),
		(OrderSeason,	NameSeasonLong + ' %02d'),
		(OrderSeason,	NameSeasonShort + ' %01d'),
		(OrderSeason,	NameSeasonShort + ' %02d'),
		(OrderSeason,	'%01d ' + NameSeasonLong),
		(OrderSeason,	'%02d ' + NameSeasonLong),
		(OrderSeason,	'%01d. ' + NameSeasonLong),
		(OrderSeason,	'%02d. ' + NameSeasonLong),
		(OrderSeason,	'%01d'),
		(OrderSeason,	'%02d'),
	]

	FormatsEpisode = [
		(OrderTitle,				'%s'),
		(OrderEpisodeTitle,			'%01d %s'),
		(OrderEpisodeTitle,			'%02d %s'),
		(OrderEpisodeTitle,			'%01d. %s'),
		(OrderEpisodeTitle,			'%02d. %s'),
		(OrderSeasonEpisodeTitle,	'%01dx%01d %s'),
		(OrderSeasonEpisodeTitle,	'%01dx%02d %s'),
		(OrderSeasonEpisodeTitle,	'%02dx%02d %s'),
		(OrderEpisodeTitle,			NameEpisodeShort + '%01d %s'),
		(OrderEpisodeTitle,			NameEpisodeShort + '%02d %s'),
		(OrderEpisodeTitle,			NameEpisodeShort + '%01d. %s'),
		(OrderEpisodeTitle,			NameEpisodeShort + '%02d. %s'),
		(OrderSeasonEpisodeTitle,	NameSeasonShort + '%01d' + NameEpisodeShort + '%01d %s'),
		(OrderSeasonEpisodeTitle,	NameSeasonShort + '%01d' + NameEpisodeShort + '%02d %s'),
		(OrderSeasonEpisodeTitle,	NameSeasonShort + '%02d' + NameEpisodeShort + '%02d %s'),
		(OrderEpisode,				'%01d'),
		(OrderEpisode,				'%02d'),
		(OrderSeasonEpisode,		'%01dx%01d'),
		(OrderSeasonEpisode,		'%01dx%02d'),
		(OrderSeasonEpisode,		'%02dx%02d'),
		(OrderEpisode,				NameEpisodeShort + '%01d'),
		(OrderEpisode,				NameEpisodeShort + '%02d'),
		(OrderSeasonEpisode,		NameSeasonShort + '%01d' + NameEpisodeShort + '%01d'),
		(OrderSeasonEpisode,		NameSeasonShort + '%01d' + NameEpisodeShort + '%02d'),
		(OrderSeasonEpisode,		NameSeasonShort + '%02d' + NameEpisodeShort + '%02d'),
	]

	Formats = None

	@classmethod
	def _format(self, format, title = None, year = None, season = None, episode = None):
		order = format[0]
		format = format[1]
		if order == self.OrderTitle:
			return format % (title)
		elif order == self.OrderTitleYear:
			return format % (title, year)
		elif order == self.OrderYearTitle:
			return format % (year, title)
		elif order == self.OrderSeason:
			return format % (season)
		elif order == self.OrderEpisode:
			return format % (episode)
		elif order == self.OrderSeasonEpisode:
			return format % (season, episode)
		elif order == self.OrderEpisodeTitle:
			return format % (episode, title)
		elif order == self.OrderSeasonEpisodeTitle:
			return format % (season, episode, title)
		else:
			return title

	@classmethod
	def _extract(self, metadata, encode = False):
		title = metadata['tvshowtitle'] if 'tvshowtitle' in metadata else metadata['title']
		if encode: title = Converter.unicode(string = title, umlaut = True)
		year = int(metadata['year']) if 'year' in metadata else None
		season = int(metadata['season']) if 'season' in metadata else None
		episode = int(metadata['episode']) if 'episode' in metadata else None
		return (title, year, season, episode)

	@classmethod
	def _data(self, title, year, season, episode, encode = False):
		if not title == None and encode: title = Converter.unicode(string = title, umlaut = True)
		if not year == None: year = int(year)
		if not season == None: season = int(season)
		if not episode == None: episode = int(episode)
		return (title, year, season, episode)

	@classmethod
	def _initialize(self):
		if self.Formats == None:
			from resources.lib.extensions import interface
			aeonNox = interface.Skin.isBubblesAeonNox()
			self.Formats = {}

			setting = Settings.getInteger('interface.title.movies')
			if setting == self.Default:
				setting = self.DefaultAeonNoxMovie if aeonNox else self.DefaultMovie
			else:
				setting -= 1
			self.Formats[self.TypeMovie] = self.FormatsTitle[setting]

			setting = Settings.getInteger('interface.title.documentaries')
			if setting == self.Default:
				setting = self.DefaultAeonNoxDocumentary if aeonNox else self.DefaultDocumentary
			else:
				setting -= 1
			self.Formats[self.TypeDocumentary] = self.FormatsTitle[setting]

			setting = Settings.getInteger('interface.title.shorts')
			if setting == self.Default:
				setting = self.DefaultAeonNoxShort if aeonNox else self.DefaultShort
			else:
				setting -= 1
			self.Formats[self.TypeShort] = self.FormatsTitle[setting]

			setting = Settings.getInteger('interface.title.shows')
			if setting == self.Default:
				setting = self.DefaultAeonNoxShow if aeonNox else self.DefaultShow
			else:
				setting -= 1
			self.Formats[self.TypeShow] = self.FormatsTitle[setting]

			setting = Settings.getInteger('interface.title.seasons')
			if setting == self.Default:
				setting = self.DefaultAeonNoxSeason if aeonNox else self.DefaultSeason
			else:
				setting -= 1
			self.Formats[self.TypeSeason] = self.FormatsSeason[setting]

			setting = Settings.getInteger('interface.title.episodes')
			if setting == self.Default:
				setting = self.DefaultAeonNoxEpisode if aeonNox else self.DefaultEpisode
			else:
				setting -= 1
			self.Formats[self.TypeEpisode] = self.FormatsEpisode[setting]

	@classmethod
	def title(self, type = TypeNone, metadata = None, title = None, year = None, season = None, episode = None, encode = False):
		if not metadata == None:
			title, year, season, episode = self._extract(metadata = metadata, encode = encode)
		title, year, season, episode = self._data(title = title, year = year, season = season, episode = episode, encode = encode)

		if type == self.TypeNone:
			if not season == None and not episode == None:
				type = self.TypeEpisode
			if not season == None:
				type = self.TypeSeason
			else:
				type = self.TypeMovie

		self._initialize()
		format = self.Formats[type]

		return self._format(format = format, title = title, year = year, season = season, episode = episode)

	# Raw title to search on the web/scrapers.
	@classmethod
	def titleUniversal(self, metadata = None, title = None, year = None, season = None, episode = None, encode = False):
		if not metadata == None:
			title, year, season, episode = self._extract(metadata = metadata, encode = encode)
		title, year, season, episode = self._data(title = title, year = year, season = season, episode = episode, encode = encode)

		if not season == None and not episode == None:
			return '%s S%02dE%02d' % (title, season, episode)
		elif not year == None:
			return  '%s (%s)' % (title, year)
		else:
			return title

###################################################################
# LIGHTPACK
###################################################################

from resources.lib.externals.lightpack import lightpack

class Lightpack(object):

	StatusUnknown = None
	StatusOn = 'on'
	StatusOff = 'off'

	# Number of LEDs in Lightpack
	MapSize = 10

	PathWindows = ['C:\\Program Files (x86)\\Prismatik\\Prismatik.exe', 'C:\\Program Files\\Prismatik\\Prismatik.exe']
	PathLinux = ['/usr/bin/prismatik', '/usr/local/bin/prismatik']

	def __init__(self):
		self.mError = False

		self.mEnabled = Settings.getBoolean('lightpack.enabled')

		self.mPrismatikMode = Settings.getInteger('lightpack.prismatik.mode')
		self.mPrismatikLocation = Settings.getString('lightpack.prismatik.location')

		self.mLaunchAutomatic = Settings.getBoolean('lightpack.launch.automatic')
		self.mLaunchAnimation = Settings.getBoolean('lightpack.launch.animation')

		self.mProfileFixed = Settings.getBoolean('lightpack.profile.fixed')
		self.mProfileName = Settings.getString('lightpack.profile.name')

		self.mCount = Settings.getInteger('lightpack.count')
		self.mMap = self._map()

		self.mHost = Settings.getString('lightpack.connection.host')
		self.mPort = Settings.getInteger('lightpack.connection.port')
		self.mAuthorization = Settings.getBoolean('lightpack.connection.authorization')
		self.mApiKey = Settings.getString('lightpack.connection.api')

		self.mLightpack = None
		self._initialize()

	def __del__(self):
		try: self._unlock()
		except: pass
		try: self._disconnect()
		except: pass

	def _map(self):
		result = []
		set = 10
		for i in range(self.mCount):
			start = self.MapSize * i
			for j in range(1, self.MapSize + 1):
				result.append(start + j)
		return result

	def _initialize(self):
		if not self.mEnabled:
			return

		api = self.mApiKey if self.mAuthorization else ''
		self.mLightpack = lightpack.lightpack(self.mHost, self.mPort, api, self.mMap)
		try:
			if not self._connect():
				raise Exception()
		except:
			try:
				if self.mLaunchAutomatic:
					automatic = self.mPrismatikMode == 0 or self.mPrismatikPath == None or self.mPrismatikPath == ''

					if 'win' in sys.platform or 'nt' in sys.platform:
						command = 'start "Prismatik" /B /MIN "%s"'
						if automatic:
							executed = False
							for path in self.PathWindows:
								if os.path.exists(path):
									os.system(command % path)
									executed = True
									break
							if not executed:
								os.system('prismatik') # Global path
						else:
							os.system(command % self.mPrismatikPath)
					elif 'darwin' in sys.platform or 'max' in sys.platform:
						os.system('open "' + self.mPrismatikPath + '"')
					else:
						command = '"%s" &'
						if automatic:
							executed = False
							for path in self.PathLinux:
								if os.path.exists(path):
									os.system(command % path)
									executed = True
									break
							if not executed:
								os.system('prismatik') # Global path
						else:
							os.system(command % self.mPrismatikPath)

					time.sleep(3)
					self._connect()
			except:
				self._errorSet()

		try:
			if self.status() == self.StatusUnknown:
				self.mLightpack = None
			else:
				try:
					if self.mProfileFixed and self.mProfileName and not self.mProfileName == '':
						self._profileSet(self.mProfileName)
				except:
					self._errorSet()
		except:
			self.mLightpack = None

	def _error(self):
		return self.mError

	def _errorSuccess(self):
		return not self.mError

	def _errorSet(self):
		self.mError = True

	def _errorClear(self):
		self.mError = False

	def _connect(self):
		return self.mLightpack.connect() >= 0

	def _disconnect(self):
		self.mLightpack.disconnect()

	def _lock(self):
		self.mLightpack.lock()

	def _unlock(self):
		self.mLightpack.unlock()

	# Color is RGB array or hex. If index is None, uses all LEDs.
	def _colorSet(self, color, index = None, lock = False):
		if lock: self.mLightpack.lock()

		if isinstance(color, basestring):
			color = color.replace('#', '')
			if len(color) == 6:
				color = 'FF' + color
			color = [int(color[i : i + 2], 16) for i in range(2, 8, 2)]

		if index == None:
			self.mLightpack.setColorToAll(color[0], color[1], color[2])
		else:
			self.mLightpack.setColor(index, color[0], color[1], color[2])

		if lock: self.mLightpack.unlock()

	def _profileSet(self, profile):
		try:
			self._errorClear()
			self._lock()
			self.mLightpack.setProfile(profile)
			self._unlock()
		except:
			self._errorSet()
		return self._errorSuccess()

	def _message(self):
		from resources.lib.extensions import interface
		interface.Dialog.confirm(title = 33406, message = 33410)

	@classmethod
	def settings(self):
		Settings.launch(category = Settings.CategoryLightpack)

	def enabled(self):
		return self.mEnabled

	def status(self):
		if not self.mEnabled:
			return self.StatusUnknown

		try:
			self._errorClear()
			self._lock()
			status = self.mLightpack.getStatus()
			self._unlock()
			return status.strip()
		except:
			self._errorSet()
		return self.StatusUnknown

	def statusUnknown(self):
		return self.status() == self.StatusUnknown

	def statusOn(self):
		return self.status() == self.StatusOn

	def statusOff(self):
		return self.status() == self.StatusOff

	def switchOn(self, message = False):
		if not self.mEnabled:
			return False

		try:
			self._errorClear()
			self._lock()
			self.mLightpack.turnOn()
			self._unlock()
		except:
			self._errorSet()
		success = self._errorSuccess()
		if not success and message: self._message()
		return success

	def switchOff(self, message = False):
		if not self.mEnabled:
			return False

		try:
			self._errorClear()
			self._lock()
			self.mLightpack.turnOff()
			self._unlock()
		except:
			self._errorSet()
		success = self._errorSuccess()
		if not success and message: self._message()
		return success

	def _animateSpin(self, color):
		for i in range(len(self.mMap)):
			self._colorSet(color = color, index = i)
			time.sleep(0.1)

	def animate(self, force = True, message = False, delay = False):
		if not self.mEnabled:
			return False

		if force or self.mLaunchAnimation:
			try:
				self.switchOn()
				self._errorClear()
				if delay: # The Lightpack sometimes gets stuck on the red light on startup animation. Maybe this delay will solve that?
					time.sleep(1)
				self._lock()

				for i in range(2):
					self._animateSpin('FFFF0000')
					self._animateSpin('FFFF00FF')
					self._animateSpin('FF0000FF')
					self._animateSpin('FF00FFFF')
					self._animateSpin('FF00FF00')
					self._animateSpin('FFFFFF00')

				self._unlock()
			except:
				self._errorSet()
		else:
			return False
		success = self._errorSuccess()
		if not success and message: self._message()
		return success

###################################################################
# HARDWARE
###################################################################

class Hardware(object):

	PerformanceSlow = 'slow'
	PerformanceMedium = 'medium'
	PerformanceFast = 'fast'

	ConfigurationSlow = {'processors' : 2, 'memory' : 2147483648}
	ConfigurationMedium = {'processors' : 4, 'memory' : 4294967296}

	@classmethod
	def performance(self):
		processors = self.processors()
		memory = self.memory()

		if processors == None and memory == None:
			return self.PerformanceMedium

		if not processors == None and not self.ConfigurationSlow['processors'] == None and processors <= self.ConfigurationSlow['processors']:
			return self.PerformanceSlow
		if not memory == None and not self.ConfigurationSlow['memory'] == None and memory <= self.ConfigurationSlow['memory']:
			return self.PerformanceSlow

		if not processors == None and not self.ConfigurationMedium['processors'] == None and processors <= self.ConfigurationMedium['processors']:
			return self.PerformanceMedium
		if not memory == None and not self.ConfigurationMedium['memory'] == None and memory <= self.ConfigurationMedium['memory']:
			return self.PerformanceMedium

		return self.PerformanceFast

	@classmethod
	def slow(self):
		processors = self.processors()
		if not processors == None and not self.ConfigurationSlow['processors'] == None and processors <= self.ConfigurationSlow['processors']:
			return True
		memory = self.memory()
		if not memory == None and not self.ConfigurationSlow['memory'] == None and memory <= self.ConfigurationSlow['memory']:
			return True
		return False

	@classmethod
	def processors(self):
		# http://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python

		# Python 2.6+
		try:
			import multiprocessing
			return multiprocessing.cpu_count()
		except: pass

		# PSUtil
		try:
			import psutil
			return psutil.cpu_count() # psutil.NUM_CPUS on old versions
		except: pass

		# POSIX
		try:
			result = int(os.sysconf('SC_NPROCESSORS_ONLN'))
			if result > 0: return result
		except: pass

		# Windows
		try:
			result = int(os.environ['NUMBER_OF_PROCESSORS'])
			if result > 0: return result
		except: pass

		# jython
		try:
			from java.lang import Runtime
			runtime = Runtime.getRuntime()
			result = runtime.availableProcessors()
			if result > 0: return result
		except: pass

		# cpuset
		# cpuset may restrict the number of *available* processors
		try:
			result = re.search(r'(?m)^Cpus_allowed:\s*(.*)$', open('/proc/self/status').read())
			if result:
				result = bin(int(result.group(1).replace(',', ''), 16)).count('1')
				if result > 0: return result
		except: pass

		# BSD
		try:
			sysctl = subprocess.Popen(['sysctl', '-n', 'hw.ncpu'], stdout=subprocess.PIPE)
			scStdout = sysctl.communicate()[0]
			result = int(scStdout)
			if result > 0: return result
		except: pass

		# Linux
		try:
			result = open('/proc/cpuinfo').read().count('processor\t:')
			if result > 0: return result
		except: pass

		# Solaris
		try:
			pseudoDevices = os.listdir('/devices/pseudo/')
			result = 0
			for pd in pseudoDevices:
				if re.match(r'^cpuid@[0-9]+$', pd):
					result += 1
			if result > 0: return result
		except: pass

		# Other UNIXes (heuristic)
		try:
			try:
				dmesg = open('/var/run/dmesg.boot').read()
			except IOError:
				dmesgProcess = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE)
				dmesg = dmesgProcess.communicate()[0]
			result = 0
			while '\ncpu' + str(result) + ':' in dmesg:
				result += 1
			if result > 0: return result
		except: pass

		return None

	@classmethod
	def memory(self):
		try:
			from psutil import virtual_memory
			memory = virtual_memory().total
			if memory > 0: return memory
		except: pass

		try:
			memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
			if memory > 0: return memory
		except: pass

		try:
			memory = dict((i.split()[0].rstrip(':'),int(i.split()[1])) for i in open('/proc/meminfo').readlines())
			memory = memory['MemTotal'] * 1024
			if memory > 0: return memory
		except: pass

		try:
			from ctypes import Structure, c_int32, c_uint64, sizeof, byref, windll
			class MemoryStatusEx(Structure):
				_fields_ = [
					('length', c_int32),
					('memoryLoad', c_int32),
					('totalPhys', c_uint64),
					('availPhys', c_uint64),
					('totalPageFile', c_uint64),
					('availPageFile', c_uint64),
					('totalVirtual', c_uint64),
					('availVirtual', c_uint64),
					('availExtendedVirtual', c_uint64)]
				def __init__(self):
					self.length = sizeof(self)
			memory = MemoryStatusEx()
			windll.kernel32.GlobalMemoryStatusEx(byref(memory))
			memory = memory.totalPhys
			if memory > 0: return memory
		except: pass

		return None

###################################################################
# EXTENSIONS
###################################################################

class Extensions(object):

	# Types
	TypeRequired = 'required'
	TypeRecommended = 'recommended'
	TypeOptional = 'optional'

	# IDs
	IdBubblesAddon = 'plugin.video.bubbles'
	IdBubblesArtwork = 'script.bubbles.artwork'
	IdBubblesBinaries = 'script.bubbles.binaries'
	IdBubblesResources = 'script.bubbles.resources'
	IdBubblesIcons = 'script.bubbles.icons'
	IdBubblesSkins = 'script.bubbles.skins'
	IdBubblesAeonNox = 'skin.bubbles.aeon.nox'
	IdUrlResolver = 'script.module.urlresolver'
	IdMetaHandler = 'script.module.metahandler'
	IdTrakt = 'script.trakt'
	IdQuasar = 'plugin.video.quasar'
	IdQuasarRepository = 'repository.quasar'

	@classmethod
	def settings(self, id):
		try:
			System.execute('Addon.OpenSettings(%s)' % id)
			return True
		except:
			return False

	@classmethod
	def launch(self, id):
		try:
			System.execute('RunAddon(%s)' % id)
			return True
		except:
			return False

	@classmethod
	def installed(self, id):
		try:
			idReal = xbmcaddon.Addon(id).getAddonInfo('id')
			return id == idReal
		except:
			return False

	@classmethod
	def enable(self, id, refresh = False):
		try: System.execute('InstallAddon(%s)' % id)
		except: pass
		try: System.executeJson('{"jsonrpc" : "2.0", "method" : "Addons.SetAddonEnabled", "params" : {"addonid" : "%s", "enabled" : true}, "id" : 1}' % id)
		except: pass
		if refresh:
			try: System.execute('Container.Refresh')
			except: pass

	@classmethod
	def disable(self, id, refresh = False):
		try: System.executeJson('{"jsonrpc" : "2.0", "method" : "Addons.SetAddonEnabled", "params" : {"addonid" : "%s", "enabled" : false}, "id" : 1}' % id)
		except: pass
		if refresh:
			try: System.execute('Container.Refresh')
			except: pass

	@classmethod
	def list(self):
		from resources.lib.extensions import interface

		result = [
			{
				'id' : self.IdBubblesResources,
				'name' : 'Bubbles Resources',
				'type' : self.TypeRequired,
				'description' : 33726,
				'icon' : 'extensionsbubbles.png',
			},
			{
				'id' : self.IdBubblesArtwork,
				'name' : 'Bubbles Artwork',
				'type' : self.TypeRecommended,
				'description' : 33727,
				'icon' : 'extensionsbubbles.png',
			},
			{
				'id' : self.IdBubblesBinaries,
				'name' : 'Bubbles Binaries',
				'type' : self.TypeOptional,
				'description' : 33728,
				'icon' : 'extensionsbubbles.png',
			},
			{
				'id' : self.IdBubblesIcons,
				'name' : 'Bubbles Icons',
				'type' : self.TypeOptional,
				'description' : 33729,
				'icon' : 'extensionsbubbles.png',
			},
			{
				'id' : self.IdBubblesSkins,
				'name' : 'Bubbles Skins',
				'type' : self.TypeOptional,
				'description' : 33730,
				'icon' : 'extensionsbubbles.png',
			},
			{
				'id' : self.IdBubblesAeonNox,
				'name' : 'Bubbles Aeon Nox',
				'type' : self.TypeOptional,
				'description' : 33731,
				'icon' : 'extensionsbubbles.png',
			},
			{
				'id' : self.IdUrlResolver,
				'name' : 'UrlResolver',
				'type' : self.TypeRequired,
				'description' : 33732,
				'icon' : 'extensionsurlresolver.png',
			},
			{
				'id' : self.IdMetaHandler,
				'name' : 'MetaHandler',
				'type' : self.TypeOptional,
				'description' : 33733,
				'icon' : 'extensionsmetahandler.png',
			},
			{
				'id' : self.IdTrakt,
				'name' : 'Trakt',
				'type' : self.TypeRecommended,
				'description' : 33734,
				'icon' : 'extensionstrakt.png',
			},
			{
				'id' : self.IdQuasar,
				'dependencies' : [self.IdQuasarRepository],
				'name' : 'Quasar',
				'type' : self.TypeOptional,
				'description' : 33735,
				'icon' : 'extensionsquasar.png',
			},
		]

		for i in range(len(result)):
			result[i]['installed'] = self.installed(result[i]['id'])
			if 'dependencies' in result[i]:
				for dependency in result[i]['dependencies']:
					if not self.installed(dependency):
						result[i]['installed'] = False
						break
			result[i]['description'] = interface.Translation.string(result[i]['description'])

		return result

	@classmethod
	def dialog(self, id):
		extensions = self.list()
		for extension in extensions:
			if extension['id'] == id:
				from resources.lib.extensions import interface

				type = ''
				if extension['type'] == self.TypeRequired:
					type = 33723
				elif extension['type'] == self.TypeRecommended:
					type = 33724
				elif extension['type'] == self.TypeOptional:
					type = 33725
				if not type == '':
					type = ' (%s)' % interface.Translation.string(type)

				message = ''
				message += interface.Format.fontBold(extension['name'] + type)
				message += interface.Format.newline() + extension['description']

				action = 33737 if extension['installed'] else 33736

				choice = interface.Dialog.option(title = 33391, message = message, labelConfirm = action, labelDeny = 33486)
				if choice:
					if extension['installed']:
						if extension['type'] == self.TypeRequired:
							interface.Dialog.confirm(title = 33391, message = 33738)
						else:
							self.disable(extension['id'], refresh = True)
					else:
						if 'dependencies' in extension:
							for dependency in extension['dependencies']:
								self.enable(dependency, refresh = True)
						self.enable(extension['id'], refresh = True)

				return True
		return False

###################################################################
# QUASAR
###################################################################

class Quasar(object):

	Id = Extensions.IdQuasar
	Name = 'Quasar'

	@classmethod
	def settings(self):
		Extensions.settings(id = self.Id)

	@classmethod
	def launch(self):
		Extensions.launch(id = self.Id)

	@classmethod
	def install(self, confirm = False):
		Extensions.enable(id = Extensions.IdQuasar, refresh = False)
		self.connect(confirm = confirm)
		return True

	@classmethod
	def interface(self):
		host = Settings.getString('streaming.torrent.quasar.host')
		port = Settings.getString('streaming.torrent.quasar.port')
		System.openLink('http://%s:%s/web/' % (host, port))

	@classmethod
	def connected(self):
		return Settings.getBoolean('streaming.torrent.quasar.connected')

	@classmethod
	def connect(self, confirm = False):
		try:
			if not System.installed(self.Id):
				if confirm:
					from resources.lib.extensions import interface
					message = interface.Translation.string(33476) + ' ' + interface.Translation.string(33475)
					if interface.Dialog.option(title = self.Name, message = 33475):
						self.install(confirm = False)
					else:
						raise Exception()
				else:
					raise Exception()
			Settings.set('streaming.torrent.quasar.connected', True)
			Settings.set('streaming.torrent.quasar.connection', 'Connected')
		except:
			self.disconnect()

	@classmethod
	def disconnect(self):
		Settings.set('streaming.torrent.quasar.connected', False)
		Settings.set('streaming.torrent.quasar.connection', 'Disconnected')

###################################################################
# TRAKT
###################################################################

class Trakt(object):

	Id = Extensions.IdTrakt
	Website = 'https://trakt.tv'

	@classmethod
	def settings(self):
		Extensions.settings(id = self.Id)

	@classmethod
	def launch(self):
		Extensions.launch(id = self.Id)

	@classmethod
	def installed(self):
		return Extensions.installed(id = self.Id)

	@classmethod
	def enable(self, refresh = False):
		return Extensions.enable(id = self.Id, refresh = refresh)

	@classmethod
	def disable(self, refresh = False):
		return Extensions.disable(id = self.Id, refresh = refresh)

	@classmethod
	def website(self, open = False):
		if open: System.openLink(self.Website)
		return self.Website

###################################################################
# URLRESOLVER
###################################################################

class UrlResolver(object):

	Id = Extensions.IdUrlResolver

	@classmethod
	def settings(self):
		Extensions.settings(id = self.Id)

	@classmethod
	def installed(self):
		return Extensions.installed(id = self.Id)

	@classmethod
	def enable(self, refresh = False):
		return Extensions.enable(id = self.Id, refresh = refresh)

	@classmethod
	def disable(self, refresh = False):
		return Extensions.disable(id = self.Id, refresh = refresh)

###################################################################
# METAHANDLER
###################################################################

class MetaHandler(object):

	Id = Extensions.IdMetaHandler

	@classmethod
	def settings(self):
		Extensions.settings(id = self.Id)

	@classmethod
	def installed(self):
		return Extensions.installed(id = self.Id)

	@classmethod
	def enable(self, refresh = False):
		return Extensions.enable(id = self.Id, refresh = refresh)

	@classmethod
	def disable(self, refresh = False):
		return Extensions.disable(id = self.Id, refresh = refresh)

###################################################################
# BACKUP
###################################################################

class Backup(object):

	Extension = 'bub'

	TypeAll = 'all'
	TypeSettings = 'settings'
	TypeDatabases = 'databases'

	@classmethod
	def _path(self, clear = False):
		return System.temporary(directory = 'backup', bubbles = True, make = True, clear = clear)

	@classmethod
	def restore(self):
		try:
			from resources.lib.extensions import interface

			choice = interface.Dialog.option(title = 33773, message = 33782)
			if not choice: return False

			path = interface.Dialog.browse(title = 33773, type = interface.Dialog.BrowseFile, mask = self.Extension)
			directory = self._path(clear = True)
			directoryData = System.profile()

			file = zipfile.ZipFile(path, 'r')
			file.extractall(directory)
			file.close()

			directories, files = File.listDirectory(directory)
			counter = 0
			for file in files:
				fileFrom = File.joinPath(directory, file)
				fileTo = File.joinPath(directoryData, file)
				if File.move(fileFrom, fileTo, replace = True):
					counter += 1

			File.deleteDirectory(path = directory, force = True)

			if counter == 0:
				interface.Dialog.confirm(title = 33773, message = 33778)
				return False
			elif counter == len(files):
				interface.Dialog.notification(title = 33773, message = 33785, icon = interface.Dialog.IconSuccess)
				return True
			else:
				message = interface.Translation.string(33783) % System.id()
				interface.Dialog.confirm(title = 33773, message = message)
				return False
		except:
			Logger.error()
			interface.Dialog.confirm(title = 33773, message = 33778)
			return False

	@classmethod
	def create(self, type):
		try:
			from resources.lib.extensions import convert
			from resources.lib.extensions import interface

			message = ''
			if type == self.TypeAll: message = 33781
			elif type == self.TypeSettings: message = 33779
			elif type == self.TypeDatabases: message = 33780
			choice = interface.Dialog.option(title = 33773, message = message)
			if not choice: return False

			path = interface.Dialog.browse(title = 33773, type = interface.Dialog.BrowseDirectoryWrite)
			date = convert.ConverterTime(Time.timestamp(), convert.ConverterTime.FormatTimestamp).string(convert.ConverterTime.FormatDate)
			path = File.joinPath(path, 'Bubbles Backup ' + date + ' ')

			counter = 0
			suffix = ''
			while File.exists(path + suffix + '.' + self.Extension):
				counter += 1
				suffix = '[%d]' % counter

			path = path + suffix + '.' + self.Extension
			file = zipfile.ZipFile(path, 'w')

			content = []
			directory = self._path(clear = True)
			directoryData = System.profile()
			directories, files = File.listDirectory(directoryData)

			if type == self.TypeAll:
				content = files
			elif type == self.TypeSettings:
				settings = 'settings.xml'
				for i in range(len(files)):
					if files[i].lower() == settings:
						content.append(files[i])
						break
			elif type == self.TypeDatabases:
				extension = '.db'
				for i in range(len(files)):
					if files[i].lower().endswith(extension):
						content.append(files[i])

			tos = [File.joinPath(directory, i) for i in content]
			froms = [File.joinPath(directoryData, i) for i in content]

			for i in range(len(content)):
				try:
					File.copy(froms[i], tos[i], overwrite = True)
					file.write(tos[i], content[i])
				except: pass

			file.close()
			File.deleteDirectory(path = directory, force = True)

			interface.Dialog.notification(title = 33773, message = 33784, icon = interface.Dialog.IconSuccess)
			return True
		except:
			Logger.error()
			interface.Dialog.confirm(title = 33773, message = 33777)
			return False

	@classmethod
	def createAll(self):
		return self.create(self.TypeAll)

	@classmethod
	def createSettings(self):
		return self.create(self.TypeSettings)

	@classmethod
	def createDatabases(self):
		return self.create(self.TypeDatabases)

###################################################################
# DONATIONS
###################################################################

class Donations(object):

	# Currency
	CurrencyNone = None
	CurrencyAugur = 'augur'
	CurrencyBitcoin = 'bitcoin'
	CurrencyDash = 'dash'
	CurrencyDogecoin = 'dogecoin'
	CurrencyEthereum = 'ethereum'
	CurrencyGolem = 'golem'
	CurrencyLitecoin = 'litecoin'

	# Popup
	PopupThreshold = 30

	@classmethod
	def show(self, currency):
		from resources.lib.extensions import interface
		return interface.Splash.popupDonations(currency = currency)

	@classmethod
	def coinbase(self, openLink = True):
		link = Settings.getString('link.coinbase')
		if openLink: System.openLink(link)
		return link

	@classmethod
	def exodus(self, openLink = True):
		link = Settings.getString('link.exodus')
		if openLink: System.openLink(link)
		return link

	@classmethod
	def show(self):
		System.window(action = 'donationsNavigator')

	@classmethod
	def popup(self):
		from resources.lib.extensions import interface
		counter = Settings.getInteger('internal.donation')
		counter += 1
		if counter >= self.PopupThreshold:
			Settings.set('internal.donation', 0)
			if not interface.Dialog.option(title = 33505, message = 35014, labelConfirm = 35015, labelDeny = 33505):
				self.show()
				return True
		else:
			Settings.set('internal.donation', counter)
		return False
