from flask import Flask, request, jsonify, render_template
from assistant import ask_assistant

app = Flask(__name__)


def generate_response(user_input):
    """Заглушка для функции генерации ответа"""
#    return ask_assistant(user_input)
    return f"Ответ на ваш запрос: **{user_input}**"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    response = generate_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
