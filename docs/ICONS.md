# Original Hue2Lox light icons

Selected by the project owner on 19 October 2026: the modern set of twenty-one selectable lamp shapes plus a legacy fallback. Sources are editable SVGs in `web/lamp-icons/`; the matching bundled geometry and metadata resolver are in `web/lamp-icons.js`.

The icons were independently drawn from simple SVG geometry for Hue2Lox. They do not contain paths from the former community icon bundle and do not claim official manufacturer endorsement or an exact depiction of every device. Bulb, candle, spot, flat ceiling light, pendant, vertical floor light, dome table light, portable bowl, strip and up/down wall light represent categories. Unknown devices use a recognizable bulb symbol as a visual fallback; this does not assert their actual device type.

All icons use a 64×64 viewBox, no fill, rounded 2.3-unit strokes and currentColor. Existing on/off/unavailable styles remain. Lamp capabilities continue to be shown separately as badges.

Stored legacy icon identifiers are translated to the new categories without retaining the old artwork. Resolution order: saved manual override, known model (LCW004 outdoor wall light, LLC020/LCT026 portable bowl), bridge archetype, legacy stored icon, bulb fallback. Under Lamps → Usage & management → Light icon, users can select a shape or Automatic. This preference persists in the registry across restarts and rescans and does not change capabilities, HTTP commands or XML. No device commands are sent by rendering icons.

The original SVG icons are licensed under Apache License 2.0; see LICENSE and NOTICE. This does not relicense historical third-party icons.

The old icon assets and current runtime attribution have been removed. Historical commits, backups and already-built old images still contain the former assets and retain their original terms. This change does not rewrite history or delete backups.

Additional product families and model assignments: [research notes](ICON-RESEARCH.md) and `catalog/lamp-icon-models.json`. Only exact catalog model IDs are mapped; manual overrides always win.

Resonate (`1746430P7`, `929003553001`) uses a compact rectangular wall-light symbol; filament model `LTO001` uses a visible-filament bulb symbol. These exact model mappings override broad bridge archetypes such as `wall_lantern` and `vintage_bulb`. Both shapes are also available as manual choices.
