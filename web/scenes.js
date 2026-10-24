'use strict';
let sceneData=null,sceneOpen=null,sceneScanning=false,sceneChanging=false,sceneRemoveKey=null;
const selectedScenes=new Set(),openSceneOptions=new Set();
let filteredScenes=[];
function resetScenes(){openSceneOptions.clear();filteredScenes=[];sceneData=null;sceneOpen=null;sceneRemoveKey=null;selectedScenes.clear();document.querySelector('#scene-show-ignored').checked=false;for(const id of ['scene-bridge-filter','scene-room-filter','scene-search'])document.querySelector('#'+id).value='';document.querySelector('#scene-list').replaceChildren();document.querySelector('#scene-message').textContent='';document.querySelector('#scene-token').checked=false;sceneSelection();}
async function loadScenes(){
 const session=adminSession;if(!session)return;
 try{const response=await adminRequest('/api/admin/scenes');if(!response.ok)throw Error();const result=await response.json();if(adminSession!==session)return;sceneData=result;const available=new Set(result.scenes.filter(s=>s.available).map(s=>s.key));for(const key of selectedScenes)if(!available.has(key))selectedScenes.delete(key);renderScenes();}
 catch(error){if(adminSession===session)document.querySelector('#scene-message').textContent=t('Szenenliste konnte nicht geladen werden. Bitte erneut einlesen.');}
}
function sceneSelection(){const button=document.querySelector('#scene-export');button.disabled=!selectedScenes.size;button.textContent=t('Auswahl als XML (')+selectedScenes.size+')';}
function renderScenes(){
 const list=document.querySelector('#scene-list');list.replaceChildren();const term=document.querySelector('#scene-search').value.toLocaleLowerCase(i18n.locale);
 const items=(sceneData?.scenes||[]).filter(s=>!s.ignored||document.querySelector('#scene-show-ignored').checked);
 const bridges=[...new Map((sceneData?.scenes||[]).map(s=>[s.bridge_id,{id:s.bridge_id,name:s.bridge}])).values()];
 const found=topologyFilter(items,document.querySelector('#scene-bridge-filter'),document.querySelector('#scene-room-filter'),bridges).filter(s=>(s.name+' '+s.bridge+' '+s.room).toLocaleLowerCase(i18n.locale).includes(term));
 filteredScenes=found;
 if(!found.length)list.append(node('p',sceneData?.scenes.length?t('Keine Szene für diesen Filter.'):t('Noch keine Szenen eingelesen. In der Hue-App speichern und danach „Szenen einlesen“ wählen.'),'info'));
 for(const [index,scene] of found.entries()){
  const entry=node('div',undefined,'export-entry'),row=node('div',undefined,'export-row'),label=node('label'),check=node('input');check.type='checkbox';check.disabled=!scene.available;check.checked=selectedScenes.has(scene.key);check.onchange=()=>{check.checked?selectedScenes.add(scene.key):selectedScenes.delete(scene.key);sceneSelection();};
  label.append(check,node('span',scene.name),node('small',scene.bridge+' · '+(scene.room||t('Ohne Raum'))+' · '+scene.light_count+t(' Lampe(n)')+(scene.ignored?t(' · Ignoriert'):scene.available?'':t(' · Nicht verfügbar'))));row.append(label);
  const details=node('div',undefined,'lamp-command-details');details.id='scene-commands-'+index;details.hidden=sceneOpen!==scene.key;
  const toggle=node('button',details.hidden?t('Befehle ▾'):t('Befehle schließen ▴'),'secondary command-toggle');toggle.disabled=!scene.available;toggle.setAttribute('aria-expanded',String(!details.hidden));toggle.setAttribute('aria-controls',details.id);toggle.onclick=()=>{hideToken();sceneOpen=sceneOpen===scene.key?null:scene.key;renderScenes();};
  const xml=node('button','XML','secondary');xml.disabled=!scene.available;xml.setAttribute('aria-label',t('XML für Szene ')+scene.name+t(' herunterladen'));xml.onclick=()=>downloadScenes([scene.key]);row.append(toggle,xml);const options=node('details',undefined,'scene-options');options.open=openSceneOptions.has(scene.key);options.ontoggle=()=>{options.open?openSceneOptions.add(scene.key):openSceneOptions.delete(scene.key);};options.append(node('summary',t('Verwaltung')),sceneActions(scene));row.append(options);entry.append(row);
  if(scene.hidden_light_count)entry.append(node('p',scene.hidden_light_count+t(' ignorierte oder entfernte Lampe(n) gehören zu dieser Hue-Szene und werden beim Aufruf mitgeschaltet.'),'sub'));
  if(!details.hidden&&scene.available){
   details.append(node('h2',scene.name),commandFields(scene.name+(scene.switch.enabled?t(' · Szene Ein/Aus'):t(' · Szene aktivieren')),scene.path,scene.commands[0].body_on,scene.commands[0].body_off),node('p',t(scene.switch.enabled?'Digitalausgang verwenden. EIN und AUS sind Gruppenbefehle; Wiederholung 0.':'Digitalausgang verwenden und mit einem Impuls ansteuern. AUS-Befehl, AUS-Header und AUS-Body leer lassen. Wiederholung 0. Erstellen und Bearbeiten bleiben in der Hue-App.'),'info'),outputAddress(sceneData.base_url));
   if(scene.switch.enabled)details.append(node('p',t('EIN aktiviert die Szene. AUS schaltet die gesamte bestätigte Gruppe aus. Keine Zustandsrückmeldung an Loxone. Nach Neustart zuerst EIN senden. Überlappende Gruppen zuerst ausschalten.'),'info'));
   if(!scene.writes_enabled)details.append(node('p',t('Steuerung auf dem Server derzeit deaktiviert.'),'error'));
  }
  entry.append(details);list.append(entry);
 }
 sceneSelection();
}
async function downloadScenes(keys){
 const message=document.querySelector('#scene-message');message.textContent=t('Export wird erstellt …');
 try{const include=document.querySelector('#scene-token').checked;const response=await adminRequest('/api/admin/scenes/export',{scenes:keys,include_token:include,language:i18n.language});if(!response.ok)throw Error();const url=URL.createObjectURL(await response.blob());const a=node('a');a.href=url;a.download='Hue2Lox-Szenen.xml';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);message.textContent=include?t('XML heruntergeladen. Sie enthält dein Zugriffstoken.'):t('XML heruntergeladen. Token-Platzhalter in Loxone ersetzen.');}
 catch(error){message.textContent=t('Szenenexport fehlgeschlagen. Anmeldung und Auswahl prüfen.');}
}
async function scanScenes(){
 if(sceneScanning||sceneChanging)return;sceneScanning=true;renderScenes();const button=document.querySelector('#scene-scan');button.disabled=true;const message=document.querySelector('#scene-message');message.textContent=t('Szenen und Lampen werden von den gekoppelten Bridges eingelesen …');
 const session=adminSession;
 try{
  const response=await adminRequest('/api/admin/bridges');if(!response.ok)throw Error();const bridges=(await response.json()).bridges.filter(b=>b.paired&&b.enabled);const failed=[];
  for(const bridge of bridges){if(adminSession!==session)return;try{const scan=await adminRequest('/api/admin/bridges/scan',{id:bridge.id});if(!scan.ok)failed.push(bridge.name);}catch(error){failed.push(bridge.name);}}
  if(adminSession!==session)return;
  await Promise.all([loadScenes(),loadLoxone(),loadBridgeManagement(),refresh()]);
  message.textContent=!bridges.length?t('Zuerst unter Bridges eine Hue Bridge koppeln.'):failed.length?t('Einlesen fehlgeschlagen: ')+failed.join(', ')+t('. Vorhandene Daten bleiben erhalten.'):t('Szenen und Lampen aktualisiert. Es wurde keine Szene aktiviert.');
 }catch(error){if(adminSession===session)message.textContent=t('Einlesen fehlgeschlagen. Anmeldung und Bridge-Verbindung prüfen.');}
 finally{sceneScanning=false;button.disabled=false;renderScenes();}
}
document.querySelector('#scene-scan').addEventListener('click',scanScenes);
document.querySelector('#scene-search').addEventListener('input',renderScenes);
document.querySelector('#scene-all').addEventListener('click',()=>{for(const scene of filteredScenes)if(scene.available)selectedScenes.add(scene.key);renderScenes();});
document.querySelector('#scene-none').addEventListener('click',()=>{selectedScenes.clear();renderScenes();});
document.querySelector('#scene-export').addEventListener('click',()=>downloadScenes([...selectedScenes]));

function sceneActions(scene){
 const box=node('div',undefined,'lamp-actions');box.append(sceneSwitchOptions(scene));const ignore=node('button',scene.ignored?t('Wieder einblenden'):t('Ignorieren'),'secondary');ignore.disabled=sceneChanging||sceneScanning;ignore.onclick=()=>changeScene(scene,'ignore',!scene.ignored);box.append(ignore);
 if(sceneRemoveKey===scene.key){
  box.append(node('span',t('Nur aus Hue2Lox entfernen? Erneutes Einlesen kann die Szene zurückbringen. Für dauerhaftes Ausblenden „Ignorieren“ wählen.'),'sub'));
  const yes=node('button',t('Jetzt entfernen'),'secondary');yes.disabled=sceneChanging||sceneScanning;yes.onclick=()=>changeScene(scene,'remove');
  const no=node('button',t('Abbrechen'),'secondary');no.onclick=()=>{sceneRemoveKey=null;renderScenes();};box.append(yes,no);
 }else{const remove=node('button',t('Entfernen'),'secondary');remove.disabled=sceneChanging||sceneScanning;remove.onclick=()=>{sceneRemoveKey=scene.key;renderScenes();};box.append(remove);}
 return box;
}
async function changeScene(scene,action,ignored=true){
 if(sceneChanging||sceneScanning)return;sceneChanging=true;renderScenes();const session=adminSession;
 try{
  const response=await adminRequest('/api/admin/scenes/'+action,{bridge_id:scene.bridge_id,scene_id:scene.key.split('/')[1],ignored});
  if(!response.ok)throw Error();if(adminSession!==session)return;
  selectedScenes.delete(scene.key);sceneOpen=null;sceneRemoveKey=null;await Promise.all([loadScenes(),loadBridgeManagement()]);
  document.querySelector('#scene-message').textContent=action==='remove'?t('Szene nur aus Hue2Lox entfernt. Erneutes Einlesen kann sie zurückbringen.'):ignored?t('Szene ignoriert. Über „Ignorierte anzeigen“ kannst du sie zurückholen.'):t('Szene wieder eingeblendet.');
 }catch(error){if(adminSession===session)document.querySelector('#scene-message').textContent=t('Änderung fehlgeschlagen. Bitte erneut versuchen; eventuell läuft eine Inventur.');}
 finally{sceneChanging=false;if(adminSession===session)renderScenes();}
}
document.querySelector('#scene-show-ignored').addEventListener('change',renderScenes);

for(const id of ['scene-bridge-filter','scene-room-filter'])document.querySelector('#'+id).addEventListener('change',renderScenes);

function sceneSwitchOptions(scene){
 const box=node('div'),title=node('strong',t('Nutzungsart der Szene'));
 const select=node('select');select.setAttribute('aria-label',t('Zielgruppe für Szene Ein/Aus'));
 const recall=node('option',t('Nur aktivieren (bisheriges Verhalten)'));recall.value='';select.append(recall);
 for(const group of scene.switch.groups){const option=node('option',group.name);option.value=group.id;select.append(option);}
 select.value=scene.switch.group_id;const warning=node('p',undefined,'info');
 const label=node('label'),check=node('input');check.type='checkbox';label.append(check,node('span',t('Ich bestätige: AUS schaltet alle aufgeführten Lampen dieser Gruppe aus.')));
 const save=node('button',t('Nutzungsart speichern'),'secondary');
 function update(){const group=scene.switch.groups.find(g=>g.id===select.value);check.checked=false;
  warning.textContent=group?group.name+': '+group.lamps.map(l=>l.name+(l.hidden?t(' (ausgeblendet)'):'')).join(', ')+(group.overlaps.length?t(' · Überlappende Gruppen: ')+group.overlaps.join(', '):''):t('Nur Szenenaktivierung, kein AUS-Befehl.');
  label.hidden=!group;save.disabled=sceneChanging||sceneScanning||!!group;
 }
 select.onchange=update;check.onchange=()=>save.disabled=sceneChanging||sceneScanning||!!select.value&&!check.checked;
 save.onclick=async()=>{if(sceneChanging||sceneScanning)return;sceneChanging=true;save.disabled=true;
  try{const response=await adminRequest('/api/admin/scenes/switch',{bridge_id:scene.bridge_id,scene_id:scene.key.split('/')[1],group_id:select.value,confirmation:scene.switch.groups.find(g=>g.id===select.value)?.confirmation});if(!response.ok)throw Error();await loadScenes();document.querySelector('#scene-message').textContent=t('Nutzungsart gespeichert. XML neu exportieren; bestehende Loxone-Konfiguration bleibt unverändert.');}
  catch(error){document.querySelector('#scene-message').textContent=t('Nutzungsart konnte nicht gespeichert werden. Neu einlesen und erneut bestätigen.');}
  finally{sceneChanging=false;renderScenes();}
 };
 box.append(title,select,warning,label,save);
 if(scene.switch.configured&&!scene.switch.enabled)box.append(node('p',t('Gruppenzuordnung nicht mehr bestätigt. Neu einlesen, Lampen prüfen und erneut bestätigen. EIN/AUS ist gesperrt.'),'error'));
 update();return box;
}
