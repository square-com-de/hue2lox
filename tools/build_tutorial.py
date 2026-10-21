"""Render the repository tutorial to the bundled, script-free help page."""
from pathlib import Path
import html
import re
import sys
LANG="en" if "--english" in sys.argv else "de"

ROOT=Path(__file__).resolve().parent.parent

def inline(text):
    text=html.escape(text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    def link(match):
        label,url=match.groups()
        return '<a href="'+url+'" target="_blank" rel="noopener noreferrer">'+label+'</a>' if url.startswith('https://') else label
    return re.sub(r'\[([^]]+)\]\(([^)]+)\)',link,text)

lines=(ROOT/'docs'/('TUTORIAL.md' if LANG=='en' else 'TUTORIAL.de.md')).read_text().splitlines();body=[];i=0
while i<len(lines):
    line=lines[i]
    if not line.strip():i+=1;continue
    if line.startswith('```'):
        code=[];i+=1
        while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
        body.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');i+=1;continue
    if line.startswith('#'):
        heading,text=line.split(' ',1);level=len(heading)
        body.append(f'<h{level}>'+inline(text)+f'</h{level}>');i+=1;continue
    image=re.fullmatch(r'!\[([^]]+)\]\(\.\./web/(tutorial-[a-z]+\.png)\)',line)
    if image:
        alt,file=image.groups();body.append('<figure><a href="/assets/'+file+'" target="_blank" rel="noopener"><img src="/assets/'+file+'" alt="'+html.escape(alt)+'" loading="lazy"></a><figcaption>'+html.escape(alt)+' · Anklicken zum Vergrößern</figcaption></figure>');i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=[c.strip() for c in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',c) for c in cells):rows.append(cells)
            i+=1
        table='<div class="table-scroll"><table><thead><tr>'+''.join('<th>'+inline(c)+'</th>' for c in rows[0])+'</tr></thead><tbody>'
        table+=''.join('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>';body.append(table);continue
    match=re.match(r'(- |\d+\. )',line)
    if match:
        ordered=match[0]!='- ';tag='ol' if ordered else 'ul';items=[];start=int(match[0].split('.')[0]) if ordered else 1
        while i<len(lines) and re.match(r'\d+\. ' if ordered else r'- ',lines[i]):
            content=re.sub(r'^(- |\d+\. )','',lines[i]);i+=1
            while i<len(lines) and lines[i].startswith('  '):content+=' '+lines[i].strip();i+=1
            items.append('<li>'+inline(content)+'</li>')
        body.append('<'+tag+(f' start="{start}"' if ordered else '')+'>'+''.join(items)+'</'+tag+'>');continue
    paragraph=[line];i+=1
    while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|!\[|- |\d+\. )',lines[i]):paragraph.append(lines[i]);i+=1
    body.append('<p>'+inline(' '.join(paragraph))+'</p>')
page='<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hue2Lox · Anleitung für Loxone Config</title><link rel="stylesheet" href="/assets/tutorial.css"></head><body><nav><a href="/">← Zurück zu Hue2Lox</a><span>ANLEITUNG</span></nav><main>'+''.join(body)+'</main><footer>Hue2Lox · by square | com</footer></body></html>\n'
if LANG=='en':
    page=page.replace('lang="de"','lang="en"').replace('Anleitung für Loxone Config','Loxone Config guide').replace('← Zurück zu Hue2Lox','← Back to Hue2Lox').replace('ANLEITUNG','GUIDE').replace('Anklicken zum Vergrößern','Click to enlarge')
page=page.replace('</nav>','<a href="/tutorial">Deutsch</a><a href="/tutorial/en">English</a></nav>')
(ROOT/('web/tutorial-en.html' if LANG=='en' else 'web/tutorial.html')).write_text(page)
