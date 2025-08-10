import telebot
import os
import socket
from gigachat import GigaChat
import json

# Настройки подключения к серверу
HOST = "127.0.0.1"
PORT = 65432
SAVE_DIR = 'submissions'
# Токен бота (убедитесь, что он не публичен!)
bot = telebot.TeleBot("8310217352:AAEJlCKcJcneY6gQ8zhDKUhRGVZCMNOZe0Q")

# Хранилище состояний пользователей
user_states = {}

# Список доступных задач (можете заменить на реальные значения)
tasks_list = [
    {"code": "00-000-0-0-0", "title": "Задача №1"},
    {"code": "00-001-0-0-0", "title": "Задача №2"},
    {"code": "00-002-0-0-0", "title": "Задача №3"},
    {"code": "01-001-1-3-2", "title": "ВСОШ по математике, 20/21, первый день, 9 класс, задача 2"}
]

# Создаем inline-клавиатуру с задачами
def create_tasks_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for task in tasks_list:
        button = telebot.types.InlineKeyboardButton(task["title"], callback_data=f'task_{task["code"]}')
        keyboard.add(button)
    return keyboard

# Обработчик команд start/help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    user_states[user_id] = {'step': 'waiting_user_code'}
    bot.reply_to(message, "Привет!\nВыберите задачу:", reply_markup=create_tasks_keyboard())

# Обработка нажатий на кнопки выбора задач
@bot.callback_query_handler(func=lambda call: True)
def process_callback_button(call):
    user_id = call.from_user.id
    task_code = call.data.split('_')[1]
    user_states[user_id]['task_code'] = task_code
    bot.answer_callback_query(callback_query_id=call.id, text="Вы выбрали задачу "+task_code)
    bot.send_message(chat_id=user_id, text=f"Ваш выбор: задача {task_code}.\nТеперь введите ваш персональный код участника:")

# Основная логика обработки сообщений
@bot.message_handler(content_types=['text', 'document'])
def handle_all_messages(message):
    user_id = message.from_user.id
    state_info = user_states.get(user_id)
    
    if not state_info or 'task_code' not in state_info:
        bot.reply_to(message, "Сначала выберите задачу командой /start")
        return

    try:
        if state_info['step'] == 'waiting_user_code':
            user_code = message.text.strip()
            if not user_code:
                bot.reply_to(message, "Ваш код участника не может быть пустым. Повторите ввод:")
                return

            user_states[user_id]['user_code'] = user_code
            bot.reply_to(message, f"✅ Ваш код участника принят.\nОтправьте ваше решение (текст или файл):")
            state_info['step'] = 'waiting_answer'
        
        elif state_info['step'] == 'waiting_answer':
            task_code = state_info['task_code']
            user_code = state_info['user_code']
            
            file_path = None

            if message.content_type == 'text':
                answer_text = message.text
                file_path = os.path.join(SAVE_DIR, f"{task_code}_{user_code}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(answer_text)

                
            elif message.content_type == 'document':
                file_info = bot.get_file(message.document.file_id)
                file_name = message.document.file_name
                file_path = os.path.join(SAVE_DIR, f"{task_code}_{user_code}_{file_name}")
                downloaded_file = bot.download_file(file_info.file_path)
                with open(file_path, 'wb') as f:
                    f.write(downloaded_file)

                    
            else:
                bot.reply_to(message, "Поддерживаются только текстовые сообщения и файлы. Попробуйте ещё раз.")
                return

            # Отправляем на сервер
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    data_to_send = {
                        "task_id": task_code,
                        "participant_name": user_code
                    }
                    json_data = json.dumps(data_to_send)
                    s.sendall(json_data.encode('utf-8'))
                    response = s.recv(1024).strip()
                    verdict = json.loads(response.decode())
            except Exception as e:
                verdict = f"Ошибка связи с сервером: {e}"

            # Отвечаем участнику
            if verdict['result'] == '✅ Верно!':
                bot.reply_to(message, f"📋 Решение участника {user_code} на задачу {task_code}:\n{verdict['result']}")
            else:
                bot.reply_to(message, f"📋 Результат проверки решения участника {user_code} на задачу {task_code}:\n{verdict['result']} ({verdict['comment']})")
            
            # Удаляем состояние
            del user_states[user_id]

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
        if user_id in user_states:
            del user_states[user_id]

# Основной цикл запуска бота
if __name__ == "__main__":
    bot.polling(none_stop=True)