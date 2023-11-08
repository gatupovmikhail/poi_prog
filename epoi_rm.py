import os
for el in os.listdir():
    try:
        n = int(el.split('_')[0])
    except ValueError:
        continue
    new_list = [str(x) for x in el.split('_')[1:]]
    new_name = '_'.join(new_list)
    if not os.path.exists(new_name):
        os.rename(el,new_name)
    else:
        print('Нельзя переименовать {}'.format(el))
        print('Уже есть файл с именем {}'.format(new_name))
        print('Переименуйте вручную')
        continue
