from flask import Blueprint, request, jsonify
from flask_login import current_user
from .models import db, UserRelation
import json

users = Blueprint('users', __name__)


@users.route('/accept-user', methods=['GET', 'POST'])
def accept_user():
    relation = json.loads(request.data)
    relation_id = relation['relation_id']
    if request.method == 'POST':
        relation = UserRelation.query.get(relation_id)
        relation.status = 1

        db.session.commit()

    return jsonify({})


@users.route('/decline-user', methods=['GET', 'POST'])
def decline_user():
    print('declining friend request');
    relation = json.loads(request.data)
    relation_id = relation['relation_id']
    if request.method == 'POST':
        relation = UserRelation.query.get(relation_id)
        relation.status = 2

        db.session.commit()

    return jsonify({})


@users.route('/block-user', methods=['GET', 'POST'])
def block_user():
    print('blocking user');
    relation = json.loads(request.data)
    relation_id = relation['relation_id']
    if request.method == 'POST':
        relation = UserRelation.query.get(relation_id)
        relation.status = 3

        db.session.commit()

    return jsonify({})


@users.route('/add-user', methods=['GET', 'POST'])
def add_user():
    print('adding user')
    user = json.loads(request.data)
    user_id = user['user_id']
    if request.method == 'POST':
        relating_relation = UserRelation.query.filter_by(
            relating_user_id=current_user.user_id,
            related_user_id=user_id).first()

        related_relation = UserRelation.query.filter_by(
            relating_user_id=user_id,
            related_user_id=current_user.user_id).first()

        if relating_relation or related_relation:
            if relating_relation:
                if relating_relation.status == 3:
                    return jsonify({})

                relating_relation.status = 0

            if related_relation:
                if related_relation.status == 3:
                    return jsonify({})

                related_relation.relating_user_id = current_user.user_id
                related_relation.related_user_id = user_id
                related_relation.action_user_id = user_id
                related_relation.status = 0

            db.session.commit()

        else:
            new_relation = UserRelation(
                status=0,
                relating_user_id=current_user.user_id,
                related_user_id=user_id,
                action_user_id=user_id
            )

            db.session.add(new_relation)
            db.session.commit()

    return jsonify({})
