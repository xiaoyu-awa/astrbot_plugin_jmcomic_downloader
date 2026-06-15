astrbot-plugin-jmcomic_downloader

---

# 禁漫本子下载器

## 指令

| 指令 | 说明 |
|------|------|
| `/jmv [id]` | 查询对应本子详细信息 |
| `/jm [id]` | 下载对应本子 |

## 依赖

- `jmcomic`
- `img2pdf`

## 配置

在插件目录下有jmcomic.yml文件
配置项可在[jmcomic](https://jmcomic.readthedocs.io/zh-cn/latest/option_file_syntax/)找到

## TODO

>1.配置jmcomic库中的可选项
>2.自动清理下载的pdf
>3.优化逻辑 防呆机制等

## 引用

- [jmcomic](https://github.com/hect0x7/JMComic-Crawler-Python)（其实核心全靠这个库了x）