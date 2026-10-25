# Security / Sicherheit

Hue2Lox has published stable releases; 1.0.2 is currently published and 1.0.3 is unreleased preparation. No fixed security-support period or response-time commitment is offered. It is intended for a trusted local network. Do not expose the admin interface directly to the Internet.

Fresh installations generate their own control token. Docker/Podman default to plain HTTP; built-in HTTPS requires explicitly configured certificate/key files, while a reverse proxy manages its own TLS. The native installer generates a self-signed certificate/key. The initial login is `admin` / `admin`; change it in the web interface before wider use. Keep private backups protected. Use HTTPS when transport encryption is required, with a verified certificate or trust setup; do not permanently disable TLS verification.

Do not report credentials, unredacted HTTP headers, private keys or exploitable vulnerability details in a public issue. Use GitHub private vulnerability reporting if enabled for this repository; otherwise contact the maintainer through an existing private channel before sharing details. No response-time guarantee is offered.

If a token or key was exposed, remove the exposure and replace the affected credential. Deleting the current file alone does not remove it from Git history. Review history separately before publication.

Deutsch: Sicherheitsprobleme vertraulich melden. Keine Tokens, Passwörter oder privaten Schlüssel in Issues, Screenshots oder Logs veröffentlichen. Das Standardpasswort nach der Einrichtung ändern; die Oberfläche nicht direkt ins Internet stellen.
