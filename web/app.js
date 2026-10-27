'use strict';
const $=s=>document.querySelector(s);
const names={overview:[t("Übersicht"),t("Bridges, Lampen und aktuelle Zustände im Überblick.")],lights:[t("Lampen"),t("Lampen verwalten und Steuerbefehle für Loxone exportieren.")],scenes:[t("Szenen"),t("Hue-Szenen einlesen und für Loxone konfigurieren.")],bridges:[t("Bridges"),t("Hue Bridges suchen, koppeln und verwalten.")],monitor:[t("HTTP-Monitor"),t("Eingehende Loxone-Anfragen und Hue-Antworten prüfen.")],loxone:[t("Loxone-Einstellungen"),t("Miniserver-Link und Zugriffstoken verwalten.")]};
let data=null,busy=false,filteredLights=[];
function node(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
function badge(text,kind=''){return node('span',text,'badge '+kind);}
function allLights(){return data.bridges.flatMap(b=>b.lights.map(l=>({...l,bridge:b})));}
function lampIcon(l,live){
 const icon=LAMP_ICONS[lampIconKey(l)];
 const box=node('div',undefined,'orb lamp-icon '+(live?(l.state.on?'is-on':'is-off'):'is-unknown'));
 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
 svg.setAttribute('viewBox','0 0 64 64');svg.setAttribute('aria-hidden','true');
 svg.setAttribute('fill','none');svg.setAttribute('stroke','currentColor');svg.setAttribute('stroke-width','2.3');svg.setAttribute('stroke-linecap','round');svg.setAttribute('stroke-linejoin','round');
 // Only bundled geometry is inserted; device names and metadata never become markup.
 svg.innerHTML=icon;
 box.append(svg);return box;
}
function lamp(l,managed=false){
 const card=node('article',undefined,'lamp'),state=l.state,live=l.status==='online';card.append(lampIcon(l,live));
 const info=node('div',undefined,'lamp-info'),heading=node('div',undefined,'lamp-heading');
 heading.append(node('h3',l.name),badge(l.ignored?t('Ignoriert'):live?(state.on?t('Ein'):t('Aus')):t('Status nicht verfügbar'),live?(state.on?'':'off'):'bad'));info.append(heading,node('div',l.bridge.name+' · '+(l.room||t('Ohne Raum'))+' · '+(l.model||'Hue'),'sub'));
 const abilities=node('div',undefined,'lamp-abilities');const type=node('span',t('Typ: ')+(t(l.lamp_type)||t('Unbekannt')),'lamp-type');if(l.product_name)type.title=l.product_name;abilities.append(type);
 for(const [cap,label] of [['on',t('Ein/Aus')],['brightness','Dimmer'],['temperature','Tunable White'],['rgb','RGB']])if((l.capabilities||[]).includes(cap))abilities.append(badge(label,'off'));info.append(abilities);if(l.error)info.append(node('p',t(l.error),'sub'));card.append(info);
 const reading=node('div',undefined,'reading');let ct='—';if(live){const c=state.color_temperature;if(c&&c.mirek_valid&&Number.isFinite(c.mirek)&&c.mirek>0)ct=Math.round(1000000/c.mirek).toLocaleString(i18n.locale)+' K';else ct=(l.capabilities||[]).includes('rgb')?'RGB':'—';}
 for(const [value,label]of [[live&&Number.isFinite(state.brightness)?state.brightness.toLocaleString(i18n.locale,{maximumFractionDigits:1})+' %':'—',t('Helligkeit (gespeichert)')],[ct,t('Farbe / Weißtemperatur')]]){const r=node('div');r.append(node('strong',value),node('small',label));reading.append(r);}card.append(reading);if(managed)card.append(lampCommands(l));return card;
}
function bridgeCard(b){const card=node('article',undefined,'bridge');card.append(badge(b.enabled?(b.status==='degraded'?t('Verbindung prüfen'):t('Eingerichtet')):t('Vorbereitet'),b.enabled?(b.status==='degraded'?'bad':''):'off'),node('h3',b.name),node('div',b.id.toUpperCase()+' · '+b.host,'address'),node('p',b.enabled?b.lights.filter(l=>!l.ignored).length+t(' eingerichtete Lampe(n) · TLS zur Hue Bridge'): t('Noch nicht aktiviert · keine Abfragen')));return card;}
function render(){const lamps=allLights().filter(l=>!l.ignored);$('#bridge-count').textContent=data.bridges.filter(b=>b.enabled).length;$('#light-count').textContent=lamps.length;$('#on-count').textContent=lamps.filter(l=>l.state&&l.state.on).length;$('#scene-count').textContent=data.scene_count;renderMiniserverLink(data.miniserver);$('#bridge-summary').replaceChildren(...data.bridges.map(bridgeCard));renderLights();$('#updated').textContent=t('Zuletzt gelesen: ')+new Date(data.updated_at).toLocaleString(i18n.locale);const failed=lamps.filter(l=>l.status==='unavailable').length;$('#notice').textContent=failed?failed+t(' Statusabfrage(n) fehlgeschlagen. Angezeigte Daten prüfen.'):t('Nur Anzeige · keine Lampenänderungen · automatische Aktualisierung alle 10 Sekunden');$('#notice').classList.toggle('error',failed>0);}
function updateFilterOptions(select,options,allLabel){if(select.options.length===options.length+1&&options.every((item,index)=>select.options[index+1].value===item.value&&select.options[index+1].text===item.label))return;const selected=select.value;select.replaceChildren(new Option(allLabel,''),...options.map(item=>new Option(item.label,item.value)));select.value=options.some(item=>item.value===selected)?selected:'';}
function topologyFilter(items,bridgeSelect,roomSelect,bridges){
 const options=[...bridges].sort((a,b)=>a.name.localeCompare(b.name,i18n.locale)).map(b=>({value:b.id,label:b.name}));
 updateFilterOptions(bridgeSelect,options,t('Alle Bridges'));
 const scoped=items.filter(item=>!bridgeSelect.value||item.bridge_id===bridgeSelect.value);
 const rooms=[...new Set(scoped.map(item=>item.room||''))].sort((a,b)=>a.localeCompare(b,i18n.locale));
 updateFilterOptions(roomSelect,rooms.map(room=>({value:JSON.stringify(room),label:room||t('Ohne Raum/Zone')})),t('Alle Räume/Zonen'));
 return scoped.filter(item=>!roomSelect.value||JSON.stringify(item.room||'')===roomSelect.value);
}
function renderLights(){if(!data)return;const term=$('#search').value.toLocaleLowerCase(i18n.locale);const visible=allLights().filter(l=>!l.ignored||$('#show-ignored').checked).map(l=>({...l,bridge_id:l.bridge.id}));const found=topologyFilter(visible,$('#bridge-filter'),$('#room-filter'),data.bridges).filter(l=>((l.name||'')+' '+(l.room||'')+' '+l.bridge.name).toLocaleLowerCase(i18n.locale).includes(term));filteredLights=found;$('#light-list').replaceChildren(...(found.length?found.map(l=>lamp(l,true)):[node('p',t('Keine eingerichtete Lampe für diesen Filter.'),'info')]));}
async function refresh(){if(busy||!adminSession)return;busy=true;$('#refresh').disabled=true;try{const response=await adminRequest('/api/overview');if(!response.ok)throw Error();const result=await response.json();if(result.status!=='ok')throw Error();data=result;render();}catch(e){$('#notice').textContent=t('Verbindung zum Dienst unterbrochen. Vorhandene Anzeigen können veraltet sein. Erneut aktualisieren.');$('#notice').classList.add('error');}finally{busy=false;$('#refresh').disabled=false;}}
document.querySelectorAll('nav button').forEach(button=>button.addEventListener('click',()=>{const page=button.dataset.page;document.body.dataset.page=page;document.querySelectorAll('.page').forEach(p=>p.hidden=p.id!=='page-'+page);document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b===button));$('#title').textContent=names[page][0];$('#subtitle').textContent=names[page][1];if(page==='monitor')loadMonitor();}));
$('#refresh').addEventListener('click',()=>$('#page-scenes').hidden?Promise.all([refresh(),loadScenes()]):scanScenes());$('#search').addEventListener('input',renderLights);$('#bridge-filter').addEventListener('change',renderLights);$('#room-filter').addEventListener('change',renderLights);bootAdmin();setInterval(()=>{if(!document.hidden&&adminSession)refresh();},10000);

let pendingRemoval=null, lampChanging=false;
function lampActions(l){
 const box=node('div',undefined,'lamp-actions');const key=l.bridge.id+'/'+l.id;
 const ignore=node('button',l.ignored?t('Wieder einblenden'):t('Ignorieren'));ignore.type='button';ignore.disabled=lampChanging;
 ignore.onclick=()=>changeLamp(l,'ignore',!l.ignored);box.append(ignore);
 if(pendingRemoval===key){
  box.append(node('span',t('Nur aus Hue2Lox entfernen? Beim nächsten Einlesen kann sie wieder erscheinen. Für dauerhaftes Ausblenden „Ignorieren“ wählen.'),'sub'));
  const yes=node('button',t('Jetzt entfernen'));yes.type='button';yes.disabled=lampChanging;yes.onclick=()=>changeLamp(l,'remove');
  const no=node('button',t('Abbrechen'));no.type='button';no.onclick=()=>{pendingRemoval=null;renderLights();};box.append(yes,no);
 }else{const remove=node('button',t('Entfernen'));remove.type='button';remove.disabled=lampChanging;remove.onclick=()=>{pendingRemoval=key;renderLights();};box.append(remove);}
 return box;
}
async function changeLamp(l,action,ignored=true){
 if(lampChanging)return;lampChanging=true;renderLights();
 try{
  const response=await adminRequest('/api/admin/lights/'+action,{bridge_id:l.bridge.id,light_id:l.id,ignored});
  if(!response.ok)throw Error();
  pendingRemoval=null;selectedLights.delete(l.bridge.id+'/'+l.id);openCommandKey=null;
  await refresh();await loadLoxone();await loadBridgeManagement();
  $('#lamp-message').textContent=action==='remove'?t('Aus Hue2Lox entfernt. Erneutes Einlesen kann die Lampe wieder hinzufügen.'):ignored?t('Lampe ignoriert. Über „Ignorierte anzeigen“ kannst du sie wieder einblenden.'):t('Lampe wieder eingeblendet.');
 }catch(error){$('#lamp-message').textContent=t('Änderung fehlgeschlagen. Bitte erneut versuchen; eventuell läuft gerade eine Inventur.');}
 finally{lampChanging=false;renderLights();}
}
$('#show-ignored').addEventListener('change',renderLights);

try{const page=sessionStorage.getItem("hue2lox-language-page");sessionStorage.removeItem("hue2lox-language-page");if(Object.hasOwn(names,page))document.querySelector(`nav button[data-page="${page}"]`).click();}catch(_){}
