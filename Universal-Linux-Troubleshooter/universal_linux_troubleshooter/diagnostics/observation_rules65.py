"""v65 direct signals remain *provisional* and never approve repairs."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule

OBSERVATION_RULES65 = {
    'software35.packages.pacman-orphans': ObservationRule(
        'arch_orphans65','arch_orphans','observed',
        'De lokale pacman-database heeft één of meer niet-vereiste afhankelijkheden gevonden',
        'Een geslaagde pacman -Qdtq query geeft geldige, unieke pakketnamen terug.',
        'De markering orphan is geen bewijs dat het pakket voor deze gebruiker overbodig is, en '
        'ook geen bewijs dat het de opslagklacht veroorzaakt. Verwijder niets automatisch.'),
    'hardware34.gpu.cooling-fan': ObservationRule(
        'gpu_fan_fault65','gpu_fan_fault','observed',
        'Een expliciet geïdentificeerde GPU-hardwaremonitor meldt een fan-foutstatus',
        'Een bekende GPU-hwmon-driver heeft minstens één fanN_fault=1 gemeld.',
        'Dit bewijst geen stilstaande fan of defecte GPU; de oorzaak van warmte/geluid is onbekend. '
        'Als de driver geen fan_fault aanbiedt, blijft de status onbekend.'),
}
