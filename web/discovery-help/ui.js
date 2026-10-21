// This file is bundled with the scripts; no scripts are fetched or executed by the browser.
const discoveryMessages = {
  MISSING_DNSSD: 'Dieses Skript benötigt macOS mit dns-sd.',
  SEARCH_MAC: 'Suche Hue Bridges lokal (bei drei Bridges ungefähr 21 Sekunden) …',
  SEARCH: 'Suche Hue Bridges im lokalen Netzwerk …',
  NONE: 'Keine Bridges gefunden. Netzwerkverbindung, VPN und Firewall prüfen oder die Bridge-IP im Router nachsehen.',
  NO_HOST: 'Hostname nicht aufgelöst',
  NO_IPV4: 'Keine IPv4-Antwort innerhalb von 3 Sekunden',
  MISSING_AVAHI: 'avahi-browse fehlt. Debian/Ubuntu: sudo apt install avahi-utils; Fedora: sudo dnf install avahi-tools.',
  AVAHI_SERVICE: 'Avahi-Dienst prüfen: systemctl status avahi-daemon',
  FAILED: 'Lokale Suche fehlgeschlagen:'
};
function localDiscoveryCommand(platform) {
  const script = localDiscoveryScripts[platform].replace(/@@([A-Z0-9_]+)@@/g, (_, key) => {
    // Templates use single-quoted messages in shell and PowerShell.
    const message = t(discoveryMessages[key]);
    return platform === 'windows' ? message.replaceAll("'", "''") : message.replaceAll("'", "'\\''");
  });
  return platform === 'windows' ? script : "bash <<'HUE2LOX_LOCAL_SEARCH'\n" + script + "HUE2LOX_LOCAL_SEARCH\n";
}
async function copyDiscoveryCommand(code, status) {
  const value = code.textContent;
  try {
    if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(value);
  } catch (_) {
    // HTTP LAN pages may lack the modern Clipboard API. Try the legacy copy path.
    const area = document.createElement('textarea');
    area.value = value; area.setAttribute('readonly', '');
    area.style.position = 'fixed'; area.style.opacity = '0';
    document.body.append(area); area.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } catch (_) {}
    area.remove();
    if (!copied) {
      const range = document.createRange(); range.selectNodeContents(code);
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      status.textContent = t('Automatisches Kopieren nicht möglich. Der Befehl ist markiert: mit Strg+C oder Cmd+C kopieren.');
      return;
    }
  }
  status.textContent = t('Kopiert – jetzt im Terminal einfügen.');
}
function renderDiscoveryHelp() {
  const parent = document.getElementById('discovery-help-platforms');
  if (!parent) return;
  const platforms = [
    ['macos', 'macOS – Terminal', 'Ohne Zusatzinstallation. Bei drei Bridges dauert die Suche ungefähr 21 Sekunden.'],
    ['windows', 'Windows – PowerShell', 'Windows PowerShell 5.1 oder PowerShell 7. Ohne Administratorrechte oder Zusatzinstallation. Die Suche dauert ungefähr 6 Sekunden.'],
    ['linux', 'Linux – Terminal', 'Benötigt Bash und avahi-browse sowie einen laufenden Avahi-Dienst. Die Suche dauert ungefähr 5 Sekunden.']
  ];
  for (const [platform, title, description] of platforms) {
    const details = document.createElement('details');
    const summary = document.createElement('summary'); summary.textContent = t(title);
    const hint = document.createElement('p'); hint.textContent = t(description);
    const pre = document.createElement('pre');
    const code = document.createElement('code'); code.textContent = localDiscoveryCommand(platform); pre.append(code);
    const button = document.createElement('button'); button.type = 'button'; button.className = 'secondary';
    button.textContent = t('Befehl kopieren'); button.setAttribute('aria-label', t('Befehl kopieren') + ': ' + t(title));
    const status = document.createElement('p'); status.setAttribute('role', 'status');
    button.addEventListener('click', () => copyDiscoveryCommand(code, status));
    details.append(summary, hint);
    if (platform === 'linux') {
      const dependency = document.createElement('p');
      dependency.textContent = t('Falls avahi-browse fehlt: Debian/Ubuntu: sudo apt install avahi-utils · Fedora: sudo dnf install avahi-tools. Als root sudo weglassen.');
      details.append(dependency);
    }
    details.append(button, status, pre); parent.append(details);
  }
}
renderDiscoveryHelp();
