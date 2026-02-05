"""
Prefect 3.x 调度示例

使用方法：
1. 直接运行 - 本地测试
2. 部署调度 - 使用 prefect deploy 命令
"""

from datetime import datetime
from prefect import flow, task


@task
def print_hello():
    """打印任务"""
    print(f"Hello Prefect! 当前时间: {datetime.now()}")


@flow(name="hello-schedule-1", cron="0 0 * * *")
def hello_flow():
    """工作流"""
    print_hello()


if __name__ == "__main__":
    print("=" * 60)
    print("Prefect 3.x 调度示例")
    print("=" * 60)
    print("\n选择运行方式:")
    print("  1. 本地测试 (直接运行)")
    print("  2. 部署调度 (需要 Prefect)")
    print("  q. 退出")
    print("=" * 60)
    
    choice = input("\n请输入选项: ").strip()
    
    if choice == "1":
        print("\2n本地测试...")
        hello_flow()
        print("完成!")
        
    elif choice == "2":
        print("\n部署调度...")
        print("请使用命令:")
        print("  1. prefect deploy test_prefect.py:hello_flow --name hello-schedule")
        print("  2. 或启动本地 Server: prefect server start")
        
    elif choice.lower() == "q":
        print("退出")
    else:
        print("无效选项")
