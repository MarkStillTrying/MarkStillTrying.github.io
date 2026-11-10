// 手机上的字号，加上物品格子的大小（格子那一条电脑上也用；电脑上别的字还是 24、36、72 这些 12 的倍数）。
//
// 网站用的是像素字体 Fusion Pixel：一个字是 12×12 个「字体像素」。字要清楚，每个字体像素得正好占整数个屏幕像素。
// 字号 F（CSS 像素）× 这台手机的屏幕密度 D ÷ 12 = 一个字体像素占几个屏幕像素；要它是整数 k，F 就得等于 12 × k ÷ D。
// 每台手机的屏幕密度不一样（苹果多是 3，也有 2；安卓有 2.625、2.75、3、3.5……），所以没有哪个固定的字号在所有手机上都清楚：
// 密度 3 的手机 16 是清楚的、18 发虚，密度 2 的手机正好反过来。
// 这里按想要的大小（正文 17、第一屏那句话 20、小标题 24、店招 36）给这台手机找最近的那个清楚的字号，写进 CSS 变量，css/site.css 里手机那几节用它。
//
// 放在 <head> 里、样式表前面先跑：页面第一次画出来时字号已经定了，不会先大后小跳一下。
// 没开 JavaScript 时用 css 里 :root 写的备用字号。
(function () {
  var GRID = 12;   // 字体的格子：12 像素一个字
  var MIN = 14;    // 正文算出来比这还小就再大一档（太小看不清）
  var last = 0;    // 上一次算的时候的屏幕密度：没变就不用再算
  function apply() {
    var d = window.devicePixelRatio || 1;
    if (d === last) return;
    last = d;
    function near(px, min) {   // 离 px 最近的那一档（一档 = 一个字体像素占几个屏幕像素）；给了 min 就不小于 min
      var k = Math.max(1, Math.round(px * d / GRID));
      if (min && GRID * k / d < min) k++;
      return k;
    }
    function down(px) { return Math.max(1, Math.floor(px * d / GRID)); }   // 不超过 px 的最大一档（放不下就不行的地方用）
    // 正文按「14～18」取中间偏大的 17：像素字笔画粗，太小了难认
    var body = near(17, MIN);
    var head = Math.max(body + 1, near(24));   // 小标题至少比正文大一档
    var sizes = {
      "--f-body": body,                              // 正文、按钮、标签
      "--f-lead": Math.max(body, near(20)),          // 第一屏那句话
      "--f-head": head,                              // 小标题
      "--f-sign": Math.max(head, down(36)),          // 店招：最大 36，再大 360 宽的手机上牌子比屏幕宽
      "--f-sign-s": down(32),                        // 320 宽的小手机上的店招：最大 32
      "--f-big": Math.max(head + 1, down(36)),       // 详情页的游戏名：至少比小标题大一档
      // 物品格子下面的小字，格子的大小跟着它走（格子宽 56/12 个字，见 css 的 .tiles），电脑上也用：
      "--f-cap": near(13, 11.5),                     // 手机：12～14，格子 56～64，一排四个
      "--f-cap-d": near(15.5)                        // 电脑：普通显示器 12（格子 56），高清屏 18（格子 84），一排八个
    };
    var style = document.documentElement.style;
    for (var name in sizes) style.setProperty(name, (GRID * sizes[name] / d).toFixed(5) + "px");
  }
  apply();
  window.addEventListener("resize", apply);   // 电脑上缩放网页、把窗口拖到另一块屏幕时，屏幕密度会变
})();
