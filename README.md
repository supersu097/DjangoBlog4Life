# DjangoBlog4Life
:snake:一个WordPress主题的Django博客

## Philosophy
- WordPress主题做前端，后端由Django驱动
- 轻量化，数据库默认采用Sqlite，可自行升级为MySQL
- 永远基于Django最新的LTS版本，不追新立异
- 推荐采用Linux+Nginx+Sqlite+Python3.6架构
- 推荐Nginx采用Yum默认的版本，Python也用CentOS7默认的3.6，二者均不自行编译
- VPS单一用途的话，推荐可不采用Virtualenv虚拟环境部署

## Features
### 特色功能：
- 集成了虎皮椒支付，支持付费阅读
- 支持Google Adsense，全站共3个广告位
- 支持Mac风格的代码高亮

### 一般功能：
- 完整移植了WordPress传统博客主题的搜索、分类、归档、最新评论、标签云、友链侧边栏小工具
- 支持Gravatar头像，支持自定义国内镜像
- 支持最多5级嵌套评论，评论支持分页
- 用户评论和后台文章编辑均支持富文本操作
- 用户评论和收到付费阅读的文章费用后发送邮件通知站长
- 用户评论支持验证码
- 用户评论时强制对邮箱有效性进行校验
- 简单移植了WordPress的评论审核功能

### 安全特性：
- 强制采用含有随机字符串的后台url
- 生产环境的settings_prod.py配置开启了Django的全部安全特性，防XSS，防SQL注入等

## Todo
- 支持发表文章后自动推送给百度
- 有人发表了评论自动给父级评论者发送邮件通知

## Deploy
暂无，后续详见博客。
