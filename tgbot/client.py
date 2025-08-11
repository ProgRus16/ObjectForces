import pandas as pd
df = pd.read_parquet('../math_problems.parquet', engine='pyarrow')
# Отключаем ограничения на количество отображаемых столбцов и строк
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Убираем ограничение ширины колонок
pd.set_option('display.width', None)

# Полностью показываем содержимое каждой ячейки
pd.set_option('display.max_colwidth', None)
with open('output.txt', 'w') as f:
    print([
    {"code": f"01-003-3-{i}", "title": f"IMO Math - {i}"} for i in range(len(df.index))
], file=f)