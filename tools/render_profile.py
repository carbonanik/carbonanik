"""Render GitHub profile artwork: python3 tools/render_profile.py (requires Pillow)."""
from html import escape
from colorsys import rgb_to_hls
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    'dark': dict(bg='#0d1117', panel='#161b22', border='#30363d', text='#e6edf3', muted='#8b949e', accent='#79c0ff', value='#a5d6ff', green='#7ee787'),
    'light': dict(bg='#ffffff', panel='#f6f8fa', border='#d0d7de', text='#24292f', muted='#57606a', accent='#0969da', value='#0550ae', green='#1a7f37'),
}
PORTRAIT_PALETTES = {
    # Three warm skin/shadow tones and two greens from the portrait's rim light.
    'dark': ('#8c6b53', '#c3936b', '#e5bc94', '#75834c', '#bdd46b'),
    'light': ('#594637', '#a06d48', '#b47c52', '#56642f', '#768c35'),
}
# Sclera cells on the 80-column portrait grid; leave the neighboring pupils dark.
EYE_WHITES = {(26, 16), (38, 16)}

def text(x, y, value, color, size=14, extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" {extra}>{escape(value)}</text>'

def svg(width, height, title, description, elements):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">\n'
        f'<title id="title">{escape(title)}</title>\n<desc id="desc">{escape(description)}</desc>\n'
        '<g font-family="DejaVu Sans Mono, Consolas, monospace">\n'
        + '\n'.join(elements) + '\n</g>\n</svg>\n'
    )

def portrait_rows():
    # Encode brightness as glyph density. The dark backdrop becomes whitespace.
    # The SVG needs no embedded raster image, external font, or script.
    with Image.open(ROOT / 'anik-portrait-color.webp') as portrait:
        # Frame the face and shoulders so the portrait stays legible at README size.
        width, height = portrait.size
        portrait = portrait.crop((width * .17, height * .08, width * .90, height * .81))
        colors = portrait.convert('RGB').resize((80, 50), Image.Resampling.LANCZOS)
        gray = ImageOps.autocontrast(portrait.convert('L'))
        gray = gray.resize((80, 50), Image.Resampling.LANCZOS)
    ramp = ' .,:;irsXA253hMHGS#9B&@'
    def glyph(pixel):
        brightness = max(0, pixel - 40) / 215
        return ramp[round(brightness ** 0.6 * (len(ramp) - 1))]
    return [[(glyph(gray.getpixel((x, y))), colors.getpixel((x, y))) for x in range(80)] for y in range(50)]

def portrait_color(rgb, theme, column=None, row=None):
    if (column, row) in EYE_WHITES:
        return '#ffffff'
    # Use five flat portrait colors plus white for the eyes.
    hue, lightness, saturation = rgb_to_hls(*(channel / 255 for channel in rgb))
    palette = PORTRAIT_PALETTES[theme]
    if .17 <= hue <= .46 and saturation > .12:
        return palette[3 if lightness < .35 else 4]
    return palette[0 if lightness < .28 else 1 if lightness < .50 else 2]

def profile(theme, rows):
    c = THEMES[theme]
    elements = [
        f'<rect x="0.5" y="0.5" width="1079" height="579" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<path d="M1 48H1079" stroke="{c["border"]}"/>',
    ]
    for x, color in [(24, '#ff5f57'), (44, '#febc2e'), (64, '#28c840')]:
        elements.append(f'<circle cx="{x}" cy="25" r="5" fill="{color}"/>')
    elements += [text(92, 30, 'carbonanik / README.md', c['muted'], 12), text(1038, 30, '~/', c['accent'], 12)]
    for i, row in enumerate(rows):
        # Position each colored glyph on the original monospace grid.
        glyphs = ''.join(
            f'<tspan x="{28 + column * 4.997:.3f}" fill="{portrait_color(rgb, theme, column, i)}"'
            + (' stroke="#594637" stroke-width="0.25" paint-order="stroke"' if (column, i) in EYE_WHITES else '')
            + f'>{escape(char)}</tspan>'
            for column, (char, rgb) in enumerate(row) if char != ' '
        )
        elements.append(f'<text y="{77 + i * 8.5}" font-size="8.3">{glyphs}</text>')
    elements += [
        text(225, 533, 'ANIK', c['text'], 17, 'text-anchor="middle" font-weight="bold" letter-spacing="5"'),
        text(225, 554, 'build software that solves real problems', c['muted'], 10, 'text-anchor="middle"'),
        text(462, 86, 'anik@carbonanik', c['accent'], 19, 'font-weight="bold"'),
        text(462, 107, '────────────────────────────────────────────────────────', c['border'], 16),
    ]
    for y, key, value in [
        (134, 'Name', 'Anik'),
        (156, 'Location', 'Bangladesh'),
        (178, 'Role', 'Flutter & Backend Developer'),
        (200, 'OS', 'Fedora Linux'),
        (222, 'Editors', 'VS Code, Android Studio'),
        (266, 'Languages', 'Dart, Python, Kotlin, SQL'),
        (288, 'Mobile', 'Flutter, Jetpack Compose'),
        (310, 'Backend', 'FastAPI, Flask, REST APIs'),
        (332, 'Data', 'PostgreSQL, SQLite, Firebase, Hive'),
        (354, 'State', 'Riverpod, BLoC, Provider'),
        (376, 'Tools', 'Git, Docker, GitHub Actions'),
        (420, 'Building', 'SaaS products & Flutter apps'),
        (442, 'Projects', 'School SaaS, logic circuits, chat'),
        (464, 'Interests', 'AI, automation, developer tools'),
        (486, 'Learning', 'System design, DevOps, Kubernetes'),
        (508, 'Portfolio', 'carbonanik.web.app'),
    ]:
        elements += [text(462, y, key, c['accent']), text(606, y, ':', c['muted']), text(626, y, value, c['value'])]
    elements += [text(462, 550, '$ keep building', c['green']), f'<rect x="599" y="538" width="8" height="15" fill="{c["green"]}"/>']
    return svg(1080, 580, 'Anik | Flutter & Backend Developer', 'An ASCII portrait of Anik alongside a terminal-style overview of his skills, projects, and interests.', elements)

def link_card(theme, label, value, command):
    c = THEMES[theme]
    return svg(532, 90, label, value, [
        f'<rect x="0.5" y="0.5" width="531" height="89" rx="10" fill="{c["panel"]}" stroke="{c["border"]}"/>',
        text(23, 34, '$', c['green'], 17), text(45, 34, command, c['text'], 15),
        text(23, 63, value, c['muted'], 12), text(493, 49, '↗', c['accent'], 24),
    ])

if __name__ == '__main__':
    assets = ROOT / 'assets'
    assets.mkdir(exist_ok=True)
    rows = portrait_rows()
    for theme in THEMES:
        (assets / f'profile-{theme}.svg').write_text(profile(theme, rows), encoding='utf-8')
        for name, label, value, command in [
            ('portfolio', 'Visit my portfolio', 'carbonanik.web.app', 'open portfolio'),
            ('projects', 'Explore my projects', 'github.com/carbonanik', 'ls projects'),
        ]:
            (assets / f'{name}-{theme}.svg').write_text(link_card(theme, label, value, command), encoding='utf-8')
    print('Rendered six profile SVGs in assets/.')
