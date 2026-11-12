"""Ten v62 provisional observations; no automated repair route approved."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule


def rule(fact, conclusion, proof, caveat):
    return ObservationRule('application_events62',fact,'observed',conclusion,proof,caveat)

OBSERVATION_RULES62 = {
    'software35.development.git-auth': rule('git_auth_rejected','Git-authenticatiefout als gebeurtenis gemeld','Een Git-proces meldt een expliciete toegang- of authenticatieweigering.','Repository, identiteit en geldigheid van credentials zijn niet beoordeeld; deel nooit tokens of wachtwoorden.'),
    'software35.development.git-worktree-dirty': rule('git_local_changes_protected','Git beschermt bestaande lokale wijzigingen','Git meldde dat een branch- of werkboomactie bestanden zou overschrijven.','Het huidige werkboomverschil en de juiste herstelactie zijn niet vastgesteld; nooit wijzigingen weggooien.'),
    'software35.development.python-externally-managed': rule('pip_externally_managed','pip meldt een extern beheerde Python-omgeving','Een pip-proces registreerde expliciet externally-managed-environment.','Python-omgeving en virtuele omgeving zijn niet geïdentificeerd; geen installaties forceren.'),
    'software35.development.build-tool-missing': rule('build_executable_missing','Buildproces meldt een ontbrekend uitvoerbaar commando','Make of Ninja meldt een command-not-found-fout tijdens het bouwen.','Het ontbrekende commando kan projectspecifiek zijn; geen willekeurige toolchain installeren.'),
    'software35.appimage.noexec-filesystem': rule('appimage_noexec_block','AppImage meldt een mogelijke noexec-blokkering','Een AppImage-gerelateerde fouttekst bevat expliciet een noexec- of execute-weigering.','De werkelijke mountopties, bestandsrechten en het bedoelde AppImage zijn niet bevestigd.'),
    'software35.applications.desktop-entry-invalid': rule('desktop_entry_invalid','Fout bij het valideren van een desktopstarter','Een desktop-file-validate-gerelateerde melding wijst op een ongeldige .desktop-structuur.','De gemelde starter is niet gekoppeld aan de ontbrekende menuvermelding; geen globale menuwijziging.'),
    'software35.flatpak.app-not-launching': rule('flatpak_launch_failure','Flatpak meldt een mislukte applicatiestart','Een Flatpak-gerelateerde melding beschrijft expliciet een mislukte appstart.','Applicatie-ID, user/system-scope, runtime en precieze oorzaak zijn nog niet vastgesteld.'),
    'virtualization.container-fail': rule('podman_container_start_failure','Podman meldt een mislukte containerstart','Een Podman-gerelateerde melding noemt een containerstart- of aanmaakfout.','Container-ID, inhoud, oorspronkelijke rechten en reden van mislukken zijn niet vastgesteld.'),
    'virtualization.podman-rootless-error': rule('podman_rootless_userns_error','Podman meldt een rootless/user-namespacefout','Een Podman-proces meldt expliciet een rootless- of gebruikersnaamruimtefout.','Of de fout door kernelbeleid, configuratie of bestandsrechten komt is onbekend; niet als root herhalen.'),
    'system.shutdown-hangs': rule('shutdown_stop_timeout','Systemd meldt een stop-time-out','Een systemd-melding beschrijft expliciet een stop-time-out voor een unit.','Een huidige-bootsteekproef kan de vorige afsluiting missen; de verantwoordelijke unit en vertraging zijn niet bevestigd.'),
}
