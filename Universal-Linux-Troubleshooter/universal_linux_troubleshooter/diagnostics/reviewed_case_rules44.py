"""Explicit case-reviewed *observational* evidence rules.

These rules deliberately establish ONLY a named local observation, not a root
cause or the applicability of a documented solution route. Each case is listed
individually so a future reviewer must consciously add scope and counterproof.
The words "supported" mean a signal was observed, not that the user's exact
symptom or any proposed cause is confirmed. A missing signal is UNKNOWN.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObservationRule:
    probe: str
    fact: str
    positive: str
    conclusion: str
    proof: str
    limitation: str


# There is no catch-all wildcard or fallback rule. Use stable case IDs only.
OBSERVATION_RULES: dict[str, ObservationRule] = {
    # Every GPU signal is limited to "a kernel GPU event was observed".
    'graphics.black-screen': ObservationRule('kernel_signals', 'gpu_reset', 'observed', 'GPU-resetmelding gevonden bij onderzoek naar zwart beeld', 'Een grafische driver meldde een reset/hang in het huidige kernel-log.', 'Een verband met het zwarte scherm, de timing en de oorzaak is nog niet vastgesteld.'),
    'graphics.game-stutter': ObservationRule('kernel_signals', 'gpu_reset', 'observed', 'GPU-resetmelding aanwezig bij onderzoek naar haperingen', 'Een GPU-reset of ring-time-out is vastgelegd.', 'Het event hoeft niet bij de betreffende game of het haperen te horen.'),
    'hardware.computer-freezes': ObservationRule('kernel_signals', 'gpu_reset', 'observed', 'GPU-resetgebeurtenis aangetroffen tijdens vastloperonderzoek', 'De kernel meldt een GPU-reset of ring-time-out.', 'De gebeurtenis bewijst niet dat deze de vastloper heeft veroorzaakt.'),
    'gaming.proton-game-no-start': ObservationRule('kernel_signals', 'gpu_reset', 'observed', 'GPU-resetmelding gevonden tijdens gameonderzoek', 'Er is een GPU-reset of ring-time-out geregistreerd.', 'Een Proton-probleem, tijdsverband of GPU-hardwaredefect is niet bewezen.'),
    'hardware34.gpu.vram-errors': ObservationRule('kernel_signals', 'gpu_vram_error', 'observed', 'Specifieke videogeheugenfout in GPU-log waargenomen', 'Het kernel-log bevat een expliciete GPU/VRAM-geheugenfout.', 'Een defect VRAM-component, herhaling en betrokken apparaat zijn nog niet bewezen.'),
    'hardware34.gpu.display-no-signal': ObservationRule('kernel_signals', 'gpu_reset', 'observed', 'GPU-resetmelding gevonden bij ontbrekend videosignaal', 'De grafische driver registreerde een reset/hang.', 'De fysieke monitorverbinding en eventuele tijdsrelatie zijn niet vastgesteld.'),
    'display.black-after-resume': ObservationRule('kernel_signals', 'gpu_reset', 'observed', 'GPU-resetmelding gevonden bij onderzoek na slaapstand', 'Het huidige kernellog bevat een GPU-reset.', 'Er is geen bewijs dat de reset tijdens resume optrad.'),
    # Kernel memory/OOM signals: warnings are not diagnosis of a bad DIMM.
    'applications.ram-low': ObservationRule('kernel_signals', 'oom_kill', 'observed', 'Linux heeft een proces wegens geheugentekort beëindigd', 'De kernel meldt een out-of-memory kill.', 'De schuldige toepassing, RAM-capaciteit en herhaling zijn niet vastgesteld.'),
    'hardware34.memory.ecc-corrected': ObservationRule('kernel_signals', 'ecc_ce', 'observed', 'Gecorrigeerde ECC-geheugenmelding aangetroffen', 'De kernel registreert een EDAC CE/corrected ECC-gebeurtenis.', 'Een enkele historische melding bewijst geen defecte DIMM en geen toename van de teller.'),
    'hardware34.cpu.mce-errors': ObservationRule('kernel_signals', 'cpu_mce', 'observed', 'CPU machine-check/gebeurtenis geregistreerd', 'Het kernellog bevat een expliciete machine-check/hardware-error-melding.', 'Een MCE identificeert niet automatisch een defecte CPU of de exacte gebeurtenisoorzaak.'),
    'hardware34.memory.xmp-expo-instability': ObservationRule('kernel_signals', 'ecc_ue', 'observed', 'Niet-corrigeerbare geheugengebeurtenis gevonden', 'De kernel registreert een ECC-UE-gebeurtenis.', 'Er is geen bewijs dat het XMP-/EXPO-profiel actief is of de oorzaak vormt.'),
    # PCIe health signals must never blame a motherboard, riser, slot or NVMe.
    'hardware34.board.pcie-correctable': ObservationRule('kernel_signals', 'pcie_corrected', 'observed', 'PCIe AER-gecorrigeerde fout waargenomen', 'De kernel registreert een PCIe AER corrected event.', 'Een herhaalde storing of een defect apparaat is hiermee niet bewezen.'),
    'hardware34.board.pcie-fatal': ObservationRule('kernel_signals', 'pcie_fatal', 'observed', 'Ernstige PCIe-fout gemeld', 'Een PCIe AER fatal/uncorrectable of DPC-gebeurtenis is geregistreerd.', 'De veroorzakende kaart, riser en oorzaak zijn niet onafhankelijk geïdentificeerd.'),
    'hardware34.other.device-controller-collision': ObservationRule('kernel_signals', 'pcie_fatal', 'observed', 'PCIe-foutmelding gevonden bij controlleronderzoek', 'De kernel meldt een ernstige PCIe-fout.', 'De fout is nog niet aan meerdere apparaten of dezelfde controller gekoppeld.'),
    'hardware34.other.external-gpu-dock': ObservationRule('kernel_signals', 'pcie_fatal', 'observed', 'Ernstige PCIe-foutmelding bij eGPU-onderzoek', 'De kernel meldt een ernstige PCIe-link/controllergebeurtenis.', 'Er is geen bewijs dat de eGPU-dock dit veroorzaakte of betrokken is.'),
    # Filesystem and OOM observations are never causal explanations by themselves.
    'hardware34.storage.drive-power-loss': ObservationRule('kernel_signals', 'fs_error', 'observed', 'Bestandssysteemfout gevonden tijdens opslagonderzoek', 'Er is een specifieke bestandssysteemfout vastgelegd.', 'Deze fout bewijst geen fysieke stroomonderbreking van de schijf.'),
    'system.disk-space-update': ObservationRule('kernel_signals', 'fs_error', 'observed', 'Bestandssysteemfout aangetroffen tijdens updateonderzoek', 'De kernel bevat een concrete bestandssysteemfout.', 'De fout toont niet aan dat ruimtegebrek of de update het probleem veroorzaakte.'),
    'hardware34.power.psu-random-reset': ObservationRule('kernel_signals', 'gpu_reset', 'observed', 'GPU-resetmelding gevonden bij onderzoek naar stroomuitval', 'De grafische driver registreerde een reset.', 'Een GPU-reset bewijst geen defecte voeding of fysiek stroomverlies.'),
    'applications.app-crash': ObservationRule('kernel_signals', 'oom_kill', 'observed', 'Linux heeft een proces beëindigd wegens geheugentekort', 'Een OOM-kill is vastgelegd in het kernel-log.', 'Of dit de genoemde toepassing was, moet uit procesidentiteit en timing blijken.'),
    'hardware34.power.battery-degraded': ObservationRule('power_supply', 'battery_wear', 'degraded', 'Gemeten batterijcapaciteit aanzienlijk onder ontwerpwaarde', 'De sysfs full-charge-capaciteit bedraagt hoogstens 60% van de ontwerpwaarde.', 'Laag gemeten accuvermogen bewijst geen zwelling, veiligheidsrisico of noodzaak voor onmiddellijke vervanging.'),
    'hardware.battery-drain': ObservationRule('power_supply', 'battery_wear', 'degraded', 'Verminderde gemeten batterijcapaciteit', 'De capaciteit bij volle lading ligt aanzienlijk onder de ontwerpwaarde.', 'Achtergrondbelasting en energieverbruik zijn niet gemeten; dit verklaart de gemelde gebruiksduur niet volledig.'),
    'hardware.battery-not-charging': ObservationRule('power_supply', 'battery_charge', 'not_charging', 'Batterij meldt momenteel niet opladen', 'De batterijstatus in sysfs staat op Not charging of Discharging.', 'Laaddrempels, netadapter, laadniveau en firmwarebeleid zijn nog niet gecorreleerd.'),
    'hardware34.power.ac-offline': ObservationRule('power_supply', 'ac', 'offline', 'Voedingsadapter meldt momenteel offline', 'Een eenduidige sysfs Mains-netadapter meldt online=0.', 'Niet bewezen is of de gebruiker een lader heeft aangesloten, of kabel/poort defect is.'),
    'hardware34.power.adapter-underpowered': ObservationRule('power_supply', 'ac', 'offline', 'Netadapter wordt momenteel niet als aangesloten gemeld', 'Sysfs meldt een offline netadapter.', 'De adapter is niet als ondergedimensioneerd of defect aangetoond.'),
    'hardware34.cpu.core-topology': ObservationRule('cpu_boot_limit', 'cpu_limit', 'active', 'Actieve CPU-opstartlimiet aangetroffen', 'Bootparameter maxcpus en de online/present CPU-set wijzen samen op een actieve beperking.', 'Firmware-SMT-keuzes, modellen en andere topologiebeperkingen zijn hiermee niet volledig vastgesteld.'),
}
