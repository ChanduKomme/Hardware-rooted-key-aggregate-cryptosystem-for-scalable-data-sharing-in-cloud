# text_oled_viewer.py
import curses, textwrap, os, time
from hardware_io import Image, ImageDraw, ImageFont, oled

# monospace fits best on 128x64
try:
    _font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
except Exception:
    _font = ImageFont.load_default()

_COLS = 21
_LINES_PER_PAGE = 5  # 5 * 12px ≈ 60px usable

def _render_page(lines, start, title=None):
    img = Image.new("1", (oled.width, oled.height))
    d = ImageDraw.Draw(img)
    y = 0
    if title:
        d.text((0, y), title[:_COLS], font=_font, fill=255)
        y += 12
    page = lines[start:start+_LINES_PER_PAGE]
    for ln in page:
        d.text((0, y), ln, font=_font, fill=255)
        y += 12
    total = len(lines)
    footer = f"{start+1}-{min(start+_LINES_PER_PAGE,total)}/{total}"
    d.rectangle((0, oled.height-12, oled.width, oled.height), fill=0)
    d.text((0, oled.height-12), footer, font=_font, fill=255)
    oled.display(img)

def _flash(msg, title=None):
    img = Image.new("1", (oled.width, oled.height))
    d = ImageDraw.Draw(img)
    y = 0
    if title:
        d.text((0, y), title[:_COLS], font=_font, fill=255)
        y += 12
    d.text((0, y), msg[:_COLS], font=_font, fill=255)
    oled.display(img)
    time.sleep(1)

def _wrap_text(s):
    out = []
    for para in s.splitlines() or [""]:
        wrapped = textwrap.wrap(
            para, width=_COLS,
            replace_whitespace=False, drop_whitespace=False,
            break_long_words=True, break_on_hyphens=False
        )
        out.extend(wrapped if wrapped else [""])
    return out or [""]

def view_text_on_oled(text: str, title: str = "Decrypted", export_path: str | None = None):
    lines = _wrap_text(text)
    start = 0
    max_start = max(0, len(lines) - _LINES_PER_PAGE)

    if not export_path:
        safe_title = "".join(c for c in (title or "text") if c.isalnum() or c in ("-", "_", "."))
        export_dir = os.path.join(os.path.dirname(__file__), "oled_exports")
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"{safe_title}.txt")

    def main(stdscr):
        nonlocal start, max_start
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.keypad(True)
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
        except Exception:
            pass

        def clamp():
            nonlocal start, max_start
            if start < 0: start = 0
            if start > max_start: start = max_start

        _render_page(lines, start, title)
        while True:
            ch = stdscr.getch()
            if ch in (ord('q'), 27): break
            elif ch in (curses.KEY_DOWN, ord('j')): start += 1
            elif ch in (curses.KEY_UP,   ord('k')): start -= 1
            elif ch == curses.KEY_NPAGE: start += _LINES_PER_PAGE
            elif ch == curses.KEY_PPAGE: start -= _LINES_PER_PAGE
            elif ch == curses.KEY_HOME:  start  = 0
            elif ch == curses.KEY_END:   start  = max_start
            elif ch == ord('s'):
                try:
                    with open(export_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    _flash(f"Saved: {os.path.basename(export_path)}", title)
                except Exception:
                    _flash("Save err", title)
            elif ch == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, b = curses.getmouse()
                    if b & 0x800000: start += 1   # wheel down
                    if b & 0x80000:  start -= 1   # wheel up
                except Exception:
                    pass
            clamp()
            _render_page(lines, start, title)

    curses.wrapper(main)
