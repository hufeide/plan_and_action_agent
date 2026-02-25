"""
启动脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from new.presentation.api import run_server

if __name__ == '__main__':
    print("\n" + "="*60)
    print("启动新架构API服务器")
    print("="*60)
    print("地址：http://0.0.0.0:5003")
    print("="*60 + "\n")
    
    run_server(host='0.0.0.0', port=5003, debug=False)
