'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ui = require('../web/catalogo.js');
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname,'../catalog/mods.json'),'utf8'));
const find = id => catalog.mods.find(m => m.id === id);

test('busca ignora acentos e exige todas as palavras', () => {
  assert.equal(ui.normalize('CONVERSÃO'), 'conversao');
  assert.equal(ui.matches(find('hanbok-revised'),{query:'HANBOK material'}),true);
  assert.equal(ui.matches(find('hanbok-revised'),{query:'hanbok inexistente'}),false);
});
test('escopo e evidência não confundem catálogo principal com disponível', () => {
  assert.equal(catalog.mods.filter(m => ui.matches(m,{scope:'principal'})).length,49);
  assert.equal(catalog.mods.filter(m => ui.matches(m,{scope:'pendente'})).length,18);
  assert.equal(catalog.mods.filter(m => ui.matches(m,{scope:'historico'})).length,8);
  assert.equal(ui.matches(find('hidden-crafting'),{scope:'principal'}),false);
  assert.equal(ui.matches(find('tal-karlstein'),{verification:'page_read'}),true);
});
test('filtro de corpo não confunde UNP com BHUNP', () => {
  assert.equal(ui.matches(find('urbon-chic-lua'),{body:'3BA'}),true);
  assert.equal(ui.matches(find('urbon-chic-lua'),{body:'BHUNP'}),true);
  assert.equal(ui.matches(find('urbon-chic-lua'),{body:'UNP'}),false);
  assert.equal(ui.matches(find('tal-karlstein'),{body:'unknown'}),true);
});
test('seleção corrompida ou desconhecida não quebra a interface', () => {
  for (const raw of ['bad json','{}','null','false']) assert.equal(ui.restoreSelection(raw,catalog.mods).size,0);
  const selected=ui.restoreSelection('["hanbok-revised","missing","hanbok-revised",42]',catalog.mods);
  assert.deepEqual([...selected],['hanbok-revised']);
});
test('seleção e filtros combinam sem selecionar tudo por engano', () => {
  const selected=new Set(['hanbok-revised']);
  assert.equal(ui.matches(find('hanbok-revised'),{onlySelected:true},selected),true);
  assert.equal(ui.matches(find('bdo-guardian'),{onlySelected:true},selected),false);
});
test('exportação é plano de pesquisa, nunca download concluído', () => {
  const plan=ui.exportPlan(catalog,new Set(['bdo-sura-blade','hanbok-revised','missing']));
  assert.equal(plan.type,'research_plan_not_downloaded_mods');
  assert.equal(plan.entries.length,2);
  assert.equal(plan.entries[0].id,'hanbok-revised');
  assert.ok(plan.entries.every(m => m.downloaded===false));
  assert.ok(ui.planText(plan).includes('Arquivo baixado por esta interface: NÃO'));
  assert.ok(ui.planText(plan).includes('https://www.nexusmods.com/'));
  plan.entries[0].requirements.push('fixture');
  assert.ok(!find('hanbok-revised').requirements.includes('fixture'));
});

// DOM mínimo para executar o código real de montagem/eventos sem dependências.
// append() retorna undefined como no navegador (não permite encadeamento acidental).
function browser(storageThrows=false) {
  const nodes=new Map();
  let active=null;
  class Element {
    constructor(tag){this.tagName=tag;this.children=[];this.events={};this.attrs={};this._text='';this.value='';this.checked=false;this.hidden=false;this.disabled=false;}
    set textContent(value){this._text=String(value);this.children=[];}
    get textContent(){return this._text+this.children.map(n => n.textContent).join('');}
    append(...items){for (const item of items){if(item.tagName==='#fragment') this.children.push(...item.children);else this.children.push(item);}}
    replaceChildren(...items){this.children=[];this.append(...items);}
    setAttribute(key,value){this.attrs[key]=value;}
    addEventListener(name,callback){(this.events[name] ||= []).push(callback);}
    dispatch(name){for(const callback of this.events[name]||[]) callback({preventDefault(){}});}
    click(){if(!this.disabled)this.dispatch('click');}
    remove(){this.removed=true;}
    focus(){active=this;}
  }
  const ids=['catalog-data','total-records','selection-count','status','category','scope','body','verification','query','only-selected','export-txt','export-json','clear-selection','reset-filters','cards','results','empty','coverage','version'];
  for(const id of ids) {const node=new Element('div');node.id=id;nodes.set(id,node);}
  const labels={categories:{packs:'Packs',armaduras:'Armaduras',conversoes:'Conversões',cabelos:'Cabelos',animacoes:'Animações',patches:'Patches',integracoes:'Integrações',personagens:'Personagens'},scopes:{principal:'Principal',pendente:'Pendente',historico:'Histórico'},methods:{page_read:'Lida',search_index:'Busca',author_index:'Índice'},availability:{},permissions:{}};
  nodes.get('catalog-data').textContent=JSON.stringify({catalog,stats:{total:75,scopes:{principal:49,pendente:18,historico:8}},labels});
  nodes.get('scope').value='principal';
  function walk(root){return [root,...root.children.flatMap(walk)];}
  const get=id => nodes.get(id)||walk(nodes.get('cards')).find(n=>n.id===id);
  const store=new Map(), blobs=[];
  const document={getElementById:get,createElement:tag=>new Element(tag),createDocumentFragment:()=>new Element('#fragment'),body:new Element('body')};
  const context={document,localStorage:{getItem(key){if(storageThrows)throw Error('blocked');return store.get(key)||null;},setItem(key,value){if(storageThrows)throw Error('blocked');store.set(key,value);}},Blob,URL:{createObjectURL(blob){blobs.push(blob);return 'blob:test';},revokeObjectURL(){}},setTimeout(){}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../web/catalogo.js'),'utf8'),context);
  return {get,walk,blobs,store,getActive:()=>active};
}
test('DOM: monta todas as fichas principais, inclusive relações', () => {
  const b=browser();
  assert.equal(b.get('cards').children.length,49);
  assert.equal(b.get('total-records').textContent,'75');
  assert.equal(b.get('export-txt').disabled,true);
  const links=b.walk(b.get('cards')).filter(n=>n.tagName==='a'&&n.target==='_blank');
  assert.ok(links.length>49);
  assert.ok(links.every(a=>a.rel==='noopener noreferrer'));
});
test('DOM: busca, escopo e limpar filtros funcionam', () => {
  const b=browser();
  b.get('query').value='nao-ha-esta-referencia';b.get('query').dispatch('input');
  assert.equal(b.get('cards').children.length,0);assert.equal(b.get('empty').hidden,false);
  b.get('reset-filters').click();assert.equal(b.get('cards').children.length,49);
  b.get('scope').value='historico';b.get('scope').dispatch('change');
  assert.equal(b.get('cards').children.length,8);
  b.get('scope').value='';b.get('scope').dispatch('change');
  assert.equal(b.get('cards').children.length,75);
});
test('DOM: selecionar, exportar e limpar operam sobre a seleção', async () => {
  const b=browser();
  const card=b.get('mod-hanbok-revised');
  const box=b.walk(card).find(n=>n.tagName==='input');box.checked=true;box.dispatch('change');
  assert.equal(b.get('selection-count').textContent,'1 selecionado');
  assert.equal(b.get('export-json').disabled,false);
  b.get('export-json').click();
  assert.equal(b.blobs.length,1);
  const plan=JSON.parse(await b.blobs[0].text());
  assert.deepEqual(plan.entries.map(m=>m.id),['hanbok-revised']);
  assert.equal(plan.entries[0].downloaded,false);
  b.get('only-selected').checked=true;b.get('only-selected').dispatch('change');
  assert.equal(b.get('cards').children.length,1);
  b.get('clear-selection').click();
  assert.equal(b.get('cards').children.length,0);assert.equal(b.get('selection-count').textContent,'0 selecionados');
});
test('DOM: relacionamento revela e foca a ficha referenciada', () => {
  const b=browser();
  const card=b.get('mod-caenarvon-hair-addon');
  b.walk(card).find(n=>n.href==='#mod-dint-bdor-hair').click();
  assert.equal(b.get('query').value,'dint-bdor-hair');
  assert.equal(b.getActive().id,'mod-dint-bdor-hair');
});
test('DOM: indisponibilidade de localStorage é explicada sem impedir uso', () => {
  const b=browser(true);
  assert.equal(b.get('cards').children.length,49);
  assert.match(b.get('status').textContent,/temporária/);
  const box=b.walk(b.get('mod-hanbok-revised')).find(n=>n.tagName==='input');
  box.checked=true;box.dispatch('change');
  assert.equal(b.get('export-txt').disabled,false);
  assert.match(b.get('status').textContent,/Exporte/);
});
