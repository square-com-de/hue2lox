# Hue2Lox: HTTP outputs in Loxone Config

For Loxone Config 17.2. The Miniserver must be able to reach Hue2Lox and its configured bridge. Load and back up the current Miniserver program before editing. Screenshots show the German interface and contain no real credentials. Field labels may differ between Config languages and versions.

## 1. Choose a control mode

Under **Lights**, open **Usage & management**. Type and capability badges come from the Hue Bridge: On/off, Dimmer, Tunable White and RGB. The local model catalog can supplement product names; it never overrides bridge capabilities.

Under **Use with Loxone**, check the modes you need. Your choices are saved and survive a bridge scan. A suitable mode is selected by default:

| Light capabilities | Default |
| --- | --- |
| Color and white temperature | Lumitech RGB + White |
| Color | RGB |
| White temperature without color | Tunable White |
| Brightness only | Dimming |
| Switching only | On/off |

**XML includes all checked modes.** Open **Commands** and select a **Command preview** to copy one variant. Shared fields appear once. At least one mode must remain selected. This does not control the light or update existing Loxone commands.

Only detected modes enabled on the server are offered. For Tunable White, use **Lumitech** in Loxone, select white light and set brightness above 0% to test it. Both Tunable White and Lumitech RGB + White use `{"loxone_lumitech":<v>}`; the latter also supports color.

![Control mode and copy fields in Hue2Lox (German interface)](../web/tutorial-commands.png)

## 2. Create a virtual output

1. Select **Virtual Outputs** in Loxone Config and create a **Virtual Output**, named for example `Hue2Lox`.
2. Enter your Hue2Lox base address, for example `https://192.0.2.96:8443`.
3. Add a **Virtual Output Command** beneath it.

Use the address of your own Hue2Lox server. Do not add a light path or `/health` to this base address.

## 3. Copy the command fields

Copy these fields in the order shown in Hue2Lox:

1. Output command name
2. Command for ON
3. HTTP header for ON
4. HTTP body for ON
5. HTTP method for ON: PUT

**Copy header with token** copies the authorization and Content-Type header. It is one line containing the literal characters `\r\n` between the two headers. Keep these characters exactly as copied. Do not replace them with Enter or add a blank line at the end.

```text
Authorization: Bearer DEIN_HUE2LOX_TOKEN\r\nContent-Type: application/json
```

Replace the placeholder with your token; never use it as an actual token. `<v>` in the body must remain unquoted: Loxone replaces it with the output value.

For existing commands, replace the entire ON header, and the OFF header for On/off commands. Updating Hue2Lox does not alter your Miniserver program. XML uses the same header format; you do not need to reimport a template just to correct a header.

- **On/off:** enable digital output and also copy the OFF fields.
- **Dimming, Tunable White, RGB, Lumitech:** set Unit to `<v>`, disable digital output and leave OFF fields empty. Value 0 switches off. Dimming uses 0–100%; RGB and Lumitech require the matching actuator type on the Lighting Controller.

![Virtual output command properties in Loxone Config (German interface)](../web/tutorial-config.png)

## Alternative: import XML

Select multiple lights and use **Export selection as XML** to create one virtual output with all selected commands. Each separate import creates another output; an existing output is not automatically extended. For later additions, you can create a command manually under the existing output and copy the fields from Hue2Lox.

The **XML** button on a light exports its checked control modes. Each mode gets its own command. Do not connect multiple competing outputs to the same light. Filters limit the visible list; selections remain when filters change.

Import the template under Virtual Outputs in Loxone Config, then check the base address, token and actuator type. By default, XML contains a token placeholder. Including the actual token requires selecting **Token in XML**. That file contains credentials and must not be shared publicly.

## 4. Test from the Miniserver

Connect the command to a suitable test output, save the program to the Miniserver and trigger it deliberately. Start the **HTTP monitor** to inspect the response. HTTP 200 confirms that Hue accepted the request; verify the effect on the light itself.

![Successful response in the HTTP monitor (German interface)](../web/tutorial-monitor.png)

For HTTP 401 check the token; for 403 check whether control is enabled. For **HTTP 400**, start recording, trigger the command again and inspect **Body (sanitized)**: a numeric value rather than a string, a resolved `<v>` and the matching RGB/Lumitech format. Invalid JSON reports its line and column.

`<v.1>` was not confirmed as the cause of the earlier failure. Integer-valued JSON numbers such as `84013.0` are accepted; fractional values are rejected. Inspect the actual body rather than inferring the cause from display formatting alone.

For connection failures, check the address, port and certificate. Trusting a certificate in your browser does not automatically make the Miniserver trust it. Its HTTPS request must work separately.

## Scenes

Create and edit scenes in the Hue app. Under **Scenes**, scan the list and use the command or XML. Trigger a scene using an ON pulse; leave OFF fields empty. Ignored or removed lights can still be controlled by a scene that includes them in Hue.

## Short light paths

Copy the path from the light card. GUI and XML use `/<bridge>/<light>/state`, with at most eight characters per name. Aliases stay stable across renaming and scanning. Legacy long paths and the Hue Go path remain supported. Existing Loxone commands are not changed automatically. Shortening a path alone is not a proven general fix for malformed HTTP framing; use the documented header format and inspect the monitor.
