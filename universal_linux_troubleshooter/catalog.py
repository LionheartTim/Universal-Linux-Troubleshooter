"""Stable diagnostic catalogue: honest scopes and beginner-friendly wording."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    key: str
    title: str
    purpose: str
    explanation: str


@dataclass(frozen=True)
class Category:
    key: str
    title: str
    subtitle: str
    intro: str
    checks: tuple[Check, ...]


CATEGORIES: tuple[Category, ...] = (
    Category(
        "network", "Internet & Network", "Connectivity, Wi-Fi, routing and DNS",
        "Check what happens between your computer, your router and the internet. A lost connection does not always mean your provider is at fault.",
        (
            Check("adapter", "Network adapters", "See which Wi-Fi and cable connections your computer can find.",
                  "Confirm which interfaces exist and which driver each interface uses. Detecting an interface alone does not prove it works."),
            Check("wifi", "Wi-Fi connection", "See whether Wi-Fi is connected right now (not its past stability).",
                  "This first check reads the current connection state. It does not measure signal strength or investigate past dropouts."),
            Check("ip", "IP configuration", "Check whether your computer has a network address and knows how to reach your router.",
                  "Look for missing addresses, DHCP failures, and suspicious routes. Tests must account for distro-specific network managers."),
            Check("dns", "Website name check", "With permission, check whether Linux can find a website's address.",
                  "Looks up the address of www.mozilla.org through your normal Linux name resolver. This may contact a DNS server. It does not visit the website or test whether the connection stays working. Nothing is sent without your permission."),
            Check("gateway", "Local gateway", "See which router your computer plans to use, without contacting it.",
                  "Reads local route settings only, not whether router traffic succeeds. Do not reset the router as a first step."),
            Check("external", "External connectivity", "With permission, check whether an outside website answers once.",
                  "An optional secure connection to www.mozilla.org can test access beyond your router. This does not prove every site works. No connection is made without your permission."),
        ),
    ),
    Category(
        "hardware", "Hardware & Power", "Thermals, memory, sensors and shutdowns",
        "Check your computer's parts without changing their settings.",
        (
            Check("sensors", "Temperature sensors", "See whether your computer can show temperature readings.",
                  "Sensor availability and labels differ by hardware. Missing readings do not mean normal temperatures."),
            Check("power", "Power management", "Examine shutdown and suspend-related records.",
                  "Compare power events and system logs. Abrupt power loss may leave little or no trace in the logs."),
            Check("memory", "Memory indicators", "Look for messages about problems with your computer's memory.",
                  "Kernel memory warnings are useful clues; absence of warnings does not prove RAM is healthy."),
            Check("hardware_logs", "Hardware warnings", "Review available hardware and kernel error records.",
                  "Correlate events by time and device. Warnings alone do not always identify the failing component."),
        ),
    ),
    Category(
        "storage", "Storage & Filesystems", "Disk health, mounts and capacity",
        "Check your disks and free space. This app will never delete files or change a disk.",
        (
            Check("space", "Disk space", "See how much space is left for files and apps.",
                  "Capacity checks help find full filesystems and temporary space pressure."),
            Check("drives", "Drive inventory", "See which disks and storage areas your computer can find.",
                  "Distinguish physical devices, partitions and mounted filesystems to avoid confusion."),
            Check("health", "Drive health indicators", "Read a disk’s built-in health warning, if your account can access it.",
                  "Uses smartctl in read-only mode if installed and permitted. No administrator password, disk self-test or repair. Not all drives expose health data; a good result does not guarantee safety."),
            Check("fs_logs", "Filesystem warnings", "Review filesystem-related error messages.",
                  "Collect warnings without invoking automatic filesystem repair; repairs require informed user action."),
        ),
    ),
    Category(
        "applications", "Applications & Services", "Crashes, processes and background services",
        "Find out why a program or something running in the background may not work.",
        (
            Check("services", "Service status", "See whether important background programs reported a problem.",
                  "Check the applicable service manager; do not assume every distribution runs the same tools."),
            Check("app_crashes", "Application crashes", "Look for recent application crash messages in local system logs.",
                  "Looks at recent system-log messages, not complete app crash reports. Match timestamps before drawing conclusions."),
            Check("resources", "Resource pressure", "Check whether your computer is short on memory or very busy.",
                  "Short spikes are not automatically faults; compare with the reported symptom."),
            Check("permissions", "Permissions clues", "Find messages about programs that were not allowed to open or change something.",
                  "Explain any permission-related evidence without automatically changing ownership or access rules."),
        ),
    ),
    Category(
        "graphics", "Graphics & Display", "GPU, drivers and monitors",
        "Check screen problems without changing display settings.",
        (
            Check("gpu", "GPU inventory", "List graphics devices found in the computer.",
                  "This lists hardware but does not confirm which driver or graphics card an app uses."),
            Check("render", "Graphics errors", "Inspect graphics-driver and rendering warnings.",
                  "Look for recurring errors and contextualize them before recommending a driver change."),
            Check("display", "Display configuration", "Check which physical screen connections Linux can see.",
                  "Only checks connections reported by the kernel. It does not yet read display resolution or desktop settings."),
        ),
    ),
    Category(
        "audio", "Audio & Bluetooth", "Devices, services and wireless audio",
        "Check whether sound and Bluetooth devices are present and working.",
        (
            Check("audio_devices", "Audio devices", "See which sound cards Linux lists.",
                  "Does not check which speaker or microphone is chosen, or whether sound can be heard."),
            Check("audio_services", "Audio services", "Check whether the programs that handle sound are working.",
                  "Modern Linux systems may use PipeWire and WirePlumber; test actual system capabilities."),
            Check("bluetooth", "Bluetooth status", "Check for a Bluetooth adapter and its background service.",
                  "This first check does not yet test radio blocking, pairing or device connections."),
        ),
    ),
    Category(
        "virtualization", "Virtual Machines & Containers", "Virtualization services and guest connectivity",
        "Check virtual computers and containers, if you use them.",
        (
            Check("vm_backend", "Virtualization backend", "Identify available VM-related services.",
                  "Check what is actually installed before looking for a service or configuration."),
            Check("vm_network", "Virtual network", "See whether common virtual-network connections are listed.",
                  "Presence of a virtual network is not proof that traffic can pass through it."),
            Check("containers", "Container environment", "See whether common container programs are installed.",
                  "Lists common installed tools only, not running containers or errors."),
        ),
    ),
    Category(
        "system", "System, Boot & Updates", "Startup, system logs and package state",
        "Find out what Linux reported when your computer started or something went wrong.",
        (
            Check("boot", "Boot events", "Look for messages from when your computer started.",
                  "Only checks recent current-boot messages. Older messages may be missing or hidden."),
            Check("updates", "Update state", "Review local update or restart notices without going online.",
                  "Only local restart clues and staged atomic versions are checked; it does not look for new online updates."),
            Check("system_logs", "System errors", "Look at recent messages about things that may have gone wrong.",
                  "System messages are checked for recognizable faults and relevant solutions. A warning alone is not proof of a defect."),
        ),
    ),
)


def match_categories(query: str) -> tuple[Category, ...]:
    """Find categories using titles, descriptions and their checks."""
    q = query.strip().casefold()
    if not q:
        return CATEGORIES
    return tuple(
        cat for cat in CATEGORIES
        if q in cat.title.casefold()
        or q in cat.subtitle.casefold()
        or q in cat.intro.casefold()
        or any(
            q in f"{check.title} {check.purpose} {check.explanation}".casefold()
            for check in cat.checks
        )
    )
