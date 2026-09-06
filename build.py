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
}

SITE = "https://maysoulme.ru"
TG = "https://t.me/maysoulme"
INTENSIV = "https://mayasoul.ru"

# ---------------------------------------------------------------- продающий блок в гайде

SELL = """
<section class="ms-sell">
  <div class="ms-sell__in">
    <p class="ms-sell__bridge">%%BRIDGE%%</p>

    <div class="ms-sell__rule"></div>

    <span class="ms-sell__label">Интенсив</span>
    <h2 class="ms-sell__title">ИИ-стратегия <em>на миллион</em></h2>
    <p class="ms-sell__lead">Гайды дают детали. Интенсив собирает из них систему: блог, который растёт не от удачного ролика, а от того, что за ним стоит.</p>

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
    <p class="ms-sell__proof-note">Разница не в удаче и не в количестве роликов. Разница в стратегии — в том, кому ты говоришь, что именно и куда ведёшь человека дальше.</p>

    <ul class="ms-sell__list">
      <li><b>Стратегия и позиционирование</b> — за что тебе платят и чем ты отличаешься от сотни таких же экспертов</li>
      <li><b>Текстовые и разговорные ролики</b> — два формата, которые набирают холодную аудиторию и превращают её в свою</li>
      <li><b>ИИ-агент с памятью канала</b> — помнит все твои посты и предлагает продолжение уже начатых тем, чтобы блог звучал как одна история</li>
      <li><b>Парсер идей</b> — собирает залетающие ролики твоей ниши, пока ты завтракаешь, и выдаёт готовые темы</li>
      <li><b>Готовые ассистенты и шаблоны</b> — сценарист, редактор, распаковка, прогревы: забираешь и пользуешься</li>
    </ul>

    <p class="ms-sell__author">Я собрала всё это в Claude Code без единого программиста — объясняя задачи обычными словами. За последнее время это дало мне +10 000 в Telegram и +22 000 в Instagram на узком экспертном контенте. На интенсиве я показываю ровно то, что делаю сама.</p>

    <a class="ms-sell__cta" href="%%INTENSIV%%">Смотреть программу интенсива →</a>
    <p class="ms-sell__note">Вечный доступ · чат поддержки со мной · формат VIP с личным сопровождением</p>
  </div>
</section>

<footer class="ms-foot">
  <a class="ms-foot__back" href="../../">← Все гайды maysoulme</a>
  <p>Бесплатная библиотека <a href="../../">maysoulme</a> · новые гайды сначала в <a href="%%TG%%">телеграм-канале</a></p>
</footer>

<style>
  .ms-sell { background: #121212; color: #fff; margin-top: 90px; padding: 84px 22px 78px;
    font-family: 'Inter', -apple-system, sans-serif; }
  .ms-sell__in { max-width: 660px; margin: 0 auto; }
  .ms-sell__bridge { font-family: 'Libre Baskerville', Georgia, serif; font-size: 20px; line-height: 1.62;
    color: #f0ece7; font-style: italic; margin: 0; }
  .ms-sell__rule { height: 1px; background: #2e2e2e; margin: 44px 0 40px; }
  .ms-sell__label { display: inline-block; border: 1px solid #c9a07a; color: #c9a07a; font-size: 10.5px;
    font-weight: 600; letter-spacing: .2em; text-transform: uppercase; padding: 6px 14px; margin-bottom: 22px; }
  .ms-sell__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(28px, 5vw, 40px);
    font-weight: 700; line-height: 1.24; margin: 0 0 16px; color: #fff; }
  .ms-sell__title em { font-style: italic; color: #c9a07a; }
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

  .ms-sell__author { font-size: 15.5px; line-height: 1.72; color: #b5b5b5; margin: 0 0 36px;
    padding-left: 18px; border-left: 2px solid #c9a07a; }

  .ms-sell__cta { display: inline-block; background: #fff; color: #121212 !important; text-decoration: none;
    padding: 17px 36px; font-weight: 700; font-size: 16.5px; transition: opacity .18s; }
  .ms-sell__cta:hover { opacity: .86; }
  .ms-sell__note { font-size: 13.5px; color: #8a8a8a; margin: 16px 0 0; }

  .ms-foot { max-width: 660px; margin: 0 auto; padding: 44px 22px 64px; text-align: center;
    font-family: 'Inter', -apple-system, sans-serif; font-size: 14.5px; color: #777; }
  .ms-foot a { color: #710C04; }
  .ms-foot__back { display: inline-block; font-weight: 600; text-decoration: none; margin-bottom: 12px; }
  .ms-foot__back:hover { text-decoration: underline; }
  .ms-foot p { margin: 0; }
  @media (max-width: 560px) {
    .ms-sell { padding: 60px 20px 56px; }
    .ms-sell__bridge { font-size: 18px; }
    .ms-sell__proof-vs { display: none; }
  }
</style>
"""

def sell_block(g):
    return (SELL.replace("%%BRIDGE%%", html.escape(g["bridge"]))
                .replace("%%INTENSIV%%", INTENSIV)
                .replace("%%TG%%", TG))

# ---------------------------------------------------------------- обработка гайда

def process_guide(src_html: str, g: dict) -> str:
    s = src_html
    s = s.replace("https://maiyamaiya19999-bit.github.io/maysoulme-assets/logo-ms.png", "../../logo-ms.png")
    s = re.sub(r'(<img[^>]+src=")(?:\./)?logo-ms\.(png|svg)(")', r'\1../../logo-ms.png\3', s)
    s = re.sub(r'(<a[^>]*class="[^"]*nav__logo[^"]*"[^>]*href=")#(")', r'\1../../\2', s)
    if "og:title" not in s:
        og = (f'<meta property="og:type" content="article">\n'
              f'<meta property="og:title" content="{html.escape(g["title"])}">\n'
              f'<meta property="og:description" content="{html.escape(g["desc"])}">\n'
              f'<meta property="og:url" content="{SITE}/guides/{g["slug"]}/">\n'
              f'<meta property="og:image" content="{SITE}/logo-ms.png">\n')
        s = s.replace("</head>", og + "</head>", 1)
    block = sell_block(g)
    s = s.replace("</body>", block + "</body>", 1) if "</body>" in s else s + block
    return s

def resolve(src: str):
    root, rest = src.split("/", 1)
    p = SOURCE_ROOTS.get(root)
    return (p / rest) if p else None

# ---------------------------------------------------------------- главная

def build_index(data):
    total = sum(len(c["guides"]) for c in data["categories"])
    nav = "\n".join(f'      <a href="#{c["id"]}">{html.escape(c["title"])}</a>'
                    for c in data["categories"])
    n = 0
    sections = []
    for c in data["categories"]:
        rows = []
        for g in c["guides"]:
            n += 1
            rows.append(f"""        <a class="row" href="guides/{g['slug']}/">
          <span class="row__n">{n:02d}</span>
          <span class="row__body">
            <span class="row__tag">{html.escape(g['tag'])}</span>
            <span class="row__title">{html.escape(g['title'])}</span>
            <span class="row__desc">{html.escape(g['desc'])}</span>
          </span>
          <span class="row__arrow">→</span>
        </a>""")
        sections.append(f"""    <section class="cat" id="{c['id']}">
      <div class="cat__head">
        <h2 class="cat__title">{html.escape(c['title'])}</h2>
        <p class="cat__lead">{html.escape(c['lead'])}</p>
      </div>
      <div class="rows">
{chr(10).join(rows)}
      </div>
    </section>""")
    return (TEMPLATE.replace("%%TOTAL%%", str(total))
                    .replace("%%NAV%%", nav)
                    .replace("%%SECTIONS%%", "\n\n".join(sections))
                    .replace("%%TG%%", TG)
                    .replace("%%INTENSIV%%", INTENSIV)
                    .replace("%%SITE%%", SITE))

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>maysoulme — библиотека гайдов и промптов</title>
<meta name="description" content="Библиотека maysoulme: %%TOTAL%% гайдов и промптов про блог с нейросетями — разговорные reels, тексты своим голосом, распаковка личности, ИИ-ассистенты. Бесплатно.">
<meta property="og:type" content="website">
<meta property="og:title" content="Библиотека maysoulme">
<meta property="og:description" content="%%TOTAL%% гайдов и промптов про блог с нейросетями. Бесплатно, без регистрации.">
<meta property="og:url" content="%%SITE%%/">
<meta property="og:image" content="%%SITE%%/logo-ms.png">
<link rel="icon" href="logo-ms.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700&family=DM+Sans:ital@1&display=swap" rel="stylesheet">
<style>
  :root { --accent: #710C04; --gold: #c9a07a; --ink: #1a1a1a; --line: #e6e4e1; --mute: #8a8a8a; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { font-family: 'Inter', -apple-system, sans-serif; background: #fff; color: var(--ink);
    font-size: 17px; line-height: 1.7; -webkit-font-smoothing: antialiased; }
  a { color: inherit; }
  .wrap { max-width: 940px; margin: 0 auto; padding: 0 30px; }

  /* навбар */
  .nav { position: sticky; top: 0; z-index: 100; background: rgba(255,255,255,.94);
    backdrop-filter: saturate(160%) blur(10px); border-bottom: 1px solid var(--line); }
  .nav__in { max-width: 940px; margin: 0 auto; padding: 15px 30px; display: flex; align-items: center; gap: 12px; }
  .nav__logo img { height: 26px; display: block; }
  .nav__name { font-family: 'DM Sans', sans-serif; font-style: italic; color: var(--mute); font-size: 14.5px; }
  .nav__links { margin-left: auto; display: flex; align-items: center; gap: 26px; font-size: 14px; }
  .nav__links a { text-decoration: none; color: #5a5a5a; transition: color .15s; }
  .nav__links a:hover { color: var(--accent); }
  .nav__cta { border: 1px solid var(--accent); color: var(--accent) !important; padding: 8px 17px;
    font-weight: 600; letter-spacing: .02em; transition: background .18s, color .18s; }
  .nav__cta:hover { background: var(--accent); color: #fff !important; }
  @media (max-width: 780px) { .nav__links a:not(.nav__cta) { display: none; } }

  /* герой */
  .hero { padding: 112px 0 88px; max-width: 700px; }
  .hero__label { font-size: 10.5px; font-weight: 600; letter-spacing: .24em; text-transform: uppercase;
    color: var(--accent); display: block; margin-bottom: 30px; }
  h1 { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(36px, 6.2vw, 58px);
    font-weight: 400; line-height: 1.18; letter-spacing: -.01em; margin-bottom: 26px; }
  h1 em { font-style: italic; color: var(--accent); }
  .hero__lead { color: #4a4a4a; font-size: 19px; line-height: 1.72; max-width: 580px; }
  .hero__meta { margin-top: 40px; padding-top: 22px; border-top: 1px solid var(--line);
    display: flex; gap: 40px; flex-wrap: wrap; color: var(--mute); font-size: 13.5px;
    letter-spacing: .04em; }

  /* разделы */
  .cat { padding: 18px 0 62px; scroll-margin-top: 72px; }
  .cat__head { margin-bottom: 8px; }
  .cat__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: 27px; font-weight: 400;
    letter-spacing: -.005em; }
  .cat__lead { color: var(--mute); font-size: 15.5px; margin-top: 8px; }

  /* строки-гайды */
  .rows { margin-top: 26px; border-top: 1px solid var(--line); }
  .row { display: flex; align-items: flex-start; gap: 26px; padding: 26px 14px 26px 0;
    border-bottom: 1px solid var(--line); text-decoration: none; transition: padding .22s, background .22s; }
  .row:hover { background: #faf9f8; padding-left: 14px; padding-right: 0; }
  .row__n { font-family: 'Libre Baskerville', Georgia, serif; font-style: italic; font-size: 15px;
    color: var(--accent); padding-top: 3px; min-width: 26px; opacity: .8; }
  .row__body { flex: 1; }
  .row__tag { display: block; font-size: 10px; font-weight: 600; letter-spacing: .2em;
    text-transform: uppercase; color: var(--mute); margin-bottom: 8px; }
  .row__title { display: block; font-family: 'Libre Baskerville', Georgia, serif; font-size: 20px;
    line-height: 1.36; margin-bottom: 8px; transition: color .18s; }
  .row:hover .row__title { color: var(--accent); }
  .row__desc { display: block; font-size: 15.5px; line-height: 1.66; color: #6a6a6a; max-width: 620px; }
  .row__arrow { color: var(--line); font-size: 19px; padding-top: 24px; transition: color .18s, transform .22s; }
  .row:hover .row__arrow { color: var(--accent); transform: translateX(4px); }
  @media (max-width: 560px) {
    .row { gap: 16px; padding: 22px 0; }
    .row__arrow { display: none; }
    .row__title { font-size: 18px; }
  }

  /* интенсив */
  .intensiv { background: #121212; color: #fff; margin-top: 40px; padding: 104px 0 96px; scroll-margin-top: 60px; }
  .intensiv__in { max-width: 940px; margin: 0 auto; padding: 0 30px; }
  .intensiv__label { display: inline-block; border: 1px solid var(--gold); color: var(--gold); font-size: 10.5px;
    font-weight: 600; letter-spacing: .2em; text-transform: uppercase; padding: 6px 14px; margin-bottom: 26px; }
  .intensiv h2 { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(32px, 5.4vw, 50px);
    font-weight: 400; line-height: 1.2; margin-bottom: 22px; }
  .intensiv h2 em { font-style: italic; color: var(--gold); }
  .intensiv__lead { color: #bdbdbd; font-size: 18px; line-height: 1.72; max-width: 600px; }
  .intensiv__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 56px; margin-top: 56px;
    border-top: 1px solid #2a2a2a; }
  @media (max-width: 820px) { .intensiv__grid { grid-template-columns: 1fr; gap: 0; } }
  .intensiv__item { padding: 22px 0; border-bottom: 1px solid #2a2a2a; }
  .intensiv__item b { display: block; font-size: 15.5px; font-weight: 600; margin-bottom: 5px; }
  .intensiv__item span { font-size: 14.5px; color: #9c9c9c; line-height: 1.6; }
  .intensiv__proof { display: flex; gap: 46px; flex-wrap: wrap; margin: 52px 0 44px; }
  .intensiv__stat b { display: block; font-family: 'Libre Baskerville', Georgia, serif; font-size: 34px;
    font-weight: 400; color: var(--gold); line-height: 1.2; }
  .intensiv__stat span { font-size: 13.5px; color: #9c9c9c; letter-spacing: .03em; }
  .intensiv__cta { display: inline-block; background: #fff; color: #121212 !important; text-decoration: none;
    padding: 17px 38px; font-weight: 700; font-size: 16.5px; transition: opacity .18s; }
  .intensiv__cta:hover { opacity: .86; }
  .intensiv__note { font-size: 13.5px; color: #7d7d7d; margin-top: 16px; }

  /* телеграм */
  .tg { padding: 90px 0; border-bottom: 1px solid var(--line); }
  .tg__in { max-width: 940px; margin: 0 auto; padding: 0 30px; display: flex; align-items: center;
    justify-content: space-between; gap: 32px; flex-wrap: wrap; }
  .tg h2 { font-family: 'Libre Baskerville', Georgia, serif; font-size: 27px; font-weight: 400; margin-bottom: 8px; }
  .tg p { color: var(--mute); font-size: 16px; max-width: 460px; }
  .tg a { display: inline-block; border: 1px solid var(--ink); padding: 15px 32px; font-weight: 600;
    font-size: 15.5px; text-decoration: none; transition: background .18s, color .18s; white-space: nowrap; }
  .tg a:hover { background: var(--ink); color: #fff; }

  /* подвал */
  .foot { padding: 34px 0 60px; font-size: 13.5px; color: var(--mute); display: flex; gap: 20px;
    flex-wrap: wrap; justify-content: space-between; }
  .foot a { color: var(--mute); }
</style>
</head>
<body>

<nav class="nav">
  <div class="nav__in">
    <a class="nav__logo" href="./"><img src="logo-ms.png" alt="MS"></a>
    <span class="nav__name">maysoulme</span>
    <div class="nav__links">
%%NAV%%
      <a class="nav__cta" href="#intensiv">Интенсив</a>
    </div>
  </div>
</nav>

<div class="wrap">
  <header class="hero">
    <span class="hero__label">Библиотека maysoulme</span>
    <h1>Гайды и промпты для блога <em>с нейросетями</em></h1>
    <p class="hero__lead">Собрано то, чем пользуюсь сама каждый день: разговорные reels, тексты своим голосом, распаковка личности, ИИ-ассистенты. Забирай и применяй.</p>
    <div class="hero__meta">
      <span>%%TOTAL%% материалов</span>
      <span>Бесплатно, без регистрации</span>
      <span>Библиотека пополняется</span>
    </div>
  </header>

%%SECTIONS%%
</div>

<section class="intensiv" id="intensiv">
  <div class="intensiv__in">
    <span class="intensiv__label">Платный интенсив</span>
    <h2>ИИ-стратегия <em>на миллион</em></h2>
    <p class="intensiv__lead">Гайды выше — это отдельные детали. На интенсиве из них собирается система: блог растёт не от удачного ролика, а от того, что стоит за ним.</p>

    <div class="intensiv__proof">
      <div class="intensiv__stat"><b>+10 000</b><span>в Telegram</span></div>
      <div class="intensiv__stat"><b>+22 000</b><span>в Instagram</span></div>
      <div class="intensiv__stat"><b>19 000</b><span>просмотров → 240 подписчиков и 30 000 ₽</span></div>
    </div>

    <div class="intensiv__grid">
      <div class="intensiv__item"><b>Стратегия и позиционирование</b><span>За что тебе платят и чем ты отличаешься от сотни похожих экспертов</span></div>
      <div class="intensiv__item"><b>Текстовые и разговорные ролики</b><span>Два формата: один набирает холодную аудиторию, другой превращает её в свою</span></div>
      <div class="intensiv__item"><b>ИИ-агент с памятью канала</b><span>Помнит все твои посты и предлагает продолжение начатых тем</span></div>
      <div class="intensiv__item"><b>Парсер идей</b><span>Собирает залетающие ролики ниши, пока ты завтракаешь</span></div>
      <div class="intensiv__item"><b>Готовые ассистенты и шаблоны</b><span>Сценарист, редактор, распаковка, прогревы — забираешь и пользуешься</span></div>
      <div class="intensiv__item"><b>Без единого программиста</b><span>Всё собрано в Claude Code — задачи объясняются обычными словами</span></div>
    </div>

    <p style="margin-top:48px"><a class="intensiv__cta" href="%%INTENSIV%%">Смотреть программу и цены →</a></p>
    <p class="intensiv__note">Вечный доступ · чат поддержки · формат VIP с личным сопровождением</p>
  </div>
</section>

<section class="tg">
  <div class="tg__in">
    <div>
      <h2>Новые гайды — сначала в канале</h2>
      <p>Пишу про блогинг и нейросети без магии и мотивации: что работает, что нет и почему.</p>
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

</body>
</html>
"""

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
                dest.write_text(process_guide(src.read_text(encoding="utf-8", errors="ignore"), g),
                                encoding="utf-8")
                copied += 1
            elif dest.exists():
                skipped += 1
                print(f"  ~ источник недоступен, оставлен собранный: {g['slug']}")
            else:
                print(f"  ! НЕТ НИ ИСТОЧНИКА, НИ СБОРКИ: {g['slug']} ({g['src']})")
    (ROOT / "index.html").write_text(build_index(data), encoding="utf-8")
    print(f"Готово: {copied} гайдов пересобрано, {skipped} оставлено, главная обновлена.")

if __name__ == "__main__":
    main()
