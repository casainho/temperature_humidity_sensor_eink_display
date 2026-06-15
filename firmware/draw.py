import framebuf

# Colors for a white-background e-ink display (framebuf bit=1 → white, bit=0 → black)
BLACK = 0
WHITE = 1


def draw_text(fb, font, text, x, y):
    """Render text using a font_to_py font module.

    Font glyphs store stroke pixels as bit=1.  The SSD1681 e-ink display
    represents black pixels as bit=0, so glyph bytes are XOR-inverted before
    blitting.  Returns the x position immediately after the last character.
    """
    fmt = framebuf.MONO_HMSB if font.reverse() else framebuf.MONO_HLSB
    col = x
    for ch in text:
        glyph, h, w = font.get_ch(ch)
        buf = bytearray(glyph)
        for i in range(len(buf)):
            buf[i] ^= 0xFF
        glyph_fb = framebuf.FrameBuffer(buf, w, h, fmt)
        fb.blit(glyph_fb, col, y)
        col += w
    return col


def text_width(font, text):
    """Return the pixel width of a string in the given font."""
    w = 0
    for ch in text:
        _, _, cw = font.get_ch(ch)
        w += cw
    return w


def draw_graph(fb, x, y, w, h, data, y_min, y_max, fill=True, x_steps=None):
    """Draw a filled line graph inside a bordered box at (x, y, w, h)."""
    fb.rect(x, y, w, h, BLACK)

    if not data or len(data) < 2:
        return

    y_range = float(y_max - y_min) or 1.0
    bottom = y + h - 1
    x_steps = max(1, x_steps if x_steps is not None else len(data) - 1)

    def to_px(i, val):
        px = x + 1 + (i * (w - 2)) // x_steps
        py = bottom - int((val - y_min) * (h - 2) / y_range)
        return px, max(y + 1, min(bottom, py))

    pts = [to_px(i, v) for i, v in enumerate(data)]

    if fill:
        for i in range(1, len(pts)):
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            for xi in range(x0, x1 + 1):
                yi = y0 if x0 == x1 else y0 + (y1 - y0) * (xi - x0) // (x1 - x0)
                yi = max(y + 1, min(bottom, yi))
                if bottom > yi:
                    fb.vline(xi, yi, bottom - yi, BLACK)

    for i in range(1, len(pts)):
        fb.line(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], BLACK)
