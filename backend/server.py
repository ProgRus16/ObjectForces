import os
from socketserver import BaseRequestHandler, TCPServer
import json
from gigachat import GigaChat

class TaskChecker(BaseRequestHandler):
    def handle(self):
        try:
            print("it worked! 0")
            request_data = self.request.recv(1024).strip()
            data = json.loads(request_data.decode())
            
            task_id = data['task_id']
            participant_name = data['participant_name']
            solution_file_path = f"../tgbot/submissions/{task_id}_{participant_name}.txt"
            problem_file_path = f"tasks/{task_id}.txt"
            print("it worked! 1")
            # Загружаем решение пользователя
            with open(solution_file_path, 'r') as sol_file:
                user_solution = sol_file.read().strip()
            print("it worked! 2")
            # Загружаем условие задачи
            with open(problem_file_path, 'r') as prob_file:
                task_text = prob_file.read().strip()
            print("it worked! 3")
            # Здесь выполняется логика проверки решения
            correct_answer = str(check_solution(user_solution, task_text))
            print("it worked! 4")
            print(correct_answer)
            if correct_answer == 'ДА':
                response = {'result': '✅ Верно!'}
            else:
                response = {'result': '❌ Не верно',
                            'comment': correct_answer.split("_")[1]}
            print("it worked! 5")
            self.request.sendall(json.dumps(response).encode())
            print("it worked! 6")
        except Exception as e:
            print(f"Ошибка: {e}")
            self.request.sendall(b"{'result': false}")

def check_solution(content, taskText):
    with GigaChat(credentials="NzhhM2ExM2ItMDRhNS00YTBhLWJhMjktYTU2NDA5NTEwNDllOjRjZjhlZDZlLWQ3MGItNGE5MC05NmRiLTgyNzY4ZDcxODY0Yw==", verify_ssl_certs=False) as giga:
        response = giga.chat(f"Дана задача: \"{taskText}\" и её решение, приведённое пользователем: \"{content}\". Ответь \"ДА\" или \"НЕТ\", правильно ли приведённое решение задачи. если решение верно, то не пиши ничего, кроме одного слова \"ДА\", в противном случае пиши \"НЕТ\" и через нижнее подчёркивание пиши комментарий (пример: НЕТ_так не работает, потому что (и так далее, продолжаешь)). Если не совпадает итоговый ответ, есть упущения в логике и т.п., пиши \"НЕТ\", оценивай по всей строгости и следи, чтобы решение было максимально похоже на оригинальное. Будь максимально умён и не допускай ошибок - не называй хорошее решение неправильным, а плохое - верным. Если у тебя всё получится - будешь молодец, если не получится - то кому-то капец.")
        return response.choices[0].message.content
if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 65432
    server = TCPServer((HOST, PORT), TaskChecker)
    print("Сервер запущен...")
    server.serve_forever()