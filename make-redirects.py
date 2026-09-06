#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ставит редиректы со старых адресов гайдов на новые адреса портала.

  python3 make-redirects.py           показать, что будет сделано
  python3 make-redirects.py --apply   применить и запушить

Запускать ПОСЛЕ того, как домен привязан к порталу.
Старые страницы заменяются на короткую страницу-редирект (meta refresh + JS),
поисковики и телеграм-превью подхватывают canonical на новый адрес.
"""
import subprocess, sys, tempfile, shutil, html
from pathlib import Path

SITE = "https://maysoulme.ru"
OWNER = "maiyamaiya19999-bit"

# старый файл -> новый slug портала
REDIRECTS = [
    # (репозиторий, путь внутри репо, новый slug, название)
    ("maysoulme-assets", "humanizator.html",                    "promt-humanizator",          "Промт-хуманизатор"),
    ("maysoulme-assets", "reels-expert.html",                   "razgovornyj-ekspertnyj-rolik","Разговорный экспертный ролик"),
    ("maysoulme-assets", "lichnaya-istoriya.html",              "lichnaya-istoriya",          "Личная история под суфлёр"),
    ("maysoulme-assets", "posty-karuseli.html",                 "post-karusel",               "Пост-карусель"),
    ("maysoulme-assets", "raspakovka-lichnosti.html",           "raspakovka-lichnosti",       "Распаковка личности"),
    ("maysoulme-assets", "tripwire-ca.html",                    "analiz-ca-tripwire",         "Анализ ЦА для трипваера"),
    ("maysoulme-assets", "kimi_blogging_guide_v3.html",         "kimi-dlya-bloginga",         "Kimi для блогинга"),
    ("maysoulme-assets", "guides/claude-russia/index.html",     "claude-i-chatgpt-v-rossii",  "Claude и ChatGPT в России"),
    ("maysoulme-assets", "ai-access-guide/index.html",          "claude-i-chatgpt-v-rossii",  "Claude и ChatGPT в России"),
    ("maysoulme-assets", "guides/podgotovka-akkaunta/index.html","podgotovka-akkaunta",       "Подготовка аккаунта"),
    ("maysoulme-assets", "guides/claude-skills/index.html",     "luchshie-skilly-claude",     "Лучшие скиллы для Claude"),
    ("maysoulme-assets", "guides/codex-skill/index.html",       "svoj-skill-dlya-codex",      "Свой первый скилл"),
    ("maysoulme-assets", "guides/promt-pravdy/index.html",      "promt-pravdy",               "Промпт правды"),
    ("maysoulme-assets", "family-tree-guide/index.html",        "genealogicheskoe-drevo",     "Генеалогическое древо"),
    ("photo-audit-guide",  "index.html", "gde-moi-foto",                "Где в интернете есть мои фото"),
    ("reels-guide",        "index.html", "40-scenariev",                "40 сценариев для Reels"),
    ("razgovornye-roliki", "index.html", "formula-razgovornyh-rolikov", "Формула разговорных роликов"),
    ("carousel-prompt",    "index.html", "post-karusel",                "Пост-карусель"),
    ("english-course",     "index.html", "anglijskij-za-16-chasov",     "Английский за 16 часов"),
]

PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>{title} — переехал на maysoulme.ru</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<meta name="robots" content="noindex">
<script>location.replace("{url}");</script>
<style>body{{font-family:-apple-system,Inter,sans-serif;max-width:520px;margin:16vh auto;padding:0 22px;
color:#1a1a1a;text-align:center;line-height:1.7}}a{{color:#710C04;font-weight:600}}</style>
</head>
<body>
<p>Гайд «{title}» переехал на новый адрес.</p>
<p><a href="{url}">Открыть на maysoulme.ru →</a></p>
</body>
</html>
"""

def main():
    apply = "--apply" in sys.argv
    by_repo = {}
    for repo, path, slug, title in REDIRECTS:
        by_repo.setdefault(repo, []).append((path, slug, title))

    for repo, items in by_repo.items():
        print(f"\n=== {repo}")
        for path, slug, title in items:
            print(f"   {path}  →  {SITE}/guides/{slug}/")
        if not apply:
            continue
        tmp = Path(tempfile.mkdtemp())
        work = tmp / repo
        subprocess.run(["gh", "repo", "clone", f"{OWNER}/{repo}", str(work), "--", "-q"], check=True)
        for path, slug, title in items:
            f = work / path
            if not f.exists():
                print(f"   ! нет файла {path}, пропускаю")
                continue
            f.write_text(PAGE.format(title=html.escape(title), url=f"{SITE}/guides/{slug}/"), encoding="utf-8")
        subprocess.run(["git", "-C", str(work), "add", "-A"], check=True)
        r = subprocess.run(["git", "-C", str(work), "commit", "-q", "-m",
                            "Редиректы на портал maysoulme.ru"], capture_output=True)
        if r.returncode == 0:
            subprocess.run(["git", "-C", str(work), "push", "-q"], check=True)
            print("   ✓ запушено")
        else:
            print("   — нечего менять")
        shutil.rmtree(tmp, ignore_errors=True)

    if not apply:
        print("\nЭто предпросмотр. Чтобы применить:  python3 make-redirects.py --apply")

if __name__ == "__main__":
    main()
