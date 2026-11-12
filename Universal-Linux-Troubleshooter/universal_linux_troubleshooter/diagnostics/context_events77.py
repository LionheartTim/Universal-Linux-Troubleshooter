"""v77 individual, *provisional* context-adjacent event observations.

Unlike a target inventory, these require an explicit current-boot journal
message from an allowlisted process or from the kernel transport. They are
NOT target-scoped, not proof of an actual symptom, not an approved repair, and
never treat a user's supplied label as a command, source or FACT. Absent logs
are a sample only, never absence of a problem.
"""
from __future__ import annotations
from dataclasses import dataclass
import re

from ..results import ResultStatus
from .focused_evidence import _journal, _report, KERNEL_JOURNAL
from .diagnostic_events59 import SERVICE_EVENTS_JOURNAL, _sender

@dataclass(frozen=True)
class ContextEvent77:
    source: str
    senders: tuple[str, ...]
    pattern: str
    example: str
    event: str
    limitation: str

EVENTS77: dict[str, ContextEvent77] = {
    'applications.app-wont-open': ContextEvent77('service', ('systemd', 'systemd-user-runtime-dir'), '\\bfailed at step EXEC spawning\\b.{0,150}\\b(?:permission denied|exec format error|no such file or directory)\\b', 'Failed at step EXEC spawning /usr/bin/test: Permission denied', 'Een systemd-programmastart is op EXEC-niveau mislukt.', 'Het exacte gekozen programma en de oorzaak van de startfout zijn niet gekoppeld.'),
    'apps.flatpak-file-access': ContextEvent77('service', ('xdg-document-portal', 'xdg-desktop-portal'), '\\b(?:document portal|document access)\\b.{0,150}\\b(?:permission denied|access denied|request denied)\\b', 'Document portal request denied: permission denied', 'Een documentportal heeft een toegangsverzoek geweigerd.', 'Het Flatpak-app-ID, document, tijdstip en aangevraagde machtiging zijn niet onafhankelijk gekoppeld.'),
    'audio.mic-not-working': ContextEvent77('service', ('xdg-desktop-portal', 'wireplumber'), '\\b(?:microphone|audio input)\\b.{0,150}\\b(?:permission denied|access denied|request denied)\\b', 'Microphone access denied', 'Een audiobron- of microfoontoegang is volgens de betrokken dienst geweigerd.', 'Geen fysieke microfoonfout, applicatie-identiteit of werkende opname bewezen.'),
    'audio.microphone-not-recording': ContextEvent77('service', ('xdg-desktop-portal', 'wireplumber'), '\\b(?:microphone|audio input)\\b.{0,150}\\b(?:permission denied|access denied|request denied)\\b', 'Microphone access denied', 'Een microfoon- of invoertoegangsweigering is geregistreerd.', 'De betrokken toepassing, opnamekwaliteit en vergelijking met een tweede app ontbreken.'),
    'display.screenshare-black': ContextEvent77('service', ('xdg-desktop-portal', 'xdg-desktop-portal-kde', 'xdg-desktop-portal-gnome'), '\\b(?:screencast|screen sharing|screen capture)\\b.{0,150}\\b(?:permission denied|access denied|request denied|cancelled)\\b', 'ScreenCast request denied by user', 'Een schermdeel-/screencastverzoek is geweigerd of afgebroken.', 'Een bewust geweigerd verzoek bewijst geen zwart beeld of compositorprobleem.'),
    'hardware34.audio.mic-jack-detection': ContextEvent77('kernel', (), '\\b(?:snd_hda_intel|snd_hda_codec|hdaudio)\\b.{0,120}\\b(?:jack detection failed|jack sense failed)\\b', 'snd_hda_codec: jack detection failed', 'Een HDA-jackdetectiefout is in het kernellog geregistreerd.', 'Welke jack/headset betrokken is en een fysiek defect zijn niet vastgesteld.'),
    'hardware34.board.sensor-controller': ContextEvent77('kernel', (), '\\b(?:hwmon|i2c)\\b.{0,160}\\b(?:probe failed|failed to register hwmon)\\b', 'hwmon controller: probe failed', 'De kernel registreert een mislukte hardwaremonitorinitialisatie.', 'De bedoelde chip, firmwarestatus en fysieke controllerfout zijn niet aangetoond.'),
    'hardware34.display.panel-physical': ContextEvent77('kernel', (), '\\b(?:drm|amdgpu|i915|nouveau)\\b.{0,160}\\blink training failed\\b', 'drm: display link training failed', 'Een GPU-driver heeft een display-linktrainingfout gemeld.', 'Een paneel- of kabeldefect is niet bewezen; vergelijking buiten het OS ontbreekt.'),
    'hardware34.storage.ssd-not-present-firmware': ContextEvent77('kernel', (), '\\bnvme\\d{1,3}\\b.{0,130}\\b(?:failed to initialize|initialization failed|controller is down)\\b', 'nvme0: failed to initialize controller', 'De kernel heeft een NVMe-controllerinitialisatiefout vastgelegd.', 'UEFI-/firmware-inventaris en exacte SSD-identiteit zijn niet beschikbaar.'),
    'network.dns-problem': ContextEvent77('service', ('systemd-resolved',), '\\b(?:dns (?:query|transaction|request)|resolve(?:d|r)?)\\b.{0,170}\\b(?:failed|timed out|timeout|server failure)\\b', 'DNS query for example.invalid failed', 'De resolverdienst meldt een mislukte DNS-aanvraag.', 'De bedoelde hostnaam, netwerkvergelijking en toestemming zijn niet gekoppeld.'),
    'software35.applications.file-association': ContextEvent77('service', ('xdg-open', 'gio'), '\\b(?:no method available for opening|no application is registered to handle|no default application for)\\b', 'No application is registered to handle this MIME type', 'Een toepassingsstarter rapporteert geen geschikte MIME-handler.', 'Het bestandstype, de bedoelde app en de huidige desktopstandaard zijn niet gekoppeld.'),
    'software35.applications.segfault-plugin': ContextEvent77('service', ('systemd-coredump',), '\\bprocess\\s+\\d{1,10}\\s+\\([^)]{1,100}\\)\\s+(?:of user \\d+ )?dumped core\\b', 'Process 123 (example) dumped core', 'Een procescrash is als coredump geregistreerd.', 'Er is geen bewijs voor een plug-in als oorzaak of betrokken app-identiteit.'),
    'software35.containers.disk-space': ContextEvent77('service', ('podman', 'conmon', 'libpod'), '\\b(?:container storage|overlay storage|storage driver|graphroot)\\b.{0,160}\\bno space left on device\\b', 'container storage: no space left on device', 'Podman rapporteert een ENOSPC-fout tijdens een opslaghandeling.', 'Containernaam, quota, bestandsysteem en effectieve opslagoorzaak zijn onbekend.'),
    'software35.desktop.shortcut-conflict': ContextEvent77('service', ('kglobalacceld', 'kglobalaccel', 'kwin_wayland', 'kwin_x11'), '\\b(?:global )?(?:shortcut|key binding)\\b.{0,130}\\b(?:already in use|conflicts? with|is already assigned)\\b', 'Global shortcut already in use', 'Een toetsenbordsneltoetsconflict is door de desktopdienst gemeld.', 'Actieve toetscombinatie, applicatie en gebruikersconfiguratie zijn niet gekoppeld.'),
    'software35.desktop.wayland-clipboard': ContextEvent77('service', ('kwin_wayland', 'xdg-desktop-portal', 'wireplumber'), '\\bclipboard\\b.{0,150}\\b(?:transfer failed|data transfer failed|permission denied)\\b', 'Clipboard data transfer failed', 'Een Wayland-gerelateerde klembordoverdracht is mislukt.', 'Welke twee apps, MIME-data en gebruikershandeling betrokken zijn is onbekend.'),
    'software35.flatpak.file-access-denied': ContextEvent77('service', ('xdg-document-portal', 'xdg-desktop-portal'), '\\b(?:document portal|document access)\\b.{0,150}\\b(?:permission denied|access denied|request denied)\\b', 'Document portal request denied: permission denied', 'Een documentportal heeft een bestandstoegangsverzoek geweigerd.', 'Flatpak-ID, bestand, toestemming en actuele sandboxcontext zijn niet vastgesteld.'),
    'software35.network.firewall-blocks': ContextEvent77('kernel', (), '(?:\\[UFW BLOCK\\]|\\bIN=.{0,150}OUT=.{0,150}\\bDROP\\b)', '[UFW BLOCK] IN=eth0 OUT= SRC=192.0.2.4 DST=192.0.2.5', 'De kernel rapporteert een UFW-/firewalldropmelding.', 'De betrokken poort, app, richting en toepasselijke beleidsregel zijn niet gekoppeld.'),
    'software35.network.hostname-resolution': ContextEvent77('service', ('systemd-resolved',), '\\b(?:dns (?:query|transaction|request)|resolve(?:d|r)?)\\b.{0,170}\\b(?:failed|timed out|timeout|server failure)\\b', 'DNS query for example.invalid failed', 'De systeemresolver rapporteert een naamomzettingsfout.', 'De bedoelde hostnaam, /etc/hosts, NSS en toegestane resolutie zijn niet vergeleken.'),
    'software35.network.vpn-route': ContextEvent77('service', ('NetworkManager',), '\\b(?:vpn\\d{0,3}|tun\\d{1,3}|wg\\d{1,3})\\b.{0,130}\\b(?:failed to add route|route installation failed|failed to set route)\\b', 'vpn0 failed to add route', 'NetworkManager meldt een fout bij het instellen van een VPN-route.', 'Welke bestemming, verbinding en routetabel betrokken zijn, blijft onbekend.'),
    'system.flatpak-problem': ContextEvent77('service', ('flatpak', 'flatpak-system-helper'), '\\b(?:runtime\\s+\\S{1,100}\\s+(?:is )?not installed|unable to find required runtime)\\b', 'Unable to find required runtime', 'Flatpak rapporteert een ontbrekende runtime.', 'Het gekozen app-ID en de daadwerkelijke installatie-/startoorzaak zijn niet gekoppeld.'),
    'system.laptop-lid-suspend': ContextEvent77('service', ('systemd-logind',), '\\b(?:lid (?:closed|opened)|lid switch triggered)\\b', 'Lid closed.', 'logind registreert een lid-schakelaargebeurtenis.', 'Slaapstand, juiste apparaat, dockstatus en tijdsverband zijn niet bewezen.'),
    'system.login-one-user-fails': ContextEvent77('service', ('sddm', 'gdm', 'gdm3', 'lightdm'), '\\b(?:failed to (?:start|launch) (?:user )?session|session startup failed)\\b', 'Failed to start user session', 'Een displaymanager rapporteert een mislukte sessiestart.', 'Welke gebruiker, sessie en tegenovergesteld werkend account zijn niet bewezen.'),
    'virtualization.container-disk': ContextEvent77('service', ('podman', 'conmon', 'libpod'), '\\b(?:container storage|overlay storage|storage driver|graphroot)\\b.{0,160}\\bno space left on device\\b', 'container storage: no space left on device', 'Podman registreert een opslag-ENOSPC-melding.', 'De bedoelde container, volume, quota en onderliggend filesysteem zijn niet gekoppeld.'),
    'virtualization.vm-no-network': ContextEvent77('service', ('libvirtd', 'virtnetworkd'), '\\b(?:virtual network|network\\s+\\S{1,80})\\b.{0,150}\\b(?:failed to start|start failed|failed to create)\\b', 'Virtual network default failed to start', 'Libvirt rapporteert een mislukte virtuele-netwerkstart.', 'De betrokken VM, guestadapter, IP en connectiviteit zijn niet vastgesteld.'),
}

assert len(EVENTS77) == 24
COMPILED77 = {cid: re.compile(spec.pattern, re.IGNORECASE) for cid, spec in EVENTS77.items()}

def _event_matches(case_id: str, record: dict) -> bool:
    spec = EVENTS77[case_id]
    message = record.get('MESSAGE')
    if not isinstance(message, str) or len(message) > 4096:
        return False
    if spec.source == 'kernel':
        # A journalctl -k filter alone isn't a cryptographic attestation, but
        # _TRANSPORT=kernel must be recorded, not merely claimed in MESSAGE.
        if record.get('_TRANSPORT') != 'kernel':
            return False
    else:
        sender = _sender(record)
        if sender is None or sender.casefold() not in {s.casefold() for s in spec.senders}:
            return False
    return bool(COMPILED77[case_id].search(message[:1200]))

def probe_context_events77(host):
    system = _journal(host, SERVICE_EVENTS_JOURNAL)
    kernel = _journal(host, KERNEL_JOURNAL)
    facts = {}
    for case, spec in EVENTS77.items():
        journal = kernel if spec.source == 'kernel' else system
        facts['event77_' + case.replace('.', '_').replace('-', '_')] = (
            'unknown' if journal is None else
            'observed' if any(_event_matches(case, entry) for entry in journal)
            else 'not_observed_in_sample'
        )
    return _report('context_events77',
        ResultStatus.WARNING if 'observed' in facts.values() else
        ResultStatus.UNKNOWN if 'unknown' in facts.values() else ResultStatus.INFO,
        *(key + '=' + state for key, state in facts.items()),
        explanation=('Begrensde journald-steekproef van de huidige boot, met expliciete '
                     'afzendercontrole. Signalen zijn niet gekoppeld aan de doel-app, VM, '
                     'hardware of eerdere gebruikershandeling. Geen bewijs voor oorzaak, '
                     'geen automatisch herstel en geen bewijs dat andere storingen ontbreken.'))
