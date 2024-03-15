from decimal import Decimal
import json
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
    /send 'адрес отправителя' 'адрес получателя' 'количество монет' -  команда для отправки монет с определенного адреса кошелька
    /listunspent - команда об информации кошелька
    /getaddressmessage 'адрес' - команда для получения баланса адреса """
    bot.send_message(message.chat.id, start)

@bot.message_handler(commands=["getbalance"])
def get_balance(message):
    balance = rpc_client.getbalance()
    bot.send_message(message.chat.id, f"Ваш текущий баланс: {balance} KZC")

@bot.message_handler(commands=["getnewaddress"])
def get_newaddress(message):
    address = rpc_client.getnewaddress()
    bot.send_message(message.chat.id, f"Ваш новый адрес: {address}")

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

@bot.message_handler(commands=['getaddressbalance'])
def get_address_balance(message):
    data_json = rpc_client.listunspent()  
    address = message.text.split()[1]
    amount = None  
    for item in data_json:  
        if item.get("address") == address:
            amount = str(Decimal(item["amount"]))  
            break  
    if amount is not None:
        bot.reply_to(message, f"Баланс адреса {address}: {amount} KZC")
    else:
        bot.reply_to(message, f"Адрес {address} не найден или у него нулевой баланс")

@bot.message_handler(commands=['listunspent'])
def listunspent(message):
    list = rpc_client.listunspent()
    bot.send_message(message.chat.id, f"{list}")

if __name__ == '__main__':
     bot.infinity_polling()
