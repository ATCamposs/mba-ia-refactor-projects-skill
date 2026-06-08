from sqlalchemy.orm import joinedload

from database import db
from models.task import Task


def list_tasks_with_relations():
    tasks = Task.query.options(
        joinedload(Task.user),
        joinedload(Task.category),
    ).all()
    result = []
    for task in tasks:
        task_data = _task_to_enriched_dict(task)
        result.append(task_data)
    return result


def get_task_enriched(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return None
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def count_overdue_tasks():
    overdue_count = 0
    for task in Task.query.all():
        if task.is_overdue():
            overdue_count += 1
    return overdue_count


def _task_to_enriched_dict(task):
    task_data = task.to_dict()
    task_data['overdue'] = task.is_overdue()

    if task.user:
        task_data['user_name'] = task.user.name
    else:
        task_data['user_name'] = None

    if task.category:
        task_data['category_name'] = task.category.name
    else:
        task_data['category_name'] = None

    return task_data


def user_task_summary(task):
    task_data = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'overdue': task.is_overdue(),
    }
    return task_data
