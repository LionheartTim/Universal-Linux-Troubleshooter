# Steam troubleshooting in Manual Diagnostics (v128)

Manual Diagnostics now has a dedicated **Software → Steam** section with **69 beginner-friendly, English troubleshooting guides**. They include Steam startup, sign-in, Flatpak access, updating, downloads, disk space, library moves, native games, Proton, Steam Linux Runtime, controllers and Steam Input, GPU/video/audio issues, cloud saves, Remote Play, Workshop, mods, VR and Wayland.

## What the guides do

- Each guide explains the reported symptom, precautions, two meaningful comparisons, and what results can and cannot establish.
- Each guide is anchored to an **existing** reviewed Manual Diagnostics case. The existing case scan remains read-only; none of these 69 guides is a newly proven diagnosis or a new executable repair path.
- Starting a Steam guide adds the single new read-only `steam_inventory128` probe. It checks Steam Flatpak registration in the two known Flatpak scopes, the existence of known user-local Steam directories, and counts manifest *filenames* only in two bounded local `steamapps` folders. It does **not** read game files, credentials, account data, configuration, manifests' contents, or saves; nor does it open Steam or contact the network. Missing data is `UNKNOWN`, not a fault.
- Steam's other library locations, servers, the correctness of game installations, account eligibility and game compatibility cannot be proved by that inventory. A selected guide's comparisons are meant to help the person investigate those possibilities without risky blanket changes.

## Duplicate password entry

`guide127_38` (“Computer asks for a password every time an app opens”) duplicated the existing, more precise `software35.security.secret-store` (“App repeatedly asks for password after login”). The additional guide was removed; the canonical diagnosis and its two existing solution routes remain intact. There is a *separate* Steam password guide because Steam sign-in, keyring and administrator prompts must be distinguished in that app.

## New-in-version markers

A leading `•` is added only when a guide's `introduced_version` equals the current development guide version. In v128 it marks the **69 new Steam guides**. Guides introduced in v127 remain accessible without the point. A future version must update `CURRENT_GUIDE_VERSION` and mark its own newly added guides, leaving older items unmarked.

## Sources used to check the technical framing

- Valve Proton source and debugging instructions: https://github.com/ValveSoftware/Proton
- Valve Steam Linux Runtime diagnostics: https://github.com/ValveSoftware/steam-runtime/blob/master/doc/reporting-steamlinuxruntime-bugs.md
- Steam Support: Steam Cloud, conflicting and missing saves: https://help.steampowered.com/en/faqs/view/68D2-35AB-09A9-7678
- Flathub documentation: application filesystem permissions: https://docs.flathub.org/docs/for-users/troubleshooting
- Steam/Proton compatibility settings (Ubuntu documentation): https://ubuntu.com/docs/steam/howto/configure-proton/

These sources inform the guide phrasing; they do not certify a particular local fault. Steam menus and Proton behavior can change over time. Always prioritize the user-visible version and evidence.
