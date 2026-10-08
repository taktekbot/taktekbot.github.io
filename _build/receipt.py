"""The receipt: /open's numbers printed as a shop receipt, as PNGs for sharing.

    python3 _build/receipt.py [open.json] [outdir]

Reads assets/open.json (the same file /open/ is built from, so the receipt never says anything the page
doesn't) and writes open/receipt.png (1080x1350, for posts) and open/receipt-og.png (1200x630, the page's
share image). Needs Pillow; build.py skips the receipt if Pillow is missing. Font: $RECEIPT_FONT, else
JetBrains Mono from the brand repo, else Menlo.
"""
import datetime as dt, json, os, sys
from pathlib import Path

FONTS = [os.environ.get("RECEIPT_FONT", ""),
         str(Path.home() / "work/taktekhq/brand/taktek/type/fonts/jetbrains-mono/JetBrainsMono-Regular.ttf"),
         "/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
BOLD = [os.environ.get("RECEIPT_FONT_BOLD", ""),
        str(Path.home() / "work/taktekhq/brand/taktek/type/fonts/jetbrains-mono/JetBrainsMono-Bold.ttf")] + FONTS[2:]
START = dt.date(2026, 10, 8)   # the day the first-dollar goal was set: receipt #1
PAPER, INK, FAINT, BG = (250, 248, 240), (24, 24, 24), (120, 118, 110), (17, 17, 17)


def font(paths, size):
    from PIL import ImageFont
    for p in paths:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def lines(d):
    """The receipt's rows: (left, right, style). Everything comes from open.json."""
    day = dt.date.fromisoformat(d["generated_at"][:10])
    burn, rev = d["burn_monthly_usd"], d["revenue_lifetime_usd"]
    w = d["week"]
    rows = [("TAKTEK AGENT FLEET", "", "head"), ("taktekbot.com/open", "", "centre"),
            (f"RECEIPT #{(day - START).days + 1:03d}", day.strftime("%d %b %Y").upper(), "plain"), ("", "", "rule")]
    rows += [(c["name"].upper(), f'{c["usd"]:,.2f}', "plain") for c in d["categories"]]
    rows += [("", "", "rule"), ("COSTS / MONTH", f"{burn:,.2f}", "bold"),
             ("PAID BY CUSTOMERS", f"{rev:,.2f}", "bold"),
             ("BALANCE", f"{rev - burn:,.2f}", "big"), ("", "", "rule"),
             ("PROPOSALS SENT THIS WEEK", f'{w["proposals_sent"]:,}', "plain"),
             ("REPLIES", f'{w["replies"]:,}', "plain"),
             ("DAYS LEFT TO 31 OCT", f'{d["days_left"]}', "plain"), ("", "", "rule")]
    rows.append(("NO REFUNDS. NO REVENUE EITHER." if rev == 0 else "FIRST DOLLAR: RECEIVED.", "", "centre"))
    rows.append(("THANK YOU FOR WATCHING", "", "centre"))
    return rows


def draw_receipt(d, width):
    """The paper itself, `width` px wide, as tall as its rows need."""
    from PIL import Image, ImageDraw
    s = width / 640
    f, fb, fh = font(FONTS, int(22 * s)), font(BOLD, int(22 * s)), font(BOLD, int(34 * s))
    pad, step = int(40 * s), int(38 * s)
    rows = lines(d)
    h = pad * 2 + sum(int(step * (1.6 if st in ("head", "big") else 1)) for *_, st in rows) + int(90 * s)
    img = Image.new("RGB", (width, h), PAPER)
    g = ImageDraw.Draw(img)
    y = pad
    for left, right, st in rows:
        ft = fh if st in ("head", "big") else fb if st == "bold" else f
        if st == "rule":
            for x in range(pad, width - pad, int(14 * s)):
                g.text((x, y), "-", font=f, fill=FAINT)
        elif st in ("head", "centre"):
            g.text((width / 2, y), left, font=ft, fill=INK if st == "head" else FAINT, anchor="ma")
        else:
            g.text((pad, y), left, font=ft, fill=INK)
            g.text((width - pad, y), right, font=ft, fill=INK, anchor="ra")
        y += int(step * (1.6 if st in ("head", "big") else 1))
    # a barcode that encodes nothing but looks the part: bar widths from the balance's digits
    bx, digits = pad, "".join(ch for ch in f'{d["burn_monthly_usd"]:.2f}{d["days_left"]}' if ch.isdigit()) * 6
    for i, ch in enumerate(digits):
        bw = max(1, int((int(ch) % 3 + 1) * 2 * s))
        if i % 2 == 0:
            g.rectangle([bx, y + int(10 * s), bx + bw, y + int(70 * s)], fill=INK)
        bx += bw + max(2, int(2 * s))
        if bx > width - pad:
            break
    # torn edges, top and bottom
    tooth = int(16 * s)
    for x in range(0, width + tooth, tooth):
        g.polygon([(x, 0), (x + tooth / 2, tooth / 2), (x + tooth, 0)], fill=BG)
        g.polygon([(x, h), (x + tooth / 2, h - tooth / 2), (x + tooth, h)], fill=BG)
    return img


def render(d, size, rotate=-2.5):
    from PIL import Image
    W, H = size
    paper = draw_receipt(d, int(min(W * 0.62, H * 0.9 * 0.55)) if W > H else int(W * 0.72))
    if paper.height > H * 0.94:
        k = H * 0.94 / paper.height
        paper = paper.resize((int(paper.width * k), int(paper.height * k)), Image.LANCZOS)
    paper = paper.convert("RGBA").rotate(rotate, expand=True, resample=Image.BICUBIC)
    out = Image.new("RGB", (W, H), BG)
    out.paste(paper, ((W - paper.width) // 2, (H - paper.height) // 2), paper)
    return out


def render_og(d, size=(1200, 630)):
    """The share card: the receipt down the left, the three numbers that matter on the right."""
    from PIL import Image, ImageDraw
    W, H = size
    paper = draw_receipt(d, 640)
    k = H * 0.92 / paper.height
    paper = paper.resize((int(paper.width * k), int(paper.height * k)), Image.LANCZOS)
    out = Image.new("RGB", (W, H), BG)
    out.paste(paper, (60, (H - paper.height) // 2))
    g = ImageDraw.Draw(out)
    x, y = 60 + paper.width + 60, 120
    rev, burn = d["revenue_lifetime_usd"], d["burn_monthly_usd"]
    for text, size_, colour in ((f"${rev:,.2f} earned", 54, PAPER), (f"${burn:,.2f}/mo to run", 40, PAPER),
                                (f'{d["days_left"]} days left to 31 Oct', 40, PAPER), ("", 30, FAINT),
                                ("An AI agent fleet's", 30, FAINT), ("real numbers:", 30, FAINT),
                                ("taktekbot.com/open", 30, FAINT)):
        g.text((x, y), text, font=font(BOLD if size_ > 40 else FONTS, size_), fill=colour)
        y += int(size_ * 1.45)
    return out


def main(src, outdir):
    d = json.loads(Path(src).read_text())
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    render(d, (1080, 1350)).save(outdir / "receipt.png", optimize=True)
    render_og(d).save(outdir / "receipt-og.png", optimize=True)
    return outdir / "receipt.png"


if __name__ == "__main__":
    site = Path(__file__).resolve().parent.parent
    print(main(sys.argv[1] if len(sys.argv) > 1 else site / "assets/open.json",
               sys.argv[2] if len(sys.argv) > 2 else site / "open"))
