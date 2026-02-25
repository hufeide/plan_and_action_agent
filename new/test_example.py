"""
测试示例 - 演示如何使用新架构
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application.team_orchestrator import TeamOrchestrator
from infrastructure.ai_service import AIConfig


def test_basic_workflow():
    """测试基本工作流"""
    print("\n" + "="*80)
    print("测试：基本工作流（讨论→共识→协作）")
    print("="*80)
    
    # 创建编排器
    ai_config = AIConfig(
        base_url="http://192.168.1.159:19000/v1",
        model="Qwen3Coder",
        api_key="empty"
    )
    orchestrator = TeamOrchestrator(ai_config)
    
    # 处理用户需求
    result = orchestrator.handle_user_requirement(
        requirement="开发一个在线图书管理系统",
        agent_count=3
    )
    
    # 打印结果
    print("\n" + "-"*80)
    print("处理结果：")
    print("-"*80)
    print(f"成功：{result['success']}")
    print(f"消息：{result['message']}")
    
    if result['success']:
        print(f"\n团队信息：")
        print(f"  - 团队名称：{result['team'].name}")
        print(f"  - 成员数量：{result['team'].get_agent_count()}")
        
        print(f"\n讨论信息：")
        print(f"  - 讨论主题：{result['discussion'].topic}")
        print(f"  - 讨论轮数：{result['discussion'].current_round}")
        print(f"  - 消息数量：{len(result['discussion'].messages)}")
        print(f"  - 共识：{result['consensus'].content[:100]}...")
        
        print(f"\n计划信息：")
        print(f"  - 目标：{result['plan'].goal}")
        print(f"  - 任务数量：{len(result['plan'].tasks)}")
        print(f"  - 任务列表：")
        for task in result['plan'].tasks:
            print(f"    * {task.description[:50]}... → {task.assignee_name}")
    
    print("\n" + "="*80)
    print(f"总Token消耗：{orchestrator.ai_service.get_total_tokens()}")
    print("="*80 + "\n")


def test_task_progress():
    """测试任务进度更新"""
    print("\n" + "="*80)
    print("测试：任务进度更新")
    print("="*80)
    
    orchestrator = TeamOrchestrator()
    
    # 先创建一个计划
    result = orchestrator.handle_user_requirement(
        requirement="开发一个简单的博客系统",
        agent_count=2
    )
    
    if result['success'] and result['plan']:
        plan = result['plan']
        
        # 更新第一个任务的进度
        if plan.tasks:
            task = plan.tasks[0]
            print(f"\n更新任务进度：{task.description[:50]}...")
            
            for progress in [25, 50, 75, 100]:
                update_result = orchestrator.update_task_progress(task.id, progress)
                print(f"  进度：{progress}% - 状态：{update_result['task']['status']}")
            
            print(f"\n计划整体进度：{plan.get_progress():.1f}%")
    
    print("="*80 + "\n")


def test_get_status():
    """测试获取状态"""
    print("\n" + "="*80)
    print("测试：获取当前状态")
    print("="*80)
    
    orchestrator = TeamOrchestrator()
    
    # 创建一个计划
    orchestrator.handle_user_requirement(
        requirement="开发一个待办事项应用",
        agent_count=2
    )
    
    # 获取状态
    status = orchestrator.get_current_status()
    
    print(f"\n当前状态：")
    print(f"  - 团队：{status['team']['name'] if status['team'] else '无'}")
    print(f"  - 讨论：{status['discussion']['topic'] if status['discussion'] else '无'}")
    print(f"  - 计划：{status['plan']['goal'] if status['plan'] else '无'}")
    print(f"  - Token消耗：{status['total_tokens']}")
    
    print("="*80 + "\n")


if __name__ == '__main__':
    # 运行测试
    test_basic_workflow()
    test_task_progress()
    test_get_status()
