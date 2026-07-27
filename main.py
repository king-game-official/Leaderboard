import os
from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# ---------- ВСЕ СЕКРЕТЫ ЧИТАЕМ ИЗ ОКРУЖЕНИЯ ----------
SECRET_KEY = os.environ.get('API_SECRET_KEY')

MONGO_URI = os.environ.get('MONGO_URI')

# Подключаемся к MongoDB
client = MongoClient(MONGO_URI)
db = client['leaderboard_db']      # имя базы данных
scores = db['scores']              # коллекция для рекордов

# Индекс для быстрой сортировки по убыванию очков
scores.create_index([('score', -1)])

# ---------- ЗАЩИТА API-КЛЮЧОМ ----------
@app.before_request
def check_api_key():
    if request.path == '/score' and request.method == 'POST':
        key = request.headers.get('X-API-Key')
        if not key or key != SECRET_KEY:
            abort(401, description='Invalid API key')

# ---------- СОХРАНЕНИЕ РЕКОРДА ----------
@app.route('/score', methods=['POST'])
def save_score():
    data = request.get_json()
    player = data.get('player')
    score = data.get('score')
    
    if not player or score is None:
        return jsonify({'error': 'Missing player or score'}), 400
    
    try:
        score = int(score)
    except:
        return jsonify({'error': 'Score must be integer'}), 400
    
    if score < 0 or score > 9999999:
        return jsonify({'error': 'Score out of range'}), 400

    record = scores.find_one({'player': player})
    if record:
        if score > record['score']:
            scores.update_one(
                {'_id': record['_id']},
                {'$set': {'score': score, 'updated_at': datetime.utcnow()}}
            )
            return jsonify({'message': 'Record updated', 'new_record': True})
        else:
            return jsonify({'message': 'Not a new record', 'new_record': False})
    else:
        scores.insert_one({
            'player': player,
            'score': score,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        return jsonify({'message': 'Record created', 'new_record': True})

@app.route('/', methods=['GET'])
def home():
    # Получаем общее количество игроков
    total_players = scores.count_documents({})
    
    # Получаем топ-3 игроков
    top_players = scores.find().sort('score', -1).limit(3)
    top_list = [{'player': doc['player'], 'score': doc['score']} for doc in top_players]
    
    # Возвращаем красивую JSON-статистику
    return jsonify({
        'service': 'Leaderboard API',
        'status': 'online',
        'total_players': total_players,
        'top_players': top_list,
        'endpoints': {
            'leaderboard': '/leaderboard',
            'send_score': '/score (POST)',
            'delete_player': '/player (DELETE)'
        }
    })

# ---------- ПОЛУЧЕНИЕ ----------
@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    top = scores.find().sort('score', -1)
    result = [{'player': doc['player'], 'score': doc['score']} for doc in top]
    return jsonify(result)

# ---------- УДАЛЕНИЕ ИГРОКА (ТОЛЬКО ДЛЯ АДМИНА) ----------
@app.route('/player', methods=['DELETE'])
def delete_player():
    # Проверяем API-ключ (тот же, что и для POST)
    key = request.headers.get('X-API-Key')
    if not key or key != SECRET_KEY:
        abort(401, description='Invalid API key')
    
    data = request.get_json()
    player = data.get('player')
    if not player:
        return jsonify({'error': 'Missing player name'}), 400
    
    result = scores.delete_one({'player': player})
    if result.deleted_count == 0:
        return jsonify({'error': 'Player not found'}), 404
    else:
        return jsonify({'message': f'Player {player} deleted successfully'})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
