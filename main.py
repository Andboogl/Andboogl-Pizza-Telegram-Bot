from telebot import types, TeleBot
from db_handlers import IsExistsError, CannotFoundFieldError
from db_handlers import Db
import texts
import os


bot = TeleBot(os.getenv('TOKEN'))
db = Db('db.db')


NEW_DISH_DATA = []

main_menu_markup = types.ReplyKeyboardMarkup()
main_menu_markup.add(types.KeyboardButton('Головне меню'))


def changing_work_time(message):
    if message.text != '/cancel':
        db.update_work_time(message.text)
        bot.send_message(message.from_user.id, 'Час роботи змінений', reply_markup=main_menu_markup)

    elif message.text == '/cancel':
        bot.send_message(message.from_user.id, 'Операція скасована', reply_markup=main_menu_markup)

def add_dish_to_database(message):
    try:
        if message.text != '/cancel':
            NEW_DISH_DATA.append(int(message.text))
            db.add_dish(NEW_DISH_DATA[0], NEW_DISH_DATA[1], NEW_DISH_DATA[2], NEW_DISH_DATA[3], NEW_DISH_DATA[-1])
            bot.send_message(message.from_user.id, 'Блюдо успішно додано', reply_markup=main_menu_markup)
        
        else:
            bot.send_message(message.from_user.id, 'Операція скасована', reply_markup=main_menu_markup)
    
    except IsExistsError:
        bot.send_message(message.from_user.id, 'Блюдо з таким ID вже існує')
        bot.send_message(message.from_user.id, 'Введи ID ще раз:')
        bot.register_next_step_handler(message, add_dish_to_database)
    
    except ValueError:
        bot.send_message(message.from_user.id, 'ID повиннен бути цілим числом')
        bot.send_message(message.from_user.id, 'Введи ID ще раз:')
        bot.register_next_step_handler(message, add_dish_to_database)

def add_dish_id(message):
    if message.text != '/cancel':
        NEW_DISH_DATA.append(message.text)
        bot.send_message(message.from_user.id, 'Додай ID:')
        bot.register_next_step_handler(message, add_dish_to_database)

    else:
        bot.send_message(message.from_user.id, 'Операція скасована', reply_markup=main_menu_markup)

def add_dish_price(message):
    if message.text != '/cancel':
        if message.content_type == 'text':
            NEW_DISH_DATA.append(message.text)
            bot.send_message(message.from_user.id, 'Додай ціну (напиши  /cancel, щоб відминити дії):')
            bot.register_next_step_handler(message, add_dish_id)
        
        else:
            bot.send_message(message.from_user.id, 'Невірний тип данних. Потрібно відправити боту текст')
    
    else:
        bot.send_message(message.from_user.id, 'Операція скасована', reply_markup=main_menu_markup)

def add_dish_description(message):
    if message.text != '/cancel':
        if message.content_type == 'text':
            NEW_DISH_DATA.append(message.text)
            markup = types.ReplyKeyboardMarkup()
            markup.add('/cancel')

            bot.send_message(message.from_user.id, 'Напиши опис (напиши  /cancel, щоб відминити дії):')
            bot.register_next_step_handler(message, add_dish_price)
    
        else:
            bot.send_message(message.from_user.id, 'Невірний тип данних. Потрібно відправити боту текст')
    
    else:
        bot.send_message(message.from_user.id, 'Операція скасована', reply_markup=main_menu_markup)

def add_dish_name(message):
    if message.text != '/cancel':
        if message.content_type == 'photo':
            NEW_DISH_DATA.append(message.photo[0].file_id)
            print(message.photo[0].file_id)
            markup = types.ReplyKeyboardMarkup()
            markup.add('/cancel')
            bot.send_message(message.from_user.id, 'Введи назву (напиши  /cancel, щоб відминити дії):', reply_markup=markup)
            bot.register_next_step_handler(message, callback=add_dish_description)
        
        else:
            markup = types.ReplyKeyboardMarkup()
            markup.add('/cancel')
            bot.send_message(message.from_user.id, 'Це не фото. Скинь фото ще раз:', reply_markup=markup)
            bot.register_next_step_handler(message, callback=add_dish_name)
    
    else:
        bot.send_message(message.from_user.id, 'Операція скасована', reply_markup=main_menu_markup)

def delete_dish(message):
    if message.text != '/cancel':
        if message.content_type == 'text':
            try:
                db.delete_dish(int(message.text))
                bot.send_message(message.from_user.id, 'Страва видаленна', reply_markup=main_menu_markup)
            
            except CannotFoundFieldError:
                bot.send_message(message.from_user.id, 'Блюда за таким ID не знайденно. Спробуйте ще раз:')
                markup = types.ReplyKeyboardMarkup()
                markup.add('/cancel')

                bot.send_message(message.from_user.id, texts.ID_ENTER_TEXT, reply_markup=markup)
                bot.register_next_step_handler(message, delete_dish)
        
            except ValueError:
                bot.send_message(message.from_user.id, 'ID повинен бути числом')
                markup = types.ReplyKeyboardMarkup()
                markup.add('/cancel')

                bot.send_message(message.from_user.id, texts.ID_ENTER_TEXT, reply_markup=markup)
                bot.register_next_step_handler(message, delete_dish)
    
        
        else:
            bot.send_message(message.from_user.id, 'Це не текстові данні')
            markup = types.ReplyKeyboardMarkup()
            markup.add('/cancel')

            bot.send_message(message.from_user.id, texts.ID_ENTER_TEXT, reply_markup=markup)
            bot.register_next_step_handler(message, delete_dish)
    
    else:
        bot.send_message(message.from_user.id, 'Операція відміненна', reply_markup=main_menu_markup)
    

@bot.message_handler()
def message_handler(message):
    """Обробник повідомленнь."""
    if message.chat.type == 'supergroup':
        bot.send_message(message.chat.id, 'Цей бот не працює у группах. Будь-ласка, напишіть у ЛС.')

    else:
        if message.text.lower() == 'меню':
            dishs = db.get_dishs()

            if dishs:
                for i in dishs:
                    text = f"""<b>{i[1]}</b>
{i[2]}

Ціна: {i[3]}"""
                    
                    if message.from_user.id == 5167252577:
                        text += f'\n<b>Дата додавання у базу: {i[4]}\nID: {i[5]}</b>'
        
                    bot.send_photo(message.from_user.id, i[0], caption=text, parse_mode='html', reply_markup=main_menu_markup)
            
            else:
                text = 'Поки-що у базі нема ніяких блюд'
                bot.send_message(message.from_user.id, text, reply_markup=main_menu_markup)
        
        elif message.text.lower() == 'час роботи':
            work_time = db.get_work_time()
            text = f"Час роботи: {work_time}"
            bot.send_message(message.from_user.id, text, reply_markup=main_menu_markup)
        
        elif message.text.lower() == 'змінити час роботи':
            if message.from_user.id == 5167252577:
                markup = types.ReplyKeyboardMarkup()
                markup.add(types.KeyboardButton('/cancel'))
                bot.send_message(message.from_user.id, texts.CHANGE_WORK_TIME_TEXT, reply_markup=markup)

                bot.register_next_step_handler(message, changing_work_time)
        
        elif message.text.lower() == 'додати страву':
            if message.from_user.id == 5167252577:
                NEW_DISH_DATA.clear()
                markup = types.ReplyKeyboardMarkup()
                markup.add('/cancel')

                bot.send_message(message.from_user.id, 'Скинь фото блюда', reply_markup=markup)
                bot.register_next_step_handler(message, callback=add_dish_name)
        
        elif message.text.lower() == 'видалити страву':
            if message.from_user.id == 5167252577:
                markup = types.ReplyKeyboardMarkup()
                markup.add('/cancel')

                bot.send_message(message.from_user.id, texts.ID_ENTER_TEXT, reply_markup=markup)
                bot.register_next_step_handler(message, delete_dish)
        
        else:
            if message.from_user.id == 5167252577:
                markup = types.ReplyKeyboardMarkup()
                markup.add(
                    types.KeyboardButton('Меню'),
                    types.KeyboardButton('Час роботи')
                    )
                markup.add(
                    types.KeyboardButton('Додати страву'),
                    types.KeyboardButton('Видалити страву')
                    )
                markup.add(types.KeyboardButton('Змінити час роботи'))
                bot.send_message(message.from_user.id, texts.ADMIN_START_TEXT, reply_markup=markup)
            
            else:
                markup = types.ReplyKeyboardMarkup()
                markup.add(
                    types.KeyboardButton('Меню')
                )
                markup.add(
                    types.KeyboardButton('Час роботи')
                )
                bot.send_message(message.from_user.id, texts.START_TEXT, reply_markup=markup)



bot.polling(none_stop=True)
