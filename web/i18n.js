'use strict';
// German source phrases are stable message keys. Device names and protocol values
// are never passed through a DOM-wide translation observer.
const i18n = (()=>{
 function choose(saved,languages){if(['de','en'].includes(saved))return saved;for(const locale of languages||[]){const base=locale.toLowerCase().split('-')[0];if(['de','en'].includes(base))return base;}return 'en';}
 let saved;try{saved=localStorage.getItem('hue2lox-language');}catch(_){}
 const language=choose(saved,navigator.languages||[navigator.language]);
 const locale=language==='de'?'de-DE':'en-GB';
 function translate(key){return window.HUE2LOX_MESSAGES?.[language]?.[key]??window.HUE2LOX_MESSAGES?.de?.[key]??key;}
 function staticPage(){
  document.documentElement.lang=language;
  // Runs once, before application code inserts user/bridge-provided strings.
  const walker=document.createTreeWalker(document.documentElement,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){const n=walker.currentNode;if(n.parentElement?.closest('script,style,code,pre'))continue;const key=n.textContent.trim();if(key&&Object.hasOwn(window.HUE2LOX_MESSAGES.de,key))n.textContent=n.textContent.replace(key,translate(key));}
  for(const e of document.querySelectorAll('[title],[placeholder],[aria-label],[alt]'))for(const attr of ['title','placeholder','aria-label','alt']){const value=e.getAttribute(attr);if(value)e.setAttribute(attr,translate(value));}
  for(const select of document.querySelectorAll('[data-language-select]')){select.value=language;select.addEventListener('change',()=>{try{localStorage.setItem('hue2lox-language',select.value);sessionStorage.setItem('hue2lox-language-page',document.body.dataset.page||'overview');}catch(_){}location.reload();});}
  for(const button of document.querySelectorAll('[data-language]')){button.setAttribute('aria-pressed',String(button.dataset.language===language));button.addEventListener('click',()=>{if(button.dataset.language===language)return;try{localStorage.setItem('hue2lox-language',button.dataset.language);sessionStorage.setItem('hue2lox-language-page',document.body.dataset.page||'overview');}catch(_){}location.reload();});}
  for(const a of document.querySelectorAll('a[href="/tutorial"]'))a.href=language==='en'?'/tutorial/en':'/tutorial';
 }
 staticPage();
 return {language,locale,translate,choose};
})();
function t(key){return i18n.translate(key);}
