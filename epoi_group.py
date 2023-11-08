import os
import sys
import PIL  # pip install pillow
from math import floor
from PIL import Image, UnidentifiedImageError
import shutil
import re

NAME_FILE_WITH_PREV_DATA = 'epoi_group_prev_session_data.csv' # в этот файл записываются названия папок из прошлого запуска

global MAX_LEN_OF_NAME_DIRS
MAX_LEN_OF_NAME_DIRS = 29 # full max len of directories in poi. _prog_ учитывается при подсчете.

global MAX_LEN_OF_NAME_PICTURES
MAX_LEN_OF_NAME_PICTURES = 12 # max  len of name of pictures. расширение .bmp и xx_ не учитываем при подсчете!

global REQUIRED_COLOR_DEPTH
REQUIRED_COLOR_DEPTH = '24' # 24 бит/пиксель глубина цвета, то есть по 8 бит на канал, 3 канала.
global SIGN_COLOR_DEPTH
SIGN_COLOR_DEPTH = 'RGB' # RGB - обозначение глубины 24 конкретно для pillow (PIL),подробнее
# смотри https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes

def generate_access_symbols():
    # generating characters, whith you can use for names of final directories and in light programs.
    '''
    this function generate list of characters, which you can use in names of directories, pictures or files.
    :return: str with allowed characters
    '''

    ref_massiv = []
    for letter in range(65,91):
        ref_massiv.append(chr(letter))
    ref_massiv = ''.join(ref_massiv)
    ref_massiv += ref_massiv.lower()
    ref_massiv += '1234567890_'
    return ref_massiv

ref_massiv = generate_access_symbols() # str with allowed characters


def is_letters_latin(row, ref_massiv=ref_massiv):
    # проверяет, все ли символы в строке можно использовать.
    '''
    checks, which characters in row  you can use.
    :param row: row, which is being checked
    :param ref_massiv: row, which contains all allowed characters
    :return: True/False
     False - some forbidden characters are exist.
     True - all characters are allowed
    '''

    for letter in row:
        if not(letter in ref_massiv):
            print('В названии {} есть '.format(row), end='')
            print('недопустимый символ {}'.format(letter))
            print('Символы, которые можно использовать:')
            print(ref_massiv)
            print('(Нельзя использовать русские буквы)')
            return False
    return True


def change_color_depth(name_pic, pic):
    '''
    Меняет глубину цвета картинки на REQUIRED_COLOR_DEPTH (24 бит)
    :param name_pic: Имя картинки
    :param pic: объект библиотеки PILL
    :return: None
    '''
    if not ('.bmp' in name_pic):
        new_name_pic = name_pic + '.bmp'
    else:
        new_name_pic = name_pic
    if not (pic.mode == SIGN_COLOR_DEPTH):
        print('Картинка {} имеет глубину'.format(name_pic) +
              ' цвета не {} бит.'.format(REQUIRED_COLOR_DEPTH))
        print('Конвертируется в картинку с глубиной {} бит'.format(REQUIRED_COLOR_DEPTH))
        pic_24 = pic.convert(SIGN_COLOR_DEPTH)
        os.remove(name_pic)
        pic_24.save(new_name_pic, bitmap_format='bmp')
        print('Переконвертировано')
        print()


def check_name_of_pic(name_pic):
    '''
    Проверяет длину имени картинки. Если она больше чем MAX_LEN_OF_NAME_PICTURES, выдает ошибку
    :param name_pic: Имя картинки с номером и расширением. Пример: 01_red.bmp
    :return:
    '''
    name_pic = name_pic.replace('.bmp', '')
    if '_' in name_pic:
        name_pic = '_'.join(name_pic.split('_')[1:])
    if len(name_pic) > MAX_LEN_OF_NAME_PICTURES:
        print('Длина итогового имени картинки {} слишком велика:'.format(name_pic))
        print('{} символов (макс {})'.format(len(name_pic), MAX_LEN_OF_NAME_PICTURES))
        print('Поменяйте название исходной картинки на более короткое.')
        print('Затем перезапустите программу')
        sys.exit()


def checking_of_pictures(path_pic,
                         change_color_depth=change_color_depth,
                         is_letters_latin=is_letters_latin):
    '''
    Проверяет картинки на соответствие требованиям поек
    :param path_pic папка, в которой нужно проверить картинки
    :param change_color_depth: описана выше
    :param is_letters_latin: описана выше
    :return:
    '''

    def is_good_len(name_pic):
        if len(name_pic.replace('.bmp', '')) > MAX_LEN_OF_NAME_PICTURES:
            print('Длина названия картинки {} равна {} символов '.format(name_pic, len(name_pic.replace('.bmp', ''))))
            print('Максимально возможная длина {} символов'.format(MAX_LEN_OF_NAME_PICTURES))
            print('.bmp и xx_ не учитываем. Например у картинки 01_h.bmp будет длина 1')
            return False
        if len(name_pic.replace('.bmp', '')) == 0:
            print('Название картинки должно содержать хотя бы 1 символ')
            return False
        return True

    def is_already_exist(new_name, names_pictures):
        if new_name in names_pictures:
            print('Картинка с таким названием уже существует')
            return True
        else:
            return False

    base_dir = os.getcwd()
    os.chdir(path_pic)
    names_pictures = os.listdir()

    for name_pic in names_pictures:
        try:
            pic = Image.open(name_pic)
        except UnidentifiedImageError:
            print('Warn: ' + name_pic + ' это не картинка или ее не удается открыть')
            continue
        except IsADirectoryError:
            print('Warn: ' + name_pic + ' это папка')
            continue

        if not (pic.format.upper() == 'BMP'):
            print('Неверный формат картинки {}. '.format(name_pic) +
                  'Обнаруженный формат: {} '.format(pic.format) +
                  'Конвертация в BMP')
            if len(name_pic.split('.')) > 1:
                name_without_bmp = name_pic.split('.')[0]
            new_format_name = name_without_bmp + '.bmp'
            pic.save(new_format_name, bitmap_format='bmp')
            os.remove(name_pic)
            name_pic = new_format_name
            pic = Image.open(new_format_name)
            print('Переконвертировано\n')

        change_color_depth(name_pic, pic)

        flag_good_name = True
        if is_good_len(name_pic) == False:
            flag_good_name = False
        if is_letters_latin(name_pic.replace('.bmp', '')) == False:
            flag_good_name = False

        if flag_good_name == False:
            print('Введите другое название')
            new_name = input()
            while (is_already_exist(new_name, names_pictures) == True or
                   is_good_len(new_name) == False or
                   is_letters_latin(new_name.replace('.bmp', '')) == False):
                print('Введите другое название')
                new_name = input()

            if not ('.bmp' in new_name):
                new_name += '.bmp'
            pic.save(name_pic, bitmap_format='bmp')
            os.rename(name_pic, new_name)
    os.chdir(base_dir)


def resizing_and_saving_image(path_pic, path,
                              new_height,
                              check_name_of_pic=check_name_of_pic):
    '''
    Перемещает картинки из одной папки в другую, добавляя номера, подгоняя их высоту и ширину (ширину пропорционально)

    :param path_pic: путь до папки, ОТКУДА будут браться картинки.
    :param path: путь до папки, куда будут сохраняться картинки
    :param new_height: int - требуемая высота картинки в пикселях. Равна количеству пикселей в пойке.
    :param check_name_of_pic: функция описана выше
    :return:
    '''
    num = 0
    names_saved_pic = []
    for name_pic in os.listdir(path_pic):
        try:
            picture = Image.open(os.path.join(path_pic, name_pic))
            num += 1
        except UnidentifiedImageError:
            print('Warn: ' + name_pic + ' это не картинка или ее не удается открыть')
            continue
        except IsADirectoryError:
            print('Warn: ' + name_pic + ' это папка')
            continue

        if num > 99:
            print('Не может быть больше 99 картинок в одной папке. Распределите картинки по нескольким папкам')
            sys.exit()

        old_width = picture.size[0]
        old_height = picture.size[1]
        new_width = int(round(old_width * new_height / old_height))  # Заодно подгоняется ширина, чтобы сохранить пропрорции.
        picture = picture.resize((new_width, new_height))

        if '.bmp' in name_pic:
            name_pic = name_pic.replace('.bmp','')

        name_out_pic = '{:0>2}_{}.bmp'.format(num, name_pic)
        check_name_of_pic(name_out_pic)
        path_name_out_pic = os.path.join(path, name_out_pic)

        picture.save(path_name_out_pic, "BMP")
        names_saved_pic.append(name_out_pic)

    return names_saved_pic


def does_object_exist(name, file_or_dir):
    if file_or_dir == 'dir':
        if os.path.isdir(name):
            return True
        else:
            print('Не найдена папка с именем {}, возможно вы ошиблись в названии,\n'.format(name) +
                  'либо же ваша папка находится не в одной папке с программой.\n' +
                  'Введите правильное название. Если хотите прервать программу,' +
                  ' просто нажмите Enter')
            return False


def seacrh_of_picdir(prohod=1, does_object_exist=does_object_exist):
    directories = []
    files = []
    for something in os.listdir():
        if os.path.isdir(something):
            directories.append(something)
        if os.path.isfile(something):
            files.append(something)

    # oпределяем имя папки с картинками
    if len(directories) == 1 and prohod == 1:
        path_pic = directories[0]
    else:
        print('Введите имя папки с картинками')
        fl_exist = False
        while not (fl_exist == True):
            path_pic = input()
            if len(path_pic) == 0:
                print('Вы действительно хотите выйти? Если да, еще раз нажмите Enter')
                print('Если нет, введите что-нибудь и нажмите Enter')
                answer = input()
                if len(answer) == 0:
                    sys.exit()
            fl_exist = does_object_exist(path_pic, 'dir')

    return path_pic


def use_data_from_previous_sessions(name_file_with_prev_data=NAME_FILE_WITH_PREV_DATA):
    if name_file_with_prev_data in os.listdir():
        file_prev_data = open(name_file_with_prev_data, 'r')
        header_data = file_prev_data.readline()[:-1].split(',')
        values_data = file_prev_data.readline()[:-1].split(',')
        prev_data = dict(zip(header_data, values_data))
        path_pic = prev_data['папка_с_картинками']
        name_dir_out = prev_data['имя_будущей_папки_для_реквизита']
        print('Обнаружены названия из предыдущего запуска:')
        print()
        for key, val in prev_data.items():
            print(key + ': ' + val)

        print('Использовать названия файлов и папок из предыдущего запуска? ' +
              'Если да, нажмите Enter. Если нет, напечатайте что-нибудь и нажмите Enter.')
        answer = input()
        if len(answer) == 0:
            use_previous_data = True
        else:
            use_previous_data = False
    else:
        use_previous_data = False

    if use_previous_data == True:
        return path_pic, name_dir_out
    else:
        return False, False

def isint(num):
    try:
        h = int(num)
        return True
    except ValueError:
        print('Значение должно быть целым числом')
        return False


def input_and_checking_name_of_output_dir(is_letters_latin=is_letters_latin, isint=isint):
    print('ВВедите имя будущей папки для реквизита. Помните, что оно должно начинаться с  XX_group_ или с XX_prog_')
    print('где XX - порядковый  номер программы на пойке')
    name_dir_out = input()

    flag_good_name = False
    while (flag_good_name == False):
        flag_good_name = True

        if not('_group_' in name_dir_out) and not('_prog_' in name_dir_out):
            print('Имя должно начинаться с номера программы, за которым идет _group_ или _prog_ (обратите внимание ' +
                  'на нижние подчеркивания!')
            flag_good_name = False

        if (not (len(name_dir_out.split('_')[0]) == 2) or
                not (isint(name_dir_out.split('_')[0]))):
            print('Название папки должно начинаться с номера папки')
            print('Номер папки должен быть в двухзначном формате')
            print('Пример: 01_group_somebody')
            flag_good_name = False

        if len(name_dir_out) > MAX_LEN_OF_NAME_DIRS or len(name_dir_out) == 0:
            print('Длина имени пойки должна быть меньше {} символов '.format(MAX_LEN_OF_NAME_DIRS) +
                  'и содержать хотя бы 1 символ.')
            flag_good_name = False

        if is_letters_latin(name_dir_out) == False:
            flag_good_name = False

        if flag_good_name == False:
            print('Введите другое название')
            name_dir_out = input()

    print('Имя папки для реквизита')
    print(name_dir_out)
    print()
    return name_dir_out


def write_data_for_future_sessions(path_pic, name_dir_out,
                                   name_file_with_future_data=NAME_FILE_WITH_PREV_DATA):
    file_out = open(name_file_with_future_data, 'w')
    header_data = ','.join(['папка_с_картинками', 'имя_будущей_папки_для_реквизита']) + '\n'
    file_out.write(header_data)
    values_data = ','.join([path_pic, name_dir_out]) + '\n'
    file_out.write(values_data)
    file_out.close()
    print('Названия файлов и папок для повторного запуска записаны в ' + name_file_with_future_data)
    print()

def direct(direct):
    path=os.getcwd()
    path = os.path.join(path, direct.split('.')[0])
    if os.path.isdir(path) == False:
        os.mkdir(path) # только на один уровень ниже. иначе исп. makedirs()
        print('Успешно создана папка {}'.format(path))
    else:
        print('Папка  {} уже существует. Пересоздать? '.format(path))
        print('(Если да, просто нажмите Enter.', end=' ')
        print('Если нет, перед нажатием Enter введите что-нибудь в поле)')
        flag_rm = str(input())
        if len(flag_rm) == 0:
            shutil.rmtree(path)
            os.mkdir(path)
            print('Папка  {} пересоздана\n'.format(path))
        else:
            print('Окей, прерываем программу.')
            sys.exit()
    return path

def input_only_good_val(is_good):
    fl_good = False
    while fl_good == False:
        val = input().strip()
        fl_good = is_good(val)
    return val

def massiv_of_times(time_metka):
    dtime = []  # абсолютное время относительно точки включения
    stime = []  # абсолютное время относительно точки включения в нужном для e-poi формате
    pop = 0  # для учета секундной задержки
    for j in range(len(time_metka)):
        dtime.append((float(time_metka[j]) - float(time_metka[0])))

    for j in range(len(time_metka)):
        minn = int(floor(dtime[j] // 60))
        sec = int(floor(dtime[j] % 60)) - pop  # минус секунда! Учет секундной задержки. Но не для первого тайминга
        if (sec == -1):
            sec = 59
            minn -= 1
        msec = int(floor((dtime[j] - floor(dtime[j] % 60) - floor(dtime[j] // 60) * 60) * 100))
        if msec > 999:
            print(dtime[j])
            print(floor(dtime[j] // 60))
            print(dtime[j] % 60)
            print((dtime[j] - floor(dtime[j] % 60) - floor(dtime[j] // 60) * 60) * 100)
        stime.append('{:0>2}:{:0>2}:{:0>2}'.format(minn, sec, msec))
        pop = 1
    return stime

def define_speed(name_saved_pic, stime):
    speed_signature = re.findall(r'S\d\dD', name_saved_pic)
    if len(speed_signature) == 1:
        speed_is_number = True
        try:
            speed = int(speed_signature[0][1:-1])
        except ValueError:
            print('Обнаружен шаблон для задания скорости {} в имени {}'.format(speed_signature, name_saved_pic))
            print('ERROR: Не удалось перевести скорость в число. Проверьте шаблон')
            out_st = '{} - {}\n'.format(name_saved_pic, stime)
            speed_is_number = False

        if speed_is_number == True:
            speed = round(float(speed) / 10, 1)
            if 0.2 <= speed <= 9.9:
                print('Спецзадержка {} для картинки {}'.format(speed, name_saved_pic))
                out_st = '{} - {} ({})\n'.format(name_saved_pic, stime, speed)
            else:
                print('Обнаружен шаблон для задания скорости {} в имени {}'.format(speed_signature, name_saved_pic))
                print('ERROR: недопустимое значение задержки {}'.format(speed))
                out_st = '{} - {}\n'.format(name_saved_pic, stime)
    else:
        out_st = '{} - {}\n'.format(name_saved_pic, stime)
    return out_st

def create_program_file(name_saved_pic, name_dir_out, massiv_of_times=massiv_of_times, define_speed=define_speed):
    good_delay = False
    while not (good_delay):
        print('Введите длительность показа картинок в секундах')
        pic_delay = input()
        try:
            pic_delay = float(pic_delay.replace(',','.'))
        except ValueError:
            print('Нужно ввести число')
            continue

        good_delay = True
        if pic_delay <= 0:
            good_delay = False
            print('Число должно быть больше нуля ')

    row_times = []
    for i in range(0,len(name_saved_pic)+1):
        row_times.append(pic_delay*i)

    # intervals = []
    # for j in range(1, len(row_times)):
    #     intervals.append((float(row_times[j]) - float(row_times[j - 1])))
    # intervals.append(0)

    ready_times = massiv_of_times(row_times)
    dop = 'Finish - {}\nRepeat after finish - yes\nLock buttons - no'.format(ready_times[-1])


    with open(os.path.join(name_dir_out,'program.txt'),'w') as file_out:
        for t,pic in zip(ready_times[:-1], name_saved_pic):
            pic = pic.replace('.bmp','')
            out_st = define_speed(pic, t)
            file_out.write(out_st)
        file_out.write(dop)





if __name__ == '__main__':
    path_pic, name_dir_out = use_data_from_previous_sessions()
    if (path_pic == False):
        path_pic = seacrh_of_picdir()
        print("Папка с картинками: {path_pic}".format(path_pic=path_pic))
        print("Если все правильно, введите Enter. Если что-то неверно, напечатайте что-нибудь и нажмите Enter.")

        answer = input()
        if len(answer) == 0:
            pass
        else:
            path_pic = seacrh_of_picdir(prohod=2)

        name_dir_out = input_and_checking_name_of_output_dir()

    print('Проверка картинок в папке с картинками...')
    print()
    checking_of_pictures(path_pic)

    write_data_for_future_sessions(path_pic, name_dir_out)  # запись введенных имен для будущих запусков

    name_path = direct(name_dir_out)

    print('Введите высоту реквизита в пикселях')
    new_hight = input_only_good_val(is_good=isint)
    new_hight = int(new_hight)

    name_saved_pic = resizing_and_saving_image(path_pic, name_path, new_hight)

    if not('group' in name_dir_out):
        create_program_file(name_saved_pic, name_dir_out)

    print('Программа успешно завершена')