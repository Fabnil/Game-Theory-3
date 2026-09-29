#!/usr/bin/env python3
"""Build a page-faithful Markdown edition of the supplied AGT textbook.

The PDF's mathematical fonts do not have a reliable Unicode map. Each PDF page
is therefore rendered as an image, while extracted text is included only as a
search aid. Formal statements and figures are additionally cropped from the
source pages. This script deliberately does not reconstruct equations.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pymupdf
from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "materials/sources/Nisan-et-al-AGT-book.pdf"
PAGE_DIR = HERE / "images/pages"
STATEMENT_DIR = HERE / "images/statements"
FIGURE_DIR = HERE / "images/figures"
CHAPTER_DIR = HERE / "chapters"
SCALE = 1.8
PAGE_QUALITY = 84

CHAPTERS = [
    (1, 24, "Basic Solution Concepts and Computational Issues"),
    (2, 50, "The Complexity of Finding Nash Equilibria"),
    (3, 74, "Equilibrium Computation for Two-Player Games in Strategic and Extensive Form"),
    (4, 100, "Learning, Regret Minimization, and Equilibria"),
    (5, 124, "Combinatorial Algorithms for Market Equilibria"),
    (6, 156, "Computation of Market Equilibria by Convex Programming"),
    (7, 180, "Graphical Games"),
    (8, 202, "Cryptography and Game Theory"),
    (9, 230, "Introduction to Mechanism Design (for Computer Scientists)"),
    (10, 264, "Mechanism Design without Money"),
    (11, 288, "Combinatorial Auctions"),
    (12, 322, "Computationally Efficient Approximation Mechanisms"),
    (13, 352, "Profit Maximization in Mechanism Design"),
    (14, 384, "Distributed Algorithmic Mechanism Design"),
    (15, 406, "Cost Sharing"),
    (16, 432, "Online Mechanisms"),
    (17, 464, "Introduction to the Inefficiency of Equilibria"),
    (18, 482, "Routing Games"),
    (19, 508, "Network Formation Games and the Potential Function Method"),
    (20, 538, "Selfish Load Balancing"),
    (21, 564, "The Price of Anarchy and the Design of Scalable Resource Allocation Mechanisms"),
    (22, 592, "Incentives and Pricing in Communications Networks"),
    (23, 614, "Incentives in Peer-to-Peer Systems"),
    (24, 634, "Cascading Behavior in Networks: Algorithmic and Economic Issues"),
    (25, 654, "Incentives and Information Security"),
    (26, 672, "Computational Aspects of Prediction Markets"),
    (27, 698, "Manipulation-Resistant Reputation Systems"),
    (28, 720, "Sponsored Search Auctions"),
    (29, 738, "Computational Evolutionary Game Theory"),
]

PARTS = [
    (1, 22, "Computing in Games"),
    (2, 228, "Algorithmic Mechanism Design"),
    (3, 462, "Quantifying the Inefficiency of Equilibria"),
    (4, 590, "Additional Topics"),
]

KINDS = (
    "Theorem",
    "Lemma",
    "Proposition",
    "Definition",
    "Corollary",
    "Claim",
    "Algorithm",
    "Observation",
)
FORMAL_RE = re.compile(
    r"^(" + "|".join(KINDS) + r")\b(?:\s+(\d+(?:\.\d+)*))?"
)
FIGURE_RE = re.compile(r"^(Figure|Table)\s+(\d+(?:\.\d+)+)(?:\b|\.)")
SECTION_RE = re.compile(r"^(\d{1,2}\.\d+(?:\.\d+)?)\s+(\S.{2,})$")
LIGATURES = str.maketrans(
    {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}
)


def clean(text: str) -> str:
    """Expose unmapped font glyphs instead of silently inventing mathematics."""
    text = text.translate(LIGATURES)
    converted = "".join(
        f"⟦U+{ord(ch):04X}; см. снимок страницы⟧"
        if ord(ch) < 32 and ch not in "\n\t"
        else ch
        for ch in text
    )
    return "\n".join(line.rstrip() for line in converted.splitlines())


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def make_regions(page_count: int) -> list[dict]:
    starts = [
        {"kind": "front", "number": 0, "start": 1, "title": "Front matter"},
        *[
            {"kind": "part", "number": n, "start": start, "title": title}
            for n, start, title in PARTS
        ],
        *[
            {"kind": "chapter", "number": n, "start": start, "title": title}
            for n, start, title in CHAPTERS
        ],
        {"kind": "index", "number": 30, "start": 758, "title": "Index"},
    ]
    starts.sort(key=lambda item: item["start"])
    for i, item in enumerate(starts):
        item["end"] = (starts[i + 1]["start"] - 1) if i + 1 < len(starts) else page_count
        if item["kind"] == "chapter":
            item["file"] = f"{item['number']:02d}_{slug(item['title'])}.md"
        elif item["kind"] == "part":
            item["file"] = f"part_{item['number']:02d}.md"
        elif item["kind"] == "front":
            item["file"] = "00_front_matter.md"
        else:
            item["file"] = "30_index.md"
    assert starts[0]["start"] == 1 and starts[-1]["end"] == page_count
    assert all(a["end"] + 1 == b["start"] for a, b in zip(starts, starts[1:]))
    return starts


def lines_with_fonts(page: pymupdf.Page) -> list[dict]:
    result = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            result.append(
                {
                    "text": clean("".join(s["text"] for s in line["spans"]).strip()),
                    "font": spans[0]["font"],
                    "size": spans[0]["size"],
                    "bbox": line["bbox"],
                }
            )
    return result


def save_crop(page_image: Image.Image, box: tuple[float, float, float, float], path: Path) -> None:
    x0, y0, x1, y1 = box
    pixel_box = tuple(round(value * SCALE) for value in (x0, y0, x1, y1))
    page_image.crop(pixel_box).save(path, "PNG", optimize=True)


def render_page(doc: pymupdf.Document, number: int) -> Image.Image:
    page = doc[number - 1]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def collect_page(doc: pymupdf.Document, number: int, image: Image.Image) -> dict:
    page = doc[number - 1]
    # sort=True silently drops several unmapped mathematical font codes in this
    # particular PDF. The PDF's own text order is the safer searchable layer.
    raw_text = page.get_text("text")
    text = clean(raw_text).rstrip()
    font_lines = lines_with_fonts(page)
    page_record = {
        "number": number,
        "text": text,
        "control_glyphs": sum(ord(c) < 32 and c not in "\n\t" for c in raw_text),
        "statements": [],
        "figures": [],
        "sections": [],
    }
    for line in font_lines:
        value = line["text"]
        if "Bold" not in line["font"]:
            continue
        section = SECTION_RE.match(value)
        if section and line["size"] >= 10.5 and len(value) < 125:
            page_record["sections"].append({"number": section.group(1), "title": section.group(2)})
        formal = FORMAL_RE.match(value)
        figure = FIGURE_RE.match(value)
        if not formal and not figure:
            continue
        kind, identifier = (formal or figure).groups()
        identifier = identifier or "без номера"
        is_figure = figure is not None
        index = len(page_record["figures"] if is_figure else page_record["statements"]) + 1
        directory = FIGURE_DIR if is_figure else STATEMENT_DIR
        file_identifier = slug(identifier) if identifier != "без номера" else "unnumbered"
        filename = f"p{number:04d}_{kind.lower()}_{file_identifier}_{index:02d}.png"
        x0, y0, x1, y1 = line["bbox"]
        if is_figure:
            top = max(42.0, y0 - 250.0)
            bottom = min(page.rect.height - 35.0, y1 + 25.0)
        else:
            top = max(42.0, y0 - 10.0)
            bottom = min(page.rect.height - 39.0, y0 + 255.0)
        save_crop(image, (60.0, top, page.rect.width - 60.0, bottom), directory / filename)
        item = {
            "kind": kind,
            "number": identifier,
            "heading": value,
            "page": number,
            "image": f"images/{'figures' if is_figure else 'statements'}/{filename}",
        }
        if not is_figure and y0 > page.rect.height - 120.0 and number < len(doc):
            continuation_image = render_page(doc, number + 1)
            continuation_name = filename.removesuffix(".png") + "_continuation.png"
            continuation_page = doc[number]
            save_crop(
                continuation_image,
                (60.0, 58.0, continuation_page.rect.width - 60.0, 285.0),
                directory / continuation_name,
            )
            item["continuation_image"] = f"images/statements/{continuation_name}"
        page_record["figures" if is_figure else "statements"].append(item)
    return page_record


def chapter_page(page_number: int) -> int | None:
    return page_number - 21 if page_number >= 22 else None


def page_markdown(record: dict, prefix: str) -> str:
    number = record["number"]
    image = f"{prefix}images/pages/p{number:04d}.jpg"
    pdf = f"{prefix}../materials/sources/Nisan-et-al-AGT-book.pdf#page={number}"
    printed = chapter_page(number)
    printed_label = f" · книжная стр. {printed}" if printed is not None else ""
    out = [
        f'<a id="pdf-page-{number:04d}"></a>',
        f"### PDF стр. {number}{printed_label}",
        "",
        f"![Исходная PDF-страница {number}]({image})",
        "",
        f"[Открыть страницу отдельно]({image}) · [Открыть страницу в PDF]({pdf})",
        "",
    ]
    for item in record["statements"]:
        out += [
            f"**{item['heading']}** — фрагмент оригинальной страницы:",
            "",
            f"![{item['kind']} {item['number']}, PDF стр. {number}]({prefix}{item['image']})",
            "",
            f"[Открыть фрагмент отдельно]({prefix}{item['image']})",
            "",
        ]
        if item.get("continuation_image"):
            out += [
                f"Начало следующей страницы для проверки продолжения: "
                f"![Следующая страница после {item['kind']} {item['number']}]"
                f"({prefix}{item['continuation_image']})",
                "",
            ]
    for item in record["figures"]:
        out += [
            f"**{item['heading']}** — область рисунка или таблицы:",
            "",
            f"![{item['kind']} {item['number']}, PDF стр. {number}]({prefix}{item['image']})",
            "",
            f"[Открыть фрагмент отдельно]({prefix}{item['image']})",
            "",
        ]
    out += [
        "<details>",
        "<summary>Поисковый текст страницы (формулы сверяйте с изображением)</summary>",
        "",
        "~~~~text",
        record["text"] or "[На этой странице нет извлекаемого текстового слоя.]",
        "~~~~",
        "",
        "</details>",
        "",
    ]
    return "\n".join(out)


def region_intro(region: dict, pages: list[dict], is_full_book: bool = False) -> str:
    number = region["number"]
    title = region["title"]
    if region["kind"] == "chapter":
        heading = f"Глава {number}. {title}"
    elif region["kind"] == "part":
        heading = f"Часть {number}. {title}"
    elif region["kind"] == "front":
        heading = "Вводные страницы"
    else:
        heading = "Предметный указатель"
    if is_full_book:
        out = [f"## {heading}", ""]
    else:
        out = [f"# {heading}", ""]
    out += [
        f"**PDF-страницы:** {region['start']}–{region['end']}. "
        "Изображения передают исходную страницу; извлечённый текст ниже нужен для поиска.",
        "",
    ]
    sections = []
    for page in pages:
        for section in page["sections"]:
            sections.append(
                f"- [{section['number']} {section['title']}](#pdf-page-{page['number']:04d}) "
                f"— PDF стр. {page['number']}"
            )
    if sections:
        out += ["### Разделы", "", *sections, ""]
    return "\n".join(out)


def write_readme(regions: list[dict], pages: list[dict], digest: str) -> None:
    statement_count = sum(len(p["statements"]) for p in pages)
    figure_count = sum(len(p["figures"]) for p in pages)
    control_pages = sum(bool(p["control_glyphs"]) for p in pages)
    out = [
        "# Algorithmic Game Theory — постраничный Markdown-архив",
        "",
        "Источник: Nisan et al., *Algorithmic Game Theory*, файл "
        "[Nisan-et-al-AGT-book.pdf](../materials/sources/Nisan-et-al-AGT-book.pdf). "
        "Здесь сохранены **все 775 страниц**: вводные материалы, четыре части, 29 глав и "
        "предметный указатель. Книжная нумерация после вводных страниц равна номеру "
        "страницы PDF минус 21.",
        "",
        f"Контрольная сумма исходного PDF (SHA-256): `{digest}`.",
        "",
        "## Как читать",
        "",
        "- [Вся книга одним большим Markdown-файлом](00_full_book.md). Для быстрого "
        "просмотра удобнее файлы глав ниже.",
        "- [Теоремы, определения, леммы и другие формальные утверждения](KEY_STATEMENTS.md) "
        f"({statement_count} фрагментов исходных страниц).",
        "- [Рисунки и таблицы](FIGURES.md) "
        f"({figure_count} фрагментов исходных страниц).",
        "- Текст под каждой страницей можно искать и копировать. Он получен автоматически; "
        "математические шрифты PDF местами не имеют однозначного Unicode-соответствия. "
        f"Такие знаки встречаются на {control_pages} страницах и показаны как "
        "`⟦U+0001; см. снимок страницы⟧` и подобные маркеры. "
        "В указателе и других многоколоночных местах порядок извлечённых строк также "
        "может отличаться от порядка чтения. "
        "**Не используйте поисковый слой как источник точной формулы**: "
        "сверяйте её с изображением страницы.",
        "- Фрагмент под заголовком формального утверждения помогает быстро найти его; "
        "если текст продолжается ниже или на следующей странице, откройте полный снимок. "
        "Дополнительный фрагмент следующей страницы не означает, что утверждение непременно "
        "продолжается.",
        "- Для повторной сборки запустите [build_book.py](build_book.py) с PyMuPDF и Pillow. "
        "Скрипт и изображения сохранены вместе с Markdown.",
        "",
        "## Содержание",
        "",
        "| Раздел | PDF-страницы | Файл |",
        "|---|---:|---|",
    ]
    for region in regions:
        if region["kind"] == "chapter":
            label = f"{region['number']}. {region['title']}"
        elif region["kind"] == "part":
            label = f"Часть {region['number']}. {region['title']}"
        elif region["kind"] == "front":
            label = "Вводные страницы"
        else:
            label = "Предметный указатель"
        out.append(
            f"| {label} | {region['start']}–{region['end']} | "
            f"[Открыть](chapters/{region['file']}) |"
        )
    out += [
        "",
        "Этот архив сохраняет **содержание исходных страниц**, а не выдаёт "
        "автоматическое распознавание формул за проверенную TeX-транскрипцию. "
        "Скриншоты утверждений представляют оригинал учебника, а не перерисованную схему.",
        "",
    ]
    (HERE / "README.md").write_text("\n".join(out), encoding="utf-8")


def write_indexes(regions: list[dict], pages: list[dict]) -> None:
    region_for_page = {
        n: region
        for region in regions
        for n in range(region["start"], region["end"] + 1)
    }
    for field, filename, title in [
        ("statements", "KEY_STATEMENTS.md", "Формальные утверждения"),
        ("figures", "FIGURES.md", "Рисунки и таблицы"),
    ]:
        out = [
            f"# {title}",
            "",
            "Это ссылки на фрагменты **оригинального PDF**. Для проверки полного контекста "
            "откройте соответствующую страницу главы.",
            "",
        ]
        last_region = None
        for page in pages:
            region = region_for_page[page["number"]]
            for item in page[field]:
                if region["file"] != last_region:
                    label = (
                        f"Глава {region['number']}. {region['title']}"
                        if region["kind"] == "chapter"
                        else region["title"]
                    )
                    out += [f"## {label}", ""]
                    last_region = region["file"]
                anchor = f"#pdf-page-{page['number']:04d}"
                item_label = (
                    item["heading"] if item["number"] == "без номера"
                    else f"{item['kind']} {item['number']}"
                )
                out.append(
                    f"- **{item_label}** "
                    f"([PDF стр. {page['number']}](chapters/{region['file']}{anchor})) — "
                    f"[фрагмент]({item['image']})"
                    + (
                        f", [продолжение]({item['continuation_image']})"
                        if item.get("continuation_image")
                        else ""
                    )
                )
            if page[field]:
                out.append("")
        (HERE / filename).write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    for directory in (PAGE_DIR, STATEMENT_DIR, FIGURE_DIR, CHAPTER_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for directory, pattern in (
        (PAGE_DIR, "p*.jpg"),
        (STATEMENT_DIR, "p*.png"),
        (FIGURE_DIR, "p*.png"),
    ):
        for old_image in directory.glob(pattern):
            old_image.unlink()
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    doc = pymupdf.open(SOURCE)
    assert len(doc) == 775, f"Unexpected number of PDF pages: {len(doc)}"
    regions = make_regions(len(doc))
    pages = []
    for number in range(1, len(doc) + 1):
        image = render_page(doc, number)
        image.save(PAGE_DIR / f"p{number:04d}.jpg", "JPEG", quality=PAGE_QUALITY, optimize=True)
        pages.append(collect_page(doc, number, image))
        image.close()
        if number % 50 == 0 or number == len(doc):
            print(f"Rendered {number}/{len(doc)} pages", flush=True)

    with (HERE / "00_full_book.md").open("w", encoding="utf-8") as big:
        big.write(
            "# Algorithmic Game Theory — полный постраничный архив\n\n"
            "Это поисковый текст и изображения всех страниц PDF. Для навигации откройте "
            "[содержание](README.md). Формулы и обозначения сверяйте с изображениями.\n\n"
        )
        for region in regions:
            selected = pages[region["start"] - 1 : region["end"]]
            big.write(region_intro(region, selected, is_full_book=True))
            path = CHAPTER_DIR / region["file"]
            with path.open("w", encoding="utf-8") as chapter:
                chapter.write(region_intro(region, selected))
                chapter.write("[К содержанию](../README.md) · [К полному файлу](../00_full_book.md)\n\n")
                for page in selected:
                    chapter.write(page_markdown(page, "../"))
                    big.write(page_markdown(page, ""))

    write_indexes(regions, pages)
    write_readme(regions, pages, digest)
    statement_counts = Counter(
        item["kind"] for page in pages for item in page["statements"]
    )
    manifest = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": digest,
        "pdf_pages": len(doc),
        "chapter_count": len(CHAPTERS),
        "region_count": len(regions),
        "page_images": len(pages),
        "formal_statement_images": sum(len(p["statements"]) for p in pages),
        "formal_continuation_images": sum(
            bool(item.get("continuation_image"))
            for p in pages
            for item in p["statements"]
        ),
        "figure_and_table_images": sum(len(p["figures"]) for p in pages),
        "formal_by_kind": dict(sorted(statement_counts.items())),
        "pages_with_unmapped_glyphs": sum(bool(p["control_glyphs"]) for p in pages),
        "regions": [
            {key: region[key] for key in ("kind", "number", "title", "start", "end", "file")}
            for region in regions
        ],
    }
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in manifest.items() if k != "regions"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
