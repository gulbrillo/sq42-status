import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
from pypresence import Presence
import time

def close_app(icon):
    icon.stop()
    RPC.clear()
    RPC.close()
    exit()

def setup_tray():
    icon_image = Image.new('RGB', (64, 64), color='white')
    icon = pystray.Icon("Discord Status Updater", icon_image, menu=pystray.Menu(
        item('Close', close_app)
    ))
    icon.run()

def update_presence():
    client_id = '1300650992895004744'
    global RPC
    RPC = Presence(client_id)
    RPC.connect()
    RPC.update(
        state="Chapter 1: Prologue",
        start=time.time(),
        large_image="logo_color",
        large_text="Epic Quest",
        buttons=[
            {"label": "Join Adventure", "url": "https://robertsspaceindustries.com/enlist?referral=STAR-F3GJ-MFBD"}
        ]
    )
    while True:
        time.sleep(15)  # Keep the presence alive

# Run the tray icon and presence updater in separate threads
tray_thread = threading.Thread(target=setup_tray)
presence_thread = threading.Thread(target=update_presence)
tray_thread.start()
presence_thread.start()

