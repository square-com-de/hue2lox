# Scenes as on/off lighting circuits

Available in Stable 1.0.0. On 24 October 2026 the user confirmed scene switching and final OFF with Hue and Loxone in the Portainer test stack. Existing Loxone commands are not rewritten.

## Setup

**On/off is visible directly in each scene row and is the default.** If exactly one group contains precisely the same lamps as the scene, Hue2Lox assigns it automatically at startup or during a scan. No checkbox or extra Save step. The assignment is stored locally without recalling a scene.

1. Scan scenes. An already known, uniquely matching group works after the update without another selection.
2. The OFF group appears beside **Control: On/off**. Its lamps, including hidden lamps and overlapping groups, are visible directly.
3. If several groups match exactly, or only larger groups exist, choose a group. Selection saves immediately. Larger groups are never selected automatically; additional lamps are explicitly listed by name. Until a group is chosen there is no on/off XML or misleading fallback command.
4. Export XML and use the **digital**, not analog output as a lighting circuit in the Loxone Lighting Controller. ON sends `{"on":true}`, OFF sends `{"on":false}` to `/api/scenes/<bridge>/<scene>/state`. Repetition stays 0.
5. For the existing scene-recall behavior, choose **Recall only** directly. This preference survives restarts and scans; its export contains only recall, as before.

ON recalls the saved Hue scene without an additional dimming value. OFF switches off **the entire assigned group**, including additional lamps. There is no native Hue scene-OFF endpoint. Rescan after changes in Hue. If saved group membership or scene assignment changes, no new group is silently selected: the UI shows current lamps and asks you to choose the group again. A placeholder allows choosing the same changed group again. Stale selections are rejected; no confirmation checkbox is needed.

Existing explicit group assignments are retained. Existing recall endpoints and imported Loxone commands continue to work and are not rewritten. New exports use the displayed mode. Older records without a saved mode/group are considered undecided: on/off becomes the default, automatically usable only with a unique exact group. The first PR45 version did not store a reset-to-recall preference, so those old choices cannot be reconstructed. New explicit recall preferences are stored. Published RC packages remain unchanged.

## Scene changes and limitations

Hue2Lox serializes scene commands without an artificial ON delay. For A and B on the same group, both sequences work: A ON → A OFF → B ON, and A ON → B ON → A OFF. In the second case the superseded A OFF is ignored without a Hue request. The monitor identifies ignored commands rather than claiming Hue confirmation. The first sequence can briefly switch the group off before B; flicker-free changes are not promised.

Repeated OFF for an already inactive scene is ignored. Repeated ON recalls the scene again; there are no delayed background actions. For overlapping groups, switch the active group off first. Otherwise ON returns HTTP 409 without writing to Hue. Disjoint groups remain independent, although execution is still serialized.

Ownership is **command history, not observed lamp state**, and provides no state feedback to Loxone. After restart, changed configuration or a recall-only call, ownership is unknown: send ON for the desired scene first. OFF without clear ownership returns HTTP 409. A timeout or Hue partial error does not claim success (HTTP 502); the physical outcome may be uncertain. Overlapping groups remain blocked in this case until a successful ON on the same group restores ownership. There are no automatic retries or reactivation. A deliberate ON may turn the lights on again.

**Unavoidable ambiguity without event identifiers:** In A ON → B ON → A ON → A OFF, the final command may be a delayed OFF from the first activation or the real OFF for the new activation. Static Loxone outputs provide no activation identifier. Ordering starts when a fully validated command enters the queue, not at network arrival. That queue order applies: the final A OFF switches off the currently assigned group. There is no guarantee against arbitrarily delayed commands, and a fixed delay cannot resolve this ambiguity.

The Hue app, physical switches, ordinary lamp outputs and other integrations may change lamps independently. These changes are not reflected in scene command ownership. Avoid parallel control paths for the same lamps when relying on scene on/off circuits. Existing recall-only endpoints and XML remain available.

## Candidate-specific acceptance

Automated tests use synthetic bridge responses only, covering both orders, rapid changes, repetitions, final OFF, group isolation/overlap, concurrency, restart, timeout/partial errors, token/CSRF and XML. They do not establish actual Hue or Loxone command ordering. Before approval, use an explicitly chosen test environment to check real A/B and rapid A/B/C changes, final OFF and visible full-group effects. Record monitor evidence without tokens or keys. No production measurements or automatic migration.

The user observation of 24 October 2026 applies to the recorded 1.0.0/1.0.1 revision, not a new 1.0.3 qualification. [Open hardware checklist #42](https://github.com/square-com-de/hue2lox/issues/42).
