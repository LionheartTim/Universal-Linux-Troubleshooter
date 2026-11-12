"""Case-scoped, beginner-friendly physical connection checks (not auto-repairs).

Linux cannot establish cable/port failure from missing enumeration alone. The app
runs its approved read-only checks first; only safe, explicitly applicable,
user-operated comparisons are described here. These are *investigation steps*,
not confirmed causes, validated repair routes, or executable instructions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Kind = Literal['usb', 'usb_if_external', 'external_storage', 'external_storage_if_usb', 'dock', 'monitor', 'ethernet', 'audio_jack', 'audio_if_external', 'charging', 'internal_storage']

@dataclass(frozen=True)
class PhysicalPlan:
    kind: Kind
    title: str
    steps: tuple[str, ...]
    outcomes: tuple[str, ...]

    def describe(self) -> str:
        return ('VEILIGE FYSIEKE VERBINDINGSCONTROLE (GEEN BEWEZEN OORZAAK)\n'
                + self.title + '\n'
                + '\n'.join(f'{i}. {s}' for i, s in enumerate(self.steps, 1))
                + '\n\nMogelijke uitkomsten:\n'
                + '\n'.join('• ' + s for s in self.outcomes)
                + '\n\nStart daarna dezelfde diagnose opnieuw met "Investigate selected problem". '
                'De Troubleshooter leest de technische gegevens opnieuw; je hoeft zelf geen logs te bekijken. '
                'Een verbetering na het wisselen bewijst nog niet welk onderdeel defect is. '
                'Er worden geen wijzigingen uitgevoerd.')

# Intentional exact scope, not substring matching: software port conflicts,
# network firewalls and internal USB headers must never receive USB swaps.
USB_CASES = frozenset({
    'peripherals.usb-not-recognized',
    'hardware34.peripherals.usb-autosuspend',
    'hardware34.peripherals.usb-bandwidth',
    'hardware34.peripherals.usb-descriptor',
    'hardware34.other.printer-usb-power',
    'hardware34.other.scanner-usb',
    'hardware34.peripherals.audio-usb-dac',
    'hardware34.peripherals.webcam-uvc',
})
EXTERNAL_STORAGE_CASES = frozenset({
    'hardware34.storage.external-usb-bridge',
    'storage.external-drive-wont-mount',
})
DOCK_CASES = frozenset({
    'hardware34.peripherals.dock-power-cycle',
    'hardware.peripheral-thermal',
    'hardware34.other.external-gpu-dock',
    'hardware34.peripherals.thunderbolt-not-authorized',
})
MONITOR_CASES = frozenset({
    'display.second-monitor-missing',
    'graphics.second-monitor',
    'hardware34.display.edid-invalid',
    'hardware34.display.monitor-flicker',
    'hardware34.gpu.display-no-signal',
    'hardware34.gpu.hdmi-dp-audio',
})
ETHERNET_CASES = frozenset({
    'network.wired-link-no-carrier',
    'hardware34.peripherals.wired-link-flaps',
})
AUDIO_JACK_CASES = frozenset({'hardware34.audio.mic-jack-detection'})
CHARGING_CASES = frozenset({
    'hardware.battery-not-charging',
    'hardware34.power.ac-offline',
    'hardware34.power.adapter-underpowered',
    'hardware34.power.charging-port-damaged',
})
INTERNAL_STORAGE_CASES = frozenset({'hardware34.storage.sata-crc'})
# These problems MAY involve external USB devices, but may instead be wireless,
# built-in or software-only. The guides are explicitly conditional: no claim
# is made that USB is the user's connection type.
USB_IF_EXTERNAL_CASES = frozenset({
    'peripherals.gamepad-not-detected',
    'hardware34.peripherals.gamepad-controller',
    'hardware34.peripherals.hid-keyboard',
    'hardware34.peripherals.mouse-touchpad',
    'printing.printer-not-detected',
    'hardware34.peripherals.wireless-radio-missing',
    'audio.bluetooth-not-found',
})
STORAGE_IF_USB_CASES = frozenset({'storage.disk-not-found'})
AUDIO_IF_EXTERNAL_CASES = frozenset({
    'audio.mic-not-working', 'audio.sound-missing',
    'hardware34.audio.speaker-distortion',
})

_PLANS: dict[Kind, PhysicalPlan] = {
 'usb_if_external': PhysicalPlan('usb_if_external', 'Alleen als dit een EXTERN USB-apparaat is: andere poort en kabel',(
     'Is het apparaat ingebouwd of uitsluitend via Bluetooth/Wi-Fi verbonden? Sla deze fysieke USB-stappen over; ze zijn dan niet toepasselijk.',
     'Is het wel een extern USB-apparaat: stop lopende overdrachten en sluit het indien veilig direct aan op een andere passende USB-poort van de computer, niet via dezelfde hub.',
     'Gebruik eventueel een bekende, passende USB-DATAkabel of andere geschikte ontvanger als die verwisselbaar is; niet forceren en geen ingebouwde onderdelen losmaken.',
     'Bij een printer: onderbreek eerst de lopende taak; vergelijk USB-verbinding alleen als de printer werkelijk via USB is aangesloten.',
 ),(
     'Werkt het via een andere geschikte poort of kabel? Het eerdere pad is verdacht, maar geen defect apparaat of poort is bewezen.',
     'Blijft het probleem? Driver, machtigingen, firmware, stroomvoorziening en apparaat zijn nog mogelijke oorzaken.',
 )),
 'external_storage_if_usb': PhysicalPlan('external_storage_if_usb','Alleen bij externe USB-opslag: eerst gegevens veiligstellen',(
     'Is het een interne SSD/HDD? Ga NIET met USB-poorten experimenteren; deze aanwijzingen zijn niet toepasselijk.',
     'Bij I/O-fouten, klikgeluid of belangrijke gegevens: STOP met herhaald aansluiten, bescherm eerst je gegevens.',
     'Bij een normale, nog toegankelijke externe USB-schijf: koppel veilig af via je bestandsbeheerder en probeer daarna een andere passende USB-poort direct op de computer.',
     'Gebruik zo nodig een bekende, juiste USB-datakabel; forceer niets en gebruik uitsluitend ondersteunde voeding.',
 ),(
     'Als een andere poort werkt, is het eerdere verbindingspad verdacht; de schijf is daarmee niet gezond bewezen.',
     'Bij aanhoudende I/O-fouten: geen nieuwe experimenten; bescherm gegevens en onderzoek opslaggezondheid.',
 )),
 'audio_if_external': PhysicalPlan('audio_if_external','Alleen bij externe microfoon of luidsprekers: aansluiting vergelijken',(
     'Bij ingebouwde luidsprekers of microfoon: sla de kabel- en poortcontrole over; die is dan niet toepasselijk.',
     'Bij een extern USB-audioapparaat: probeer als dat veilig kan een andere geschikte USB-poort direct op de computer in plaats van dezelfde hub.',
     'Bij een externe 3,5-mm-aansluiting: controleer de juiste jack en probeer alleen een geschikte bekende werkende kabel of headset; forceer niets.',
     'De Troubleshooter onderzoekt daarna zelf opnieuw de audioapparaten en -services, zonder dat jij logs hoeft te lezen.',
 ),(
     'Werkt een andere aansluiting? Kabel of poort is mogelijk betrokken, maar het is geen bewezen defect.',
     'Werkt het nergens? Audio-uitvoerselectie, profiel, permissies en het externe apparaat blijven mogelijke oorzaken.',
 )),
 'usb': PhysicalPlan('usb','Extern USB-apparaat, kabel, USB-poort of hub',(
     'Kijk alleen naar het EXTERNE apparaat. Gebruik geen interne USB-header, open de kast niet en trek geen aangesloten interne onderdelen los.',
     'Als het veilig kan: sluit het apparaat rechtstreeks aan op een andere, passende USB-poort van de computer (dus niet via dezelfde hub of dock). Gebruik geen kracht en beschadigde connectoren niet.',
     'Heeft het apparaat een afneembare kabel? Probeer eventueel een bekende, werkende USB-datakabel van het juiste type; sommige kabels kunnen alleen opladen.',
     'Als een hub of dock gebruikt werd: vergelijk een directe aansluiting met de hub. Bij apparaten die extra voeding nodig hebben: gebruik alleen de voorgeschreven voeding.',
 ),(
     'Werkt het apparaat op een andere poort? Dan is de eerste USB-poort of aansluitroute VERDACHT, niet bewezen defect.',
     'Werkt het rechtstreeks maar niet via de hub? Dan is de hub-/voedingsroute verdacht.',
     'Werkt het op geen enkele geschikte poort? Dan blijven kabel, apparaat, voeding, controller en software mogelijke oorzaken.',
 )),
 'external_storage': PhysicalPlan('external_storage','Externe USB-schijf: eerst gegevens beschermen',(
     'Bij I/O-fouten, tikkende schijf, herhaalde uitval of onvervangbare gegevens: STOP met wisselen en herhaal geen belastende tests. Bescherm de gegevens en vraag zo nodig deskundige hulp.',
     'Is de schijf nog toegankelijk en zijn er geen waarschuwingssignalen? Sla werk op en gebruik eerst de veilige ontkoppelfunctie in je bestandsbeheerder; verplaats nooit een schijf tijdens schrijven.',
     'Probeer daarna voorzichtig een andere geschikte USB-poort DIRECT op de computer, zonder hub of dock. Gebruik indien mogelijk ook een passende, bekende goede datakabel.',
     'Sluit niet aan op ongeschikte voeding of connectoren; forceer niets.',
 ),(
     'Werkt de schijf op een andere poort? De eerste poort/hub/aansluitroute verdient aandacht; dat bewijst geen defect.',
     'Blijft de schijf wegvallen of toont Linux I/O-fouten? Niet blijven wisselen; gegevensbescherming gaat voor verdere diagnose.',
 )),
 'dock': PhysicalPlan('dock','Dock / USB-C / Thunderbolt: poort, kabel en hub isoleren',(
     'Stop lopende bestandskopieën en koppel aangesloten opslagapparaten eerst veilig los. Trek geen kabel los tijdens firmware-updates of laden met een beschadigde connector.',
 'Controleer of de dockkabel volledig vastzit. Probeer alleen als veilig en compatibel een andere geschikte USB-C/Thunderbolt-poort en eventueel een gecertificeerde kabel met voldoende data-/video-ondersteuning.',
 'Vergelijk, indien mogelijk, het betrokken apparaat rechtstreeks op de computer met dezelfde aansluiting via het dock. Gebruik uitsluitend de juiste originele/ondersteunde voeding.',
 ),(
     'Werkt de directe verbinding wel? Het dock, de dockkabel, voeding of de compatibiliteit is verdacht; nog niet bewezen defect.',
     'Werkt het op geen geschikte poort? USB-C-alternatieve modi, Thunderbolt-autorisatie, driver en apparaat blijven mogelijke oorzaken.',
 )),
 'monitor': PhysicalPlan('monitor','Beeldschermverbinding: kabel, ingang en videopoort',(
     'Controleer eerst of de monitor stroom heeft en de juiste HDMI/DisplayPort-ingang gekozen is.',
     'Als dat veilig kan: sluit de videokabel opnieuw aan, probeer een bekende werkende HDMI/DisplayPort-kabel of een andere geschikte uitgang op dezelfde grafische kaart en een bijpassende ingang op de monitor.',
     'Gebruik geen converter of adapter waarvan de vereiste videospecificatie onzeker is. Verander geen interne GPU-aansluitingen.',
 ),(
     'Werkt het op een andere videopoort of met een andere kabel? Dan is het eerder gebruikte pad verdacht, maar de oorzaak is nog niet bewezen.',
     'Blijft het scherm weg? Onderzoek dan ook monitormodus, EDID, GPU-driver en hardware zonder een willekeurige driverwissel.',
 )),
 'ethernet': PhysicalPlan('ethernet','Bekabeld netwerk: netwerkkabel en router-/switchpoort',(
     'Controleer of de netwerkkabel goed vastzit en probeer, indien beschikbaar, een bekende werkende Ethernetkabel.',
     'Probeer een andere vrije LAN-poort van dezelfde router of switch als dat veilig en toegestaan is. Gebruik geen onbekende WAN-, PoE- of beheerpoort.',
     'Laat de Troubleshooter daarna opnieuw de linkstatus en netwerkconfiguratie controleren.',
 ),(
     'Komt de verbinding terug na kabel- of poortwissel? Het oorspronkelijke verbindingspad is verdacht, maar nog niet bewezen defect.',
     'Blijft de link actief maar komt er geen IP-adres? Dan volgt het IP-/DHCP-spoor, niet meteen een kabeldiagnose.',
 )),
 'audio_jack': PhysicalPlan('audio_jack','Analoge headset: jack, aansluiting en adapter',(
     'Controleer of de headsetstekker helemaal in de juiste audioaansluiting zit en of het een passende microfoon-/headsetcombinatie is.',
     'Als er een andere geschikte audio-ingang of bekende werkende headset beschikbaar is, vergelijk daarmee. Forceer geen connector.',
 ),(
     'Werkt een andere ingang wel? De eerste jack of configuratie verdient onderzoek.',
     'Blijft de microfoon uit? Ook audio-profiel, toestemming of headset kan de oorzaak zijn.',
 )),
 'charging': PhysicalPlan('charging','Opladen: kabel en externe voedingsaansluiting',(
     'Bij oververhitting, brandgeur, vonken, verkleuring of beschadigde laadpoort: STOP met aansluiten en gebruik de lader niet; laat deze nakijken.',
     'Anders: controleer op zichtbare schade en of alleen de voor het apparaat bedoelde originele/ondersteunde kabel en voeding stevig zijn aangesloten.',
     'Bij USB-C-laden: probeer uitsluitend een door de fabrikant als LAADPOORT ondersteunde andere USB-C-poort, als die aanwezig is; niet iedere USB-C-poort kan laden.',
 ),(
     'Laden via een andere ondersteunde poort is een aanwijzing voor een aansluitprobleem, niet het bewijs van een defecte poort.',
     'Blijft opladen uit? Ook voeding, accu, firmware en laadregeling blijven mogelijke oorzaken.',
 )),
 'internal_storage': PhysicalPlan('internal_storage','Interne SATA-gegevenskabel (alleen veilige vervolgstap)',(
     'Bij toenemende I/O-fouten eerst gegevens beschermen. Maak geen interne kast open terwijl de computer ingeschakeld is.',
     'Alleen als je bekwaam bent en het apparaat veilig spanningsvrij is: laat een SATA-datakabel en aansluiting controleren of vervangen door een bekende goede. Bij twijfel laat je dit door een deskundige doen.',
 ),(
     'Verandering na kabelvervanging is een aanwijzing voor het verbindingspad, niet automatisch bewijs dat de schijf gezond is.',
 )),
}

_CASE_KIND: dict[str,Kind] = {}
for kind, ids in (('usb', USB_CASES), ('usb_if_external',USB_IF_EXTERNAL_CASES),
                  ('external_storage_if_usb',STORAGE_IF_USB_CASES), ('audio_if_external',AUDIO_IF_EXTERNAL_CASES),
                  ('external_storage',EXTERNAL_STORAGE_CASES),
                  ('dock',DOCK_CASES), ('monitor',MONITOR_CASES),
                  ('ethernet',ETHERNET_CASES), ('audio_jack',AUDIO_JACK_CASES),
                  ('charging',CHARGING_CASES), ('internal_storage',INTERNAL_STORAGE_CASES)):
    for cid in ids:
        if cid in _CASE_KIND:
            raise RuntimeError(f'Physical guide conflict: {cid}')
        _CASE_KIND[cid] = kind


def guide_for_case(case_id: str) -> PhysicalPlan | None:
    """Exact case ID only: no user text, model output or logs choose a guide."""
    kind = _CASE_KIND.get(case_id)
    return _PLANS[kind] if kind else None


def guided_case_ids() -> frozenset[str]:
    return frozenset(_CASE_KIND)
