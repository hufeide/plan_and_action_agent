"""
Flask API - 提供RESTful接口
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from application.team_orchestrator import TeamOrchestrator
from infrastructure.ai_service import AIConfig
import os

app = Flask(__name__)
CORS(app)

# 静态文件服务
@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)

# 创建编排器
orchestrator = TeamOrchestrator()

# 用于跟踪是否正在处理需求的标志
is_processing_requirement = False


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok"})


@app.route('/api/requirement', methods=['POST'])
def handle_requirement():
    """
    处理用户需求
    
    Request:
        {
            "requirement": "开发一个电商网站",
            "agent_count": 3
        }
    
    Response:
        {
            "success": bool,
            "message": str,
            "team": {...},
            "discussion": {...},
            "plan": {...}
        }
    """
    global is_processing_requirement
    
    # 检查是否正在处理需求
    if is_processing_requirement:
        return jsonify({
            "success": False,
            "message": "正在处理其他需求，请稍后再试"
        }), 429
    
    data = request.json
    requirement = data.get('requirement')
    agent_count = data.get('agent_count', 3)
    
    if not requirement:
        return jsonify({
            "success": False,
            "message": "需求不能为空"
        }), 400
    
    try:
        # 设置处理标志
        is_processing_requirement = True
        
        result = orchestrator.handle_user_requirement(requirement, agent_count)
        
        return jsonify({
            "success": result["success"],
            "message": result["message"],
            "team": result["team"].to_dict() if result["team"] else None,
            "discussion": result["discussion"].to_dict() if result["discussion"] else None,
            "plan": result["plan"].to_dict() if result["plan"] else None
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"处理失败：{str(e)}"
        }), 500
    finally:
        # 清除处理标志
        is_processing_requirement = False


@app.route('/api/task/progress', methods=['POST'])
def update_task_progress():
    """
    更新任务进度
    
    Request:
        {
            "task_id": "xxx",
            "progress": 50
        }
    """
    data = request.json
    task_id = data.get('task_id')
    progress = data.get('progress', 0)
    
    if not task_id:
        return jsonify({
            "success": False,
            "message": "任务ID不能为空"
        }), 400
    
    try:
        result = orchestrator.update_task_progress(task_id, progress)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新失败：{str(e)}"
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    try:
        status = orchestrator.get_current_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取状态失败：{str(e)}"
        }), 500


@app.route('/api/update-goal', methods=['POST'])
def update_goal():
    """
    更新需求
    
    Request:
        {
            "goal": "新的需求描述"
        }
    """
    data = request.json
    goal = data.get('goal')
    
    if not goal:
        return jsonify({
            "success": False,
            "message": "需求不能为空"
        }), 400
    
    try:
        result = orchestrator.update_goal(goal)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新需求失败：{str(e)}"
        }), 500


@app.route('/api/update-task', methods=['POST'])
def update_task():
    """
    更新任务
    
    Request:
        {
            "task_id": "xxx",
            "description": "新的任务描述",
            "assignee_name": "新的负责人"
        }
    """
    data = request.json
    task_id = data.get('task_id')
    description = data.get('description')
    assignee_name = data.get('assignee_name')
    
    if not task_id or not description or not assignee_name:
        return jsonify({
            "success": False,
            "message": "任务ID、描述和负责人不能为空"
        }), 400
    
    try:
        result = orchestrator.update_task(task_id, description, assignee_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新任务失败：{str(e)}"
        }), 500


@app.route('/api/execute-tasks', methods=['POST'])
def execute_tasks():
    """
    并行执行选中的任务
    
    Request:
        {
            "task_ids": ["task1", "task2"]
        }
    """
    data = request.json
    task_ids = data.get('task_ids', [])
    
    if not task_ids:
        return jsonify({
            "success": False,
            "message": "至少选择一个任务"
        }), 400
    
    try:
        result = orchestrator.execute_tasks(task_ids)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"执行任务失败：{str(e)}"
        }), 500


@app.route('/api/reexecute-plan', methods=['POST'])
def reexecute_plan():
    """
    重新执行计划
    """
    try:
        result = orchestrator.reexecute_plan()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"重新执行失败：{str(e)}"
        }), 500


@app.route('/api/execution-status', methods=['GET'])
def get_execution_status():
    """
    获取执行状态
    """
    try:
        status = orchestrator.get_execution_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取执行状态失败：{str(e)}"
        }), 500


def run_server(host='0.0.0.0', port=5003, debug=False):
    """启动服务器"""
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server(debug=True)
