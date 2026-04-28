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

    # Clean the ID
    if "details/" in kahoot_id:
        kahoot_id = kahoot_id.split("details/")[1].split("/")[0]
    elif "/" in kahoot_id:
        kahoot_id = kahoot_id.split("/")[-1]

    # Updated API Endpoint
    api_url = f"https://create.kahoot.it/rest/kahoots/{kahoot_id}"
    
    # Advanced headers to look like a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://create.kahoot.it/",
        "Origin": "https://create.kahoot.it"
    }

    try:
        session = requests.Session()
        response = session.get(api_url, headers=headers, timeout=10)
        
        # Log the status for debugging in Render logs
        print(f"Kahoot API Status: {response.status_code}")

        if response.status_code == 403:
            return jsonify({"error": "Access Forbidden. This Kahoot is likely PRIVATE."}), 403
        if response.status_code == 404:
            return jsonify({"error": "Kahoot not found. Check the ID/Link."}), 404
        
        # If it's not JSON, Kahoot blocked the cloud server
        if "application/json" not in response.headers.get('Content-Type', ''):
            return jsonify({"error": "Kahoot blocked the server connection. Try again in 1 minute."}), 429

        data = response.json()
        
        questions = []
        for q in data.get('questions', []):
            # Support for Quiz, True/False, and Multiple Choice
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
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
