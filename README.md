# Cloudflare Turnstile 自动处理（cloudflare-turnstile-solving）

这是一个用于识别并自动处理 Cloudflare Turnstile 验证的简单实现，目标是在自动化测试中应对 Turnstile 验证页面。

本仓库包含多个平台的运行示例与环境说明（Windows、Debian、Alpine/docker 等），以及用于视觉识别的模板图片目录 `template/`。

## 目录概览

- `windows/`、 `linux/` - 平台说明与示例。
- `windows/main.py`、`linux/main.py` - 各平台主程序脚本。
- `windows/template/`、`linux/template/` - 浏览器截图模板，用于OpenCV视觉匹配。
- `windows/requirements.txt` 、 `linux/requirements.txt` - Python 依赖清单。

## 核心特性

- 自动识别 Turnstile 验证区域并尝试交互（基于OpenCV目标识别与自动化操作）。
- 可替换模版图片以适配不同浏览器或分辨率。
- 提供多平台安装与运行说明，便于在容器或本地环境运行。

## 快速开始（通用）

1. 克隆仓库：

```bash
git clone https://github.com/sukafon/cloudflare-turnstile-solving.git
cd cloudflare-turnstile-solving
cd windows/  # 或 cd linux/ 根据你的平台
```

2. 创建并激活虚拟环境（可选但推荐）：

Windows (cmd.exe):

```bat
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS (bash):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

退出虚拟环境

```bash
deactivate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 根据你的平台，参见下面的“平台安装与运行”节运行 windows/ linux 目录下对应的 `main.py`。

## 平台安装与运行说明

下面汇总了仓库中已有的说明：请根据你的系统选择相应小节。

### Windows

在 `windows/windows环境安装指南.txt` 中的步骤：

- 安装依赖：

```bat
pip install -r requirements.txt
```

- 可选：用实际浏览器截图替换 `windows/template/` 中的模板图片，重命名为 `template.png` 和 `sub_template.png`，确保尺寸和位置与浏览器元素一致。

- 运行：

```bat
python main.py
```

### Debian 系（例如 Ubuntu）

在 `Linux/Debian系环境安装指南.txt` 中的步骤：

```bash
pip install -r requirements.txt
chmod +x main.py
python3 main.py
```

同样建议用浏览器截图替换 `template/` 中的模板图片。

### Alpine / Docker（仅在 docker-webtop 容器内测试通过）

在 `Linux/Alpine-Docker环境安装指南.txt` 中给出更详细的包和 OpenCV 安装备选：

- 推荐使用 Alpine 的预编译包：

```bash
sudo apk update
sudo apk add opencv opencv-dev py3-opencv
python3 -c "import cv2; print(cv2.__version__)"
pip install mss python-xlib
chmod +x main.py
python3 main.py
```

- 或者在无法使用系统包时，可编译安装 `opencv-python`（注意编译慢且占空间）。

## 模板图片说明

- 仓库中的 `template/` 和平台子目录包含若干示例模版图像（`template.png`, `sub_template.png`, `template_back.png` 等）。
- 建议使用截图工具（例如 QQ 截图）截取浏览器中 Turnstile 验证块及相关交互控件，保存为 `template.png` 和 `sub_template.png`，并放在相应平台的 `template/` 目录中。

替换模版时注意：分辨率、缩放（浏览器缩放比例）和浏览器主题可能影响目标识别效果。

## 说明文件

- Windows 平台说明：`windows/Windows环境安装指南.txt`
- Debian 平台说明：`linux/Debian系环境安装指南.txt`
- Alpine/docker 说明：`linux/Alpine-Docker环境安装指南.txt`

## 运行流程

- 程序默认每5秒尝试识别一次屏幕中的 Turnstile 验证区域。你可以直接修改代码以符合你的使用需求。

## 常见问题（FAQ）

- 识别失败或识别不准确：
	- 尝试更换或重新截取模板图片，保证元素位置和尺寸一致；
	- 检查屏幕缩放比例（Windows 的显示缩放），尽量使用 100% 缩放；
	- 在不同分辨率或浏览器下调试模板；

- OpenCV 安装失败：
	- 在 Debian/Ubuntu 优先使用系统包或安装头文件后再 pip 安装；
	- 在 Alpine 建议使用 `apk` 提供的预编译包以减少编译问题。

## 开发与贡献

- 欢迎提交 issue 与 PR。请在 issue 中描述测试平台、Python 版本与模板图示例。

## 许可证

MIT License
