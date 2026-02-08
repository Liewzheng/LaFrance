#!/bin/bash
# LaFrance 启动脚本

cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "🔄 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
if ! python -c "import edge_tts" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 运行
echo "🥐 启动 LaFrance 法语语音生成器..."
echo ""
python main.py "$@"
