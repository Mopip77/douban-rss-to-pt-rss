# douban-rss-to-pt-rss

将豆瓣中`想看`的影视剧自动生成 pt 站 rss 订阅链接，发送至`qbitorrent`.

##### 效果图

| **豆瓣想看列表**                              | **qb rss 生成效果**                     |
| --------------------------------------------- | --------------------------------------- |
| <img src="images/douban.jpg" width = "300" /> | ![](images/result.png)                  |
|                                               | 会按照`pt站/影片标题`的层级格式进行存储 |

## 需配置的环境变量

| key                       | value example     | description                                                                              |
| ------------------------- | ----------------- | ---------------------------------------------------------------------------------------- |
| DOUBAN_USER_ID            | 12345             | 豆瓣账号 id (可以在个人资料页找到一串数字 id)                                            |
| SITES                     | tjupt,mteam       | 需要搜索的 pt 站名，用逗号分割（[当前支持的 pt 站](#当前支持的pt站名)）                  |
| QB_URL                    | http://qb.xxx.com | qb 地址                                                                                  |
| QB_USER                   | qbit              | qb 用户名                                                                                |
| QB_PWD                    | 12345             | qb 密码                                                                                  |
| tjupt_passkey             | 3j3oi32onf        | 各 pt 站的 passkey，key 的格式为 <pt 站名>\_passkey，例如 tjupt_passkey, chdbits_passkey |
| TELEGRAM_BOT_ENABLE       | true              | 是否启用 telegram bot 消息发送                                                           |
| TELEGRAM_API_ID           | 11111             | telegram api id                                                                          |
| TELEGRAM_API_HASH         | 22222             | telegram api hash                                                                        |
| TELEGRAM_PHONE_NUMBER     | +8613012341234    | telegram 手机号                                                                          |
| TELEGRAM_MESSAGE_TEMPLATE | 想看 {title}      | telegram 消息模板，目前支持 title 变量                                                   |

## 当前支持的 pt 站名

- tjupt
- chdbits

## 运行

该 docker 镜像会在 `8-23点` 每隔 `5分钟` 执行一次，`0-8点` `每个小时` 执行一次

`docker-compose.yml`

```yaml
version: 3

services:
  rss:
    image: mopip77/douban-rss-to-pt-rss
    container_name: douban-rss-to-pt-rss
    restart: unless-stopped
    network_mode: host
    volumes:
      - /path/to/your/config:/app/config
    environment:
      - TZ=Asia/Shanghai
      - DOUBAN_USER_ID=12345
      - SITES=tjupt,chdbits
      - QB_URL=http://127.0.0.1:8083
      - QB_USERNAME=username
      - QB_PWD=password
      - tjupt_passkey=0E43BD4F134F31BCB0C4
      - chdbits_passkey=6B6286D49D4F4E33D5EF
```

如果使用了 telegram 模块，需要创建容器后，在容器内登录 telegram，输入验证码，才可使用

```bash
python login.py
```