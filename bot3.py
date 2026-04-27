from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/get_answers', methods=['GET'])
def get_answers():
    kahoot_id = request.args.get('url')
    if not kahoot_id:
        return jsonify({"error": "No ID provided"}), 400

    # Clean the ID if a full URL was pasted
    if "details/" in kahoot_id:
        kahoot_id = kahoot_id.split("details/")[1].split("/")[0]

    # THE FIX: Added 'User-Agent' to trick Kahoot into thinking we are a browser
    api_url = f"https://create.kahoot.it/rest/kahoots/{kahoot_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        
        # Check if Kahoot actually gave us data
        if response.status_code == 403:
            return jsonify({"error": "Kahoot is Private or Restricted"}), 403
        if response.status_code != 200:
            return jsonify({"error": f"Kahoot API returned error {response.status_code}"}), response.status_code

        data = response.json()
        
        questions = []
        for q in data.get('questions', []):
            # Only get the correct answers
            correct_choices = [choice.get('answer') for choice in q.get('choices', []) if choice.get('correct')]
            questions.append({
                "question": q.get('question'),
                "answers": correct_choices
            })

        return jsonify({
            "title": data.get('title'),
            "questions": questions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
