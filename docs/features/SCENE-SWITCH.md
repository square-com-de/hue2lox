# Scenes as on/off lighting circuits — development after RC6

This optional extension belongs to the feature PR for [issue 42](https://github.com/square-com-de/hue2lox/issues/42), not the published RC6. Existing configurations are not migrated automatically. Hardware acceptance remains open.

## Setup

1. Rescan the inventory under **Scenes**. This does not recall a scene.
2. Open the scene's **Management → Scene usage mode**. **Recall only** remains the default.
3. Select the target group and inspect **every listed lamp**, including hidden lamps and overlapping groups. Only fully resolvable Hue rooms/zones containing every scene lamp and having an unambiguous grouped-light endpoint are offered.
4. Explicitly confirm the full-group effect and save. If the inventory changed in the meantime, review and confirm again.
5. Export XML again and use the **digital**, not analog output as a lighting circuit in the Loxone Lighting Controller. ON sends `{"on":true}`, OFF sends `{"on":false}` to `/api/scenes/<bridge>/<scene>/state`. Repetition stays 0. Existing Loxone projects are not changed automatically.

ON recalls the saved Hue scene without any additional dimming value. OFF switches off **the entire confirmed group**, including lamps the scene does not change. There is no native Hue scene-OFF endpoint. Changed group membership or scene assignment blocks the on/off endpoint until reconfirmed after a rescan. Changes outside Hue2Lox become known only after rescanning; always rescan after changing the Hue configuration before using it again.

## Scene changes and limitations

Hue2Lox serializes scene commands without an artificial ON delay. For A and B on the same group, both sequences work: A ON → A OFF → B ON, and A ON → B ON → A OFF. In the second case the superseded A OFF is ignored without a Hue request. The monitor identifies ignored commands rather than claiming Hue confirmation. The first sequence can briefly switch the group off before B; flicker-free changes are not promised.

Repeated OFF for an already inactive scene is ignored. Repeated ON recalls the scene again; there are no delayed background actions. For overlapping groups, switch the active group off first. Otherwise ON returns HTTP 409 without writing to Hue. Disjoint groups remain independent, although execution is still serialized.

Ownership is **command history, not observed lamp state**, and provides no state feedback to Loxone. After restart, changed configuration or a recall-only call, ownership is unknown: send ON for the desired scene first. OFF without clear ownership returns HTTP 409. A timeout or Hue partial error does not claim success (HTTP 502); the physical outcome may be uncertain. Overlapping groups remain blocked in this case until a successful ON on the same group restores ownership. There are no automatic retries or reactivation. A deliberate ON may turn the lights on again.

**Unavoidable ambiguity without event identifiers:** In A ON → B ON → A ON → A OFF, the final command may be a delayed OFF from the first activation or the real OFF for the new activation. Static Loxone outputs provide no activation identifier. Ordering starts when a fully validated command enters the queue, not at network arrival. That queue order applies: the final A OFF switches off the currently assigned group. There is no guarantee against arbitrarily delayed commands, and a fixed delay cannot resolve this ambiguity.

The Hue app, physical switches, ordinary lamp outputs and other integrations may change lamps independently. These changes are not reflected in scene command ownership. Avoid parallel control paths for the same lamps when relying on scene on/off circuits. Existing recall-only endpoints and XML remain available.

## Acceptance still required

Automated tests use synthetic bridge responses only, covering both orders, rapid changes, repetitions, final OFF, group isolation/overlap, concurrency, restart, timeout/partial errors, token/CSRF and XML. They do not establish actual Hue or Loxone command ordering. Before approval, use an explicitly chosen test environment to check real A/B and rapid A/B/C changes, final OFF and visible full-group effects. Record monitor evidence without tokens or keys. No production measurements or automatic migration.
