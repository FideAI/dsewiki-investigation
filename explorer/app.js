'use strict';
const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text)n.textContent=text;if(cls)n.className=cls;return n;};
let items=[],shown=80;
function link(text,url){const a=el('a',text);a.href=url;return a;}
function renderList(){
 const q=$('search').value.trim().toLowerCase(),kind=$('kind').value;
 const found=items.filter(i=>(q||kind==='all'||kind==='featured'&&i.priority||i.kind===kind)&&(!$('disputed').checked||i.disputed)&&(!q||[i.id,i.title,i.rationale,i.assessment,i.report].join(' ').toLowerCase().includes(q))).sort((a,b)=>(a.priority||999)-(b.priority||999)||a.id.localeCompare(b.id));
 $('count').textContent=`${found.length.toLocaleString()} matching items`;
 $('list').replaceChildren(...found.slice(0,shown).map(i=>{const a=link('',`#${i.id}`);a.append(el('span',`${i.id} · ${i.assessment}`,'meta'),el('span',i.title));a.className='result';if(location.hash===`#${i.id}`)a.setAttribute('aria-current','true');return a;}));
 $('more').hidden=found.length<=shown;
}
function section(title,text){if(!text)return;const s=el('section');s.append(el('h3',title),el('p',typeof text==='string'?text:JSON.stringify(text,null,2)));$('detail').append(s);}
function renderDetail(){
 const id=decodeURIComponent(location.hash.slice(1))||'P01',i=items.find(x=>x.id===id);$('detail').replaceChildren();
 if(!i){$('detail').append(el('h2','Assessment not found'),el('p','Search the catalog or select a claim from the list.'));return;}
 $('detail').append(el('p',`${i.id} · ${i.kind}`,'eyebrow'),el('h2',i.title),el('p',i.assessment,'verdict'));
 if(i.disputed)$('detail').append(el('p','Contestable assessment · excluded from the narrower sensitivity count','disputed'));
 section('Why we assessed it this way',i.rationale);section(i.kind==='publication'?'Context':'Original coding notes',i.context);section('Limits or required correction',i.limits);section('What the report gets right',i.validCore);
 if(i.followupClaims?.length)section('Claims in the follow-up',i.followupClaims.join('\n\n'));
 if(i.sources.length){$('detail').append(el('h3','Read the original passages'));i.sources.forEach(s=>{$('detail').append(link(`${s.caption||s.report} · ${s.lines.length?'lines '+Math.min(...s.lines)+'–'+Math.max(...s.lines):'full report'} ↗`,s.url));});}
 if(i.evidence.length){$('detail').append(el('h3','Evidence and analysis'));const ul=el('ul');i.evidence.forEach(e=>{const li=el('li');li.append(e.url?link(e.reference,e.url):el('span',`${e.reference} — record identifier or shorthand; consult the source and reproduction instructions.`));ul.append(li);});$('detail').append(ul);}
 if(i.related?.length){$('detail').append(el('h3','Underlying assessments'));const p=el('p');i.related.forEach(r=>{p.append(link(r,`#${r}`),document.createTextNode(' · '));});$('detail').append(p);}
 const issue=new URL('https://github.com/FideAI/dsewiki-investigation/issues/new');issue.searchParams.set('template','challenge.yml');issue.searchParams.set('title',`Review ${i.id}: ${i.title.slice(0,90)}`);issue.searchParams.set('claim-id',i.id);
 const box=el('div',null,'challenge');box.append(el('h3','Does our interpretation hold up?'),el('p','Point to the passage or record, explain the disagreement, and suggest a correction. Public feedback is not counted as independent adjudication until reviewed.'),link('Challenge this assessment ↗',issue.href));$('detail').append(box);renderList();
}
['search','kind','disputed'].forEach(id=>$(id).addEventListener('input',()=>{shown=80;renderList();}));$('more').addEventListener('click',()=>{shown+=80;renderList();});window.addEventListener('hashchange',renderDetail);
fetch('data.json').then(r=>{if(!r.ok)throw new Error('Catalog unavailable');return r.json();}).then(d=>{items=d.items;renderDetail();}).catch(()=>{$('detail').replaceChildren(el('h2','The evidence catalog could not load.'),link('Inspect the repository directly','https://github.com/FideAI/dsewiki-investigation'));$('count').textContent='Please reload or open the repository.';});
