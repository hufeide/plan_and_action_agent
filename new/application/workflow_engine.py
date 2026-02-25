"""
工作流引擎 - 执行"讨论→共识→协作"的核心流程
"""
import uuid
from typing import List, Optional
from domain.agent import Agent
from domain.discussion import Discussion
from domain.consensus import Consensus
from domain.plan import Plan
from domain.task import Task
from infrastructure.ai_service import AIService


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def run_discussion(self, topic: str, agents: List[Agent], max_rounds: int = 3, save_callback=None) -> Discussion:
        """
        运行讨论流程
        
        流程：
        1. 初始化讨论
        2. 多轮讨论
        3. 尝试达成共识
        4. 返回讨论结果
        """
        discussion = Discussion(
            id=str(uuid.uuid4()),
            topic=topic,
            max_rounds=max_rounds
        )
        
        # 调用带回调的讨论方法
        self.run_discussion_with_callback(discussion, agents, save_callback)
        
        return discussion
    
    def run_discussion_with_callback(self, discussion: Discussion, agents: List[Agent], save_callback=None):
        """
        运行讨论流程（带回调）
        
        流程：
        1. 使用已有的discussion对象
        2. 多轮讨论
        3. 每轮讨论后保存结果
        4. 尝试达成共识
        """
        print(f"\n{'='*60}")
        print(f"开始讨论：{discussion.topic}")
        print(f"参与者：{', '.join([a.name for a in agents])}")
        print(f"{'='*60}\n")
        
        # 多轮讨论
        for round_num in range(1, discussion.max_rounds + 1):
            discussion.start_new_round()
            print(f"\n--- 第 {round_num} 轮讨论 ---")
            
            # 每个Agent发表意见
            for agent in agents:
                opinion = self._generate_opinion(agent, discussion)
                if opinion:
                    discussion.add_message(agent.id, agent.name, opinion)
                    print(f"{agent.name}（{agent.role}）：{opinion[:100]}...")
            
            # 每轮讨论后保存结果
            if save_callback:
                save_callback(discussion)
            
            # 检查是否达成共识
            if round_num >= 2:  # 至少2轮后才尝试达成共识
                consensus = self._check_consensus(discussion, agents)
                if consensus:
                    discussion.reach_consensus(consensus)
                    print(f"\n✓ 达成共识：{consensus[:100]}...")
                    # 达成共识后保存结果
                    if save_callback:
                        save_callback(discussion)
                    break
        
        # 如果未达成共识，强制生成共识
        if not discussion.is_finished():
            consensus = self._force_consensus(discussion, agents)
            if consensus:
                discussion.reach_consensus(consensus)
                print(f"\n✓ 强制达成共识：{consensus[:100]}...")
            else:
                discussion.fail()
                print("\n✗ 讨论失败，未能达成共识")
            # 强制达成共识后保存结果
            if save_callback:
                save_callback(discussion)
    
    def create_plan_from_consensus(self, goal: str, consensus: Consensus, agents: List[Agent]) -> Plan:
        """
        基于共识创建执行计划
        
        流程：
        1. 基于共识提取任务
        2. 为每个任务分配合适的Agent
        3. 创建计划
        """
        print(f"\n{'='*60}")
        print(f"基于共识创建执行计划")
        print(f"{'='*60}\n")
        
        # 提取任务
        tasks = self._extract_tasks(goal, consensus, agents)
        
        # 创建计划
        plan = Plan(
            id=str(uuid.uuid4()),
            goal=goal,
            consensus=consensus
        )
        
        for task_desc, agent in tasks:
            task = Task(
                id=str(uuid.uuid4()),
                description=task_desc
            )
            task.assign_to(agent.id, agent.name)
            plan.add_task(task)
            print(f"任务：{task_desc[:50]}... → {agent.name}（{agent.role}）")
        
        return plan
    
    def _generate_opinion(self, agent: Agent, discussion: Discussion) -> Optional[str]:
        """生成Agent的意见"""
        # 获取之前的讨论内容
        recent_messages = discussion.get_recent_messages(3)
        context = "\n".join([
            f"{msg.agent_name}：{msg.content[:100]}"
            for msg in recent_messages
        ]) if recent_messages else "这是第一轮讨论"
        
        prompt = f"""作为 {agent.name}（{agent.role}），直接发表你对以下主题的专业意见：

主题：{discussion.topic}
当前轮次：第 {discussion.current_round} 轮

之前的讨论：
{context}

重要要求：
1. 直接以第一人称发表你的观点，给出你的专业意见和建议
2. 不要解释你的思考过程，不要包含任何思考引导词
3. 不要重复之前的内容，只发表新的观点
4. 保持内容简洁明了，重点突出
5. 使用专业、正式的语言
6. 长度控制在300-500字之间

请直接开始你的观点，不要有任何引言或开场白。"""
        
        result = self.ai_service.generate(prompt)
        return result["text"] if result["success"] else None
    
    def _check_consensus(self, discussion: Discussion, agents: List[Agent]) -> Optional[str]:
        """检查是否达成共识"""
        # 获取最近一轮的所有意见
        recent_messages = [
            msg for msg in discussion.messages
            if msg.round == discussion.current_round
        ]
        
        if not recent_messages:
            return None
        
        # 让AI判断是否达成共识
        opinions = "\n".join([
            f"{msg.agent_name}：{msg.content}"
            for msg in recent_messages
        ])
        
        prompt = f"""分析以下团队讨论，判断是否达成共识：

主题：{discussion.topic}

本轮意见：
{opinions}

如果团队成员的意见基本一致，请总结共识内容。
如果意见分歧较大，请回复"未达成共识"。

只返回共识内容或"未达成共识"，不要添加其他解释。"""
        
        result = self.ai_service.generate(prompt)
        if result["success"]:
            consensus = result["text"]
            # 如果不是"未达成共识"，则认为达成了共识
            if "未达成共识" not in consensus:
                return consensus
        
        return None
    
    def _force_consensus(self, discussion: Discussion, agents: List[Agent]) -> Optional[str]:
        """强制生成共识"""
        all_opinions = "\n".join([
            f"{msg.agent_name}：{msg.content[:150]}"
            for msg in discussion.messages
        ])
        
        prompt = f"""团队已经讨论了 {discussion.current_round} 轮关于"{discussion.topic}"的话题。

所有讨论内容：
{all_opinions}

请基于以上讨论，总结一个平衡的共识方案。直接给出共识内容，不要解释。"""
        
        result = self.ai_service.generate(prompt)
        return result["text"] if result["success"] else None
    
    def _extract_tasks(self, goal: str, consensus: Consensus, agents: List[Agent]) -> List[tuple]:
        """
        从共识中提取任务并分配
        
        Returns:
            List[(task_description, assigned_agent)]
        """
        agent_info = "\n".join([
            f"- {agent.name}（{agent.role}）：{', '.join(agent.skills)}"
            for agent in agents
        ])
        
        prompt = f"""基于以下共识，提取具体的执行任务：

目标：{goal}
共识：{consensus.content}

团队成员：
{agent_info}

请提取3-6个具体任务，每个任务一行，格式：
任务描述 | 负责人姓名

只返回任务列表，不要添加其他内容。"""
        
        result = self.ai_service.generate(prompt)
        if not result["success"]:
            # 如果AI调用失败，返回默认任务
            return [(f"执行任务{i+1}", agents[i % len(agents)]) for i in range(3)]
        
        # 解析任务
        tasks = []
        lines = result["text"].strip().split('\n')
        
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 2:
                    task_desc = parts[0].strip()
                    assignee_name = parts[1].strip()
                    
                    # 查找对应的Agent
                    agent = next((a for a in agents if a.name == assignee_name), None)
                    if agent:
                        tasks.append((task_desc, agent))
                    else:
                        # 如果找不到，分配给第一个Agent
                        tasks.append((task_desc, agents[0]))
        
        # 限制任务数量最多6个
        tasks = tasks[:6]
        
        # 如果没有提取到任务，返回默认任务
        if not tasks:
            tasks = [(f"执行任务{i+1}", agents[i % len(agents)]) for i in range(3)]
        
        return tasks
