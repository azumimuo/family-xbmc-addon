import os, sys, time
import xbmc, xbmcgui, xbmcaddon

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id').decode( 'utf-8' )
__addonname__    = __addon__.getAddonInfo('name').decode("utf-8")

class MyMonitor(xbmc.Monitor):
    def __init__(self, settings_callback):
        self.settings_callback = settings_callback
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        self.settings_callback()

class Main(object):
    pin = 0
    edge = 0
    silent = 'false'
    function = ''

    def __init__(self):
        pass

    def start(self):
        monitor = MyMonitor(self.on_settings_changed)
        self.setup()
        monitor.waitForAbort()
        self.cleanup()

    def cleanup(self):
        try:GPIO.remove_event_detect(self.pin)
        except: pass
        try: GPIO.cleanup()
        except: pass

    def on_settings_changed(self):
        self.cleanup()
        self.setup()

    def pin_callback(self, pin):
        if self.silent == 'false':
            dialog = xbmcgui.Dialog()
            dialog.notification(__addonname__, 'Executing %s' % self.function, xbmcgui.NOTIFICATION_INFO, 2000)
        time.sleep(0.5)
        xbmc.executebuiltin(self.function)

    def setup(self):
        settings = xbmcaddon.Addon()

        self.pin = int(settings.getSetting("pin"))
        self.edge = int(settings.getSetting("edge"))
        self.function = settings.getSetting("function").strip()
        self.silent = settings.getSetting("silent").strip()

        if self.pin == 0:
            return

        try:
            GPIO.setmode(GPIO.BOARD)

            if self.edge == 1:
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.pin_callback)
            else:
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.pin_callback)
        except:
            dialog = xbmcgui.Dialog()
            dialog.notification(__addonname__, 'Error setting up pin: %s' % self.pin, xbmcgui.NOTIFICATION_ERROR, 2000)


def osmc_install_gpio():
    dialog  = xbmcgui.DialogProgress()

    dialog.create(__addonname__,'Fixing GPIO Permissions')

    os.system('sudo groupadd -f -r gpio')
    os.system('sudo adduser osmc gpio')
    os.system('sudo adduser root gpio')
    with open('/home/osmc/udev.temp','w') as f:
        f.write("""SUBSYSTEM=="bcm2835-gpiomem", KERNEL=="gpiomem", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
""")
    os.system('sudo mv /home/osmc/udev.temp /etc/udev/rules.d/99-gpio.rules')

    dialog.update(10, 'Updating package cache..')
    os.system('sudo dpkg --configure -a')
    os.system('sudo apt-get update')

    dialog.update(25, 'Installing required build packages..')
    os.system('sudo apt-get install --reinstall -y python-pip python-dev gcc')

    dialog.update(50, 'Installing RPi.GPIO..')
    os.system('sudo pip install --force-reinstall rpi.gpio')

    dialog.update(75, 'Cleaning Up..')
    os.system('sudo apt-get remove -y python-pip python-dev gcc')
    os.system('sudo apt-get -y autoremove')

    dialog.update(100, 'Install Complete. Rebooting...')
    time.sleep(1)
    xbmc.executebuiltin('Reboot')
    sys.exit(0)

if __name__ == '__main__':
    uname  = ' '.join(os.uname()).lower()
    dialog = xbmcgui.Dialog()

    if 'libreelec' in uname:        
        def check_rpi_tools():
            try:
                rpi_tools = xbmcaddon.Addon('virtual.rpi-tools')
                sys.path.append(os.path.join(rpi_tools.getAddonInfo('path').decode("utf-8"), 'lib'))
                return True
            except:
                return False

        if not check_rpi_tools():
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{"addonid":"virtual.rpi-tools","enabled":true}}')
            xbmc.executebuiltin('InstallAddon(virtual.rpi-tools)', True)
            if not check_rpi_tools():
                dialog.ok(__addonname__, "This add-on requires the 'Raspberry Pi Tools' add-on")
                sys.exit(0)

        try:
            import RPi.GPIO as GPIO
        except:
            dialog.ok(__addonname__, "Could not import the RPi.GPIO library", "Try re-installing the 'Raspberry Pi Tools' add-on")

    elif 'osmc' in uname:
        try:
            import RPi.GPIO as GPIO
        except:
            if dialog.yesno(__addonname__, "The RPi.GPIO Python library is required.", "This will take about 2 to 5 minutes to build and install.", "Build & Install now?"):
                osmc_install_gpio()
            else:
                sys.exit(0)
    else:
        dialog.ok(__addonname__, "This add-on is only compatible with LibreELEC & OSMC on the Raspberry Pi")
        sys.exit(0)

    main = Main()
    main.start()