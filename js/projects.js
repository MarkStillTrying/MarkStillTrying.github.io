// 作品列表：加一款游戏就在这里加一条，首页往下翻会自动多出一段，用它自己的画风。
// 字段：
//   id        文件夹 / 链接用的英文名；首页那一段的锚点是 #p-<id>
//   theme     画风。css/site.css 里 .t-<theme> 那一节定义面板、按钮、底纹用什么图；不写就是本站默认的旧海报
//   name, en  中文名、英文名
//   status    角上的标记（开发中 / 测试中 / 已上线），不写就不显示
//   state     给玩家看的一句话：现在能不能玩、在哪玩
//   platform  平台（会变成第一个标签）
//   tags      标签
//   blurb     一句话介绍
//   role      给招聘方看的：这项目我做了什么、用了什么
//   page      详情页（没有就不出「看详情」按钮）
//   showcase  首页那一段上面的展示窗：bg 背景图，sprites 站在前面的动物（按顺序排开，站不下的自动藏起来），label 左下角的小牌子，alt 给读屏软件念的
//   tiles     首页那一段里的小格子（项目里的美术）：img 图，name 名字
//   downloads 下载，按渠道分（测试服 / 正式服），每个渠道下按平台写（android / ios）。每个平台：
//               url      下载链接。安卓指向测试服的「最新安装包」接口（/api/apk/latest：服务器永远给它上面最新的一个包，
//                        发新版不用改网站）；苹果填 TestFlight 公开链接。空着就显示「准备中」
//               hint     写在按钮旁边的一句话（比如「永远是最新版」）。测试服没开跨域，网页读不到版本号和大小，只能写死一句
//               release  （可选）安卓去 GitHub 仓库查最新 Release（owner/repo）：没发过显示「准备中」，发过就把按钮指到里面的 .apk、
//                        显示版本、大小、日期。现在不用：安装包传在测试服上，不发在 GitHub
//               label    按钮上的字
//               notes    装的时候要注意的几句话，逐条显示
//   soon      一个平台都没开放时写的那句话（不写就是「下载还没开放」）
window.PROJECTS = [
  {
    id: "ferazoic",
    theme: "ferazoic",
    name: "兽变纪元",
    en: "FERAZOIC",
    status: "开发中",
    state: "安卓测试版 · 苹果版准备中",
    platform: "安卓",
    tags: ["城建", "养成", "自动战斗", "多人"],
    blurb: "末日之后，动物们发生了突变。挖一座地下避难所，招募突变动物，在禁区里和其他玩家抢地盘。",
    role: "一个人做：程序、美术、策划、服务器（Unity · C# · ASP.NET Core）",
    page: "ferazoic.html",
    showcase: {
      bg: "assets/games/ferazoic/chapter1.png",
      sprites: ["mutant_dog", "porcupine", "snapping_turtle", "cobra", "centipede"],
      label: "《兽变纪元》里的突变动物",
      alt: "废墟城市前站着一排突变动物：突变犬、豪猪、鳄龟、眼镜蛇、变异蜈蚣"
    },
    tiles: [
      { img: "assets/games/ferazoic/tiles/nuclear_battery.png", name: "核电池" },
      { img: "assets/games/ferazoic/tiles/mutation_potion.png", name: "突变药剂" },
      { img: "assets/games/ferazoic/tiles/recruit_ticket.png", name: "诱饵罐头" },
      { img: "assets/games/ferazoic/tiles/token_ticket.png", name: "生锈钥匙" },
      { img: "assets/games/ferazoic/tiles/marble.png", name: "弹珠" },
      { img: "assets/games/ferazoic/tiles/battery.png", name: "电池" },
      { img: "assets/games/ferazoic/tiles/scavenge_map.png", name: "拾荒地图" },
      { img: "assets/games/ferazoic/tiles/pull_tab.png", name: "拉环" }
    ],
    downloads: [
      {
        channel: "测试服",
        android: {
          url: "https://47-243-198-46.sslip.io/api/apk/latest",
          hint: "永远是测试服上最新的一版",
          label: "安卓版下载",
          notes: [
            "用手机自带的浏览器打开这个链接下载，微信里打不开。",
            "下载后打开安装包，手机问「允许安装来自此来源的应用」时选允许。",
            "2026 年 11 月 3 日之前装过的要先卸载再装：签名换了，直接覆盖装不上。卸载前先在游戏里设好账号密码，装好后点「账号登录」能回到原来的号。",
            "第一次打开点「注册账号」。",
            "以后有新版本，打开游戏时会自己下载、提示安装，不用再回来下载。",
            "测试版，连的是测试服。"
          ]
        },
        ios: {
          url: null,
          label: "苹果版下载（TestFlight）",
          notes: [
            "先在 App Store 装好 TestFlight，再点链接，按提示安装。"
          ]
        }
      }
    ],
    soon: "下载还没开放"
  }
];

// 动物的精灵图：帧宽高（1 倍像素）、8 帧一圈要多少毫秒。和游戏里的 anim.json 一致。
window.SPRITES = {
  mutant_dog:      { fw: 64,  fh: 64, dur: 880,  sheet: "assets/games/ferazoic/sprites/mutant_dog_idle.png" },
  porcupine:       { fw: 112, fh: 80, dur: 1000, sheet: "assets/games/ferazoic/sprites/porcupine_idle.png" },
  snapping_turtle: { fw: 112, fh: 80, dur: 1120, sheet: "assets/games/ferazoic/sprites/snapping_turtle_idle.png" },
  cobra:           { fw: 112, fh: 80, dur: 1040, sheet: "assets/games/ferazoic/sprites/cobra_idle.png" },
  centipede:       { fw: 112, fh: 80, dur: 1040, sheet: "assets/games/ferazoic/sprites/centipede_idle.png" }
};
