"""Device-specific beginner guides using the EXISTING diagnostic trees.

These are symptom entry points and physical/user-observable retest instructions,
not additional proven diagnosis cases or machine-executable solutions. Each
entry maps to one existing hardware tree, which collects read-only evidence.
No permission to run commands, reconfigure hardware, or make repairs is added.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PeripheralTopic:
    key: str
    title: str
    case_id: str
    search_terms: tuple[str, ...]
    precautions: tuple[str, ...]
    comparison: tuple[str, ...]
    interpretations: tuple[str, ...]

    def describe(self) -> str:
        """English wording in every entry point, including legacy callers.

        Data and mappings remain unchanged. The English guide is the public
        presentation; the original v48 metadata is retained for provenance.
        """
        from .topic_catalog127 import guide_for_topic
        return guide_for_topic(self.key, self.case_id).describe()


def _topic(key, title, case_id, terms, precautions, comparison, interpretations):
    return PeripheralTopic(key, title, case_id, tuple(terms), tuple(precautions), tuple(comparison), tuple(interpretations))


TOPICS = (
    _topic('mouse_wired', 'Mouse · wired / USB', 'hardware34.peripherals.mouse-touchpad',
        ('muis', 'mouse', 'cursor', 'usb mouse', 'muisknop', 'scrollwiel'),
        ('Stop lopende handelingen als de aanwijzer onverwacht beweegt.',),
        ('Controleer of de USB-stekker goed vastzit en probeer veilig een andere geschikte USB-poort direct op de computer, buiten de hub om.',
         'Probeer indien mogelijk een andere bekende werkende muis op dezelfde aansluiting. Controleer een afneembare datakabel zonder iets te forceren.'),
        ('Werkt dezelfde muis elders wel? De oorspronkelijke aansluitroute is verdacht; een defecte poort is niet bewezen.',
         'Werkt geen muis? Ook de USB-controller, bureaubladsessie of software blijft mogelijk.')),
    _topic('mouse_wireless', 'Mouse · wireless / dongle / Bluetooth', 'hardware34.peripherals.mouse-touchpad',
        ('draadloze muis', 'wireless mouse', 'dongle', 'receiver', 'bluetooth mouse', 'batterij muis'),
        ('Een draadloze muis kan een USB-ontvanger of Bluetooth gebruiken; deze paden zijn niet hetzelfde.',),
        ('Controleer de aan/uitstand en vervang of laad zo nodig de batterij volgens de handleiding.',
         'Bij een losse USB-ontvanger: probeer een andere USB-poort direct op de computer, niet via dezelfde hub; bewaar de originele ontvanger.',
         'Bij Bluetooth: controleer of de muis in de juiste koppelmodus staat; bevestig zelf of opnieuw koppelen gewenst is.'),
        ('Werkt de ontvanger elders? Dan is het eerste aansluitpad mogelijk betrokken.',
         'Bluetooth-uitval bewijst geen defecte USB-poort; de radio of koppeling kan een rol spelen.')),
    _topic('keyboard_wired', 'Keyboard · USB / missing keys', 'hardware34.peripherals.hid-keyboard',
        ('toetsenbord', 'keyboard', 'key stuck', 'key repeat', 'toets werkt niet'),
        ('Bij herhaald onbedoeld typen: beëindig eerst veilig de invoer; voer geen gevoelige wachtwoorden in tijdens de test.',),
        ('Controleer de externe USB-aansluiting en probeer, indien mogelijk, direct een andere geschikte USB-poort.',
         'Gebruik een bekend werkend extern toetsenbord ter vergelijking. Een enkele niet-werkende toets kan ook een lay-out- of mechanisch probleem zijn.'),
        ('Werkt een ander toetsenbord? Het eerste toetsenbord of zijn kabel verdient aandacht, maar is niet bewezen defect.',
         'Een andere toetsenbordindeling of toegankelijkheidsfunctie kan verkeerde toetsen verklaren.')),
    _topic('keyboard_wireless', 'Keyboard · wireless / receiver', 'hardware34.peripherals.hid-keyboard',
        ('wireless keyboard', 'bluetooth keyboard', 'draadloos toetsenbord', 'keyboard dongle'),
        ('Behoud een werkende manier om in te loggen voordat je draadloze invoerapparaten opnieuw koppelt.',),
        ('Controleer aan/uitstand, batterij en of het toetsenbord bij de juiste ontvanger of Bluetooth-host hoort.',
         'Bij een aparte USB-ontvanger: probeer eventueel een andere geschikte poort direct op de computer.',
         'Bij Bluetooth: controleer de koppelstatus; wis geen werkende koppeling zonder een alternatieve invoermethode.'),
        ('Werkt alleen een andere ontvangerpositie? Storing of het verbindingspad kan meespelen.',
         'Geen reactie is geen bewijs van defect toetsenbord of controller.')),
    _topic('touchpad', 'Touchpad · built-in laptop', 'hardware34.peripherals.mouse-touchpad',
        ('touchpad', 'trackpad', 'laptop muis', 'gesture', 'aanraakvlak'),
        ('Een ingebouwd touchpad is geen extern USB-apparaat; koppel niets intern los.',),
        ('Controleer of een touchpad-toets of ondersteunde laptopinstelling het touchpad heeft uitgeschakeld.',
         'Gebruik zo nodig tijdelijk een externe muis voor bediening; de Troubleshooter kan daarna de beschikbare invoergegevens opnieuw lezen.'),
        ('Een werkende externe muis bewijst niet dat het touchpad stuk is.',
         'Touchpadinstellingen, driver, sessie en hardware blijven afzonderlijke mogelijkheden.')),
    _topic('headphones_jack', 'Headphones · 3.5 mm / headset jack', 'hardware34.audio.mic-jack-detection',
        ('hoofdtelefoon', 'koptelefoon', 'headphones', 'headset', '3.5 mm', 'jack', 'microfoon jack'),
        ('Begin met laag volume om plotseling hard geluid te voorkomen.',),
        ('Controleer de juiste 3,5-mm aansluiting en of de stekker volledig, zonder kracht, aangesloten is.',
         'Een combinatie-headset (TRRS) en aparte microfoon-/hoofdtelefoonpoorten kunnen een geschikte splitter vereisen.',
         'Vergelijk indien beschikbaar met een bekende werkende headset of een andere geschikte ingang.'),
        ('Werkt een andere headset? De eerste headset of kabel is verdacht, maar niet bewezen defect.',
         'Geen microfoonsignaal kan ook door een verkeerd invoerprofiel of ontbrekende toestemming komen.')),
    _topic('headphones_usb', 'Headphones · USB headset / DAC', 'hardware34.peripherals.audio-usb-dac',
        ('usb headset', 'usb hoofdtelefoon', 'usb koptelefoon', 'usb headphones', 'dac', 'audio interface'),
        ('Begin met laag luistervolume. Stop lopende opnames of gesprekken voordat je het apparaat losmaakt.',),
        ('Sluit de headset of USB-DAC direct aan op een geschikte andere USB-poort, zonder dezelfde hub.',
         'Probeer alleen bij afneembare kabels een geschikte bekende USB-datakabel; een laadkabel is soms ongeschikt.',
         'De Troubleshooter controleert daarna de zichtbare audioapparaten opnieuw.'),
        ('Verandering per poort duidt op de aansluitroute, niet op een bewezen poortdefect.',
         'Een correcte USB-verbinding bewijst nog geen juiste audio-uitvoer, invoerprofiel of audiorechten.')),
    _topic('headphones_bluetooth', 'Headphones · Bluetooth audio', 'audio.bluetooth-audio',
        ('bluetooth hoofdtelefoon', 'bluetooth koptelefoon', 'wireless headphones', 'oortjes', 'earbuds', 'buds'),
        ('Begin met laag volume; onderbreek een gesprek of opname voordat je het audioapparaat wisselt.',),
        ('Controleer batterij, afstand en of de hoofdtelefoon met de juiste computer verbonden is.',
         'Als het geluid hapert: probeer een kortere afstand en minder obstakels zonder de hele Bluetooth-configuratie te wissen.',
         'Bij een microfoonprobleem kan het Bluetooth-profiel andere audiokwaliteit bieden; een profielwissel gebeurt alleen met jouw keuze.'),
        ('Een stabielere verbinding op kortere afstand is een aanwijzing voor bereik/interferentie, geen bewijs van defecte hardware.',
         'Audioprofiel, radio, codec en applicatie blijven alternatieven.')),
    _topic('microphone', 'Microphone · USB / built-in', 'audio.mic-not-working',
        ('microphone', 'microfoon', 'usb mic', 'ingebouwde mic', 'mic mute'),
        ('Leg niet onbedoeld privégesprekken vast. De Troubleshooter maakt geen audio-opname.',),
        ('Bij een externe USB-microfoon: controleer of mute uit staat en probeer zo nodig een andere geschikte USB-poort.',
         'Bij een ingebouwde microfoon: sla externe kabel- en poortstappen over.',
         'Een opname- of toestemmingstest blijft een bewuste keuze van de gebruiker; de Troubleshooter leest alleen beschikbare apparaatstatus.'),
        ('Geen audiogegevens betekent niet automatisch een kapotte microfoon.',
         'Mute, gekozen bron, app-toestemming en hardware zijn afzonderlijke verklaringen.')),
    _topic('webcam', 'Webcam · USB / privacy shutter', 'hardware34.peripherals.webcam-uvc',
        ('webcam', 'camera', 'usb camera', 'privacy shutter', 'videobellen'),
        ('De Troubleshooter activeert geen camera en maakt geen foto of opname.',),
        ('Controleer de fysieke privacyschuif of cameraknop.',
         'Bij een externe USB-camera: probeer indien veilig een andere geschikte USB-poort direct op de computer.',
         'Bij een ingebouwde laptopcamera: sla fysieke USB-stappen over.'),
        ('Een dichte privacyschuif verklaart een zwart beeld maar niet noodzakelijk het ontbreken van het apparaat.',
         'App-toegang, portal, driver en apparaat zijn mogelijk zonder bewezen defect.')),
    _topic('printer', 'Printer · USB disconnecting', 'hardware34.other.printer-usb-power',
        ('printer', 'usb printer', 'afdrukken', 'print spooler'),
        ('Onderbreek lopende afdruktaken voor je de kabel losmaakt. Raak hete onderdelen niet aan.',),
        ('Alleen bij een USB-printer: vergelijk een andere geschikte USB-datakabel en een directe poort zonder hub.',
         'Bij een netwerkprinter: geen USB-kabelstappen uitvoeren; netwerkverbinding en printerstatus zijn aparte routes.'),
        ('Werkt een directe USB-verbinding? Het eerdere aansluitpad verdient onderzoek.',
         'Printwachtrij of driverfouten worden hierdoor niet uitgesloten.')),
    _topic('scanner', 'Scanner · USB / power', 'hardware34.other.scanner-usb',
        ('scanner', 'scanapparaat', 'document scanner'),
        ('Onderbreek een actieve scan en schakel alleen volgens de apparaatvoorschriften uit.',),
        ('Bij een externe USB-scanner: controleer de voorgeschreven voeding en probeer een directe geschikte USB-poort.',
         'Probeer bij een afneembare kabel eventueel een bekende werkende datakabel.'),
        ('USB-herkenning bewijst niet dat de scansoftware het apparaat ondersteunt.',
         'Bij aanhoudende uitval blijven voeding, driver, kabel en scanner mogelijk.')),
    _topic('gamepad', 'Game controller · gamepad / receiver', 'hardware34.peripherals.gamepad-controller',
        ('controller', 'gamepad', 'joystick', 'gaming pad'),
        ('Stop actieve besturing in games voordat je een controller omplugt.',),
        ('Bij bedraad USB: probeer een andere geschikte USB-poort direct op de computer; controleer de datakabel.',
         'Bij draadloos: controleer batterij en de juiste ontvanger of Bluetooth-koppeling.',
         'Herstart geen spel of verwijder geen gameprofielen zonder noodzaak.'),
        ('Wordt de controller wel gezien maar reageert alleen één game niet, onderzoek dan spelinstellingen.',
         'De poort of controller is niet op basis van alleen een verbindingsfout defect bewezen.')),
    _topic('dock', 'Dock · USB-C / Thunderbolt', 'hardware34.peripherals.dock-power-cycle',
        ('dock', 'usb-c hub', 'thunderbolt dock', 'hub', 'port replicator'),
        ('Stop externe kopieën en koppel opslag veilig af voordat je een dock losmaakt.',),
        ('Probeer een geschikte gecertificeerde kabel en uitsluitend een poort met de vereiste USB-C/Thunderbolt-mogelijkheden.',
         'Vergelijk aangesloten apparaten rechtstreeks met de verbinding via het dock; gebruik de ondersteunde stroomadapter.'),
        ('Een directe verbinding die wel werkt maakt het dockpad verdacht, niet bewezen defect.',
         'USB-C-videomodi, Thunderbolt-autorisatie en stroomverbruik blijven mogelijke oorzaken.')),
    _topic('touchscreen', 'Touchscreen · touch input', 'hardware34.peripherals.touchscreen',
        ('touchscreen', 'aanraakscherm', 'touch display', 'digitizer'),
        ('Maak geen ingebouwde connectors los. Gebruik geen onnodige herkalibratie of factory reset.',),
        ('Controleer of het scherm zelf correct werkt terwijl de aanraking niet reageert.',
         'Bij een extern touchscreen kan een afzonderlijke USB-datakabel nodig zijn naast HDMI/DisplayPort; sluit alleen passende kabels aan.'),
        ('Werkend beeld bewijst niet dat de touch-interface werkt.',
         'De driver, compositor, USB-touchverbinding en digitizer blijven mogelijke oorzaken.')),
    _topic('fingerprint', 'Fingerprint reader · unavailable', 'hardware34.peripherals.fingerprint-sensor',
        ('fingerprint', 'vingerafdruk', 'biometric reader', 'biometrie'),
        ('Verwijder geen bestaande inlogmethode en verander geen authenticatiebeleid tijdens een diagnose.',),
        ('Bij een externe USB-lezer: controleer de directe USB-aansluiting en probeer indien veilig een andere geschikte poort.',
         'Bij een ingebouwde sensor: geen kast openen en geen USB-poortstappen.'),
        ('Herkenning door Linux bewijst niet dat een sensor door de biometrische software wordt ondersteund.',
         'Compatibiliteit, firmware, permissies en hardware zijn mogelijk.')),
    _topic('usb_storage', 'External USB storage · disconnects', 'hardware34.storage.external-usb-bridge',
        ('externe usb schijf', 'external usb disk', 'usb stick', 'flash drive', 'sd kaartlezer'),
        ('Bij I/O-fouten, klikgeluiden of belangrijke gegevens: stop herhaald aansluiten en bescherm eerst data.',
         'Ontkoppel een toegankelijke schijf veilig voordat je de verbinding wijzigt.'),
        ('Zonder waarschuwingssignalen: probeer een andere geschikte USB-poort direct op de computer en een passende datakabel.',
         'Gebruik geen geforceerde mounts, formattering of bestandssysteemreparaties.'),
        ('Een andere poort die werkt bewijst geen gezonde gegevensdrager.',
         'Blijven I/O-fouten: stop met testen en richt je op gegevensbescherming.')),
    _topic('speakers', 'Speakers · external / distorted', 'hardware34.audio.speaker-distortion',
        ('speakers', 'luidsprekers', 'externe speakers', 'gekraak audio'),
        ('Zet het volume laag; zet eerst een versterker uit voordat je analoge audiokabels verwisselt.',),
        ('Bij externe luidsprekers: controleer de juiste aansluiting, voeding en kabel zonder iets te forceren.',
         'Bij ingebouwde luidsprekers: sla kabeltests over; audio-instellingen worden door de Troubleshooter gecontroleerd waar mogelijk.'),
        ('Een verbetering met andere speakers wijst mogelijk op de externe audioketen.',
         'Clipping, audioprofiel en driver blijven mogelijke oorzaken.')),
)

BY_KEY = {topic.key: topic for topic in TOPICS}
assert len(BY_KEY) == len(TOPICS), 'duplicate peripheral topic key'


def matching_topics(search: str = '') -> tuple[PeripheralTopic, ...]:
    text = search.strip().casefold()[:150]
    return tuple(t for t in TOPICS if not text or text in t.title.casefold()
                 or any(text in term.casefold() for term in t.search_terms))


def guide_for_topic(topic_key: str, case_id: str) -> PeripheralTopic:
    topic = BY_KEY[topic_key]
    if topic.case_id != case_id:
        raise ValueError('Topic cannot be used with an unrelated diagnosis tree')
    return topic
