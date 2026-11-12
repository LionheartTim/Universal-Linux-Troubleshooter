"""v64 cautiously attributed direct observations; no repair routes."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule

OBSERVATION_RULES64 = {
    'hardware34.cooling.sensor-disconnect': ObservationRule(
        'thermal_fault64','temp_sensor_fault','observed',
        'Een temperatuurmonitor meldt een onbetrouwbare sensormeting',
        'Minstens één begrensd gelezen sysfs tempN_fault-bestand meldt precies 1.',
        'Dit bewijst geen losse kabel, defecte sensor of daadwerkelijke temperatuur. Bij ontbrekende driverondersteuning blijft de status onbekend.'),
    'software35.flatpak.duplicate-scope': ObservationRule(
        'flatpak_scopes64','app_both_scopes','observed',
        'Eén Flatpak-app-ID komt voor in gebruikers- én standaardsysteemscope',
        'Twee geslaagde alleen-lezen Flatpak-overzichten bevatten dezelfde exacte app-ID.',
        'Meerdere installaties zijn toegestaan; dit bewijst geen versie-, bron- of startconflict. Geen scope wissen of bron wisselen.'),
}
