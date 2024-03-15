import telebot 
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_user = "kzcashrpc"
rpc_pass = "5uR9VsaYgMpunzYnC2rVxOcz"
rpc_host = "127.0.0.1"
rpc_client = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_host}:8276", timeout=120)

token = '6451449114:AAFuX71HWZwDmJ0aHFOg5mkVKCDf1sEHd0s'

bot = telebot.TeleBot(token)

@bot.message_handler(commands=["start"])
def start(message):
    start = """Привет я telegram bot по kzcash 
    Команды:
    /getbalance - команда для того, чтобы узнать твой баланс
    /getnewaddress - команда для того, чтобы создать новый адрес кошельку 
    /send 'адрес отправителя' 'адрес получателя' 'количество монет' """
    bot.send_message(message.chat.id, start)

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): 
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=["getbalance"])
def get_balance(message):
    balance = rpc_client.getbalance()
    bot.send_message(message.chat.id, balance)

@bot.message_handler(commands=["getnewaddress"])
def get_newaddress(message):
    address = rpc_client.getaddress()
    bot.send_message(message.chat.id, address)

@bot.message_handler(commands=["send"])
def send_coins(message):
    global temp
    args = message.text.split()[1:]
    if len(args) != 3:
        bot.reply_to(message, "Для того, чтобы отправить монеты введите команду:/send адрес_отправителя адрес_ получателя количество_монет")
        return
    sender_address, receiver_address, amount = args

    try:
       inputs = rpc_client.listunspent(0, 9999, [sender_address])

    except JSONRPCException:
       bot.reply_to(message, f"Неправильный адрес кошелька отправителя")
       return
    
    for i in inputs:
       temp = i
       if float(float(temp.get("amount"))) > (float(amount) + 0.001):
            break
    if float(float(temp.get("amount"))) < (float(amount) + 0.001):
       bot.reply_to(message, f"Недостаточно средств в кошельке")
       return
    res = float(temp.get("amount")) - float(amount) - 0.001 
    intTrans = {"txid":temp.get("txid"), "vout": temp.get("vout")}
    try:
       createTrans = rpc_client.createrawtransaction([intTrans], {receiver_address:amount, sender_address:res})
    
    except JSONRPCException:
       bot.reply_to(message, f"Ошибка, простите, повторите попытку снова")
    signTrans = rpc_client.signrawtransaction(createTrans)
    receivedHex = signTrans.get("hex")
    txid = rpc_client.sendrawtransaction(receivedHex)
    bot.reply_to(message, f"Монеты успешно отправлены. ID: {txid}")
  


if __name__ == '__main__':
     bot.infinity_polling()