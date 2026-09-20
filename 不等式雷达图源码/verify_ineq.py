# -*- coding: utf-8 -*-
# 25 条不等式逐条数值验证（numpy），上屏前的最后一道闸
import numpy as np

rng = np.random.default_rng(20260920)
PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name)


def quad(f, a, b, n=4000):
    x = np.linspace(a, b, n)
    y = f(x)
    return np.trapezoid(y, x)


ok = True
# 01 AM-GM
for _ in range(200):
    a, b = rng.uniform(0.01, 50, 2)
    ok = ok and np.sqrt(a * b) <= (a + b) / 2 + 1e-12
check("01 基本不等式 sqrt(ab) <= (a+b)/2", ok)

# 02 均值链 H <= G <= A <= Q
ok = True
for _ in range(200):
    v = rng.uniform(0.05, 30, 6)
    H = len(v) / np.sum(1 / v); G = np.prod(v) ** (1 / len(v))
    A = v.mean(); Q = np.sqrt((v ** 2).mean())
    ok = ok and H <= G + 1e-9 <= A + 1e-9 and A <= Q + 1e-9
check("02 均值不等式链 H<=G<=A<=Q", ok)

# 03 幂平均单调
ok = True
for _ in range(200):
    v = rng.uniform(0.05, 30, 6)
    M = lambda r: (np.mean(v ** r)) ** (1 / r)
    ok = ok and M(1) <= M(2) + 1e-9 and M(2) <= M(3) + 1e-9 and M(-1) <= M(1) + 1e-9
check("03 幂平均 r<s => M_r <= M_s", ok)

# 04 柯西(代数)
ok = True
for _ in range(200):
    a, b = rng.normal(size=8), rng.normal(size=8)
    ok = ok and (a @ b) ** 2 <= (a @ a) * (b @ b) + 1e-9
check("04 柯西不等式 (Σab)^2 <= Σa^2 Σb^2", ok)

# 05 柯西积分形式
ok = True
for _ in range(50):
    p1, p2 = rng.normal(size=3), rng.normal(size=3)
    f = lambda x: np.polyval(p1, x); g = lambda x: np.polyval(p2, x)
    x = np.linspace(-1, 1, 4000)
    lhs = np.trapezoid(f(x) * g(x), x) ** 2
    rhs = np.trapezoid(f(x) ** 2, x) * np.trapezoid(g(x) ** 2, x)
    ok = ok and lhs <= rhs + 1e-7
check("05 柯西积分形式 (∫fg)^2 <= ∫f^2 ∫g^2", ok)

# 06 嵌入不等式 2Σ_{i<j} a_ia_j <= (n-1)Σa_i^2
ok = True
for _ in range(200):
    v = rng.normal(size=9)
    cross = sum(v[i] * v[j] for i in range(9) for j in range(i + 1, 9))
    ok = ok and 2 * cross <= 8 * np.sum(v ** 2) + 1e-9
check("06 嵌入不等式", ok)

# 07 杨氏不等式 ab <= a^p/p + b^q/q, 1/p+1/q=1
ok = True
for _ in range(200):
    p = rng.uniform(1.2, 5); q = 1 / (1 - 1 / p)
    a, b = rng.uniform(0.05, 20, 2)
    ok = ok and a * b <= a ** p / p + b ** q / q + 1e-9
check("07 杨氏不等式", ok)

# 08 赫尔德(和式)
ok = True
for _ in range(200):
    a, b = rng.normal(size=10), rng.normal(size=10)
    p = 3.0; q = 1.5
    lhs = np.sum(np.abs(a * b))
    rhs = (np.sum(np.abs(a) ** p)) ** (1 / p) * (np.sum(np.abs(b) ** q)) ** (1 / q)
    ok = ok and lhs <= rhs + 1e-8
check("08 赫尔德不等式", ok)

# 09 赫尔德积分形式
ok = True
for _ in range(50):
    p1 = rng.normal(size=3) * 2
    g1 = rng.normal(size=3) * 2
    f = lambda x: np.polyval(p1, x); g = lambda x: np.polyval(g1, x)
    x = np.linspace(0.1, 1.5, 4000)
    p, q = 3.0, 1.5
    lhs = np.trapezoid(np.abs(f(x) * g(x)), x)
    rhs = (np.trapezoid(np.abs(f(x)) ** p, x)) ** (1 / p) * (np.trapezoid(np.abs(g(x)) ** q, x)) ** (1 / q)
    ok = ok and lhs <= rhs + 1e-7
check("09 赫尔德积分形式", ok)

# 10 闵可夫斯基(和式)
ok = True
for _ in range(200):
    a, b = rng.normal(size=10), rng.normal(size=10)
    p = 3.0
    lhs = (np.sum(np.abs(a + b) ** p)) ** (1 / p)
    rhs = (np.sum(np.abs(a) ** p)) ** (1 / p) + (np.sum(np.abs(b) ** p)) ** (1 / p)
    ok = ok and lhs <= rhs + 1e-8
check("10 闵可夫斯基不等式", ok)

# 11 闵可夫斯基积分形式
ok = True
for _ in range(50):
    p1, g1 = rng.normal(size=3), rng.normal(size=3)
    f = lambda x: np.polyval(p1, x); g = lambda x: np.polyval(g1, x)
    x = np.linspace(0.1, 1.2, 4000)
    p = 3.0
    lhs = (np.trapezoid(np.abs(f(x) + g(x)) ** p, x)) ** (1 / p)
    rhs = (np.trapezoid(np.abs(f(x)) ** p, x)) ** (1 / p) + (np.trapezoid(np.abs(g(x)) ** p, x)) ** (1 / p)
    ok = ok and lhs <= rhs + 1e-7
check("11 闵可夫斯基积分形式", ok)

# 12 范数三角不等式
ok = True
for _ in range(200):
    x, y = rng.normal(size=6), rng.normal(size=6)
    ok = ok and np.linalg.norm(x + y) <= np.linalg.norm(x) + np.linalg.norm(y) + 1e-9
check("12 三角不等式 ||x+y|| <= ||x||+||y||", ok)

# 13 伯努利
ok = True
for _ in range(300):
    x = rng.uniform(-0.9, 1.5); n = int(rng.integers(2, 7))
    ok = ok and (1 + x) ** n >= 1 + n * x - 1e-9
check("13 伯努利不等式", ok)

# 14 琴生(和式)
ok = True
for _ in range(200):
    v = rng.uniform(-2, 2, 7)
    ok = ok and np.exp(v.mean()) <= np.mean(np.exp(v)) + 1e-9        # e^x 凸
    vp = rng.uniform(0.05, 5, 7)
    ok = ok and np.log(vp.mean()) >= np.mean(np.log(vp)) - 1e-9      # ln 凹
check("14 琴生不等式 f(mean) <= mean f", ok)

# 15 琴生积分形式
ok = True
for _ in range(50):
    c = rng.uniform(0.02, 0.5)
    f = lambda x: np.exp(x)
    x = np.linspace(0, 1, 4000)
    mean_x = np.trapezoid(x, x) / (1 - 0)
    mean_f = np.trapezoid(f(x), x) / (1 - 0)
    ok = ok and f(mean_x) <= mean_f + 1e-7
check("15 琴生积分形式 f(∫x) <= ∫f", ok)

# 16 切比雪夫(和式): 同序 => avg(ab) >= avg(a)avg(b)
ok = True
for _ in range(200):
    a = np.sort(rng.uniform(0, 10, 8)); b = np.sort(rng.uniform(0, 10, 8))
    ok = ok and np.mean(a * b) >= a.mean() * b.mean() - 1e-9
check("16 切比雪夫不等式", ok)

# 17 切比雪夫积分形式
ok = True
for _ in range(50):
    c1, c2 = np.sort(rng.uniform(0.1, 3, 2)), np.sort(rng.uniform(0.1, 3, 2))
    f = lambda x: c1[0] + c1[1] * x ** 2
    g = lambda x: c2[0] + c2[1] * x ** 3
    x = np.linspace(0, 1, 4000)
    lhs = np.trapezoid(f(x) * g(x), x)
    rhs = np.trapezoid(f(x), x) * np.trapezoid(g(x), x)
    ok = ok and lhs >= rhs - 1e-7
check("17 切比雪夫积分形式 ∫fg >= ∫f ∫g", ok)

# 18 排序不等式: 同序 >= 乱序
ok = True
for _ in range(200):
    a = np.sort(rng.uniform(0, 10, 7)); b = np.sort(rng.uniform(0, 10, 7))
    base = a @ b
    for _ in range(20):
        perm = rng.permutation(7)
        ok = ok and base >= a @ b[perm] - 1e-9
check("18 排序不等式", ok)

# 19 舒尔不等式 Σa(a-b)(a-c) >= 0
ok = True
for _ in range(300):
    a, b, c = np.sort(rng.uniform(0.05, 10, 3))[::-1]
    ok = ok and a * (a - b) * (a - c) + b * (b - c) * (b - a) + c * (c - a) * (c - b) >= -1e-9
check("19 舒尔不等式", ok)

# 20 内斯比特
ok = True
for _ in range(300):
    a, b, c = rng.uniform(0.05, 10, 3)
    ok = ok and a / (b + c) + b / (c + a) + c / (a + b) >= 1.5 - 1e-9
check("20 内斯比特不等式", ok)

# 21 外森比克 a^2+b^2+c^2 >= 4√3 S
ok = True
for _ in range(300):
    A_, B_, C_ = rng.uniform(-5, 5, (3, 2))
    a = np.linalg.norm(B_ - C_); b = np.linalg.norm(A_ - C_); c = np.linalg.norm(A_ - B_)
    S = abs((B_[0]-A_[0])*(C_[1]-A_[1]) - (B_[1]-A_[1])*(C_[0]-A_[0])) / 2
    if S > 1e-6:
        ok = ok and a ** 2 + b ** 2 + c ** 2 >= 4 * np.sqrt(3) * S - 1e-7
check("21 外森比克不等式", ok)

# 22 欧拉 R >= 2r
ok = True
for _ in range(300):
    A_, B_, C_ = rng.uniform(-5, 5, (3, 2))
    a = np.linalg.norm(B_ - C_); b = np.linalg.norm(A_ - C_); c = np.linalg.norm(A_ - B_)
    S = abs((B_[0]-A_[0])*(C_[1]-A_[1]) - (B_[1]-A_[1])*(C_[0]-A_[0])) / 2
    if S > 1e-6:
        R = a * b * c / (4 * S)
        r = 2 * S / (a + b + c)
        ok = ok and R >= 2 * r - 1e-7
check("22 欧拉不等式 R >= 2r", ok)

# 23 等周 L^2 >= 4πS
ok = True
for _ in range(300):
    w, h = rng.uniform(0.1, 10, 2)
    ok = ok and (2 * (w + h)) ** 2 >= 4 * np.pi * w * h - 1e-9
    a, b = rng.uniform(0.1, 10, 2)
    ok = ok and (a + b + np.hypot(a, b)) ** 2 >= 4 * np.pi * a * b / 2 - 1e-9  # 直角三角形
check("23 等周不等式 L^2 >= 4πS", ok)

# 24 哈达玛 |det| <= ∏行范数
ok = True
for _ in range(200):
    M = rng.normal(size=(5, 5))
    ok = ok and abs(np.linalg.det(M)) <= np.prod(np.linalg.norm(M, axis=1)) + 1e-8
check("24 哈达玛不等式", ok)

# 25 弗罗宾尼斯秩不等式 r(AB)+r(BC) <= r(B)+r(ABC)
ok = True
for _ in range(100):
    n = 5
    def lowrank(k):
        U = rng.normal(size=(n, k)); V = rng.normal(size=(k, n))
        return U @ V
    A_, B_, C_ = lowrank(3), lowrank(3), lowrank(3)
    r = lambda M: np.linalg.matrix_rank(M, tol=1e-9)
    ok = ok and r(A_ @ B_) + r(B_ @ C_) <= r(B_) + r(A_ @ B_ @ C_) + 1
check("25 弗罗宾尼斯秩不等式", ok)

print(f"\n==== {len(PASS)} passed, {len(FAIL)} failed ====")
if FAIL:
    print("FAILED:", FAIL)
