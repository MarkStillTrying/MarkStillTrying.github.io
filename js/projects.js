// 作品列表：加一款游戏就在这里加一条，首页会自动多出一张海报。
// 字段：
//   id        文件夹 / 链接用的英文名
//   name, en  中文名、英文名
//   status    海报左上角的红章（开发中 / 测试中 / 已上线），不写就不盖章
//   state     给玩家看的一句话：现在能不能玩、在哪玩
//   platform  平台（会变成第一个标签）
//   tags      海报上的标签
//   blurb     一句话介绍
//   role      给招聘方看的：这项目我做了什么、用了什么
//   page      介绍页（没有就不出「看介绍」按钮）
//   download  下载链接。没有就不显示下载按钮，只写一句 soon 里的话
//   soon      下载没开放时写的那句话（不写就是「下载还没开放」）
//   cover     海报上的图：bg 背景图，sprites 站在前面的动物（按顺序排开，站不下的自动藏起来）
//   coverAlt  封面图给读屏软件念的一句话
//   fix       海报怎么贴在墙上：tape（两角胶带）/ tape-top（中间一条胶带）/ pins（图钉）
//   curl      右下角要不要卷起来
//   seed      撕边的随机种子，换个数字撕边就不一样
window.PROJECTS = [
  {
    id: "ferazoic",
    name: "兽变纪元",
    en: "FERAZOIC",
    status: "开发中",
    state: "安卓 · 测试服已上线，还没开放下载",
    platform: "安卓",
    tags: ["城建", "养成", "自动战斗", "多人"],
    blurb: "末日之后，动物们发生了突变。挖一座地下避难所，招募突变动物，在禁区里和其他玩家抢地盘。",
    role: "一个人做：程序、美术、策划、服务器（Unity · C# · ASP.NET Core）",
    page: "ferazoic.html",
    download: null,
    soon: "下载还没开放",
    cover: {
      bg: "assets/games/ferazoic/chapter1.png",
      sprites: ["mutant_dog", "porcupine"]
    },
    coverAlt: "兽变纪元的游戏画面：废墟城市前站着突变犬和豪猪",
    fix: "tape",
    curl: true,
    seed: 1
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
