# file: mcp_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/mcp/data', methods=['POST'])
def receive_data():
    mcp_msg = request.get_json()
    # 你可以這裡把 mcp_msg 存入資料庫、推到緩衝區，或直接印出來檢查
    print("[MCP 收到]", mcp_msg)
    return jsonify({"status": "received"}), 200
@app.route('/', methods=['GET'])
def health():
    return "OK", 200


if __name__ == '__main__':
    # 預設監聽 0.0.0.0:8000
    app.run(host='0.0.0.0', port=8000)
