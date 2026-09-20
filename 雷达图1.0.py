# -*- coding: utf-8 -*-
# 雷达图动画复刻 —— 依据原片 120.6s / 1280x720@30fps 逐帧取证逆向
# 结构: 黑底星空粒子 + 六维雷达(理论/实践/群众/品德/国际/历史) + 23 个人物分段
# 转场判定: 换人 = 颜色 0.35s 交叉 morph + 数值跳变后滚动上涨;
#           63s = 放大+压暗大转场; 99-106.6s = 黑场; 107s = 故障闪入 + 橙蓝描边高亮段
import math
import random

import numpy as np
from manim import *

config.frame_width = 16
config.frame_height = 9          # 80 px/unit @1280x720

R_RADAR = 3.54          # 283px / 80
CENTER = np.array([0.0, -0.14, 0.0])
ANG = [90, 30, -30, -90, -150, 150]          # 理论 实践 群众 品德 国际 历史
AX_NAMES = ["理论贡献", "实践贡献", "群众路线", "个人品德", "国际主义", "历史影响"]
AX_POS = [(0.02, 3.62), (4.10, 2.01), (3.97, -2.09),
          (-0.10, -4.14), (-4.05, -2.09), (-4.11, 2.03)]

# t=起始秒 c=主色 v=终值(理论,实践,群众,品德,国际,历史) rim=橙蓝描边高亮
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
GAP_START, GAP_END = 99.0, 106.6     # 黑场间隔
END_T, TOTAL = 119.4, 120.6


def unit(a):
    r = np.radians(a)
    return np.array([math.cos(r), math.sin(r), 0.0])


def fmt(v):
    return "10+" if v >= 11 else str(int(round(v)))


class RadarRemake(Scene):
    def construct(self):
        self.clock = 0.0
        self.c_cur = ManimColor(SEGS[0]["c"])
        self.c_to = ManimColor(SEGS[0]["c"])
        self.ct = ValueTracker(0.0)     # 颜色 morph 进度
        self.op = ValueTracker(0.0)     # 雷达层全局透明度
        self.sc = ValueTracker(1.0)     # 雷达缩放(大转场用)
        self.rim = ValueTracker(0.0)
        self.tr = [ValueTracker(float(v)) for v in SEGS[0]["v"]]
        self.start_v = [float(v) for v in SEGS[0]["v"]]

        self.build_particles()
        self.build_web()
        self.build_radar()
        self.build_labels()

        self.play(self.op.animate.set_value(1),
                  FadeIn(self.web), FadeIn(self.labels),
                  FadeIn(self.particles), FadeIn(self.haze),
                  run_time=0.9)
        self.clock = 0.9
        self.set_all_nums(self.start_v)

        for i in range(21):
            nxt = SEGS[i + 1]["t"] if i < 20 else GAP_START
            self.run_segment(i, SEGS[i], nxt)

        # ---- 黑场间隔 ----
        self.to(GAP_START)
        self.play(self.op.animate.set_value(0),
                  FadeOut(self.web), FadeOut(self.labels),
                  FadeOut(self.particles), FadeOut(self.haze),
                  run_time=0.9)
        self.clock += 0.9
        self.to(GAP_END)

        # ---- 尾段(故障闪入 + 橙蓝描边) ----
        for i in (21, 22):
            nxt = SEGS[22]["t"] if i == 21 else END_T
            self.run_segment(i, SEGS[i], nxt,
                             first_after_gap=(i == 21))

        self.to(END_T)
        self.play(self.op.animate.set_value(0),
                  FadeOut(self.web), FadeOut(self.labels),
                  FadeOut(self.particles), FadeOut(self.haze),
                  run_time=0.8)
        self.wait(TOTAL - END_T - 0.8)

    # ---------- 组件 ----------
    def col_now(self):
        return interpolate_color(self.c_cur, self.c_to, self.ct.get_value())

    def build_particles(self):
        rnd = random.Random(7)
        ps = VGroup()
        for _ in range(46):
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
            ps.add(g)
        self.particles = ps
        self.add(ps)

        haze = VGroup()
        for cx, cy, rr in [(-6.2, 3.4, 2.0), (6.4, 3.0, 1.7), (-6.8, -3.2, 1.9),
                           (6.6, -3.4, 1.8), (0.5, 4.3, 2.2), (0, -4.4, 2.0)]:
            blob = VGroup()
            for k in range(5):
                c = Circle(radius=rr * (0.25 + 0.19 * k), stroke_width=0,
                           fill_color=WHITE, fill_opacity=0.013)
                c.base_op = 0.013
                blob.add(c)
            blob.move_to([cx, cy, 0])
            haze.add(blob)
        self.haze = haze
        self.add(haze)

        def up(mob, dt):
            col = self.col_now()
            opac = self.op.get_value()
            t = self.time
            for p in mob:
                p.shift(p.vel * dt)
                x, y = p.get_x(), p.get_y()
                if x > 7.9:
                    p.set_x(-7.9)
                if x < -7.9:
                    p.set_x(7.9)
                if y > 4.5:
                    p.set_y(-4.5)
                if y < -4.5:
                    p.set_y(4.5)
                osc = 0.55 + 0.45 * math.sin(t * p.freq + p.phase)
                p[2].set_color(interpolate_color(col, WHITE, 0.55))
                p[2].set_opacity(p.op * osc * 0.9 * opac)
                p[1].set_color(col)
                p[1].set_opacity(0.10 * p.op * osc * opac)
                p[0].set_color(col)
                p[0].set_opacity(0.045 * p.op * osc * opac)
            for blob in self.haze:
                for c in blob:
                    c.set_color(col)
                    c.set_opacity(c.base_op * opac)
        ps.add_updater(up)

    def build_web(self):
        web = VGroup()
        gray = "#5A5A5A"
        for lvl in range(1, 6):
            pts = [CENTER + unit(a) * (R_RADAR * lvl / 5) for a in ANG]
            poly = Polygon(*pts, stroke_color=gray, stroke_width=1.6,
                           stroke_opacity=0.75 if lvl == 5 else 0.42)
            poly.base_so = 0.75 if lvl == 5 else 0.42
            web.add(poly)
        for a in ANG:
            ln = Line(CENTER, CENTER + unit(a) * R_RADAR,
                      stroke_color=gray, stroke_width=1.4,
                      stroke_opacity=0.42)
            ln.base_so = 0.42
            web.add(ln)
        self.web = web

    def poly_pts(self):
        s = self.sc.get_value()
        return [CENTER + unit(ANG[ax]) *
                (R_RADAR * self.tr[ax].get_value() / 10 * s)
                for ax in range(6)]

    def build_radar(self):
        def web_up(m, dt):
            k = max(0.06, 1.0 - 0.94 * self.rim.get_value()) \
                * self.op.get_value()
            for c in m:
                c.set_stroke(opacity=c.base_so * k)
        self.web.add_updater(web_up)

        def line_mix():
            # rim 尾段: 描边贴近本色不发白; 普通段: 亮白描边
            return 0.30 if self.rim.get_value() > 0.5 else 0.55

        fill = always_redraw(lambda: Polygon(
            *self.poly_pts(), stroke_width=0,
            fill_color=self.col_now(),
            fill_opacity=0.38 * self.op.get_value()))
        glow = always_redraw(lambda: Polygon(
            *self.poly_pts(), fill_opacity=0, stroke_width=18,
            stroke_color=interpolate_color(self.col_now(), WHITE, 0.45),
            stroke_opacity=0.30 * self.op.get_value()))
        line = always_redraw(lambda: Polygon(
            *self.poly_pts(), fill_opacity=0, stroke_width=5,
            stroke_color=interpolate_color(self.col_now(), WHITE, line_mix()),
            stroke_opacity=self.op.get_value()))
        rim_o = always_redraw(lambda: Polygon(
            *[p + (p - CENTER) * 0.022 for p in self.poly_pts()],
            fill_opacity=0, stroke_width=3, stroke_color="#FF9C3C",
            stroke_opacity=0.9 * self.rim.get_value() * self.op.get_value()))
        rim_b = always_redraw(lambda: Polygon(
            *[p - (p - CENTER) * 0.03 for p in self.poly_pts()],
            fill_opacity=0, stroke_width=2, stroke_color="#3CC8FF",
            stroke_opacity=0.8 * self.rim.get_value() * self.op.get_value()))
        self.radar_layers = VGroup(fill, glow, line, rim_o, rim_b)
        self.add(self.radar_layers)

    def build_labels(self):
        self.num_mobs = []
        self.labels = VGroup()
        for ax in range(6):
            name = Text(AX_NAMES[ax], font="PingFang SC", weight=BOLD,
                        font_size=26, color=WHITE)
            num = self.mk_num(self.start_v[ax])
            g = VGroup(name, num).arrange(RIGHT, buff=0.16)
            g.move_to([AX_POS[ax][0], AX_POS[ax][1], 0])
            self.num_mobs.append(num)
            self.labels.add(VGroup(name, num))

    def mk_num(self, v):
        return Text(fmt(v), font="Menlo", weight=BOLD,
                    font_size=28, color=WHITE)

    def set_num(self, ax, v):
        old = self.num_mobs[ax]
        new = self.mk_num(v)
        new.move_to(old, aligned_edge=LEFT)
        self.labels[ax].remove(old)
        self.labels[ax].add(new)
        self.num_mobs[ax] = new

    def set_all_nums(self, vals):
        for ax in range(6):
            self.set_num(ax, vals[ax])

    # ---------- 时间轴 ----------
    def to(self, t):
        d = t - self.clock
        if d > 0.01:
            n = int(round(d * 30))
            self.wait(n / 30)
            self.clock += n / 30
        self.clock = max(self.clock, t)

    def run_segment(self, i, seg, nxt, first_after_gap=False):
        fin = [float(v) for v in seg["v"]]
        dur = nxt - seg["t"]
        st = [max(2.0, f - 1.0) for f in fin]
        rim_target = 1.0 if seg.get("rim") else 0.0

        self.to(seg["t"])
        self.c_cur = ManimColor(self.col_now())
        self.c_to = ManimColor(seg["c"])

        if first_after_gap:
            self.play(self.op.animate.set_value(1),
                      FadeIn(self.web), FadeIn(self.labels),
                      FadeIn(self.particles), FadeIn(self.haze),
                      run_time=0.5)
            for o in (0.25, 1.0, 0.4, 1.0):
                self.play(self.op.animate.set_value(o),
                          self.labels.animate.set_opacity(o),
                          run_time=0.1)
            self.clock += 0.9
            self.to(seg["t"] + 0.9)

        if seg.get("blur"):
            self.web.save_state()
            self.labels.save_state()
            self.play(self.ct.animate.set_value(1.0),
                      self.sc.animate.set_value(1.22),
                      self.web.animate.scale(1.22, about_point=CENTER)
                      .set_opacity(0.12),
                      self.labels.animate.set_opacity(0.12),
                      self.op.animate.set_value(0.12),
                      self.rim.animate.set_value(rim_target),
                      run_time=0.5, rate_func=rush_into)
            self.play(self.sc.animate.set_value(1.0),
                      self.web.animate.restore(),
                      self.labels.animate.restore(),
                      self.op.animate.set_value(1.0),
                      *[self.tr[ax].animate.set_value(st[ax])
                        for ax in range(6)],
                      run_time=0.5, rate_func=rush_from)
            self.clock += 1.0
        else:
            self.play(self.ct.animate.set_value(1.0),
                      *[self.tr[ax].animate.set_value(st[ax])
                        for ax in range(6)],
                      self.rim.animate.set_value(rim_target),
                      run_time=0.3)
            self.clock += 0.3
        self.ct.set_value(0)
        self.c_cur = ManimColor(seg["c"])
        self.c_to = ManimColor(seg["c"])
        self.set_all_nums(st)

        # 数值滚动
        roll_win = min(1.8, max(0.7, dur * 0.4))
        events = []
        for ax in range(6):
            steps = int(round(fin[ax] - st[ax]))
            if steps <= 0:
                continue
            for k in range(1, steps + 1):
                tt = seg["t"] + 0.45 + ax * 0.13 + \
                    (k / steps) * (roll_win - 0.78)
                events.append((min(tt, nxt - 0.5), ax, int(st[ax] + k)))
        events.sort(key=lambda e: e[0])
        for tt, ax, val in events:
            self.to(tt)
            self.play(self.tr[ax].animate.set_value(val),
                      run_time=0.2, rate_func=linear)
            self.set_num(ax, val)
            self.clock += 0.2
        self.to(nxt - 0.3 if nxt < END_T else nxt)
