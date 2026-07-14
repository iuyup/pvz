# Plants vs Zombies - Simplified

一个使用 Python + Pygame 编写的简化版《植物大战僵尸》塔防 Demo。项目以单文件玩法原型为主，包含种植、阳光经济、波次推进、不同僵尸护甲、小推车、铲子、暂停、胜负结算等核心流程，适合作为学习 Pygame 游戏循环和 2D 塔防逻辑的练习项目。

> 本项目是学习与作品集用途的非官方 Demo，不包含原版游戏资源或商业用途授权。

## 功能特性

- 5 行草坪、植物卡槽、阳光资源和冷却时间系统
- 三种难度：Easy / Normal / Hard
- 四种植物：
  - Sunflower：周期性产出阳光
  - Peashooter：向右发射豌豆攻击僵尸
  - Wallnut：高血量阻挡单位
  - Cherry Bomb：延迟爆炸，范围清场
- 僵尸波次系统：
  - 5 波进攻
  - 波次进度条
  - 开局倒计时和波次提醒
  - 普通僵尸、路障配饰、铁桶配饰
- 配饰护甲机制：
  - 路障和铁桶作为独立配饰叠加在普通僵尸上
  - 配饰有独立血量
  - 配饰被打掉后僵尸变回普通形态
  - 伤害不会从配饰溢出到本体
- 每行一个小推车：
  - 僵尸突破防线时自动触发
  - 推车会清理该行经过的僵尸
  - 每行只能触发一次
- 铲子工具：
  - 点击铲子进入移除模式
  - 点击已种植物格子移除植物
  - 右键可取消铲子或卡片选择
- 暂停、胜利、失败和重开流程

## 运行方式

确保本机安装了 Python 3 和 Pygame。

```powershell
python -m pip install pygame
python pvz.py
```

在 Windows 上，也可以直接双击项目根目录的 `启动游戏.bat` 启动游戏。启动失败时，窗口会保留错误信息；请先按上方命令安装 Python 或 Pygame 后再重试。

## Automated regression tests

The tests run Pygame with the dummy SDL driver and do not open a game window:

```powershell
python -m unittest discover -s tests -v
```

They cover first-wave timing, zombie blocking, pea targeting, mower kills, win/loss flow, sun collection, and wave counts for all difficulties.

## Window controls

The game keeps its original logical layout while scaling to the window size. Drag the native title bar to move the window; drag its edges or corners to resize it. Black bars preserve the game's aspect ratio on non-matching window sizes.

如果已经安装过 Pygame，直接运行：

```powershell
python pvz.py
```

## 操作说明

- 鼠标左键点击植物卡片：选择要种植的植物
- 鼠标左键点击草坪格子：放置选中的植物
- 鼠标左键点击阳光：收集阳光
- 鼠标左键点击铲子：进入或退出铲除模式
- 铲除模式下点击植物：移除该植物
- 鼠标右键：取消当前卡片或铲子选择
- `ESC`：暂停 / 继续，或从难度选择返回菜单
- `R`：在胜利或失败界面重新开始

## 项目结构

```text
.
├── pvz.py
└── assets/
    ├── bucket_accessory.png
    ├── cherry_bomb_cut.png
    ├── cherry_bomb_warn.png
    ├── cone_accessory.png
    ├── explosion.png
    ├── lawn_checker_mild.png
    ├── lawn_mower.png
    ├── peashooter_right_cut.png
    ├── shovel_cut.png
    ├── sun_cut.png
    ├── sunflower_cut.png
    ├── wallnut_cut.png
    └── zombie_cut.png
```

## 实现要点

- `pvz.py` 保持单文件结构，便于阅读和快速迭代
- 顶部集中定义网格尺寸、植物数值、僵尸数值、波次参数和资源路径
- `Plant` 及其子类负责植物状态与行为
- `Zombie` 使用普通本体加配饰的方式实现路障/铁桶僵尸
- `WaveManager` 负责波次节奏、生成间隔和难度缩放
- `Game` 负责资源加载、输入处理、状态切换、更新和绘制
- 使用 `dt` 驱动移动、攻击、冷却、阳光下落和动画计时

## 当前状态

核心玩法链路已经完整：从菜单开始、选择难度、种植防守、波次推进，到胜利/失败结算都可以运行。当前更偏向可玩的训练 Demo，而不是完整复刻版。

## 已知问题

- 同排存在多个僵尸时，豌豆命中目标的顺序仍有改进空间
- 数值平衡仍需要更多实机通关测试
- 美术资源以项目当前可用贴图为主，后续可以继续统一风格
