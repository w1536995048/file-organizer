# file-organizer 智能文件整理工具

下载文件夹堆了几百个文件？一个命令自动按类型分类归档。

## 功能

- 按文件类型自动分类：图片 / 视频 / 音频 / 文档 / 压缩包 / 程序 / 代码 / 其他
- `--dry-run` 试运行模式：先预览，不实际移动
- `--by-date`：分类下再按年月分子目录
- `--undo`：一键撤销上次整理（带操作日志）
- 同名文件自动加序号，永不覆盖

## 安装

无需第三方依赖，Python 3.6+ 直接运行。

## 用法

```bash
# 先预览（推荐第一次用）
python organizer.py ~/Downloads --dry-run

# 正式整理
python organizer.py ~/Downloads

# 分类 + 按年月分子目录
python organizer.py ~/Downloads --by-date

# 撤销上一次整理
python organizer.py --undo
```

## 示例

```
$ python organizer.py ~/Downloads --dry-run
[试运行] 共 5 个文件：
  vacation.jpg  ->  图片/vacation.jpg
  report.pdf    ->  文档/report.pdf
  song.mp3      ->  音频/song.mp3
  backup.zip    ->  压缩包/backup.zip
  setup.exe     ->  程序/setup.exe

试运行模式，未实际移动。如确认请去掉 --dry-run。
```

## 自定义分类

直接编辑 `organizer.py` 顶部的 `CATEGORIES` 字典即可增删分类与后缀。

## License

MIT
