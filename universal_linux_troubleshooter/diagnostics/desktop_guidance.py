"""Human-readable, step-by-step paths to network settings for common desktops.

These are instructions only; this module does not launch any program or change settings.
Never assume all Linux users are running the same desktop.
"""
from __future__ import annotations
import os


def desktop_name(environment: dict[str, str] | None = None) -> str:
    env = os.environ if environment is None else environment
    name = ":".join((env.get("XDG_CURRENT_DESKTOP", ""), env.get("DESKTOP_SESSION", ""))).lower()
    if "plasma" in name or "kde" in name:
        return "kde"
    if "gnome" in name or "ubuntu" in name:
        return "gnome"
    if "xfce" in name or "xubuntu" in name:
        return "xfce"
    if "cinnamon" in name:
        return "cinnamon"
    if "mate" in name:
        return "mate"
    if "lxqt" in name:
        return "lxqt"
    return "other"


def network_settings_steps(desktop: str | None = None) -> str:
    """Instructions for a novice, adaptable to KDE/GNOME/etc. No actions performed."""
    system = (desktop or desktop_name()).lower()
    if system == "kde":
        return ("On KDE Plasma (including Bazzite):\n"
                "1. Click the application menu in the lower-left corner of your desktop.\n"
                "2. Search for 'System Settings' and open it.\n"
                "3. In the left menu, choose 'Wi-Fi & Internet' (or search for 'Connections').\n"
                "4. Check whether Wi-Fi is switched on and whether the correct network says 'Connected'.\n"
                "Tip: You can also click the network symbol near the clock in the taskbar.")
    if system == "gnome":
        return ("On GNOME:\n"
                "1. Click the system menu in the top-right corner of the screen.\n"
                "2. Open 'Settings' (gear symbol).\n"
                "3. Click 'Wi-Fi' in the left menu. For a network cable, click 'Network' instead.\n"
                "4. Check whether your connection is switched on and shows the expected network name.")
    if system == "xfce":
        return ("On Xfce (including Xubuntu):\n"
                "1. Find the network connection symbol on the taskbar, often near the clock.\n"
                "2. Click it to see the available networks. Look for your connected network.\n"
                "3. For more details, open the application menu > Settings > 'Network Connections' "
                "(if that option is installed).\n"
                "4. Check that the expected connection is active.")
    if system == "cinnamon":
        return ("On Cinnamon:\n"
                "1. Open the application menu.\n"
                "2. Open 'System Settings'.\n"
                "3. Find 'Network' and inspect Wi-Fi or wired connections.\n"
                "4. Check that your expected network is connected.")
    if system in ("mate", "lxqt"):
        return ("On this desktop:\n"
                "1. Find the network symbol in the panel, often beside the clock.\n"
                "2. Click it and check that your network is connected.\n"
                "3. If needed, open the application menu > Preferences / Settings > 'Network Connections' "
                "(when NetworkManager is installed).")
    return ("To find your network settings:\n"
            "1. Find the network or Wi-Fi symbol on your desktop panel, often near the clock.\n"
            "2. Click it to see whether your intended Wi-Fi or cable connection is active.\n"
            "3. If you do not see it, open the application menu and search for 'Network' or 'Connections'.\n"
            "Different Linux desktops use different menu names, so yours may look a little different.")


# Plain-language navigation for common problems. These are instructions, not
# commands; we never launch System Settings or change a desktop preference.
_DESKTOP_SETTINGS = {
    "kde": {
        "sound": ("Sound", "Find 'Playback Devices' and check which speaker or headphones are selected."),
        "display": ("Display & Monitor", "Check that the screen you want to use is enabled."),
        "bluetooth": ("Bluetooth", "Check whether Bluetooth is switched on and whether your device is connected."),
    },
    "gnome": {
        "sound": ("Sound", "Under 'Output', look for your speakers or headphones. Check the volume."),
        "display": ("Displays", "Look for your screen and check whether it is enabled."),
        "bluetooth": ("Bluetooth", "Check whether Bluetooth is on and your device appears as connected."),
    },
    "xfce": {
        "sound": ("Sound / PulseAudio Volume Control", "Check the selected output device and volume; this tool may have a different name on your system."),
        "display": ("Display", "Check whether the expected monitor is enabled."),
        "bluetooth": ("Bluetooth / Bluetooth Manager", "Check whether Bluetooth is on and whether the device appears as connected. Some Xfce systems do not install a Bluetooth manager."),
    },
}


def desktop_settings_steps(topic: str, desktop: str | None = None) -> str:
    """Show concrete, non-destructive clicks for sound, display or Bluetooth."""
    if topic not in {"sound", "display", "bluetooth"}:
        raise ValueError("Unknown settings category")
    system = (desktop or desktop_name()).lower()
    if system in ("kde", "gnome", "xfce"):
        target, hint = _DESKTOP_SETTINGS[system][topic]
        if system == "kde":
            return ("On KDE Plasma (including Bazzite):\n"
                    "1. Click the application menu on your desktop (usually bottom left).\n"
                    "2. Search for 'System Settings' and open it.\n"
                    f"3. Find '{target}' in the left menu, or use the search field.\n"
                    f"4. {hint}")
        if system == "gnome":
            return ("On GNOME:\n"
                    "1. Open the top-right system menu.\n"
                    "2. Click 'Settings' (the gear symbol).\n"
                    f"3. Select '{target}' in the left menu.\n"
                    f"4. {hint}")
        return ("On Xfce (including Xubuntu):\n"
                "1. Open the application menu.\n"
                "2. Select 'Settings' (or 'Settings Manager').\n"
                f"3. Look for '{target}'.\n"
                f"4. {hint}")
    names = {"sound": "Sound or Audio", "display": "Display or Monitor", "bluetooth": "Bluetooth"}
    return ("To find this setting on your Linux desktop:\n"
            "1. Open the application menu.\n"
            f"2. Search for '{names[topic]}' or open 'Settings'.\n"
            "3. Look for the device you want to use and check whether it is switched on or selected.\n"
            "Menu names may differ on your Linux desktop. If you cannot find the setting, "
            "do not change unrelated options.")


# v103: named and conditional navigation for the KDE game-controller page.
# The screen exists in KDE documentation, but modules can be absent, hidden,
# or version-dependent. The UI must NEVER invent a generic "desktop test screen".
def controller_test_screen_steps(desktop: str | None = None) -> str:
    """Read-only, user-operated navigation. No external app is launched."""
    system = (desktop or desktop_name()).lower()
    if system == 'kde':
        return (
            'On KDE Plasma:\n'
            '1. Open the Application Launcher (usually at the left end of the panel).\n'
            '2. Type "System Settings" and open the matching application.\n'
            '3. In the settings search box, type "Game Controller". '
            'If it is shown, open Hardware > Input Devices > Game Controller.\n'
            '4. If a controller is listed, select it and look for available '
            'button or joystick input indicators. Press a button and observe whether it responds.\n'
            '5. If the Game Controller page is missing, do not search under '
            'Display settings: this module may be absent or hidden when no '
            'supported device is detected. We can check whether Linux sees '
            'the controller instead; do not conclude the controller is broken.\n'
            'If you cannot find the page, tell me exactly which settings you see. '
            'I will use that result to choose a different read-only check.'
        )
    return (
        'There is no single game-controller test page on every Linux desktop.\n'
        '1. Open the application menu and look for System Settings or Settings.\n'
        '2. Search there for "Game Controller" or "Input Devices". '
        'Only open a matching setting if it actually appears.\n'
        '3. If there is no matching page, that is normal on some desktop environments. '
        'We can check whether Linux detects the controller with a documented read-only '
        'terminal command instead. Please tell me which desktop environment you use.'
    )
