#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import math
import html

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

INK = "#13282A"
INK2 = "#203A35"
MUTED = "#66736A"
GREEN = "#0A7A43"
LIME = "#82E35B"
LIME2 = "#B9F28F"
PALE = "#EEF5E8"
PAPER = "#F8FAF4"
WHITE = "#FEFFF9"
LINE = "#D7E0D1"
SHADOW = (47, 78, 58, 45)

FONT_REG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
FONT_MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    w, h = size
    a = hex_rgba(top)
    b = hex_rgba(bottom)
    im = Image.new("RGBA", size)
    px = im.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(4))
        for x in range(w):
            px[x, y] = c
    return im


def radial_gradient(size: tuple[int, int], inner: str, outer: str, center=(0.35, 0.25)) -> Image.Image:
    w, h = size
    a, b = hex_rgba(inner), hex_rgba(outer)
    cx, cy = w * center[0], h * center[1]
    maxd = math.hypot(max(cx, w - cx), max(cy, h - cy))
    im = Image.new("RGBA", size)
    px = im.load()
    for y in range(h):
        for x in range(w):
            t = min(1.0, math.hypot(x - cx, y - cy) / maxd)
            t = t * t * (3 - 2 * t)
            px[x, y] = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(4))
    return im


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return m


def add_glass_card(base: Image.Image, box, radius=24, fill=(255, 255, 250, 228), border=(210, 224, 205, 255), shadow=SHADOW, blur=18, offset=(0, 10)):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sd.rounded_rectangle((x1 + offset[0], y1 + offset[1], x2 + offset[0], y2 + offset[1]), radius=radius, fill=shadow)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(shadow_layer)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=border, width=1)
    # top highlight
    d.arc((x1 + 2, y1 + 2, x2 - 2, y2 - 2), 190, 350, fill=(255, 255, 255, 190), width=2)


def draw_centered(draw: ImageDraw.ImageDraw, xy, text, fnt, fill, anchor="mm"):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def fit_text(draw, text, max_width, font_path, start_size, min_size=12):
    size = start_size
    while size > min_size:
        fnt = font(font_path, size)
        if draw.textbbox((0, 0), text, font=fnt)[2] <= max_width:
            return fnt
        size -= 1
    return font(font_path, min_size)


def draw_omnitrix_orb(base: Image.Image, cx: int, cy: int, r: int, glow=True):
    if glow:
        g = Image.new("RGBA", base.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.ellipse((cx-r*1.45, cy-r*1.45, cx+r*1.45, cy+r*1.45), fill=(88, 225, 82, 75))
        base.alpha_composite(g.filter(ImageFilter.GaussianBlur(max(8, r // 2))))
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((cx-r, cy-r+10, cx+r, cy+r+10), fill=(12, 49, 33, 80))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(max(4, r // 6))))

    # metallic rings
    outer = radial_gradient((2*r, 2*r), "#F9FFF3", "#5B7361", (0.28, 0.18))
    outer.putalpha(rounded_mask((2*r, 2*r), r))
    base.alpha_composite(outer, (cx-r, cy-r))
    d = ImageDraw.Draw(base)
    d.ellipse((cx-r+4, cy-r+4, cx+r-4, cy+r-4), outline=(25, 74, 50, 230), width=max(2, r//18))
    d.ellipse((cx-r*0.76, cy-r*0.76, cx+r*0.76, cy+r*0.76), fill=hex_rgba(INK), outline=(164, 234, 144, 255), width=max(2, r//16))
    # hourglass
    rr = r * 0.52
    pts = [
        (cx-rr, cy-rr), (cx+rr, cy-rr), (cx+rr*0.28, cy),
        (cx+rr, cy+rr), (cx-rr, cy+rr), (cx-rr*0.28, cy)
    ]
    d.polygon(pts, fill=hex_rgba(LIME))
    d.line(pts + [pts[0]], fill=(190, 255, 164, 255), width=max(1, r//24), joint="curve")
    d.arc((cx-r*0.82, cy-r*0.82, cx+r*0.82, cy+r*0.82), 205, 320, fill=(255,255,255,170), width=max(2, r//16))


def logo_orb(base: Image.Image, cx: int, cy: int, r: int, kind: str):
    # Glow and 3D shell
    glow_color = {
        "salesforce": (70, 174, 255, 75),
        "tenstorrent": (70, 90, 92, 65),
        "microsoft": (106, 179, 255, 70),
    }[kind]
    g = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.ellipse((cx-r*1.35, cy-r*1.35, cx+r*1.35, cy+r*1.35), fill=glow_color)
    base.alpha_composite(g.filter(ImageFilter.GaussianBlur(r//2)))

    shell = radial_gradient((2*r, 2*r), "#FFFFFF", "#9FB0A3", (0.28, 0.2))
    shell.putalpha(rounded_mask((2*r, 2*r), r))
    base.alpha_composite(shell, (cx-r, cy-r))
    d = ImageDraw.Draw(base)
    d.ellipse((cx-r+5, cy-r+5, cx+r-5, cy+r-5), outline=(52, 80, 62, 150), width=2)
    inner_r = int(r*0.78)

    if kind == "salesforce":
        inner = radial_gradient((2*inner_r, 2*inner_r), "#54C4FF", "#0477C8", (0.28, 0.18))
        inner.putalpha(rounded_mask((2*inner_r, 2*inner_r), inner_r))
        base.alpha_composite(inner, (cx-inner_r, cy-inner_r))
        dd = ImageDraw.Draw(base)
        # cloud cluster
        blue = (0, 161, 224, 255)
        for dx, dy, rr in [(-28, 4, 24), (-4, -10, 31), (27, 1, 26), (2, 14, 35)]:
            dd.ellipse((cx+dx-rr, cy+dy-rr, cx+dx+rr, cy+dy+rr), fill=blue)
        draw_centered(dd, (cx, cy+4), "salesforce", font(FONT_BOLD, max(10, r//4)), (255,255,255,255))
    elif kind == "tenstorrent":
        inner = radial_gradient((2*inner_r, 2*inner_r), "#34434A", "#090E11", (0.3,0.2))
        inner.putalpha(rounded_mask((2*inner_r,2*inner_r),inner_r))
        base.alpha_composite(inner,(cx-inner_r,cy-inner_r))
        dd = ImageDraw.Draw(base)
        # angular TT-inspired monogram
        w = r*0.82
        dd.polygon([(cx-w*.65,cy-w*.42),(cx-w*.08,cy-w*.42),(cx-w*.08,cy-w*.12),(cx-w*.32,cy+w*.46),(cx-w*.72,cy+w*.10),(cx-w*.45,cy-w*.02)], fill=(246,248,246,255))
        dd.polygon([(cx+w*.65,cy-w*.42),(cx+w*.08,cy-w*.42),(cx+w*.08,cy-w*.12),(cx+w*.32,cy+w*.46),(cx+w*.72,cy+w*.10),(cx+w*.45,cy-w*.02)], fill=(183,198,194,255))
        dd.ellipse((cx-7, cy-7, cx+7, cy+7), fill=hex_rgba(LIME))
    elif kind == "microsoft":
        inner = radial_gradient((2*inner_r, 2*inner_r), "#FBFCFD", "#DDE5E7", (0.3,0.2))
        inner.putalpha(rounded_mask((2*inner_r,2*inner_r),inner_r))
        base.alpha_composite(inner,(cx-inner_r,cy-inner_r))
        dd=ImageDraw.Draw(base)
        s=int(r*.43); gap=int(r*.07)
        x0=cx-s-gap//2; y0=cy-s-gap//2
        colors=[(242,80,34,255),(127,186,0,255),(0,164,239,255),(255,185,0,255)]
        dd.rectangle((x0,y0,x0+s-gap,y0+s-gap),fill=colors[0])
        dd.rectangle((cx+gap//2,y0,cx+s+gap//2,y0+s-gap),fill=colors[1])
        dd.rectangle((x0,cy+gap//2,x0+s-gap,cy+s+gap//2),fill=colors[2])
        dd.rectangle((cx+gap//2,cy+gap//2,cx+s+gap//2,cy+s+gap//2),fill=colors[3])
    # highlight
    d.arc((cx-r+8,cy-r+8,cx+r-8,cy+r-8),205,320,fill=(255,255,255,180),width=max(2,r//15))


def draw_bg_pattern(base: Image.Image):
    d = ImageDraw.Draw(base)
    w,h=base.size
    # faint circuit arcs
    for offset in (0, 180, 360):
        d.arc((w-420-offset//2,-160+offset//3,w+200-offset//2,460+offset//3),180,300,fill=(95,150,95,25),width=2)
    for x in range(40,w,120):
        d.ellipse((x,h-34,x+4,h-30),fill=(86,180,92,40))


def build_forms():
    W,H=1200,500
    base=vertical_gradient((W,H),"#F9FBF6","#EDF4E8")
    draw_bg_pattern(base)
    d=ImageDraw.Draw(base)
    d.text((42,35),"OMNITRIX LOADOUT",font=font(FONT_BOLD,15),fill=hex_rgba(GREEN))
    d.text((40,65),"Different strengths. One mission.",font=font(FONT_BOLD,42),fill=hex_rgba(INK))
    d.text((42,116),"Systems precision, AI reasoning, and builder energy — three ways I approach engineering.",font=font(FONT_REG,18),fill=hex_rgba(MUTED))
    draw_omnitrix_orb(base,1115,70,36,True)
    # source cards only
    src=Image.open(ASSETS/"alien-forms-source.webp").convert("RGBA").crop((0,136,1200,410))
    src=src.resize((1128,258),Image.Resampling.LANCZOS)
    panel=Image.new("RGBA",(1160,292),(0,0,0,0))
    add_glass_card(panel,(0,0,1159,291),radius=26,fill=(255,255,250,235),border=(208,224,201,255),shadow=(30,68,42,55),blur=20,offset=(0,10))
    # add source inside with rounded mask
    mask=rounded_mask(src.size,20)
    panel.alpha_composite(Image.composite(src,Image.new("RGBA",src.size,(0,0,0,0)),mask),(16,16))
    base.alpha_composite(panel,(20,174))
    # green light under panel
    glow=Image.new("RGBA",base.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.rounded_rectangle((240,466,960,478),radius=7,fill=(92,224,82,80))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    base.convert("RGB").save(ASSETS/"forms-console.webp","WEBP",quality=93,method=6)


def build_experience(horizontal=True):
    W,H=(1200,480) if horizontal else (640,1235)
    base=vertical_gradient((W,H),"#FAFCF7","#ECF4E8")
    draw_bg_pattern(base)
    d=ImageDraw.Draw(base)
    if horizontal:
        d.text((38,28),"FIELD LOG / EXPERIENCE",font=font(FONT_BOLD,15),fill=hex_rgba(GREEN))
        d.text((38,57),"Three teams. One engineering path.",font=font(FONT_BOLD,35),fill=hex_rgba(INK))
        d.text((40,99),"Enterprise platforms, AI acceleration, and developer-facing products.",font=font(FONT_REG,17),fill=hex_rgba(MUTED))
        draw_omnitrix_orb(base,1138,66,30)
        cards=[(28,132,384,452),(422,132,778,452),(816,132,1172,452)]
    else:
        d.text((28,24),"FIELD LOG / EXPERIENCE",font=font(FONT_BOLD,14),fill=hex_rgba(GREEN))
        d.text((28,52),"Three teams. One path.",font=font(FONT_BOLD,31),fill=hex_rgba(INK))
        d.text((28,91),"A compact record of where I built and learned.",font=font(FONT_REG,16),fill=hex_rgba(MUTED))
        draw_omnitrix_orb(base,578,58,28)
        cards=[(24,128,616,464),(24,500,616,836),(24,872,616,1219)]
    data=[
        ("NOW","Salesforce","Associate Member of Technical Staff",["Enterprise software","Salesforce Platform"],"Bengaluru, India","salesforce","MODE 01"),
        ("PREVIOUSLY","Tenstorrent","AI Intern",["AI acceleration","TT-Metalium"],"","tenstorrent","MODE 02"),
        ("MAY — JUL 2025","Microsoft","Software Engineer Intern",["SharePoint Embedded","Office Document Services & Platforms"],"Hyderabad, India","microsoft","MODE 03"),
    ]
    for i,(box,item) in enumerate(zip(cards,data)):
        x1,y1,x2,y2=box; tag,company,role,focus,loc,kind,mode=item
        add_glass_card(base,box,radius=25,fill=(255,255,252,237) if i!=1 else (244,249,240,242),border=(207,222,201,255),shadow=(36,74,48,54),blur=16,offset=(0,9))
        dd=ImageDraw.Draw(base)
        dd.rounded_rectangle((x1+12,y1+16,x1+18,y2-16),radius=3,fill=(95,219,84,255))
        orb_r=49 if horizontal else 58
        logo_orb(base,x1+78 if horizontal else x1+92,y1+75 if horizontal else y1+88,orb_r,kind)
        # status chip
        chip_text=tag
        fchip=font(FONT_BOLD,11 if horizontal else 12)
        bbox=dd.textbbox((0,0),chip_text,font=fchip)
        cw=bbox[2]-bbox[0]+24
        dd.rounded_rectangle((x2-cw-18,y1+18,x2-18,y1+46),radius=14,fill=(233,244,226,255),outline=(195,216,187,255))
        dd.text((x2-cw//2-18,y1+32),chip_text,font=fchip,fill=hex_rgba(GREEN),anchor="mm")
        tx=x1+32
        title_y=y1+142 if horizontal else y1+155
        dd.text((tx,title_y),company,font=font(FONT_BOLD,29 if horizontal else 34),fill=hex_rgba(INK))
        role_font=fit_text(dd,role,x2-x1-64,FONT_SEMI,18 if horizontal else 21,14)
        dd.text((tx,title_y+42),role,font=role_font,fill=hex_rgba(INK2))
        fy=title_y+75
        for line in focus:
            dd.text((tx,fy),line,font=font(FONT_REG,15 if horizontal else 18),fill=hex_rgba(MUTED))
            fy+=23 if horizontal else 27
        if loc:
            dd.ellipse((tx, y2-43, tx+8,y2-35),fill=hex_rgba(GREEN))
            dd.text((tx+16,y2-46),loc,font=font(FONT_MED,13 if horizontal else 15),fill=hex_rgba(MUTED))
        dd.text((x2-24,y2-39),mode,font=font(FONT_BOLD,11),fill=hex_rgba(GREEN),anchor="ra")
    name="experience-console.webp" if horizontal else "experience-console-mobile.webp"
    base.convert("RGB").save(ASSETS/name,"WEBP",quality=93,method=6)


def tile_icon(draw, box, label, bg, fg=(255,255,255,255), shape="round"):
    x1,y1,x2,y2=box
    if shape=="hex":
        cx=(x1+x2)/2; cy=(y1+y2)/2; r=(x2-x1)/2
        pts=[(cx+r*math.cos(math.pi/3*k+math.pi/6),cy+r*math.sin(math.pi/3*k+math.pi/6)) for k in range(6)]
        draw.polygon(pts,fill=bg)
    else:
        draw.rounded_rectangle(box,radius=18,fill=bg)
    f=fit_text(draw,label,x2-x1-10,FONT_BOLD,19,10)
    draw.text(((x1+x2)//2,(y1+y2)//2),label,font=f,fill=fg,anchor="mm")


def build_tech():
    W,H=1200,325
    base=vertical_gradient((W,H),"#FBFCF8","#EDF4E8")
    draw_bg_pattern(base)
    d=ImageDraw.Draw(base)
    d.text((38,30),"TECH ARSENAL",font=font(FONT_BOLD,15),fill=hex_rgba(GREEN))
    d.text((38,60),"Tools mapped to the form that uses them.",font=font(FONT_BOLD,34),fill=hex_rgba(INK))
    d.text((40,102),"Recognizable technologies, arranged as one calm interface instead of a wall of badges.",font=font(FONT_REG,17),fill=hex_rgba(MUTED))
    items=[
      ("C++","#1267A6"),("C#","#7B3BB8"),(".NET","#512BD4"),("Py","#3776AB"),("TS","#3178C6"),
      ("PT","#EE4C2C"),("TF","#FF7A00"),("CV","#3AAE4D"),("sk","#F7931E"),("Az","#0089D6"),
      ("D","#2496ED"),("git","#F05032"),("GH","#24292F")
    ]
    start_x=34; gap=10; tw=78; ty=150
    for i,(label,color) in enumerate(items):
        x=start_x+i*(tw+gap)
        add_glass_card(base,(x,ty,x+tw,ty+132),radius=19,fill=(255,255,252,235),border=(210,223,205,255),shadow=(40,72,48,32),blur=10,offset=(0,5))
        dd=ImageDraw.Draw(base)
        tile_icon(dd,(x+14,ty+15,x+tw-14,ty+75),label,hex_rgba(color),shape="round")
        names=["C++","C#",".NET","Python","TypeScript","PyTorch","TensorFlow","OpenCV","scikit-learn","Azure","Docker","Git","GitHub"]
        f=fit_text(dd,names[i],tw-10,FONT_MED,11,8)
        dd.text((x+tw/2,ty+102),names[i],font=f,fill=hex_rgba(INK2),anchor="mm")
        mode="SYS" if i<5 else "AI" if i<9 else "BUILD"
        dd.text((x+tw/2,ty+120),mode,font=font(FONT_BOLD,8),fill=hex_rgba(GREEN),anchor="mm")
    base.convert("RGB").save(ASSETS/"tech-console.webp","WEBP",quality=94,method=6)


def build_selected():
    W,H=1200,350
    base=vertical_gradient((W,H),"#FAFCF7","#ECF4E8")
    draw_bg_pattern(base)
    d=ImageDraw.Draw(base)
    entries=[
      (24,24,584,326,"VISUAL STUDIO CODE","ArrayQueue correctness","Fixed symmetrical boundary errors when consuming a queue from both ends.","Regression tests for interleaved operations.","PR #301119","vscode"),
      (616,24,1176,326,"GOOGLETEST","UTF-8 JSON output","Preserved UTF-8 bytes across signed- and unsigned-character platforms.","End-to-end regression coverage.","PR #5082","gtest")
    ]
    for x1,y1,x2,y2,org,title,body1,body2,pr,kind in entries:
        add_glass_card(base,(x1,y1,x2,y2),radius=26,fill=(255,255,252,240),border=(207,222,201,255),shadow=(35,72,46,52),blur=17,offset=(0,9))
        dd=ImageDraw.Draw(base)
        # icon orb
        cx=x1+68; cy=y1+66
        if kind=="vscode":
            g=radial_gradient((84,84),"#41B7F2","#0065A9",(0.3,0.2)); g.putalpha(rounded_mask((84,84),42)); base.alpha_composite(g,(cx-42,cy-42))
            dd.polygon([(cx-22,cy),(cx+6,cy-25),(cx+31,cy-13),(cx+31,cy+13),(cx+6,cy+25)],fill=(255,255,255,240))
            dd.polygon([(cx-22,cy),(cx+8,cy+13),(cx+8,cy-13)],fill=(5,96,160,255))
        else:
            g=radial_gradient((84,84),"#FFFFFF","#DDEAE1",(0.3,0.2)); g.putalpha(rounded_mask((84,84),42)); base.alpha_composite(g,(cx-42,cy-42))
            dd.arc((cx-25,cy-25,cx+25,cy+25),35,330,fill=(66,133,244,255),width=10)
            dd.line((cx+2,cy,cx+28,cy),fill=(52,168,83,255),width=10)
            dd.ellipse((cx-8,cy-8,cx+8,cy+8),fill=(234,67,53,255))
        dd.text((x1+126,y1+40),org,font=font(FONT_BOLD,13),fill=hex_rgba(GREEN))
        dd.text((x1+126,y1+64),title,font=font(FONT_BOLD,27),fill=hex_rgba(INK))
        dd.rounded_rectangle((x2-105,y1+28,x2-28,y1+57),radius=14,fill=(226,245,220,255),outline=(189,219,181,255))
        dd.text((x2-66,y1+43),"MERGED",font=font(FONT_BOLD,10),fill=hex_rgba(GREEN),anchor="mm")
        def wrap_lines(value, max_width, fnt):
            words=value.split(); out=[]; cur=""
            for word in words:
                test=(cur+" "+word).strip()
                if dd.textbbox((0,0),test,font=fnt)[2] <= max_width:
                    cur=test
                else:
                    if cur: out.append(cur)
                    cur=word
            if cur: out.append(cur)
            return out
        f1=font(FONT_REG,17); f2=font(FONT_REG,17)
        yy=y1+132
        for ln in wrap_lines(body1,x2-x1-72,f1)[:2]:
            dd.text((x1+36,yy),ln,font=f1,fill=hex_rgba(INK2)); yy+=24
        yy+=6
        for ln in wrap_lines(body2,x2-x1-72,f2)[:2]:
            dd.text((x1+36,yy),ln,font=f2,fill=hex_rgba(MUTED)); yy+=24
        dd.line((x1+36,y1+244,x2-36,y1+244),fill=hex_rgba(LINE),width=1)
        dd.text((x1+36,y1+282),pr,font=font(FONT_BOLD,15),fill=hex_rgba(GREEN))
        dd.text((x2-36,y1+282),"READ THE CHANGE  ↗",font=font(FONT_BOLD,12),fill=hex_rgba(INK),anchor="ra")
    base.convert("RGB").save(ASSETS/"selected-work.webp","WEBP",quality=94,method=6)


def draw_project_icon(base,cx,cy,kind):
    d=ImageDraw.Draw(base)
    g=radial_gradient((76,76),"#F8FFF2","#CDE1C7",(0.3,0.2)); g.putalpha(rounded_mask((76,76),20)); base.alpha_composite(g,(cx-38,cy-38))
    d.rounded_rectangle((cx-38,cy-38,cx+38,cy+38),radius=20,outline=(130,174,124,180),width=1)
    if kind=="code":
        d.line((cx-20,cy,cx-8,cy-12),fill=hex_rgba(GREEN),width=5)
        d.line((cx-20,cy,cx-8,cy+12),fill=hex_rgba(GREEN),width=5)
        d.line((cx+20,cy,cx+8,cy-12),fill=hex_rgba(GREEN),width=5)
        d.line((cx+20,cy,cx+8,cy+12),fill=hex_rgba(GREEN),width=5)
    elif kind=="doc":
        d.rounded_rectangle((cx-18,cy-24,cx+18,cy+24),radius=4,fill=(202,64,83,255))
        for yy in (-10,0,10): d.line((cx-10,cy+yy,cx+10,cy+yy),fill=(255,255,255,255),width=3)
    elif kind=="audio":
        for i,h in enumerate([18,28,40,24,34,16]):
            x=cx-25+i*10
            d.rounded_rectangle((x,cy-h//2,x+5,cy+h//2),radius=2,fill=(71,76,190,255))
    elif kind=="chart":
        d.line((cx-22,cy+20,cx-22,cy-20),fill=hex_rgba(GREEN),width=4)
        d.line((cx-22,cy+20,cx+24,cy+20),fill=hex_rgba(GREEN),width=4)
        d.line((cx-16,cy+12,cx-3,cy-2,cx+8,cy+4,cx+22,cy-16),fill=(116,67,179,255),width=5,joint="curve")


def build_projects():
    W,H=1200,590
    base=vertical_gradient((W,H),"#FAFCF7","#ECF4E8")
    draw_bg_pattern(base)
    d=ImageDraw.Draw(base)
    d.text((38,28),"INVENTOR LAB / FEATURED BUILDS",font=font(FONT_BOLD,15),fill=hex_rgba(GREEN))
    d.text((38,58),"Four projects. Four different problems.",font=font(FONT_BOLD,35),fill=hex_rgba(INK))
    d.text((40,101),"Production-minded tools, applied AI, language technology, and machine learning.",font=font(FONT_REG,17),fill=hex_rgba(MUTED))
    draw_omnitrix_orb(base,1137,65,30)
    data=[
      (28,136,582,344,"Codeforces MCP","Competitive-programming intelligence","Real submission data → weaknesses, roadmaps, virtual contests, and recommendations.",["TypeScript","MCP","Zod","Algorithms"],"code"),
      (618,136,1172,344,"Daily AI Research","Autonomous research scout","Finds arXiv papers, summarizes them with Gemini, and publishes structured notes.",["Python","Gemini","arXiv","Actions"],"doc"),
      (28,372,582,562,"VāNī","Universal translation workspace","Text, audio, recordings, and documents across 35+ languages.",["Python","Flask","Speech","Documents"],"audio"),
      (618,372,1172,562,"Spectral Data Prediction","ML pipeline + Streamlit interface","Random Forest, XGBoost, and stacking for spectral prediction experiments.",["Python","scikit-learn","XGBoost","Streamlit"],"chart"),
    ]
    for x1,y1,x2,y2,title,sub,body,tags,kind in data:
        add_glass_card(base,(x1,y1,x2,y2),radius=25,fill=(255,255,252,238),border=(207,222,201,255),shadow=(35,72,46,48),blur=15,offset=(0,8))
        draw_project_icon(base,x1+68,y1+64,kind)
        dd=ImageDraw.Draw(base)
        dd.text((x1+124,y1+35),title,font=fit_text(dd,title,x2-x1-150,FONT_BOLD,24,18),fill=hex_rgba(INK))
        dd.text((x1+124,y1+70),sub,font=font(FONT_MED,15),fill=hex_rgba(GREEN))
        # wrap body manually
        words=body.split(); lines=[]; cur=""
        fbody=font(FONT_REG,16)
        maxw=x2-x1-52
        for word in words:
            test=(cur+" "+word).strip()
            if dd.textbbox((0,0),test,font=fbody)[2] <= maxw:
                cur=test
            else:
                lines.append(cur); cur=word
        if cur: lines.append(cur)
        yy=y1+112
        for ln in lines[:2]:
            dd.text((x1+26,yy),ln,font=fbody,fill=hex_rgba(MUTED)); yy+=24
        tx=x1+26; ty=y2-42
        for tag in tags:
            ft=font(FONT_MED,10)
            bw=dd.textbbox((0,0),tag,font=ft)[2]+18
            dd.rounded_rectangle((tx,ty-14,tx+bw,ty+12),radius=12,fill=(237,243,234,255),outline=(216,226,211,255))
            dd.text((tx+bw/2,ty),tag,font=ft,fill=hex_rgba(INK2),anchor="mm")
            tx+=bw+7
        dd.text((x2-28,y2-29),"OPEN REPOSITORY  ↗",font=font(FONT_BOLD,11),fill=hex_rgba(GREEN),anchor="ra")
    base.convert("RGB").save(ASSETS/"featured-builds.webp","WEBP",quality=94,method=6)


def build_community():
    W,H=1200,300
    base=vertical_gradient((W,H),"#FAFCF7","#ECF4E8")
    draw_bg_pattern(base)
    d=ImageDraw.Draw(base)
    d.text((38,28),"TEAM MODE",font=font(FONT_BOLD,15),fill=hex_rgba(GREEN))
    d.text((38,58),"Build together. Grow together.",font=font(FONT_BOLD,35),fill=hex_rgba(INK))
    cards=[(28,120,386,276),(421,120,779,276),(814,120,1172,276)]
    info=[("LEADERSHIP","Co-Head, Competitive Programming","50+ students · 20+ workshops · 15+ contests","people"),
          ("MENTORSHIP","Technical Mentor","30+ students · problem solving · interviews","mentor"),
          ("EDUCATION","B.Tech, Computer Science","IIT Jammu · CGPA 8.8/10","cap")]
    for box,(tag,title,desc,kind) in zip(cards,info):
        x1,y1,x2,y2=box
        add_glass_card(base,box,radius=23,fill=(255,255,252,238),border=(207,222,201,255),shadow=(35,72,46,40),blur=13,offset=(0,7))
        dd=ImageDraw.Draw(base)
        # icon tile
        dd.rounded_rectangle((x1+20,y1+24,x1+84,y1+88),radius=18,fill=(229,242,223,255),outline=(190,215,183,255))
        cx=x1+52; cy=y1+56
        if kind=="people":
            for dx,dy,r in [(-15,-9,7),(0,-15,8),(15,-9,7)]: dd.ellipse((cx+dx-r,cy+dy-r,cx+dx+r,cy+dy+r),fill=hex_rgba(GREEN))
            dd.rounded_rectangle((cx-30,cy+2,cx+30,cy+25),radius=10,fill=hex_rgba(GREEN))
        elif kind=="mentor":
            dd.ellipse((cx-10,cy-25,cx+10,cy-5),fill=hex_rgba(GREEN))
            dd.rounded_rectangle((cx-14,cy-2,cx+14,cy+24),radius=8,fill=hex_rgba(GREEN))
            dd.arc((cx-30,cy-17,cx+30,cy+37),200,340,fill=hex_rgba(GREEN),width=4)
        else:
            dd.polygon([(cx-29,cy-8),(cx,cy-24),(cx+29,cy-8),(cx,cy+8)],fill=hex_rgba(GREEN))
            dd.rectangle((cx-18,cy+4,cx+18,cy+19),fill=hex_rgba(GREEN))
        dd.text((x1+105,y1+27),tag,font=font(FONT_BOLD,11),fill=hex_rgba(GREEN))
        dd.text((x1+105,y1+52),title,font=fit_text(dd,title,x2-x1-125,FONT_BOLD,20,15),fill=hex_rgba(INK))
        # wrap desc
        fdesc=font(FONT_REG,14); words=desc.split(); cur=""; lines=[]
        for word in words:
            test=(cur+" "+word).strip()
            if dd.textbbox((0,0),test,font=fdesc)[2] <= x2-(x1+105)-24: cur=test
            else: lines.append(cur); cur=word
        if cur: lines.append(cur)
        yy=y1+87
        for ln in lines[:2]: dd.text((x1+105,yy),ln,font=fdesc,fill=hex_rgba(MUTED)); yy+=22
        dd.text((x2-22,y2-24),"MODE ACTIVE",font=font(FONT_BOLD,9),fill=hex_rgba(GREEN),anchor="ra")
    base.convert("RGB").save(ASSETS/"community.webp","WEBP",quality=94,method=6)


def header_svg(label,title,subtitle):
    label = html.escape(label, quote=True)
    title = html.escape(title, quote=True)
    subtitle = html.escape(subtitle, quote=True)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="108" viewBox="0 0 1200 108" role="img" aria-label="{title}">
<defs>
  <linearGradient id="bg" x2="1"><stop stop-color="#F8FAF4"/><stop offset="1" stop-color="#EEF5E9"/></linearGradient>
  <radialGradient id="metal" cx="30%" cy="20%"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#6E8574"/></radialGradient>
  <filter id="s"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#35543D" flood-opacity=".18"/></filter>
</defs>
<rect x="1" y="1" width="1198" height="106" rx="24" fill="url(#bg)" stroke="#D7E0D1"/>
<g transform="translate(54 54)" filter="url(#s)">
  <circle r="34" fill="url(#metal)" stroke="#1B5236" stroke-width="2"/>
  <circle r="25" fill="#13282A" stroke="#B7F39B"/>
  <path d="M-14-15H14L4 0L14 15H-14L-4 0Z" fill="#82E35B"/>
</g>
<text x="108" y="35" font-family="Inter,Segoe UI,Arial" font-size="13" font-weight="700" letter-spacing="1.8" fill="#0A7A43">{label}</text>
<text x="107" y="72" font-family="Inter,Segoe UI,Arial" font-size="33" font-weight="700" letter-spacing="-.7" fill="#13282A">{title}</text>
<text x="1160" y="58" text-anchor="end" font-family="Inter,Segoe UI,Arial" font-size="16" fill="#66736A">{subtitle}</text>
<circle cx="1170" cy="22" r="4" fill="#82E35B"/>
</svg>'''


def build_headers():
    headers={
      "about":("01 / HUMAN FORM","About the engineer","Same human. More possibilities."),
      "forms":("02 / OMNITRIX LOADOUT","Select a form","Different strengths. One mission."),
      "tech":("03 / TOOL MATRIX","Tech arsenal","Tools chosen for the problem, not the badge wall."),
      "experience":("04 / FIELD LOG","Experience","Enterprise software, AI acceleration, and developer products."),
      "opensource":("05 / UPSTREAM SIGNAL","Open-source journey","Public work. Visible progress."),
      "selected":("06 / MERGED MISSIONS","Selected work","Small fixes. Durable impact."),
      "builds":("07 / INVENTOR LAB","Featured builds","Things I designed, automated, and shipped."),
      "community":("08 / TEAM MODE","Community & leadership","Build together. Grow together."),
      "connect":("09 / NEXT TRANSFORMATION","Connect","The next mission starts with a conversation."),
    }
    for name,args in headers.items():
        (ASSETS/f"section-{name}.svg").write_text(header_svg(*args),encoding="utf-8")


def build_status_svg():
    items=[("CURRENT FORM","SOFTWARE ENGINEER"),("CORE","SYSTEMS + AI"),("SIGNAL","OPEN SOURCE ONLINE"),("MISSION","BUILD / LEARN / SHARE")]
    cards=[]
    for i,(a,b) in enumerate(items):
        x=18+i*295
        cards.append(f'''<g transform="translate({x} 18)">
<rect width="277" height="106" rx="22" fill="#FEFFF9" fill-opacity=".91" stroke="#D5DFCF" filter="url(#shadow)"/>
<circle cx="36" cy="33" r="10" fill="#E5F7DC" stroke="#B9DAAC"/><circle cx="36" cy="33" r="4" fill="#55D451"/>
<text x="58" y="36" font-family="Inter,Segoe UI,Arial" font-size="12" font-weight="700" letter-spacing="1.2" fill="#66736A">{a}</text>
<text x="28" y="77" font-family="Inter,Segoe UI,Arial" font-size="20" font-weight="700" fill="#13282A">{b}</text>
</g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="142" viewBox="0 0 1200 142" role="img" aria-label="Omnitrix engineering status">
<defs><linearGradient id="bg" y2="1"><stop stop-color="#F9FBF6"/><stop offset="1" stop-color="#ECF4E7"/></linearGradient><filter id="shadow"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#2F5E3A" flood-opacity=".12"/></filter></defs>
<rect width="1200" height="142" rx="27" fill="url(#bg)"/>{''.join(cards)}
</svg>'''


def main():
    build_headers()
    (ASSETS/"omnitrix-status.svg").write_text(build_status_svg(),encoding="utf-8")
    build_forms()
    build_experience(True)
    build_experience(False)
    build_tech()
    build_selected()
    build_projects()
    build_community()
    print("visual assets generated")

if __name__ == "__main__":
    main()
