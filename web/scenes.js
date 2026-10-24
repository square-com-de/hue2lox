'use strict';
let sceneData=null,sceneOpen=null,sceneScanning=false,sceneChanging=false,sceneRemoveKey=null;
const selectedScenes=new Set(),openSceneOptions=new Set();
let filteredScenes=[];
function resetScenes(){openSceneOptions.clear();filteredScenes=[];sceneData=null;sceneOpen=null;sceneRemoveKey=null;selectedScenes.clear();document.querySelector('#scene-show-ignored').checked=false;for(const id of ['scene-bridge-filter','scene-room-filter','scene-search'])document.querySelector('#'+id).value='';document.querySelector('#scene-list').replaceChildren();document.querySelector('#scene-message').textContent='';document.querySelector('#scene-token').checked=false;sceneSelection();}
async function loadScenes(){
 const session=adminSession;if(!session)return;
 try{const response=await adminRequest('/api/admin/scenes');if(!response.ok)throw Error();const result=await response.json();if(adminSession!==session)return;sceneData=result;const available=new Set(result.scenes.filter(s=>s.available&&!s.switch.needs_group).map(s=>s.key));for(const key of selectedScenes)if(!available.has(key))selectedScenes.delete(key);renderScenes();}
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
  const entry=node('div',undefined,'export-entry'),row=node('div',undefined,'export-row'),label=node('label'),check=node('input');check.type='checkbox';check.disabled=!scene.available||scene.switch.needs_group;check.checked=selectedScenes.has(scene.key);check.onchange=()=>{check.checked?selectedScenes.add(scene.key):selectedScenes.delete(scene.key);sceneSelection();};
  label.append(check,node('span',scene.name),node('small',scene.bridge+' · '+(scene.room||t('Ohne Raum'))+' · '+scene.light_count+t(' Lampe(n)')+(scene.ignored?t(' · Ignoriert'):scene.available?'':t(' · Nicht verfügbar'))));row.append(label);
  const details=node('div',undefined,'lamp-command-details');details.id='scene-commands-'+index;details.hidden=sceneOpen!==scene.key;
  const toggle=node('button',details.hidden?t('Befehle ▾'):t('Befehle schließen ▴'),'secondary command-toggle');toggle.disabled=!scene.available||scene.switch.needs_group;toggle.setAttribute('aria-expanded',String(!details.hidden));toggle.setAttribute('aria-controls',details.id);toggle.onclick=()=>{hideToken();sceneOpen=sceneOpen===scene.key?null:scene.key;renderScenes();};
  const xml=node('button','XML','secondary');xml.disabled=!scene.available||scene.switch.needs_group;xml.setAttribute('aria-label',t('XML für Szene ')+scene.name+t(' herunterladen'));xml.onclick=()=>downloadScenes([scene.key]);row.append(toggle,xml);const options=node('details',undefined,'scene-options');options.open=openSceneOptions.has(scene.key);options.ontoggle=()=>{options.open?openSceneOptions.add(scene.key):openSceneOptions.delete(scene.key);};options.append(node('summary',t('Verwaltung')),sceneActions(scene));row.append(options);entry.append(row,sceneSwitchOptions(scene));
  if(scene.hidden_light_count)entry.append(node('p',scene.hidden_light_count+t(' ignorierte oder entfernte Lampe(n) gehören zu dieser Hue-Szene und werden beim Aufruf mitgeschaltet.'),'sub'));
  if(!details.hidden&&scene.available&&!scene.switch.needs_group){
   details.append(node('h2',scene.name),commandFields(scene.name+(scene.switch.enabled?t(' · Szene Ein/Aus'):t(' · Szene aktivieren')),scene.path,scene.commands[0].body_on,scene.commands[0].body_off),node('p',t(scene.switch.enabled?'Digitalausgang verwenden. EIN und AUS sind Gruppenbefehle; Wiederholung 0.':'Digitalausgang verwenden und mit einem Impuls ansteuern. AUS-Befehl, AUS-Header und AUS-Body leer lassen. Wiederholung 0. Erstellen und Bearbeiten bleiben in der Hue-App.'),'info'),outputAddress(sceneData.base_url));
   if(scene.switch.enabled)details.append(node('p',t('EIN aktiviert die Szene. AUS schaltet die gesamte zugeordnete Gruppe aus. Keine Zustandsrückmeldung an Loxone. Nach Neustart zuerst EIN senden. Überlappende Gruppen zuerst ausschalten.'),'info'));
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
document.querySelector('#scene-all').addEventListener('click',()=>{for(const scene of filteredScenes)if(scene.available&&!scene.switch.needs_group)selectedScenes.add(scene.key);renderScenes();});
document.querySelector('#scene-none').addEventListener('click',()=>{selectedScenes.clear();renderScenes();});
document.querySelector('#scene-export').addEventListener('click',()=>downloadScenes([...selectedScenes]));

function sceneActions(scene){
 const box=node('div',undefined,'lamp-actions');const ignore=node('button',scene.ignored?t('Wieder einblenden'):t('Ignorieren'),'secondary');ignore.disabled=sceneChanging||sceneScanning;ignore.onclick=()=>changeScene(scene,'ignore',!scene.ignored);box.append(ignore);
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
 const state=scene.switch,box=node('div',undefined,'scene-switch-settings'),controls=node('div',undefined,'scene-switch-controls');
 const label=node('label',t('Steuerung')),mode=node('select');mode.setAttribute('aria-label',t('Steuerung der Szene'));
 for(const [value,text] of [['switch',t('Ein/Aus')],['recall',t('Nur aktivieren')]]){const option=node('option',text);option.value=value;mode.append(option);}
 mode.value=state.mode;mode.disabled=sceneChanging||sceneScanning||!scene.available;label.append(mode);controls.append(label);
 const group=state.groups.find(g=>g.id===state.group_id);
 if(state.mode==='switch'){
  const target=node('select');target.setAttribute('aria-label',t('Gruppe für AUS'));const empty=node('option',t('Gruppe wählen …'));empty.value='';target.append(empty);
  for(const candidate of state.groups){const option=node('option',candidate.name+(candidate.extra_light_ids.length?t(' · zusätzliche Lampen: ')+candidate.extra_light_ids.length:''));option.value=candidate.id;target.append(option);}
  target.value=state.enabled&&group?group.id:'';target.disabled=sceneChanging||sceneScanning||!scene.available||!state.groups.length;
  const targetLabel=node('label',t('Gruppe für AUS'));targetLabel.append(target);controls.append(targetLabel);
  target.onchange=()=>{if(target.value)return saveSceneMode(scene,'group',target.value);};
 }
 box.append(controls);
 if(state.mode==='recall')box.append(node('p',t('Nur Szenenaktivierung, kein AUS-Befehl.'),'sub'));
 else if(group){
  const names=group.lamps.map(l=>l.name+(l.hidden?t(' (ausgeblendet)'):'')).join(', ');
  box.append(node('p',(state.automatic&&state.enabled?t('Automatisch zugeordnet. '):'')+t('AUS schaltet diese Gruppe aus: ')+group.name+' · '+names,'sub'));
  const extra=group.lamps.filter(l=>group.extra_light_ids.includes(l.id));
  if(extra.length)box.append(node('p',t('Zusätzlich zur Szene betroffen: ')+extra.map(l=>l.name).join(', '),'info'));
  if(group.overlaps.length)box.append(node('p',t('Überlappende Gruppen: ')+group.overlaps.join(', '),'sub'));
  if(!state.enabled)box.append(node('p',t('Die Gruppe wurde geändert. Aktuelle Lampen prüfen und die Gruppe oben erneut auswählen. Bis dahin ist Ein/Aus gesperrt.'),'error'));
 }else {
  for(const candidate of state.groups){const extra=candidate.lamps.filter(l=>candidate.extra_light_ids.includes(l.id));if(extra.length)box.append(node('p',candidate.name+' · '+t('Zusätzlich zur Szene betroffen: ')+extra.map(l=>l.name).join(', '),'info'));}
  box.append(node('p',state.groups.length?t('Für Ein/Aus oben eine Gruppe wählen. AUS betrifft alle dort aufgeführten Lampen.'):t('Keine passende Gruppe bekannt. Szenen erneut einlesen oder „Nur aktivieren“ wählen.'),'info'));
 }
 mode.onchange=()=>saveSceneMode(scene,mode.value==='recall'?'recall':'auto',state.exact_group_id||'');
 return box;
}
async function saveSceneMode(scene,mode,groupId){
 if(sceneChanging||sceneScanning)return;sceneChanging=true;const session=adminSession;renderScenes();
 try{
  const group=scene.switch.groups.find(g=>g.id===groupId);
  const response=await adminRequest('/api/admin/scenes/switch',{bridge_id:scene.bridge_id,scene_id:scene.key.split('/')[1],mode,group_id:mode==='recall'?'':groupId,confirmation:group?.confirmation});
  if(!response.ok)throw Error();if(adminSession!==session)return;await loadScenes();
  document.querySelector('#scene-message').textContent=t('Steuerung gespeichert. XML neu exportieren; bestehende Loxone-Befehle bleiben unverändert.');
 }catch(error){if(adminSession===session){await loadScenes();document.querySelector('#scene-message').textContent=t('Gruppe konnte nicht übernommen werden. Aktuelle Lampen prüfen und erneut auswählen.');}}
 finally{sceneChanging=false;if(adminSession===session)renderScenes();}
}
