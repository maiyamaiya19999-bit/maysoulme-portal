#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка портала maysoulme.

  python3 build.py

Читает guides.json, копирует исходные HTML-гайды в guides/<slug>/index.html,
чинит пути к логотипу, вешает возврат на портал и подвал, генерирует главную.
Если исходник недоступен — уже собранный гайд остаётся как есть.

Чтобы добавить новый гайд: положить его HTML куда угодно, прописать блок
в guides.json (slug, title, desc, tag, src) и запустить build.py.
"""
import json, re, shutil, html
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

ACCENT = "#710C04"

# ---------------------------------------------------------------- обработка гайда

FOOTER = """
<footer class="portal-footer">
  <a class="portal-footer__back" href="../../">← Все гайды maysoulme</a>
  <p class="portal-footer__line">Гайд из бесплатной библиотеки <a href="../../">maysoulme</a>. Больше — в <a href="{tg}">телеграм-канале</a>.</p>
  <a class="portal-footer__cta" href="../../#intensiv">Интенсив «ИИ-стратегия на миллион» →</a>
</footer>
<style>
  .portal-footer {{ max-width: 720px; margin: 64px auto 0; padding: 32px 22px 56px; border-top: 1px solid #e8e8e8;
    font-family: 'Inter', -apple-system, sans-serif; font-size: 15px; color: #666; text-align: center; }}
  .portal-footer a {{ color: {accent}; }}
  .portal-footer__back {{ display: inline-block; font-weight: 600; margin-bottom: 14px; text-decoration: none; }}
  .portal-footer__back:hover {{ text-decoration: underline; }}
  .portal-footer__line {{ margin: 0 0 22px; line-height: 1.6; }}
  .portal-footer__cta {{ display: inline-block; background: {accent}; color: #fff !important; text-decoration: none;
    padding: 13px 26px; font-weight: 600; font-size: 15px; }}
</style>
"""

def process_guide(src_html: str, g: dict) -> str:
    s = src_html
    # логотип -> локальный файл портала
    s = s.replace("https://maiyamaiya19999-bit.github.io/maysoulme-assets/logo-ms.png", "../../logo-ms.png")
    s = re.sub(r'(<img[^>]+src=")(?:\./)?logo-ms\.(png|svg)(")', r'\1../../logo-ms.png\3', s)
    # клик по логотипу в навбаре -> главная портала
    s = re.sub(r'(<a[^>]*class="[^"]*nav__logo[^"]*"[^>]*href=")#(")', r'\1../../\2', s)
    # og-теги для красивых превью в телеграме
    if "og:title" not in s:
        og = (f'<meta property="og:type" content="article">\n'
              f'<meta property="og:title" content="{html.escape(g["title"])}">\n'
              f'<meta property="og:description" content="{html.escape(g["desc"])}">\n'
              f'<meta property="og:url" content="{SITE}/guides/{g["slug"]}/">\n'
              f'<meta property="og:image" content="{SITE}/logo-ms.png">\n')
        s = s.replace("</head>", og + "</head>", 1)
    # подвал портала
    if "portal-footer" not in s:
        foot = FOOTER.format(tg=TG, accent=ACCENT)
        s = s.replace("</body>", foot + "</body>", 1) if "</body>" in s else s + foot
    return s

def resolve(src: str) -> Path | None:
    root, rest = src.split("/", 1)
    p = SOURCE_ROOTS.get(root)
    return (p / rest) if p else None

# ---------------------------------------------------------------- главная

def card(g, cat_id):
    return f"""        <a class="card" href="guides/{g['slug']}/">
          <span class="card__tag">{html.escape(g['tag'])}</span>
          <h3 class="card__title">{html.escape(g['title'])}</h3>
          <p class="card__desc">{html.escape(g['desc'])}</p>
          <span class="card__go">Открыть →</span>
        </a>"""

def build_index(data, counts):
    total = sum(len(c["guides"]) for c in data["categories"])
    nav_links = "\n".join(
        f'      <a href="#{c["id"]}">{html.escape(c["title"])}</a>' for c in data["categories"])
    sections = []
    for c in data["categories"]:
        cards = "\n".join(card(g, c["id"]) for g in c["guides"])
        sections.append(f"""    <section class="cat" id="{c['id']}">
      <div class="cat__head">
        <h2 class="cat__title">{html.escape(c['title'])}</h2>
        <p class="cat__lead">{html.escape(c['lead'])}</p>
      </div>
      <div class="cards">
{cards}
      </div>
    </section>""")
    return TEMPLATE.format(
        total=total, nav_links=nav_links, sections="\n\n".join(sections),
        tg=TG, intensiv=INTENSIV, site=SITE)

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>maysoulme — блог, ИИ и система контента</title>
<meta name="description" content="Бесплатная библиотека гайдов и промптов про блогинг с нейросетями: reels, тексты, распаковка личности, ИИ-ассистенты. И интенсив «ИИ-стратегия на миллион».">
<meta property="og:type" content="website">
<meta property="og:title" content="maysoulme — блог, ИИ и система контента">
<meta property="og:description" content="{total} бесплатных гайдов и промптов про блогинг с нейросетями. И интенсив «ИИ-стратегия на миллион».">
<meta property="og:url" content="{site}/">
<meta property="og:image" content="{site}/logo-ms.png">
<link rel="icon" href="logo-ms.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700;800&family=DM+Sans:ital@1&display=swap" rel="stylesheet">
<style>
  :root {{ --accent: #710C04; --ink: #1a1a1a; --grey: #f5f5f5; --line: #e8e8e8; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Inter', -apple-system, sans-serif; background: #fff; color: var(--ink);
    font-size: 17px; line-height: 1.7; -webkit-font-smoothing: antialiased; }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1000px; margin: 0 auto; padding: 0 22px; }}

  /* навбар */
  .nav {{ position: sticky; top: 0; z-index: 100; background: #fff; border-bottom: 1px solid #f0f0f0; }}
  .nav__in {{ max-width: 1000px; margin: 0 auto; padding: 13px 22px; display: flex; align-items: center; gap: 12px; }}
  .nav__logo img {{ height: 28px; display: block; }}
  .nav__name {{ font-family: 'DM Sans', sans-serif; font-style: italic; color: #888; font-size: 15px; }}
  .nav__links {{ margin-left: auto; display: flex; gap: 22px; font-size: 14.5px; }}
  .nav__links a {{ text-decoration: none; color: #555; }}
  .nav__links a:hover {{ color: var(--accent); }}
  .nav__cta {{ background: var(--accent); color: #fff !important; padding: 8px 16px; font-weight: 600; }}
  @media (max-width: 720px) {{ .nav__links a:not(.nav__cta) {{ display: none; }} }}

  /* герой */
  .hero {{ padding: 74px 0 52px; max-width: 720px; }}
  .badge {{ display: inline-block; border: 1px solid var(--accent); color: var(--accent); font-size: 11px;
    font-weight: 600; letter-spacing: .18em; text-transform: uppercase; padding: 6px 14px; margin-bottom: 26px; }}
  h1 {{ font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(30px, 5.4vw, 46px);
    font-weight: 700; line-height: 1.25; margin-bottom: 20px; }}
  h1 em {{ font-style: italic; color: var(--accent); }}
  .hero__lead {{ color: #444; font-size: 18.5px; }}
  .hero__meta {{ margin-top: 26px; display: flex; gap: 22px; flex-wrap: wrap; color: #666; font-size: 14.5px; }}
  .hero__meta span::before {{ content: ""; display: inline-block; width: 5px; height: 5px; background: var(--accent);
    margin-right: 8px; vertical-align: 3px; }}

  /* категории и карточки */
  .cat {{ padding: 46px 0 8px; scroll-margin-top: 70px; }}
  .cat__head {{ border-top: 1px solid var(--line); padding-top: 26px; margin-bottom: 26px; }}
  .cat__title {{ font-family: 'Libre Baskerville', Georgia, serif; font-size: 25px; font-weight: 700; }}
  .cat__lead {{ color: #666; font-size: 16px; margin-top: 6px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(288px, 1fr)); gap: 16px; }}
  .card {{ display: flex; flex-direction: column; background: #f9f9f9; border: 1px solid var(--line);
    padding: 22px 22px 20px; text-decoration: none; transition: border-color .18s, background .18s, transform .18s; }}
  .card:hover {{ border-color: var(--accent); background: #fff; transform: translateY(-2px); }}
  .card__tag {{ font-size: 10.5px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 12px; }}
  .card__title {{ font-family: 'Libre Baskerville', Georgia, serif; font-size: 18.5px; font-weight: 700;
    line-height: 1.35; margin-bottom: 10px; }}
  .card__desc {{ font-size: 15px; line-height: 1.62; color: #555; flex: 1; }}
  .card__go {{ margin-top: 18px; font-size: 14px; font-weight: 600; color: var(--accent); }}

  /* интенсив */
  .intensiv {{ background: var(--ink); color: #fff; margin-top: 66px; padding: 62px 0; scroll-margin-top: 60px; }}
  .intensiv__in {{ max-width: 1000px; margin: 0 auto; padding: 0 22px; display: grid;
    grid-template-columns: 1.15fr .85fr; gap: 46px; align-items: start; }}
  @media (max-width: 820px) {{ .intensiv__in {{ grid-template-columns: 1fr; gap: 30px; }} }}
  .intensiv .badge {{ border-color: #c9a07a; color: #c9a07a; }}
  .intensiv h2 {{ font-family: 'Libre Baskerville', Georgia, serif; font-size: clamp(26px, 4vw, 35px);
    line-height: 1.28; margin-bottom: 18px; }}
  .intensiv h2 em {{ font-style: italic; color: #c9a07a; }}
  .intensiv p {{ color: #cfcfcf; font-size: 17px; }}
  .intensiv__list {{ list-style: none; margin: 24px 0 0; }}
  .intensiv__list li {{ padding: 11px 0; border-bottom: 1px solid #333; font-size: 15.5px; color: #e4e4e4; }}
  .intensiv__list li::before {{ content: "—"; color: #c9a07a; margin-right: 10px; }}
  .intensiv__cta {{ display: inline-block; background: #fff; color: var(--ink) !important; text-decoration: none;
    padding: 15px 32px; font-weight: 700; font-size: 16px; margin-top: 26px; }}
  .intensiv__note {{ font-size: 13.5px; color: #999; margin-top: 14px; }}

  /* телеграм */
  .tg {{ background: var(--grey); padding: 52px 0; text-align: center; }}
  .tg h2 {{ font-family: 'Libre Baskerville', Georgia, serif; font-size: 26px; margin-bottom: 12px; }}
  .tg p {{ color: #555; max-width: 520px; margin: 0 auto 24px; }}
  .tg a {{ display: inline-block; background: var(--accent); color: #fff !important; text-decoration: none;
    padding: 14px 30px; font-weight: 600; }}

  /* подвал */
  .foot {{ padding: 34px 0 54px; font-size: 14px; color: #888; display: flex; gap: 20px;
    flex-wrap: wrap; justify-content: space-between; }}
  .foot a {{ color: #888; }}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav__in">
    <a class="nav__logo" href="./"><img src="logo-ms.png" alt="MS"></a>
    <span class="nav__name">maysoulme</span>
    <div class="nav__links">
{nav_links}
      <a class="nav__cta" href="#intensiv">Интенсив</a>
    </div>
  </div>
</nav>

<div class="wrap">
  <header class="hero">
    <span class="badge">Блог · ИИ · система контента</span>
    <h1>Всё, что я знаю про блог <em>с нейросетями</em> — в одном месте</h1>
    <p class="hero__lead">Бесплатные гайды и промпты, которыми я пользуюсь сама каждый день: разговорные reels, тексты своим голосом, распаковка личности, ИИ-ассистенты. Плюс интенсив, если хочешь собрать из этого систему.</p>
    <div class="hero__meta">
      <span>{total} гайдов и промптов</span>
      <span>Бесплатно, без регистрации</span>
      <span>Обновляется</span>
    </div>
  </header>

{sections}
</div>

<section class="intensiv" id="intensiv">
  <div class="intensiv__in">
    <div>
      <span class="badge">Платный интенсив</span>
      <h2>ИИ-стратегия <em>на миллион</em></h2>
      <p>Гайды выше — это отдельные детали. На интенсиве мы собираем из них систему: стратегия, контент, свои ИИ-ассистенты и парсер идей, который приносит темы, пока ты завтракаешь.</p>
      <a class="intensiv__cta" href="{intensiv}">Смотреть программу и цены →</a>
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
  <div class="wrap">
    <h2>Новые гайды — сначала в канале</h2>
    <p>Пишу про блогинг и нейросети без магии и мотивации: что работает, что нет и почему.</p>
    <a href="{tg}">Читать @maysoulme</a>
  </div>
</section>

<div class="wrap">
  <footer class="foot">
    <span>© maysoulme · Майя Шебаршина</span>
    <span><a href="{tg}">Telegram</a> · <a href="politika.html">Политика конфиденциальности</a></span>
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
    (ROOT / "index.html").write_text(build_index(data, None), encoding="utf-8")
    print(f"Готово: {copied} гайдов пересобрано, {skipped} оставлено, главная обновлена.")

if __name__ == "__main__":
    main()
