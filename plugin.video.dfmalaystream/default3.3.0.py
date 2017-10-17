import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string, sys, os, json
import commonresolvers
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from htmlentitydefs import name2codepoint as n2cp
from resources import df
import HTMLParser
       
try:
        from sqlite3 import dbapi2 as sqlite
        print "Loading sqlite3 as DB engine"
except:
        from pysqlite2 import dbapi2 as sqlite
        print "Loading pysqlite2 as DB engine"
 
 
addon_id = 'plugin.video.dfmalaystream'
plugin = xbmcaddon.Addon(id=addon_id)
BASE_URL = 'http://selangit.org/master/sg1'
net = Net()
addon = Addon('plugin.video.dfmalaystream', sys.argv)
dialog = xbmcgui.Dialog()
postdata = df.postdata()
 
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
                pageUrl = url + '&page=' + startPage
        print pageUrl
        html = net.http_GET(pageUrl).content.encode('utf-8')
        checkauthorize = re.search('MVO AUTHORIZATION', html)
        if checkauthorize:
           df.paircheck()
           return
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + 'page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content.encode('utf-8')
                match = re.compile('href=\"(.+?)\"\stitle=\"(.+?)\".+?target.+?\"><img src="(.+?)"', re.DOTALL).findall(html)
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
                pageUrl = url + '&page=' + startPage
        print pageUrl
        html = net.http_GET(pageUrl).content.encode('utf-8')
        checkauthorize = re.search('MVO AUTHORIZATION', html)
        if checkauthorize:
           df.paircheck()
           return
        listitem = GetMediaInfo(html)
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + 'page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content.encode('utf-8')
                match = re.compile('href=\"(.+?)\"\stitle=\"(.+?)\".+?target.+?\"><img src="(.+?)"', re.DOTALL).findall(html)
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
                pageUrl = url + '&page=' + startPage
        print pageUrl
        searchurl = url.split("?")
        html = net.http_GET(pageUrl).content.encode('utf-8')
        checkauthorize = re.search('MVO AUTHORIZATION', html)
        if checkauthorize:
           df.paircheck()
           return
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
        checkauthorize = re.search('MVO AUTHORIZATION', html)
        if checkauthorize:
           df.paircheck()
           return
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
        checkauthorize = re.search('MVO AUTHORIZATION', html)
        if checkauthorize:
           df.paircheck()
           return
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
    addon.add_directory({'mode': 'KoreaMenu'}, {'title':  '[COLOR green]KOREA-MVO[/COLOR]'}, img=IconPath + 'korea.png', fanart=FanartPath + 'korea.png')
    addon.add_directory({'mode': 'AnimeMenu'}, {'title':  '[COLOR green]ANIME-MVO[/COLOR]'}, img=IconPath + 'anime.png', fanart=FanartPath + 'anime.png')
    addon.add_directory({'mode': 'AnimationMenu'}, {'title':  '[COLOR green]ANIMATION-MVO[/COLOR]'}, img=IconPath + 'animation.png', fanart=FanartPath + 'animation.png')
    addon.add_directory({'mode': 'ChineseMenu'}, {'title':  '[COLOR green]CHINESE-MVO[/COLOR]'}, img=IconPath + 'chinese.png', fanart=FanartPath + 'chinese.png')
    addon.add_directory({'mode': 'ThailandMenu'}, {'title':  '[COLOR green]THAILAND-MVO[/COLOR]'}, img=IconPath + 'movie.png', fanart=FanartPath + 'movie.png')
    addon.add_directory({'mode': 'MelayuFilemMenu'}, {'title':  '[COLOR yellow]MelayuFilem-MVO[/COLOR]'}, img=IconPath + 'movie.png', fanart=FanartPath + 'movie.png')
    addon.add_directory({'mode': 'ComingSoonMenu'}, {'title':  '[COLOR yellow]Coming Soon[/COLOR]'}, img=IconPath + 'cs.png', fanart=FanartPath + 'cs.png')
    addon.add_directory({'mode': 'RequestMenu'}, {'title':  '[COLOR yellow]Request-MVO[/COLOR]'}, img=IconPath + 'request.png', fanart=FanartPath + 'request.png') 
        #addon.add_directory({'mode': 'ResolverSettings'}, {'title':  '[COLOR red]Resolver Settings[/COLOR]'}, img=IconPath + 'resolver.png', fanart=FanartPath + 'fanart.png')      
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    df.paircheck()
       
def AcgMenu():    #G
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/acgtube/drama/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'EXTRA Drama'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/acgtube/Telemovie/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'EXTRA Telemovie'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/acgtube/tvshow/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'TV Show'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')                    
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
 
def Dfm2uMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/movie/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Movies Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/telemovie/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Telemovie Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/drama/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Drama Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/tvshow/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'TV Show Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/klasik/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Klasik Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/indonesia/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Indonesia Mvo'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')                  
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def EnglishMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/English/movie/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'English Mvo'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def HindustanMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/ind/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Hindustan Mvo'}, img=IconPath + 'hindi.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def KoreaMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/korea/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Korea Mvo'}, img=IconPath + 'korea.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def AnimeMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/anime/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Anime Mvo'}, img=IconPath + 'anime.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def AnimationMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/animation/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Animation Mvo'}, img=IconPath + 'animation.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def RequestMenu():
        addon.add_directory({'mode': 'GetSingleLink', 'section': 'ALL', 'url': BASE_URL + '/request/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Request Mvo'}, img=IconPath + 'request.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def ChineseMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/chinese/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Chinese Mvo'}, img=IconPath + 'chinese.png', fanart=FanartPath + 'fanart.png')      
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def ThailandMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/thai/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Thailand Mvo'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')                  
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
def MelayuFilemMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': 'http://selangit.org/master/sg1/cilok/' + postdata,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Melayu Filem Mvo'}, img=IconPath + 'eng.png', fanart=FanartPath + 'fanart.png')                  
        xbmcplugin.endOfDirectory(int(sys.argv[1]))  
 
def ComingSoonMenu():
       
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
elif mode == 'KoreaMenu':
    KoreaMenu()
elif mode == 'ChineseMenu':
    ChineseMenu()
elif mode == 'AnimeMenu':
    AnimeMenu()
elif mode == 'AnimationMenu':
    AnimationMenu()
elif mode == 'RequestMenu':
    RequestMenu()
elif mode == 'ThailandMenu':
    ThailandMenu()    
elif mode == 'Dfm2uMenu':
    Dfm2uMenu()
elif mode == 'MelayuFilemMenu':
    MelayuFilemMenu()
elif mode == 'ComingSoonMenu':
    ComingSoonMenu()   
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