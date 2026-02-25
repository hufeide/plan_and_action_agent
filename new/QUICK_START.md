# 快速开始指南

## 一、安装依赖

```bash
pip install flask flask-cors requests
```

## 二、配置AI服务

编辑 `infrastructure/ai_service.py` 中的默认配置，或在创建时传入配置：

```python
from new.infrastructure.ai_service import AIConfig

ai_config = AIConfig(
    base_url="http://your-ai-server:port/v1",
    model="your-model-name",
    api_key="your-api-key"
)
```

## 三、使用方式

### 方式1：直接使用Python API

```python
from new.application.team_orchestrator import TeamOrchestrator

# 创建编排器
orchestrator = TeamOrchestrator()

# 处理用户需求
result = orchestrator.handle_user_requirement(
    requirement="开发一个在线图书管理系统",
    agent_count=3
)

# 查看结果
if result['success']:
    print(f"团队：{result['team'].name}")
    print(f"共识：{result['consensus'].content}")
    print(f"计划：{result['plan'].goal}")
    print(f"任务数：{len(result['plan'].tasks)}")
```

### 方式2：启动API服务器

```bash
cd new
python run.py
```

服务器将在 `http://0.0.0.0:5003` 启动

### 方式3：运行测试示例

```bash
cd new
python test_example.py
```

## 四、API接口

### 1. 处理用户需求

```bash
POST /api/requirement
Content-Type: application/json

{
    "requirement": "开发一个电商网站",
    "agent_count": 3
}
```

响应：
```json
{
    "success": true,
    "message": "需求处理成功",
    "team": {
        "id": "xxx",
        "name": "AI协作团队",
        "agents": [...]
    },
    "discussion": {
        "id": "xxx",
        "topic": "如何实现：开发一个电商网站",
        "messages": [...],
        "consensus": "..."
    },
    "plan": {
        "id": "xxx",
        "goal": "开发一个电商网站",
        "tasks": [...]
    }
}
```

### 2. 更新任务进度

```bash
POST /api/task/progress
Content-Type: application/json

{
    "task_id": "xxx",
    "progress": 50
}
```

### 3. 获取当前状态

```bash
GET /api/status
```

响应：
```json
{
    "team": {...},
    "discussion": {...},
    "plan": {...},
    "total_tokens": 12345
}
```

## 五、核心流程说明

### 完整流程
```
用户输入需求
    ↓
1. 分析需求，AI推荐角色
    ↓
2. 创建团队（Team + Agents）
    ↓
3. 团队讨论（Discussion）
   - 多轮讨论
   - 每个Agent发表意见
   - 检查是否达成共识
    ↓
4. 达成共识（Consensus）
    ↓
5. 基于共识创建计划（Plan）
   - 提取具体任务
   - 智能分配给Agent
    ↓
6. 返回完整结果
```

### 讨论流程
```
初始化讨论
    ↓
第1轮：每个Agent发表意见
    ↓
第2轮：每个Agent继续讨论
    ↓
检查共识：意见是否一致？
    ├─ 是 → 达成共识，结束
    └─ 否 → 继续下一轮
    ↓
第N轮：继续讨论
    ↓
达到最大轮数 → 强制生成共识
```

## 六、核心概念

### 1. Agent（智能体）
- 代表团队中的一个成员
- 有角色、技能、状态
- 可以参与讨论、执行任务

### 2. Team（团队）
- 管理多个Agent
- 提供成员查询和管理

### 3. Discussion（讨论）
- 代表一次团队讨论
- 包含多轮对话
- 最终达成共识

### 4. Consensus（共识）
- 团队讨论的结果
- 不可变的值对象
- 用于指导后续计划

### 5. Plan（计划）
- 基于共识制定
- 包含多个任务
- 跟踪执行进度

### 6. Task（任务）
- 具体的执行单元
- 分配给特定Agent
- 有状态和进度

## 七、架构优势

### 1. 清晰的职责分离
- Domain层：业务实体和规则
- Application层：业务流程编排
- Infrastructure层：技术实现
- Presentation层：用户接口

### 2. 无循环依赖
- 单向依赖：Presentation → Application → Domain
- 依赖注入：易于测试和替换

### 3. 统一的数据管理
- StateStore统一管理所有状态
- 单一数据源，避免不一致

### 4. 清晰的业务流程
- WorkflowEngine编排核心流程
- 讨论→共识→计划，逻辑清晰

## 八、扩展示例

### 添加新的领域对象

```python
# new/domain/review.py
@dataclass
class Review:
    """评审实体"""
    id: str
    plan_id: str
    reviewer_id: str
    comments: str
    approved: bool
```

### 添加新的应用服务

```python
# new/application/review_service.py
class ReviewService:
    """评审服务"""
    
    def review_plan(self, plan_id: str, reviewer_id: str):
        # 评审逻辑
        pass
```

### 添加新的API端点

```python
# new/presentation/api.py
@app.route('/api/review', methods=['POST'])
def review_plan():
    # 调用ReviewService
    pass
```

## 九、常见问题

### Q1: 如何修改AI配置？
A: 在创建TeamOrchestrator时传入AIConfig：
```python
ai_config = AIConfig(
    base_url="your-url",
    model="your-model",
    api_key="your-key"
)
orchestrator = TeamOrchestrator(ai_config)
```

### Q2: 如何调整讨论轮数？
A: 在调用run_discussion时指定max_rounds：
```python
discussion = workflow_engine.run_discussion(
    topic="...",
    agents=[...],
    max_rounds=10  # 默认5轮
)
```

### Q3: 如何自定义角色？
A: 直接创建Agent时指定：
```python
agent = Agent(
    id="xxx",
    name="Alice",
    role="自定义角色",
    skills=["技能1", "技能2"]
)
```

### Q4: 如何持久化数据？
A: 扩展StateStore，添加数据库支持：
```python
class DatabaseStateStore(StateStore):
    def save_team(self, team):
        super().save_team(team)
        # 保存到数据库
        db.save(team)
```

## 十、下一步

1. 阅读 `ARCHITECTURE_COMPARISON.md` 了解新旧架构对比
2. 运行 `test_example.py` 查看完整示例
3. 查看各个模块的源代码，了解实现细节
4. 根据需求扩展功能

## 十一、联系方式

如有问题，请查看：
- `README.md` - 项目概述
- `ARCHITECTURE_COMPARISON.md` - 架构对比
- 源代码注释 - 详细说明
