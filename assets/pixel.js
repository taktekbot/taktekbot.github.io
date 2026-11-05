// Pixel headings. Glyphs: Nizar's 6x6 letters from the first taktek.io (Dec 2025), plus C F P V X Y 0-9 $ , drawn to match.
// <canvas class="px" data-text="LINE|LINE"> draws the text; h1[data-px] gets a canvas from its own text.
(function(){
const G={
A:[".####.","###.##","###.##","######","###.##","###.##"],B:["#####.","###.#.","######","###..#","###..#","######"],
C:[".#####","###...","###...","###...","###...",".#####"],D:["#####.","###.##","###..#","###..#","###.##","#####."],
E:[".#####","####..","######","####..","####..",".#####"],F:["######","####..","#####.","####..","####..","####.."],
G:[".#####","###.##","##....","##.###","###.##",".#####"],H:["###.##","###.##","######","######","###.##","###.##"],
I:["######","######","..###.","..###.","..###.","######"],K:["##..##","##.###","#####.","######","##.###","##..##"],
L:["###...","###...","###...","###...","#####.","######"],M:["##...#","###.##","######","######","##.#.#","##...#"],
N:["###..#","####.#","######","######","##.###","##..##"],O:[".####.","###.##","###.##","###.##","###.##",".####."],
P:["#####.","###.##","###.##","#####.","###...","###..."],R:["######","##.###","##..##","#####.","##.###","##..##"],
S:[".#####","####..","#####.",".#####","..####","#####."],T:["######","######",".####.","..###.","..###.","..###."],
U:["##...#","##...#","##...#","##...#","######",".#####"],V:["###.##","###.##","###.##","###.##",".####.","..##.."],
W:["##.#.#","##.#.#","##.#.#","##.#.#","######",".#####"],X:["###.##",".####.","..##..",".####.","###.##","###.##"],
Y:["###.##","###.##",".####.","..###.","..###.","..###."],Z:["######","######","..###.",".###..","######","######"],
"0":[".####.","###.##","###.##","###.##","###.##",".####."],"1":["..###.",".####.","..###.","..###.","..###.","######"],
"2":[".####.","##..##","...###","..###.",".###..","######"],"3":["#####.","....##","..###.","....##","....##","#####."],
"4":["###.##","###.##","######","....##","....##","....##"],"5":["######","###...","#####.","....##","....##","#####."],
"6":[".####.","###...","#####.","###.##","###.##",".####."],"7":["######","....##","...##.","..###.","..###.","..###."],
"8":[".####.","###.##",".####.","###.##","###.##",".####."],"9":[".####.","###.##","###.##",".#####","....##",".####."],
"$":["..#...",".#####","####..",".####.","..####","#####."],",":["......","......","......","......","##....",".#...."],
".":["......","......","......","......","##....","##...."],"?":["######","##...#","...###","...##.","......","...##."],
"@":[".####.","#....#","#.##.#","#.####","#.....",".#####"]," ":["......","......","......","......","......","......"]};
const root=document.documentElement;
const tok=n=>getComputedStyle(root).getPropertyValue(n).trim();
document.querySelectorAll('h1[data-px]').forEach(h=>{const c=document.createElement('canvas');c.className='px';
  c.dataset.text=h.textContent.trim().toUpperCase();c.setAttribute('aria-hidden','true');h.classList.add('sr');h.after(c)});
const cvs=[...document.querySelectorAll('canvas.px')];
function draw(cv,cell){
  const lines=cv.dataset.text.split('|'), k=+(cv.dataset.scale||1), c=cell*k;
  const cols=Math.max(...lines.map(l=>l.length))*8, rows=lines.length*8;
  const dpr=Math.min(2,window.devicePixelRatio||1);
  cv.width=cols*c*dpr; cv.height=rows*c*dpr; cv.style.width=cols*c+'px';
  const x=cv.getContext('2d'); x.setTransform(dpr,0,0,dpr,0,0); x.fillStyle=tok('--ink');
  lines.forEach((l,li)=>[...l].forEach((ch,ci)=>(G[ch]||G[' ']).forEach((r,ry)=>[...r].forEach((p,rx)=>{
    if(p==='#')x.fillRect((ci*8+1+rx)*c,(li*8+1+ry)*c,c,c)}))));
}
function snap(el,cell){ // sit on the page grid
  el.style.transform='';const r=el.getBoundingClientRect();
  const dx=((r.left+scrollX)%cell+cell)%cell, dy=((r.top+scrollY)%cell+cell)%cell;
  el.style.transform='translate('+(-dx)+'px,'+(-dy)+'px)';
}
function all(){root.style.setProperty('--line',Math.max(1,1/(window.devicePixelRatio||1))+'px');const cell=parseFloat(tok('--cell'))||8;cvs.forEach(cv=>draw(cv,cell));
  [...cvs,...document.querySelectorAll('.face')].forEach(el=>snap(el,cell))}
addEventListener('resize',all);
all(); document.fonts&&document.fonts.ready.then(all);
})();
