#$pyFunction
def GetLSProData(page_data, Cookie_Jar, m):
	import requests
	import re

	session = requests.session()

	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0 FirePHP/0.7.4",
			   "Referer": "http://www.tonton.com.my/login",
			   "Connection": "keep-alive"}

	r = session.get('http://www.tonton.com.my/vindicia/playerOTP?id=J3ZmNmeDpV1EMWlR6YJU_YDCqKbh_bSg&account_id=067dcc18-d9ad-0904-95e4-4d7e8d63cb4c', headers=headers)
	token = re.findall(r'"token":"(.*?)"', r.text)[0].replace('\/', '/')

	r = session.get(token, headers=headers)

	headers = {'Referer': 'http://player.ooyala.com/static/cacheable/a749e376b1fadc6784b96bd76a37692d/player_v2.swf?player=dde0012b6dcc4dc7b26306bdaff0dce2',
			   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0 FirePHP/0.7.4'}
	r = session.get('http://player.ooyala.com/sas/akamai_edge_auth_token?embed_code=J3ZmNmeDpV1EMWlR6YJU_YDCqKbh_bSg&video_pcode=owMjgyOkSbJagb4ozVY_03UrHYLt', headers=headers)
	return r.text+'&hdcore=2.10.3&g=SWEQGAKKWKPS'
