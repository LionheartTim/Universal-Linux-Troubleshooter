"""Non-repair follow-up guidance for evidence-limited Manual Diagnostics cases.

These are editorially reviewed, explicitly mapped informational actions. They
cannot run commands, change configurations, approve a resolution route, or
convert a logged event into a proven physical cause. A physical step belongs
in physical_connections.py, which already handles data-safety preconditions.
"""
from __future__ import annotations

# The user is never asked to interpret logs or execute diagnostic commands.
# Every item is a safe self-contained explanation or a user-only observation.
_FOLLOWUPS: dict[str, tuple[str, ...]] = {
    'software35.applications.gpu-vs-app-interference': (
        'Als het veilig kan: sluit de optionele achtergrondapp tijdelijk en gebruik de computer daarna normaal. Forceer geen nieuwe GPU-crash.',
        'Kies daarna Rescan. Als de GPU ook zonder de app vastloopt, is een direct oorzakelijk verband met die app minder aannemelijk, maar nog niet uitgesloten.',
        'Een crash van DeepCool vlak na een GPU-reset kan ook een gevolg van de instabiliteit zijn. Verwijder geen driver of programma op basis van tijdsoverlap.',
    ),
    'graphics.gpu-crash': (
        'Vermijd een geforceerde stresstest of een ongerichte driverwissel. De Troubleshooter kan alleen beschikbare lokale GPU-gebeurtenissen beoordelen.',
        'Is de storing tijdens normaal gebruik opnieuw opgetreden, gebruik dan Rescan; het verdwijnen van een melding bewijst op zichzelf geen reparatie.',
    ),
    'hardware34.gpu.physical-reset': (
        'Een GPU-reset kan ontstaan door driver, voeding, firmware of hardware. Een logmelding alleen maakt geen van die oorzaken bewezen.',
        'Gebruik Rescan na normaal gebruik; forceer geen nieuwe vastloper en verander geen driver zonder vastgestelde aanleiding.',
    ),
    'hardware34.storage.nvme-critical-warning': (
        'Bij een actuele NVMe-gezondheidswaarschuwing: bescherm eerst belangrijke gegevens en vermijd belastende schrijftests.',
        'Een waarschuwing over temperatuur of beschikbare reserve is niet hetzelfde als een bewezen defecte SSD. Laat type waarschuwing, schijfidentiteit en gegevensgezondheid bevestigen voordat vervanging wordt geadviseerd.',
        'Bij aanhoudende I/O-fouten: stop experimenten en volg schijf- of fabrikantspecifieke gegevensherstelbegeleiding.',
    ),
    'hardware34.storage.raid-degraded': (
        'Bescherm gegevens voordat je iets aan de array wijzigt. Start geen automatische rebuild, force-assemble of schijfvervanging op basis van één oude logmelding.',
        'De actuele arraystatus en het juiste lid moeten afzonderlijk betrouwbaar vastgesteld zijn.',
    ),
    'storage.filesystem-errors': (
        'Bescherm zo mogelijk eerst de gegevens. Voer geen fsck, geforceerde remount of reparatie uit op een actief beschrijfbaar bestandssysteem.',
        'De juiste herstelmethode hangt af van bestandssysteem, actuele mountstatus en bevestigde onderliggende schijfgezondheid.',
    ),
    'software35.services.oom-killed': (
        'Een OOM-afsluiting bewijst geheugenuitputting op dat moment, maar geen defect RAM en geen specifieke veroorzakende applicatie.',
        'Een Rescan mag alleen nieuwe OOM-gebeurtenissen rapporteren; afwezige meldingen bewijzen geen definitief herstel.',
    ),
    'system.oom-killed': (
        'Een OOM-afsluiting is niet hetzelfde als een defecte geheugenmodule. Geen RAM vervangen of app verwijderen zonder extra bewijs.',
    ),
    'system.failed-service': (
        'Een mislukte systemd-unit is vastgesteld, maar die hoeft niets met de gekozen klacht te maken te hebben.',
        'Wijzig of schakel geen willekeurige service uit. Een hercontrole toont alleen de nieuwe actuele toestand.',
    ),
    'applications.service-failed': (
        'Een mislukte unit bewijst nog niet dat deze de betrokken toepassing laat crashen. Schakel geen service willekeurig uit.',
    ),
    'network.wifi-password': (
        'Een authenticatiefout betekent niet automatisch dat het wachtwoord fout is. Ook routerinstellingen, signaal en beveiligingsprotocol kunnen meespelen.',
        'Controleer alleen zelf of het bedoelde netwerk is geselecteerd; deel nooit het wachtwoord of andere geheimen in een log of supportbericht.',
    ),
    'software35.network.dns-per-app': (
        'Wijzig niet de DNS van het hele systeem zolang alleen één applicatie problemen heeft.',
        'Controleer desgewenst in de normale applicatie of het om één specifieke site gaat; de Troubleshooter voert geen internetverzoeken uit zonder afzonderlijke toestemming.',
        'Wanneer een pakketwijziging later aantoonbaar passend is, kan de gebruiker de juiste bron in Universal Linux Software Manager kiezen.',
    ),
    'software35.flatpak.portal-dialog-missing': (
        'Een portal-fout bewijst nog niet dat een Flatpak-app defect is of dat het portalpakket ontbreekt.',
        'Voer geen algemene sandbox-override of willekeurige herinstallatie uit. Bij bewezen pakketproblemen blijft de oorspronkelijke installatiebron leidend.',
    ),
    'network.wifi-drops': (
        'Een ontkoppelingsmelding bewijst geen defecte Wi-Fi-kaart of fout wachtwoord; accesspoint, signaal en powersave kunnen ook meespelen.',
        'Laat de normale verbinding opnieuw tot stand komen en kies Rescan; forceer geen uitval.',
    ),
    # v61 package and container observations: explanation-only next steps.
    # None of these authorizes a shell command, a package-source change or repair.
    'software35.packages.apt-foreign-repository': (
        'Een melding over een Release-bestand of sleutel vertelt nog niet of het om een externe repository gaat. De installatiebron moet eerst afzonderlijk worden vastgesteld.',
        'Schakel GPG-controles niet uit en importeer geen willekeurige sleutels. Bij een bewezen pakketbronprobleem kun je de GUI van Universal Linux Software Manager kiezen; een terminalroute vereist distributiespecifiek gecontroleerde opdrachten.',
    ),
    'software35.packages.apt-held': (
        'Pakketten die worden achtergehouden kunnen ook door de distributie bewust worden uitgesteld. Dit bewijst geen administratieve pin of fout.',
        'Verwijder geen hold en forceer geen upgrade zonder eerst de exacte pakketstatus te bevestigen.',
    ),
    'software35.packages.dnf-dependency-conflict': (
        'Een DNF-afhankelijkheidsconflict zegt nog niet welke pakketbron verantwoordelijk is. Maak onderscheid tussen een gewone RPM-distributie en een Atomic/rpm-ostree-systeem.',
        'Voer geen geforceerde pakketverwijdering of bronwissel uit. Bij een bewezen pakketprobleem blijft de oorspronkelijke installatiebron bepalend.',
    ),
    'software35.packages.pacman-file-conflict': (
        'Pacman meldt mogelijk een bestandsconflict, maar het is niet bewezen of het bestand bij een pakket of bij gebruikersgegevens hoort.',
        'Verwijder of overschrijf geen bestanden met force-opties zonder onafhankelijke eigenaarschapscontrole.',
    ),
    'software35.packages.rpm-ostree-layered': (
        'Een layered-package conflict zegt nog niet welke pakketlaag veilig kan worden verwijderd. De huidige bootdeployment en betrokken laag vragen aparte verificatie.',
        'Verwijder geen noodzakelijke systeemlaag en wijzig de Atomic-deployment niet op basis van één journald-melding.',
    ),
    'software35.packages.zypper-lock': (
        'Een pakketlock kan bewust zijn geplaatst om compatibiliteit te bewaren. Het waargenomen lock-event bewijst niet dat de lock verouderd is.',
        'Ontgrendel of verwijder geen pakket voordat de bedoeling en de gevolgen zijn vastgesteld.',
    ),
    'software35.packages.zypper-repo-mismatch': (
        'Een vendorconflict bewijst geen defecte repository; bronbeleid en distributie-upgrade kunnen het verschil verklaren.',
        'Accepteer geen willekeurige vendorwissel of force-update zonder eerst de gewenste bron te bevestigen.',
    ),
    'software35.packages.flatpak-remote': (
        'Een ontbrekende Flatpak-remote is iets anders dan een onbereikbare remote. De juiste gebruikers- of systeeminstallatiescope moet eerst bekend zijn.',
        'Voeg niet automatisch een vervangende bron toe. Universal Linux Software Manager kan bij een later bewezen pakketprobleem een begrijpelijke GUI-route bieden.',
    ),
    'software35.packages.snap-refresh': (
        'Een mislukte of vastgehouden Snap-refresh kan bewust zijn uitgesteld. Het logevent toont niet automatisch een beschadigde installatie.',
        'Verwijder geen Snap of hold en forceer geen refresh zonder actuele pakketstatus.',
    ),
    'system.upgrade-signature-error': (
        'Een handtekeningfout is een beveiligingssignaal; bepaal eerst welke ondertekende bron en metadata daadwerkelijk betrokken zijn.',
        'Schakel cryptografische verificatie nooit uit om de update toch te forceren.',
    ),
    'software35.containers.podman-image-missing': (
        'Een imagefout bewijst niet dat het image werkelijk verdwenen is; tag, opslagcontext en registryrechten kunnen verschillen.',
        'De Troubleshooter haalt geen image van internet en gebruikt geen rootrechten zonder aparte toestemming.',
    ),
    'software35.containers.podman-rootless-port': (
        'Een rootlesspoortfout kan ontstaan doordat een lage hostpoort niet zonder bevoegdheden geopend kan worden. De gewenste poort en service zijn nog niet bevestigd.',
        'Wijzig geen systeembeveiligingslimieten en start de container niet als root op basis van deze melding.',
    ),
    'software35.containers.volume-permission': (
        'Een container-volumeweigering kan samenhangen met UID-mapping, SELinux-labels, mountmodus of een verkeerd pad. Geen van die oorzaken is afzonderlijk bewezen.',
        'Gebruik geen recursieve permissiewijzigingen en schakel SELinux niet uit om de fout te omzeilen.',
    ),
    'software35.containers.container-network': (
        'Een DNS-fout binnen een container bewijst niet dat host-DNS defect is; beide netwerkomgevingen moeten afzonderlijk vergeleken worden.',
        'De Troubleshooter voert geen externe netwerkcontrole uit zonder toestemming en wijzigt geen DNS-instellingen op basis van deze melding.',
    ),
    # v62: optional beginner-safe triage for observed application and tool events.
    'software35.development.git-auth': (
        'Een Git-toegangsweigering kan met de gekozen remote, het account of de autorisatie samenhangen. Deel nooit wachtwoorden, toegangstokens of SSH-sleutels.',
        'Wijzig geen globale Git-instellingen en maak geen nieuwe credentials aan op basis van één oude logmelding. De Troubleshooter vraagt geen geheimen op.',
    ),
    'software35.development.git-worktree-dirty': (
        'Git beschermt mogelijk lokale bestanden tegen overschrijven. Laat bestaande werkbestanden en ongecommitte wijzigingen intact.',
        'Voer geen reset --hard, clean of geforceerde checkout uit. De bedoelde branch en de waarde van lokale wijzigingen moeten eerst bekend zijn.',
    ),
    'software35.development.python-externally-managed': (
        'Een door de distributie beheerde Python-installatie is niet hetzelfde als een kapotte pip-installatie. De exacte Python-omgeving is nog onbekend.',
        'Vermijd --break-system-packages en gebruik geen sudo-pip. Een projectspecifieke virtuele omgeving kan later een passende optie zijn, mits de omgeving bekend is.',
    ),
    'software35.development.build-tool-missing': (
        'Een buildfout door een onbekend commando zegt niet vanzelf welke ontwikkeltool of pakket ontbreekt. Een script kan ook naar een verkeerde naam verwijzen.',
        'Installeer geen willekeurige systeemcompiler. De projectvereisten en de exacte betrokken tool moeten eerst betrouwbaar worden gecontroleerd.',
    ),
    'software35.appimage.noexec-filesystem': (
        'Een AppImage-executiefout kan door mountopties, bestandsrechten of een ongeschikte runtime ontstaan. Een tekstmelding bewijst geen van die oorzaken afzonderlijk.',
        'Verplaats geen persoonlijke data en verander geen mountopties of beveiligingsinstellingen zonder de feitelijke bestandslocatie en mountstatus vast te stellen.',
    ),
    'software35.applications.desktop-entry-invalid': (
        'Een ongeldige .desktop-starter kan een ontbrekend startmenu-item verklaren, maar het is niet bewezen dat de melding van de bedoelde applicatie afkomstig is.',
        'Bewerk of verwijder geen globale .desktop-bestanden; eerst moet de juiste starter en het gebruikers- of systeempad bekend zijn.',
    ),
    'software35.flatpak.app-not-launching': (
        'Een mislukte Flatpak-start bewijst niet dat de installatie is beschadigd. Scope, runtime, sandboxrechten en de applicatie zelf kunnen verschillen.',
        'Verwijder geen gebruikersgegevens of de Flatpak-installatie. Een latere pakketoplossing moet de oorspronkelijke bron en installatie-scope respecteren.',
    ),
    'virtualization.container-fail': (
        'Een mislukte containerstart kan een fout in het image, configuratie of toegewezen hulpmiddelen betekenen. De bron en inhoud zijn nog niet vastgesteld.',
        'Verwijder geen container of persistent volume en wijzig geen rechten als root op basis van één melding. Bewaar gegevens voordat een herstelkeuze wordt gemaakt.',
    ),
    'virtualization.podman-rootless-error': (
        'Bij een rootless-fout zijn de gebruikersnaamruimte en de huidige beveiligingsinstellingen nog niet onafhankelijk gecontroleerd.',
        'Start dezelfde container niet zomaar met beheerdersrechten en schakel SELinux of andere toegangscontrole niet uit.',
    ),
    'system.shutdown-hangs': (
        'Een systemd-stop-time-out in een beperkte huidige-bootlog bewijst nog niet dat dit de vorige trage afsluiting veroorzaakte.',
        'Forceer geen extra afsluitproblemen en schakel geen onbekende systeemdienst uit. Kies na normaal gebruik Rescan; zonder relevant tijdstip blijft de oorzaak onbekend.',
    ),
    # v64: direct observational facts are not proof of a root cause.
    'hardware34.cooling.sensor-disconnect': (
        'De hardwaremonitor meldt een sensormeting die mogelijk niet betrouwbaar is. Dit bewijst niet dat de sensor fysiek loszit.',
        'Verhoog de belasting niet om het probleem uit te lokken. Controleer normale gebruikstemperaturen als een andere betrouwbare sensor beschikbaar is en kies Rescan; bij duidelijke oververhitting het systeem veilig uitschakelen.',
    ),
    'software35.flatpak.duplicate-scope': (
        'Een applicatie-ID in USER en SYSTEM is niet automatisch een probleem. Controleer eerst welke installatie daadwerkelijk wordt gestart en of er werkelijk een versie- of bronconflict is.',
        'Verwijder geen installatie of gebruikersgegevens en wissel geen bron zonder bevestiging. Gebruik bij een bewezen probleem desgewenst Universal Linux Software Manager voor de GUI-route.',
    ),
    # v63 direct hardware measurements: a tachometer or SMART count is not a failed part.
    'hardware34.storage.sata-reallocated': (
        'Een niet-nul SMART-sectorteller is reden om belangrijke gegevens veilig te stellen. Vermijd onnodige zware schrijfproeven en begin geen lange zelftest zonder gegevensbescherming.',
        'De oorzaak, het precieze apparaat en de trend moeten verder onderzocht worden; verwijder of vervang geen schijf uitsluitend vanwege één tellerwaarde.',
    ),
    'hardware34.cooling.fan-rpm-zero': (
        '0 RPM kan bij moderne systemen een normale ventilatorstop zijn. Beoordeel de veilige gebruikstoestand en let op daadwerkelijk oplopende temperaturen; forceer geen stresstest.',
        'Raak ventilatoren niet aan terwijl de computer aanstaat. Alleen een gekoppelde sensor en een gecontroleerde fysieke waarneming kunnen verder helpen.',
    ),
    'hardware34.cooling.pump-rpm': (
        'Een pompsensor met 0 RPM bewijst niet dat de pomp stilstaat: de tachometerkabel of sensor kan ontbreken. Forceer geen belastingstest.',
        'Bij duidelijk oplopende CPU-temperaturen: beëindig zware taken en schakel het systeem veilig uit. Controleer aansluitingen alleen wanneer het apparaat volledig uitgeschakeld is.',
    ),
    # v65: observations only; package removals and hardware repair are never automatic.
    'software35.packages.pacman-orphans': (
        'Een orphan-label betekent alleen dat een pakket niet meer als dependency wordt vereist. Het kan toch bewust voor jouw workflow gebruikt worden.',
        'Verwijder niet alles in één keer. Beoordeel een later bewezen opruimactie desgewenst via de Arch-tab van Universal Linux Software Manager; controleer eerst welke pakketten je wilt behouden.',
    ),
    'hardware34.gpu.cooling-fan': (
        'Een gpu-hwmon fan-foutstatus is geen bewijs dat de ventilator fysiek stilstaat. Ook driver- en tachometersignalen kunnen misleiden.',
        'Forceer geen GPU-stresstest. Bij duidelijke oververhitting zware taken stoppen, de computer veilig uitschakelen en pas dan de ventilatie visueel controleren.',
    ),
    'storage.mount-failed': (
        'Een mountfout bewijst nog niet dat de schijf defect is. Verander /etc/fstab niet op basis van een losstaande melding.',
        'Bij twijfel over gegevensintegriteit eerst gegevens beschermen voordat een herstelroute wordt gekozen.',
    ),
}


def followup_for_case(case_id: str, *, completed: bool) -> tuple[str, ...]:
    """Only informational next steps after a completed scan; never a repair."""
    return _FOLLOWUPS.get(case_id, ()) if completed else ()
