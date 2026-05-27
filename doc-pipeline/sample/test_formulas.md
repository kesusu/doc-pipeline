## A. 求频率/波长/能量

来源：教材第1章 §1.2，式(1.2.3)

$$ h = 6.626\times10^{-34} \text{ J·s}, \quad c = 3\times10^{8} \text{ m/s} $$

1μm光子 = 1.24eV（记住这个常数，直接用）

$$ E = h\nu = \frac{hc}{\lambda} $$

易错：单位！题目给nm，公式用m，必须先换算

## B. 纵模间隔/模式数/损耗/Q值

### 纵模间隔

$$ \Delta\nu_q = \frac{c}{2L'} $$

其中 $L' = n \cdot L$（有介质要乘折射率）

### 腔内纵模数

$$ N = \frac{\Delta\nu_G}{\Delta\nu_q} = \frac{\Delta\nu_G \cdot 2L'}{c} $$

### 损耗和Q值

$$ Q = 2\pi\nu_0 \frac{E}{\delta E} = \frac{2\pi\nu_0 L'}{\delta \cdot c} $$

| 参数 | 公式 | 单位 |
|------|------|------|
| 损耗系数 | $\delta = \delta_i + \frac{1}{2}\ln\frac{1}{R_1 R_2}$ | 无量纲 |
| 光子寿命 | $t_c = \frac{L'}{\delta \cdot c}$ | s |
| Q值 | $Q = 2\pi\nu_0 t_c$ | 无量纲 |

## C. 判断腔的稳定性

### g参数

$$ g_1 = 1 - \frac{L}{R_1}, \quad g_2 = 1 - \frac{L}{R_2} $$

### 稳定性判据

$$ 0 < g_1 g_2 < 1 \quad \text{（稳定腔）} $$

### R的符号规则

- 凹面镜朝向腔内：$R > 0$
- 凸面镜朝向腔内：$R < 0$

| 腔型 | $g_1$ | $g_2$ | $g_1 g_2$ |
|------|-------|-------|-----------|
| 对称共焦腔 | 0 | 0 | 0 |
| 对称球面腔 | $1-L/R$ | $1-L/R$ | $(1-L/R)^2$ |
| 平凹腔 | 1 | $1-L/R$ | $1-L/R$ |
| 平行平面腔 | 1 | 1 | 1 |

## D. 高斯光束参数

### 基本关系

$$ w(z) = w_0 \sqrt{1 + \left(\frac{z}{z_R}\right)^2} $$

$$ z_R = \frac{\pi w_0^2}{\lambda} \quad \text{（瑞利长度）} $$

### q参数

$$ \frac{1}{q(z)} = \frac{1}{R(z)} - i\frac{\lambda}{\pi w^2(z)} $$

$$ q(z) = q_0 + z $$

### ABCD法则

$$ q_2 = \frac{A q_1 + B}{C q_1 + D} $$

## E. 谱线加宽

### 多普勒线宽

$$ \Delta\nu_D = 2\nu_0 \sqrt{\frac{2kT\ln 2}{mc^2}} = 7.16\times10^{-7}\nu_0\sqrt{\frac{T}{M}} $$

| 加宽类型 | 机制 | 线型 | 典型激光器 |
|----------|------|------|-----------|
| 均匀加宽 | 碰撞/自然 | 洛伦兹 | CO₂, Nd:YAG |
| 非均匀加宽 | 多普勒 | 高斯 | He-Ne |
| 综合加宽 | 两者都有 | Voigt | - |

## F. 增益、阈值、输出功率

### 增益系数

$$ G = \Delta N \sigma(\nu) $$

### 发射截面

$$ \sigma(\nu) = \frac{A_{21} \lambda^2}{8\pi n^2} g(\nu, \nu_0) $$

### 阈值条件

$$ G_{th} = \delta = \alpha + \frac{1}{2L}\ln\frac{1}{R_1 R_2} $$

### 输出功率（均匀加宽单模，$T \ll 1$）

$$ P = \frac{1}{2} I_s T A \left(\sqrt{\frac{I_s}{I_{in}}} - 1\right)^{-2} $$
