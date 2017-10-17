# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string, sys, os, json
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
import HTMLParser
net = Net()


###### Hwid ###########
def Gethwid():
        while True:
           hwid = xbmc.getInfoLabel("network.macaddress")
           if hwid not in ('Busy','Sibuk'):
             break
        return hwid
        
###### Ipid ###########
def Getipid():
        ipid = xbmc.getInfoLabel("Network.IPAddress")
        return ipid        

###### Postdata ###########
def postdata():
        hwid = Gethwid()
        ipid = Getipid()
        if hwid == '00:00:00:00:00:00':
           hwid = ipid.replace('.', ':')
        parameters = {"hwid" : hwid,"ipid" : ipid}
        postid = '?' + urllib.urlencode(parameters)
        return postid

###### AUTHORIZE ###########
def paircheck():
        url =  'http://selangit.org/master/sg1/paircheck.php' + postdata()
        dialog = xbmcgui.Dialog()
        result = net.http_GET(url).content
        js_result = json.loads(result)
        pairurl = js_result['pairurl']
        header = js_result['header']
        line1 = js_result['line1']
        line2 = js_result['line2']
        line3 = js_result['line3']
        if js_result['status'] == 'unauthorize':
            alert = dialog.yesno(header,line1,line2,line3,'I Will Open This Link Later','Please Open This Link For Me')
            if alert:
               openbrowser(pairurl)
        elif header:
            alert = dialog.ok(header, line1, line2, line3)
            return alert

###### Auto Open Browser ###########
def openbrowser(url):
     osWin = xbmc.getCondVisibility('system.platform.windows')
     osOsx = xbmc.getCondVisibility('system.platform.osx')
     osLinux = xbmc.getCondVisibility('system.platform.linux')
     osAndroid = xbmc.getCondVisibility('System.Platform.Android')

     if osOsx:
          xbmc.executebuiltin("System.Exec(open "+url+")")
     elif osWin:
          xbmc.executebuiltin("System.Exec(cmd.exe /c start "+url+")")
     elif osLinux and not osAndroid:
          xbmc.executebuiltin("System.Exec(xdg-open "+url+")")
     elif osAndroid:
          xbmc.executebuiltin("StartAndroidActivity(com.android.browser,android.intent.action.VIEW,,"+url+")")
          xbmc.executebuiltin("StartAndroidActivity(org.mozilla.firefox,android.intent.action.VIEW,,"+url+")")
          xbmc.executebuiltin("StartAndroidActivity(com.android.chrome,,,"+url+")")

###### Progress Bar Dialog ###########
def PERCENT():
    dp = xbmcgui.DialogProgress()
    dp.create('Head','Body','gddgdg','ddgdgdgdg')
    dp.update(10)
    xbmc.sleep(1000)
    dp.update(20)
    xbmc.sleep(1000)
    dp.update(30)
    xbmc.sleep(1000)
    dp.update(40)
    xbmc.sleep(1000)
    dp.update(50)
    xbmc.sleep(1000)
    dp.update(60)
    xbmc.sleep(1000)
    dp.update(70)
    xbmc.sleep(1000)
    dp.update(80)
    xbmc.sleep(1000)
    dp.update(90)
    xbmc.sleep(1000)
    dp.update(100)
    dp.close()