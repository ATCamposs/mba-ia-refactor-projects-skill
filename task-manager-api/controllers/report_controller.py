from datetime import datetime, timedelta

from flask import jsonify, request
from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from models.user import User


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    p1 = Task.query.filter_by(priority=1).count()
    p2 = Task.query.filter_by(priority=2).count()
    p3 = Task.query.filter_by(priority=3).count()
    p4 = Task.query.filter_by(priority=4).count()
    p5 = Task.query.filter_by(priority=5).count()

    overdue_count = 0
    overdue_list = []
    for task in Task.query.all():
        if task.is_overdue():
            overdue_count += 1
            overdue_list.append({
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (datetime.utcnow() - task.due_date).days,
            })

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago,
    ).count()

    user_stats = _build_user_productivity()

    report = {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': p1,
            'high': p2,
            'medium': p3,
            'low': p4,
            'minimal': p5,
        },
        'overdue': {
            'count': overdue_count,
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    done = pending = in_progress = cancelled = overdue = high_priority = 0

    for task in tasks:
        if task.status == 'done':
            done += 1
        elif task.status == 'pending':
            pending += 1
        elif task.status == 'in_progress':
            in_progress += 1
        elif task.status == 'cancelled':
            cancelled += 1

        if task.priority <= 2:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    report = {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        },
    }
    return jsonify(report), 200


def get_categories():
    categories = Category.query.all()
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    result = []
    for category in categories:
        cat_data = category.to_dict()
        cat_data['task_count'] = counts.get(category.id, 0)
        result.append(cat_data)
    return jsonify(result), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar categoria: {str(e)}")
        return jsonify({'error': 'Erro ao criar categoria'}), 500


def update_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    data = request.get_json()
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    try:
        db.session.commit()
        return jsonify(category.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar categoria: {str(e)}")
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Categoria deletada'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar categoria: {str(e)}")
        return jsonify({'error': 'Erro ao deletar'}), 500


def _build_user_productivity():
    users = User.query.all()
    user_stats = []
    for user in users:
        user_tasks = Task.query.filter_by(user_id=user.id).all()
        total = len(user_tasks)
        completed = sum(1 for task in user_tasks if task.status == 'done')
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })
    return user_stats
