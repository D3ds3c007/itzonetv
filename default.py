import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import sys
import xbmcvfs
import os
from datetime import datetime
import json
import urllib.request
import xml.etree.ElementTree as ET



ADDON = xbmcaddon.Addon("plugin.video.iptvvoucher")
IPTV_ADDON_ID = "pvr.iptvsimple"
IPTV_ADDON = xbmcaddon.Addon(IPTV_ADDON_ID)
SECRET_KEY = "Raitra123##@@Vip"

# Server API where vouchers are validated
VOUCHER_API_URL = "http://localhost:5000/vouchers"
addon_data_path = os.path.join(xbmcvfs.translatePath("special://userdata"),'addon_data', 'pvr.iptvsimple')


addon_path = xbmcaddon.Addon().getAddonInfo('path')
pyjwt_path = os.path.join(addon_path, 'resources', 'libs', 'pyjwt')
sys.path.append(pyjwt_path)

import jwt



def show_voucher_input():
    """
    Show a Kodi dialog to enter the voucher code.
    """
    keyboard = xbmc.Keyboard("", "Enter Voucher Code", False)
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        return keyboard.getText().strip()
    return None

def update_m3u_url(new_url):
    settings_file = os.path.join(addon_data_path, "instance-settings-1.xml")

    if not os.path.exists(settings_file):
        xbmcgui.Dialog().notification("Error", "IPTV Simple Client settings file not found!", xbmcgui.NOTIFICATION_ERROR, 8000)
        return False
    
    tree = ET.parse(settings_file)
    root = tree.getroot()
    
    for setting in root.findall("setting"):
        #print the setting id and it's child value
        if setting.get("id") == "m3uUrl":
            setting.text = new_url
            break
   
    tree.write(settings_file)

def validate_voucher(voucher_code):
    
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "voucher": voucher_code
    }

    json_data = json.dumps(data).encode("utf-8")
    try:
         req = urllib.request.Request(VOUCHER_API_URL, data=json_data, headers=headers)

         response = urllib.request.urlopen(req)
         response_data = json.load(response)
         
         print(f"RESPONSE = {response_data}")
         print(f"RESPONSE PROP = {response_data['expiration_date']}")


         return response_data
    except Exception as e:
        print(e)
        return False

def save_subscription_info(m3u_url, expiry_date, encoded_token):
    #  IPTV_ADDON.setSetting("m3uUrl", "http://it-zone.tech/test/URL")
    ADDON.setSetting("token", encoded_token)
    update_m3u_url(m3u_url)
    xbmcgui.Dialog().ok("Success", f"Subscription renewed!\nExpires on: {expiry_date}")

#write function to get the m3u url from the addon pvr.iptvsimple. The m3u url is stored in the settings of the addon and
def main():
    expiry_date_str = ADDON.getSetting('expiry_date')

    print(f"Subscription Expiry Date: {expiry_date_str}")
    voucher_code = show_voucher_input()
    if voucher_code:
        response = validate_voucher(voucher_code)
        if response["success"] == True:
                expiry_date = response['expiration_date']
                print(f"Expiry date is {expiry_date}")
                print(type(expiry_date))

                payload = {
                    "expiry_date": expiry_date  # or you could use timestamp
                }

                # Create the JWT token
                encoded_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

                # To decode it
                decoded_payload = jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
                
                save_subscription_info(response["m3uUrl"], expiry_date, encoded_token) 
                print(f"Expiry date is {decoded_payload}")
                xbmcgui.Dialog().ok("Success", "Subscription renewed successfully!")
        else:
                xbmcgui.Dialog().ok("Error", "Invalid Voucher Code! "+ str(new_m3u_url))
             

if __name__ == "__main__":
     main()
