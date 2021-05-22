from flask import Blueprint, request, jsonify
from .models import db, UserRelation
import json

friends = Blueprint('friends', __name__)

@friends.route('/remove-friend', methods=['GET', 'POST'])
def remove_friend():
    relation = json.loads(request.data)
    relation_id = relation['relation_id']
    if request.method == 'POST':
        relation = UserRelation.query.get(relation_id)
        db.session.delete(relation)
        db.session.commit()

    return jsonify({})
