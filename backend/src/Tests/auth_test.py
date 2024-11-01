# from src.main import app
# from src.config import setting

# from sqlalchemy import select, insert
# from fastapi.testclient import TestClient


# def test_app():
#     client = TestClient(app)

#     with client.websocket_connect('/chat/ws', headers=headers) as websocket:
#         websocket.send_json({
#  "subscriptions": {
#     "channel": [
#       "chat.id2"
#     ],
#     "action": "add"
#  }
# }   )

#         data = websocket.receive_json()

#         assert data == {
#  "subscriptions": {
#     "channel": [
#       "chat.id2"
#     ],
#     "action": "add"
#  }
# }
