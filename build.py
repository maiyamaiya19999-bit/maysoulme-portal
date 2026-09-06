#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка портала maysoulme.

  python3 build.py

Читает guides.json, копирует исходные HTML-гайды в guides/<slug>/index.html,
чинит пути к логотипу, добавляет продающий блок интенсива, генерирует главную.
Если исходник недоступен — уже собранный гайд остаётся как есть.

Чтобы добавить гайд: положить HTML, прописать блок в guides.json
(slug, title, desc, tag, src, bridge) и запустить build.py.
"""
import json, re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
SOURCE_ROOTS = {
    "assets": HOME / "Desktop/клод/maysoulme-assets",
    "repos":  HOME / "Desktop/клод/архив/portal-sources",
    "desk":   HOME / "Desktop/клод",
}

SITE = "https://maysoulme.ru"

def strip_tags(t):
    return re.sub(r'<[^>]+>', '', t)

_OLD_STAR = '<svg viewBox="0 0 100 100" fill="currentColor"><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(0.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(30.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(60.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(90.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(120.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(150.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(180.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(210.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(240.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(270.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(300.0 50 50)"/><rect x="47" y="6" width="6" height="44" rx="3" transform="rotate(330.0 50 50)"/></svg>'
TG = "https://t.me/maysoulme"
INTENSIV = "https://mayasoul.ru"

# ---------------------------------------------------------------- продающий блок в гайде

BAR = """<div class="ms-progress"><i></i></div>
<div class="ms-bar">
  <a class="ms-bar__logo" href="../../"><img src="../../logo-ms.png" alt="MS"></a>
  <a class="ms-bar__back" href="../../">&larr; Все гайды</a>
  <span class="ms-bar__min">%%MIN%% мин чтения</span>
  <span class="ms-bar__name">maysoulme</span>
  <button class="ms-bar__theme theme" type="button" onclick="msTheme()" aria-label="Сменить тему">☾</button>
</div>

"""

SELL = """
<section class="ms-sell">
  <div class="ms-sell__in">
    <p class="ms-sell__bridge">%%BRIDGE%%</p>

    <div class="ms-sell__rule"></div>

    <span class="ms-sell__label">Интенсив</span>
    <h2 class="ms-sell__title">ИИ-стратегия <i>на миллион</i></h2>
    <p class="ms-sell__lead">Гайды — это отдельные детали. На интенсиве мы собираем из них систему, чтобы блог рос не от одного удачного ролика, а от того, что за ним стоит.</p>

    <div class="ms-sell__proof">
      <div class="ms-sell__proof-item">
        <span class="ms-sell__num">600 000</span>
        <span class="ms-sell__cap">просмотров — и 8 подписчиков</span>
      </div>
      <div class="ms-sell__proof-vs">против</div>
      <div class="ms-sell__proof-item ms-sell__proof-item--win">
        <span class="ms-sell__num">19 000</span>
        <span class="ms-sell__cap">просмотров — 240 подписчиков и 30 000 ₽</span>
      </div>
    </div>
    <p class="ms-sell__proof-note">Дело не в удаче и не в количестве роликов. Дело в том, кому вы говорите, что именно и куда ведёте человека дальше.</p>

    <ul class="ms-sell__list">
      <li><b>Стратегия и позиционирование</b> — за что вам платят и чем вы отличаетесь от сотни похожих экспертов</li>
      <li><b>Текстовые и разговорные ролики</b> — один формат набирает холодную аудиторию, второй превращает её в свою</li>
      <li><b>ИИ-агент с памятью канала</b> — помнит все ваши посты и предлагает продолжение начатых тем, чтобы блог звучал как одна история</li>
      <li><b>Парсер идей</b> — собирает залетающие ролики вашей ниши, пока вы завтракаете, и выдаёт готовые темы</li>
      <li><b>Готовые ассистенты и шаблоны</b> — сценарист, редактор, распаковка, прогревы: забираете и пользуетесь</li>
    </ul>

    <p class="ms-sell__author">Всё это я собрала в Claude Code без единого программиста — просто объясняла задачи обычными словами. На интенсиве показываю ровно то, что делаю сама каждый день.</p>
    <span class="ms-sell__sign">Майя</span>

    <a class="ms-sell__cta" href="%%INTENSIV%%">Смотреть программу интенсива →</a>
    <p class="ms-sell__note">Вечный доступ · чат поддержки со мной · формат VIP с личным сопровождением</p>
  </div>
</section>

<footer class="ms-foot">
  <a class="ms-foot__back" href="../../">← Все гайды maysoulme</a>
  <p>Бесплатная библиотека <a href="../../">maysoulme</a> · новое сначала в <a href="%%TG%%">телеграм-канале</a></p>
</footer>

<style>
  @font-face { font-family: 'Denistina'; src: url('../../denistina.ttf') format('truetype'); font-display: swap; }

  nav.nav, header.nav, nav:not([class]) { display: none !important; }
  .ms-bar { position: sticky; top: 0; z-index: 9999; display: flex; align-items: center; gap: 18px;
    padding: 11px 22px; background: var(--g-bg, #fff); border-bottom: 1px solid var(--g-line, #e6e4e1);
    font-family: 'Inter', -apple-system, sans-serif; }
  .ms-bar__logo img { height: 24px; display: block; }
  .ms-bar__min { font-size: 13px; color: var(--g-faint, #8f8a84); margin-left: 6px; }
  .ms-progress { position: fixed; top: 0; left: 0; right: 0; height: 2px; z-index: 10000; pointer-events: none; }
  .ms-progress i { display: block; height: 100%; width: 0; background: var(--g-accent, #710C04); transition: width .1s linear; }

  .ms-toc { display: block; width: 100%; grid-column: 1 / -1; flex-basis: 100%;
    background: var(--g-surface, #f5f5f5); padding: 26px 28px 22px; margin: 0 0 44px;
    font-family: 'Inter', -apple-system, sans-serif; }
  .ms-toc__label { display: block; font-size: 10.5px; font-weight: 600; letter-spacing: .22em; text-transform: uppercase;
    color: var(--g-faint, #8f8a84); margin-bottom: 14px; }
  .ms-toc ol { list-style: none; margin: 0; padding: 0; counter-reset: toc; columns: 2; column-gap: 36px; }
  .ms-toc li { counter-increment: toc; break-inside: avoid; padding: 7px 0; border-top: 1px solid var(--g-line, #e6e4e1); }
  .ms-toc li:first-child { border-top: none; }
  .ms-toc a { text-decoration: none; color: var(--g-fg, #1a1a1a); font-size: 15px; line-height: 1.45; display: flex; gap: 12px; }
  .ms-toc a::before { content: counter(toc, decimal-leading-zero); font-family: 'Libre Baskerville', Georgia, serif;
    font-style: italic; color: var(--g-accent, #710C04); flex: none; min-width: 22px; }
  .ms-toc a:hover { color: var(--g-accent, #710C04); }
  @media (max-width: 620px) { .ms-toc ol { columns: 1; } .ms-toc { padding: 20px 20px 16px; } .ms-bar__min { display: none; } }
  .ms-bar__back { font-size: 14px; font-weight: 600; color: var(--g-accent, #710C04); text-decoration: none; }
  .ms-bar__back:hover { text-decoration: underline; }
  .ms-bar__name { font-style: italic; color: var(--g-faint, #8f8a84); font-size: 14px; letter-spacing: .02em; margin-left: auto; }
  .ms-bar__theme { background: none; border: 1px solid var(--g-line, #e6e4e1); color: var(--g-muted, #6c6c6c);
    width: 32px; height: 32px; cursor: pointer; font-size: 14px; display: flex; align-items: center;
    justify-content: center; }
  .ms-bar__theme:hover { border-color: var(--g-accent, #710C04); color: var(--g-accent, #710C04); }

  .ms-sell { background: #121212; color: #fff; margin-top: 90px; padding: 78px 22px 72px;
    font-family: 'Inter', -apple-system, sans-serif; }
  .ms-sell__in { max-width: 660px; margin: 0 auto; }
  .ms-sell__bridge { font-family: 'Libre Baskerville', Georgia, serif; font-size: 20px; line-height: 1.62;
    color: #f0ece7; font-style: italic; margin: 0; }
  .ms-sell__rule { height: 1px; background: #2e2e2e; margin: 42px 0 38px; }
  .ms-sell__label { display: inline-block; border: 1px solid #c9a07a; color: #c9a07a; font-size: 10.5px;
    font-weight: 600; letter-spacing: .2em; text-transform: uppercase; padding: 6px 14px; margin-bottom: 22px; }
  .ms-sell__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(28px, 5vw, 40px);
    font-weight: 700; line-height: 1.24; margin: 0 0 16px; color: #fff; }
  .ms-sell__title i { font-style: italic; color: #c9a07a; font-weight: 400; }
  .ms-sell__lead { font-size: 17.5px; line-height: 1.7; color: #c4c4c4; margin: 0 0 40px; }

  .ms-sell__proof { display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
    border-top: 1px solid #2e2e2e; border-bottom: 1px solid #2e2e2e; padding: 26px 0; }
  .ms-sell__proof-item { flex: 1; min-width: 190px; }
  .ms-sell__num { display: block; font-family: 'Libre Baskerville', Georgia, serif; font-size: 30px;
    color: #6f6f6f; line-height: 1.2; }
  .ms-sell__proof-item--win .ms-sell__num { color: #c9a07a; }
  .ms-sell__cap { display: block; font-size: 13.5px; color: #9a9a9a; margin-top: 6px; line-height: 1.5; }
  .ms-sell__proof-vs { font-size: 11px; letter-spacing: .18em; text-transform: uppercase; color: #6f6f6f; }
  .ms-sell__proof-note { font-size: 15.5px; line-height: 1.7; color: #b5b5b5; margin: 22px 0 40px; }

  .ms-sell__list { list-style: none; margin: 0 0 38px; padding: 0; }
  .ms-sell__list li { padding: 15px 0; border-bottom: 1px solid #2a2a2a; font-size: 15.5px;
    line-height: 1.62; color: #cfcfcf; }
  .ms-sell__list li b { color: #fff; font-weight: 600; }
  .ms-sell__list li::before { content: "—"; color: #c9a07a; margin-right: 10px; }

  .ms-sell__author { font-size: 15.5px; line-height: 1.72; color: #b5b5b5; margin: 0 0 6px;
    padding-left: 18px; border-left: 2px solid #c9a07a; }
  .ms-sell__sign { display: block; font-family: 'Denistina', cursive; color: #c9a07a; font-size: 52px;
    line-height: 1; margin: 4px 0 30px 18px; }

  .ms-sell__cta { display: inline-block; background: #fff; color: #121212 !important; text-decoration: none;
    padding: 17px 36px; font-weight: 700; font-size: 16.5px; transition: opacity .18s; }
  .ms-sell__cta:hover { opacity: .86; }
  .ms-sell__note { font-size: 13.5px; color: #8a8a8a; margin: 16px 0 0; }

  .ms-foot { max-width: 660px; margin: 0 auto; padding: 44px 22px 64px; text-align: center;
    font-family: 'Inter', -apple-system, sans-serif; font-size: 14.5px; color: var(--g-muted, #777); }
  .ms-foot a { color: var(--g-accent, #710C04); }
  .ms-foot__back { display: inline-block; font-weight: 600; text-decoration: none; margin-bottom: 12px; }
  .ms-foot__back:hover { text-decoration: underline; }
  .ms-foot p { margin: 0; }
  @media (max-width: 560px) {
    .ms-sell { padding: 56px 20px 52px; }
    .ms-sell__bridge { font-size: 18px; }
    .ms-sell__proof-vs { display: none; }
    .ms-bar__name { display: none; }
  }
</style>

<script>
  function msTheme(){
    var d = document.documentElement.getAttribute('data-theme') === 'dark';
    document.documentElement.setAttribute('data-theme', d ? 'light' : 'dark');
    try { localStorage.setItem('ms-theme', d ? 'light' : 'dark'); } catch(e){}
    msIcon();
  }
  (function(){
    var bar = document.querySelector('.ms-progress i'); if (!bar) return;
    function upd(){ var h = document.documentElement; var max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? Math.min(100, h.scrollTop / max * 100) : 0) + '%'; }
    window.addEventListener('scroll', upd, {passive: true}); upd();
  })();
  function msIcon(){
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('.theme').forEach(function(b){ b.textContent = dark ? '☀' : '☾'; });
  }
  msIcon();
</script>
"""

def sell_block(g):
    return (SELL.replace("%%BRIDGE%%", html.escape(g["bridge"]))
                .replace("%%INTENSIV%%", INTENSIV)
                .replace("%%TG%%", TG))

# ---------------------------------------------------------------- обработка гайда

COLOR_MAP = [
    (r'#f{3}(?:f{3})?\b', 'var(--g-bg)'),
    (r'#(?:fafafa|f9f9f9|f8f8f8|f7f7f7|f5f5f5|f4f4f4|f7f5f2|faf9f8)\b', 'var(--g-surface)'),
    (r'#(?:1a1a1a|111111|111|000000|000|222222|222)\b', 'var(--g-fg)'),
    (r'#710c04\b', 'var(--g-accent)'),
    (r'#(?:e8e8e8|eeeeee|eee|f0f0f0|ececec|e6e4e1|dddddd|ddd|e0e0e0)\b', 'var(--g-line)'),
    (r'#(?:333333|333|444444|444|555555|555|666666|666)\b', 'var(--g-muted)'),
    (r'#(?:888888|888|999999|999|aaaaaa|aaa|b3b3b3)\b', 'var(--g-faint)'),
]

THEME_VARS = """<script>(function(){var t;try{t=localStorage.getItem('ms-theme')}catch(e){}
if(!t)t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
document.documentElement.setAttribute('data-theme',t)})();</script>
<style id="ms-theme-vars">
  :root { --g-bg:#ffffff; --g-surface:#f5f5f5; --g-fg:#1a1a1a; --g-accent:#710C04;
          --g-line:#e6e4e1; --g-muted:#555555; --g-faint:#8f8a84; }
  [data-theme="dark"] { --g-bg:#100f0e; --g-surface:#191715; --g-fg:#ece7e1; --g-accent:#d8ac83;
          --g-line:#2a2724; --g-muted:#a49d95; --g-faint:#8b847c; }
  html, body { background: var(--g-bg); color: var(--g-fg); }
  [data-theme="dark"] img[src*="logo-ms"] { filter: invert(1) brightness(1.6); }
  /* страховка от горизонтального скролла на телефоне */
  @media (max-width: 640px) {
    html, body { overflow-x: hidden; }
    [class*="__row"], [class*="-row"] { flex-wrap: wrap !important; }
    .slide, .slide__body, .slide__inner, [class*="__inner"] { min-width: 0 !important; }
    img, video, table, pre { max-width: 100% !important; }
    pre { overflow-x: auto; }
  }
</style>
"""

def _swap_colors(css: str) -> str:
    for pat, val in COLOR_MAP:
        css = re.sub(pat, val, css, flags=re.I)
    return css

def themeify(s: str) -> str:
    """Меняем цвета фирменной палитры на переменные — так работает тёмная тема."""
    s = re.sub(r'(<style[^>]*>)(.*?)(</style>)',
               lambda m: m.group(1) + _swap_colors(m.group(2)) + m.group(3), s, flags=re.S)
    s = re.sub(r'style="([^"]*)"', lambda m: 'style="' + _swap_colors(m.group(1)) + '"', s)
    return s

def reading_minutes(page_html: str) -> int:
    body = page_html.split('<section class="ms-sell">')[0]
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', body, flags=re.S)
    text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
    return max(1, round(len(re.findall(r'\w+', text)) / 180))

def add_toc(s: str) -> str:
    """Оглавление по h2 — чтобы структура гайда читалась с первого экрана."""
    heads = list(re.finditer(r'<h2([^>]*)>(.*?)</h2>', s, flags=re.S))
    if len(heads) < 4:
        return s
    items, out, pos = [], [], 0
    for i, m in enumerate(heads, 1):
        attrs, inner = m.group(1), m.group(2)
        title = html.unescape(re.sub(r'<[^>]+>', '', inner)).strip()
        title = re.sub(r'^\d{1,2}[.)]\s*', '', title)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else f"s-{i}"
        new_tag = m.group(0) if idm else f'<h2 id="{hid}"{attrs}>{inner}</h2>'
        items.append(f'<li><a href="#{hid}">{html.escape(title)}</a></li>')
        out.append(s[pos:m.start()]); out.append(new_tag); pos = m.end()
    out.append(s[pos:])
    s = "".join(out)
    toc = ('<div class="ms-toc" role="navigation" aria-label="Содержание"><span class="ms-toc__label">Содержание</span><ol>'
           + "".join(items) + '</ol></div>\n')
    first = re.search(r'<h2', s)
    return s[:first.start()] + toc + s[first.start():]

SLIDES_TO_ARTICLE = """<style id="ms-slides">
  /* презентация 60/40 под видеоурок → обычная читаемая статья */
  .slide { height: auto !important; min-height: 0 !important; width: 100% !important; display: block !important;
    padding: 56px 0 !important; border-bottom: 1px solid var(--g-line, #e6e4e1); }
  .slide:first-of-type { padding-top: 40px !important; }
  .slide__body { width: 100% !important; max-width: 780px; margin: 0 auto; padding: 0 24px !important; display: block !important; }
  .slide__inner { max-width: none !important; }
  .divider, .slide .nav { display: none !important; }
  .ms-toc { max-width: 732px; margin-left: auto; margin-right: auto; }
</style>
"""

def process_guide(src_html: str, g: dict) -> str:
    s = src_html
    if ('class="slide"' in s or "slide__body" in s) and "ms-slides" not in s:
        s = s.replace("</head>", SLIDES_TO_ARTICLE + "</head>", 1)
    s = s.replace("https://maiyamaiya19999-bit.github.io/maysoulme-assets/logo-ms.png", "../../logo-ms.png")
    s = re.sub(r'(<img[^>]+src=")(?:\./)?logo(?:-ms)?\.(png|svg)(")', r'\1../../logo-ms.png\3', s)
    s = re.sub(r'(<a[^>]*class="[^"]*nav__logo[^"]*"[^>]*href=")#(")', r'\1../../\2', s)
    s = s.replace('href="start.html"', 'href="https://maiyamaiya19999-bit.github.io/claude-montage-skill/start.html"')
    s = s.replace('href="index.html"', 'href="../claude-montazher/"')
    s = s.replace('href="team.html"', 'href="https://maiyamaiya19999-bit.github.io/claude-montage-skill/team.html"')
    s = s.replace("&family=DM+Sans:ital@1", "").replace("family=DM+Sans:ital@1&", "")
    if "ms-theme-vars" not in s:
        s = themeify(s)
        s = s.replace("</head>", THEME_VARS + "</head>", 1)
    if "og:title" not in s:
        og = (f'<meta property="og:type" content="article">\n'
              f'<meta property="og:title" content="{html.escape(strip_tags(g["title"]))}">\n'
              f'<meta property="og:description" content="{html.escape(g["desc"])}">\n'
              f'<meta property="og:url" content="{SITE}/guides/{g["slug"]}/">\n'
              f'<meta property="og:image" content="{SITE}/logo-ms.png">\n')
        s = s.replace("</head>", og + "</head>", 1)
    if "ms-toc" not in s:
        s = add_toc(s)
    g["minutes"] = reading_minutes(s)
    if "ms-bar" not in s:
        bar = BAR.replace("%%MIN%%", str(g["minutes"]))
        m = re.search(r'<body[^>]*>', s)
        s = (s[:m.end()] + "\n" + bar + s[m.end():]) if m else bar + s
    block = sell_block(g)
    s = s.replace("</body>", block + "</body>", 1) if "</body>" in s else s + block
    return s

def copy_assets(src: Path, dest_dir: Path, page: str):
    """Картинки и файлы для скачивания, лежащие рядом с исходником, едут вместе с гайдом."""
    import shutil
    for ref in set(re.findall(r'(?:src|href)="([^"#?:]+)"', page)):
        if ref.startswith(("../", "/")) or ref.endswith((".html", "/")):
            continue
        f = src.parent / ref
        if f.is_file():
            (dest_dir / ref).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest_dir / ref)

def resolve(src: str):
    root, rest = src.split("/", 1)
    p = SOURCE_ROOTS.get(root)
    return (p / rest) if p else None

# ---------------------------------------------------------------- главная

def build_index(data):
    short = {"reels": "Reels", "content": "Контент", "start": "ИИ с нуля", "claude": "Claude", "life": "Для жизни"}
    nav = "\n".join(f'      <a href="#{c["id"]}">{short.get(c["id"], strip_tags(c["title"]))}</a>'
                    for c in data["categories"])
    index = "\n".join(
        f'    <a href="#{c["id"]}"><i>{k:02d}</i>{strip_tags(c["title"])}</a>'
        for k, c in enumerate(data["categories"], 1))
    n = 0
    sections = []
    for k, c in enumerate(data["categories"], 1):
        cards = []
        cells = len(c["guides"]) + 1
        rem = cells % 3
        last_span = (4 - rem) if rem else 0
        for i, g in enumerate(c["guides"]):
            n += 1
            cls = " card--lead" if i == 0 else ""
            if last_span and i == len(c["guides"]) - 1:
                cls += f" card--w{last_span}"
            cards.append(f"""        <a class="card{cls}" href="guides/{g['slug']}/">
          <span class="card__top"><span class="card__tag">{html.escape(g['tag'])} · {g.get('minutes', 5)} мин</span><span class="card__n">{n:02d}</span></span>
          <span class="card__title">{g['title']}</span>
          <span class="card__desc">{html.escape(g['desc'])}</span>
          <span class="card__go">Открыть <i>&rarr;</i></span>
        </a>""")
        sections.append(f"""    <section class="cat" id="{c['id']}">
      <div class="cat__head">
        <span class="cat__num">{k:02d}</span>
        <div class="cat__text">
          <h2 class="cat__title">{c['title']}</h2>
          <p class="cat__lead">{html.escape(c['lead'])}</p>
        </div>
      </div>
      <div class="cards">
{chr(10).join(cards)}
      </div>
    </section>""")
    return (TEMPLATE.replace("%%NAV%%", nav)
                    .replace("%%INDEX%%", index)
                    .replace("%%SECTIONS%%", "\n\n".join(sections))
                    .replace("%%TG%%", TG)
                    .replace("%%INTENSIV%%", INTENSIV)
                    .replace("%%SITE%%", SITE))

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>maysoulme — гайды и промпты для блога с нейросетями</title>
<meta name="description" content="Гайды и промпты про блог с нейросетями: разговорные reels, тексты своим голосом, распаковка личности, свои ИИ-ассистенты. Бесплатно, без регистрации.">
<meta property="og:type" content="website">
<meta property="og:title" content="maysoulme — гайды и промпты для блога с нейросетями">
<meta property="og:description" content="Всё, чем Майя пользуется сама каждый день. Бесплатно, без регистрации.">
<meta property="og:url" content="%%SITE%%/">
<meta property="og:image" content="%%SITE%%/img/hero.jpg">
<script>(function(){var t;try{t=localStorage.getItem('ms-theme')}catch(e){}
if(!t)t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
document.documentElement.setAttribute('data-theme',t)})();</script>
<link rel="icon" href="logo-ms.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400;1,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  @font-face { font-family: 'Denistina'; src: url('denistina.ttf') format('truetype'); font-display: swap; }

  :root {
    --accent: #710C04; --bg: #ffffff; --fg: #1a1a1a; --muted: #5f5c58; --faint: #948e87;
    --line: #e4e0db; --cream: #f6f3ef; --card: #ffffff; --shadow: rgba(30,20,16,.10);
    --dark-bg: #1a1a1a; --gold: #c9a07a;
  }
  [data-theme="dark"] {
    --accent: #d8ac83; --bg: #100f0e; --fg: #ece7e1; --muted: #aaa39b; --faint: #7f7871;
    --line: #2a2724; --cream: #171614; --card: #141312; --shadow: rgba(0,0,0,.55); --dark-bg: #171614;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--fg);
    font-size: 17px; line-height: 1.7; -webkit-font-smoothing: antialiased; transition: background .25s, color .25s; }
  a { color: inherit; }
  img { max-width: 100%; }
  .wrap { max-width: 1080px; margin: 0 auto; padding: 0 32px; }
  .serif { font-family: 'Libre Baskerville', Georgia, serif; }
  .hand { font-family: 'Denistina', cursive; color: var(--accent); font-weight: 400; }

  /* ---------- шапка ---------- */
  .nav { position: sticky; top: 0; z-index: 100; background: var(--bg); border-bottom: 1px solid var(--line); }
  .nav__in { max-width: 1080px; margin: 0 auto; padding: 14px 32px; display: flex; align-items: center; gap: 16px; }
  .nav__logo img { height: 26px; display: block; }
  [data-theme="dark"] .nav__logo img { filter: invert(1) brightness(1.6); }
  .nav__name { font-style: italic; color: var(--faint); font-size: 14.5px; letter-spacing: .02em; margin-top: 1px; }
  .nav__links { margin-left: auto; display: flex; align-items: center; gap: 26px; font-size: 14px; white-space: nowrap; }
  .nav__links a { text-decoration: none; color: var(--muted); transition: color .15s; }
  .nav__links a:hover { color: var(--accent); }
  .nav__cta { background: var(--accent); color: var(--bg) !important; padding: 10px 20px; font-weight: 600; transition: opacity .18s; }
  .nav__cta:hover { opacity: .88; }
  .theme { background: none; border: 1px solid var(--line); color: var(--muted); width: 34px; height: 34px; cursor: pointer;
    font-size: 15px; line-height: 1; display: flex; align-items: center; justify-content: center; flex: none;
    transition: border-color .18s, color .18s; }
  .theme:hover { border-color: var(--accent); color: var(--accent); }
  @media (max-width: 900px) { .nav__links a:not(.nav__cta) { display: none; } }
  @media (max-width: 430px) { .nav__cta { padding: 9px 13px; font-size: 12.5px; } .nav__name { display: none; } }

  /* ---------- первый экран ---------- */
  .hero { display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: center; padding: 72px 0 64px; }
  h1 { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(24px, 3.4vw, 35px); font-weight: 400;
    line-height: 1.36; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 24px; }
  h1 b { font-weight: 700; }
  h1 .hand { display: block; text-transform: none; letter-spacing: 0; line-height: .95;
    font-size: clamp(48px, 7vw, 78px); margin-top: 10px; }
  .hero__lead { color: var(--muted); font-size: 18px; line-height: 1.74; max-width: 500px; }
  .hero__art { position: relative; margin: 0; padding: 0 0 20px 20px; }
  .hero__art::before { content: ""; position: absolute; left: 0; top: 20px; right: 20px; bottom: 0; background: var(--cream); }
  .hero__art img { position: relative; width: 100%; aspect-ratio: 4 / 3; object-fit: cover; display: block; }
  @media (max-width: 880px) {
    .hero { grid-template-columns: 1fr; gap: 34px; padding: 40px 0 40px; }
    .hero__art { order: -1; padding: 0 0 14px 14px; } .hero__art::before { top: 14px; right: 14px; }
  }

  /* ---------- оглавление ---------- */
  .index { display: flex; align-items: center; gap: 12px 24px; flex-wrap: wrap; padding: 18px 0; border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line); font-size: 13px; }
  .index::-webkit-scrollbar { display: none; }
  @media (max-width: 620px) { .index { flex-wrap: nowrap; white-space: nowrap; overflow-x: auto; scrollbar-width: none; gap: 22px; padding-right: 40px;
    -webkit-mask-image: linear-gradient(90deg, #000 84%, transparent); mask-image: linear-gradient(90deg, #000 84%, transparent); } }
  .index__label { font-size: 10.5px; font-weight: 600; letter-spacing: .22em; text-transform: uppercase; color: var(--faint); }
  .index a { text-decoration: none; color: var(--muted); transition: color .15s; }
  .index a:hover { color: var(--accent); }
  .index a i { font-family: 'Libre Baskerville', Georgia, serif; font-style: italic; color: var(--accent); margin-right: 7px; }

  /* ---------- маршрут ---------- */
  .route { margin-top: 64px; padding: 44px 44px 40px; background: var(--cream); }
  .route__head { max-width: 560px; margin-bottom: 30px; }
  .route__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: 22px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; line-height: 1.3; margin-bottom: 8px; }
  .route__title i { font-style: italic; color: var(--accent); }
  .route__lead { color: var(--muted); font-size: 15.5px; line-height: 1.65; }
  .route__steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; position: relative; }
  .step { position: relative; padding: 22px 34px 8px 0; text-decoration: none; border-top: 1px solid var(--line); }
  .step + .step { padding-left: 34px; }
  .step + .step::before { content: "→"; position: absolute; left: -9px; top: 22px; font-family: 'Libre Baskerville', Georgia, serif;
    font-size: 18px; color: var(--accent); background: var(--cream); padding: 0 4px; }
  .step__n { display: block; font-family: 'Libre Baskerville', Georgia, serif; font-style: italic; font-size: 30px;
    color: var(--accent); line-height: 1; margin-bottom: 12px; }
  .step__title { display: block; font-family: 'Libre Baskerville', Georgia, serif; font-size: 17.5px; font-weight: 700;
    line-height: 1.35; margin-bottom: 6px; transition: color .18s; }
  .step:hover .step__title { color: var(--accent); }
  .step__desc { display: block; font-size: 14px; line-height: 1.6; color: var(--muted); }
  @media (max-width: 760px) {
    .route { padding: 30px 24px 26px; margin-top: 40px; }
    .route__steps { grid-template-columns: 1fr; }
    .step, .step + .step { padding: 18px 0 14px; }
    .step + .step::before { content: "↓"; left: auto; right: 0; top: 18px; }
  }

  /* ---------- разделы ---------- */
  .cat { padding: 78px 0 6px; scroll-margin-top: 70px; }
  .cat__head { display: flex; align-items: flex-start; gap: 26px; padding-bottom: 26px; border-bottom: 1px solid var(--line);
    margin-bottom: 30px; }
  .cat__num { font-family: 'Libre Baskerville', Georgia, serif; font-style: italic; font-size: 46px; line-height: 1;
    color: var(--accent); flex: none; margin-top: -4px; }
  .cat__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: 22px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .09em; line-height: 1.3; }
  .cat__title i { font-style: italic; color: var(--accent); }
  .cat__lead { color: var(--faint); font-size: 15px; margin-top: 6px; }

  /* ---------- карточки ---------- */
  .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  @media (max-width: 900px) { .cards { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 620px) { .cards { grid-template-columns: 1fr; } }
  .card { display: flex; flex-direction: column; background: var(--card); border: 1px solid var(--line);
    padding: 26px 26px 22px; text-decoration: none; transition: border-color .2s, box-shadow .25s, transform .25s; }
  .card:hover { border-color: var(--accent); box-shadow: 0 16px 40px var(--shadow); transform: translateY(-4px); }
  .card__top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px; }
  .card__tag { font-size: 10px; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--accent); }
  .card__n { font-family: 'Libre Baskerville', Georgia, serif; font-style: italic; font-size: 14px; color: var(--faint); }
  .card__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: 16px; font-weight: 700; line-height: 1.5;
    margin-bottom: 12px; text-transform: uppercase; letter-spacing: .035em; }
  .card__title i { font-style: italic; }
  .card__desc { font-size: 14.5px; line-height: 1.66; color: var(--muted); flex: 1; }
  .card__go { margin-top: 22px; padding-top: 15px; border-top: 1px solid var(--line); font-size: 13.5px; font-weight: 600; color: var(--accent); }
  .card__go i { font-style: normal; display: inline-block; margin-left: 7px; transition: transform .22s; }
  .card:hover .card__go i { transform: translateX(5px); }
  .card--lead { grid-column: span 2; background: var(--cream); border-color: transparent; padding: 30px 30px 24px; }
  .card--lead .card__title { font-size: 19px; line-height: 1.42; }
  .card--lead .card__desc { font-size: 15.5px; max-width: 90%; }
  .card--w2 { grid-column: span 2; } .card--w3 { grid-column: span 3; }
  .card--w2 .card__desc, .card--w3 .card__desc { max-width: 640px; }
  @media (max-width: 900px) { .card--w3 { grid-column: span 2; } }
  @media (max-width: 620px) { .card--lead, .card--w2, .card--w3 { grid-column: span 1; } }

  /* ---------- цитата ---------- */
  .quote { margin: 86px 0 0; padding: 64px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); text-align: center; }
  .quote p { font-family: 'Libre Baskerville', Georgia, serif; font-size: 26px; line-height: 1.56; max-width: 680px; margin: 0 auto; }
  .quote p i { font-style: italic; color: var(--accent); }
  .quote .sign { font-family: 'Denistina', cursive; color: var(--accent); font-size: 44px; display: block; margin-top: 26px; line-height: 1; }

  /* ---------- интенсив ---------- */
  .intensiv { background: var(--dark-bg); color: #fff; margin-top: 86px; padding: 84px 0; scroll-margin-top: 60px; }
  [data-theme="dark"] .intensiv { border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
  .intensiv__in { max-width: 1080px; margin: 0 auto; padding: 0 32px; display: grid; grid-template-columns: 1.15fr .85fr;
    gap: 60px; align-items: start; }
  @media (max-width: 880px) { .intensiv__in { grid-template-columns: 1fr; gap: 36px; } }
  .intensiv__label { display: inline-block; border: 1px solid var(--gold); color: var(--gold); font-size: 10.5px; font-weight: 600;
    letter-spacing: .2em; text-transform: uppercase; padding: 6px 14px; margin-bottom: 26px; }
  .intensiv h2 { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(30px, 4.6vw, 44px); font-weight: 400;
    line-height: 1.22; margin-bottom: 20px; color: #fff; }
  .intensiv h2 i { font-style: italic; color: var(--gold); }
  .intensiv p { color: #c6c2bd; font-size: 17px; line-height: 1.72; }
  .intensiv__list { list-style: none; margin: 4px 0 0; }
  .intensiv__list li { padding: 14px 0; border-bottom: 1px solid #332f2b; font-size: 15.5px; color: #e4e0db; }
  .intensiv__list li::before { content: "—"; color: var(--gold); margin-right: 10px; }
  .intensiv__cta { display: inline-block; background: #fff; color: #1a1a1a !important; text-decoration: none; padding: 16px 34px;
    font-weight: 700; font-size: 16px; margin-top: 32px; transition: opacity .18s; }
  .intensiv__cta:hover { opacity: .87; }
  .intensiv__note { font-size: 13.5px; color: #8f8a84; margin-top: 14px; }

  /* ---------- канал ---------- */
  .tg { background: var(--cream); padding: 78px 0; }
  .tg__in { max-width: 1080px; margin: 0 auto; padding: 0 32px; display: flex; align-items: center; justify-content: space-between;
    gap: 30px; flex-wrap: wrap; }
  .tg h2 { font-family: 'Libre Baskerville', Georgia, serif; font-size: 20px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; margin-bottom: 10px; }
  .tg h2 i { font-style: italic; color: var(--accent); }
  .tg p { color: var(--muted); font-size: 16px; max-width: 500px; }
  .tg a { display: inline-block; background: var(--accent); color: var(--bg) !important; padding: 15px 32px; font-weight: 600;
    font-size: 15.5px; text-decoration: none; transition: opacity .18s; white-space: nowrap; }
  .tg a:hover { opacity: .88; }

  /* ---------- подвал ---------- */
  .foot { padding: 32px 0 58px; font-size: 13.5px; color: var(--faint); display: flex; gap: 20px; flex-wrap: wrap; justify-content: space-between; }
  .foot a { color: var(--faint); }
</style>
</head>
<body>

<nav class="nav">
  <div class="nav__in">
    <a class="nav__logo" href="./"><img src="logo-ms.png" alt="MS"></a>
    <span class="nav__name">maysoulme</span>
    <div class="nav__links">
%%NAV%%
      <a class="nav__cta" href="#intensiv">Вступить на интенсив</a>
      <button class="theme" type="button" onclick="msTheme()" aria-label="Сменить тему">☾</button>
    </div>
  </div>
</nav>

<div class="wrap">
  <header class="hero">
    <div class="hero__text">
      <h1>Гайды и промпты для <b>блога</b><span class="hand">с нейросетями</span></h1>
      <p class="hero__lead">Здесь всё, чем пользуюсь сама каждый день: сценарии роликов, тексты своим голосом, распаковка, свои ИИ-ассистенты. Забирайте и пробуйте.</p>
    </div>
    <figure class="hero__art">
      <img src="img/hero.jpg" alt="Ноутбук, кофе и работа над блогом" loading="eager">
    </figure>
  </header>

  <nav class="index" aria-label="Разделы">
    <span class="index__label">Разделы</span>
%%INDEX%%
  </nav>

  <section class="route">
    <div class="route__head">
      <h2 class="route__title">Если вы здесь <i>впервые</i></h2>
      <p class="route__lead">Не нужно читать всё подряд. Три шага по порядку — и у вас уже есть доступ, свой голос и первый ролик.</p>
    </div>
    <div class="route__steps">
      <a class="step" href="guides/claude-i-chatgpt-v-rossii/">
        <span class="step__n">01</span>
        <span class="step__title">Поставить Claude</span>
        <span class="step__desc">Полчаса — и доступ есть, без бана и нервов</span>
      </a>
      <a class="step" href="guides/raspakovka-lichnosti/">
        <span class="step__n">02</span>
        <span class="step__title">Распаковать себя</span>
        <span class="step__desc">Чтобы нейросеть говорила вашими словами, а не своими</span>
      </a>
      <a class="step" href="guides/formula-razgovornyh-rolikov/">
        <span class="step__n">03</span>
        <span class="step__title">Снять первый ролик</span>
        <span class="step__desc">По формуле, которая держит человека в кадре до конца</span>
      </a>
    </div>
  </section>

%%SECTIONS%%

  <section class="quote">
    <p>Люди остаются не ради пользы. Они остаются там, где <i>узнали себя</i>.</p>
    <span class="sign">Майя</span>
  </section>
</div>

<section class="intensiv" id="intensiv">
  <div class="intensiv__in">
    <div>
      <span class="intensiv__label">Платный интенсив</span>
      <h2>ИИ-стратегия <i>на миллион</i></h2>
      <p>Гайды выше — это отдельные детали. На интенсиве мы собираем из них систему: стратегия, контент, свои ИИ-ассистенты и парсер идей, который приносит темы, пока вы завтракаете.</p>
      <a class="intensiv__cta" href="%%INTENSIV%%">Смотреть программу и цены →</a>
      <p class="intensiv__note">Вечный доступ · чат поддержки · есть формат VIP с личным сопровождением</p>
    </div>
    <ul class="intensiv__list">
      <li>Стратегия блога и позиционирование</li>
      <li>Текстовые и разговорные reels</li>
      <li>ИИ-агент с памятью вашего канала</li>
      <li>Парсер залетающих идей ниши</li>
      <li>Готовые ассистенты и шаблоны</li>
      <li>Собрано без единого программиста</li>
    </ul>
  </div>
</section>

<section class="tg">
  <div class="tg__in">
    <div>
      <h2>Новое — <i>сначала</i> в канале</h2>
      <p>Там я показываю всё то же самое по горячим следам: что затестила, что сработало, а что оказалось полной ерундой.</p>
    </div>
    <a href="%%TG%%">Читать @maysoulme</a>
  </div>
</section>

<div class="wrap">
  <footer class="foot">
    <span>© maysoulme · Майя Шебаршина</span>
    <span><a href="%%TG%%">Telegram</a> · <a href="politika.html">Политика конфиденциальности</a></span>
  </footer>
</div>

<script>
  function msTheme(){
    var d = document.documentElement.getAttribute('data-theme') === 'dark';
    document.documentElement.setAttribute('data-theme', d ? 'light' : 'dark');
    try { localStorage.setItem('ms-theme', d ? 'light' : 'dark'); } catch(e){}
    msIcon();
  }
  (function(){
    var bar = document.querySelector('.ms-progress i'); if (!bar) return;
    function upd(){ var h = document.documentElement; var max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? Math.min(100, h.scrollTop / max * 100) : 0) + '%'; }
    window.addEventListener('scroll', upd, {passive: true}); upd();
  })();
  function msIcon(){
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('.theme').forEach(function(b){ b.textContent = dark ? '☀' : '☾'; });
  }
  msIcon();
</script>

</body>
</html>
"""

# ---------------------------------------------------------------- автодобавление

DEFAULT_BRIDGE = ("Этот гайд — одна деталь. На интенсиве мы собираем из таких деталей систему: "
                  "стратегию, контент и своих ИИ-ассистентов под ваш блог.")

def discover(data):
    """Гайд, положенный в guides/<slug>/index.html с meta-тегами ms-section (и по желанию
    ms-title, ms-desc, ms-tag, ms-bridge), попадает на главную без правки guides.json."""
    known = {g["slug"] for c in data["categories"] for g in c["guides"]}
    cats = {c["id"]: c for c in data["categories"]}
    added = []
    for d in sorted((ROOT / "guides").iterdir()):
        f = d / "index.html"
        if d.name in known or not f.exists():
            continue
        page = f.read_text(encoding="utf-8", errors="ignore")
        meta = dict(re.findall(r'<meta name="ms-(\w+)" content="([^"]*)"', page))
        if meta.get("section") not in cats:
            continue
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, flags=re.S)
        title = meta.get("title") or (strip_tags(h1.group(1)).strip() if h1 else d.name)
        dm = re.search(r'<meta name="description" content="([^"]*)"', page)
        desc = meta.get("desc") or (dm.group(1) if dm else "")
        g = dict(slug=d.name, title=title, desc=html.unescape(desc), tag=meta.get("tag", "Гайд"),
                 src=None, bridge=meta.get("bridge", DEFAULT_BRIDGE))
        cats[meta["section"]]["guides"].append(g)
        added.append(g)
    return added

# ---------------------------------------------------------------- main

def main():
    data = json.loads((ROOT / "guides.json").read_text(encoding="utf-8"))
    copied = skipped = 0
    for c in data["categories"]:
        for g in c["guides"]:
            dest_dir = ROOT / "guides" / g["slug"]
            dest = dest_dir / "index.html"
            src = resolve(g["src"])
            if src and src.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)
                page = process_guide(src.read_text(encoding="utf-8", errors="ignore"), g)
                dest.write_text(page, encoding="utf-8")
                copy_assets(src, dest_dir, page)
                copied += 1
            elif dest.exists():
                g["minutes"] = reading_minutes(dest.read_text(encoding="utf-8", errors="ignore"))
                skipped += 1
                print(f"  ~ источник недоступен, оставлен собранный: {g['slug']}")
            else:
                print(f"  ! НЕТ НИ ИСТОЧНИКА, НИ СБОРКИ: {g['slug']} ({g['src']})")
    auto = discover(data)
    for g in auto:
        f = ROOT / "guides" / g["slug"] / "index.html"
        page = process_guide(f.read_text(encoding="utf-8", errors="ignore"), g)
        f.write_text(page, encoding="utf-8")
        print(f"  + добавлен по meta-тегам: {g['slug']} → {g['title']}")
    (ROOT / "index.html").write_text(build_index(data), encoding="utf-8")
    print(f"Готово: {copied} гайдов пересобрано, {skipped} оставлено, {len(auto)} добавлено автоматически, главная обновлена.")

if __name__ == "__main__":
    main()
