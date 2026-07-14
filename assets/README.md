# Assets

`pvz.py` 从此目录加载运行时资源。静态贴图和逐帧动画分开维护，避免根目录堆放 PNG。

```text
assets/
├── static/                 # `ASSET_FILES` 中登记的基础贴图
│   ├── plants/             # 植物本体与樱桃炸弹预警图
│   ├── zombies/            # 僵尸本体及路障、铁桶配件
│   ├── processed/          # 去除烘焙阴影后的静态副本，保留原图
│   ├── board/              # 草坪底图和割草机
│   ├── items/              # 铲子、阳光等可交互物品
│   └── effects/            # 独立特效，例如爆炸
└── animations/             # `manifest.json` 管理的逐帧动画
    ├── processed/          # 去除烘焙阴影后的逐帧副本
    └── <character>/<state>/<frame>.png
```

维护约定：

- 移动或重命名 `static/` 下的文件时，同步更新 `pvz.py` 的 `ASSET_FILES`。
- 新动画帧使用 PNG，放入角色/状态目录，并在 `animations/manifest.json` 登记相对路径、时长和循环方式。
- 动画帧必须保持透明背景；角色帧由加载器按底部居中锚点归一化，避免画面跳动。
- 如需消除烘焙阴影，保留原图并写入 `processed/` 副本；统一落地阴影由渲染层绘制，僵尸使用缩小三分之一的版本。
