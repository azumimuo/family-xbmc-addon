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

# No Bubbles imports, because it does not work during script execution of downloader.py.

import os
import xbmc
import xbmcgui
import xbmcaddon
import threading

try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

DatabaseLocks = {}
DatabaseLocksCustom = {}

class Database(object):

	Timeout = 20

	def __init__(self, name, addon = None, connect = True):
		try:
			global DatabaseLocks
			if not name in DatabaseLocks:
				DatabaseLocks[name] = threading.Lock()
			self.mLock = DatabaseLocks[name]

			global DatabaseLocksCustom
			if not name in DatabaseLocksCustom:
				DatabaseLocksCustom[name] = threading.Lock()
			self.mLockCustom = DatabaseLocksCustom[name]

			self.mAddon = addon
			if not name.endswith('.db'):
				name += '.db'
			self.mPath = os.path.join(xbmc.translatePath(self._addon().getAddonInfo('profile').decode('utf-8')), name)
			if connect: self._connect()
		except:
			pass

	def __del__(self):
		self._close()

	def _lock(self):
		self.mLockCustom.acquire()

	def _unlock(self):
		if not self.mLockCustom.locked():
			self.mLockCustom.release()

	def _connect(self):
		try:
			# SQLite does not allow database objects to be used from multiple threads. Explicitly allow multi threading.
			try: self.mConnection = database.connect(self.mPath, check_same_thread = False, timeout = self.Timeout)
			except: self.mConnection = database.connect(self.mPath, timeout = self.Timeout)

			self.mDatabase = self.mConnection.cursor()
			self._initialize()
			return True
		except:
			return False

	def _addon(self):
		if self.mAddon:
			return xbmcaddon.Addon(self.mAddon)
		else:
			return xbmcaddon.Addon()

	def _initialize(self):
		pass

	def _list(self, items):
		if not type(items) in [list, tuple]:
			items = [items]
		return items

	def _close(self):
		try: self.mConnection.close()
		except: pass

	def _null(self):
		return 'NULL'

	def _commit(self):
		try:
			self.mConnection.commit()
			return True
		except:
			return False

	def _execute(self, query):
		try:
			self.mLock.acquire()
			self.mDatabase.execute(query)
			return True
		except Exception as error:
			xbmc.log('BUBBLES ERROR [Database]: ' + str(error), xbmc.LOGERROR)
			return False
		finally:
			self.mLock.release()

	# query must contain %s for table name.
	# tables can be None, table name, or list of tables names.
	# If tables is None, will retrieve all tables in the database.
	def _executeAll(self, query, tables = None):
		result = True
		if tables == None:
			tables = self._tables()
		tables = self._list(tables)
		for table in tables:
			result = result and self._execute(query % table)
		return result

	def _tables(self):
		return self._selectValues('SELECT name FROM sqlite_master WHERE type IS "table"')

	def _create(self, query, commit = True):
		result = self._execute(query)
		if result and commit:
			result = self._commit()
		return result

	def _createAll(self, query, tables, commit = True):
		result = self._executeAll(query, tables)
		if result and commit:
			result = self._commit()
		return result

	# Retrieves a list of rows.
	# Each row is a tuple with all the return values.
	# Eg: [(row1value1, row1value2), (row2value1, row2value2)]
	def _select(self, query):
		self._execute(query)
		return self.mDatabase.fetchall()

	# Retrieves a single row.
	# Each row is a tuple with all the return values.
	# Eg: (row1value1, row1value2)
	def _selectSingle(self, query):
		self._execute(query)
		return self.mDatabase.fetchone()

	# Retrieves a list of single values from rows.
	# Eg: [row1value1, row1value2]
	def _selectValues(self, query):
		try:
			result = self._select(query)
			return [i[0] for i in result]
		except:
			return []

	# Retrieves a signle value from a single row.
	# Eg: row1value1
	def _selectValue(self, query):
		try:
			return self._selectSingle(query)[0]
		except:
			return None

	# Checks if the value exists, such as an ID.
	def _exists(self, query):
		return len(self._select(query)) > 0

	def _insert(self, query, commit = True):
		result = self._execute(query)
		if result and commit:
			result = self._commit()
		return result

	def _update(self, query, commit = True):
		result = self._execute(query)
		if result and commit:
			result = self._commit()
		return result

	# Deletes specific row in table.
	# If table is none, assumes it was already set in the query
	def _delete(self, query, table = None, commit = True):
		if not table == None:
			query = query % table
		result = self._execute(query)
		if result and commit:
			result = self._commit()
		return result

	# Deletes all rows in table.
	# tables can be None, table name, or list of tables names.
	# If tables is None, deletes all rows in all tables.
	def _deleteAll(self, tables = None, commit = True):
		result = self._executeAll('DELETE FROM %s;', tables)
		if result and commit:
			result = self._commit()
		return result

	# Drops single table.
	def _drop(self, table, commit = True):
		result = self._execute('DROP TABLE IF EXISTS %s;' % table)
		if result and commit:
			result = self._commit()
		return result

	# DRops all tables.
	def _dropAll(self, commit = True):
		result = self._executeAll('DROP TABLE IF EXISTS %s;')
		if result and commit:
			result = self._commit()
		return result

	# tables can be None, table name, or list of tables names.
	# If tables is provided, only clears the specific table(s), otherwise clears all tables.
	def clear(self, tables = None, confirm = False):
		title = self._addon().getAddonInfo('name') + ' - ' + self._addon().getLocalizedString(33013).encode('utf-8')
		message = self._addon().getLocalizedString(33042).encode('utf-8')
		if not confirm or xbmcgui.Dialog().yesno(title, message):
			self._deleteAll(tables)
			if confirm:
				message = self._addon().getLocalizedString(33043).encode('utf-8')
				icon = xbmc.translatePath(xbmcaddon.Addon('script.bubbles.resources').getAddonInfo('path').decode('utf-8'))
				icon = os.path.join(icon, 'resources', 'media', 'notifications', 'information.png')
				xbmcgui.Dialog().notification(title, message, icon = icon)
