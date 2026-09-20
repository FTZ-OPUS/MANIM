# -*- coding: utf-8 -*-
# 不等式天花板 · 雷达图鉴 —— 雷达图源码机制(ValueTracker+always_redraw+星空粒子) × 公式混剪技能(1秒/卡+transform_mismatches)
# 左侧六维雷达随卡 morph，右侧不等式名 + 公式 + 注解
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
import random

import numpy as np
from manim import *

from ir_data import INEQS, PAL

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16.0
config.frame_height = 9.0
config.background_color = "#050505"

T_RUN, T_HOLD = 0.45, 0.55
FONT = "Kaiti SC"

ANG = [90, 30, -30, -90, -150, 150]
AX_NAMES = ["考试频率", "竞赛热度", "数学美感", "应用广度", "初等亲和", "推广深度"]
CL = np.array([-3.55, -0.2, 0.0])       # 雷达中心(左侧)
R_RADAR = 2.5
RX = 3.05                                # 右侧文字列中心 x

GOLD1, GOLD2 = "#FFD166", "#F59E62"
OR1, OR2 = "#FF8A50", "#FFD166"
GREEN = "#66D19E"
TEAL = "#4DB6AC"
LBL = "#B9C6D6"


def unit(a):
    r = np.radians(a)
    return np.array([math.cos(r), math.sin(r), 0.0])


class IneqRadar(Scene):
    def construct(self):
        self.c_cur = ManimColor(PAL[0])
        self.c_to = ManimColor(PAL[0])
        self.ct = ValueTracker(0.0)                     # 颜色 morph 进度
        self.tr = [ValueTracker(0.0) for _ in range(6)]

        self.build_particles()
        self.build_web()
        self.build_labels()
        self.build_radar()

        title = Text("不等式天花板 · 雷达图鉴", font=FONT, weight=BOLD, font_size=34)
        title.set_color_by_gradient(GOLD1, GOLD2).move_to(UP * 3.95)

        self.play(FadeIn(title), FadeIn(self.web), FadeIn(self.labels),
                  FadeIn(self.particles), FadeIn(self.haze), run_time=0.6)
        self.wait(0.4)

        cur = INEQS[0]
        cur_name = self.make_name(cur[0])
        cur_f = self.make_formula(cur[1])
        cur_note = self.make_note(cur[2])
        self.play(
            ct_anim(self), *vtrack_anim(self, cur[3]),
            FadeIn(cur_name, shift=DOWN * 0.3),
            FadeIn(cur_f, shift=DOWN * 0.3),
            FadeIn(cur_note),
            run_time=T_RUN,
        )
        self.wait(T_HOLD)

        for k in range(1, len(INEQS)):
            name, latex, note, scores = INEQS[k]
            self.c_cur = ManimColor(self.col_now())
            self.c_to = ManimColor(PAL[k % len(PAL)])
            self.ct.set_value(0.0)
            nn = self.make_name(name)
            nf = self.make_formula(latex)
            nnote = self.make_note(note)
            self.play(
                ReplacementTransform(cur_name, nn),
                TransformMatchingTex(cur_f, nf, transform_mismatches=True),
                ReplacementTransform(cur_note, nnote),
                ct_anim(self), *vtrack_anim(self, scores),
                run_time=T_RUN,
            )
            cur_name, cur_f, cur_note = nn, nf, nnote
            self.wait(T_HOLD)

        # ---- 结尾：六边形拉满 ----
        end_name = Text("六边形拉满", font=FONT, weight=BOLD, font_size=96)
        end_name.set_color_by_gradient(GOLD1, GOLD2).move_to([RX, 0.9, 0])
        end_note = Text("关注我 · 考场稳赢", font=FONT, weight=BOLD, font_size=38, color=GREEN)
        end_note.move_to([RX, -0.8, 0])
        self.c_cur = ManimColor(self.col_now())
        self.c_to = ManimColor(GOLD1)
        self.ct.set_value(0.0)
        self.play(
            ct_anim(self), *vtrack_anim(self, [9, 9, 9, 9, 9, 9]),
            ReplacementTransform(cur_name, end_name),
            ReplacementTransform(cur_f, end_note),
            FadeOut(cur_note),
            run_time=T_RUN,
        )
        self.wait(1.1)
        self.play(FadeOut(end_name), FadeOut(end_note), FadeOut(title),
                  FadeOut(self.web), FadeOut(self.labels), FadeOut(self.radar_layers),
                  FadeOut(self.particles), FadeOut(self.haze), run_time=0.5)

    # ---------- 颜色 ----------
    def col_now(self):
        return interpolate_color(self.c_cur, self.c_to, self.ct.get_value())

    # ---------- 星空粒子(雷达图源码移植, 简化) ----------
    def build_particles(self):
        rnd = random.Random(7)
        ps = VGroup()
        for _ in range(38):
            r = rnd.uniform(0.03, 0.09)
            core = Circle(radius=r, fill_color=WHITE, fill_opacity=0.85, stroke_width=0)
            halo1 = Circle(radius=r * 2.0, fill_color=WHITE, fill_opacity=0.10, stroke_width=0)
            halo2 = Circle(radius=r * 3.2, fill_color=WHITE, fill_opacity=0.045, stroke_width=0)
            g = VGroup(halo2, halo1, core).move_to(
                [rnd.uniform(-7.6, 7.6), rnd.uniform(-4.3, 4.3), 0])
            g.vel = np.array([rnd.uniform(-0.18, 0.18),
                              rnd.uniform(-0.11, 0.11), 0.0])
            g.op = rnd.uniform(0.3, 1.0)
            g.freq = rnd.uniform(0.5, 1.8)
            g.phase = rnd.uniform(0, 6.28)
            ps.add(g)
        self.particles = ps
        self.add(ps)

        haze = VGroup()
        for cx, cy, rr in [(-6.2, 3.4, 2.0), (6.4, 3.0, 1.7), (-6.8, -3.2, 1.9),
                           (6.6, -3.4, 1.8), (0.5, 4.3, 2.2)]:
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

        scene = self
        scene._pt = 0.0

        def up(mob, dt):
            scene._pt += dt
            t = scene._pt
            col = scene.col_now()
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
                p[2].set_color(interpolate_color(col, WHITE, 0.55))
                p[2].set_opacity(p.op * osc * 0.9)
                p[1].set_color(col)
                p[1].set_opacity(0.10 * p.op * osc)
                p[0].set_color(col)
                p[0].set_opacity(0.045 * p.op * osc)
            for blob in scene.haze:
                for c in blob:
                    c.set_color(col)

        ps.add_updater(up)

    # ---------- 六边形网 ----------
    def build_web(self):
        web = VGroup()
        gray = "#5A5A5A"
        for lvl in range(1, 6):
            pts = [CL + unit(a) * (R_RADAR * lvl / 5) for a in ANG]
            web.add(Polygon(*pts, stroke_color=gray, stroke_width=1.6,
                            stroke_opacity=0.8 if lvl == 5 else 0.42))
        for a in ANG:
            web.add(Line(CL, CL + unit(a) * R_RADAR,
                         stroke_color=gray, stroke_width=1.4, stroke_opacity=0.42))
        self.web = web
        self.add(web)

    # ---------- 轴标签 + 数值 ----------
    def build_labels(self):
        self.labels = VGroup()
        for ax in range(6):
            u = unit(ANG[ax])
            name = Text(AX_NAMES[ax], font=FONT, weight=BOLD, font_size=20, color=LBL)
            name.move_to(CL + u * (R_RADAR * 1.24))
            num = always_redraw(lambda ax=ax: DecimalNumber(
                self.tr[ax].get_value(), num_decimal_places=0,
                font_size=26, color=WHITE).move_to(CL + unit(ANG[ax]) * (R_RADAR * 0.62)))
            self.labels.add(name, num)
        self.add(self.labels)

    # ---------- 雷达三层(填充/辉光/描边) ----------
    def poly_pts(self):
        return [CL + unit(ANG[ax]) * (R_RADAR * self.tr[ax].get_value() / 10)
                for ax in range(6)]

    def build_radar(self):
        scene = self
        fill = always_redraw(lambda: Polygon(
            *scene.poly_pts(), stroke_width=0,
            fill_color=scene.col_now(), fill_opacity=0.38))
        glow = always_redraw(lambda: Polygon(
            *scene.poly_pts(), fill_opacity=0, stroke_width=16,
            stroke_color=interpolate_color(scene.col_now(), WHITE, 0.45),
            stroke_opacity=0.30))
        line = always_redraw(lambda: Polygon(
            *scene.poly_pts(), fill_opacity=0, stroke_width=5,
            stroke_color=interpolate_color(scene.col_now(), WHITE, 0.55)))
        self.radar_layers = VGroup(fill, glow, line)
        self.add(self.radar_layers)

    # ---------- 右侧构件 ----------
    def make_name(self, s):
        t = Text(s, font=FONT, weight=BOLD, font_size=58)
        t.set_color_by_gradient(GOLD1, GOLD2)
        t.move_to([RX, 2.45, 0])
        if t.width > 7.2:
            t.scale_to_fit_width(7.2)
        return t

    def make_formula(self, latex):
        f = MathTex(latex, font_size=54, stroke_width=1.1)
        f.set_color_by_gradient(OR1, OR2)
        f.move_to([RX, 0.1, 0])
        if f.width > 6.6:
            f.scale_to_fit_width(6.6)
        return f

    def make_note(self, s):
        t = Text(s, font=FONT, weight=BOLD, font_size=28, color=GREEN)
        t.move_to([RX, -1.9, 0])
        if t.width > 7.2:
            t.scale_to_fit_width(7.2)
        return t


def ct_anim(scene):
    return scene.ct.animate.set_value(1.0)


def vtrack_anim(scene, scores):
    return [scene.tr[ax].animate.set_value(float(scores[ax])) for ax in range(6)]
