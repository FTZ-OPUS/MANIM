# -*- coding: utf-8 -*-
# 雷达图 2.0 —— 在 1.0 复刻版(120.6s / 23 段)基础上的全面美学升级
# 升级点:
#   背景  深空蓝渐变(中心辉光+四角暗角) + 8 团随主色呼吸的星云 + 64 颗三层光晕星点(含彩星)
#   网格  冷 slate 高亮环(外环 0.95/内环 0.5) + 六轴彩色辐条 + 网格辉光底层 + 顶部 2/4/6/8/10 刻度
#   雷达  主色填充 0.45 + 内芯提亮 + 双层辉光 + 六轴六色渐变描边(彩虹边) + 顶点四层光点
#   转场  冲击波圆环(扩散/内缩) + 颜色 morph + 数值先沉后滚; 大转场 zoom+压暗; 黑场后故障闪入(RGB 分离+故障条)
#   数字  滚轮式(odometer)连续滚动, 随 ValueTracker 丝滑跟随
#   扫描  雷达扇形扫光 5.5s/圈, 颜色跟随主色
import math
import random

import numpy as np
from manim import *

config.frame_width = 16
config.frame_height = 9
config.background_color = "#070B16"

R_RADAR = 3.54
CENTER = np.array([0.0, -0.14, 0.0])
ANG = [90, 30, -30, -90, -150, 150]
AX_NAMES = ["理论贡献", "实践贡献", "群众路线", "个人品德", "国际主义", "历史影响"]
AX_POS = [(0.02, 3.62), (4.10, 2.01), (3.97, -2.09),
          (-0.10, -4.14), (-4.05, -2.09), (-4.11, 2.03)]

# 六轴固定色(亮色系, 深底上清晰可见)
AX_COLORS = ["#4DD0E1", "#FFB74D", "#F06292", "#FFD54F", "#64B5F6", "#CE93D8"]

BG_GLOW = "#1A2547"
SLATE = "#8B9BB8"

SEGS = [
    dict(t=1.0,   c="#17B8BA", v=(4, 6, 6, 4, 4, 5)),
    dict(t=8.7,   c="#B89AF0", v=(5, 8, 8, 8, 7, 7)),
    dict(t=10.0,  c="#E868C8", v=(5, 8, 9, 8, 8, 7)),
    dict(t=13.5,  c="#E8944A", v=(5, 7, 6, 7, 10, 8)),
    dict(t=18.0,  c="#4A90D9", v=(5, 6, 8, 8, 8, 7)),
    dict(t=23.0,  c="#8F86E8", v=(8, 3, 4, 3, 4, 7)),
    dict(t=27.2,  c="#1FA8C8", v=(5, 6, 8, 8, 8, 7)),
    dict(t=32.0,  c="#D8A8C8", v=(7, 3, 5, 7, 6, 8)),
    dict(t=37.0,  c="#E07A4A", v=(8, 4, 5, 6, 5, 8)),
    dict(t=41.5,  c="#A8C840", v=(5, 7, 8, 8, 8, 7)),
    dict(t=45.5,  c="#40C878", v=(7, 6, 7, 6, 7, 7)),
    dict(t=50.5,  c="#C8C830", v=(5, 7, 8, 9, 8, 8)),
    dict(t=55.5,  c="#E878C8", v=(6, 7, 8, 8, 8, 7)),
    dict(t=60.5,  c="#30C8C0", v=(8, 7, 9, 8, 8, 8)),
    dict(t=63.0,  c="#D8A0A0", v=(4, 10, 8, 8, 6, 7), blur=True),
    dict(t=68.5,  c="#48C058", v=(7, 8, 6, 6, 10, 7)),
    dict(t=75.0,  c="#30C0B0", v=(7, 8, 7, 9, 7, 8)),
    dict(t=80.5,  c="#A88AE0", v=(9, 7, 7, 9, 8, 10)),
    dict(t=82.0,  c="#F040E0", v=(11, 5, 7, 9, 10, 11)),
    dict(t=88.0,  c="#B8C040", v=(8, 6, 6, 9, 9, 8)),
    dict(t=94.0,  c="#E04858", v=(8, 9, 6, 6, 6, 8)),
    dict(t=107.0, c="#0F7E7A", v=(10, 10, 9, 10, 9, 10), rim=True),
    dict(t=112.0, c="#B03384", v=(10, 10, 11, 10, 9, 10), rim=True),
]
GAP_START, GAP_END = 99.0, 106.6
END_T, TOTAL = 119.4, 120.6

# 段主色统一提亮 8%, 深底上更鲜活
SEGS_C = [interpolate_color(ManimColor(s["c"]), WHITE, 0.08) for s in SEGS]


def unit(a):
    r = np.radians(a)
    return np.array([math.cos(r), math.sin(r), 0.0])


def ease_in_out_cubic(t):
    # 三次缓动: 起步收尾都丝滑
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2


def fmt(v):
    return "10+" if v >= 11 else str(int(round(v)))


class RadarV2(Scene):
    def construct(self):
        self.clock = 0.0
        self.c_cur = ManimColor(SEGS_C[0])
        self.c_to = ManimColor(SEGS_C[0])
        self.ct = ValueTracker(0.0)     # 颜色 morph 进度
        self.op = ValueTracker(0.0)     # 全局透明度(黑场用)
        self.dim = ValueTracker(1.0)    # 大转场压暗系数
        self.rim = ValueTracker(0.0)    # 橙蓝描边
        self.gl = ValueTracker(0.0)     # 故障分离量
        self.tr = [ValueTracker(0.0) for _ in range(6)]

        self.build_backdrop()
        self.build_particles()
        self.build_web()
        self.build_sweep()
        self.build_radar()
        self.build_labels()
        self.build_header()

        # ---- 开场: 雷达从中心生长 ----
        self.play(self.op.animate.set_value(1.0),
                  *[self.tr[ax].animate.set_value(float(SEGS[0]["v"][ax]))
                    for ax in range(6)],
                  FadeIn(self.header),
                  run_time=0.9, rate_func=smooth)
        self.clock = 0.9

        for i in range(21):
            nxt = SEGS[i + 1]["t"] if i < 20 else GAP_START
            self.run_segment(i, SEGS[i], nxt)

        # ---- 黑场间隔(内缩冲击波) ----
        self.to(GAP_START)
        self.shockwave(SEGS_C[20], expand=False, dur=0.55)
        self.play(self.op.animate.set_value(0.0),
                  FadeOut(self.header),
                  run_time=0.9, rate_func=smooth)
        self.clock += 0.9
        self.to(GAP_END)

        # ---- 尾段(故障闪入 + 橙蓝描边) ----
        for i in (21, 22):
            nxt = SEGS[22]["t"] if i == 21 else END_T
            self.run_segment(i, SEGS[i], nxt, first_after_gap=(i == 21))

        # ---- 收尾 ----
        self.to(END_T)
        self.shockwave(ManimColor("#FFD166"), dur=0.6)
        self.play(self.op.animate.set_value(0.0),
                  FadeOut(self.header),
                  run_time=0.8, rate_func=smooth)
        self.clock += 0.8

    # ---------- 基础工具 ----------
    def eff(self):
        return self.op.get_value() * self.dim.get_value()

    def col_now(self):
        return interpolate_color(self.c_cur, self.c_to, self.ct.get_value())

    def poly_pts(self):
        return [CENTER + unit(ANG[ax]) *
                (R_RADAR * self.tr[ax].get_value() / 10)
                for ax in range(6)]

    def to(self, t):
        d = t - self.clock
        if d > 0.01:
            n = int(round(d * config.frame_rate))
            self.wait(n / config.frame_rate)
            self.clock += n / config.frame_rate
        self.clock = max(self.clock, t)

    # ---------- 背景: 中心辉光 + 四角暗角 ----------
    def build_backdrop(self):
        bg = VGroup()
        glow = VGroup()
        for k in range(72):
            r = 0.20 * (12.5 / 0.20) ** (k / 71.0)
            glow.add(Circle(radius=r, fill_color=BG_GLOW, fill_opacity=0.020,
                            stroke_width=0).move_to(CENTER))
        bg.add(glow)
        for cx, cy in [(8.6, 4.9), (-8.6, 4.9), (8.6, -4.9), (-8.6, -4.9)]:
            for k in range(14):
                r = 1.0 * (8.0 / 1.0) ** (k / 13.0)
                bg.add(Circle(radius=r, fill_color="#03040A", fill_opacity=0.055,
                              stroke_width=0).move_to([cx, cy, 0]))
        self.add(bg)

        def bg_up(m, dt):
            o = 0.25 + 0.75 * self.op.get_value()
            for c in glow:
                c.set_opacity(0.020 * o)
        glow.add_updater(bg_up)

    # ---------- 星云 + 星点 ----------
    def build_particles(self):
        rnd = random.Random(7)
        accents = ["#FFD54F", "#4DD0E1", "#F06292", "#64B5F6", "#CE93D8", "#FFB74D"]
        ps = VGroup()
        for i in range(64):
            r = rnd.uniform(0.03, 0.10)
            core = Circle(radius=r, fill_color=WHITE, fill_opacity=0.85,
                          stroke_width=0)
            halo1 = Circle(radius=r * 2.0, fill_color=WHITE,
                           fill_opacity=0.10, stroke_width=0)
            halo2 = Circle(radius=r * 3.4, fill_color=WHITE,
                           fill_opacity=0.045, stroke_width=0)
            g = VGroup(halo2, halo1, core).move_to(
                [rnd.uniform(-7.6, 7.6), rnd.uniform(-4.3, 4.3), 0])
            g.vel = np.array([rnd.uniform(-0.22, 0.22),
                              rnd.uniform(-0.13, 0.13), 0.0])
            g.op = rnd.uniform(0.3, 1.0)
            g.freq = rnd.uniform(0.5, 1.8)
            g.phase = rnd.uniform(0, 6.28)
            g.accent = accents[i % len(accents)] if i % 4 == 0 else None
            ps.add(g)
        self.particles = ps
        self.add(ps)

        haze = VGroup()
        for cx, cy, rr in [(-6.2, 3.4, 2.2), (6.4, 3.0, 1.9), (-6.8, -3.2, 2.1),
                           (6.6, -3.4, 2.0), (0.5, 4.3, 2.4), (0, -4.4, 2.2),
                           (-3.2, 0.4, 1.6), (3.4, -0.6, 1.7)]:
            blob = VGroup()
            for k in range(10):
                c = Circle(radius=rr * (0.26 + 0.098 * k), stroke_width=0,
                           fill_color=WHITE, fill_opacity=0.017)
                c.base_op = 0.017
                blob.add(c)
            blob.move_to([cx, cy, 0])
            haze.add(blob)
        self.haze = haze
        self.add(haze)

        def up(mob, dt):
            col = self.col_now()
            e = self.eff()
            t = self.time
            for p in mob:
                p.shift(p.vel * dt)
                if p.get_x() > 7.9:
                    p.set_x(-7.9)
                if p.get_x() < -7.9:
                    p.set_x(7.9)
                if p.get_y() > 4.5:
                    p.set_y(-4.5)
                if p.get_y() < -4.5:
                    p.set_y(4.5)
                osc = 0.55 + 0.45 * math.sin(t * p.freq + p.phase)
                base = ManimColor(p.accent) if p.accent \
                    else interpolate_color(col, WHITE, 0.55)
                hc = interpolate_color(base, col, 0.30) if p.accent else col
                p[2].set_color(base)
                p[2].set_opacity(p.op * osc * 0.9 * e)
                p[1].set_color(hc)
                p[1].set_opacity(0.10 * p.op * osc * e)
                p[0].set_color(hc)
                p[0].set_opacity(0.045 * p.op * osc * e)
            for blob in self.haze:
                for c in blob:
                    c.set_color(col)
                    c.set_opacity(c.base_op * e)
        ps.add_updater(up)

    # ---------- 网格: 高亮环 + 彩色辐条 + 辉光底层 ----------
    def build_web(self):
        web = VGroup()
        for lvl in range(1, 6):
            pts = [CENTER + unit(a) * (R_RADAR * lvl / 5) for a in ANG]
            poly = Polygon(*pts, stroke_color=SLATE,
                           stroke_width=2.4 if lvl == 5 else 1.5,
                           stroke_opacity=0.95 if lvl == 5 else 0.50)
            poly.base_so = 0.95 if lvl == 5 else 0.50
            web.add(poly)
        for ax, a in enumerate(ANG):
            ln = Line(CENTER, CENTER + unit(a) * R_RADAR,
                      stroke_color=AX_COLORS[ax], stroke_width=1.9,
                      stroke_opacity=0.72)
            ln.base_so = 0.72
            web.add(ln)
        self.web = web

        glow = VGroup()
        bases = []
        for m in web:
            g = m.copy()
            base = ManimColor(m.get_stroke_color())
            g.set_stroke(color=base, width=8, opacity=0.10)
            glow.add(g)
            bases.append(base)
        self.web_glow = glow
        self.web_glow_base = bases

        def web_up(m, dt):
            k = self.eff() * max(0.06, 1.0 - 0.94 * self.rim.get_value())
            for c in m:
                c.set_stroke(opacity=c.base_so * k)
            for g, base in zip(self.web_glow, self.web_glow_base):
                g.set_stroke(color=interpolate_color(base, self.col_now(), 0.45),
                             opacity=0.10 * k)
        web.add_updater(web_up)
        self.add(web)
        self.add(glow)

        # 顶部刻度 2/4/6/8(最外圈=满格, 不标数字以免压住轴标签)
        self.scale_nums = VGroup()
        for k, val in enumerate([2, 4, 6, 8]):
            t = Text(str(val), font="Menlo", weight=BOLD, font_size=17,
                     color=SLATE)
            t.move_to(CENTER + unit(90) * (R_RADAR * (k + 1) / 5) + RIGHT * 0.26)
            self.scale_nums.add(t)
        self.add(self.scale_nums)

    # ---------- 扫描扇形 ----------
    def build_sweep(self):
        wedge = Sector(radius=R_RADAR * 1.04, start_angle=-math.pi / 10,
                       angle=math.pi / 5, fill_color=WHITE, fill_opacity=0.05,
                       stroke_width=0)
        edge = Line(CENTER, CENTER + unit(18) * R_RADAR * 1.04,
                    stroke_color=WHITE, stroke_width=1.6, stroke_opacity=0.3)
        grp = VGroup(wedge, edge).move_to(CENTER)
        self.sweep = grp
        self.add(grp)

        def sweep_up(m, dt):
            col = self.col_now()
            e = self.eff()
            m[0].set_fill(color=col, opacity=0.055 * e)
            m[1].set_stroke(color=interpolate_color(col, WHITE, 0.35),
                            width=1.6, opacity=0.32 * e)
            m.rotate(TAU * dt / 5.5, about_point=CENTER)
        grp.add_updater(sweep_up)

    # ---------- 雷达五层 + 彩虹描边 + 顶点光点 + 橙蓝描边 + 故障副本 ----------
    def build_radar(self):
        def pulse(a):
            return 0.75 + 0.25 * math.sin(self.time * 3.0)

        fill = always_redraw(lambda: Polygon(
            *self.poly_pts(), stroke_width=0,
            fill_color=self.col_now(),
            fill_opacity=0.45 * self.eff()))
        inner = always_redraw(lambda: Polygon(
            *[CENTER + (p - CENTER) * 0.55 for p in self.poly_pts()],
            stroke_width=0,
            fill_color=interpolate_color(self.col_now(), WHITE, 0.45),
            fill_opacity=0.10 * self.eff()))
        glow = always_redraw(lambda: Polygon(
            *self.poly_pts(), fill_opacity=0, stroke_width=15,
            stroke_color=interpolate_color(self.col_now(), WHITE, 0.45),
            stroke_opacity=0.22 * self.eff()))
        halo = always_redraw(lambda: Polygon(
            *self.poly_pts(), fill_opacity=0, stroke_width=30,
            stroke_color=interpolate_color(self.col_now(), WHITE, 0.22),
            stroke_opacity=0.08 * self.eff()))
        rainbow = always_redraw(lambda: VGroup(*self.edge_lines()))
        dots = always_redraw(lambda: VGroup(*self.vertex_dots()))
        rim_o = always_redraw(lambda: Polygon(
            *[p + (p - CENTER) * 0.030 for p in self.poly_pts()],
            fill_opacity=0, stroke_width=4.5, stroke_color="#FF9C3C",
            stroke_opacity=0.9 * self.rim.get_value() * pulse(0) * self.eff()))
        rim_b = always_redraw(lambda: Polygon(
            *[p - (p - CENTER) * 0.040 for p in self.poly_pts()],
            fill_opacity=0, stroke_width=2.8, stroke_color="#3CC8FF",
            stroke_opacity=0.8 * self.rim.get_value() * pulse(0) * self.eff()))
        g_o = always_redraw(lambda: Polygon(
            *[p + RIGHT * 0.06 * self.gl.get_value() for p in self.poly_pts()],
            fill_opacity=0, stroke_width=4.5, stroke_color="#FF7A00",
            stroke_opacity=0.85 * self.gl.get_value() * self.eff()))
        g_b = always_redraw(lambda: Polygon(
            *[p - RIGHT * 0.06 * self.gl.get_value() for p in self.poly_pts()],
            fill_opacity=0, stroke_width=4.5, stroke_color="#00CFFF",
            stroke_opacity=0.85 * self.gl.get_value() * self.eff()))
        self.radar_layers = VGroup(fill, inner, glow, halo, rainbow, dots,
                                   rim_o, rim_b, g_o, g_b)
        self.add(self.radar_layers)

    def edge_lines(self):
        pts = self.poly_pts()
        e = self.eff()
        lines = []
        nseg = 3
        for ed in range(6):
            i, j = ed, (ed + 1) % 6
            ci, cj = ManimColor(AX_COLORS[i]), ManimColor(AX_COLORS[j])
            d = pts[j] - pts[i]
            for k in range(nseg):
                t0, t1 = k / nseg, (k + 1) / nseg
                col = interpolate_color(ci, cj, (t0 + t1) / 2)
                lines.append(Line(pts[i] + d * t0, pts[i] + d * t1,
                                  stroke_color=col, stroke_width=4.5,
                                  stroke_opacity=e))
        return lines

    def vertex_dots(self):
        pts = self.poly_pts()
        e = self.eff()
        g = VGroup()
        for ax in range(6):
            c = ManimColor(AX_COLORS[ax])
            p = pts[ax]
            g.add(Circle(radius=0.50, fill_color=c, fill_opacity=0.10 * e,
                         stroke_width=0).move_to(p))
            g.add(Circle(radius=0.155, fill_color=c, fill_opacity=0.90 * e,
                         stroke_width=0).move_to(p))
            g.add(Circle(radius=0.085, fill_color=WHITE, fill_opacity=0.95 * e,
                         stroke_width=0).move_to(p))
        return g

    # ---------- 轴标签(彩色) + 滚轮数字 ----------
    def build_labels(self):
        self.name_mobs = []
        self.num_texts = []
        self.labels = VGroup()
        for ax in range(6):
            name = Text(AX_NAMES[ax], font="PingFang SC", weight=BOLD,
                        font_size=26, color=AX_COLORS[ax])
            nums = [self.mk_num(v) for v in range(13)]
            probe = nums[5]
            g = VGroup(name, probe).arrange(RIGHT, buff=0.18)
            g.move_to([AX_POS[ax][0], AX_POS[ax][1], 0])
            slot = probe.get_center()
            for t in nums:
                t.move_to(slot, aligned_edge=LEFT)
            grp = VGroup(name, *nums)
            grp.add_updater(self.mk_num_updater(ax, slot))
            self.labels.add(grp)
            self.name_mobs.append(name)
            self.num_texts.append(nums)

        def labels_up(mob, dt):
            e = self.eff()
            for n in self.name_mobs:
                n.set_opacity(e)
            for t in self.scale_nums:
                t.set_opacity(0.80 * e)
        self.labels.add_updater(labels_up)
        self.add(self.labels)

    def mk_num(self, v):
        return Text(fmt(v), font="Menlo", weight=BOLD, font_size=28,
                    color=WHITE)

    def mk_num_updater(self, ax, slot):
        def up(mob, dt):
            v = self.tr[ax].get_value()
            e = self.eff()
            h = 0.30
            lo = int(math.floor(v + 1e-6))
            lo = max(0, min(lo, 11))
            frac = v - lo
            if frac > 1 - 1e-6:
                lo = min(lo + 1, 11)
                frac = 0.0
            for k, t in enumerate(self.num_texts[ax]):
                if k == lo:
                    t.move_to(slot + UP * frac * h, aligned_edge=LEFT)
                    t.set_opacity((1 - frac) * e)
                elif k == lo + 1 and frac > 0.01:
                    t.move_to(slot + DOWN * (1 - frac) * h, aligned_edge=LEFT)
                    t.set_opacity(frac * e)
                else:
                    t.set_opacity(0)
        return up

    def build_header(self):
        self.header = Text("六维能力 · 雷达图鉴", font="Kaiti SC",
                           weight=BOLD, font_size=30)
        self.header.set_color_by_gradient("#9FB2CC", "#EAF2FF")
        self.header.move_to([0, 4.12, 0])
        self.add(self.header)

    # ---------- 转场特效 ----------
    def shockwave(self, color, expand=True, rmax=5.0, dur=0.4):
        rw = ValueTracker(0.18 if expand else rmax)

        def mk():
            r = rw.get_value()
            k = (r - 0.18) / (rmax - 0.18) if expand else r / rmax
            k = min(1.0, max(0.0, k))
            return Circle(radius=r, stroke_color=color,
                          stroke_width=4.5 * (1 - k) + 0.7,
                          stroke_opacity=0.9 * (1 - k)).move_to(CENTER)
        ring = always_redraw(mk)
        self.add(ring)
        self.play(rw.animate.set_value(rmax if expand else 0.02),
                  run_time=dur, rate_func=smooth)
        self.remove(ring)
        self.clock += dur

    def glitch_bars(self):
        for y0, h, op, d in [(-4.2, 0.16, 0.40, 0.22), (3.8, 0.07, 0.30, 0.16)]:
            bar = Rectangle(width=16, height=h, fill_color=WHITE,
                            fill_opacity=op, stroke_width=0)
            bar.move_to([0, y0, 0])
            self.add(bar)
            self.play(bar.animate.move_to([0, -y0, 0]).set_opacity(0),
                      run_time=d, rate_func=smooth)
            self.remove(bar)
            self.clock += d

    # ---------- 时间轴 ----------
    def run_segment(self, i, seg, nxt, first_after_gap=False):
        fin = [float(v) for v in seg["v"]]
        dur = nxt - seg["t"]
        st = [max(2.0, f - 1.0) for f in fin]
        rim_target = 1.0 if seg.get("rim") else 0.0
        newc = SEGS_C[i]
        big = bool(seg.get("blur"))
        shock_dur = min(0.40, max(0.30, dur * 0.22))

        self.to(seg["t"])
        self.c_cur = ManimColor(self.col_now())
        self.c_to = ManimColor(newc)

        if first_after_gap:
            # 故障闪入: 亮起 + RGB 分离 + 闪烁 + 故障条
            self.play(self.op.animate.set_value(1.0),
                      self.gl.animate.set_value(1.0),
                      FadeIn(self.header),
                      run_time=0.35, rate_func=smooth)
            self.clock += 0.35
            self.play(self.gl.animate.set_value(0.0),
                      run_time=0.40, rate_func=smooth)
            self.clock += 0.40
            for o in (0.25, 1.0, 0.45, 1.0):
                self.play(self.op.animate.set_value(o), run_time=0.09)
                self.clock += 0.09
            self.glitch_bars()
            self.to(seg["t"] + 0.9)

        if big:
            # 大转场: zoom + 压暗(加速冲出/减速归来)
            self.shockwave(newc, dur=shock_dur)
            self.web.save_state()
            self.web_glow.save_state()
            self.play(self.ct.animate.set_value(1.0),
                      self.dim.animate.set_value(0.15),
                      self.web.animate.scale(1.22, about_point=CENTER),
                      self.web_glow.animate.scale(1.22, about_point=CENTER),
                      self.rim.animate.set_value(rim_target),
                      *[self.tr[ax].animate.set_value(st[ax])
                        for ax in range(6)],
                      run_time=0.55, rate_func=rush_into)
            self.clock += 0.55
            self.play(self.dim.animate.set_value(1.0),
                      self.web.animate.restore(),
                      self.web_glow.animate.restore(),
                      *[self.tr[ax].animate.set_value(fin[ax])
                        for ax in range(6)],
                      run_time=0.65, rate_func=rush_from)
            self.clock += 0.65
            self.to(nxt - 0.30)
            return

        # 普通转场: 冲击波 + 颜色 morph + 数值先沉
        self.shockwave(newc, dur=shock_dur)
        self.play(self.ct.animate.set_value(1.0),
                  self.rim.animate.set_value(rim_target),
                  *[self.tr[ax].animate.set_value(st[ax])
                    for ax in range(6)],
                  run_time=0.25, rate_func=smooth)
        self.clock += 0.25
        self.ct.set_value(0)
        self.c_cur = ManimColor(newc)
        self.c_to = ManimColor(newc)

        # 数值滚动上涨
        roll = min(2.0, max(0.22, dur - 0.25 - shock_dur - 0.30))
        self.play(*[self.tr[ax].animate.set_value(fin[ax])
                    for ax in range(6)],
                  run_time=roll, rate_func=ease_in_out_cubic)
        self.clock += roll
        self.to(nxt - 0.30)
