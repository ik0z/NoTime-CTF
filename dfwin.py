import datetime
import os
import socket
import subprocess
import winreg

# Get current date and time
now = datetime.datetime.now()

# Get device information
device_name = socket.gethostname()
device_ip = socket.gethostbyname(device_name)
device_domain = subprocess.check_output(['powershell.exe', 'Get-WmiObject Win32_ComputerSystem | Select-Object Domain']).decode('utf-8').split('\n')[2].strip()

# Evidence of execution
user_assist_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist")
user_assist_guids = []
try:
    i = 0
    while True:
        guid = winreg.EnumKey(user_assist_key, i)
        user_assist_guids.append(guid)
        i += 1
except WindowsError:
    pass
user_assist_data = []
for guid in user_assist_guids:
    count_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist\\{guid}\\Count")
    i = 0
    while True:
        try:
            name, value, _ = winreg.EnumValue(count_key, i)
            user_assist_data.append(f"UserAssist\\{guid}\\Count\\{name}: {value}")
            i += 1
        except WindowsError:
            break
shim_cache_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\AppCompatCache")
shim_cache_data = []
try:
    i = 0
    while True:
        name, value, _ = winreg.EnumValue(shim_cache_key, i)
        shim_cache_data.append(f"AppCompatCache\\{name}: {value}")
        i += 1
except WindowsError:
    pass
am_cache_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\hivelist")
am_cache_data = []
try:
    i = 0
    while True:
        key = winreg.EnumKey(am_cache_key, i)
        if "Amcache.hve" in key:
            amcache_key = winreg.OpenKey(am_cache_key, key + "\\Root\\File")
            j = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(amcache_key, j)
                    am_cache_data.append(f"Amcache.hve\\Root\\File\\{key}\\{name}: {value}")
                    j += 1
                except WindowsError:
                    break
        i += 1
except WindowsError:
    pass
bam_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\bam\\UserSettings")
dam_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\dam\\UserSettings")
bam_data = []
dam_data = []
try:
    i = 0
    while True:
        sid = winreg.EnumKey(bam_key, i)
        bam_sid_key = winreg.OpenKey(bam_key, sid)
        try:
            name, value, _ = winreg.EnumValue(bam_sid_key, 0)
            bam_data.append(f"BAM\\{sid}\\{name}: {value}")
        except WindowsError:
            pass
        dam_sid_key = winreg.OpenKey(dam_key, sid)
        try:
            name, value, _ = winreg.EnumValue(dam_sid_key, 0)
            dam_data.append(f"DAM\\{sid}\\{name}: {value}")
        except WindowsError:
            pass
        i += 1
except WindowsError:
    pass

# External/USB Device Forensics
usbstor_data = []
usbstor_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Enum\\USBSTOR")
try:
    i = 0
    while True:
        device_key_name = winreg.EnumKey(usbstor_key, i)
        device_key = winreg.OpenKey(usbstor_key, device_key_name)
        try:
            friendly_name, _ = winreg.QueryValueEx(device_key, "FriendlyName")
            manufacturer, _ = winreg.QueryValueEx(device_key, "Mfg")
            usbstor_data.append(f"USBSTOR\\{device_key_name}: {friendly_name} ({manufacturer})")
        except WindowsError:
            pass
        i += 1
except WindowsError:
    pass

usb_data = []
usb_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Enum\\USB")
try:
    i = 0
    while True:
        device_key_name = winreg.EnumKey(usb_key, i)
        device_key = winreg.OpenKey(usb_key, device_key_name)
        try:
            friendly_name, _ = winreg.QueryValueEx(device_key, "FriendlyName")
            manufacturer, _ = winreg.QueryValueEx(device_key, "Mfg")
            usb_data.append(f"USB\\{device_key_name}: {friendly_name} ({manufacturer})")
        except WindowsError:
            pass
        i += 1
except WindowsError:
    pass

# Write output to file
with open(f"{device_name}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt", "w") as f:
    f.write(f"Device Name: {device_name}\n")
    f.write(f"IP Address: {device_ip}\n")
    f.write(f"Domain: {device_domain}\n")
    f.write("\nExternal/USB Device Forensics:\n")
    for item in usbstor_data:
        f.write(f"{item}\n")
    for item in usb_data:
        f.write(f"{item}\n")
    f.write("\nFile/Folder Usage or Knowledge:\n")
    for item in recent_docs_data:
        f.write(f"{item}\n")
    for item in office_recent_data:
        f.write(f"{item}\n")
    for item in shellbags_data:
        f.write(f"{item}\n")
    for item in open_save_data:
        f.write(f"{item}\n")
    f.write("\nSystem Info and Accounts:\n")
    for item in users_data:
        f.write(f"{item}\n")