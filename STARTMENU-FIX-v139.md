# ULTS v139 — native Flatpak startmenu-reparatie

Deze reparatie wordt **meegebouwd in de Flatpak**. Een persoonlijke
`~/.local/share/applications/*.desktop`-aanpassing is niet nodig.

- `flatpak/ults-run`: selecteert Wayland als de socket in de sandbox
  beschikbaar is; kiest anders X11 (`xcb`) wanneer er een X11-display is.
- `flatpak/ults-run-original`: het ongewijzigde oorspronkelijke startscript.
- Het Flatpak-manifest installeert beide scripts in `/app/bin`.
- Het `.desktop`-bestand start `ults-run`, zonder DBusActivatable of
  host-specifieke paden. Flatpak herschrijft deze `Exec=` bij installatie.
- PySide6 en Qt worden door de actuele BaseApp geleverd; er worden geen
  oude PySide6-binaries in de GitHub-bronmap meegeleverd.

## Testen van het echte startmenu

Na het installeren van de nieuwe Flatpak moet een eerdere persoonlijke
ULTS-menukoppeling **eerst geback-upt en gedeactiveerd** worden, anders
blijft KDE die gebruiken in plaats van de nieuwe Flatpak-koppeling.
KDE's cache kan vervolgens worden ververst met `kbuildsycoca6 --noincremental`.

Deze bronmap is gereconstrueerd uit v138. Bestaande metadata of ingebouwde
versiestrings kunnen nog v138 tonen. De oorspronkelijke gitgeschiedenis is
niet in de Flatpak-installatie aanwezig.
