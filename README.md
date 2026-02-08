# 🥐 LaFrance - 法语语音生成器

一个简单易用的法语文字转语音工具，基于微软 Edge TTS，支持多种法语声音。

## ✨ 功能特点

- 🎙️ **5种法语声音** - 男声/女声可选
- ⚡ **免费使用** - 基于 Edge TTS，无需 API Key
- 🐢 **语速可调** - 支持加快/减慢朗读速度
- 💾 **自动保存** - 生成 MP3 文件到 samples/ 目录
- 🔊 **自动播放** - 生成后自动播放（可关闭）
- 📚 **学习例句** - 内置多邻国法语课程例句

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ~/Workspace/python/LaFrance
pip install -r requirements.txt
```

### 2. 运行

```bash
# 交互模式（推荐）
python main.py

# 快速朗读一句话
python main.py "Bonjour Madame, je voudrais un café."

# 演示模式（朗读所有例句）
python main.py demo

# 指定声音朗读
python main.py quick "Je t'aime" denise
```

## 🎙️ 可用的声音

| 名字 | 性别 | 特点 |
|------|------|------|
| `henri` | 男声 | 标准法国男声 |
| `denise` | 女声 | 温柔女声（默认）|
| `eloise` | 女声 | 年轻女声 |
| `remy` | 男声 | 多语言男声 |
| `vivienne` | 女声 | 多语言女声 |

## 💬 交互模式命令

进入交互模式后，可以使用以下命令：

```
🇫🇷 > Bonjour!                    # 直接输入法语句子朗读
🇫🇷 > /voice henri                # 切换声音
🇫🇷 > /rate +20%                 # 加快语速
🇫🇷 > /rate -30%                 # 减慢语速
🇫🇷 > /list                      # 列出所有声音
🇫🇷 > /help                      # 显示帮助
🇫🇷 > quit                       # 退出
```

## 📝 代码示例

```python
from main import FrenchTTS, quick_speak
import asyncio

# 方式1: 快速朗读
quick_speak("Bonjour tout le monde!", voice="denise")

# 方式2: 自定义生成
async def main():
    tts = FrenchTTS(voice="henri", rate="+10%")
    
    # 生成并播放
    await tts.speak("Je parle français.")
    
    # 生成不播放，保存文件
    path = await tts.speak("Au revoir!", play=False)
    print(f"已保存到: {path}")

asyncio.run(main())
```

## 📁 文件结构

```
LaFrance/
├── main.py           # 主程序
├── config.py         # 配置文件
├── requirements.txt  # 依赖列表
├── samples/          # 生成的音频文件
└── README.md         # 本文件
```

## 🔧 依赖说明

- **edge-tts**: 微软 Edge TTS 接口
- **pygame**: 音频播放（跨平台）
- **playsound3**: 备选播放方案

## 💡 提示

1. 第一次使用需要联网下载声音模型
2. 生成的音频保存在 `samples/` 目录，按时间命名
3. 如果自动播放失败，请手动播放生成的 MP3 文件
4. 支持所有 Unicode 字符，可以朗读带音符的法语字母

## 🐛 常见问题

**Q: 播放没有声音？**
A: 可能是系统音量问题，或者 pygame 初始化失败。检查生成的 MP3 文件是否正常。

**Q: 如何改变默认声音？**
A: 修改 `config.py` 中的 `DEFAULT_VOICE` 变量。

**Q: 支持其他语言吗？**
A: 本工具专为法语优化，但 edge-tts 支持多种语言，可以在代码中修改 `voice` 参数。

---

🌙 Created for LaFrance 法语学习
