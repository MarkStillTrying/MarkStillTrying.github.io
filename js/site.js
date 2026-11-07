// 页面上的小零件：撕边、动物精灵、首页的项目段落、下载按钮（写了 release 的还会去查 GitHub Release）。
(function () {
  // 固定种子的随机数，同一张海报每次打开撕得一样
  function rng(seed) {
    var s = (seed * 9301 + 49297) % 233280;
    return function () { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  }

  // 撕边：四条边各一串随机凹进去的点（3 像素一格，有台阶感），右下角可以按卷角裁掉一个三角
  function tornEdge(seed, curl) {
    var r = rng(seed), pts = [];
    function d() { return Math.floor(r() * 4) * 3; }
    var i, n;
    for (i = 0, n = 14; i <= n; i++) pts.push((i / n * 100).toFixed(1) + "% " + d() + "px");
    for (i = 1, n = 10; i <= n; i++) {
      if (curl && i === n) break;
      pts.push("calc(100% - " + d() + "px) " + (i / n * 100).toFixed(1) + "%");
    }
    if (curl) { pts.push("100% calc(100% - 60px)"); pts.push("calc(100% - 60px) 100%"); }
    for (i = curl ? 1 : 0, n = 14; i <= n; i++) pts.push(((1 - i / n) * 100).toFixed(1) + "% calc(100% - " + d() + "px)");
    for (i = 1, n = 10; i < n; i++) pts.push(d() + "px " + ((1 - i / n) * 100).toFixed(1) + "%");
    return pts.join(",");
  }

  // 给一张海报套上撕边和贴法。fix: tape / tape-top / pins；curl: 右下角卷起来
  function dressPoster(el, opts) {
    var wrap = el.parentElement;
    el.style.setProperty("--cut", tornEdge(opts.seed || 1, !!opts.curl));
    var fix = opts.fix || "tape";
    var parts = fix === "pins" ? ["pin tl", "pin tr"] : fix === "tape-top" ? ["tape t"] : ["tape tl", "tape tr"];
    if (opts.curl) parts.push("curl");
    parts.forEach(function (cls) { var i = document.createElement("i"); i.className = cls; wrap.appendChild(i); });
  }

  // 一只会动的动物
  function sprite(unit) {
    var s = window.SPRITES[unit]; if (!s) return null;
    var el = document.createElement("i");
    el.className = "sprite"; el.setAttribute("aria-hidden", "true");
    el.style.setProperty("--fw", s.fw); el.style.setProperty("--fh", s.fh);
    el.style.setProperty("--dur", s.dur + "ms"); el.style.backgroundImage = "url(" + s.sheet + ")";   // 直接写在元素上，变量里的 url 会按 css 文件的位置找
    el.dataset.fw = s.fw;
    return el;
  }

  // 把舞台上的动物排开：按舞台现在的宽度，一只占 72 像素（× 倍数）的位置，居中站成一排；站不下的藏起来。
  // 展示窗的宽度随屏幕变，所以位置不能写死，窗口一变就重排。
  function layoutStage(stage) {
    var s = parseFloat(getComputedStyle(stage).getPropertyValue("--s")) || 3;
    var kids = stage.querySelectorAll(".sprite"); if (!kids.length) return;
    var W = stage.clientWidth, slot = 72 * s, show = Math.max(1, Math.min(kids.length, Math.floor(W / slot)));
    for (var i = 0; i < kids.length; i++) {
      var el = kids[i];
      if (i >= show) { el.style.display = "none"; continue; }
      el.style.display = "";
      var fw = (+el.dataset.fw || 112) * s;
      var x = Math.round(W / 2 + (i - (show - 1) / 2) * slot - fw / 2);
      el.style.left = Math.round(x / s) * s + "px";   // 对齐到整像素，图才清楚
    }
  }
  function layoutAllStages() { Array.prototype.forEach.call(document.querySelectorAll(".stage[data-auto]"), layoutStage); }

  // 吉祥物那一排：每只跳的节奏错开；每隔几秒随机挑一只转身看另一边，过一会儿转回来。系统设了「减少动态」就都不动
  // 首页那一排吉祥物：放不下就从两头轮流往里藏，剩下的左半边朝右、右半边朝左（翻面），各自蹦、偶尔转个身
  function liveMascots(row) {
    var all = Array.prototype.slice.call(row.querySelectorAll(".m")); if (!all.length) return;
    var r = rng(7), shown = all;
    all.forEach(function (m) {
      var img = m.querySelector("img");
      if (img) { img.style.setProperty("--w", img.getAttribute("width")); img.style.setProperty("--h", img.getAttribute("height")); }
      m.style.setProperty("--hd", (1000 + Math.floor(r() * 500)) + "ms");
      m.style.setProperty("--hdelay", "-" + Math.floor(r() * 1000) + "ms");
    });
    function fit() {
      var ms = parseFloat(getComputedStyle(row).getPropertyValue("--ms")) || 1;
      var gap = 12 * ms, avail = (row.closest("header") || row.parentNode || row).clientWidth;   // 按整个第一屏的宽算，不按那句话的宽
      var w = all.map(function (m) { var img = m.querySelector("img"); return (img ? parseInt(img.getAttribute("width"), 10) : 0) * ms; });
      var lo = 0, hi = all.length, cutLeft = true;
      while (hi - lo > 1) {
        var total = gap * (hi - lo - 1);
        for (var i = lo; i < hi; i++) total += w[i];
        if (total <= avail) break;
        if (cutLeft) lo++; else hi--;
        cutLeft = !cutLeft;
      }
      shown = all.slice(lo, hi);
      all.forEach(function (m, i) { m.classList.toggle("hide", i < lo || i >= hi); });
      shown.forEach(function (m, i) { m.classList.toggle("flip", i >= Math.ceil(shown.length / 2)); });
    }
    fit();
    var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(fit, 100); });
    if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    function turn() {
      var m = shown[Math.floor(r() * shown.length)], img = m.querySelector("img"); if (!img) return;
      var face = m.classList.contains("flip") ? 1 : -1;   // 转到和平时相反的那边
      img.style.setProperty("--face", face);
      setTimeout(function () { img.style.removeProperty("--face"); }, 900 + Math.floor(r() * 1500));
    }
    (function loop() { setTimeout(function () { turn(); loop(); }, 2500 + Math.floor(r() * 3500)); })();
  }

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  // 查 GitHub 上最新的 Release：有就回 { tag, date, apk: { url, size } }，没发过回 null，查不了（限流、断网）回 undefined。
  // 同一个仓库只查一次，结果在本次会话里记 10 分钟（GitHub 不登录每小时只让查 60 次）
  var releaseCache = {};
  function latestRelease(repo, cb) {
    if (!repo) { cb(undefined); return; }
    var key = "release:" + repo, cached;
    try { cached = JSON.parse(sessionStorage.getItem(key) || "null"); } catch (e) { cached = null; }
    if (cached && Date.now() - cached.at < 600000) { setTimeout(function () { cb(cached.data); }, 0); return; }   // 等按钮先放进页面再回调
    if (releaseCache[repo]) { releaseCache[repo].push(cb); return; }
    releaseCache[repo] = [cb];
    function done(data) {
      try { if (data !== undefined) sessionStorage.setItem(key, JSON.stringify({ at: Date.now(), data: data })); } catch (e) {}
      releaseCache[repo].forEach(function (f) { f(data); }); delete releaseCache[repo];
    }
    if (!window.fetch) { done(undefined); return; }
    fetch("https://api.github.com/repos/" + repo + "/releases/latest", { headers: { Accept: "application/vnd.github+json" } }).then(function (r) {
      if (r.status === 404) return null;
      if (!r.ok) return undefined;
      return r.json().then(function (j) {
        var apk = null;
        (j.assets || []).forEach(function (a) { if (!apk && /\.apk$/i.test(a.name)) apk = { url: a.browser_download_url, size: a.size }; });
        return { tag: j.tag_name, name: j.name, date: j.published_at, apk: apk };
      });
    }).then(done, function () { done(undefined); });
  }
  function fmtSize(b) { return b >= 1048576 ? (b / 1048576).toFixed(b >= 10485760 ? 0 : 1) + " MB" : Math.round(b / 1024) + " KB"; }
  function fmtDate(iso) { var d = new Date(iso); return isNaN(d) ? "" : d.getFullYear() + " 年 " + (d.getMonth() + 1) + " 月 " + d.getDate() + " 日"; }

  // 一个平台的下载按钮。能下：按钮；还不能：「准备中」的说明。
  // 安卓要查 Release：查到就把链接换成里面的 .apk，并在 info 里写版本、大小、日期；确定没发过就换成「准备中」；查不了就保持固定链接
  function platformButton(d, platName, info) {
    if (!d.url) return el("span", "gbtn off", platName + "版准备中");
    var a = el("a", "gbtn ok", d.label || (platName + "版下载")); a.href = d.url;
    if (d.hint && info) info.textContent = d.hint;
    if (d.release) latestRelease(d.release, function (rel) {
      if (rel === null) { if (a.parentNode) a.parentNode.replaceChild(el("span", "gbtn off", platName + "版准备中"), a); if (info) info.textContent = ""; return; }
      if (!rel) return;
      if (rel.apk) a.href = rel.apk.url;
      if (info) info.textContent = [rel.tag, rel.apk ? fmtSize(rel.apk.size) : "", fmtDate(rel.date)].filter(Boolean).join(" · ");
    });
    return a;
  }
  var PLATFORMS = [["android", "安卓"], ["ios", "苹果"]];

  // 首页：每个项目一段，用它自己的画风（class t-<theme>）。结构都一样，样子由 css 里的主题决定
  function renderProjects(root) {
    (window.PROJECTS || []).forEach(function (p) {
      var sec = el("section", "project" + (p.theme ? " t-" + p.theme : "")); sec.id = "p-" + p.id;
      sec.setAttribute("aria-label", p.name);
      var inner = el("div", "inner"); sec.appendChild(el("div", "band")).appendChild(inner);
      if (p.showcase) {
        var win = el("div", "window"); win.setAttribute("role", "img"); win.setAttribute("aria-label", p.showcase.alt || p.name);
        if (p.showcase.bg) win.style.backgroundImage = "url(" + p.showcase.bg + ")";
        var stage = el("div", "stage"); stage.setAttribute("data-auto", "");
        (p.showcase.sprites || []).forEach(function (u) { var e = sprite(u); if (e) stage.appendChild(e); });
        win.appendChild(stage);
        if (p.showcase.label) win.appendChild(el("span", "label", p.showcase.label));
        inner.appendChild(win);
      }
      var panel = el("div", "panel"); inner.appendChild(panel);
      var head = el("div", "phead"); panel.appendChild(head);
      var h = el("h2", null, p.name); if (p.en) { h.appendChild(document.createTextNode(" ")); h.appendChild(el("small", null, p.en)); } head.appendChild(h);
      if (p.status) head.appendChild(el("span", "status", p.status));
      if (p.state) panel.appendChild(el("div", "state", p.state));
      var tags = el("div", "tags"); [p.platform].concat(p.tags || []).filter(Boolean).forEach(function (t) { tags.appendChild(el("span", "chip", t)); }); panel.appendChild(tags);
      if (p.blurb) panel.appendChild(el("p", "blurb", p.blurb));
      if (p.role) panel.appendChild(el("div", "role", p.role));
      if (p.tiles && p.tiles.length) {
        var tiles = el("div", "tiles");
        p.tiles.forEach(function (t) { var f = el("figure", "tile"); var im = el("img"); im.src = t.img; im.alt = t.name; im.width = 56; im.height = 56; f.appendChild(im); f.appendChild(el("figcaption", null, t.name)); tiles.appendChild(f); });
        panel.appendChild(tiles);
      }
      var btns = el("div", "btns"); panel.appendChild(btns);
      if (p.page) { var go = el("a", "gbtn", "看详情 →"); go.href = p.page; btns.appendChild(go); }
      var ch = (p.downloads || [])[0];
      if (ch) PLATFORMS.forEach(function (pl) { if (ch[pl[0]]) btns.appendChild(platformButton(ch[pl[0]], pl[1], null)); });
      else btns.appendChild(el("span", "gbtn off", p.soon || "下载还没开放"));
      root.appendChild(sec);
    });
  }

  // 详情页的下载区：<div data-downloads="ferazoic"></div>，按 PROJECTS 里那一条的 downloads 生成：每个渠道一块，里面每个平台一行
  function renderDownloads(root) {
    var p = (window.PROJECTS || []).filter(function (x) { return x.id === root.getAttribute("data-downloads"); })[0];
    if (!p || !p.downloads || !p.downloads.length) { root.appendChild(el("span", "gbtn off", (p && p.soon) || "下载还没开放")); return; }
    p.downloads.forEach(function (ch) {
      var block = el("div", "channel");
      if (ch.channel) block.appendChild(el("h3", null, ch.channel));
      PLATFORMS.forEach(function (pl) {
        var d = ch[pl[0]]; if (!d) return;
        var row = el("div", "dlrow"); row.appendChild(el("h4", null, pl[1]));
        var line = el("div", "btns"); var info = el("span", "ver");
        line.appendChild(platformButton(d, pl[1], info)); line.appendChild(info); row.appendChild(line);
        if (d.notes && d.notes.length) { var ul = el("ul", "notes"); d.notes.forEach(function (t) { ul.appendChild(el("li", null, t)); }); row.appendChild(ul); }
        block.appendChild(row);
      });
      root.appendChild(block);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var list = document.querySelector("[data-projects]"); if (list) renderProjects(list);
    Array.prototype.forEach.call(document.querySelectorAll("[data-downloads]"), renderDownloads);
    // 页面里写死的海报：data-poster="种子" data-fix="tape" data-curl
    Array.prototype.forEach.call(document.querySelectorAll("[data-poster]"), function (e) {
      dressPoster(e, { seed: +e.getAttribute("data-poster") || 1, fix: e.getAttribute("data-fix"), curl: e.hasAttribute("data-curl") });
    });
    // 页面里写死的动物：<div class="stage" data-sprites="mutant_dog,cobra" data-auto>（data-auto 自动排开）
    Array.prototype.forEach.call(document.querySelectorAll("[data-sprites]"), function (st) {
      st.getAttribute("data-sprites").split(",").forEach(function (item) { var e = sprite(item.trim()); if (e) st.appendChild(e); });
    });
    Array.prototype.forEach.call(document.querySelectorAll(".mascots"), liveMascots);
    layoutAllStages();
    var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(layoutAllStages, 100); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layoutAllStages);
  });
})();
