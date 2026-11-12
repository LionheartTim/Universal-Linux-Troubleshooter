"""Extra beginner-friendly problem entries, grounded in the existing Manual trees.

These guides are *entry points*, not new diagnosed failures or remedy gates.
No commands, permission changes, repairs or network requests are performed.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import re
from pathlib import Path

from .peripheral_topics48 import TOPICS as LEGACY_TOPICS
from ..knowledge.diagnosis_trees import load_trees

DATA = Path(__file__).resolve().parents[2] / 'knowledge_sources' / 'supplemental_problem_guides127.json'
STEAM_DATA = DATA.parent / 'steam_problem_guides128.json'
# New-in-this-release is a UI marker, never a diagnostic distinction.
CURRENT_GUIDE_VERSION = 135

# Older peripheral help was written partly in Dutch. Replacing the displayed
# guidance has no effect on the underlying reviewed diagnosis tree or evidence.
_OLDER_GUIDES_EN = {
'mouse_wired': ('Stop tasks that could be disrupted by unexpected pointer movement.', 'Check the USB connection and, if safe, try a different suitable port directly on the computer.', 'Compare with a known working mouse, if one is available.', 'A change between ports suggests a connection-path issue; it does not prove a bad port.'),
'mouse_wireless': ('Keep a working pointer or keyboard available before changing connections.', 'Check the mouse power and battery; identify whether it uses Bluetooth or a USB receiver.', 'If it uses a receiver, try a direct USB port; if Bluetooth, check its connection without deleting a working pairing.', 'Receiver and Bluetooth problems require different checks.'),
'keyboard_wired': ('Do not enter passwords while keys are behaving unpredictably.', 'Check the USB connection and try another suitable port if safe.', 'Compare with a working keyboard; check the selected keyboard layout when only individual keys differ.', 'Wrong characters can result from a layout mismatch rather than a failed keyboard.'),
'keyboard_wireless': ('Keep an alternative way to log in before changing wireless input settings.', 'Check power, battery and which receiver or Bluetooth host the keyboard uses.', 'Confirm the connection; do not remove a working pairing just to run a test.', 'A missing response does not by itself prove that the keyboard is faulty.'),
'touchpad': ('Do not open the laptop or disconnect internal cables.', 'Check the laptop touchpad shortcut or switch and its desktop setting.', 'If necessary, use an external mouse to navigate while ULTS reads the input-device information.', 'An external mouse working does not establish a failed touchpad.'),
'headphones_jack': ('Start at a low volume to avoid sudden loud sound.', 'Check the correct 3.5 mm socket and whether a combined headset requires a compatible splitter.', 'Compare with a known working headset or audio socket, if available.', 'No microphone signal can also reflect the selected input or application permission.'),
'headphones_usb': ('Start with low volume and stop active recordings before disconnecting devices.', 'Try a suitable direct USB port, avoiding the same hub.', 'For a removable cable, compare with a known working USB data cable.', 'USB recognition alone does not prove audio routing or microphone access works.'),
'headphones_bluetooth': ('Keep the volume low and end calls before switching audio profiles.', 'Check the battery, range and whether the headset is connected to the intended computer.', 'If audio breaks up, compare at a shorter distance without wiping the pairing.', 'Range, audio profile and application settings may all matter.'),
'microphone': ('Do not record or share private conversations as a test.', 'For USB microphones, check the mute switch and connection; skip USB checks for built-in microphones.', 'Check the input source and permissions in the application you are using.', 'A listed microphone does not guarantee that sound is being captured.'),
'webcam': ('ULTS will not turn on your camera or capture photos.', 'Check the privacy shutter and camera switch.', 'For an external camera, compare another suitable direct USB port; skip this for built-in cameras.', 'Privacy controls, application permissions and drivers can all cause a black image.'),
'printer': ('Stop current print jobs before changing a USB connection; avoid hot printer components.', 'For USB printers, try a suitable data cable and a direct USB port.', 'For network printers, investigate the network connection instead of the USB port.', 'A stable USB connection does not rule out a stuck print queue or driver problem.'),
'scanner': ('Stop the scan before disconnecting anything.', 'Check the scanner power supply and cable.', 'If it is an external USB scanner, try a suitable direct port.', 'USB detection does not prove the scanning application supports the scanner.'),
'gamepad': ('Stop active gameplay before disconnecting the controller.', 'For a wired gamepad, check the USB data cable and suitable direct port.', 'For a wireless controller, check the battery, receiver or Bluetooth pairing.', 'A detected controller is not proof that its buttons generate input events.'),
'dock': ('Safely unmount external storage and stop copying files before unplugging a dock.', 'Check that the cable and port support the dock features being used.', 'If safe, compare one device connected directly with the same device connected through the dock.', 'A successful direct connection points toward the dock path, not a proven defective dock.'),
'touchscreen': ('Do not open the device or reset it without a reason.', 'Check whether the image displays normally while touch input is missing.', 'For external touch monitors, check whether touch needs a separate USB data cable.', 'Working video does not prove the touch interface works.'),
'fingerprint': ('Keep a working password or other login method available.', 'For an external reader, check its USB connection; skip this for built-in sensors.', 'Check whether the fingerprint reader is supported by the available login software.', 'Hardware detection alone does not establish software compatibility.'),
'usb_storage': ('Protect important data; stop repeated tests if you see I/O errors or hear clicking.', 'Safely eject the drive before changing connections.', 'If it is safe and data is protected, compare a suitable direct USB port and cable.', 'Do not format or attempt filesystem repairs as a diagnostic shortcut.'),
'speakers': ('Start with low volume; switch off external amplifiers before changing analogue cables.', 'Check the speaker power and cable, or skip these checks for built-in speakers.', 'Compare a known working audio output if available.', 'A distorted signal can come from the audio profile, source level or speakers.'),
}

@dataclass(frozen=True)
class SymptomGuide:
    key: str
    title: str
    case_id: str
    domain: str
    heading: str
    search_terms: tuple[str, ...]
    precautions: tuple[str, ...]
    comparison: tuple[str, ...]
    interpretations: tuple[str, ...]
    introduced_version: int = 0

    def describe(self) -> str:
        return '\n\n'.join((
            'A CLOSER LOOK AT YOUR PROBLEM',
            self.title,
            'BEFORE YOU START\n' + '\n'.join('• ' + x for x in self.precautions),
            'WHAT TO TRY\n' + '\n'.join(f'{i}. {x}' for i, x in enumerate(self.comparison, 1)),
            'WHAT THE RESULTS MEAN\n' + '\n'.join('• ' + x for x in self.interpretations),
            'When you have finished, choose Rescan to refresh the available local checks. '
            'These observations cannot, by themselves, confirm the cause. '
            'ULTS will not change settings or repair anything for you.',
        ))

@lru_cache(maxsize=1)
def all_topics() -> tuple[SymptomGuide, ...]:
    catalog = load_trees()['cases']
    extras = json.loads(DATA.read_text(encoding='utf-8'))
    if extras.get('schema_version') != 1:
        raise ValueError('Unsupported symptom-guide version')
    topics = []
    for old in LEGACY_TOPICS:
        if old.key not in _OLDER_GUIDES_EN:
            raise ValueError('Missing English guide for ' + old.key)
        precautions, step1, step2, outcome = _OLDER_GUIDES_EN[old.key]
        topics.append(SymptomGuide(old.key, old.title, old.case_id,
                     catalog[old.case_id]['domain'], 'Peripherals & Devices',
                     old.search_terms, (precautions,), (step1, step2), (outcome,)))
    steam = json.loads(STEAM_DATA.read_text(encoding='utf-8'))
    if steam.get('schema_version') != 1:
        raise ValueError('Unsupported Steam guide version')
    for raw in [*extras['guides'], *steam['guides']]:
        for field in ('key', 'title', 'case_id', 'domain', 'heading', 'search_terms', 'precautions', 'comparison', 'interpretations'):
            if not raw.get(field):
                raise ValueError(f'Missing guide field {field}')
        if raw['case_id'] not in catalog or catalog[raw['case_id']]['domain'] != raw['domain']:
            raise ValueError('Invalid guide-to-case mapping: ' + raw['key'])
        topics.append(SymptomGuide(*(raw[k] if k in ('key', 'title', 'case_id', 'domain', 'heading')
                           else tuple(raw[k]) for k in ('key', 'title', 'case_id', 'domain', 'heading', 'search_terms', 'precautions', 'comparison', 'interpretations')),
                           introduced_version=128 if raw['key'].startswith('steam128_') else 127))
    if len({x.key for x in topics}) != len(topics):
        raise ValueError('Duplicate symptom guide')
    return tuple(topics)

BY_KEY = {topic.key:topic for topic in all_topics()}

def matching_topics(search: str = '', *, domain: str | None = None, heading: str | None = None) -> tuple[SymptomGuide, ...]:
    term = search.casefold().strip()[:150]
    words = tuple(re.findall(r"[\w]+", term))
    def matches(topic: SymptomGuide) -> bool:
        if not term:
            return True
        title = topic.title.casefold()
        aliases = ' '.join(topic.search_terms).casefold()
        haystack = ' '.join((title, topic.case_id.casefold(), aliases))
        return (term in haystack
                or (len(words) >= 2 and all(
                    any(part.startswith(word) or word.startswith(part)
                        for part in re.findall(r"[\w]+", haystack))
                    for word in words)))
    return tuple(t for t in all_topics()
                 if (domain is None or t.domain == domain)
                 and (heading is None or t.heading == heading)
                 and matches(t))

def guide_for_topic(topic_key: str, case_id: str) -> SymptomGuide:
    topic = BY_KEY[topic_key]
    if topic.case_id != case_id:
        raise ValueError('Symptom guide does not belong to the selected case')
    return topic
