# 机场自动签到
**使用Github Actions自动签到是违反了Github Actions条款的，如果仍需使用请fork后添加删除的两个yml自行使用**

做这个项目主要是看到最近冒出来许多机场注册就能白嫖，签到就送流量。然后又顺便拿这个项目学习一下Github Actions。
请注意，本项目不讨论跟fq有兽的话题，仅仅是技术讨论，不要询厞白嫖jc等内容！！！
## 功能

废话，肯定就是机场自动签到啊。
## 本地运行

1. 复制 `.env.example` 为 `.env`，按下方"部署"表格填写参数（`.env` 已被 `.gitignore` 忽略，请勿提交到仓库）：

   ```
   cp .env.example .env
   ```

2. 安装依赖并运行：

   ```
   pip install -r requirements.txt
   python main.py
   ```

> 参数读取优先级：环境变量 > `.env` 文件。GitHub Actions 场景下无需创建 `.env`，直接在 Secrets 中配置即可，两种方式互不影响。

## 部署

https://xcao.top/post-278.html 水个博文，操作更详细

1. Fork此仓库
2. 到`Settings`→`Secrets`→`Actions` 添加以下参数：

| 参数  | 是否必须  | 内容  | 示例  |
| ------------ | ------------ | ------------ | ------------ |
| EMAIL  | 是  | 注册机场所用邮箱  | a@example.com  |
| PASSWORD  | 是  | 注册机场所用密码  | password1  |
| BASE_URL  | 是  | 机场地址（不要带 /user 后缀）  | https://examplea.com  |
| BASE_URL2 | 否  | 第二站机场地址，账号缺省时复用第一站  | https://exampleb.com  |
| EMAIL2 / PASSWORD2 | 否  | 第二站账号，不填则复用 EMAIL / PASSWORD  |  |
| SCKEY  | 否  | Sever酱秘钥  | SCTxxxxxxxxxxxxxx  |
| TGBOT  | 否  | Telegram推送bot  | 5xxxxxxx:xxxxxxxxx  |
| TGUSERID  | 否  | Telegram推送人id  | 8xxxxxxxxx  |

> 多站支持：按 `BASE_URL2` → `BASE_URL3` → … 顺序自动循环签到所有已配置站点，每站签到结果分行输出。`BASE_URL` 为根地址，脚本会自动拼接 `/auth/login` 与 `/user/checkin`。

3. 转到`Actions`创建一个workflow，运行一次，以后每天项目都会自动运行。最后，可以到Run sign查看签到情况，同时也会通过Sever酱发送出去。
## 参考
1. https://github.com/zhjc1124/ssr_autocheckin 用了他的机场签到代码。
2. https://github.com/sirodeneko/genshin-sign 参考其Actions的yml。
~~（两个仓库均无许可证，让我有点蒙）~~
最近仓库https://github.com/sirodeneko/genshin-sign 增加了GPL许可证，在征求作者同意后，本仓库依旧保持使用MIT许可证进行开源，以下为与作者通信邮件
[![](https://raw.githubusercontent.com/xiaocao666tzh/imghosting/main/image.png)](https://raw.githubusercontent.com/xiaocao666tzh/imghosting/main/image.png)
