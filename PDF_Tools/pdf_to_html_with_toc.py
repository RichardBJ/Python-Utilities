#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert a bookmarked PDF to a single HTML with:
- A nested TOC generated from the PDF bookmarks (outlines)
- Per-page anchors (#p1, #p2, ...) and hyperlinks from the TOC

Tested with:
  - Python 3.13
  - pikepdf 9.9.0
  - PyMuPDF (pymupdf) 1.26.1

Notes:
- Some bookmarks use JavaScript or remote targets; those cannot be resolved
  to page numbers and will appear in the TOC as non-clickable (gray).
python3 pdf_to_html_with_toc.py THESIS_OCR.pdf THOMAS_THESIS.html 
"""

from pathlib import Path
from html import escape

import pikepdf
from pikepdf import Pdf, Name, Array, Dictionary, String
import fitz  # PyMuPDF


# ---------- Helpers to resolve destinations to page indices ----------

def _build_page_obj_index(pdf: Pdf):
    """
    Map page indirect object IDs (obj, gen) -> zero-based page indices.
    We cannot hash pikepdf.Object directly; use page.obj.objgen as a stable key.
    """
    return {page.obj.objgen: idx for idx, page in enumerate(pdf.pages)}


def _iter_name_tree(node):
    """Yield (name, value) from a PDF name tree node (handles /Kids recursion)."""
    if Name("/Names") in node:
        names = node[Name("/Names")]
        # names is [key1, val1, key2, val2, ...]
        for i in range(0, len(names), 2):
            yield str(names[i]), names[i + 1]
    if Name("/Kids") in node:
        for kid in node[Name("/Kids")]:
            yield from _iter_name_tree(kid)


def _resolve_named_dest(pdf: Pdf, name: str):
    """Return explicit destination object for a named destination."""
    root = pdf.root
    names = root.get(Name("/Names"))
    if not names:
        return None
    dests = names.get(Name("/Dests"))
    if not dests:
        return None
    for key, val in _iter_name_tree(dests):
        if key == name:
            # val may be an array (explicit dest) or a dict containing /D
            if isinstance(val, Dictionary) and Name("/D") in val:
                return val[Name("/D")]
            return val
    return None


def _dest_to_page_index(dest, page_obj_to_index):
    """
    Convert a destination to a zero-based page index.
    Handles explicit destinations like [<page-ref>, 'Fit', ...].
    """
    if isinstance(dest, Array) and len(dest) > 0:
        page_ref = dest[0]
        # Derive a hashable lookup key (objnum, gennum)
        key = None
        try:
            if hasattr(page_ref, "objgen"):  # raw object reference
                key = page_ref.objgen
            elif hasattr(page_ref, "obj") and hasattr(page_ref.obj, "objgen"):
                key = page_ref.obj.objgen
        except Exception:
            key = None
        return page_obj_to_index.get(key, None)

    # Named destination (handled by caller via _resolve_named_dest)
    if isinstance(dest, (String, Name)):
        return None

    return None


def outline_item_to_index(pdf: Pdf, item, page_obj_to_index):
    """Best-effort: return page index (0-based) or None for an OutlineItem."""
    # 1) Explicit destination
    dest = getattr(item, "destination", None)
    if dest is not None:
        idx = _dest_to_page_index(dest, page_obj_to_index)
        if idx is not None:
            return idx
        # It might be a named destination
        if isinstance(dest, (String, Name)):
            nd = _resolve_named_dest(pdf, str(dest))
            if nd is not None:
                return _dest_to_page_index(nd, page_obj_to_index)

    # 2) Action dict with GoTo /D
    act = getattr(item, "action", None)
    if isinstance(act, Dictionary):
        if act.get(Name("/S")) == Name("/GoTo") and Name("/D") in act:
            d = act[Name("/D")]
            idx = _dest_to_page_index(d, page_obj_to_index)
            if idx is not None:
                return idx
            # Named destination embedded in /D?
            if isinstance(d, (String, Name)):
                nd = _resolve_named_dest(pdf, str(d))
                if nd is not None:
                    return _dest_to_page_index(nd, page_obj_to_index)

    # 3) Fallback via page_location.page (if available)
    pl = getattr(item, "page_location", None)
    if pl is not None:
        pg = getattr(pl, "page", None)
        if pg is not None:
            key = getattr(pg, "objgen", None)
            if key is None and hasattr(pg, "obj") and hasattr(pg.obj, "objgen"):
                key = pg.obj.objgen
            if key is not None:
                return page_obj_to_index.get(key, None)

    return None


# ---------- Extract a nested outline structure ----------

def extract_outline(pdf_path: str):
    """
    Returns a nested list of dicts:
    [
      { "title": "Section", "page": 0, "children": [...] },
      ...
    ]
    """
    with Pdf.open(pdf_path) as pdf, pdf.open_outline() as outline:
        page_obj_to_index = _build_page_obj_index(pdf)

        def walk(items):
            out = []
            for it in items:
                title = (getattr(it, "title", "") or "").strip()
                page_idx = outline_item_to_index(pdf, it, page_obj_to_index)
                children = walk(it.children) if getattr(it, "children", None) else []
                out.append({"title": title, "page": page_idx, "children": children})
            return out

        return walk(outline.root)


# ---------- Render pages to HTML with anchors ----------

def pdf_pages_to_html_with_anchors(pdf_path: str):
    """
    Returns (list_of_sections_html, page_count).
    Each item is a <section id="p{n}">...</section> for page n (1-based anchor).
    """
    doc = fitz.open(pdf_path)
    sections = []
    for i, page in enumerate(doc):
        # Extract text blocks without images
        blocks = page.get_text("blocks")  # Returns list of text blocks
        page_html = ""
        for block in blocks:
            # block[4] contains the text, block[6] is block type (0=text, 1=image)
            if block[6] == 0:  # Only process text blocks
                text = escape(block[4].strip())
                if text:
                    page_html += f'<p>{text}</p>\n'
        
        sections.append(f'<section id="p{i+1}" class="page">\n{page_html}\n</section>')
    return sections, len(doc)


# ---------- Build a nested TOC (<ul><li>...) ----------

def toc_to_html(entries):
    def li(entry):
        title = escape(entry["title"] or "")
        if entry["page"] is not None:
            href = f'#p{entry["page"]+1}'
            link = f'<a href="{href}">{title}</a>'
        else:
            link = f'<span class="unresolved">{title}</span>'
        kids = entry.get("children", [])
        ul = f'<ul>{"".join(li(k) for k in kids)}</ul>' if kids else ""
        return f'<li>{link}{ul}</li>'

    return f'<nav id="toc"><h2>Contents</h2><ul>{"".join(li(e) for e in entries)}</ul></nav>'


# ---------- Main conversion ----------

def convert(pdf_path: str, out_html: str):
    outline = extract_outline(pdf_path)
    sections, _ = pdf_pages_to_html_with_anchors(pdf_path)
    toc_html = toc_to_html(outline)

    css = """
    <style>
      :root { color-scheme: light dark; }
      body { font-family: system-ui, Arial, sans-serif; margin: 0; }
      #toc { position: sticky; top: 0; background: var(--bg, #fff);
             padding: 1rem; border-bottom: 1px solid #ddd; }
      #toc h2 { margin: 0 0 .5rem 0; font-size: 1.1rem; }
      #toc ul { list-style: none; padding-left: 1rem; }
      #toc li { margin: .2rem 0; }
      #toc a { text-decoration: none; color: #0645ad; }
      #toc a:hover { text-decoration: underline; }
      #toc .unresolved { color: #888; }
      .page { padding: 1rem; border-bottom: 1px dashed #eee; }
    </style>
    """

    html = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>{escape(Path(pdf_path).stem)}</title>
{css}
<body>
{toc_html}
{"".join(sections)}
</body>
</html>"""

    Path(out_html).write_text(html, encoding="utf-8")
    print(f"Wrote {out_html}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python pdf_to_html_with_toc.py INPUT.pdf OUTPUT.html")
        raise SystemExit(1)
    convert(sys.argv[1], sys.argv[2])