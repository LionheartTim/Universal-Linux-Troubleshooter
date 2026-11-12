"""Friendly, practical next steps. These text commands are never executed by the app.

Plain English comes first. Technical output remains available in Evidence / Logs.
"""
from __future__ import annotations
from ..results import ResultStatus
from .desktop_guidance import network_settings_steps

_GUIDANCE: dict[tuple[str, str, ResultStatus], str] = {
    ("network", "adapter", ResultStatus.OK): """1. Linux can see your network devices. No adapter repair is needed based on this check.
2. If your internet still disconnects, run 'IP configuration' in this app next.
3. To see which devices are connected, open a terminal and paste:
   ip -br link
   ip -br address
4. 'DOWN' simply means a connection is not active right now. This can be normal for a device you do not use.
5. If your Wi-Fi keeps disconnecting, write down when it happens. A later check will look for connection errors.

This check does not test your Wi-Fi signal or your router. If the internet works, you do not need to change anything.""",
    ("network", "adapter", ResultStatus.WARNING): """1. Open your computer's network settings. Check whether Wi-Fi or the network cable connection is turned on.
2. To see what Linux can find, open a terminal and paste:
   ip -br link
3. If your Wi-Fi or cable device is missing, check whether it appears in your computer's system information. In a virtual machine, check its network settings instead.
4. Do not reinstall anything or reset your router yet. First find out which device is missing.

A missing device in this list does not prove that it is broken.""",
    ("network", "ip", ResultStatus.OK): """1. Your computer has an IP address (its address on the network) and knows which route to use. Nothing needs to be changed based on this check.
2. If websites still will not open, check your network settings in a terminal:
   ip route
   ip -6 route
3. If your system supports it, this command shows the settings used to find website addresses:
   resolvectl status
4. 'Website name check' can test name lookups with your permission. 'Local gateway' checks local router settings only.

This result does not prove that the internet works. Do not reset your router just because a website fails to load.""",
    ("network", "ip", ResultStatus.WARNING): """1. Open your computer's network settings and find the connection you actually want to use.
2. If it should be connected, check whether it has a network address:
   ip -br address
   ip route
3. If your computer uses NetworkManager, you can also check the connections with:
   nmcli device status
4. If your intended connection is disconnected, reconnect it using your normal network settings. Then run this check again.

An unused connection can have no address and still be completely normal. Do not enter guessed network settings.""",
    ("network", "ip", ResultStatus.UNKNOWN): """1. Your computer has a network address, but this check could not confirm how it would reach the internet.
2. If your network should have internet access, look at the connection settings first.
3. You can inspect those settings without changing anything:
   ip -br address
   ip route
   ip -6 route
4. Check again once your normal internet connection is active.

Some private networks do not need internet access, so a missing route is not always a problem.""",
    ("storage", "space", ResultStatus.OK): """1. The location checked has enough free space for now. There is nothing to clean up based on this result.
2. If an app still says the disk is full, that app may save its files on a different disk.
3. To see the free space on your disks, open a terminal and paste:
   df -h
4. Only remove files that you recognize and no longer need.

This measures free space. It does not check whether a disk is healthy.""",
    ("storage", "space", ResultStatus.WARNING): """1. Save your work. One place where your computer stores files may be getting full.
2. To see which disk is short on space, open a terminal and paste:
   df -h
3. Look at your own Downloads and Trash folders first. Remove only files you no longer want.
4. On Bazzite or another Atomic Linux system, the main system image can look completely full even when this is normal. Never delete Linux system files by hand.
5. Run 'Disk space' again after you have made any changes.

Do not erase disks or delete unknown folders. If you are not sure what is safe to remove, stop and ask first.""",
    ("storage", "drives", ResultStatus.OK): """1. Linux showed a list of storage devices. This does not mean every disk is healthy.
2. If you are looking for a missing disk, compare that list with the drives you expect to see.
3. You can see the drive list again in a terminal:
   lsblk -o NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO
4. If a disk is missing, check the connection before changing its settings. If your files are important and you suspect damage, back them up.

Do not format a disk just because it does not appear in a folder.""",
    ("applications", "resources", ResultStatus.OK): """1. Your computer had enough available memory (RAM) during this check. No change is needed based on this result.
2. If a program freezes, check again while the problem is happening. Memory use can change quickly.
3. You can use your desktop's System Monitor or these commands:
   free -h
   uptime
4. If the same app repeatedly uses a lot of memory, note its name and when this happens.

This one quick check cannot tell us whether the computer is always running smoothly.""",
    ("applications", "resources", ResultStatus.WARNING): """1. Save any open work. Your computer may be running low on working memory (RAM).
2. Open your desktop's System Monitor and sort programs by memory use.
3. To see the available memory in a terminal, paste:
   free -h
4. If you recognize a program using a lot of memory, save its work before choosing to close it yourself.
5. Run this test again to see whether there is more memory available.

Do not delete system files or turn off unknown services to fix a memory warning.""",
    ("applications", "services", ResultStatus.OK): """1. Linux did not report any stopped system services that it considers failed. No repair is suggested by this check.
2. If a particular app still does not work, the problem may be in that app rather than a system service.
3. You can see the failed-service list in a terminal:
   systemctl --failed --no-pager

This does not check every program or every background task on your computer.""",
    ("applications", "services", ResultStatus.WARNING): """1. Open 'Evidence / Logs'. Look for the name of the service that Linux says failed. A service is a program that works in the background.
2. To see details for that service, replace UNIT_NAME in this command with its exact name:
   systemctl status UNIT_NAME --no-pager
3. To see its recent messages, you can also use:
   journalctl -u UNIT_NAME -b --no-pager -n 50
4. Check whether this service has anything to do with the problem you noticed before changing anything.
5. If you choose to make a change yourself, run 'Service status' again.

UNIT_NAME is only an example: replace it with the EXACT name shown in the logs. This app does not restart services.""",
    ("system", "system_logs", ResultStatus.UNKNOWN): """1. This check could not read enough system messages to identify a reliable result.
2. Think about when the problem happened. Some messages may be missing or private.
3. To view the recent important messages that your account can read, open a terminal and paste:
   journalctl -b -p 0..3 --no-pager -n 50
4. If only one app is affected, try looking at its own error messages.

Do not change security settings just to make this check say OK. Logs can contain private details, so check them before sharing.""",
}


_OK_DETAILS = {
    ("network", "adapter"): (
        "Linux found the network equipment it can see. This check does not show whether "
        "Wi-Fi or the internet is working. If you still have a problem, run 'Wi-Fi connection' "
        "or 'IP configuration' in Internet & Network."
    ),
    ("network", "ip"): (
        "Linux reports an IP address and a configured route. This shows local "
        "network settings, NOT whether the internet or a website is reachable. "
        "If browsing still fails, first notice whether it affects all websites "
        "or just one. To check website-name resolution (DNS), you can optionally "
        "open your host terminal and run: getent ahosts www.mozilla.org. "
        "That may ask your configured DNS server for the address; the app will "
        "NOT run it without your permission. If you get IP addresses, the name "
        "resolved at that moment, but it does not prove the page opens. "
        "To see your router setting WITHOUT contacting it, run: ip -4 route show default. "
        "A 'default via' line shows a configured gateway, not that the router works."
    ),
}


def guided_solution(category: str, check: str, status: ResultStatus, fallback: str) -> str:
    """Provide a short OK summary, or step-by-step help if investigation is needed."""
    if status == ResultStatus.OK:
        extra = _OK_DETAILS.get((category, check),
                                "If you still notice a problem, look at the exact findings in 'Evidence / Logs'.")
        return ("This check finished successfully. No changes are needed based on this result.\n\n"
                + extra + "\n\n"
                "Open 'Evidence / Logs' to see what was checked. "
                "You choose what to do; this app never changes your computer for you.")
    guidance = _GUIDANCE.get((category, check, status))
    if guidance is None:
        # No reviewed procedure for this combination: do not invent one.
        return fallback
    intro = ("Steps to investigate this finding:" if status in (ResultStatus.WARNING, ResultStatus.PROBLEM)
             else "More information is needed to identify the problem:")
    if category == "network" and check in ("adapter", "ip"):
        # Replace vague, desktop-agnostic guidance with exact navigation steps.
        if status == ResultStatus.WARNING:
            if check == "adapter":
                guidance = guidance.replace("1. Open your computer's network settings. Check whether Wi-Fi or the network cable connection is turned on.",
                                            "1. Find your connection using the instructions below.")
            else:
                guidance = guidance.replace("1. Open your computer's network settings and find the connection you actually want to use.",
                                            "1. Find your connection using the instructions below.")
        guidance += "\n\nHow to find the settings on your desktop:\n" + network_settings_steps()
    return f"{intro}\n\n{guidance}\n\nYou choose what to do. This app never changes your computer for you."
