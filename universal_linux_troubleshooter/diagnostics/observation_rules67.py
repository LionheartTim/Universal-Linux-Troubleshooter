"""Evidence is strictly observational: none of these rules approve any route."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule
OBSERVATION_RULES67 = {
 'applications.cpu-high': ObservationRule('cpu_pressure67','cpu_pressure','observed',
   'Actuele CPU-wachtdruk waargenomen','De lokale PSI avg10 ligt op of boven de onderzoeksdrempel van 30%.',
   'Geen proces, oorzaak of aanhoudend CPU-verbruik bewezen; controle op het juiste moment blijft nodig.'),
 'virtualization.vm-slow': ObservationRule('cpu_pressure67','cpu_pressure','observed',
   'CPU-wachtdruk in de huidige Linux-omgeving waargenomen','De lokale PSI avg10 ligt op of boven de onderzoeksdrempel van 30%.',
   'Dit is niet aantoonbaar een VM-meting; host- of gastcontext en vertragingsoorzaak blijven onbekend.'),
 'software35.desktop.xdg-default-browser': ObservationRule('browser_handlers67','browser_handler_difference','observed',
   'Twee lokale browser-voorkeursinstellingen verschillen','De xdg-settings standaardbrowser wijkt af van de x-scheme-handler/https instelling.',
   'Niet bewezen welke browser de gebruiker wil of welke handler in de applicatie wordt gebruikt.'),
 'software35.packages.atomic-rollback': ObservationRule('rollback_slot67','alternate_deployment','observed',
   'Een alternatief rpm-ostree-deployment staat lokaal geregistreerd',
   'De lokale status bevat één booted deployment en een afzonderlijk niet-gestaged deployment.',
   'Geen update-regressie, veilige rollback of beschikbare oude werkende versie bewezen.'),
}
