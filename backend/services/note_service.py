from datetime import datetime
from extensions import db
from models.note import Note, Notebook, Tag, NoteVersion


# ========== 笔记本 ==========

def list_notebooks(user_id):
    notebooks = Notebook.query.filter_by(user_id=user_id) \
        .order_by(Notebook.sort_order, Notebook.name).all()
    return {'notebooks': [n.to_dict() for n in notebooks]}, 200


def create_notebook(user_id, data):
    name = data.get('name', '').strip()
    if not name:
        return {'error': '名称不能为空'}, 400

    nb = Notebook(
        user_id=user_id,
        name=name,
        color=data.get('color', '#6366f1'),
    )
    db.session.add(nb)
    db.session.commit()
    return {'message': '创建成功', 'notebook': nb.to_dict()}, 201


def update_notebook(user_id, nb_id, data):
    nb = Notebook.query.filter_by(id=nb_id, user_id=user_id).first()
    if not nb:
        return {'error': '笔记本不存在'}, 404

    if 'name' in data:
        nb.name = data['name'].strip()
    if 'color' in data:
        nb.color = data['color']

    db.session.commit()
    return {'message': '更新成功', 'notebook': nb.to_dict()}, 200


def delete_notebook(user_id, nb_id):
    nb = Notebook.query.filter_by(id=nb_id, user_id=user_id).first()
    if not nb:
        return {'error': '笔记本不存在'}, 404

    # 笔记本下的笔记移到无笔记本状态
    Note.query.filter_by(notebook_id=nb_id).update({'notebook_id': None})
    db.session.delete(nb)
    db.session.commit()
    return {'message': '已删除'}, 200


# ========== 标签 ==========

def list_tags(user_id):
    tags = Tag.query.filter_by(user_id=user_id).order_by(Tag.name).all()
    return {'tags': [t.to_dict() for t in tags]}, 200


def create_tag(user_id, data):
    name = data.get('name', '').strip()
    if not name:
        return {'error': '名称不能为空'}, 400

    exists = Tag.query.filter_by(user_id=user_id, name=name).first()
    if exists:
        return {'error': '标签已存在'}, 409

    tag = Tag(user_id=user_id, name=name, color=data.get('color', '#6366f1'))
    db.session.add(tag)
    db.session.commit()
    return {'message': '创建成功', 'tag': tag.to_dict()}, 201


def delete_tag(user_id, tag_id):
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
    if not tag:
        return {'error': '标签不存在'}, 404
    db.session.delete(tag)
    db.session.commit()
    return {'message': '已删除'}, 200


# ========== 笔记 ==========

def list_notes(user_id, notebook_id=None, tag_id=None, search=None, archived=False):
    query = Note.query.filter_by(user_id=user_id, is_archived=archived)

    if notebook_id:
        query = query.filter_by(notebook_id=notebook_id)
    if tag_id:
        tag = Tag.query.get(tag_id)
        if tag:
            query = query.filter(Note.tags.contains(tag))
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(Note.title.ilike(like), Note.content.ilike(like))
        )

    notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()
    return {'notes': [n.to_dict() for n in notes]}, 200


def create_note(user_id, data):
    title = data.get('title', '无标题').strip()
    content = data.get('content', '')
    notebook_id = data.get('notebook_id')
    tag_ids = data.get('tag_ids', [])

    note = Note(
        user_id=user_id,
        title=title,
        content=content,
        content_type=data.get('content_type', 'markdown'),
        notebook_id=notebook_id,
    )

    # 添加标签
    if tag_ids:
        tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
        note.tags = tags

    db.session.add(note)
    db.session.commit()

    # 保存初始版本
    _save_version(note)

    return {'message': '创建成功', 'note': note.to_dict(include_content=True)}, 201


def get_note(user_id, note_id):
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return {'error': '笔记不存在'}, 404
    return {'note': note.to_dict(include_content=True)}, 200


def update_note(user_id, note_id, data):
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return {'error': '笔记不存在'}, 404

    if 'title' in data:
        note.title = data['title'].strip()
    if 'content' in data:
        note.content = data['content']
        # 每次内容变更保存版本（最多保留10个）
        _save_version(note, max_versions=10)
    if 'notebook_id' in data:
        note.notebook_id = data['notebook_id']
    if 'is_pinned' in data:
        note.is_pinned = data['is_pinned']
    if 'is_archived' in data:
        note.is_archived = data['is_archived']
    if 'tag_ids' in data:
        tags = Tag.query.filter(Tag.id.in_(data['tag_ids']), Tag.user_id == user_id).all()
        note.tags = tags

    note.updated_at = datetime.utcnow()
    db.session.commit()

    return {'message': '更新成功', 'note': note.to_dict(include_content=True)}, 200


def delete_note(user_id, note_id):
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return {'error': '笔记不存在'}, 404
    db.session.delete(note)
    db.session.commit()
    return {'message': '已删除'}, 200


def get_versions(user_id, note_id):
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return {'error': '笔记不存在'}, 404

    versions = note.versions.limit(10).all()
    return {'versions': [v.to_dict() for v in versions]}, 200


def restore_version(user_id, note_id, version_id):
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return {'error': '笔记不存在'}, 404

    version = NoteVersion.query.filter_by(id=version_id, note_id=note_id).first()
    if not version:
        return {'error': '版本不存在'}, 404

    note.content = version.content
    note.updated_at = datetime.utcnow()
    _save_version(note, max_versions=10)
    db.session.commit()

    return {'message': '已恢复', 'note': note.to_dict(include_content=True)}, 200


def export_note(user_id, note_id, fmt='markdown'):
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return None, None

    if fmt == 'html':
        import markdown
        html_content = markdown.markdown(note.content or '', extensions=['tables', 'fenced_code'])
        full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{note.title}</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.6}}
code{{background:#f4f4f4;padding:2px 6px;border-radius:3px}}
pre{{background:#f4f4f4;padding:16px;border-radius:6px;overflow-x:auto}}</style>
</head><body><h1>{note.title}</h1>{html_content}</body></html>"""
        return full_html, f'{note.title}.html'
    else:
        return note.content or '', f'{note.title}.md'


def _save_version(note, max_versions=10):
    """保存版本，超过 max_versions 个自动删除最旧的"""
    last = NoteVersion.query.filter_by(note_id=note.id) \
        .order_by(NoteVersion.version_num.desc()).first()

    version_num = (last.version_num + 1) if last else 1

    version = NoteVersion(
        note_id=note.id,
        content=note.content,
        version_num=version_num,
    )
    db.session.add(version)

    # 清理多余版本
    count = NoteVersion.query.filter_by(note_id=note.id).count()
    if count >= max_versions:
        old = NoteVersion.query.filter_by(note_id=note.id) \
            .order_by(NoteVersion.version_num.asc()) \
            .limit(count - max_versions + 1).all()
        for v in old:
            db.session.delete(v)
