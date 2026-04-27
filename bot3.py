from flask import Flask, request, jsonify
import requests, re
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # This allows your Google Site to talk to this script

@app.route('/get_answers', methods=['GET'])
def get_answers():
    user_input = request.args.get('url')
    uuid_match = re.search(r'([a-f0-9\-]{36})', user_input)
    if not uuid_match:
        return jsonify({"error": "Invalid URL/UUID"}), 400
    
    quiz_id = uuid_match.group(1)
    details_url = f"https://create.kahoot.it/rest/kahoots/{quiz_id}"
    
    try:
        response = requests.get(details_url, headers={"User-Agent": "Mozilla/5.0"})
        quiz_data = response.json()
        results = []
        
        color_map = {0: "🔴 RED", 1: "🔵 BLUE", 2: "🟡 YELLOW", 3: "🟢 GREEN"}

        for q in quiz_data.get('questions', []):
            question_text = re.sub('<[^<]+?>', '', q.get('question', ''))
            correct_answers = []
            if 'choices' in q:
                for idx, choice in enumerate(q['choices']):
                    if choice.get('correct'):
                        ans_text = re.sub('<[^<]+?>', '', choice.get('answer', ''))
                        correct_answers.append(f"{color_map.get(idx)}: {ans_text}")
            
            results.append({"question": question_text, "answers": correct_answers})
            
        return jsonify({"title": quiz_data.get('title'), "questions": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
