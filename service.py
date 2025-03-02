import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
from datetime import datetime, date
import sys
import os
import xml.etree.ElementTree as ET


ADDON = xbmcaddon.Addon()
IPTV_ADDON_ID = "pvr.iptvsimple"
IPTV_ADDON = xbmcaddon.Addon(IPTV_ADDON_ID)
SECRET_KEY = "Raitra123##@@Vip"

addon_path = xbmcaddon.Addon().getAddonInfo('path')
pyjwt_path = os.path.join(addon_path, 'resources', 'libs', 'pyjwt')
sys.path.append(pyjwt_path)

addon_data_path = os.path.join(xbmcvfs.translatePath("special://userdata"),'addon_data', 'pvr.iptvsimple')

import jwt

def update_m3u_url(new_url):
    settings_file = os.path.join(addon_data_path, "instance-settings-1.xml")

    if not os.path.exists(settings_file):
        xbmcgui.Dialog().notification("Error", "IPTV Simple Client settings file not found!", xbmcgui.NOTIFICATION_ERROR, 8000)
        return False
    
    tree = ET.parse(settings_file)
    root = tree.getroot()
    
    for setting in root.findall("setting"):
        #print the setting id and it's child value

        print(setting.get("id"), setting.get("value"))
        if setting.get("id") == "m3uUrl":
            print("hita ilay ovaina")
            setting.text = new_url
            break
   
    tree.write(settings_file)
  
def check_subscription_status():
    token = ADDON.getSetting("token")


    if not token:
        xbmcgui.Dialog().ok("Subscription Required", "You need to enter a valid subscription token to use IT ZONE TV!")
        update_m3u_url("")
        return False
    try:
        #Convert expiry date to timestamp
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        expiry_date_str = decoded_payload["expiry_date"]
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")

        current_date = datetime.now()

        days_remaining = (expiry_date - current_date).days
        print(f"DAYS  REMAINING {days_remaining}")

        if days_remaining <= 0:
            xbmcgui.Dialog().ok("Subscription Expired", "Your IT ZONE TV subscriptioin has expired! Please renew.")
            #get all exisiting instances of the setting
            update_m3u_url("http://it-zone.tech/test/URL")
            return False
        elif days_remaining <= 364:
            xbmcgui.Dialog().notification("Warning", f"Your IT ZONE TV subscription expires in {int(days_remaining)} days!", xbmcgui.NOTIFICATION_WARNING, 8000)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", "An error occurred while checking subscription status!", xbmcgui.NOTIFICATION_ERROR, 8000)
        print(e)

    return True

class SubscriptionMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        check_subscription_status()

def run_service():
    print("Service IT ZONE STARTED")
    monitor = SubscriptionMonitor()

    if not check_subscription_status():
        return
    
    while not monitor.abortRequested():
        xbmc.sleep(21600000)
        check_subscription_status()

if __name__ == "__main__":
    run_service()

