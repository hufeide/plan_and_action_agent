# 新旧架构对比

## 一、核心差异

### 旧架构问题
1. **职责混乱**：Team类500+行，做了7件不同的事
2. **循环依赖**：Team ↔ TeamWorkflow 相互依赖
3. **数据混乱**：任务数据存储在3个地方
4. **流程不清**：讨论→AI创建计划→提取任务→分配，逻辑混乱
5. **难以测试**：强依赖，无法mock

### 新架构优势
1. **职责清晰**：每个类只做一件事
2. **无循环依赖**：单向依赖，依赖注入
3. **统一数据管理**：StateStore统一管理
4. **流程清晰**：讨论→共识→计划→执行
5. **易于测试**：依赖注入，可mock

## 二、架构对比

### 旧架构
```
modules/
├── agent.py (150行)
├── team.py (500行) ← 太臃肿
├── team_state.py (100行)
├── team_workflow.py (350行)
├── role_based_action.py (80行)
├── task_board.py (120行)
└── visualization.py (400行)

问题：
- Team和TeamWorkflow循环依赖
- 数据分散在多个地方
- 职责不清晰
```

### 新架构
```
new/
├── domain/ (领域层)
│   ├── agent.py (60行) - Agent实体
│   ├── team.py (60行) - Team聚合根
│   ├── discussion.py (100行) - Discussion聚合根
│   ├── consensus.py (20行) - Consensus值对象
│   ├── task.py (60行) - Task实体
│   └── plan.py (70行) - Plan聚合根
├── application/ (应用层)
│   ├── workflow_engine.py (200行) - 工作流引擎
│   └── team_orchestrator.py (150行) - 团队编排器
├── infrastructure/ (基础设施层)
│   ├── ai_service.py (80行) - AI服务
│   └── state_store.py (100行) - 状态存储
└── presentation/ (展示层)
    └── api.py (100行) - Flask API

优势：
- 清晰的分层架构
- 单向依赖
- 统一的数据管理
- 职责明确
```

## 三、业务流程对比

### 旧架构流程（混乱）
```
用户输入需求
    ↓
Team.create_plan()
    ↓
Team.discuss() - 讨论
    ↓
AI创建计划（为什么不用讨论结果？）
    ↓
Team.discuss_and_vote_tasks() - 又讨论一次？
    ↓
Team.assign_tasks_from_plan() - 分配任务
    ↓
多处更新状态（容易遗漏）
```

问题：
- 讨论结果没被充分利用
- 多次AI调用效率低
- 流程不清晰

### 新架构流程（清晰）
```
用户输入需求
    ↓
TeamOrchestrator.handle_user_requirement()
    ↓
1. 推荐角色，创建团队
    ↓
2. WorkflowEngine.run_discussion()
   - 多轮讨论
   - 每轮收集意见
   - 检查共识
    ↓
3. 达成共识（Consensus）
    ↓
4. WorkflowEngine.create_plan_from_consensus()
   - 基于共识提取任务
   - 智能分配任务
    ↓
5. 返回完整结果
```

优势：
- 流程清晰，一目了然
- 讨论结果直接用于创建计划
- 单一入口，易于理解

## 四、代码质量对比

### 旧架构
```python
# Team类 - 职责混乱
class Team:
    def add_member()        # 成员管理
    def rent()              # 租用管理
    def assign_task()       # 任务管理
    def use_ai()            # AI管理
    def create_plan()       # 计划管理
    def evaluate()          # 评价管理
    # ... 500+行代码
```

### 新架构
```python
# 职责清晰，每个类只做一件事

# Team - 只管理成员
class Team:
    def add_agent()
    def get_agent()
    # 60行代码

# WorkflowEngine - 只管理流程
class WorkflowEngine:
    def run_discussion()
    def create_plan_from_consensus()
    # 200行代码

# TeamOrchestrator - 只协调流程
class TeamOrchestrator:
    def handle_user_requirement()
    # 150行代码
```

## 五、数据管理对比

### 旧架构（混乱）
```python
# 任务数据存储在3个地方
TeamState.current_plan['todo_list']  # 地方1
TaskBoard.tasks                       # 地方2
Agent.current_task                    # 地方3

# 同步困难，容易不一致
```

### 新架构（统一）
```python
# 统一的状态存储
class StateStore:
    _teams: Dict[str, Team]
    _discussions: Dict[str, Discussion]
    _plans: Dict[str, Plan]
    
# 单一数据源，易于管理
```

## 六、测试性对比

### 旧架构（难以测试）
```python
class Team:
    def __init__(self):
        self.workflow = TeamWorkflow(self)  # 强依赖
        self.role_action = RoleBasedAction()  # 强依赖
        # 无法mock，难以单元测试
```

### 新架构（易于测试）
```python
class TeamOrchestrator:
    def __init__(self, ai_config: AIConfig = None):
        self.ai_service = AIService(ai_config)  # 依赖注入
        self.workflow_engine = WorkflowEngine(self.ai_service)
        # 可以mock，易于测试

# 测试示例
def test_orchestrator():
    mock_ai_service = MockAIService()
    orchestrator = TeamOrchestrator(mock_ai_service)
    # 可以完全控制测试环境
```

## 七、扩展性对比

### 旧架构
- 添加新功能需要修改Team类（违反开闭原则）
- 模块之间紧耦合，牵一发动全身

### 新架构
- 添加新功能只需添加新的领域对象或应用服务
- 模块之间松耦合，易于扩展

## 八、使用示例对比

### 旧架构
```python
# 复杂，需要了解内部细节
team = Team("AI Team")
team.add_member(agent1)
team.add_member(agent2)
discussion = team.discuss(topic)
plan = team.create_plan(goal)
team.assign_tasks_from_plan()
# 需要手动协调多个步骤
```

### 新架构
```python
# 简单，一个方法搞定
orchestrator = TeamOrchestrator()
result = orchestrator.handle_user_requirement(
    requirement="开发一个电商网站",
    agent_count=3
)
# 自动完成：推荐角色→讨论→共识→计划
```

## 九、总结

| 维度 | 旧架构 | 新架构 |
|------|--------|--------|
| 职责分离 | ❌ 混乱 | ✅ 清晰 |
| 依赖关系 | ❌ 循环依赖 | ✅ 单向依赖 |
| 数据管理 | ❌ 分散 | ✅ 统一 |
| 业务流程 | ❌ 混乱 | ✅ 清晰 |
| 代码质量 | ❌ 臃肿 | ✅ 简洁 |
| 测试性 | ❌ 困难 | ✅ 容易 |
| 扩展性 | ❌ 困难 | ✅ 容易 |
| 易用性 | ❌ 复杂 | ✅ 简单 |

## 十、迁移建议

1. **逐步迁移**：先用新架构处理新需求，旧功能保持不变
2. **并行运行**：新旧架构可以同时运行（不同端口）
3. **数据迁移**：如需迁移数据，可以写转换脚本
4. **测试验证**：充分测试新架构的功能
5. **完全切换**：确认无误后，完全切换到新架构
