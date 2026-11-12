"""Deterministic evidence gating for *reviewed* cases only.

This does not execute a graph or set `confirmed_by_user=True`. The existing
manual graph API remains strict. Case selection uses a narrow rule set and
validated `FACT:` markers from fixed, read-only checks. Unreviewed cases stop
at UNKNOWN rather than allowing Qwen to infer an unproven route.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import re
from typing import Sequence

from ..results import DiagnosticResult, ResultStatus
from ..knowledge.diagnosis_trees import load_trees
from .catalog_coverage38 import candidate_case, safe_case_report
from .reviewed_case_rules44 import OBSERVATION_RULES
from .peripheral_rules47 import PERIPHERAL_OBSERVATIONS47
from .observation_rules50 import OBSERVATION_RULES50
from .observation_rules51 import OBSERVATION_RULES51
from .observation_rules52 import OBSERVATION_RULES52
from .observation_rules59 import OBSERVATION_RULES59
from .observation_rules61 import OBSERVATION_RULES61
from .observation_rules62 import OBSERVATION_RULES62
from .observation_rules63 import OBSERVATION_RULES63
from .observation_rules64 import OBSERVATION_RULES64
from .observation_rules65 import OBSERVATION_RULES65
from .observation_rules66 import OBSERVATION_RULES66
from .observation_rules67 import OBSERVATION_RULES67
from .observation_rules77 import OBSERVATION_RULES77
from .observation_rules78 import OBSERVATION_RULES78
from .observation_rules79 import OBSERVATION_RULES79

ULSM='https://github.com/LionheartTim/Universal-Linux-Software-Manager'
ULT='https://github.com/LionheartTim/Universal-Linux-Terminal'

@dataclass(frozen=True)
class Finding:
    case_id: str
    symptom: str                 # supported / contradicted / unknown
    route: str | None            # never choose a route without proof
    conclusion: str
    proof: tuple[str,...]
    limitations: tuple[str,...]
    solution_kind: str | None = None

    def public_summary(self) -> str:
        lines=[f'**Gecontroleerde diagnose: {self.conclusion}**',
               f'Bewijsstatus: {self.symptom}.']
        lines.extend('- '+p for p in self.proof)
        lines.extend('- Onbekend: '+p for p in self.limitations)
        if (self.route and self.solution_kind=='package') or self.case_id=='software35.network.dns-per-app':
            lines.append('**Alleen als een pakketoplossing later bewezen passend is:** kies zelf Terminal of GUI. '
                         f'Grafisch: [Universal Linux Software Manager]({ULSM}) via het juiste pakkettype en installatiebron; '
                         f'educatief: [Universal Linux Terminal]({ULT}) om de voor jouw distro en pakketbron gecontroleerde opdracht op te zoeken, uitleg te lezen en zelf te beslissen of je Enter drukt. '
                         'In de GUI: kies het juiste pakkettype, controleer de bestaande installatiebron en gebruik alleen een toepasselijke Updates-optie. '
                         'De Troubleshooter doet het diagnosewerk, niet de gebruiker.')
        lines.append('Geen instellingen gewijzigd of reparaties uitgevoerd.')
        return '\n'.join(lines)

    def model_context(self) -> str:
        return (f'case={self.case_id}; symptom={self.symptom}; proven_route={self.route or "NONE"}; '
                f'facts={self.proof}; limitations={self.limitations}. '
                'Never claim a cause solely from timing. Do not ask user to compare logs or run diagnostic commands. '
                'No automatic repair. Explain only an evidence-supported user-only remedy; '
                'package actions may show Universal Linux Software Manager GUI or educational Universal Linux Terminal. '
                'Unknown means UNKNOWN.')


def _fact(results: Sequence[DiagnosticResult], key:str, name:str) -> str|None:
    selected=[r for r in results if r.category_key=='focused' and r.check_key==key]
    if len(selected)!=1 or selected[0].status in (ResultStatus.UNKNOWN, ResultStatus.NOT_RUN):
        # A failed/truncated probe cannot authenticate an apparently positive
        # FACT marker, even when one is accidentally present in its payload.
        return None
    values=[]
    for line in selected[0].evidence:
        m=re.fullmatch(r'FACT:([a-z0-9_]+)=([a-z_]+)',line)
        if m and m.group(1)==name:
            values.append(m.group(2))
    # Never use an ambiguous or duplicated marker to choose a repair.
    return values[0] if len(values)==1 else None


def _result(results,cat,check):
    selected=[r for r in results if r.category_key==cat and r.check_key==check]
    return selected[0] if len(selected)==1 else None


def recognized_case(question:str) -> str|None:
    # Exact catalog titles take precedence over broad legacy keyword probes:
    # "PCIe fatal event" must never be misidentified as an NVMe failure.
    exact=candidate_case(question)
    if exact is not None and question.strip().casefold()==_reviewed_catalog()['cases'][exact]['title'].casefold():
        return exact
    q=question.casefold()
    if any(x in q for x in ('deepcool','mystique')) and any(x in q for x in ('gpu','graphics','videokaart')):
        return 'software35.applications.gpu-vs-app-interference'
    if 'flatpak' in q and any(x in q for x in ('dns','network','internet','netwerk')):
        return 'software35.network.dns-per-app'
    if any(x in q for x in ('nvme','ssd controller')):
        return 'hardware34.storage.nvme-critical-warning'
    if any(x in q for x in ('dhcp','no carrier','cable unplugged','ethernet cable','netwerkkabel','bekabeld')):
        return 'network.wired-link-no-carrier'
    if any(x in q for x in ('boot','startup','opstart')) and any(x in q for x in ('slow','traag','langzaam','seconds','seconden')):
        return 'software35.services.high-boot-time'
    if any(x in q for x in ('disk says full','disk full','disk is full','out of space','schijf vol','disk space full')):
        return 'storage.disk-full'
    return candidate_case(question)


# Frozen route conditions: no document edit silently authorizes an automated fix.
REVIEWED_ROUTES={
 'storage.disk-full': {'route_1':'Writable home/var is nearly full'},
 'storage.disk-smart': {'route_1':'A health warning is readable'},
 'network.no-gateway': {'route_1':'Only the affected connection has a missing gateway'},
 'network.wired-link-no-carrier':{'route_1':'Link physically down','route_2':'Link up, but DHCP fails'},
 'hardware34.storage.nvme-critical-warning':{'route_2':'Logs instead show link reset with healthy media counters'},
 'software35.services.high-boot-time':{'route_2':'Slow stage predates userspace services'},
 'network.wifi-missing':{'route_1':'Wi-Fi radio is switched off or blocked'},
 'audio.bluetooth-not-found':{'route_1':'Adapter radio is switched off or blocked'},
 'hardware34.memory.ecc-uncorrected':{'route_1':'Uncorrected memory errors present'},
 'hardware.memory-error':{'route_1':'Repeatable uncorrectable hardware-memory events'},
 'hardware34.power.battery-degraded':{'route_1':'Verified battery wear'},
 'hardware34.cpu.core-topology':{'route_2':'Boot configuration restricts visible CPUs'},
 'software35.packages.atomic-pending-reboot':{'route_1':'Pending deployment has been staged successfully'},
 'software35.boot.wrong-kernel-after-update':{'route_1':'Bazzite pending deployment not yet booted'},
}

# The reviewed user-facing instructions must also stay unchanged. Changing
# only the JSON text while keeping the applicability condition is NOT enough
# to authorize new advice. SHA256 is a drift guard, not a signature.
APPROVED_ROUTE_STEPS_DIGEST = {
    ('storage.disk-full','route_1'): 'a0ec77483dadedeaf039abbef8efbf1f706f604645dd4a7fd96e573394afd46e',
    ('storage.disk-smart','route_1'): '39b3044dca2c28a40004e20af703af2a64587f1de31294242081d0633f3dffee',
    ('network.no-gateway','route_1'): 'ebded7757446bc2a5da9516b9992ab25754f9ff4efda30cb5a3d888c82ab912c',
    ('network.wired-link-no-carrier','route_1'): '59fdb4fd26b92dce690ca6f7dc810db159679adca89ad919417db0386e7f1fd2',
    ('network.wired-link-no-carrier','route_2'): 'da6f1daf313a4784dee54b1eaedc32c661f20d3be7f43995a6c6bdd1e51c664a',
    ('hardware34.storage.nvme-critical-warning','route_2'): 'dd85a47b13e788c9c1e371a9ab628e1e396974e626e108d9641966d16789eaa0',
    ('software35.services.high-boot-time','route_2'): '96f29d2c168bf5cb75adc2c90430029a8b82adb45517da04e31e23dc3b90801c',
    ('network.wifi-missing','route_1'): '2385385b125e6e1b4a32573d9e825026e418bf0d8b83b7ed0c2f0c4c0253640e',
    ('audio.bluetooth-not-found','route_1'): '7a380d6bfd98fc56c9a4f3264e910556dc6deff1c471716185f197284b8f0fe1',
    ('hardware34.memory.ecc-uncorrected','route_1'): '1d96f8370737e09b999763967d438619aff92db95cd38405e9caf4c5a8926ff4',
    ('hardware.memory-error','route_1'): '9303fcc16c89fd18260a8e4e114b4bcc07ee363440146951fd8756c0b8271037',
    # These two were reviewed against exact applicability and user steps in v44.
    ('hardware34.power.battery-degraded','route_1'): '6cd5183b811da0ce8c1d933c39d913ba559a971233e08831dc099cfae79473e9',
    ('hardware34.cpu.core-topology','route_2'): '9da21a923fc451da75512d53e416ec8a7a57cd47d0001062bfa3c657ceba4025',
    ('software35.packages.atomic-pending-reboot','route_1'): '8d98e1b7c4ca6ade588a18d287502926445d3e26fe0e439c7a280bc99088b7c2',
    ('software35.boot.wrong-kernel-after-update','route_1'): '608e7125de75cb7e6cf8abff6f95cf491ed87eeae70f92a47051accb3bc6054d',
}


def _route_steps_digest(steps) -> str:
    value = json.dumps(steps, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


@lru_cache(maxsize=1)
def _reviewed_catalog():
    return load_trees()


def assess_problem(question:str,results:Sequence[DiagnosticResult]) -> Finding|None:
    """Assess only observed test results; no user verdict or guessed log facts."""
    case=recognized_case(question)
    if case is None:
        return None
    return assess_case_id(case, results)


def assess_case_id(case: str, results: Sequence[DiagnosticResult]) -> Finding:
    """Directly assess an explicitly selected catalog ID; no title heuristics."""
    if case not in _reviewed_catalog()['cases']:
        raise KeyError(case)
    def finding(symptom,route,conclusion,proof=(),limits=(),kind=None):
        # Refuse stale or modified route mappings instead of steering to the
        # wrong fix after someone edits the single-source JSON.
        if route is not None:
            approved=REVIEWED_ROUTES.get(case,{}).get(route)
            try:
                doc_route=next((r for r in
                    _reviewed_catalog()['cases'][case]['resolution_routes'] if r['id']==route),None)
                recorded=doc_route['applicability_condition'] if doc_route else None
                digest=_route_steps_digest(doc_route['user_steps']) if doc_route else None
            except (OSError,ValueError,KeyError,TypeError):
                recorded=digest=None
            if approved is None or recorded!=approved or digest != APPROVED_ROUTE_STEPS_DIGEST.get((case,route)):
                return Finding(case,symptom,None,'Oplossingsroute moet opnieuw worden gecontroleerd',
                               tuple(proof),('Routevoorwaarden in kennisbank verschillen van gevalideerde regels.',))
        return Finding(case,symptom,route,conclusion,tuple(proof),tuple(limits),kind)
    # Exact, reviewed cases only. Generic warning results NEVER establish
    # route applicability. Each case reads only its dedicated local FACTs.
    if case in ('network.wifi-missing', 'audio.bluetooth-not-found'):
        radio = 'wifi' if case == 'network.wifi-missing' else 'bluetooth'
        observed = _fact(results, 'radio_blocks', radio)
        if observed == 'blocked':
            return finding('supported', 'route_1',
                           ('Wi-Fi-radio' if radio == 'wifi' else 'Bluetooth-radio') + ' is geblokkeerd',
                           ('De bijbehorende rfkill-radio meldt soft- of hard-block.',),
                           ('Een hardwareblokkering moet via de ondersteunde schakelaar worden opgeheven; een driverfout is niet bewezen.',))
        if observed == 'unblocked':
            return finding('contradicted', None,
                           'De gecontroleerde radio is niet geblokkeerd',
                           ('Rfkill meldt een zichtbare, niet-geblokkeerde radio.',),
                           ('Een werkende verbinding of goed functionerende adapter is hiermee niet bewezen.',))
        return finding('unknown', None, 'Radioblokkering niet eenduidig vastgesteld',
                       limits=('Ontbrekende, gemengde of onleesbare radiostatus is geen bewijs dat een adapter fysiek ontbreekt.',))
    if case in ('hardware.memory-error', 'hardware34.memory.ecc-uncorrected'):
        ue = _fact(results, 'kernel_signals', 'ecc_ue')
        repeated = _fact(results, 'kernel_signals', 'ecc_ue_repeated')
        if ue == 'observed':
            is_reviewed_single = case == 'hardware34.memory.ecc-uncorrected'
            route = 'route_1' if is_reviewed_single or repeated == 'observed' else None
            return finding('supported', route,
                           'Specifieke niet-corrigeerbare geheugengebeurtenis geregistreerd',
                           ('Een EDAC-UE of expliciete uncorrectable ECC/memory-melding staat in het huidige bootlog.',),
                           (('Meerdere afzonderlijke tijdstippen zijn aangetoond.' if repeated == 'observed'
                             else 'Herhaling en exacte defecte module zijn niet bewezen.'),
                            'Een logmelding bewijst niet welke DIMM vervangen moet worden.'))
        return finding('unknown', None, 'Geen sluitend bewijs voor fysiek RAM-defect',
                       limits=('Ontbrekende gebeurtenissen in een begrensd log sluiten RAM-problemen niet uit.',))
    if case in ('graphics.gpu-crash', 'hardware34.gpu.physical-reset'):
        gpu = _fact(results, 'kernel_signals', 'gpu_reset')
        if gpu == 'observed':
            return finding('supported', None, 'GPU-reset of ring-time-out in kernellog waargenomen',
                           ('Een grafische driver meldt een reset of vastgelopen GPU-ring in het huidige bootlog.',),
                           ('Een verband met de gemelde crash of de oorzaak (hardware/driver/app) is nog niet aangetoond.',))
        return finding('unknown', None, 'GPU-reset niet zelfstandig vastgesteld',
                       limits=('Een begrensd kernel-log zonder matching gebeurtenis sluit een eerdere GPU-crash niet uit.',))
    if case in ('software35.services.oom-killed', 'system.oom-killed'):
        if _fact(results, 'kernel_signals', 'oom_kill') == 'observed':
            return finding('supported', None, 'Linux heeft een proces beëindigd tijdens een OOM-gebeurtenis',
                           ('Het kernellog noemt een out-of-memory kill en een proces-ID.',),
                           ('Een geheugenlek, de schuldige applicatie en de precieze oorzaak zijn niet bewezen.',))
        return finding('unknown', None, 'Geen bewezen OOM-afsluiting',
                       limits=('Een segfault is geen OOM en een begrensd log kan een oudere OOM missen.',))
    if case == 'storage.filesystem-errors':
        if _fact(results, 'kernel_signals', 'fs_error') == 'observed':
            return finding('supported', None, 'Bestandssysteemfout in het kernel-log waargenomen',
                           ('Een specifieke EXT4-, Btrfs-, XFS- of F2FS-foutmelding staat in het huidige bootlog.',),
                           ('De getroffen schijf, actuele mountstatus en eventuele mediaschade zijn nog niet vastgesteld.',))
        return finding('unknown', None, 'Bestandssysteemfout niet aangetoond',
                       limits=('Een algemene waarschuwing of het ontbreken van logregels bewijst geen schijffout.',))
    if case in ('applications.service-failed', 'system.failed-service', 'system.service-restarts'):
        if _fact(results, 'failed_units', 'failed') == 'observed':
            return finding('supported', None, 'Een of meer systemd-units zijn mislukt',
                           ('De huidige systemctl --failed-status noemt ten minste één mislukte unit.',),
                           ('Welke unit bij de gemelde klacht hoort en waarom deze faalt, is nog niet bewezen.',))
        return finding('unknown', None, 'Geen overeenkomende servicefout vastgesteld',
                       limits=('Niet gevonden in de huidige lijst betekent niet dat de service eerder niet crashte.',))
    if case == 'storage.disk-smart':
        # The fixed health checker must have completed with trustworthy SMART
        # output and identified the affected disk. One serious warning calls
        # for backup/vendor review, never immediate disk replacement.
        row = _result(results, 'storage', 'health')
        if (row is not None and row.status == ResultStatus.PROBLEM
                and row.diagnosis.startswith('A drive reported a possible serious problem: ')
                and 'Source: lsblk device list and smartctl SMART information, read-only; no disk self-tests started.' in row.evidence
                and any(re.fullmatch(r'Disk /dev/(?:sd[a-z]{1,3}|nvme\d{1,3}n\d{1,3}|mmcblk\d{1,3}|vd[a-z]{1,3}|xvd[a-z]{1,3}|hd[a-z]{1,3}): .{1,100}', line)
                        for line in row.evidence)
                and any(re.fullmatch(r'(?:sd[a-z]{1,3}|nvme\d{1,3}n\d{1,3}|mmcblk\d{1,3}|vd[a-z]{1,3}|xvd[a-z]{1,3}|hd[a-z]{1,3}): Drive reported a possible failure; smartctl exit code: \d{1,3}', line)
                        for line in row.evidence)):
            return finding('supported', 'route_1',
                           'Een geïdentificeerde schijf meldt een ernstige SMART-gezondheidswaarschuwing',
                           ('De lokale read-only SMART-controle meldt een mogelijke fout voor een herkenbare schijf.',),
                           ('Dit bewijst niet welke component of sector defect is; maak eerst een back-up en laat de schijf afzonderlijk beoordelen.',))
        return finding('unknown', None, 'Geen betrouwbare SMART-waarschuwing voor deze schijf vastgesteld',
                       limits=('Ontbrekende of onvolledige SMART-gegevens bewijzen geen gezonde schijf; geen vervangingsadvies.',))
    if case == 'network.no-gateway':
        # host_ipv4 returns primary_ipv4=present ONLY for one active
        # non-loopback interface; absent IPv4 default-route is global.
        # This authorizes checking that connection's routing configuration,
        # not changing an address or claiming a broken router.
        ip = _fact(results, 'host_ipv4', 'primary_ipv4')
        default = _fact(results, 'host_ipv4', 'ipv4_default_route')
        if ip == 'present' and default == 'absent':
            return finding('supported', 'route_1',
                           'Een actieve IPv4-verbinding mist een IPv4-standaardroute',
                           ('Eén actieve niet-loopbackinterface heeft IPv4, maar de IPv4-default-routetabel is leeg.',),
                           ('Een bewust lokaal netwerk, IPv6-routing of VPN kan dit verklaren; controleer de bedoelde instellingen zonder ze automatisch te wijzigen.',))
        return finding('unknown', None, 'Geen eenduidig ontbrekende IPv4-standaardroute vastgesteld',
                       limits=('Meerdere interfaces, ontbrekende status of IPv6-specifieke routes vereisen apart onderzoek.',))
    if case=='storage.disk-full':
        space=_result(results,'storage','space')
        if space is None or space.status in (ResultStatus.UNKNOWN,ResultStatus.NOT_RUN):
            return finding('unknown',None,'Schijfruimte nog niet betrouwbaar vastgesteld',limits=('Opslagmeting ontbreekt.',))
        if space.status==ResultStatus.OK:
            return finding('contradicted',None,'Geen gebrek aan ruimte vastgesteld op de gecontroleerde opslaglocatie',
                           ('De gecontroleerde schrijfbare opslagruimte heeft voldoende vrije ruimte.',),
                           ('Andere partities en inodes zijn niet altijd gecontroleerd.',))
        if space.status==ResultStatus.WARNING and 'less than 2 GiB' in space.explanation:
            return finding('supported','route_1','Schrijfbare opslag is bijna vol',
                           ('Veilige opslagmeting onder 2 GiB en onder 10% vrije ruimte.',),
                           ('Inodes zijn niet afzonderlijk gecontroleerd.',))
        return finding('unknown',None,'Schijfstatus heeft aanvullend bewijs nodig')
    if case=='network.wired-link-no-carrier':
        link=_fact(results,'dhcp','link'); addr=_fact(results,'dhcp','ipv4'); dhcp=_fact(results,'dhcp','dhcp')
        if link=='down':
            return finding('supported','route_1','Geen actieve fysieke Ethernet-link waargenomen',('Vaste lokale interface meldt link down.',),
                           ('Kabel, poort en adapter als onderliggende oorzaak zijn nog niet onderscheiden.',))
        if link=='up' and addr=='absent' and dhcp=='timeout':
            return finding('supported','route_2','Actieve kabelverbinding, maar DHCP-aanvraag loopt vast',
                           ('Ethernet-link up; geen IPv4; DHCP-time-out op dezelfde interface.',),
                           ('DHCP-server, instellingen en switch zijn nog niet geïsoleerd.',))
        return finding('unknown',None,'Netwerkfout niet voldoende geïsoleerd',limits=(
            'Linkstatus, IP en een bijpassend DHCP-event moeten allemaal betrouwbaar bekend zijn.',))
    if case=='hardware34.storage.nvme-critical-warning':
        reset=_fact(results,'nvme','nvme_reset'); health=_fact(results,'nvme','media_health')
        if health=='critical':
            # NVMe critical_warning is a bit field: temperature, spare,
            # reliability, and read-only conditions need different follow-up.
            # A single nonzero warning cannot prove that a drive must be
            # replaced, even though the catalog's route_1 includes replacement.
            return finding('supported',None,'NVMe meldt een actuele gezondheidswaarschuwing',
                           ('De geïdentificeerde NVMe rapporteert een niet-nul SMART-critical-warning.',),
                           ('Het type waarschuwing en een werkelijk defect zijn nog niet vastgesteld.',
                            'Bescherm belangrijke gegevens; laat vervanging alleen na verificatie adviseren.'))
        if reset=='observed' and health=='healthy_counters':
            return finding('supported','route_2','NVMe-controllerreset met niet-afwijkende mediatellers',
                           ('Kernel noemt NVMe-reset; uitgelezen SMART-tellers melden geen mediaprobleem.',),
                           ('Ook gezonde SMART-tellers sluiten toekomstige hardwarefouten niet uit.',))
        if reset=='observed':
            return finding('supported',None,'NVMe-controllerreset gezien, maar fysieke oorzaak onbekend',
                           ('De beschikbare kernelregels noemen een NVMe-reset.',),
                           ('SMART-gegevens zijn ontoegankelijk of niet conclusief; SSD-schade niet bewezen.',))
        return finding('unknown',None,'NVMe-fout nog niet bewezen',limits=('Kernellog- of gezondheidsgegevens zijn onvoldoende.',))
    if case=='software35.services.high-boot-time':
        stage=_fact(results,'boot_phases','boot_stage')
        if stage=='pre_userspace':
            return finding('supported','route_2','Bootvertraging vóór de normale achtergrondservices',
                           ('Gemeten fase vóór userspace domineert opstarttijd.',),
                           ('De firmware/loader/kernel-subfase behoeft afzonderlijke vaststelling.',))
        if stage=='userspace':
            return finding('supported',None,'Userspace is traag, maar schuldige service onbekend',
                           ('Gemeten userspacefase domineert.',),
                           ('Geen willekeurige service stoppen: individuele wachttijden niet vastgesteld.',))
        return finding('unknown',None,'Bootfase nog niet betrouwbaar vastgesteld',limits=('systemd-analyze bevat geen vergelijkbare fasetijden.',))
    if case=='software35.network.dns-per-app':
        return finding('unknown',None,'App-specifieke DNS-oorzaak niet bewezen',
                       ('Geen externe resolver beproefd zonder toestemming.',),
                       ('De app en exacte hostnaam zijn niet onafhankelijk vergeleken; geen algemene DNS-reset gerechtvaardigd.',))
    if case=='software35.applications.gpu-vs-app-interference':
        gpu=_fact(results,'gpu_app','gpu_reset'); app=_fact(results,'gpu_app','app_crash')
        if gpu=='observed' and app=='observed' and _fact(results,'gpu_app','time_overlap')=='observed':
            return finding('supported',None,'GPU-reset én DeepCool-fout gevonden; causaliteit onbekend',
                           ('GPU- en app-gebeurtenissen liggen binnen vijf seconden in de gecontroleerde logs.',),
                           ('Gelijktijdigheid bewijst niet wie wie liet crashen; geen driver of app verwijderen.',))
        return finding('unknown',None,'GPU-DeepCool-verband niet vastgesteld',limits=(
            'De beschikbare, afgebakende logs zijn onvolledig of bevatten onvoldoende matching gebeurtenissen.',))
    # Explicitly reviewed, benign user-only route: a staged rpm-ostree
    # deployment can be activated by the user's normal reboot, if desired.
    # Never reboot automatically; never infer that the update is defective.
    if case == 'software35.packages.atomic-pending-reboot':
        state = _fact(results, 'atomic_pending', 'staged_deployment')
        if state == 'observed':
            return finding('supported', 'route_1',
                           'Een rpm-ostree-deployment is klaargezet en nog niet actief',
                           ('Een staged deployment en precies één booted deployment zijn in rpm-ostree status aangetroffen.',),
                           ('De gebruiker kiest zelf of en wanneer een normale reboot geschikt is; de actieve kernelversie wordt na afloop opnieuw gecontroleerd.',))
        return finding('unknown', None, 'Geen eenduidige klaargezette rpm-ostree-deployment vastgesteld',
                       limits=('Ontbrekende of onvolledige rpm-ostree-status is geen bewijs dat er geen update is.',))
    # This Bazzite-specific documentary route requires *both* an actual staged
    # rpm-ostree deployment AND an exact host OS identifier. On Fedora,
    # openSUSE or ambiguous /etc/os-release it remains UNKNOWN.
    if case == 'software35.boot.wrong-kernel-after-update':
        staged = _fact(results, 'atomic_pending', 'staged_deployment')
        bazzite = _fact(results, 'atomic_pending', 'bazzite_os')
        if staged == 'observed' and bazzite == 'observed':
            return finding('supported', 'route_1',
                           'Bazzite heeft een nog niet opgestarte rpm-ostree-deployment',
                           ('rpm-ostree toont één actief en een afzonderlijk staged deployment; /etc/os-release identificeert Bazzite.',),
                           ('De update is niet bewezen defect. De gebruiker kiest zelf of en wanneer een normale reboot geschikt is; controleer daarna de actieve versie.',))
        return finding('unknown', None, 'Geen bevestigd Bazzite-deployment dat wacht op een reboot',
                       limits=('Rpm-ostree-gegevens of een eenduidige Bazzite-identiteit ontbreken; geen reboot als reparatie voorschrijven.',))
    # Case-specific observational rules are reviewed individually: an observed
    # event is evidence of the event ONLY, never proof of a causative link.
    if case in OBSERVATION_RULES or case in PERIPHERAL_OBSERVATIONS47 or case in OBSERVATION_RULES50 or case in OBSERVATION_RULES51 or case in OBSERVATION_RULES52 or case in OBSERVATION_RULES59 or case in OBSERVATION_RULES61 or case in OBSERVATION_RULES62 or case in OBSERVATION_RULES63 or case in OBSERVATION_RULES64 or case in OBSERVATION_RULES65 or case in OBSERVATION_RULES66 or case in OBSERVATION_RULES67 or case in OBSERVATION_RULES77 or case in OBSERVATION_RULES78 or case in OBSERVATION_RULES79:
        rule=OBSERVATION_RULES.get(case) or PERIPHERAL_OBSERVATIONS47.get(case) or OBSERVATION_RULES50.get(case) or OBSERVATION_RULES51.get(case) or OBSERVATION_RULES52.get(case) or OBSERVATION_RULES59.get(case) or OBSERVATION_RULES61.get(case) or OBSERVATION_RULES62.get(case) or OBSERVATION_RULES63.get(case) or OBSERVATION_RULES64.get(case) or OBSERVATION_RULES65.get(case) or OBSERVATION_RULES66.get(case) or OBSERVATION_RULES67.get(case) or OBSERVATION_RULES77.get(case) or OBSERVATION_RULES78.get(case) or OBSERVATION_RULES79[case]
        observed=_fact(results,rule.probe,rule.fact)
        if observed == rule.positive:
            route = ('route_1' if case == 'hardware34.power.battery-degraded'
                     else 'route_2' if case == 'hardware34.cpu.core-topology' else None)
            return finding('supported',route,rule.conclusion,(rule.proof,), (rule.limitation,))
        # Even an observed opposing value does NOT rule out intermittent faults.
        return finding('unknown',None,'Geen eenduidige, toepasselijke gebeurtenis aangetoond',
                       limits=(rule.limitation, 'Ontbrekende, onvolledige of niet-passende lokale metingen zijn geen bewijs van afwezigheid.'))
    # Unreviewed cases get a local evidence plan, but no
    # automatic root-cause assertion until independently validated rules exist.
    report=safe_case_report(case,results)
    return finding('unknown',None,
                   'Diagnoseonderzoek gestart; oorzaak nog niet onafhankelijk bewezen',
                   (f'{len(report["completed"])} lokale controles beschikbaar voor {report["title"]}.',)
                   +tuple(f'{cid}: {status} — {description}' for cid,status,description in report['observations']),
                   (('Onbeschikbare controles: '+', '.join(report['unavailable'])+'.') if report['unavailable']
                     else 'De controles geven aanwijzingen, maar vormen zonder gevalideerde casusregels geen oorzakelijk bewijs.',
                    'Geen reparatie voorgesteld zolang de oorzaak niet is vastgesteld.'))
