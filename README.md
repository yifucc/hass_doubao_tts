# HomeAssistant 豆包TTS语音合成集成
基于豆包大模型的文本转语音（TTS）服务，为Home Assistant提供原生、稳定的语音合成能力，支持多音色、语速调节等核心功能。

[![HACS](https://img.shields.io/badge/HACS-支持-blue)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.04%2B-orange)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/yifucc/hass_doubao_tts)](LICENSE)

## 功能特性
- ✅ 原生接入Home Assistant TTS核心组件，无缝适配所有媒体播放器
- ✅ 支持豆包官方全品类音色
- ✅ 自定义语速、音量调节

## 前置要求
1. Home Assistant 2026.04 及以上版本
2. 豆包开放平台账号，并已获取 TTS 服务的 API Key、Secret Key
3. 运行环境可正常访问豆包开放平台 API

## 安装方法
### 方法一：HACS 安装（推荐）
1. 打开 Home Assistant → HACS → 集成
2. 点击右上角菜单 → 自定义仓库
3. 输入仓库地址：`https://github.com/yifucc/hass_doubao_tts`，类别选择「集成」
4. 搜索 `Doubao TTS` 完成安装
5. 重启 Home Assistant

### 方法二：手动安装
1. 下载项目源码
2. 将 `custom_components/doubao_tts` 文件夹
3. 上传至 Home Assistant 配置目录下的 `custom_components/` 目录
4. 重启 Home Assistant

## 配置方法
### UI 可视化配置
1. 进入：设置 → 设备与服务 → 添加集成
2. 搜索并选择 `Doubao TTS`
3. 填写 APP ID、Access Token参数
4. 提交并完成集成