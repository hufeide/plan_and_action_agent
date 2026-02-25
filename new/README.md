# 新架构：基于讨论-共识-协作的AI团队系统

## 核心理念

用户需求 → Agent讨论 → 达成共识 → 协作执行 → 完成任务

## 架构设计

### 1. 清晰的业务流程
```
用户输入需求
    ↓
需求分析（理解需求）
    ↓
团队讨论（多轮讨论）
    ↓
达成共识（形成统一方案）
    ↓
制定计划（基于共识）
    ↓
协作执行（分工合作）
    ↓
完成任务
```

### 2. 分层架构
```
Application Layer（应用层）
├── TeamOrchestrator（团队编排器）- 协调整个流程
└── WorkflowEngine（工作流引擎）- 执行具体流程

Domain Layer（领域层）
├── Team（团队）- 团队聚合根
├── Discussion（讨论）- 讨论聚合根
├── Consensus（共识）- 共识值对象
├── Plan（计划）- 计划聚合根
└── Agent（智能体）- 成员实体

Infrastructure Layer（基础设施层）
├── AIService（AI服务）- 统一的AI调用
└── StateStore（状态存储）- 统一的状态管理
```

### 3. 核心模块

#### Domain Layer（领域层）
- `agent.py` - Agent实体
- `team.py` - Team聚合根
- `discussion.py` - Discussion聚合根
- `consensus.py` - Consensus值对象
- `plan.py` - Plan聚合根
- `task.py` - Task实体

#### Application Layer（应用层）
- `workflow_engine.py` - 工作流引擎
- `team_orchestrator.py` - 团队编排器

#### Infrastructure Layer（基础设施层）
- `ai_service.py` - AI服务
- `state_store.py` - 状态存储

#### Presentation Layer（展示层）
- `api.py` - Flask API

### 4. 关键特性

- **清晰的职责分离**：每个类只做一件事
- **无循环依赖**：单向依赖，依赖注入
- **统一的数据管理**：StateStore统一管理状态
- **清晰的业务流程**：WorkflowEngine编排流程
- **易于测试**：依赖注入，可mock
- **易于扩展**：基于接口编程

## 使用示例

```python
from new.application.team_orchestrator import TeamOrchestrator

# 创建编排器
orchestrator = TeamOrchestrator()

# 处理用户需求
result = orchestrator.handle_user_requirement(
    requirement="开发一个电商网站",
    agent_count=3
)

# 结果包含：
# - 讨论记录
# - 达成的共识
# - 制定的计划
# - 执行结果
```
