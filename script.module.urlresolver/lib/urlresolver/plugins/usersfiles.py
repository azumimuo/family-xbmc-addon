# -*- coding: UTF-8 -*-
"""
    Copyright (C) 2015  tknorris

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
"""

import re
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class UsersFilesResolver(UrlResolver):
    name = "UsersFiles"
    domains = ["usersfiles.com"]
    pattern = '(?://|\.)(usersfiles\.com)/(?:embed-)?([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()
        self.net.set_user_agent(common.IE_USER_AGENT)
        self.headers = {'User-Agent': common.IE_USER_AGENT}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        match = re.search('<script[^>]*>(eval.*?)</script>', html, re.DOTALL)
        if match:
            js_data = jsunpack.unpack(match.group(1))

            stream_url = re.findall('<param\s+name="src"\s*value="([^"]+)', js_data)
            stream_url += re.findall('file\s*:\s*[\'|\"](.+?)[\'|\"]', js_data)
            stream_url = [i for i in stream_url if not i.endswith('.srt')]

            if stream_url:
                return stream_url[0]

        raise ResolverError('Unable to find userfiles video')

    def get_url(self, host, media_id):
        return 'http://usersfiles.com/%s' % media_id
