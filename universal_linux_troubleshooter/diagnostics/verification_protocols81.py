"""Source-authored acceptance protocols for ten contextual cases.

These are case-specific, user-safe *requirements*, NOT event rules or
repair authorizations. They say exactly which independent observation and
counterexample are needed before an actual Linux machine can be certified.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class FieldProtocol81:
    independently_needed: str
    countercheck: str
    safe_procedure: str
    completion: str

PROTOCOLS81 = {
 'hardware34.gpu.gpu-not-enumerated': FieldProtocol81(
  'Vastgelegde verwachte PCI-GPU (vendor/device of firmwarefoto) naast een Linux PCI- en kernel-sysfs-opname van hetzelfde PCI-slot.',
  'Controleer BIOS/UEFI-verberging, hardware-uitschakeling en of het apparaat buiten de actieve kernel/sandbox werkelijk bestaat.',
  'Kies het exacte PCI-slot en voer Run selected uit. Vergelijk, indien nodig, de fysieke GPU en BIOS/UEFI-inventaris op het echte systeem. Alleen kijken; geen firmwarewijziging.',
  'De identiteit en ontbrekende/aanwezige enumeratie zijn onafhankelijk bevestigd; na een vrijwillige correctie wordt op hetzelfde apparaat opnieuw gemeten.'),
 'hardware34.memory.memory-channel': FieldProtocol81(
  'Werkelijke DIMM-slotindeling en kanaalindeling uit moederbordhandleiding/UEFI plus een betrouwbare, bevoegde SMBIOS-uitlezing.',
  'SMBIOS kan fout/onvolledig zijn; benchmarks en EDAC-tags bewijzen geen fysiek single-/dual-channel-gebruik.',
  'Vergelijk het exacte moederbord en DIMM-posities via de officiële handleiding en firmware-interface. Niet blind herplaatsen of het apparaat onder spanning openen.',
  'Slot- en kanaalbezetting zijn bevestigd door hardwaredocumentatie en een gecontroleerde praktijkmeting.'),
 'hardware34.power.charging-port-damaged': FieldProtocol81(
  'Waarneming van laden/ontladen met bekende goede compatibele voeding, kabel en poort; eventuele kernel-power_supply-sensor is slechts aanvullend.',
  'Een online/netstroomflag bewijst geen intacte laadpoort; connector- of kabelbeschadiging kan veiligheidsrisico geven.',
  'Stop bij warmte, vonken of zichtbare schade. Vergelijk zonder demontage de officiële voeding en een bekende goede kabel/poort; laat beschadiging professioneel beoordelen.',
  'Hetzelfde defect is reproduceerbaar geïsoleerd tot de poort, met veilige uitsluiting van kabel en voeding.'),
 'software35.appimage.update-source-change': FieldProtocol81(
  'Een onafhankelijk geauthenticeerde originele release met handtekening of checksum, en de oude plus nieuwe AppImage-identiteit.',
  'Een door de gebruiker ingevoerde hash is geen cryptografisch vertrouwde bronidentiteit en een verschil bewijst geen bronwisseling.',
  'Bewaar beide bestanden. Controleer de officiële release/herkomst via de uitgever en vergelijk de optionele alleen-lezen hash; voer geen onbekende AppImage uit.',
  'Beide versies en hun geauthenticeerde uitgevende bron zijn vastgesteld en een wijziging is aantoonbaar reproduceerbaar.'),
 'software35.desktop.font-missing': FieldProtocol81(
  'Exacte vereiste lettertypefamilie, fontconfig-inventaris in de betrokken gebruikerssessie en uitvoer uit de getroffen applicatie.',
  'Aanwezigheid in fc-list bewijst niet dat sandbox, fontfallback of applicatie de font werkelijk gebruikt.',
  'Vul de exacte familie in en controleer de inventaris. Heropen de app met hetzelfde document en vergelijk een ongewijzigde rendering; installeer geen onbekende fonts.',
  'Hetzelfde document toont de gereproduceerde fout vóór en verdwijning ná een gecontroleerde fontcorrectie.'),
 'software35.desktop.scaling-blur': FieldProtocol81(
  'Screenshots/pixelvergelijking van dezelfde app bij exact dezelfde content, schaal en renderbackend, plus compositorinstellingen.',
  'Een niet-integer schermschaal bewijst geen blur: softwareopbouw, XWayland en app-toolkit kunnen een andere oorzaak zijn.',
  'Controleer binnen de eigen bureaubladinstellingen de app op native schaal en oorspronkelijke schaal, zonder de rest van de sessie blijvend aan te passen.',
  'Hetzelfde beeld vertoont reproduceerbaar verschil bij één geïsoleerde schaal-/renderinstelling, met succesvolle hertest.'),
 'software35.development.path-command-shadowed': FieldProtocol81(
  'Exacte executable vanuit de daadwerkelijk getroffen host-shell of startende app, inclusief PATH en eventuele alias/functie.',
  'De PATH van het Troubleshooter-proces kan anders zijn, zeker vanuit Flatpak; twee gelijknamige binaries bewijzen geen verkeerde uitvoering.',
  'Controleer de werkelijk actieve applicatie- of host-shellomgeving. Vergelijk uitsluitend verwachte executable-locaties; voer geen onbekend programma uit.',
  'Vóór/na zijn de daadwerkelijk door de getroffen shell gekozen binaries bevestigd en het startsymptoom hergetest.'),
 'software35.development.venv-wrong-python': FieldProtocol81(
  'Interpreterpad en sys.prefix uit het werkelijk getroffen Python-proces vergeleken met de gekozen venv-configuratie.',
  'Het pip-script of een venv-map alleen bewijst niet welke Python de app uitvoert of welke modules worden geïmporteerd.',
  'Selecteer de originele venv-map. Controleer in het eigen project op veilige wijze welk Python-proces werkelijk draait, zonder packages te installeren.',
  'De echte projectinterpreter en importomgeving zijn bevestigd en de fout herhaalt zich niet na een doelgerichte correctie.'),
 'software35.flatpak.corrupt-user-data': FieldProtocol81(
  'Dezelfde Flatpak-app, dezelfde versie, bewaarde gebruikersdata en een door de gebruiker gecontroleerde reproduceertest in een schoon profiel.',
  'Een app-crash of bestaande ~/.var/app-map bewijst geen corrupte gebruikersdata. Privégegevens worden niet automatisch gelezen.',
  'Maak eerst een betrouwbare back-up. Test daarna uitsluitend met toestemming in een apart schoon app-profiel; verwijder nooit de originele appdata op basis van één symptoom.',
  'De klacht volgt reproduceerbaar dezelfde bewaarde data en verdwijnt in een schoon profiel bij verder gelijke omstandigheden.'),
 'software35.packages.app-source-mismatch': FieldProtocol81(
  'Exacte app-ID, geïnstalleerde scope, werkelijke remote/commit en dezelfde uitgevoerde applicatie; alternatieve RPM/DEB/AppImage identificatie apart.',
  'Dubbele Flatpak-IDs of verschillende remotes bewijzen niet dat dezelfde app uit de verkeerde bron is gestart.',
  'Vul de exacte Flatpak-app-ID in. Vergelijk USER en SYSTEM broninformatie; inspecteer de werkelijk uitgevoerde bron vóór wijzigingen. Gebruik desgewenst ULSM voor read-only inventaris.',
  'De bedoelde en daadwerkelijk gestarte bron zijn onafhankelijk aangetoond; na een door de gebruiker gekozen wijziging controleert Rescan dit opnieuw.'),
}
assert len(PROTOCOLS81) == 10

def explain_unverified81(case_id: str) -> str:
    item = PROTOCOLS81.get(case_id)
    if item is None:
        return ''
    return ('Nog vereist onafhankelijk bewijs: ' + item.independently_needed + '\n'
        'Tegenbewijs/valkuil: ' + item.countercheck + '\n'
        'Veilig vervolg (geen reparatievrijgave): ' + item.safe_procedure + '\n'
        'Acceptatiecriterium vóór afsluiten: ' + item.completion + '\n'
        'Geen veldtest, oorzaaksbewijs of geautoriseerde automatische reparatie.')
