# 个人项目网站

像素风的静态网页，放我做的游戏：介绍、截图和下载。用 GitHub Pages 托管，不用任何框架和构建工具，改完文件推上去就生效。

## 文件

- `index.html`：首页。第一屏只有店招、吉祥物和一句话；往下翻是项目，每个项目一段（按 `js/projects.js` 生成，各用各的画风），最后是「下一个项目」和「关于」。
- **项目画风**：`css/site.css` 最后一节，每个项目一个 `.t-<theme>`（现在只有 `.t-ferazoic`：游戏里的水泥墙、铁框面板、军用铁板按钮、军绿铁皮条、返回木牌，图在 `assets/games/ferazoic/ui/`）。首页那一段和详情页整页都套这个 class。加新项目：在 `projects.js` 加一条、写上 `theme`，再在 css 里加一节 `.t-<theme>` 换掉面板、按钮、底纹用的图。
- `ferazoic.html`：《兽变纪元》介绍页。
- `js/projects.js`：**作品列表**。加一款游戏就在这里加一条（字段说明写在文件开头）。下载也写在这里（`downloads`）：安卓指向这个仓库最新 Release 里的 .apk，网页打开时自己去查有没有、显示版本和大小，所以发新版只要在 GitHub 发一个 Release，网站不用改；苹果拿到 TestFlight 公开链接后填进 `ios.url`。
- `js/site.js`：撕边、动物精灵动画、首页海报的生成。
- `css/site.css`：样式。`--s` 是像素放大倍数（电脑 3 倍、手机 2 倍）。
- `assets/ui/`：铁皮墙、旧纸、胶带、卷角、图钉、店招的铁牌和链条、蒸笼（都是代码画的像素图；店招那几张由 `tools/sign.py` 画）。
- `assets/ui/mascots/`：吉祥物，Mark 画的小笼包（戴王冠的 king、猫脸的 cat、吕布 lvbu），从原图缩回 1 倍像素、去掉背景。网站的图都由 Mark 画，不用代码生成。首页第一屏那一排在 `index.html` 里排（中间放最主要的，放不下时从两头往里藏）；`js/site.js` 的 liveMascots 管藏、翻面（左半边朝右、右半边朝左）、蹦和偶尔转身。
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
