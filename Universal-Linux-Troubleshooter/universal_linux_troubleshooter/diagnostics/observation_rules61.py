"""14 provisional, case-specific package/container event observations.

These are not independently approved causes or route applicability decisions.
"""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule


def _rule(fact, heading, evidence, limits):
    return ObservationRule('package_container_events61', fact, 'observed', heading, evidence, limits)


OBSERVATION_RULES61: dict[str, ObservationRule] = {
    'software35.packages.apt-foreign-repository': _rule('apt_repo_metadata_error','APT-repositorymetadata- of sleutelmelding gezien','APT meldt een expliciet Release-bestand- of ondertekeningsprobleem.','Het is niet bewezen dat het een externe repository betreft of dat een sleutel vervangen moet worden.'),
    'software35.packages.apt-held': _rule('apt_packages_kept_back','APT meldt uitgestelde pakketten','APT registreert expliciet dat pakketten zijn achtergehouden.','Een bewuste pakket-pin of systeemwijziging is niet vastgesteld; niet automatisch unhold uitvoeren.'),
    'software35.packages.dnf-dependency-conflict': _rule('dnf_depsolve_conflict','DNF-oplosconflict in journald gezien','DNF rapporteert een conflict of een ontbrekende vereiste afhankelijkheid.','Betrokken pakketten, pakketbron en distributie zijn niet onafhankelijk vastgesteld.'),
    'software35.packages.pacman-file-conflict': _rule('pacman_file_conflict','Pacman-bestandsconflict gemeld','Pacman rapporteert een conflict bij het wegschrijven van pakketbestanden.','Of het bestand door een betrouwbaar pakket wordt beheerd is onbekend; nooit geforceerd overschrijven.'),
    'software35.packages.rpm-ostree-layered': _rule('ostree_layer_conflict','Gelaagd rpm-ostree-pakketconflict gemeld','Een rpm-ostree-fout benoemt expliciet een conflict met een layered package.','De verantwoordelijke laag of juiste verwijderactie is niet bewezen.'),
    'software35.packages.zypper-lock': _rule('zypper_package_locked','Zypper-pakketvergrendeling gemeld','Een zypper-melding noemt een locked package.','Het is niet bewezen dat de lock onbedoeld is; nooit automatisch ontgrendelen.'),
    'software35.packages.zypper-repo-mismatch': _rule('zypper_vendor_conflict','Zypper-vendorconflict gemeld','Zypper rapporteert expliciet een leveranciers- of vendorconflict.','Repo-eigenaarschap en de juiste pakketbron blijven onbekend; geen automatische vendorwissel.'),
    'software35.packages.flatpak-remote': _rule('flatpak_remote_error','Flatpak-remotefout gemeld','Een Flatpak-fout vermeldt een ontbrekende remote of onleesbare remote-samenvatting.','Een ontbrekende remote is niet hetzelfde als een netwerkprobleem; installatie-scope en bron eerst bepalen.'),
    'software35.packages.snap-refresh': _rule('snap_refresh_error','Snap-verversprobleem gemeld','Snap rapporteert een vastgehouden of mislukte refresh.','Een opzettelijk hold en een tijdelijke winkelstoring zijn niet onderscheiden.'),
    'system.upgrade-signature-error': _rule('update_signature_error','Authenticatiefout voor pakketmetadata gemeld','Een pakketbeheerprogramma rapporteert een expliciete cryptografische handtekeningfout.','Niet bewezen dat de ondertekenaar fout is; nooit verificatie uitschakelen.'),
    'software35.containers.podman-image-missing': _rule('podman_image_absent','Ontbrekend Podman-image gemeld','Een Podman-gerelateerde melding noemt een onbekend of ontbrekend image.','Dit kan een onjuiste tag, lokale cache of onbeschikbare registry zijn; netwerkverzoek vereist toestemming.'),
    'software35.containers.podman-rootless-port': _rule('podman_privileged_port','Podman-rootless poortweigering gemeld','Een expliciete rootlessport-melding benoemt een niet-toegestane poort.','Werkelijke servicebehoefte en poortconfiguratie zijn niet vastgesteld; geen systeemlimieten wijzigen.'),
    'software35.containers.volume-permission': _rule('podman_volume_access_denied','Podman-volumetoegangsweigering gemeld','Een Podman-melding noemt een bind- of volumekoppeling met toegangsweigering.','Geen bewijs voor de precieze UID-mapping, SELinux-labels of bestandsrechten.'),
    'software35.containers.container-network': _rule('podman_container_dns_failure','Podman-container DNS-fout gemeld','Een Podman-netwerkmelding noemt een mislukte naamomzetting.','Host-DNS en container-DNS zijn niet apart vergeleken; niet blind netwerkconfiguratie wijzigen.'),
}
