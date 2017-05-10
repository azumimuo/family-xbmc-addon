import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string, sys, os
import commonresolvers
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from htmlentitydefs import name2codepoint as n2cp
import HTMLParser
 
try:
        from sqlite3 import dbapi2 as sqlite
        print "Loading sqlite3 as DB engine"
except:
        from pysqlite2 import dbapi2 as sqlite
        print "Loading pysqlite2 as DB engine"
 
 
addon_id = 'plugin.video.dfmalaystream'
plugin = xbmcaddon.Addon(id=addon_id)
#DB = os.path.join(xbmc.translatePath("special://database"), 'dfv.db')
BASE_URL = 'http://selangit.org/master/sg1'
net = Net()
addon = Addon('plugin.video.dfmalaystream', sys.argv)
 
###### PATHS ###########
AddonPath = addon.get_path()
IconPath = AddonPath + "/icons/"
FanartPath = AddonPath + "/icons/"
 
##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
content = addon.queries.get('content', None)
query = addon.queries.get('query', None)
startPage = addon.queries.get('startPage', None)
numOfPages = addon.queries.get('numOfPages', None)
listitem = addon.queries.get('listitem', None)
urlList = addon.queries.get('urlList', None)
section = addon.queries.get('section', None)
 
################################################################################# Titles #################################################################################
 
def GetTitles(section, url, startPage= '1', numOfPages= '1'):
        print 'Proses penyenaraian tajuk cerita %s' % url
        pageUrl = url
        searchurl = url.split("?")
        searchurl = searchurl[0]
        match = re.search('acgtube', url)
        if match:
           searchurl =  BASE_URL + '/acgtube/search/'
        if int(startPage)> 1:
                pageUrl = url + '?page=' + startPage
        print pageUrl
        html = net.http_GET(pageUrl).content.encode('utf-8')
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + 'page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content.encode('utf-8')
                match = re.compile('<h2.+?href="(.+?)".+?>(.+?)<.+?src="(.+?)"', re.DOTALL).findall(html)
                addon.add_directory({'mode': 'GetSearchQuery', 'url': searchurl},  {'title':  '[COLOR yellow]Malay Video Online[/COLOR]'}, img=IconPath + 'search.png', fanart=FanartPath + 'fanart.png')
                for movieUrl, name, img in match:
                        addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': movieUrl}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png')
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': '[COLOR blue][B][I]Next page...[/B][/I][/COLOR]'}, img=IconPath + 'next.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
       
################################################################################# SingleLink #################################################################################
 
def GetSingleLink(section, url, startPage= '1', numOfPages= '1'):
        print 'Proses penyenaraian tajuk cerita %s' % url
        pageUrl = url
        searchurl = url.split("?")
        searchurl = searchurl[0]
        match = re.search('acgtube', url)
        if match:
           searchurl =  BASE_URL + '/acgtube/search/'
        if int(startPage)> 1:
                pageUrl = url + '?page=' + startPage
        print pageUrl
        html = net.http_GET(pageUrl).content.encode('utf-8')
        listitem = GetMediaInfo(html)
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + 'page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content.encode('utf-8')
                match = re.compile('<h2.+?href="(.+?)".+?>(.+?)<.+?src="(.+?)"', re.DOTALL).findall(html)
                addon.add_directory({'mode': 'GetSearchQuery', 'url': searchurl},  {'title':  '[COLOR yellow]Malay Video Online[/COLOR]'}, img=IconPath + 'search.png', fanart=FanartPath + 'fanart.png')
                for movieUrl, name, img in match:
                        #addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': movieUrl}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png')
                        addon.add_directory({'mode': 'PlayVideo', 'url': movieUrl, 'listitem': listitem}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png')
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': '[COLOR blue][B][I]Next page...[/B][/I][/COLOR]'}, img=IconPath + 'next.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))      
       
################################################################################# Episode #################################################################################
 
def GetEpisode(section, url, startPage= '1', numOfPages= '1'):
        print 'Proses penyenaraian tajuk cerita %s' % url
        pageUrl = url
        if int(startPage)> 1:
                pageUrl = url + '?page=' + startPage
        print pageUrl
        searchurl = url.split("?")
        html = net.http_GET(pageUrl).content.encode('utf-8')
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + 'page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content.encode('utf-8')
                match = re.compile('<h2.+?href="(.+?)".+?>(.+?)<.+?src="(.+?)"', re.DOTALL).findall(html)
                addon.add_directory({'mode': 'GetSearchQuery', 'url': searchurl[0]},  {'title':  '[COLOR yellow]Malay Video Online[/COLOR]'}, img=IconPath + 'search.png', fanart=FanartPath + 'fanart.png')
                for movieUrl, name, img in match:
                        addon.add_directory({'mode': 'GetEpisodelinks', 'section': section, 'url': movieUrl}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png')
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': '[COLOR blue][B][I]Next page...[/B][/I][/COLOR]'}, img=IconPath + 'next.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
       
############################################################################### Get Episodelinks #############################################################################
 
def GetEpisodelinks(section, url):
        print 'GETLINKS FROM URL: '+url
        html = net.http_GET(url).content.encode('utf-8')
        listitem = GetMediaInfo(html)
        content = html
        match = re.compile('<.+?href="(.+?)".+?>(.+?)<').findall(content)
        listitem = GetMediaInfo(content)
        for url, name in match:
                r = re.search('link=', content)
                if r: addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': url}, {'title':  name.strip()}, fanart=FanartPath + 'fanart.png')
                else:
                       host = GetDomain(url)
                       #if urlresolver.HostedMediaFile(url= url):
                       addon.add_directory({'mode': 'PlayVideo', 'url': url, 'listitem': listitem}, {'title':  host }, img=IconPath + 'play.png', fanart=FanartPath + 'fanart.png')
       
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
############################################################################### Get links ###################################################################################
 
 
def GetLinks(section, url):
        print 'GETLINKS FROM URL: '+url
        html = net.http_GET(url).content.encode('utf-8')
        listitem = GetMediaInfo(html)
        content = html
        match = re.compile('href="(.+?)"').findall(content)
        listitem = GetMediaInfo(content)
        for url in match:
                host = GetDomain(url)
                #if urlresolver.HostedMediaFile(url= url):
                addon.add_directory({'mode': 'PlayVideo', 'url': url, 'listitem': listitem}, {'title':  host }, img=IconPath + 'play.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
############################################################################# Play Video #####################################################################################
 
def PlayVideo(url, listitem):
    try:
        print 'in PlayVideo %s' % url
        if (urlresolver.HostedMediaFile(url)):
           stream_url = urlresolver.HostedMediaFile(url).resolve()
        else:
           stream_url = url
        #stream_url = commonresolvers.get(url).result
        xbmc.Player().play(stream_url)
        addon.add_directory({'mode': 'help'}, {'title':  '[COLOR slategray][B]^^^ Press back ^^^[/B] [/COLOR]'},'','')
    except:
        xbmc.executebuiltin("XBMC.Notification([COLOR red][B]Maaf link dipilih offline ![/B][/COLOR],[COLOR lime][B]Sila pilih lain link/host !![/B][/COLOR],7000,"")")
 
 
def GetDomain(url):
        tmp = re.compile('//(.+?)/').findall(url)
        domain = 'Unknown'
        if len(tmp) > 0 :
            domain = tmp[0].replace('www.', '')
        return domain
 
def GetMediaInfo(html):
        listitem = xbmcgui.ListItem()
        match = re.search('og:title" content="(.+?) \((.+?)\)', html)
        if match:
                print match.group(1) + ' : '  + match.group(2)
                listitem.setInfo('video', {'Title': match.group(1), 'Year': int(match.group(2)) } )
        return listitem
 
###################################################################### menus ####################################################################################################
 
def MainMenu():    #homescreen
    addon.add_directory({'mode': 'AcgMenu'}, {'title':  '[COLOR red]DRAMA/TELEMOVIE[/COLOR]'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
    addon.add_directory({'mode': 'Dfm2uMenu'}, {'title':  '[COLOR blue]MALAY-MVO[/COLOR]'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
    addon.add_directory({'mode': 'EnglishMenu'}, {'title':  '[COLOR yellow]ENGLISH-MVO[/COLOR]'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')
    addon.add_directory({'mode': 'HindustanMenu'}, {'title':  '[COLOR green]HINDUSTAN-MVO[/COLOR]'}, img=IconPath + 'movie.png', fanart=FanartPath + 'movie.png')
    addon.add_directory({'mode': 'ThailandMenu'}, {'title':  '[COLOR green]THAILAND-MVO[/COLOR]'}, img=IconPath + 'movie.png', fanart=FanartPath + 'movie.png')
    addon.add_directory({'mode': 'RilekTvMenu'}, {'title':  '[COLOR yellow]RilekTV-MVO[/COLOR]'}, img=IconPath + 'movie.png', fanart=FanartPath + 'movie.png')
        #addon.add_directory({'mode': 'ResolverSettings'}, {'title':  '[COLOR red]Resolver Settings[/COLOR]'}, img=IconPath + 'resolver.png', fanart=FanartPath + 'fanart.png')      
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
       
def AcgMenu():    #G
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/acgtube/drama/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'EXTRA Drama'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/acgtube/Telemovie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'EXTRA Telemovie'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/acgtube/tvshow/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'TV Show'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')                    
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
 
def Dfm2uMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/movie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Movies Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/telemovie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Telemovie Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/drama/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Drama Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/tvshow/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'TV Show Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/klasik/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Klasik Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/indonesia/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Indonesia Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')                  
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def EnglishMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/English/movie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'English HD Mvo'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/English/new/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'English New Release'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/English/featured/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'English Featured'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/English/popular/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'English Popular Today'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/English/kid/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Kids Animations'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')                    
        xbmcplugin.endOfDirectory(int(sys.argv[1]))    
 
def HindustanMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/ind/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Hindustan Mvo'}, img=IconPath + 'hindi.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
       
def ThailandMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/thai/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Thailand Mvo'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')                  
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def RilekTvMenu():
        addon.add_directory({'mode': 'GetSingleLink', 'section': 'ALL', 'url': BASE_URL + '/rilektv/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Rileks Tv Mvo'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')                  
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        
       
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#
 
def GetSearchQuery(url):
    url = url + '?cariler='
    #last_search = addon.load_data('search')
    #if not last_search: last_search = ''
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('[COLOR yellow]Malay Video Online[/COLOR]')
    #keyboard.setDefault(last_search)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
                query = keyboard.getText()
                addon.save_data('search',query)
                url = url + query
                GetTitles(section, url, startPage= '1', numOfPages= '1')
                #Search(query,url)
    else:
                return  
def Search(query,url):
        url = url + query
        url = url.replace(' ', '+')
        print url
        html = net.http_GET(url).content.encode('utf-8')
        match = re.compile('<h3 class="r"><a href="(.+?)".+?onmousedown=".+?">(.+?)</a>').findall(html)
        for url, title in match:
                title = title.replace('<b>...</b>', '').replace('<em>', '').replace('</em>', '')
                addon.add_directory({'mode': 'GetLinks', 'url': url}, {'title':  title})
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
 
#################################################################################################################################################################################
 
if mode == 'main':
        MainMenu()
elif mode == 'AcgMenu':
    AcgMenu()
elif mode == 'EnglishMenu':
    EnglishMenu()
elif mode == 'HindustanMenu':
    HindustanMenu()
elif mode == 'ThailandMenu':
    ThailandMenu()    
elif mode == 'Dfm2uMenu':
    Dfm2uMenu()
elif mode == 'RilekTvMenu':
    RilekTvMenu()  
elif mode == 'GetTitles':
        GetTitles(section, url, startPage, numOfPages)
elif mode == 'GetSingleLink':
        GetSingleLink(section, url, startPage, numOfPages)
elif mode == 'GetEpisode':
        GetEpisode(section, url, startPage, numOfPages)
elif mode == 'GetEpisodelinks':
        GetEpisodelinks(section, url)        
elif mode == 'GetLinks':
        GetLinks(section, url)
elif mode == 'GetSearchQuery':
        GetSearchQuery(url)
elif mode == 'Search':
        Search(query,url)
elif mode == 'PlayVideo':
        PlayVideo(url, listitem)          
#elif mode == 'ResolverSettings':
        #urlresolver.display_settings()
xbmcplugin.endOfDirectory(int(sys.argv[1]))