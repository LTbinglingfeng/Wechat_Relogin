# Wechat_Relogin
一个便捷管理微信3.9版本登录的小程序

Wechat_Relogin 是一个用于自动登录微信PC版的Python工具，支持自动点击登录按钮并截图保存。该工具特别适用于需要频繁登录微信或与微信机器人集成的场景。

## 功能特点

- 自动关闭并重启微信进程
- 自动识别微信登录窗口并点击登录按钮
- 自动截图并保存微信界面
- 支持同时启动自定义的微信机器人脚本 （您可以将其修改为启动自己的程序）
- 支持高分屏DPI适配，解决截图错位问题
- 命令行参数控制，使用灵活

## 安装要求

- Windows 操作系统
- Python 3.6+
- 微信PC版已安装(3.9版本)
- 依赖库：
  - pywin32
  - Pillow

安装依赖库：
```bash
pip install pywin32 Pillow
```

## 使用方法
直接启动即可 微信登录的结果截图将保存在Wechat_Relogin.py所在的根目录
### 基本使用

```bash
# 仅启动微信并自动登录
python Wechat_Relogin.py -login

# 启动微信并自动登录，同时启动bot.py
python Wechat_Relogin.py -login -bot

# 仅关闭微信进程
python Wechat_Relogin.py -signout

# 关闭微信进程和bot.py
python Wechat_Relogin.py -signout -botout
```

### 参数说明

- `-login`: 启动微信并自动登录
- `-signout`: 关闭微信进程
- `-bot`: 在微信启动后同时启动bot.py
- `-botout`: 在关闭微信时同时关闭bot.py

## 注意事项

1. 请确保微信已安装在默认路径，否则可能无法自动找到微信程序（可自定义路径）
2. 运行时请确保没有其他重要程序在前台运行，因为程序会自动激活微信窗口
3. 首次运行时可能需要允许Python程序的权限请求

## 许可证

本项目采用 GNU Affero General Public License v3.0 许可证。详情请见 [LICENSE](LICENSE) 文件。

Copyright (C) 2025 LTbinglingfeng
