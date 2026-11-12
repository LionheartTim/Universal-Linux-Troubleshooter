"""v63 case-specific hardware measurements; provisional signals, no repair routes."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule

OBSERVATION_RULES63 = {
    'hardware34.storage.sata-reallocated': ObservationRule(
        'ata_sectors63','ata_problem_sectors','observed',
        'SMART meldt een niet-nul ATA-probleemsectorteller',
        'Een identificeerbaar ATA/SAT-apparaat rapporteert raw attribuut 5, 197 of 198 boven nul.',
        'Dit bewijst niet dat de SATA-kabel defect is, dat schijfvervanging nu nodig is, of dat dit de gemelde schijf is; gegevens veiligstellen en identiteit controleren.'),
    'hardware34.cooling.fan-rpm-zero': ObservationRule(
        'cooling_rpm63','fan_zero','observed',
        'Een benoemde systeem-/CPU-ventilatorsensor meldt momenteel 0 RPM',
        'Een unieke sysfs-tachometersensor met passende fan-identiteit meldt nul omwentelingen.',
        'Fan-stopbeleid, sensorbedrading, fysieke rotatie en temperatuur zijn niet gecontroleerd; geen defecte ventilator bewezen.'),
    'hardware34.cooling.pump-rpm': ObservationRule(
        'cooling_rpm63','pump_zero','observed',
        'Een eenduidig benoemde pomptachometer meldt momenteel 0 RPM',
        'Een unieke sysfs-fan_input met pump/AIO-label heeft een waarde van nul.',
        'De tachometer kan ontbreken of verkeerd verbonden zijn; geen bewezen stilstaande pomp. Controleer veilig koeltemperaturen, stop bij duidelijke oververhitting.'),
}
