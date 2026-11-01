// 页面上的小零件：撕边、动物精灵、首页的作品海报、下载按钮（查 GitHub Release）。
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
  // 封面、顶图的宽度随屏幕变，所以位置不能写死，窗口一变就重排。
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

  // 查 GitHub 上最新的 Release：有就回 { tag, date, apk: { url, size } }，没发过回 null，查不了（限流、断网）回 undefined。
  // 同一个仓库只查一次，结果在本次会话里记 10 分钟（GitHub 不登录每小时只让查 60 次）
  var releaseCache = {};
  function latestRelease(repo, cb) {
    if (!repo) { cb(undefined); return; }
    var key = "release:" + repo, cached;
    try { cached = JSON.parse(sessionStorage.getItem(key) || "null"); } catch (e) { cached = null; }
    if (cached && Date.now() - cached.at < 600000) { cb(cached.data); return; }
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
  // 安卓下载按钮：查到 Release 就把链接换成里面的 .apk，并在 info 里写版本、大小、日期；
  // 确定没发过 Release 就把按钮换成「准备中」；查不了就保持原来的固定链接
  function bindRelease(btn, android, info) {
    latestRelease(android.release, function (rel) {
      if (rel === null) {
        var soon = document.createElement("span"); soon.className = "soon"; soon.textContent = "安卓版准备中";
        var row = btn.parentNode; row.replaceChild(soon, btn);
        // 首页海报上没了下载按钮，「看介绍」顶上当主按钮
        var ghost = row.querySelector(".btn.ghost"); if (ghost) { ghost.className = "btn"; ghost.textContent = "看介绍 →"; row.insertBefore(ghost, row.firstChild); }
        if (info) info.textContent = "";
        return;
      }
      if (!rel) return;
      if (rel.apk) btn.href = rel.apk.url;
      if (info) info.textContent = [rel.tag, rel.apk ? fmtSize(rel.apk.size) : "", fmtDate(rel.date)].filter(Boolean).join(" · ");
    });
  }

  // 介绍页的下载区：<div data-downloads="ferazoic"></div>，按 PROJECTS 里那一条的 downloads 生成
  function renderDownloads(root) {
    var p = (window.PROJECTS || []).filter(function (x) { return x.id === root.getAttribute("data-downloads"); })[0];
    if (!p || !p.downloads) return;
    [["android", "安卓"], ["ios", "苹果"]].forEach(function (pair) {
      var d = p.downloads[pair[0]]; if (!d) return;
      var block = document.createElement("div"); block.className = "dlblock";
      var h = document.createElement("h3"); h.textContent = pair[1]; block.appendChild(h);
      var row = document.createElement("div"); row.className = "btns";
      var info = document.createElement("span"); info.className = "ver dim";
      if (d.url) {
        var a = document.createElement("a"); a.className = "btn"; a.href = d.url; a.textContent = d.label || (pair[1] + "版下载"); row.appendChild(a);
        if (d.release) bindRelease(a, d, info);
      } else {
        var soon = document.createElement("span"); soon.className = "soon"; soon.textContent = pair[1] + "版准备中"; row.appendChild(soon);
      }
      row.appendChild(info); block.appendChild(row);
      if (d.notes && d.notes.length) {
        var ul = document.createElement("ul"); ul.className = "notes";
        d.notes.forEach(function (t) { var li = document.createElement("li"); li.textContent = t; ul.appendChild(li); });
        block.appendChild(ul);
      }
      root.appendChild(block);
    });
  }

  // 首页：按 PROJECTS 生成海报
  function renderProjects(root) {
    var list = window.PROJECTS || [];
    list.forEach(function (p, idx) {
      var wrap = document.createElement("div"); wrap.className = "poster-wrap";
      var card = document.createElement("div"); card.className = "poster card";
      var cover = document.createElement("div"); cover.className = "cover";
      cover.setAttribute("role", "img"); cover.setAttribute("aria-label", (p.coverAlt || p.name + " 的游戏画面"));
      if (p.cover && p.cover.bg) cover.style.backgroundImage = "url(" + p.cover.bg + ")";
      var stage = document.createElement("div"); stage.className = "stage"; stage.setAttribute("data-auto", "");
      ((p.cover && p.cover.sprites) || []).forEach(function (sp) { var e = sprite(typeof sp === "string" ? sp : sp.unit); if (e) stage.appendChild(e); });
      cover.appendChild(stage);
      if (p.status) { var st = document.createElement("span"); st.className = "stamp"; st.textContent = p.status; cover.appendChild(st); }
      card.appendChild(cover);
      var body = document.createElement("div"); body.className = "body";
      var h = document.createElement("h2"); h.textContent = p.name;
      if (p.en) { var en = document.createElement("small"); en.textContent = p.en; h.appendChild(document.createTextNode(" ")); h.appendChild(en); }
      body.appendChild(h);
      // 状态一句话：给玩家看的「能不能玩」
      if (p.state) { var stl = document.createElement("div"); stl.className = "state"; stl.textContent = p.state; body.appendChild(stl); }
      var tags = document.createElement("div"); tags.className = "tags";
      [p.platform].concat(p.tags || []).filter(Boolean).forEach(function (t) { var c = document.createElement("span"); c.className = "chip"; c.textContent = t; tags.appendChild(c); });
      body.appendChild(tags);
      if (p.blurb) { var bl = document.createElement("p"); bl.className = "blurb"; bl.textContent = p.blurb; body.appendChild(bl); }
      // 给招聘方看的：这项目我做了什么
      if (p.role) { var rl = document.createElement("div"); rl.className = "role"; rl.textContent = p.role; body.appendChild(rl); }
      var btns = document.createElement("div"); btns.className = "btns";
      var android = p.downloads && p.downloads.android, ios = p.downloads && p.downloads.ios;
      if ((android && android.url) || (ios && ios.url)) {
        // 有能下的：下载当主按钮，「看介绍」退成虚框。安卓那个还要等查完 Release 再定（见 bindRelease）
        if (android && android.url) { var dl = document.createElement("a"); dl.className = "btn"; dl.href = android.url; dl.textContent = android.label || "安卓版下载"; btns.appendChild(dl); bindRelease(dl, android, null); }
        if (ios && ios.url) { var dli = document.createElement("a"); dli.className = "btn"; dli.href = ios.url; dli.textContent = ios.label || "苹果版下载"; btns.appendChild(dli); }
        if (p.page) { var more = document.createElement("a"); more.className = "btn ghost"; more.href = p.page; more.textContent = "看介绍"; btns.appendChild(more); }
      } else {
        // 还不能下载：能走的「看介绍」当主按钮，「下载」只是一个说明，不做成按钮
        if (p.page) { var go = document.createElement("a"); go.className = "btn"; go.href = p.page; go.textContent = "看介绍 →"; btns.appendChild(go); }
        var soon = document.createElement("span"); soon.className = "soon"; soon.textContent = p.soon || "下载还没开放"; btns.appendChild(soon);
      }
      body.appendChild(btns); card.appendChild(body);
      wrap.appendChild(card); root.insertBefore(wrap, root.querySelector("[data-after-projects]"));
      dressPoster(card, { seed: p.seed || idx + 1, fix: p.fix, curl: p.curl });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var grid = document.querySelector("[data-projects]"); if (grid) renderProjects(grid);
    Array.prototype.forEach.call(document.querySelectorAll("[data-downloads]"), renderDownloads);
    // 页面里写死的海报：data-poster="种子" data-fix="tape" data-curl
    Array.prototype.forEach.call(document.querySelectorAll("[data-poster]"), function (el) {
      dressPoster(el, { seed: +el.getAttribute("data-poster") || 1, fix: el.getAttribute("data-fix"), curl: el.hasAttribute("data-curl") });
    });
    // 页面里写死的动物：<div class="stage" data-sprites="mutant_dog,cobra" data-auto>（data-auto 自动排开）
    Array.prototype.forEach.call(document.querySelectorAll("[data-sprites]"), function (st) {
      st.getAttribute("data-sprites").split(",").forEach(function (item) {
        var e = sprite(item.trim().split("@")[0]); if (e) st.appendChild(e);
      });
    });
    layoutAllStages();
    var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(layoutAllStages, 100); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layoutAllStages);
  });
})();
