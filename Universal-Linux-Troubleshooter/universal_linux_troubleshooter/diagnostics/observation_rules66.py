"""Case-by-case v66 observations, not causal or route-approval rules."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule

OBSERVATION_RULES66 = {
    'graphics.graphical-login': ObservationRule('display_manager66','display_manager_failed','observed',
        'Mislukte displaymanager-unit gemeld','Een specifiek bekende displaymanager staat in systemctl --failed.',
        'Niet bewezen is of dit de huidige sessie, gebruiker of grafische hardware betreft.'),
    'system.slow-boot': ObservationRule('slow_boot66','boot_delay','observed',
        'Opstartfase duurt volgens de begrensde systemd-meting relatief lang',
        'Een voor-gebruikersruimte- of gebruikersruimtefase overschrijdt de onderzoeksdrempel.',
        'De drempel is indicatief en verklaart geen hardware- of service-oorzaak.'),
    'system.system-logs': ObservationRule('critical_journal66','critical_events','observed',
        'Meerdere hooggeprioriteerde journaalgebeurtenissen gezien',
        'Ten minste drie volledig leesbare actuele berichten hebben journald-prioriteit 0–3.',
        'Aantal en prioriteit bepalen niet of de meldingen relevant zijn of dezelfde storing beschrijven.'),
    'audio.sound-missing': ObservationRule('pipewire_state66','pipewire_inactive','observed',
        'PipeWire-gebruikersservice staat niet actief',
        'Een geslaagde vaste systemctl-statusvraag meldt inactive/failed voor PipeWire.',
        'PulseAudio of een andere audioarchitectuur kan bewust worden gebruikt; de geluidsfout is niet bewezen.'),
    'virtualization.vm-feature-absent': ObservationRule('virt_cpu_flags66','virt_flag_not_exposed','observed',
        'CPU-virtualisatiefuncties niet zichtbaar in de huidige Linux-omgeving',
        'De eerste leesbare CPU-flags bevatten geen vmx of svm.',
        'Een gast-VM kan deze flags afschermen; ontbreken van software, firmwareinstelling en fysieke CPU-capaciteit zijn niet beoordeeld.'),
    'system.firmware-update': ObservationRule('service_events59','fwupd_update_failed','observed',
        'Een fwupd-updatefout is in het systeemjournaal aangetroffen',
        'Een expliciete fwupd-melding beschrijft een mislukte firmware-update.',
        'Dit bewijst geen verouderde firmware, hardwaredefect of oorzaak van de huidige klacht.'),
    'system.update-error': ObservationRule('package_container_events61','update_signature_error','observed',
        'Ondertekeningsfout bij een pakketupdate geregistreerd',
        'Een pakketbeheerprogramma meldde een expliciete fout bij handtekeningvalidatie.',
        'Welke update, repository, distributie of sleutel betrokken is, blijft onbekend; validatie nooit omzeilen.'),
}
