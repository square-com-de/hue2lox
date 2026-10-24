'use strict';
let adminSession=null,loxoneData=null;
const selectedLights=new Set();
const lampModes=new Map();
const openLampOptions=new Set();
function selectedCommand(light){const enabled=light.commands.filter(c=>light.enabled_modes.includes(c.id));return enabled.find(c=>c.id===lampModes.get(light.key))||enabled.find(c=>c.id===light.recommended_mode)||enabled[0];}
const usageSaving=new Set();
async function saveLampUsage(light,modes){if(usageSaving.has(light.key))return;if(!modes.length){document.querySelector('#lamp-message').textContent=t('Mindestens eine Nutzungsart auswählen.');renderLights();return;}usageSaving.add(light.key);try{const [bridge_id,light_id]=light.key.split('/');const response=await adminRequest('/api/admin/lights/usage',{bridge_id,light_id,modes});if(!response.ok)throw Error();await loadLoxone();document.querySelector('#lamp-message').textContent=t('Nutzungsarten gespeichert. XML enthält die angehakten Varianten. Bestehende Loxone-Befehle bleiben unverändert.');}catch(error){document.querySelector('#lamp-message').textContent=t('Nutzungsarten konnten nicht gespeichert werden.');}finally{usageSaving.delete(light.key);renderLights();}}
let revealTimer,openCommandKey=null;
function hideToken(){clearTimeout(revealTimer);const field=document.querySelector('#control-token');field.value='';field.type='password';document.querySelector('#show-token').textContent=t('Token anzeigen');}
function lockAdmin(message=''){const passwordDialog=document.querySelector('#password-dialog');if(passwordDialog.open)passwordDialog.close();document.querySelector('#password-form').reset();bridgeManagementReset();resetScenes();openCommandKey=null;adminSession=null;loxoneData=null;selectedLights.clear();lampModes.clear();openLampOptions.clear();hideToken();document.body.classList.add('locked');document.querySelector('#login-message').textContent=message;resetDiscovery();resetMonitor();filteredLights=[];document.querySelector('#token-message').textContent='';document.querySelector('#include-token').checked=false;document.querySelector('#loxone-message').textContent='';updateSelection();for(const id of ['search','bridge-filter','room-filter'])document.querySelector('#'+id).value='';document.querySelector('#light-list').replaceChildren();document.querySelector('#login-password').value='';}
async function adminRequest(path,body){const options={cache:'no-store',credentials:'same-origin'};if(body!==undefined){options.method='POST';options.headers={'Content-Type':'application/json'};if(adminSession)options.headers['X-CSRF-Token']=adminSession.csrf;options.body=JSON.stringify(body);}const response=await fetch(path,options);if(response.status===401&&path!=='/api/admin/login')lockAdmin(t('Sitzung abgelaufen. Bitte erneut anmelden.'));return response;}
async function bootAdmin(){try{const response=await adminRequest('/api/admin/session');if(response.ok){adminSession=await response.json();await unlockAdmin();}else lockAdmin();}catch(e){lockAdmin(t('Dienst nicht erreichbar. Bitte erneut versuchen.'));}}
async function unlockAdmin(){document.body.classList.remove('locked');document.querySelector('#login-password').value='';document.querySelector('#admin-user').textContent=adminSession.username;await Promise.all([refresh(),loadLoxone(),loadBridgeManagement(),loadScenes(),loadMiniserver()]);}
async function loadLoxone(){const session=adminSession;if(!session)return;const response=await adminRequest('/api/admin/lights');if(session!==adminSession)return;if(!response.ok){document.querySelector('#loxone-message').textContent=t('Lampenbefehle konnten nicht geladen werden.');return;}loxoneData=await response.json();const available=new Set(loxoneData.lights.filter(l=>l.available).map(l=>l.key));for(const key of selectedLights)if(!available.has(key))selectedLights.delete(key);renderLoxoneList();}
function renderLoxoneList(){renderLights();updateSelection();}
function lampCommands(l){
 const key=l.bridge.id+'/'+l.id,light=loxoneData?.lights.find(item=>item.key===key),available=!!light?.available;
 const box=node('div',undefined,'lamp-command-area'),row=node('div',undefined,'lamp-actions'),label=node('label',undefined,'lamp-select'),check=node('input');check.type='checkbox';check.disabled=!available;check.checked=selectedLights.has(key);check.setAttribute('aria-label',t('Für XML auswählen: ')+l.name);check.onchange=()=>{check.checked?selectedLights.add(key):selectedLights.delete(key);updateSelection();};label.append(check,node('span',t('Auswählen')));row.append(label);
 const panel=node('div',undefined,'lamp-command-details');panel.hidden=openCommandKey!==key||!available;
 panel.id='lamp-command-'+l.bridge.id+'-'+l.id;
 const toggle=node('button',panel.hidden?t('Befehle ▾'):t('Befehle schließen ▴'),'secondary command-toggle');toggle.disabled=!available;toggle.setAttribute('aria-expanded',String(!panel.hidden));toggle.setAttribute('aria-controls',panel.id);toggle.onclick=()=>{hideToken();openCommandKey=openCommandKey===key?null:key;renderLights();};
 function managementPanel(){
  const options=node('div',undefined,'lamp-options');options.hidden=!openLampOptions.has(key);options.id='lamp-options-'+l.bridge.id+'-'+l.id;
  const button=node('button',undefined,'secondary management-toggle');button.type='button';button.setAttribute('aria-controls',options.id);
  const sync=()=>{button.textContent=t('Nutzung & Verwaltung')+(options.hidden?' ▾':' ▴');button.setAttribute('aria-expanded',String(!options.hidden));};
  button.onclick=()=>{options.hidden=!options.hidden;options.hidden?openLampOptions.delete(key):openLampOptions.add(key);sync();};sync();row.insertBefore(button,toggle);return options;
 }
 const xml=node('button' ,'XML','secondary');xml.disabled=!available;xml.setAttribute('aria-label',t('XML für ')+l.name+t(' herunterladen'));xml.onclick=()=>downloadXML([key]);const modeLabel=node('label',undefined,'lamp-mode');modeLabel.append(node('span',t('Befehlsvorschau')));const mode=node('select');mode.setAttribute('aria-label',t('Steuerungsart für ')+l.name);mode.disabled=!available;if(light){for(const command of light.commands.filter(c=>light.enabled_modes.includes(c.id)))mode.append(new Option(t(command.name)+(command.id===light.recommended_mode?t(' (empfohlen)'):''),command.id));mode.value=selectedCommand(light).id;mode.onchange=()=>{lampModes.set(key,mode.value);if(!panel.hidden)showCommands(light,panel);};}modeLabel.append(mode);modeLabel.hidden=panel.hidden;row.append(toggle,xml,modeLabel);if(light){const options=managementPanel();if(l.product_name)options.append(node('p',l.product_name,'sub'));const usage=node('fieldset',undefined,'lamp-usage');usage.append(node('legend',t('Für Loxone nutzen')));for(const command of light.commands){const label=node('label'),input=node('input');input.type='checkbox';input.checked=light.enabled_modes.includes(command.id);input.disabled=usageSaving.has(key)||!available;input.setAttribute('aria-label',t(command.name)+t(' nutzen für ')+l.name);input.onchange=()=>{const modes=light.enabled_modes.filter(id=>id!==command.id);if(input.checked)modes.push(command.id);saveLampUsage(light,modes);};label.append(input,node('span',t(command.name)+(command.id===light.recommended_mode?t(' (empfohlen)'):'')));usage.append(label);}options.append(lampIconPicker(l),usage,lampActions(l));box.append(options);}else{const options=managementPanel();options.append(lampIconPicker(l),lampActions(l));box.append(options);}box.prepend(row);box.append(panel);if(!panel.hidden)showCommands(light,panel);return box;
}
function updateSelection(){document.querySelector('#export-selected').disabled=!selectedLights.size;document.querySelector('#export-selected').textContent=t('Auswahl als XML (')+selectedLights.size+')';}
function loxoneHTTPHeader(token){return 'Authorization: Bearer '+token+'\\r\\nContent-Type: application/json';}
function copyButton(text,value){const button=node('button',text,'secondary');button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(value);button.textContent=t('Kopiert');}catch(e){button.textContent=t('Bitte Text markieren');}});return button;}
function commandFields(title,path,bodyOn,bodyOff){
 const dl=node('dl',undefined,'command-fields');
 function field(label,value,header=false){const dd=node('dd');dd.append(node('code',value||t('Leer lassen')));if(header){const button=node('button',t('Header mit Token kopieren'),'secondary');button.onclick=async()=>{try{await navigator.clipboard.writeText(loxoneHTTPHeader(await tokenValue()));button.textContent=t('Kopiert');}catch(error){button.textContent=t('Token in Loxone-Einstellungen anzeigen');}};dd.append(button);}else if(value)dd.append(copyButton(t('Kopieren'),value));dl.append(node('dt',label),dd);}
 field(t('Name des Ausgangsbefehls'),title);
 field(t('Befehl bei EIN'),path);
 field(t('HTTP header bei EIN'),loxoneHTTPHeader('DEIN_HUE2LOX_TOKEN'),true);
 field(t('HTTP body bei EIN'),bodyOn);
 field(t('HTTP Methode bei EIN'),'PUT');
 dl.append(node('dt',t('Header-Format')),node('dd',t('Eine Zeile mit sichtbarem \\r\\n zwischen den Headern. Keine Enter-Zeilenumbrüche oder Leerzeile am Ende ergänzen. Bestehende EIN-/AUS-Header durch die neue Kopie ersetzen.')));
 if(bodyOff){field(t('Befehl bei AUS'),path);field(t('HTTP header bei AUS'),loxoneHTTPHeader('DEIN_HUE2LOX_TOKEN'),true);field(t('HTTP body bei AUS'),bodyOff);field(t('HTTP Methode bei AUS'),'PUT');}
 field(t('HTTP-Antwort speichern'),'');
 return dl;
}
function outputAddress(url){const details=node('details',undefined,'command-address');details.append(node('summary',t('Basisadresse des virtuellen Ausgangs')));const p=node('p');p.append(node('code',url),copyButton(t('Kopieren'),url));details.append(p);return details;}
function showCommands(light,panel){hideToken();const command=selectedCommand(light);panel.replaceChildren(node('h2',light.name));panel.append(node('p',t('Empfehlung aus den Lampenfähigkeiten: ')+t(light.commands.find(c=>c.id===light.recommended_mode)?.name)+t('. XML enthält alle angehakten Nutzungsarten. Hier wird eine Variante als Vorschau gezeigt.'),'sub'));if(!light.writes_enabled)panel.append(node('p',t('Die Steuerung ist auf dem Server derzeit deaktiviert.'),'error'));panel.append(commandFields(light.name+' · '+t(command.name),light.path,command.body_on,command.body_off));panel.append(node('p',command.analog?({tw:t('Digitalausgang deaktivieren. Aktortyp Lumitech verwenden und Weiße Lichtfarbe wählen; Helligkeit über 0 %. AUS-Felder leer lassen; Wert 0 schaltet aus.'),dim:t('Digitalausgang deaktivieren. Dimmer 0–100 %. AUS-Felder leer lassen; Wert 0 schaltet aus.'),rgb:t('Digitalausgang deaktivieren. Aktortyp RGB verwenden. AUS-Felder leer lassen; Wert 0 schaltet aus.'),lumitech:t('Digitalausgang deaktivieren. Aktortyp Lumitech für Farbe und Weiß verwenden. AUS-Felder leer lassen; Wert 0 schaltet aus.')}[command.id]):t('Digitalausgang verwenden. Header für EIN und AUS einsetzen.')));if(command.analog)panel.append(node('p',t('In Loxone Config: Einheit auf <v> setzen. Den Body passend zum Aktortyp kopieren; <v> im Body ohne Anführungszeichen übernehmen.'),'info'));panel.append(node('p',t('Bei HTTP 400: HTTP-Monitor starten, Befehl erneut auslösen und den Body (bereinigt) prüfen. Eine Zahl als Text, ein nicht ersetztes <v> oder ein zum Aktortyp unpassender Wert kann zur Ablehnung führen.'),'sub'));panel.append(outputAddress(loxoneData.base_url));const exportButton=node('button',t('XML für diese Lampe herunterladen'),'secondary');exportButton.onclick=()=>downloadXML([light.key]);panel.append(exportButton);}
async function tokenValue(){const session=adminSession;if(!session)throw Error();const response=await adminRequest('/api/admin/token',{});if(!response.ok||adminSession!==session)throw Error(t('Token nicht verfügbar'));return (await response.json()).token;}
function lampXMLFilename(name){let filename=name.replace(/[<>:"/\\|?*\u0000-\u001f\u007f]/g,'_').replace(/[. ]+$/g,'').trim()||t('Lampe');if(/^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(filename))filename='_'+filename;return filename+'.xml';}
async function downloadXML(keys){const include=document.querySelector('#include-token').checked;document.querySelector('#loxone-message').textContent=t('Export wird erstellt …');try{const response=await adminRequest('/api/admin/export',{lights:keys,include_token:include,language:i18n.language,variants:Object.fromEntries(keys.map(key=>{const light=loxoneData.lights.find(l=>l.key===key);return [key,light.enabled_modes];}))});if(!response.ok)throw Error();const blob=await response.blob();const url=URL.createObjectURL(blob);const a=node('a');a.href=url;a.download=keys.length===1?lampXMLFilename(loxoneData.lights.find(light=>light.key===keys[0]).name):'Hue2Lox-Auswahl.xml';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);document.querySelector('#loxone-message').textContent=include?t('XML heruntergeladen. Die Datei enthält dein Zugriffstoken.'):t('XML heruntergeladen. Token-Platzhalter in Loxone ersetzen.');}catch(e){document.querySelector('#loxone-message').textContent=t('Export fehlgeschlagen. Anmeldung und Lampenauswahl prüfen.');}}
document.querySelector('#login-form').addEventListener('submit',async event=>{event.preventDefault();const button=document.querySelector('#login-submit');button.disabled=true;try{const response=await adminRequest('/api/admin/login',{username:document.querySelector('#login-user').value,password:document.querySelector('#login-password').value});document.querySelector('#login-password').value='';if(response.ok){adminSession=await response.json();await unlockAdmin();}else{const result=await response.json().catch(()=>({}));const messages={401:t('Benutzername oder Passwort stimmt nicht.'),429:t('Zu viele Versuche. Bitte fünf Minuten warten.'),503:t('Der Administrator ist noch nicht eingerichtet. Einrichtung im LoxBerry-Terminal abschließen.')};lockAdmin(result.error==='invalid_origin'?t('Diese Browseradresse passt nicht zur Serverkonfiguration. Verwende die konfigurierte Adresse oder passe HUE_PUBLIC_URL an.'):messages[response.status]||t('Anmeldung fehlgeschlagen. Bitte Serverkonfiguration und Verbindung prüfen.'));}}catch(e){lockAdmin(t('Dienst nicht erreichbar. Bitte erneut versuchen.'));}finally{button.disabled=false;}});
document.querySelector('#logout').addEventListener('click',async()=>{try{const response=await adminRequest('/api/admin/logout',{});if(response.ok||response.status===401)lockAdmin(t('Du bist abgemeldet.'));else document.querySelector('#notice').textContent=t('Abmelden fehlgeschlagen. Bitte erneut versuchen.');}catch(e){document.querySelector('#notice').textContent=t('Abmelden fehlgeschlagen. Verbindung prüfen.');}});
document.querySelector('#show-token').addEventListener('click',async()=>{const field=document.querySelector('#control-token');if(field.value){hideToken();return;}try{field.value=await tokenValue();field.type='text';document.querySelector('#show-token').textContent=t('Verbergen');revealTimer=setTimeout(hideToken,30000);}catch(e){document.querySelector('#token-message').textContent=t('Token nicht verfügbar. Anmeldung prüfen.');}});
document.querySelector('#copy-header').addEventListener('click',async()=>{try{const token=await tokenValue();await navigator.clipboard.writeText(loxoneHTTPHeader(token));document.querySelector('#token-message').textContent=t('HTTP-Header kopiert. Bei EIN und bei digitalen Befehlen auch bei AUS einfügen.');}catch(e){document.querySelector('#token-message').textContent=t('Kopieren fehlgeschlagen. Token anzeigen und Header manuell übernehmen.');}});
document.querySelector('#select-all').addEventListener('click',()=>{for(const lamp of filteredLights){const key=lamp.bridge.id+'/'+lamp.id;if(loxoneData?.lights.some(light=>light.key===key&&light.available))selectedLights.add(key);};renderLoxoneList();});
document.querySelector('#select-none').addEventListener('click',()=>{selectedLights.clear();renderLoxoneList();});
document.querySelector('#export-selected').addEventListener('click',()=>downloadXML([...selectedLights]));
window.addEventListener('blur',hideToken);
document.addEventListener('visibilitychange',()=>{if(document.hidden)hideToken();});

const passwordDialog=document.querySelector('#password-dialog');
document.querySelector('#open-password').addEventListener('click',()=>{document.querySelector('#password-form').reset();document.querySelector('#password-message').textContent='';passwordDialog.showModal();});
document.querySelector('#password-cancel').addEventListener('click',()=>passwordDialog.close());
passwordDialog.addEventListener('close',()=>document.querySelector('#password-form').reset());
document.querySelector('#password-form').addEventListener('submit',async event=>{
 event.preventDefault();const message=document.querySelector('#password-message');
 const next=document.querySelector('#password-new').value;
 if(next!==document.querySelector('#password-confirm').value){message.textContent=t('Die neuen Passwörter stimmen nicht überein.');return;}
 const button=document.querySelector('#password-save');button.disabled=true;
 try{
  const response=await adminRequest('/api/admin/password',{current_password:document.querySelector('#password-current').value,new_password:next});
  if(response.ok){lockAdmin(t('Passwort geändert. Bitte mit dem neuen Passwort anmelden.'));}
  else{const result=await response.json();message.textContent=result.error==='password_invalid'?t('Das aktuelle Passwort stimmt nicht.'):response.status===429?t('Zu viele Versuche. Bitte fünf Minuten warten.'):t('Passwort konnte nicht geändert werden. Anmeldung und Installation prüfen.');document.querySelector('#password-current').value='';}
 }catch(e){message.textContent=t('Verbindung unterbrochen. Bitte erneut versuchen.');}
 finally{button.disabled=false;}
});

// Fetch the reference before handing a local Blob to the download manager, as for XML.
document.querySelector('#download-model-catalog').addEventListener('click',async()=>{
 const button=document.querySelector('#download-model-catalog'),message=document.querySelector('#catalog-download-message');
 if(button.disabled)return;button.disabled=true;message.textContent=t(' Tabelle wird geladen …');
 try{const response=await fetch('/assets/hue-models.zip',{cache:'no-store',credentials:'same-origin'});if(!response.ok||!response.headers.get('Content-Type')?.startsWith('application/zip'))throw Error();const blob=await response.blob();if(!blob.size)throw Error();const url=URL.createObjectURL(blob),link=node('a');link.href=url;link.download='Hue-Modelltabelle.zip';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);message.textContent=t(' Download gestartet.');}
 catch(error){message.textContent=t(' Download fehlgeschlagen. Verbindung zu Hue2Lox prüfen und erneut versuchen.');}
 finally{button.disabled=false;}
});

const iconSaving=new Set();
function lampIconPicker(light){
 const key=light.bridge.id+'/'+light.id,wrap=node('label',undefined,'lamp-mode lamp-icon-picker'),select=node('select');
 wrap.append(node('span',t('Lampensymbol')));
 select.append(new Option(t('Automatisch'),'auto'));
 for(const [id,label] of Object.entries(LAMP_ICON_LABELS))select.append(new Option(t(label),id));
 select.value=Object.prototype.hasOwnProperty.call(LAMP_ICON_LABELS,light.icon_override)?light.icon_override:'auto';
 select.disabled=iconSaving.has(key);select.setAttribute('aria-label',t('Lampensymbol')+' · '+light.name);
 select.onchange=async()=>{
  const icon=select.value;iconSaving.add(key);select.disabled=true;
  try{
   const response=await adminRequest('/api/admin/lights/icon',{bridge_id:light.bridge.id,light_id:light.id,icon});
   if(!response.ok)throw Error();
   for(const bridge of data?.bridges||[])if(bridge.id===light.bridge.id)for(const item of bridge.lights)if(item.id===light.id){if(icon==='auto')delete item.icon_override;else item.icon_override=icon;}
   document.querySelector('#lamp-message').textContent=t('Lampensymbol gespeichert.');
  }catch(error){document.querySelector('#lamp-message').textContent=t('Lampensymbol konnte nicht gespeichert werden.');}
  finally{iconSaving.delete(key);renderLights();}
 };
 wrap.append(select);return wrap;
}
