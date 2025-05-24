import os
import sys
import subprocess
import platform

def build_app():
    # 确定操作系统
    os_type = platform.system()
    
    # 基础命令
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",                     # 独立可执行文件
        "--follow-imports",                 # 跟踪并打包所有导入
        "--onefile",                        # 生成单个可执行文件
        "--show-progress",                  # 显示打包进度
        "--show-memory",                    # 显示内存使用情况
        "--plugin-enable=numpy",            # 启用numpy插件 (这是Nuitka官方支持的插件)
        "--include-package=streamlit",      # 包含streamlit包
        "--include-package=pandas",         # 包含pandas包
        "--include-package=plotly",         # 包含plotly包
        "--include-package=numpy",          # 包含numpy包
        "--include-package=openpyxl",       # 包含openpyxl包
        "--include-module=pandas._libs",    # 确保包含pandas的C扩展部分
        "--include-module=plotly.graph_objects",  # 确保包含plotly的关键模块
        "--include-data-dir=.=.",           # 包含当前目录下所有文件
    ]
    
    # 如果是Windows系统且存在图标文件，添加图标
    if os_type == "Windows":
        if os.path.exists("favicon.ico"):
            cmd.append("--windows-icon-from-ico=favicon.ico")
    
    # 添加目标文件
    cmd.append("run_app.py")
    
    # 输出打包命令
    print("执行打包命令:", " ".join(cmd))
    
    # 执行打包命令
    subprocess.run(cmd)
    
    print("\n打包完成！")
    if os_type == "Windows":
        print("可执行文件位于:", os.path.join(os.getcwd(), "run_app.exe"))
    else:
        print("可执行文件位于:", os.path.join(os.getcwd(), "run_app.bin"))

if __name__ == "__main__":
    # 安装依赖
    print("正在安装依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 安装Nuitka相关依赖
    print("正在安装Nuitka相关依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "nuitka", "ordered-set", "zstandard"])
    
    # 开始打包
    print("\n开始打包应用...")
    build_app() 