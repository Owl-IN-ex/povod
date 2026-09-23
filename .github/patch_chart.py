from pathlib import Path
import re

p = Path('index.html')
html = p.read_text(encoding='utf-8')

old_css = '.chart-swatch{width:8px;height:8px;border-radius:50%;background:hsl(var(--swatch-h) 58% 52%)}'
new_css = '.chart-swatch{width:8px;height:8px;border-radius:50%;background:var(--swatch-color,#dc4a29);box-shadow:0 0 0 1px color-mix(in srgb,var(--swatch-color,#dc4a29) 30%,transparent)}'
if old_css not in html:
    raise SystemExit('Expected chart swatch CSS not found')
html = html.replace(old_css, new_css, 1)

pattern = re.compile(r"      function renderExpenseChart\(r\)\{.*?\n      \}", re.S)
m = pattern.search(html)
if not m:
    raise SystemExit('renderExpenseChart not found')

new_chart = '''      function renderExpenseChart(r){
        const active=r.activeExpenses;$('donut-total').textContent=r.expensesInvalid?'—':money(active)+' ₽';
        const entries=state.expenses.map(e=>({name:e.name,value:state.mode==='fact'?r.rows[e.id]?.effectiveFact||0:r.rows[e.id]?.plan||0})).filter(x=>x.value>0).sort((a,b)=>b.value-a.value);
        const donut=$('expense-donut'),legend=$('chart-legend');
        if(r.expensesInvalid||active<=0||!entries.length){donut.style.background='var(--chart-empty)';legend.innerHTML='<span class="chart-empty">Добавьте расходы, чтобы увидеть структуру.</span>';return;}

        const lightPalette=['#E24A2B','#2F6FED','#2AA876','#8A4BD6','#E7A21A','#1397B8','#C23C78','#65723A'];
        const darkPalette=['#FF6B4A','#5B8CFF','#4CCB98','#B77AE5','#FFC857','#38BBD6','#E56A9D','#9EB35A'];
        const palette=state.theme==='dark'?darkPalette:lightPalette;

        let at=0;
        const segments=[];
        entries.forEach((x,i)=>{
          const pct=x.value/active*100,end=at+pct,color=palette[i%palette.length];
          segments.push(color+' '+at.toFixed(2)+'% '+end.toFixed(2)+'%');
          x.pct=pct;x.color=color;at=end;
        });
        donut.style.background='conic-gradient('+segments.join(',')+')';
        const visible=entries.slice(0,6);
        legend.innerHTML=visible.map(x=>'<div class="chart-item"><span class="chart-swatch" style="--swatch-color:'+x.color+'"></span><span class="chart-name">'+escapeHtml(x.name)+'</span><strong>'+Math.round(x.pct)+'%</strong></div>').join('')+(entries.length>6?'<div class="chart-more">Ещё '+(entries.length-6)+' катег.</div>':'');
      }'''
html = html[:m.start()] + new_chart + html[m.end():]

if 'Текущая сборка · 0.10.1 beta' not in html:
    raise SystemExit('Expected visible version 0.10.1 beta not found')
html = html.replace('Текущая сборка · 0.10.1 beta', 'Текущая сборка · 0.10.2 beta', 1)
html = html.replace("const APP_VERSION='0.10.1-beta'", "const APP_VERSION='0.10.2-beta'", 1)

marker = '''        <div class="patchnotes-item">
          <span class="patchnotes-dot"></span>
          <p><strong>Выравнивание покупок на мобильном</strong><br>Количество «Нужно», поле «Куплено» и «Осталось» теперь стоят строго по центру своих колонок.</p>
        </div>'''
note = '''
        <div class="patchnotes-item">
          <span class="patchnotes-dot"></span>
          <p><strong>Контрастнее диаграмма расходов</strong><br>Цвета категорий стали заметно различаться по оттенку и яркости, чтобы сегменты и легенду было легче читать.</p>
        </div>'''
if marker not in html:
    raise SystemExit('Patchnote marker not found')
html = html.replace(marker, marker + note, 1)

p.write_text(html, encoding='utf-8')
print('Patched index.html to 0.10.2 beta')
