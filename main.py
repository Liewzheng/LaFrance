#!/usr/bin/env python3
"""
LaFrance - 法语语音生成器
French Text-to-Speech Generator

支持多种法语声音，可调节语速和音调
"""

import asyncio
import edge_tts
import os
import re
import json
import hashlib
from datetime import datetime

# 启用 readline 支持（光标移动、历史记录）
try:
    import readline
    # 设置历史记录文件
    histfile = os.path.expanduser("~/.lafrance_history")
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass
except ImportError:
    readline = None
    print("⚠️  readline 未安装，光标移动和历史记录功能不可用")

# 尝试读取配置文件
try:
    from config import DEFAULT_VOICE, DEFAULT_RATE, DEFAULT_VOLUME, OUTPUT_DIR, AUTO_PLAY
except ImportError:
    # 默认配置
    DEFAULT_VOICE = "denise"
    DEFAULT_RATE = "+0%"
    DEFAULT_VOLUME = "+0%"
    OUTPUT_DIR = "samples"
    AUTO_PLAY = True

# 法语声音选项
FRENCH_VOICES = {
    "henri": "fr-FR-HenriNeural",      # 男声 - 标准
    "denise": "fr-FR-DeniseNeural",    # 女声 - 温柔
    "eloise": "fr-FR-EloiseNeural",    # 女声 - 年轻
    "remy": "fr-FR-RemyMultilingualNeural",    # 男声 - 多语言
    "vivienne": "fr-FR-VivienneMultilingualNeural",  # 女声 - 多语言
}

class FrenchTTS:
    """法语语音生成器类"""
    
    def __init__(self, voice=None, rate=None, volume=None, use_cache=True):
        """
        初始化 TTS 引擎
        
        Args:
            voice: 声音名称 (henri/denise/eloise/remy/vivienne)
            rate: 语速 (+50% 加快, -50% 减慢)
            volume: 音量 (+0% 默认)
            use_cache: 是否使用缓存（默认开启）
        """
        voice = voice or DEFAULT_VOICE
        rate = rate or DEFAULT_RATE
        volume = volume or DEFAULT_VOLUME
        
        self.voice = FRENCH_VOICES.get(voice, FRENCH_VOICES["denise"])
        self.rate = rate
        self.volume = volume
        self.output_dir = OUTPUT_DIR
        self.auto_play = AUTO_PLAY
        self.use_cache = use_cache
        
        # 缓存文件路径
        self.cache_file = os.path.join(self.output_dir, ".cache.json")
        self.cache = self._load_cache()
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _load_cache(self):
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  缓存保存失败: {e}")
    
    def _get_cache_key(self, text):
        """生成缓存键（基于文本内容+声音+语速）"""
        content = f"{text}|{self.voice}|{self.rate}|{self.volume}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def clear_cache(self):
        """清除缓存"""
        count = len(self.cache)
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print(f"🗑️  已清除 {count} 条缓存")
    
    def show_cache_info(self):
        """显示缓存信息"""
        print(f"\n📦 缓存信息:")
        print(f"   缓存文件: {self.cache_file}")
        print(f"   缓存条目: {len(self.cache)}")
        if self.cache:
            print("   最近的条目:")
            for i, (key, path) in enumerate(list(self.cache.items())[-5:], 1):
                filename = os.path.basename(path)
                print(f"     {i}. {filename}")
        print()
    
    def _sanitize_filename(self, text, max_length=30):
        """清理文本，生成安全的文件名"""
        # 移除或替换非法字符
        import re
        # 只保留字母、数字、空格和常见标点
        cleaned = re.sub(r'[^\w\s\-\']', '', text)
        # 替换多个空格为单个空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # 限制长度，取前几个单词
        words = cleaned.split()[:4]  # 最多取4个单词
        result = '_'.join(words)
        # 限制总长度
        if len(result) > max_length:
            result = result[:max_length].rstrip('_')
        return result if result else "audio"
    
    async def speak(self, text, filename=None, play=None, force_regenerate=False, verbose=True):
        """
        将文本转为语音
        
        Args:
            text: 要朗读的法语文本
            filename: 输出文件名 (默认自动生成)
            play: 是否自动播放 (默认读取配置)
            force_regenerate: 强制重新生成（忽略缓存）
            verbose: 是否显示提示信息
            
        Returns:
            生成的音频文件路径
        """
        if play is None:
            play = self.auto_play
        
        # 检查缓存
        cache_key = self._get_cache_key(text)
        cached_path = None
        
        if self.use_cache and not force_regenerate and cache_key in self.cache:
            cached_path = self.cache[cache_key]
            # 检查文件是否还存在
            if os.path.exists(cached_path):
                if verbose:
                    print(f"♻️  使用缓存: {os.path.basename(cached_path)}")
                if play:
                    self._play_audio(cached_path)
                return cached_path
            else:
                # 文件被删了，从缓存移除
                del self.cache[cache_key]
        
        # 生成新文件名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            content = self._sanitize_filename(text)
            filename = f"{timestamp}_{content}.mp3"
        
        if not filename.endswith('.mp3'):
            filename += '.mp3'
            
        output_path = os.path.join(self.output_dir, filename)
        
        if verbose:
            print("🔊 ", end="", flush=True)
        
        # 创建 TTS 通信对象
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume
        )
        
        # 保存音频文件（带简单进度指示）
        if verbose:
            import sys
            print("█", end="", flush=True)
        
        await communicate.save(output_path)
        
        if verbose:
            print("█ 100%")
            print(f"✅ 已生成: {output_path}")
        
        # 保存到缓存
        if self.use_cache:
            self.cache[cache_key] = output_path
            self._save_cache()
        
        # 自动播放
        if play:
            self._play_audio(output_path)
            
        return output_path
    
    def _play_audio(self, file_path):
        """播放音频文件"""
        try:
            # 尝试使用 pygame 播放（跨平台）
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"⚠️ 自动播放失败: {e}")
            print(f"   请手动播放: {file_path}")
    
    def list_voices(self):
        """列出所有可用的法语声音"""
        print("\n🎙️  可用的法语声音:")
        print("-" * 40)
        for name, voice_id in FRENCH_VOICES.items():
            gender = "男声" if "Henri" in voice_id or "Remy" in voice_id else "女声"
            print(f"  • {name:12} - {gender:6} ({voice_id})")
        print()


def quick_speak(text, voice="denise"):
    """快速朗读法语文本（同步接口）"""
    tts = FrenchTTS(voice=voice)
    asyncio.run(tts.speak(text))


async def interactive_mode():
    """交互式模式"""
    print("\n" + "="*50)
    print("🥐  LaFrance - 法语语音生成器")
    print("="*50)
    
    tts = FrenchTTS()
    tts.list_voices()
    
    print("输入你要朗读的法语句子 (输入 'quit' 退出):")
    print("-"*50)
    
    while True:
        try:
            text = input("\n🇫🇷 > ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("Au revoir! 👋")
                break
            
            if not text:
                continue
                
            # 特殊命令
            if text.startswith("/voice "):
                voice = text.split()[1]
                if voice in FRENCH_VOICES:
                    tts.voice = FRENCH_VOICES[voice]
                    print(f"✓ 已切换到: {voice}")
                else:
                    print(f"✗ 未知声音: {voice}")
                    tts.list_voices()
                continue
            
            if text.startswith("/rate "):
                rate = text.split()[1]
                tts.rate = rate
                print(f"✓ 语速已设为: {rate}")
                continue
            
            if text == "/help":
                print("""
📖 命令列表:
  /voice <name>  - 切换声音 (henri/denise/eloise/remy/vivienne)
  /rate <+/-n%>  - 调整语速 (/rate +20% 或 /rate -30%)
  /list          - 列出所有声音
  /cache         - 查看缓存信息
  /clear         - 清除缓存
  !<text>        - 强制重新生成（如：!Bonjour）
  /help          - 显示帮助
  quit           - 退出
                """)
                continue
            
            if text == "/list":
                tts.list_voices()
                continue
            
            if text == "/cache":
                tts.show_cache_info()
                continue
            
            if text == "/clear":
                tts.clear_cache()
                continue
            
            # 检查是否强制重新生成
            force_regenerate = False
            if text.startswith("!"):
                force_regenerate = True
                text = text[1:].strip()
            
            # 生成语音（缓存命中时会自动播放，无提示）
            await tts.speak(text, force_regenerate=force_regenerate, verbose=False)
            
        except KeyboardInterrupt:
            print("\nAu revoir! 👋")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    # 退出时保存历史记录
    if readline:
        try:
            readline.write_history_file(histfile)
        except:
            pass


# 预设的法语学习例句
SAMPLE_SENTENCES = [
    "Bonjour Madame, je voudrais un café.",
    "Je m'appelle Paul, et toi?",
    "Je parle arabe avec ma voisine marocaine.",
    "Est-ce que Paris est propre?",
    "Au revoir!",
    "S'il vous plaît.",
    "Embrasse-moi, s'il te plaît.",
    "Leo mange souvent ici.",
    "Tu connais Lisa? Elle travaille ici.",
    "Je travaille aussi ici.",
]


async def demo_mode():
    """演示模式 - 朗读所有学习例句"""
    print("\n🎬 演示模式 - 朗读法语学习例句\n")
    
    # 不同声音朗读不同句子
    voices = ["denise", "henri", "eloise"]
    
    for i, sentence in enumerate(SAMPLE_SENTENCES[:6], 1):
        voice = voices[i % len(voices)]
        tts = FrenchTTS(voice=voice)
        
        print(f"\n{i}. [{voice}] {sentence}")
        await tts.speak(sentence, filename=f"demo_{i:02d}_{voice}.mp3", play=True)
        await asyncio.sleep(0.5)  # 停顿一下
    
    print("\n✅ 演示完成！所有音频保存在 samples/ 目录")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            # 演示模式
            asyncio.run(demo_mode())
            
        elif command == "quick":
            # 快速朗读: python main.py quick "Bonjour"
            text = sys.argv[2] if len(sys.argv) > 2 else "Bonjour"
            voice = sys.argv[3] if len(sys.argv) > 3 else "denise"
            quick_speak(text, voice)
            
        elif command == "list":
            # 列出声音
            tts = FrenchTTS()
            tts.list_voices()
            
        else:
            # 直接朗读参数文本
            text = " ".join(sys.argv[1:])
            quick_speak(text)
    else:
        # 交互模式
        asyncio.run(interactive_mode())
