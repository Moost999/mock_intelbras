from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configurações do mock (pode ser sobrescrito por variáveis de ambiente)
MOCK_HOST = os.getenv("MOCK_HOST", "0.0.0.0")
MOCK_PORT = int(os.getenv("MOCK_PORT", "10000"))
MOCK_DEBUG = os.getenv("MOCK_DEBUG", "False").lower() == "true"

# Dados simulados
MOCK_USERS = {
    "6": {"name": "Usuário Bloqueado", "status": "blocked"},
    "09201802": {"name": "Usuário VIP", "status": "active"},
    "EC56D271": {"name": "Usuário Normal", "status": "active"}
}

# --- Modo ONLINE (recebe eventos do dispositivo) ---
@app.route('/notification', methods=['POST'])
def event_receiver():
    print("\n📥 Recebendo evento no modo ONLINE...")
    
    # Simula o processamento do boundary (como no código original)
    event_data = {
        "Events": [{
            "Code": "AccessControl",
            "Data": {
                "CardName": "João Silva",
                "CardNo": "EC56D271",
                "CardType": 0,
                "Door": 1,
                "ErrorCode": 0,
                "Method": 1,
                "ReaderID": 1,
                "Status": 0,
                "Type": 0,
                "Entry": 0,
                "UTC": datetime.now().isoformat(),
                "UserID": 123,
                "UserType": 0,
                "DynPWD": "222333"
            }
        }]
    }
    
    print("📋 Evento simulado:", json.dumps(event_data, indent=2))
    
    # Lógica de autorização (como no seu código original)
    card_no = event_data["Events"][0]["Data"]["CardNo"]
    user_id = event_data["Events"][0]["Data"]["UserID"]
    pwd = event_data["Events"][0]["Data"]["DynPWD"]
    
    if user_id == 6:
        return jsonify({"message": "Pagamento não realizado!", "code": "200", "auth": "false"})
    elif card_no in ["EC56D271", "09201802"]:
        return jsonify({"message": "Bem vindo!", "code": "200", "auth": "true"})
    elif pwd and int(pwd) == 222333:
        return jsonify({"message": "Acesso Liberado", "code": "200", "auth": "true"})
    
    return jsonify({"message": "Acesso Negado", "code": "200", "auth": "false"})

# --- Keepalive (para o dispositivo verificar se o servidor está online) ---
@app.route('/keepalive', methods=['GET'])
def keep_alive():
    print("💓 Keepalive recebido")
    return "OK"

# --- API de Controle (simula chamadas CGI do dispositivo Intelbras) ---
@app.route('/cgi-bin/<path:subpath>', methods=['GET'])
def cgi_bin_requests(subpath):
    action = request.args.get('action')
    print(f"\n📡 Recebida requisição CGI: {subpath}?action={action}")
    
    # Simula as respostas do dispositivo
    if action == "getCurrentTime":
        return f"result={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    elif action == "getSystemInfo":
        return "deviceType=Intelbras_AC_Device\nserialNo=MOCK123456"
    
    elif action == "getSoftwareVersion":
        return "version=2.3.5"
    
    elif action == "getSerialNo":
        return "sn=MOCK123456"
    
    elif action == "openDoor":
        door = request.args.get('channel', '1')
        print(f"🚪 Porta {door} aberta simulada")
        return "result=success"
    
    elif action == "getDoorStatus":
        return "Info.status=Close"
    
    return "error=NotImplemented", 501

# --- Health Check (para o Render) ---
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print(f"\n🚀 Servidor mock Intelbras rodando em http://{MOCK_HOST}:{MOCK_PORT}")
    app.run(host=MOCK_HOST, port=MOCK_PORT, debug=MOCK_DEBUG)