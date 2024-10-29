import sys
import os
import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
from pypresence import Presence
import time
import math
import random

# Create an event to signal the presence thread to stop
stop_event = threading.Event()

# Shared variable for the tooltip text
tooltip_text = ""
tooltip_lock = threading.Lock()

def close_app(icon, item):
    """Stops the tray icon and signals the presence thread to stop."""
    stop_event.set()     # Signal the presence thread to exit
    icon.stop()          # Stop the system tray icon

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_tray():
    """Sets up and runs the system tray icon."""
    # Path to your icon image file
    icon_path = resource_path('icon.png')  # Use resource_path to locate icon.png

    # Check if the icon file exists
    if not os.path.isfile(icon_path):
        print(f"Icon file '{icon_path}' not found.")
        return  # Exit the function if the icon file is not found

    # Load the icon image from a file
    try:
        icon_image = Image.open(icon_path).convert('RGBA')  # Ensure image has alpha channel
        icon_image = icon_image.resize((64, 64), Image.LANCZOS)
    except Exception as e:
        print(f"Error loading icon image: {e}")
        return

    icon = pystray.Icon(
        "Discord SQ42 Status",
        icon_image,
        menu=pystray.Menu(item('Quit', close_app))
    )

    def update_tooltip():
        """Updates the tooltip text of the tray icon."""
        with tooltip_lock:
            icon.title = tooltip_text
        # Schedule the next update
        if not stop_event.is_set():
            threading.Timer(1, update_tooltip).start()

    # Start updating the tooltip
    update_tooltip()

    icon.run()  # Start the tray icon event loop

def update_presence():
    """Updates the Discord Rich Presence and keeps it alive."""
    client_id = '1300650992895004744'  # Your actual Application ID

    try:
        RPC = Presence(client_id)
        RPC.connect()
    except Exception as e:
        print(f"Could not connect to Discord: {e}")
        return  # Exit if unable to connect

    # List of chapter names matching the theme of Squadron 42
    chapters = [
        "Prologue",
        "Enlistment Day",
        "First Flight",
        "Into the Breach",
        "Enemy Encounter",
        "The Lost Colony",
        "Deep Space Rescue",
        "Betrayal in the Ranks",
        "Secrets Unveiled",
        "Battle for Vega",
        "Dark Horizons",
        "The Siege of Orion",
        "Shadows of the Vanduul",
        "Allies and Enemies",
        "The Long Journey Home",
        "Crossroads",
        "The Tides of War",
        "Into the Void",
        "The Final Stand",
        "A New Threat",
        "Echoes of the Past",
        "Uncharted Territories",
        "The Calm Before the Storm",
        "The Gathering Storm",
        "Breaking Point",
        "The Reckoning",
        "Endgame",
        "Epilogue"
    ]

    total_chapters = len(chapters)

    # Randomize the starting chapter index
    chapter_index = random.randint(0, total_chapters - 1)

    # Calculate the initial time for the next chapter change
    mean_chapter_duration = 3 * 3600  # Mean duration of 3 hours in seconds
    time_until_next_chapter = -mean_chapter_duration * math.log(1 - random.random())
    next_chapter_change = time.time() + time_until_next_chapter

    # Initialize the start time once
    start_time = time.time()

    # Counter to keep track of seconds for Discord update
    seconds_counter = 15

    try:
        while not stop_event.is_set():
            current_time = time.time()

            # Update chapter if needed
            if current_time >= next_chapter_change:
                # Advance to the next chapter
                chapter_index = (chapter_index + 1) % total_chapters

                # Schedule the next chapter change
                time_until_next_chapter = -mean_chapter_duration * math.log(1 - random.random())
                next_chapter_change = current_time + time_until_next_chapter

            # Calculate elapsed time since start_time
            elapsed_seconds = int(current_time - start_time)
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_time_str = f"{hours}h {minutes}m {seconds}s"

            # Update the shared tooltip text
            with tooltip_lock:
                global tooltip_text
                tooltip_text = f"Chapter {chapter_index + 1}: {chapters[chapter_index]}\nTime Elapsed: {elapsed_time_str}"

            # Increment the seconds counter
            seconds_counter += 1

            # Update Discord presence every 15 seconds
            if seconds_counter >= 15:
                # Update the presence with the current chapter
                RPC.update(
                    state=f"Chapter {chapter_index + 1}: {chapters[chapter_index]}",
                    start=start_time,
                    large_image="logo_color",
                    large_text="Cloud Imperium Games",
                    buttons=[
                        {
                            "label": "Join me",
                            "url": "https://robertsspaceindustries.com/enlist?referral=STAR-F3GJ-MFBD"
                        }
                    ]
                )
                seconds_counter = 0  # Reset the counter

            time.sleep(1)  # Sleep for 1 second
    finally:
        # Clean up the presence before exiting
        RPC.clear()
        RPC.close()

# Run the tray icon and presence updater in separate threads
tray_thread = threading.Thread(target=setup_tray)
presence_thread = threading.Thread(target=update_presence)

tray_thread.start()
presence_thread.start()

# Wait for both threads to finish
tray_thread.join()
stop_event.set()  # Ensure the presence thread stops if the tray icon is closed
presence_thread.join()
