# 个人项目网站

像素风的静态网页，放我做的游戏：介绍、截图和下载。用 GitHub Pages 托管，不用任何框架和构建工具，改完文件推上去就生效。

## 文件

- `index.html`：首页。从上到下：店招、动物橱窗、物品橱窗、项目（作品海报由 `js/projects.js` 里的列表生成）、关于。
- `ferazoic.html`：《兽变纪元》介绍页。
- `js/projects.js`：**作品列表**。加一款游戏就在这里加一条（字段说明写在文件开头）。下载也写在这里（`downloads`）：安卓指向这个仓库最新 Release 里的 .apk，网页打开时自己去查有没有、显示版本和大小，所以发新版只要在 GitHub 发一个 Release，网站不用改；苹果拿到 TestFlight 公开链接后填进 `ios.url`。
- `js/site.js`：撕边、动物精灵动画、首页海报的生成。
- `css/site.css`：样式。`--s` 是像素放大倍数（电脑 3 倍、手机 2 倍）。
- `assets/ui/`：铁皮墙、旧纸、胶带、卷角、图钉、店招的铁牌和链条、蒸笼（都是代码画的像素图；店招那几张由 `tools/sign.py` 画）。
- `assets/games/ferazoic/tiles/`：首页橱窗里的物品格子，用游戏里的图标和品质框拼的。
- `assets/games/<游戏>/`：每款游戏的图：背景、截图、动物精灵图。
- `assets/fonts/`：像素字体 Fusion Pixel（OFL 授权，许可证在旁边）。网页用的是裁过的小字体（只带常用字，156 KB）。
- `tools/subset_font.py`：裁字体的脚本，整套字体（3.4 MB）在 `tools/font/`。网页里加了生僻字、发现某个字变成了别的字体，就在网站根目录跑一次 `python3 tools/subset_font.py`（要先 `pip install fonttools brotli`）。

## 发安卓新版

1. 打开仓库页面右边的 **Releases** → **Draft a new release**（或 Create a new release）。
2. **Choose a tag** 填一个新的版本号（比如 `v0.2`），选 **Create new tag on publish**。
3. 标题随便写（比如 `v0.2`），把安装包拖进下面的附件框，文件名改成 `ferazoic-android.apk`（固定链接靠这个名字；名字不对网页也能找到，但固定链接会失效）。
4. 不要勾 **Set as a pre-release**，点 **Publish release**。
网页会显示最新那个 Release 的版本、大小和日期。

## 本地看

直接双击 `index.html` 就能在浏览器里打开。注意 Chrome 直接打开本地文件时不让网页加载字体，字会变成系统字体，这是 Chrome 对本地文件的限制，放到网上就正常；Safari、Firefox 打开本地文件没这个问题。

## 无障碍和适配

- 文字和底色的对比度都在 4.5:1 以上；键盘 Tab 切到按钮、链接上有黄色焦点框。
- 系统开了「减少动态效果」时动物不动，停在第一帧。
- 没开 JavaScript 时首页仍有一张静态的《兽变纪元》海报能点进介绍页。
