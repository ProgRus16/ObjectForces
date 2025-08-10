import telebot
import os
import socket
from gigachat import GigaChat
import json
# Настройки подключения к серверу
HOST = "127.0.0.1"
PORT = 65432

# Токен бота (убедись, что он не публичен!)
bot = telebot.TeleBot("8310217352:AAEJlCKcJcneY6gQ8zhDKUhRGVZCMNOZe0Q")

# Хранилище состояний пользователей
user_states = {}  # {user_id: {'step': ..., 'data': ...}}

# Папка для сохранения файлов
SAVE_DIR = 'submissions'
os.makedirs(SAVE_DIR, exist_ok=True)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    user_id = message.from_user.id
    user_states[user_id] = {'step': 'waiting_task_code'}
    bot.reply_to(
        message,
        "👋 Добро пожаловать!\n"
        "Введите код задачи (например: \"pr000001\"):",
    )

@bot.message_handler(content_types=['text', 'document'])
def handle_all_messages(message):
    user_id = message.from_user.id
    state_info = user_states.get(user_id)

    if not state_info:
        bot.reply_to(message, "Пожалуйста, начните с команды /start")
        return

    step = state_info['step']

    try:
        if step == 'waiting_task_code':
            task_code = message.text.strip()
            if not task_code:
                bot.reply_to(message, "Код задачи не может быть пустым. Попробуйте снова:")
                return

            user_states[user_id] = {'step': 'waiting_user_code', 'task_code': task_code}
            bot.reply_to(message, f"✅ Код задачи: {task_code}\nВведите ваш код участника:")

        elif step == 'waiting_user_code':
            user_code = message.text.strip()
            if not user_code:
                bot.reply_to(message, "Код участника не может быть пустым. Попробуйте снова:")
                return

            user_states[user_id] = {
                'step': 'waiting_answer',
                'task_code': state_info['task_code'],
                'user_code': user_code
            }
            bot.reply_to(message, "📝 Отправьте ваш ответ текстом или файлом с решением.")

        elif step == 'waiting_answer':
            task_code = state_info['task_code']
            user_code = state_info['user_code']
            file_path = None
            answer_type = None

            if message.content_type == 'text':
                answer_text = message.text
                file_path = os.path.join(SAVE_DIR, f"{task_code}_{user_code}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(answer_text)
                answer_type = 'text'

            elif message.content_type == 'document':
                file_info = bot.get_file(message.document.file_id)
                file_name = message.document.file_name
                file_path = os.path.join(SAVE_DIR, f"{task_code}_{user_code}_{file_name}")

                downloaded_file = bot.download_file(file_info.file_path)
                with open(file_path, 'wb') as f:
                    f.write(downloaded_file)
                answer_type = 'file'
            else:
                bot.reply_to(message, "❌ Поддерживаются только текст и файлы. Попробуйте снова.")
                return

            # Успешное сохранение
            bot.reply_to(message, f"✅ {'Текст' if answer_type == 'text' else 'Файл'} успешно сохранён. Отправляю на проверку...")

            # === Отправка на сервер ===
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    print(file_path)
                    # Отправляем путь к файлу (или метаданные)
                    data_to_send = {
                        "task_id": task_code,
                        "participant_name": user_code
                    }

                    # Преобразуем словарь в строку JSON
                    json_data = json.dumps(data_to_send)
                    s.sendall(json_data.encode('utf-8'))
                    response = s.recv(1024).strip()
                    verdict = json.loads(response.decode())
            except Exception as e:
                verdict = f"Ошибка связи с сервером: {e}"

            # Завершаем состояние
            if verdict['result'] == '✅ Верно!':
                bot.reply_to(message, f"📋 Вердикт решения участника {user_code} на задачу {task_code}:\n{verdict['result']}")
            else:
                bot.reply_to(message, f"📋 Вердикт решения участника {user_code} на задачу {task_code} (учтите, что Ваши решения проверяет нейросеть; способы обратной связи указаны в описании бота):\n{verdict['result']}: {verdict['comment']}")
            del user_states[user_id]

        else:
            bot.reply_to(message, "Неизвестное состояние. Пожалуйста, начните с /start.")

    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {e}")
        if user_id in user_states:
            del user_states[user_id]


# Запуск бота
bot.polling(none_stop=True)