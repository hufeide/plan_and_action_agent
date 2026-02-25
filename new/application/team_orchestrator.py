"""
团队编排器 - 协调整个流程的入口
"""
import uuid
from typing import Dict, List
from domain.team import Team
from domain.agent import Agent
from domain.consensus import Consensus
from infrastructure.ai_service import AIService, AIConfig
from infrastructure.state_store import StateStore
from application.workflow_engine import WorkflowEngine


class TeamOrchestrator:
    """团队编排器 - 应用层的门面"""
    
    def __init__(self, ai_config: AIConfig = None):
        # 使用默认配置或传入的配置
        self.ai_config = ai_config or AIConfig(
            base_url="http://192.168.1.159:19000/v1",
            model="Qwen3Coder",
            api_key="empty"
        )
        
        self.ai_service = AIService(self.ai_config)
        self.workflow_engine = WorkflowEngine(self.ai_service)
        self.state_store = StateStore()
        self.current_stage = "idle"
        self.current_message = "就绪：等待处理需求"
    
    def handle_user_requirement(self, requirement: str, agent_count: int = 3) -> Dict:
        """
        处理用户需求 - 主流程入口
        
        流程：
        1. 分析需求，推荐角色
        2. 创建团队
        3. 团队讨论
        4. 达成共识
        5. 制定计划
        6. 返回结果
        
        Args:
            requirement: 用户需求描述
            agent_count: Agent数量
            
        Returns:
            {
                "team": Team,
                "discussion": Discussion,
                "consensus": Consensus,
                "plan": Plan,
                "success": bool
            }
        """
        print(f"\n{'#'*60}")
        print(f"处理用户需求：{requirement}")
        print(f"{'#'*60}\n")
        
        # 1. 推荐角色并创建团队
        self.current_stage = "analyzing"
        self.current_message = "分析需求，创建团队..."
        team = self._create_team_with_recommended_roles(requirement, agent_count)
        self.state_store.save_team(team)
        
        # 2. 团队讨论
        self.current_stage = "discussing"
        self.current_message = "团队讨论中..."
        # 立即保存阶段信息，以便前端能够获取到
        
        # 创建讨论对象并保存到state_store中
        from domain.discussion import Discussion
        import uuid
        discussion = Discussion(
            id=str(uuid.uuid4()),
            topic=f"如何实现：{requirement}",
            max_rounds=3
        )
        self.state_store.save_discussion(discussion)
        
        # 运行讨论并每轮保存结果
        # 注意：我们需要使用同一个discussion对象，以便前端能够获取到一致的ID
        self.workflow_engine.run_discussion_with_callback(
            discussion=discussion,
            agents=team.get_all_agents(),
            save_callback=lambda d: self.state_store.save_discussion(d)
        )
        # 保存最终结果
        self.state_store.save_discussion(discussion)
        
        # 3. 检查是否达成共识
        if not discussion.consensus:
            self.current_stage = "error"
            self.current_message = "讨论未能达成共识"
            return {
                "team": team,
                "discussion": discussion,
                "consensus": None,
                "plan": None,
                "success": False,
                "message": "讨论未能达成共识"
            }
        
        # 4. 基于共识创建计划
        self.current_stage = "consensus"
        self.current_message = "达成共识中..."
        consensus = Consensus(
            content=discussion.consensus,
            discussion_id=discussion.id
        )
        
        self.current_stage = "planning"
        self.current_message = "制定执行计划..."
        plan = self.workflow_engine.create_plan_from_consensus(
            goal=requirement,
            consensus=consensus,
            agents=team.get_all_agents()
        )
        self.state_store.save_plan(plan)
        
        self.current_stage = "completed"
        self.current_message = "任务处理完成"
        print(f"\n{'#'*60}")
        print(f"✓ 需求处理完成")
        print(f"{'#'*60}\n")
        
        return {
            "team": team,
            "discussion": discussion,
            "consensus": consensus,
            "plan": plan,
            "success": True,
            "message": "需求处理成功"
        }
    
    def update_task_progress(self, task_id: str, progress: int) -> Dict:
        """更新任务进度"""
        plan = self.state_store.get_current_plan()
        if not plan:
            return {"success": False, "message": "没有当前计划"}
        
        task = plan.get_task(task_id)
        if not task:
            return {"success": False, "message": "任务不存在"}
        
        task.update_progress(progress)
        
        # 检查计划是否完成
        if plan.is_completed():
            plan.complete()
            print(f"\n✓ 计划已完成：{plan.goal}")
        
        return {
            "success": True,
            "task": task.to_dict(),
            "plan_progress": plan.get_progress()
        }
    
    def get_current_status(self) -> Dict:
        """获取当前状态"""
        team = self.state_store.get_current_team()
        discussion = self.state_store.get_current_discussion()
        plan = self.state_store.get_current_plan()
        
        # 确定状态
        if self.current_stage == "idle":
            status = "idle"
        elif self.current_stage == "completed":
            status = "completed"
        elif self.current_stage == "error":
            status = "error"
        else:
            status = "processing"
        
        return {
            "status": status,
            "stage": self.current_stage,
            "message": self.current_message,
            "team": team.to_dict() if team else None,
            "discussion": discussion.to_dict() if discussion else None,
            "plan": plan.to_dict() if plan else None,
            "total_tokens": self.ai_service.get_total_tokens()
        }
    
    def update_goal(self, goal: str) -> Dict:
        """更新需求"""
        plan = self.state_store.get_current_plan()
        if not plan:
            return {"success": False, "message": "没有当前计划"}
        
        plan.goal = goal
        self.state_store.save_plan(plan)
        
        return {"success": True, "message": "需求修改成功"}
    
    def update_task(self, task_id: str, description: str, assignee_name: str) -> Dict:
        """更新任务"""
        plan = self.state_store.get_current_plan()
        if not plan:
            return {"success": False, "message": "没有当前计划"}
        
        task = plan.get_task(task_id)
        if not task:
            return {"success": False, "message": "任务不存在"}
        
        task.description = description
        task.assignee_name = assignee_name
        self.state_store.save_plan(plan)
        
        return {"success": True, "message": "任务修改成功"}
    
    def execute_tasks(self, task_ids: List[str]) -> Dict:
        """并行执行选中的任务"""
        import threading
        import time
        
        plan = self.state_store.get_current_plan()
        if not plan:
            return {"success": False, "message": "没有当前计划"}
        
        # 验证所有任务是否存在
        tasks = []
        for task_id in task_ids:
            task = plan.get_task(task_id)
            if not task:
                return {"success": False, "message": f"任务 {task_id} 不存在"}
            tasks.append(task)
        
        # 执行状态
        self.execution_status = {
            "status": "processing",
            "message": "任务执行中...",
            "completed_tasks": 0,
            "total_tasks": len(tasks)
        }
        
        # 并行执行任务
        def execute_task(task):
            print(f"开始执行任务：{task.description}")
            # 调用大模型执行任务
            prompt = f"你是{task.assignee_name}，请完成以下任务：{task.description}。\n\n请直接给出任务的执行结果，不要包含任何思考过程。"
            result = self.ai_service.generate(prompt)
            if result["success"]:
                task_result = result["text"]
                # 保存任务结果
                task.result = task_result
                print(f"任务执行结果：{task_result[:100]}...")
            else:
                task_result = "任务执行失败"
                task.result = task_result
                print(f"任务执行失败：{result.get('error', '未知错误')}")
            # 标记任务完成
            task.update_progress(100)
            self.execution_status["completed_tasks"] += 1
            print(f"任务完成：{task.description}")
        
        # 创建线程
        threads = []
        for task in tasks:
            thread = threading.Thread(target=execute_task, args=(task,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 由总agent调用大模型，结合子agent的结果和任务，以及需求目标，最终给出反馈
        print("\n总agent正在汇总子任务执行结果...")
        
        # 收集子任务执行结果
        task_results = []
        for task in tasks:
            task_results.append({
                "description": task.description,
                "assignee": task.assignee_name,
                "result": task.result
            })
        
        # 构建总agent的prompt
        task_results_str = "\n".join([
            f"- 任务：{result['description']}\n  负责人：{result['assignee']}\n  结果：{result['result']}"
            for result in task_results
        ])
        
        prompt = f"你是总agent，负责汇总和分析子任务的执行结果，结合需求目标，给出最终的反馈。\n\n需求目标：{plan.goal}\n\n子任务执行结果：\n{task_results_str}\n\n请根据以上信息，给出最终的反馈，包括：\n1. 子任务执行情况的总结\n2. 需求目标的达成情况\n3. 最终的结论和建议\n\n请直接给出最终反馈，不要包含任何思考过程。"
        
        # 调用大模型获取最终反馈
        final_result = self.ai_service.generate(prompt)
        if final_result["success"]:
            final_feedback = final_result["text"]
            print(f"总agent反馈：{final_feedback[:100]}...")
        else:
            final_feedback = "总agent汇总失败"
            print(f"总agent汇总失败：{final_result.get('error', '未知错误')}")
        
        # 更新执行状态
        self.execution_status["status"] = "completed"
        self.execution_status["message"] = final_feedback
        self.execution_status["final_feedback"] = final_feedback
        self.execution_status["task_results"] = task_results
        
        # 保存计划
        self.state_store.save_plan(plan)
        
        return {"success": True, "message": "任务执行完成", "final_feedback": final_feedback}
    
    def reexecute_plan(self) -> Dict:
        """重新执行计划"""
        plan = self.state_store.get_current_plan()
        if not plan:
            return {"success": False, "message": "没有当前计划"}
        
        # 重置所有任务进度
        for task in plan.tasks:
            task.update_progress(0)
        
        # 重新执行所有任务
        task_ids = [task.id for task in plan.tasks]
        return self.execute_tasks(task_ids)
    
    def get_execution_status(self) -> Dict:
        """获取执行状态"""
        if hasattr(self, 'execution_status'):
            return self.execution_status
        else:
            return {"status": "idle", "message": "未执行任务"}
    
    def _create_team_with_recommended_roles(self, requirement: str, agent_count: int) -> Team:
        """根据需求推荐角色并创建团队"""
        print(f"分析需求，推荐 {agent_count} 个合适的角色...")
        
        # 使用AI推荐角色
        roles = self._recommend_roles(requirement, agent_count)
        
        # 创建团队
        team = Team(
            id=str(uuid.uuid4()),
            name="AI协作团队"
        )
        
        # 创建Agent
        agent_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"]
        for i, role_info in enumerate(roles[:agent_count]):
            agent = Agent(
                id=str(uuid.uuid4()),
                name=agent_names[i] if i < len(agent_names) else f"Agent{i+1}",
                role=role_info["role"],
                skills=role_info["skills"]
            )
            team.add_agent(agent)
            print(f"  - {agent.name}：{agent.role}（{', '.join(agent.skills)}）")
        
        return team
    
    def _recommend_roles(self, requirement: str, count: int) -> List[Dict]:
        """推荐角色"""
        prompt = f"""基于需求"{requirement}"，推荐 {count} 个最适合的团队角色。

每个角色一行，格式：
角色名称 | 技能1,技能2,技能3

例如：
前端开发工程师 | React,TypeScript,CSS
后端架构师 | Python,数据库,API设计

只返回角色列表，不要添加其他内容。"""
        
        result = self.ai_service.generate(prompt)
        
        if not result["success"]:
            # 返回默认角色
            return [
                {"role": "开发工程师", "skills": ["编程", "设计", "测试"]},
                {"role": "产品经理", "skills": ["需求分析", "规划", "沟通"]},
                {"role": "设计师", "skills": ["UI设计", "UX设计", "原型"]}
            ]
        
        # 解析角色
        roles = []
        lines = result["text"].strip().split('\n')
        
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 2:
                    role_name = parts[0].strip()
                    skills = [s.strip() for s in parts[1].split(',')]
                    roles.append({"role": role_name, "skills": skills})
        
        # 如果解析失败，返回默认角色
        if not roles:
            roles = [
                {"role": "开发工程师", "skills": ["编程", "设计", "测试"]},
                {"role": "产品经理", "skills": ["需求分析", "规划", "沟通"]},
                {"role": "设计师", "skills": ["UI设计", "UX设计", "原型"]}
            ]
        
        return roles
