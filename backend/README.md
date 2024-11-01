# Websocet
## Websocet доступен по адресу: ws:.../apps/chat/api/chat/ws</h3>
Auth = /ws?ticket=value
### Входящий джейсон:
* chats:
    * chat_id:int
    * message:
        * data:str
        * typ :str (text|voice|video)
        * chanel: str

### Исходящий джейсон
* chat_id: int
* created_by: int
* user_name: str
* message: str
* attachment: attachment_json
* created_at:  str

