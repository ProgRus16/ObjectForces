""" from gigachat import GigaChat

taskText = "Задача: докажите или опровергните, что 24 делится на 8. Решение: 24 = 8 * 3, а это значит, что 24 делится на 8."
cont = "докажем, что это не так. 24 = 2 * 2 * 2 * 3. Мы видим, что среди множителей нет 8, а значит, 24 не делится на 8"
# Укажите ключ авторизации, полученный в личном кабинете, в интерфейсе проекта GigaChat API
with GigaChat(credentials="NzhhM2ExM2ItMDRhNS00YTBhLWJhMjktYTU2NDA5NTEwNDllOjRjZjhlZDZlLWQ3MGItNGE5MC05NmRiLTgyNzY4ZDcxODY0Yw==", verify_ssl_certs=False) as giga:
    prompt = f"Дана математическая задача с оптимальным решением: \"{taskText}\" и её решение, приведённое пользователем: \"{cont}\". Ответь \"ДА\" или \"НЕТ\", правильно ли приведённое решение задачи. не пиши ничего, кроме одного слова \"ДА\" или \"НЕТ\" соответственно. Если не совпадает итоговый ответ, есть упущения в логике и т.п., пиши \"НЕТ\", оценивай по всей строгости и следи, чтобы решение было максимально похоже на оригинальное."
    response = giga.chat(prompt)
    print(response.choices[0].message.content) """
input_string = "somecontent________anothercontent"

# Разделение строки по первому встреченному символу "_":
content_parts = input_string.split("_")

# Теперь удалим оставшиеся знаки подчёркивания в конце первой части и начале второй:
final_parts = [content_parts[0], content_parts[1].lstrip("_")]

print(final_parts)