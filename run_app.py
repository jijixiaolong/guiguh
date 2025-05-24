import os
import sys
import subprocess

def run_streamlit_app():
    # 获取应用所在目录
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置工作目录
    os.chdir(app_dir)
    
    # 启动Streamlit应用
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"]
    subprocess.run(streamlit_cmd)

if __name__ == "__main__":
    run_streamlit_app() 