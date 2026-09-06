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
    chips = "\n".join(
        f'    <a href="#{c["id"]}">{html.escape(c["title"])} <b style="font-weight:600;color:#b3aca3">{len(c["guides"])}</b></a>'
        for c in data["categories"])
    n = 0
    sections = []
    for c in data["categories"]:
        cards = []
        cells = len(c["guides"]) + 1          # первая карточка занимает две клетки
        rem = cells % 3
        last_span = (4 - rem) if rem else 0   # добираем последнюю до ровного ряда
        for i, g in enumerate(c["guides"]):
            n += 1
            lead = " card--lead" if i == 0 else ""
            if last_span and i == len(c["guides"]) - 1:
                lead += f" card--w{last_span}"
            cards.append(f"""        <a class="card{lead}" href="guides/{g['slug']}/">
          <span class="card__n">{n:02d}</span>
          <span class="card__tag">{html.escape(g['tag'])}</span>
          <span class="card__title">{html.escape(g['title'])}</span>
          <span class="card__desc">{html.escape(g['desc'])}</span>
          <span class="card__go">Открыть <i>&rarr;</i></span>
        </a>""")
        word = "материал" if len(c["guides"]) == 1 else ("материала" if len(c["guides"]) < 5 else "материалов")
        sections.append(f"""    <section class="cat" id="{c['id']}">
      <div class="cat__head">
        <h2 class="cat__title">{html.escape(c['title'])}</h2>
        <p class="cat__lead">{html.escape(c['lead'])}</p>
        <span class="cat__count">{len(c['guides'])} {word}</span>
      </div>
      <div class="cards">
{chr(10).join(cards)}
      </div>
    </section>""")
    return (TEMPLATE.replace("%%TOTAL%%", str(total))
                    .replace("%%NAV%%", nav)
                    .replace("%%CHIPS%%", chips)
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
  :root { --accent: #710C04; --gold: #c9a07a; --ink: #1a1a1a; --line: #e6e4e1;
          --mute: #8a8a8a; --cream: #f7f5f2; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { font-family: 'Inter', -apple-system, sans-serif; background: #fff; color: var(--ink);
    font-size: 17px; line-height: 1.7; -webkit-font-smoothing: antialiased; }
  a { color: inherit; }
  .wrap { max-width: 1080px; margin: 0 auto; padding: 0 32px; }

  /* навбар */
  .nav { position: sticky; top: 0; z-index: 100; background: rgba(255,255,255,.93);
    backdrop-filter: saturate(160%) blur(12px); border-bottom: 1px solid var(--line); }
  .nav__in { max-width: 1080px; margin: 0 auto; padding: 14px 32px; display: flex; align-items: center; gap: 12px; }
  .nav__logo img { height: 26px; display: block; }
  .nav__name { font-family: 'DM Sans', sans-serif; font-style: italic; color: var(--mute); font-size: 14.5px; }
  .nav__links { margin-left: auto; display: flex; align-items: center; gap: 24px; font-size: 14px; }
  .nav__links a { text-decoration: none; color: #5a5a5a; transition: color .15s; }
  .nav__links a:hover { color: var(--accent); }
  .nav__cta { background: var(--accent); color: #fff !important; padding: 10px 20px; font-weight: 600;
    letter-spacing: .01em; transition: opacity .18s; }
  .nav__cta:hover { opacity: .88; }
  @media (max-width: 900px) { .nav__links a:not(.nav__cta) { display: none; } }
  @media (max-width: 420px) { .nav__cta { padding: 9px 14px; font-size: 13px; } }

  /* герой */
  .hero { display: grid; grid-template-columns: 1.35fr .65fr; gap: 56px; align-items: center;
    padding: 84px 0 54px; }
  .hero__label { font-size: 10.5px; font-weight: 600; letter-spacing: .24em; text-transform: uppercase;
    color: var(--accent); display: block; margin-bottom: 26px; }
  h1 { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(34px, 5.2vw, 54px);
    font-weight: 400; line-height: 1.18; letter-spacing: -.01em; margin-bottom: 24px; }
  h1 em { font-style: italic; color: var(--accent); }
  .hero__lead { color: #4a4a4a; font-size: 18.5px; line-height: 1.72; max-width: 560px; }
  .hero__card { background: var(--cream); padding: 40px 34px; text-align: center; }
  .hero__mono { height: 46px; margin-bottom: 26px; opacity: .9; }
  .hero__stat { padding: 14px 0; border-top: 1px solid #e3ded7; }
  .hero__stat:first-of-type { border-top: none; }
  .hero__stat b { display: block; font-family: 'Libre Baskerville', Georgia, serif; font-size: 27px;
    font-weight: 400; color: var(--accent); line-height: 1.25; }
  .hero__stat span { font-size: 12.5px; color: #7d7669; letter-spacing: .06em; text-transform: uppercase; }
  @media (max-width: 880px) { .hero { grid-template-columns: 1fr; gap: 40px; padding: 60px 0 52px; }
    .hero__card { display: flex; align-items: center; justify-content: space-around; gap: 20px;
      padding: 26px 24px; text-align: left; }
    .hero__mono { display: none; } .hero__stat { border-top: none; padding: 0; } }

  /* чипсы-навигация */
  .chips { display: flex; gap: 10px; flex-wrap: wrap; padding-bottom: 8px; }
  .chips a { border: 1px solid var(--line); padding: 9px 18px; font-size: 13.5px; color: #5a5a5a;
    text-decoration: none; transition: all .18s; white-space: nowrap; }
  .chips a:hover { border-color: var(--accent); color: var(--accent); background: #fdfaf9; }

  /* разделы */
  .cat { padding: 62px 0 12px; scroll-margin-top: 74px; }
  .cat__head { display: flex; align-items: baseline; gap: 18px; padding-bottom: 22px;
    border-bottom: 1px solid var(--line); margin-bottom: 30px; flex-wrap: wrap; }
  .cat__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: 28px; font-weight: 400; }
  .cat__lead { color: var(--mute); font-size: 15px; }
  .cat__count { margin-left: auto; font-size: 12px; letter-spacing: .16em; text-transform: uppercase;
    color: #b3aca3; }

  /* карточки */
  .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  @media (max-width: 900px) { .cards { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 620px) { .cards { grid-template-columns: 1fr; } }
  .card { position: relative; display: flex; flex-direction: column; background: #fff;
    border: 1px solid var(--line); padding: 26px 24px 22px; text-decoration: none;
    transition: border-color .2s, box-shadow .25s, transform .25s; }
  .card:hover { border-color: var(--accent); box-shadow: 0 14px 36px rgba(26,20,18,.09);
    transform: translateY(-4px); }
  .card__n { position: absolute; top: 22px; right: 22px; font-family: 'Libre Baskerville', Georgia, serif;
    font-style: italic; font-size: 14px; color: #ccc5bb; transition: color .2s; }
  .card:hover .card__n { color: var(--accent); }
  .card__tag { font-size: 10px; font-weight: 600; letter-spacing: .2em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 14px; }
  .card__title { font-family: 'Libre Baskerville', Georgia, serif; font-size: 19px; font-weight: 400;
    line-height: 1.38; margin-bottom: 11px; }
  .card__desc { font-size: 14.5px; line-height: 1.65; color: #6a6a6a; flex: 1; }
  .card__go { margin-top: 20px; padding-top: 15px; border-top: 1px solid #f0ede9; font-size: 13.5px;
    font-weight: 600; color: var(--accent); display: flex; justify-content: space-between; align-items: center; }
  .card__go i { font-style: normal; transition: transform .22s; }
  .card:hover .card__go i { transform: translateX(5px); }

  /* карточка-акцент — первая в разделе */
  .card--lead { grid-column: span 2; background: var(--cream); border-color: #e6ded3; }
  @media (max-width: 620px) { .card--lead { grid-column: span 1; } }
  .card--lead .card__title { font-size: 25px; line-height: 1.3; }
  .card--lead .card__desc { font-size: 15.5px; max-width: 92%; }
  .card--lead .card__go { border-top-color: #e6ded3; }
  .card--w2 { grid-column: span 2; }
  .card--w3 { grid-column: span 3; }
  .card--w2 .card__desc, .card--w3 .card__desc { max-width: 640px; }
  @media (max-width: 900px) { .card--w3 { grid-column: span 2; } }
  @media (max-width: 620px) { .card--w2, .card--w3 { grid-column: span 1; } }

  /* полоса-цитата */
  .quote { margin: 78px 0 0; padding: 54px 0; border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line); text-align: center; }
  .quote p { font-family: 'Libre Baskerville', Georgia, serif; font-style: italic; font-size: 24px;
    line-height: 1.55; max-width: 720px; margin: 0 auto; }
  .quote p em { font-style: italic; color: var(--accent); }
  .quote span { display: block; margin-top: 18px; font-size: 12.5px; letter-spacing: .18em;
    text-transform: uppercase; color: var(--mute); }

  /* интенсив */
  .intensiv { background: var(--ink); color: #fff; margin-top: 82px; padding: 76px 0; scroll-margin-top: 60px; }
  .intensiv__in { max-width: 1080px; margin: 0 auto; padding: 0 32px; display: grid;
    grid-template-columns: 1.15fr .85fr; gap: 54px; align-items: start; }
  @media (max-width: 880px) { .intensiv__in { grid-template-columns: 1fr; gap: 34px; } }
  .intensiv__label { display: inline-block; border: 1px solid var(--gold); color: var(--gold); font-size: 10.5px;
    font-weight: 600; letter-spacing: .2em; text-transform: uppercase; padding: 6px 14px; margin-bottom: 24px; }
  .intensiv h2 { font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(28px, 4.4vw, 40px);
    font-weight: 400; line-height: 1.24; margin-bottom: 18px; }
  .intensiv h2 em { font-style: italic; color: var(--gold); }
  .intensiv p { color: #c4c4c4; font-size: 17px; line-height: 1.72; }
  .intensiv__stats { display: flex; gap: 34px; flex-wrap: wrap; margin: 30px 0 6px; }
  .intensiv__stats div b { display: block; font-family: 'Libre Baskerville', Georgia, serif;
    font-size: 26px; font-weight: 400; color: var(--gold); }
  .intensiv__stats div span { font-size: 12.5px; color: #9c9c9c; letter-spacing: .04em; }
  .intensiv__list { list-style: none; margin: 6px 0 0; }
  .intensiv__list li { padding: 13px 0; border-bottom: 1px solid #333; font-size: 15.5px; color: #e0e0e0; }
  .intensiv__list li::before { content: "—"; color: var(--gold); margin-right: 10px; }
  .intensiv__cta { display: inline-block; background: #fff; color: var(--ink) !important; text-decoration: none;
    padding: 16px 34px; font-weight: 700; font-size: 16px; margin-top: 30px; transition: opacity .18s; }
  .intensiv__cta:hover { opacity: .87; }
  .intensiv__note { font-size: 13.5px; color: #8f8f8f; margin-top: 14px; }

  /* телеграм */
  .tg { background: var(--cream); padding: 74px 0; }
  .tg__in { max-width: 1080px; margin: 0 auto; padding: 0 32px; display: flex; align-items: center;
    justify-content: space-between; gap: 30px; flex-wrap: wrap; }
  .tg h2 { font-family: 'Libre Baskerville', Georgia, serif; font-size: 26px; font-weight: 400; margin-bottom: 8px; }
  .tg p { color: #6f6a63; font-size: 16px; max-width: 470px; }
  .tg a { display: inline-block; background: var(--accent); color: #fff !important; padding: 15px 32px;
    font-weight: 600; font-size: 15.5px; text-decoration: none; transition: opacity .18s; white-space: nowrap; }
  .tg a:hover { opacity: .88; }

  /* подвал */
  .foot { padding: 32px 0 58px; font-size: 13.5px; color: var(--mute); display: flex; gap: 20px;
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
      <a class="nav__cta" href="#intensiv">Вступить на интенсив</a>
    </div>
  </div>
</nav>

<div class="wrap">
  <header class="hero">
    <div>
      <span class="hero__label">Библиотека maysoulme</span>
      <h1>Гайды и промпты для блога <em>с нейросетями</em></h1>
      <p class="hero__lead">Собрано то, чем пользуюсь сама каждый день: разговорные reels, тексты своим голосом, распаковка личности, ИИ-ассистенты. Забирай и применяй.</p>
    </div>
    <aside class="hero__card">
      <img class="hero__mono" src="logo-ms.png" alt="">
      <div class="hero__stat"><b>%%TOTAL%%</b><span>материалов</span></div>
      <div class="hero__stat"><b>0 ₽</b><span>без регистрации</span></div>
      <div class="hero__stat"><b>4</b><span>раздела</span></div>
    </aside>
  </header>

  <div class="chips">
%%CHIPS%%
  </div>

%%SECTIONS%%

  <section class="quote">
    <p>Разница не в удаче и не в количестве роликов. Разница в том, <em>кому ты говоришь, что именно и куда ведёшь человека дальше</em>.</p>
    <span>600 000 просмотров и 8 подписчиков · против · 19 000 просмотров и 30 000 ₽</span>
  </section>
</div>

<section class="intensiv" id="intensiv">
  <div class="intensiv__in">
    <div>
      <span class="intensiv__label">Платный интенсив</span>
      <h2>ИИ-стратегия <em>на миллион</em></h2>
      <p>Гайды выше — это отдельные детали. На интенсиве мы собираем из них систему: стратегия, контент, свои ИИ-ассистенты и парсер идей, который приносит темы, пока ты завтракаешь.</p>
      <div class="intensiv__stats">
        <div><b>+10 000</b><span>в Telegram</span></div>
        <div><b>+22 000</b><span>в Instagram</span></div>
      </div>
      <a class="intensiv__cta" href="%%INTENSIV%%">Смотреть программу и цены →</a>
      <p class="intensiv__note">Вечный доступ · чат поддержки · есть формат VIP с личным сопровождением</p>
    </div>
    <ul class="intensiv__list">
      <li>Стратегия блога и позиционирование</li>
      <li>Текстовые и разговорные reels</li>
      <li>ИИ-агент с памятью твоего канала</li>
      <li>Парсер залетающих идей ниши</li>
      <li>Готовые ассистенты и шаблоны</li>
      <li>Собрано без единого программиста</li>
    </ul>
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
