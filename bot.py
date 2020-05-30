import mysql.connector
import telebot
import constants

bot = telebot.TeleBot(constants.token)

#to initialize database
def init_db():
    global mydb
    mydb = mysql.connector.connect(
        host=constants.host,
        user=constants.myusername,
        passwd=constants.mypasswd,
        database="herohamada$bon"
    )
    mycursor = mydb.cursor()
    # mycursor.execute("CREATE DATABASE IF NOT EXISTS herohamada$bon")
    mycursor.execute("CREATE TABLE IF NOT EXISTS herohamada$customers\
    (id INT AUTO_INCREMENT PRIMARY KEY,cust_id INT NOT NULL,bonus INT NOT NULL,\
    code_id VARCHAR(10) NOT NULL)")
    mycursor.execute("CREATE TABLE IF NOT EXISTS herohamada$bonus_tb(\
    code_id VARCHAR(10) PRIMARY KEY,\
    bonus INT NOT NULL)")

#to check user's promocode 
def isExisted(code: str):
    exists = False
    if len(code) == 10:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM herohamada$bonus_tb WHERE code_id = %s"\
        , (code, ))
        if mycursor.fetchone() is not None:
            exists = True
    return exists

#add user's bonus 
def add_bonus(id: int, code: str):
    mycursor = mydb.cursor()
    bonus = 10
    mycursor.execute("INSERT INTO herohamada$customers (cust_id, bonus, code_id) \
    VALUES (%s, %s, %s)", (id, bonus, code))
    mydb.commit()
    print(mycursor.rowcount, "record inserted")


def delete_used_code(code: str):
    mycursor = mydb.cursor()
    mycursor.execute("DELETE FROM herohamada$bonus_tb WHERE code_id = %s", \
    (code,))
    mydb.commit()
    print(1, "record deleted")

# to return user's bonus sum by id 
def bonus_sum(id: int):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT SUM(bonus)\
    FROM herohamada$customers WHERE cust_id = %s",
    (id,))
    res = mycursor.fetchone()
    if res == (None,):
        res = (0,)
    return res

#main keyboard
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True, True)
keyboard1.row('получить бонусы', 'мои бонусы', 'потратить бонусы')

#keyboards to spend
keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2.row('купон на скидку', 'приз')

keyboard3 = telebot.types.ReplyKeyboardMarkup(True)
keyboard3.row('купон на скидку')


@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id, \
    'Добрый день! Спасибо, что выбрали нашу продукцию! Выберите кнопку',\
                     reply_markup=keyboard1)
#main keyboard cases
@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'получить бонусы':
        text = 'Напишите код'
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, check_code_step)
    elif message.text == 'мои бонусы':
        bot.send_message(message.chat.id, 'У вас ' +\
        str(bonus_sum(message.chat.id)[0]) + ' бонусов.', reply_markup=keyboard1)
    elif message.text == 'потратить бонусы':
        currentbonus = bonus_sum(message.chat.id)[0]
        if currentbonus >= 50:
            msg = bot.send_message(message.chat.id, 'Выберите как потратить', reply_markup=keyboard2)
            bot.register_next_step_handler(msg, spend_bonus_step)
        elif 10 <= currentbonus < 50:
            msg = bot.send_message(message.chat.id, 'Выберите как потратить', reply_markup=keyboard3)
            bot.register_next_step_handler(msg, spend_bonus_step)
        else:
            bot.send_message(message.chat.id, 'У вас недостаточно бонусов.', reply_markup=keyboard1)

    else:
        bot.send_message(message.chat.id, 'Выберите кнопку',\
        reply_markup=keyboard1)

def check_code_step(message):
    try:
        if isExisted(message.text):
            check = '+10 бонусов'
            add_bonus(message.chat.id, message.text)
            delete_used_code(message.text)
            bot.reply_to(message, str(check), reply_markup=keyboard1)
        elif isExisted(message.text) is False:
            check = 'Неправильный код'
            bot.send_message(message.chat.id, str(check) + \
            ', попробуйте снова', reply_markup=keyboard1)
        else:
            bot.send_message(message.chat.id, 'Выберите кнопку',\
                     reply_markup=keyboard1)

    except Exception as e:
        bot.reply_to(message, 'Неправильный код')

def spend_bonus_step(message):
    try:
        currentbonus = bonus_sum(message.chat.id)[0]
        choice = message.text
        if choice == 'купон на скидку':
            # delete_bonuses(message.chat.id)
            bot.send_message(message.chat.id, 'СКИДКА НА ' + str(currentbonus/2) + '% при следующей покупке!!!')
            bot.send_photo(message.chat.id, open('to_send.jpg', 'rb'))
            bot.send_message(message.chat.id, 'Выберите кнопку', reply_markup=keyboard1)
        elif choice == 'приз':
            bot.send_message(message.chat.id, 'ЗАЖИГАЛКА!', reply_markup=keyboard1)
            # delete_bonuses(message.chat.id)

    except Exception as e:
        bot.reply_to(message, e.args + 'oooops reply')



if __name__ == '__main__':
    init_db()

try:
    bot.polling(none_stop=True, interval=0)
except Exception as e:
    print('oops polling')

