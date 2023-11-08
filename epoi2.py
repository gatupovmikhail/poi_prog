import shutil
# import psutil
import os
import collections
from math import floor
import sys
import time
import datetime
import re
#sys.setdefaultencoding('utf8')

from PIL import Image, UnidentifiedImageError

###############################################################
global ASK_ABOUT_SAVE_STRUCTURE
ASK_ABOUT_SAVE_STRUCTURE = False
#ASK_ABOUT_SAVE_STRUCTURE = True  # Для сохранения структуры каталогов поек уберите решетку в НАЧАЛЕ строки

global ASK_ABOUT_WRITE_TO_POI
ASK_ABOUT_WRITE_TO_POI = False
#ASK_ABOUT_WRITE_TO_POI = True  # Для записи папки прямо на пойки уберите решетку в НАЧАЛЕ строки

global DO_AUTO_RESIZE
DO_AUTO_RESIZE = True
#Do_AUTO_RESIZE = False


###############################################################

# свернуть код в блоках Ctrl + Shift + +/-
NAME_FILE_WITH_PREV_DATA = 'epoi_prev_session_data.csv' # в этот файл записываются названия файлов и папок из прошлого запуска

global NAME_FILE_POI_NAMES
NAME_FILE_POI_NAMES = 'show_participants.txt' # файл, где хранятся имена и высоты реквизита, участвующего в шоу

global NAME_FILE_STATISTIC
NAME_FILE_STATISTIC = '/home/gatupov/prog/python/ignis_projects/epoi_dir/epoi_prog/statistic_epoi'

global SYSTEM_SIZE
SYSTEM_SIZE = 400 # стандартная ширина картинки, для которой будет вычисляться время показа картинок с *

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

def is_right_format(full_text_of_file_metok):
    # проверяет, везде ли верный формат записи меток

    flag_right_format = True
    for st in full_text_of_file_metok.split('\n'):
        if (not(st.count('>') - 1 == st.count('/')) and 
        not(st.count('>')==st.count('/') and st.count('>')==0)):
            print('Неправильный формат в строке:')
            print('{}'.format(st))
            flag_right_format = False
        if ('all' in st.lower()) and ('/' in st.lower()):
            print('Неправильный формат в строке:')
            print('{}'.format(st))
            print('all не может использоваться в одной строке с другими именами')
            sys.exit()
    if flag_right_format == False:
        print('В данных строках неверное количество > или /')
        sys.exit()


def rems(line):
    # удаление ненужных символов из строки в файле
    line=line.replace(' ','')
    line=line.replace('\t','')
    line=line.replace('\r','')
    line=line.replace('\n','')
    return line

def use_data_from_previous_sessions(name_file_with_prev_data = NAME_FILE_WITH_PREV_DATA,name_file_poi_names=NAME_FILE_POI_NAMES):

    if name_file_with_prev_data in os.listdir():
        file_prev_data = open(name_file_with_prev_data,'r')
        header_data = file_prev_data.readline()[:-1].split(',')
        values_data = file_prev_data.readline()[:-1].split(',')
        prev_data = dict(zip(header_data, values_data))
        name_file = prev_data['файл_меток']
        path_pic = prev_data['папка_с_картинками']
        name_file_out = prev_data['имя_будущей_папки_для_реквизита']
        print('Обнаружены названия из предыдущего запуска:')
        print()
        for key,val in prev_data.items():
            print(key + ': ' + val)
        if os.path.exists(name_file_poi_names):
            print('Файл с указанием имен высоты реквизита: {}'.format(name_file_poi_names))
        print()
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
        return name_file, path_pic, name_file_out
    else:
        return False, False, False
    
def write_data_for_future_sessions(name_file, path_pic, name_file_out,
                                   name_file_with_future_data = NAME_FILE_WITH_PREV_DATA):
    file_out = open(name_file_with_future_data, 'w')
    header_data = ','.join(['файл_меток','папка_с_картинками','имя_будущей_папки_для_реквизита']) + '\n'
    file_out.write(header_data)
    values_data = ','.join([name_file, path_pic, name_file_out]) + '\n'
    file_out.write(values_data)
    file_out.close()
    print('Названия файлов и папок для повторного запуска записаны в '+name_file_with_future_data)
    print()

def does_object_exist(name, file_or_dir):
    if file_or_dir == 'dir':
        if os.path.isdir(name):
            return True
        else:
            print('Не найдена папка с именем {}, возможно вы ошиблись в названии,\n'.format(name) +
                    'либо же ваша папка находится не в одной папке с программой.\n'+
                    'Введите правильное название. Если хотите прервать программу,'+
                  ' просто нажмите Enter')
            return False
    
    if file_or_dir == 'file':
        if os.path.isfile(name):
            return True
        else:
            print('Не найден файл с именем {}, возможно вы не\n'.format(name) +
                    'указали расширение или ошиблись в названии, либо\n'+
                  'же ваш файл находится не в одной папке с программой.\n' +
                    'Введите правильное название. Если хотите прервать '+
                  'программу, просто нажмите Enter')
            return False


def seacrh_of_picdir_and_metok(prohod=1, does_object_exist=does_object_exist):
    directories = []
    files = []
    for something in os.listdir():
        if os.path.isdir(something):
            directories.append(something)
        if os.path.isfile(something):
            files.append(something)
    
    # oпределяем имя папки с картинками
    if len(directories) == 1 and prohod==1:
        path_pic = directories[0]
    else:
        print('Введите имя папки с картинками')
        fl_exist = False
        while not(fl_exist == True):
            path_pic = input()
            if len(path_pic) == 0:
                print('Вы действительно хотите выйти? Если да, еще раз нажмите Enter')
                print('Если нет, введите что-нибудь и нажмите Enter')
                answer = input()
                if len(answer) == 0:
                    sys.exit()
            fl_exist = does_object_exist(path_pic, 'dir')
    # определяем имя файла меток
    if len(files) == 2 and prohod==1:
        for ffile in files:
            if not('.py' in ffile):
                name_file = ffile
    else:
        print('Введите имя дорожки отметок')
        fl_exist = False
        while not(fl_exist == True):
            name_file = input()
            if len(name_file) == 0:
                print('Вы действительно хотите выйти? Если да, еще раз нажмите Enter')
                print('Если нет, введите что-нибудь и нажмите Enter')
                answer = input()
                if len(answer) == 0:
                    sys.exit()
            fl_exist = does_object_exist(name_file, 'file')
    return name_file, path_pic


def isint(num):
    try:
        h = int(num)
        return True
    except ValueError:
        print('Значение должно быть целым числом')
        return False


def input_and_checking_name_of_output_dir(is_letters_latin=is_letters_latin, isint=isint):
    print('ВВедите имя будущей папки для реквизита. Помните, что оно должно начинаться с  XX_prog_')
    print('где XX - порядковый  номер программы у пойки')
    name_file_out=input()
    
    flag_good_name = False
    while(flag_good_name == False):
        flag_good_name = True
        
        if not('_prog_' in name_file_out):
            print('Имя должно начинаться с номера программы, за которым идет _prog_ (обратите внимание ' +
                 'на нижние подчеркивания!')
            flag_good_name = False

        if (not(len(name_file_out.split('_')[0])==2) or
                not(isint(name_file_out.split('_')[0]))):
            print('Название папки должно начинаться с номера папки')
            print('Номер папки должен быть в двухзначном формате')
            print('Пример: 01_prog_somebody')
            flag_good_name=False

        if len(name_file_out) > MAX_LEN_OF_NAME_DIRS or len(name_file_out)==0:
            print('Длина имени пойки должна быть меньше {} символов '.format(MAX_LEN_OF_NAME_DIRS)+
                  'и содержать хотя бы 1 символ.')
            flag_good_name = False

        if is_letters_latin(name_file_out) == False:
            flag_good_name = False
            
        if flag_good_name == False:
            print('Введите другое название')
            name_file_out = input()
    
    print('Имя папки для реквизита')
    print(name_file_out)
    print()
    return name_file_out



def checking_of_itog_name_of_output_dir(name_dir, names_rekv, isint=isint, is_letters_latin=is_letters_latin, rems=rems):
    for name_rekv in names_rekv:
        flag_good_name = False
        while flag_good_name == False:
            flag_good_name = True
            name_itog_dir = name_dir + '_' + name_rekv
            if len(name_itog_dir) > MAX_LEN_OF_NAME_DIRS or len(name_itog_dir) == 0:
                print('Длина итогового имени папки {}'.format(name_itog_dir)+
                      ' должна быть меньше {} символов '.format(MAX_LEN_OF_NAME_DIRS) +
                      'и содержать хотя бы 1 символ.')
                print('Текущая длина итогового названия: {}'.format(len(name_itog_dir)))
                print('Уменьшите исходное название {}'.format(name_dir))
                flag_good_name = False

            if is_letters_latin(name_itog_dir) == False:
                print('Недопустимые символы в названии пойки! ' +
                      'Поменяйте название пойки {}'.format(name_rekv))
                sys.exit()

            if not ('_prog_' in name_itog_dir):
                print('Имя должно начинаться с номера программы, за которым идет _prog_ (обратите внимание ' +
                      'на нижние подчеркивания!')
                flag_good_name = False

            if (not(len(name_itog_dir.split('_')[0]) == 2) or
                    not(isint(name_itog_dir.split('_')[0]))):
                print('Название папки должно начинаться с номера папки')
                print('Номер папки должен быть в двухзначном формате')
                print('Пример: 01_prog_somebody')
                flag_good_name = False

            if flag_good_name == False:
                print('Введите новое название')
                name_dir = rems(input())
    return name_dir


def change_color_depth(name_pic, pic):
    if not('.bmp' in name_pic):
        if len(name_pic.split('.')) > 1:
            new_name_pic = name_pic.split('.')[0]
        new_name_pic = name_pic + '.bmp'
    else:
        new_name_pic = name_pic
    if not(pic.mode == SIGN_COLOR_DEPTH):
        print('Картинка {} имеет глубину'.format(name_pic)+
              ' цвета не {} бит.'.format(REQUIRED_COLOR_DEPTH))
        print('Конвертировать в картинку с глубиной {} бит? yes/no'.format(REQUIRED_COLOR_DEPTH))
        answer = input()
        answer = answer.lower().strip()
        while not(answer in ('no', 'yes')):
            print('Недопустимый ответ.')
            print('Допустимые значения ответа: yes no')
            answer = input()
            answer = answer.lower().strip()
        if answer == 'yes':
            pic_24 = pic.convert(SIGN_COLOR_DEPTH)
            os.remove(name_pic)
            pic_24.save(new_name_pic, bitmap_format='bmp')
            print('Переконвертировано')
        if answer == 'no':
            print('Хорошо, пропускаем. Но пойка не примет картинку с такой глубиной цвета')
            
def check_name_of_pic(name_pic):
    name_pic = name_pic.replace('.bmp','')
    if '_' in name_pic:
        name_pic = '_'.join(name_pic.split('_')[1:])
    if len(name_pic) > MAX_LEN_OF_NAME_PICTURES:
        print('Длина итогового имени картинки {} слишком велика:'.format(name_pic))
        print('{} символов (макс {})'.format(len(name_pic), MAX_LEN_OF_NAME_PICTURES))
        print('Поменяйте название исходной картинки на более короткое. (в метках тоже!)')
        print('Затем перезапустите программу')
        sys.exit()
        
def checking_of_pictures(path_pic, name_file, 
                         change_color_depth=change_color_depth, 
                         is_letters_latin=is_letters_latin):

    def replace_of_wrong_names_pic(text, name_pic, new_name):
        ends = ('/', '*/', '$/', '\n', '*\n', '$\n', '\r', '*\r', '$\r')
        ends = (' /', '* /', '$ /', ' \n', '* \n', '$ \n', ' \r', '* \r', '$ \r') + ends
        ends = ('  /', '*  /', '$  /', '  \n', '*  \n', '$  \n', '  \r', '*  \r', '$  \r') + ends
        begs = ('>', '\t', '> ', '\t ', '>  ', '\t  ')
        for beg in begs:
            for end in ends:
                text = text.replace(beg+name_pic+end, beg+new_name+end)
        return text

    def is_good_len(name_pic):
        if len(name_pic.replace('.bmp','')) > MAX_LEN_OF_NAME_PICTURES:
            print('Длина названия картинки {} равна {} символов '.format(name_pic,len(name_pic.replace('.bmp',''))))
            print('Максимально возможная длина {} символов'.format(MAX_LEN_OF_NAME_PICTURES))
            print('.bmp и xx_ не учитываем. Например у картинки 01_h.bmp будет длина 1')
            return False
        if len(name_pic.replace('.bmp','')) == 0:
            print('Название картинки должно содержать хотя бы 1 символ')
            return False
        return True
    
    def is_already_exist(new_name, names_pictures):
        if new_name in names_pictures:
            print('Картинка с таким названием уже существует')
            return True
        else:
            return False
        
    def checking_blackout(names_pictures):
        if not('blackout.bmp' in names_pictures):
            black = Image.new('RGB', (400,32), (0,0,0))
            black.save('blackout.bmp', bitmap_format='bmp')
    
    base_dir = os.getcwd()
    file_metok = os.path.join(base_dir, name_file)
    os.chdir(path_pic)
    names_pictures = os.listdir()
    
    checking_blackout(names_pictures)
    
    for name_pic in names_pictures:
        try:
            pic = Image.open(name_pic)
        except UnidentifiedImageError:
            print('Warn: '+name_pic + ' это не картинка или ее не удается открыть')
            continue
        except IsADirectoryError:
            print('Warn: '+name_pic + ' это папка')
            continue
        
        
        if not(pic.format.upper() == 'BMP'):
            print('Неверный формат картинки {}. '.format(name_pic) +
                 'Обнаруженный формат: {} '.format(pic.format)+
                 'Требуется формат: BMP')
            print('Переконвертировать картинку в .bmp? yes/no')
            answer = input()
            answer = answer.lower().strip()
            while not(answer in ('yes', 'no')):
                print('Неверный формат ответа.')
                print('Возможные варианты ответа yes no')
                answer = input()
                answer = answer.lower().strip()
            if answer == 'yes':
                if len(name_pic.split('.')) > 1:
                    name_without_bmp = name_pic.split('.')[0]
                new_format_name = name_without_bmp + '.bmp'
                pic.save(new_format_name, bitmap_format='bmp')
                os.remove(name_pic) ###
                name_pic = new_format_name
                pic = Image.open(new_format_name)
                print('Переконвертировано')
            if answer == 'no':
                print('Пропускаем. Но пойка не примет картинку в таком формате')
                
        change_color_depth(name_pic, pic)
        
        flag_good_name = True
        if is_good_len(name_pic)==False:
            flag_good_name = False
        if is_letters_latin(name_pic.replace('.bmp',''))==False:
            flag_good_name = False
            
        if flag_good_name == False:
            print('Введите другое название')
            new_name = input()
            while (is_already_exist(new_name, names_pictures)==True or 
            is_good_len(new_name)==False or
            is_letters_latin(new_name.replace('.bmp',''))==False):
                print('Введите другое название')
                new_name = input()
            
            if not('.bmp' in new_name):
                new_name += '.bmp'
            # win
            #shutil.copy(name_pic, new_name)
            pic.save(new_name, bitmap_format='bmp')
            os.remove(name_pic)
            with open(file_metok,'r') as f_metok:
                text_metok = f_metok.read()
                name_pic = name_pic.replace('.bmp', '')
                new_name = new_name.replace('.bmp', '')
                new_text_metok = replace_of_wrong_names_pic(text_metok, name_pic, new_name)
            with open(file_metok,'w') as f_metok:
                f_metok.write(new_text_metok)
    os.chdir(base_dir)
    


def checking_of_zag_file_format(name_file_poi_names=NAME_FILE_POI_NAMES):
    if os.path.exists(name_file_poi_names):
        with open(name_file_poi_names,'r') as file_poi:
            for zag in file_poi:
                if not(len(zag.split('-')) == 2):
                    print('Опечатка в первой строке файла названий. '+
                          'Исправьте и перезапустите программу')
                    print('Пример строки с правильным оформлением:')
                    print('enot - 64')
                    sys.exit()
    else:
        print('Нет файла {} Создайте файл с этим названием.'.format(name_file_poi_names))


def input_of_participants(name_file_poi_names=NAME_FILE_POI_NAMES,isint=isint,
                          rems=rems, is_letters_latin=is_letters_latin):

    def input_only_good_val(is_good, rems=rems):
        fl_good = False
        while fl_good == False:
            val = rems(input())
            fl_good = is_good(val)
        return val

    def name_not_all(name, input_only_good_val=input_only_good_val,rems=rems):
        while rems(name.lower()) == 'all':
            print('Имя all нельзя использовать. Назовите любым другим именем.')
            name = input_only_good_val(is_good=is_letters_latin)
        return name

    def this_program_will_write_names_and_hights(name_file_poi_names):
        if os.path.exists(name_file_poi_names):
            print('Обнаружен файл с названиями и высотой реквизита {}'.format(name_file_poi_names))
            print('Содержание файла:')
            with open(name_file_poi_names,'r') as file_poi:
                print(file_poi.read())
            print()
            print('Использовать данные из него? Если да, нажмите Enter')
            print('Если нет, напечатайте что-нибудь и нажмите Enter')
            answer = input()
            if len(answer) == 0:
                return False # значит, вводить данные эта программа не будет
            else:
                return True
        else:
            print('Если хотите ввести названия поек и высоту реквизита через эту программу')
            print('Нажмите Enter')
            print('Если хотите сами записать данные в файл, напечатайте что-нибудь и нажмите Enter.')
            print('Затем создайте файл {} запишите туда необходимые данные '.format(name_file_poi_names))
            print('(не забудьте сохранить файл) и снова запустите программу')
            answer = input()
            if not(len(answer) == 0):
                print('Ок, после записи файла перезапустите эту программу. Не забудьте расширение .txt в названии файла')
                sys.exit() # Нужно прервать вообще всю программу
            else:
                return True

    if this_program_will_write_names_and_hights(name_file_poi_names) == False:
        return 0


    print('Введите количество уникальных программ (количество будущих папок)')

    number_programs = input_only_good_val(is_good=isint)
    number_programs = int(number_programs)

    out_text = ''
    if number_programs == 1:
        print('Введите высоту реквизита в пикселях')
        hight = input_only_good_val(is_good=isint)
        hight = int(hight)
        out_text = 'all - {}\n'.format(hight)
    else:
        print('Введите название и высоту реквизита в пикселях '+
             'для каждой световой программы')
        for i in range(number_programs):
            print('Название программы {}'.format(i+1))
            name_program = input_only_good_val(is_good=is_letters_latin)
            name_program = name_not_all(name_program)
            print('Высота реквизита в пикселях у программы {}'.format(i+1))
            hight = input_only_good_val(is_good=isint)
            hight = int(hight)
            out_text = out_text + '{} - {}\n'.format(name_program, hight)

    with open(name_file_poi_names, 'w') as file_poi:
        file_poi.write(out_text)

# создание директорий для разных участников

def direct(name_file):
    path=os.getcwd()
    path = os.path.join(path, name_file.split('.')[0])
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

def changing_and_writing_of_speed(numer, metka, stime, interval, star, dol, 
                                  file_out, pixels_in_one_second=101):
    
    state_of_width = ''
    necessary_width = -1
    add_to_name = ''
    if star==1 and dol==1: # проверка
        print('Ошибка в указаниии метки {}: Одновременно есть * и $'.format(metka))
        print('Измените метку (уберите * или $) и еще раз запустите программу.')
        speed = 9.9
        out_st = '{:0>2}_{} - {} ({})\n'.format(numer,metka,stime,speed)
        state_of_width = 0
    
    if star==0 and dol==0: # не нужно подгонять ни скорость показа, ни ширину картинки
        speed_signature = re.findall(r'S\d\dD', metka)
        if len(speed_signature) == 1:
            speed_is_number = True
            try:
                speed = int(speed_signature[0][1:-1])
            except ValueError:
                print('Обнаружен шаблон для задания скорости {} в имени {}'.format(speed_signature, metka))
                print('ERROR: Не удалось перевести скорость в число. Проверьте шаблон')
                out_st = '{:0>2}_{} - {}\n'.format(numer, metka, stime)
                speed_is_number = False

            if speed_is_number == True:
                speed = round(float(speed)/10, 1)
                if 0.2 <= speed <= 9.9:
                    print('Спецзадержка {} для картинки {}'.format(speed, metka))
                    out_st = '{:0>2}_{} - {} ({})\n'.format(numer, metka, stime, speed)
                else:
                    print('Обнаружен шаблон для задания скорости {} в имени {}'.format(speed_signature, metka))
                    print('ERROR: недопустимое значение задержки {}'.format(speed))
                    out_st = '{:0>2}_{} - {}\n'.format(numer, metka, stime)
        else:
            out_st = '{:0>2}_{} - {}\n'.format(numer,metka,stime)
        state_of_width = 0
    
    if star==0 and dol==1: # ширина картинки уже подрегулирована, на это указывает доллар
        speed=9.9
        out_st = '{:0>2}_{} - {} ({})\n'.format(numer,metka,stime,speed)
        state_of_width = 0
    
    if star==1 and dol==0: # нужно менять скорость показа и, возможно, ширину
        speed=round((interval/SYSTEM_SIZE*1000),1) # задержка
        necessary_width = round(pixels_in_one_second * interval)
        if speed >= 0.2 and speed <= 9.9:
            state_of_width = 0
        if speed > 9.9:
            speed = 9.9
            state_of_width = 1
            add_to_name = 'A'
        if speed < 0.2:
            speed = 9.9  # не ошибка! Ширина картинки подгоняется под 9.9
            state_of_width = -1
            add_to_name = 'A'

        
        out_st = '{:0>2}_{} - {} ({})\n'.format(numer, metka+add_to_name, stime, speed)

    file_out.write(out_st) # запись в programm.txt
    pic_metadata =  {'numer':numer, 
            'metka':metka, 
            'stime':stime, 
            'interval':interval, 
            'state_of_width':state_of_width, 
            'necessary_width':necessary_width,
            'add_to_name':add_to_name}
    return pic_metadata

def warning_message(metka, stime, interval, vstavka, necessary_width):
    if DO_AUTO_RESIZE == False:
        print('\nРазмер картинки {} {}.'.format(metka, vstavka)+
              'Длительность ее показа {} c. Время начала показа {}'.format(interval,stime))
        print('Есть 2 варианта решения проблемы:')
        print('1) Создайте картинку шириной {} пикселей'.format(necessary_width), end='')
        if not( 'плохо' in vstavka):
            print(' и в метках ЗАМЕНИТЕ знак * на $ и измените название картинки ') # (1 секунта = 101 пиксель)
            print('Название картинки должно отличаться от {}'.format(metka))
            print('ОЧЕНЬ рекомендуется не удалять старую картинку, так как она может быть')
            print('задействована в других метках световой программы')
        else:
            print(' при этом НЕЛЬЗЯ менять * на $ в метке')
            print('Название картинки должно быть {}'.format(metka))
        print('2) Возможно автоматическое изменение ширины картинки путем ее '+
             'растягивания по горизонтали в процессе копирования. Исходная картинка не меняется.'+
              ' При этом возможно сильное ухудшение качества, если картинка не '+
             'однотонная. При использовании АВТОМАТИЧЕСКОГО изменения '+
              'ширины картинки НЕ (!) нужно менять * на $ в метках.')
        print('Выберите вариант решения проблемы (введите 1 или 2):')
    else:
        print('Автоматическое изменение ширины картинки {} до {} пикселей'.format(metka, necessary_width))

def obrabotka_of_user_solving(user_solving):
    if len(user_solving) == 0:
        print('Вы ввели: ничего. Нужно ввести 1 или 2.')
        user_solving = input()

    if len(user_solving) == 0:
        print('Вы снова ввели: ничего. Все сломалось. Сейчас вся ваша система сотрется!')
        time.sleep(2)
        print('Да, тупая шутка. Просто перезапустите программу.')
    try:
        user_solving = int(user_solving)
    except ValueError:
        print('Допустимые значения: 1 2')
        print('Вы ввели {}'.format(user_solving))
        print('Поэтому все сломалось. В следующий раз покупайте лицензионное ПО). \n Перезапустите программу.')
        sys.exit()
        
    if not(user_solving in [1,2]):
        print('Допустимые значения: 1 2')
        print('Вы ввели {}'.format(user_solving))
        print('Поэтому все сломалось( Перезапустите программу.')
        sys.exit()
    
    if user_solving == 1:
        print('Ок. Измените картинку и перезапустите программу. '+
             'Не забудьте заменить * на $ в названии метки и поменять само название картинки.')
        sys.exit()
    if user_solving == 2:
        print('Ок')
    return user_solving
    


def resizing_and_saving_image(path_pic, path, pic_metadata,
                              new_height, warning_message=warning_message, 
                              obrobrabotka_of_user_solving=obrabotka_of_user_solving,
                             check_name_of_pic=check_name_of_pic):
    
    num = pic_metadata['numer']
    metka = pic_metadata['metka']
    stime = pic_metadata['stime']
    interval = pic_metadata['interval']
    state_of_width = pic_metadata['state_of_width'] 
    necessary_width = pic_metadata['necessary_width']
    add_to_name = pic_metadata['add_to_name']
    should_ask_user = False
    user_solving = 1
    
    try:
        picture=Image.open(os.path.join(path_pic, metka+'.bmp'))
    except FileNotFoundError:
        print()
        print('НЕТ ФАЙЛА {} \n'.format(os.path.join(path_pic, metka+'.bmp')))
        return ()    
    old_width = picture.size[0]
    old_height = picture.size[1]
    
    vstavka=None
    if state_of_width == -1:
        vstavka = 'слишком мал'
        should_ask_user = True
    if state_of_width == 1:
        vstavka = 'слишком велик'
        should_ask_user = True
    if state_of_width == 0 and not(necessary_width == -1) and not(old_width == SYSTEM_SIZE):
        vstavka = 'не равен {}. Это плохо'.format(SYSTEM_SIZE)
        should_ask_user = True
    
    if should_ask_user == True:
        if 'плохо' in vstavka:
            necessary_width = SYSTEM_SIZE

        warning_message(metka, stime, interval, vstavka, necessary_width)
        if DO_AUTO_RESIZE == False:
            user_solving = input()
            user_solving = obrabotka_of_user_solving(user_solving)
        else:
            user_solving = 2
    
    if  (necessary_width == -1) and (old_height == new_height):
        pass # не меняем картинку она уже соответствует по высоте, а по ширине не важно
           
    if necessary_width == -1 and not(old_height == new_height): #user_solving здесь не важен.
        # ширина не важна, но высоту под высоту пойки надо подогнать.
        new_width = int(round(old_width*new_height/old_height)) # Заодно подгоняется ширина, чтобы сохранить пропрорции.
        picture = picture.resize((new_width, new_height))
    
    if not(necessary_width == -1) and user_solving == 1 and not(old_height == new_height):

        # new_width = int(round(old_width*new_height/old_height))
        # picture = picture.resize((new_width, new_height))
        # хочешь, чтобы волна бежала в 2 раза быстрее? Раскомментируй 2 строчки выше, закомментируй 1 строчку ниже.
        picture = picture.resize((old_width, new_height))
    
    if not(necessary_width == -1) and user_solving == 1 and (old_height == new_height):
        # высота уже какая надо, а ширину пользователь решил подогнать сам.
        pass  # не меняем картинку
    
    if not(necessary_width == -1) and user_solving == 2:  # old_heigth == new_height не важно
        picture = picture.resize((necessary_width, new_height))
        
    name_out_pic = '{:0>2}_{}.bmp'.format(num, metka+add_to_name)
    check_name_of_pic(name_out_pic)
    path_name_out_pic = os.path.join(path, name_out_pic)
    
    picture.save(path_name_out_pic, "BMP") 
    return metka+add_to_name # если что-то добавляли, это учтется. 
    

def row_with_error(element, full_text_of_file_metok):
    st_out = ''
    for st in full_text_of_file_metok.split('\n'):
        if element in st:
            st_out+=st + '\n'
    return st_out

def is_names_in_one_time_unique(person, N_persons, full_text_of_file_metok):
    nrow = 0
    nrow_er = []
    for metka in person:
        nrow += 1
        metka = metka.split(';')
        for name_rekv in metka:
            if metka.count(name_rekv) > 1:
                if not nrow in nrow_er:
                    nrow_er.append(nrow)
    if not(len(nrow_er) == 0):
        print('В одной строке файла меток все имена поек должны различаться')
        print('Обнаружены совпадающие имена поек в одном тайминге:')
        for nrow in nrow_er:
            print(full_text_of_file_metok.split('\n')[nrow + N_persons-1])
        print('Исправьте эти строки в файле меток')
        print('И перезапустите программу')
        print()
        sys.exit()

def same_with_prev_pic(prev_pic,current_pic,current_star,current_dol):
    if current_dol + current_star > 0:
        return False
    if prev_pic['star'] + prev_pic['dol'] > 0:
        return False
    if not(prev_pic['name_pic'] == current_pic):
        return False

    return True


def obrab_of_file_with_participants(name_file_poi_names=NAME_FILE_POI_NAMES,rems=rems):
    rekv = []  # высота реквизита
    person_rekv = []  # имя пойки
    flag_rekv = 0  # количество поек (точнее программ для поек) в шоу
    with open(name_file_poi_names,'r') as input_file:
        for st in input_file:
            if not (len(st.split('-')) == 2):
                print('Неправильный формат заголовка в файле {}!'.format(name_file_poi_names))
                print('Ошибочная строка:')
                print(st)
                print('Исправьте и перезапустите программу.')
                print('Пример правильного оформления:')
                print('enot - 64')
                sys.exit()
            line = st.split('-')[1]
            line = rems(line)  # удаление невидимых символов
            try:
                hight_of_rekv = int(line)
                rekv.append(hight_of_rekv)  # сохранение высоты реквизита
            except ValueError:
                print('Ошибка в строке:')
                print(st, end='')
                print('Указанная в файле высота реквизита должна быть числом!')
                sys.exit()

            line = st.split('-')[0]
            line = rems(line)  # удаление невидимых символов
            person_rekv.append(line)  # сохранение имени пойки
            flag_rekv += 1
    if len(person_rekv) > 1 and 'all' in [x.lower() for x in person_rekv]:
        print('Недопустимое имя пойки all в файле {}'.format(name_file_poi_names))
        print('Если программ несколько, это имя использовать нельзя')
        sys.exit()
    return person_rekv, rekv, flag_rekv

def write_dirs_to_poi(list_out_dirs):
    def computing_occuped_memory_size(path):
        total_size = 0
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                total_size += os.path.getsize(file_path)
        return total_size

    # функция для определения количества свободной памяти на диске. Работает неверно.
    # def computing_free_memory_size(disk):
    #     free = psutil.disk_usage(disk).free
    #     return free

    def write_to_poi():
        print('Хотите записать программы прямо на пойку?')
        print('(Пойка должна быть подключена к компьютеру)')
        print('Если да, то введите yes, если нет -  введите no')
        while True: # будет крутиться, пока не введем yes или no
            answer = input()
            if answer.lower() == 'yes':
                return True
            if answer.lower() == 'no':
                return False
            print('Ответ должен быть yes или no. Введите еще раз')

    def find_of_rekv():
        list_of_rekv = []
        if os.name.lower() == 'posix':
            disk = '/media'
        else:
            print('Для операционной системы {}'.format(os.name))
            print('Данный функционал не разработан')
            sys.exit()

        current_user = os.environ['USER']
        mount_point = os.path.join(disk, current_user)
        for dirname in os.listdir(mount_point):
            if not(dirname.lower() == 'elements'):
                list_of_rekv.append(dirname)
                #print('Найден носитель {}'.format(dirname))
        return list_of_rekv, mount_point

    def save_statistic(path_rekv, turn_on=False):
        if turn_on == False:
            return
        print()
        print('Попытка сохранить структуру дирректорий...')
        print()
        groupID = 'UN'
        # Сохранение groupID
        if not(os.path.exists(NAME_FILE_STATISTIC)):
            print('Файл {} не существует'.format(NAME_FILE_STATISTIC))
            print('Для работы функционала записи структуры папок создайте файл statistic_epoi')
            print('И пропишите ПОЛНЫЙ и ПРАВИЛЬНЫЙ путь к нему в переменной NAME_FILE_STATISTIC')
            print(' в начале кода программы. Тогда функционал заработает при следущем запуске')
            return
        else:
            path_system_epoi = os.path.join(path_rekv,'System')
            path_config_epoi = os.path.join(path_system_epoi,'config.ini')
            if not(os.path.exists(path_system_epoi)) or not(os.path.exists(path_config_epoi)):
                print('Warning! directory System or file config.ini don"t exist')
                print('in {}'.format(path_rekv))
            else:
                with open(path_config_epoi,'r') as conf:
                    for st in conf:
                        if 'groupid' in st.lower():
                            groupID=st[:-1].split('=')[1]

        # извлечение имен всех папок
        list_of_poi_dirs = os.listdir(path_rekv)
        list_of_poi_dirs.sort()
        name_rekv = os.path.split(path_rekv)[1]
        str_of_poi_dirs = '|'.join(list_of_poi_dirs)

        now = datetime.datetime.now()
        now = now.strftime("%d-%m-%Y %H:%M")
        new_st = name_rekv + '|' + str_of_poi_dirs + '|' + groupID + '|' + now

        # находим строчку, которую надо обновить по имени пойки. Если не найдем, просто добавим новую
        with open(NAME_FILE_STATISTIC,'r') as f_stat:
            stat = f_stat.read()
        fl_replace = False
        st_replace = ''
        with open(NAME_FILE_STATISTIC, 'r') as f_stat:
            for st in f_stat:
                if name_rekv in st:
                    fl_replace = True
                    st_replace = st.strip(' \n\r\t')
        if fl_replace == True:
            stat = stat.replace(st_replace, new_st)
        else:
            stat = stat + os.linesep + new_st + os.linesep

        with open(NAME_FILE_STATISTIC,'w') as f_stat:
            f_stat.write(stat)
        print('Статистика успешно записана в {}'.format(NAME_FILE_STATISTIC))





    if not(write_to_poi()):
        return

    we_will_not_repeat = False
    while we_will_not_repeat == False:

        print('Если захотите прервать программу, нажмите Ctrl + C (в терминале)')
        print()
        time.sleep(1)

        if not (len(list_out_dirs) == 1):
            print('Какую световую программу хотите записать? Выберите номер')
            print()
            for i, out_dir in enumerate(list_out_dirs):
                print('{} {}'.format(i, out_dir))
            print()
            list_access_num = [k for k in range(i + 1)]
            str_access_num = ' '.join([str(k) for k in list_access_num])
            answer_num = -20
            while not (answer_num) in list_access_num:
                print('Ответ должен быть одним из чисел {}'.format(str_access_num))
                try:
                    answer_num = int(input())
                except ValueError:
                    answer_num = -20
        else:
            answer_num = 0

        choose_out_dir = list_out_dirs[answer_num]
        print('Выбрана программа {}'.format(os.path.split(choose_out_dir)[1]))
        print()

        list_of_rekv, mount_point = find_of_rekv()
        print('Помните, что кроме поек к компьютеру не должно быть подключено никаких переносных устройств.')
        print('Потому что выбранная папка переносится на ВСЕ подключенные устройства (флешки, карты памяти и т. д.)')
        if len(list_of_rekv) == 0:
            print('Не найдены пойки, подключенные к компьютеру!')
            print('Подключите пойки и после этого нажмите Enter')
            answ = input()
            continue
        print('Программа будет записана на устройства:')
        print()
        for name_rekv in list_of_rekv:
            print(name_rekv)
        print()
        print('Если список устройств верный, введите y.')
        print('Если есть лишние устройства, отключите их, и ТОЛЬКО после этого нажмите Enter')
        print('Программа заново определит список устройств')

        answer_continue = input()
        if not(answer_continue.lower() == 'y') and not(len(answer_continue) == 0):
            print('Нужно либо ввести y, либо не вводить ничего. Попробуйте еще раз')
            answer_continue = input()

        if len(answer_continue) == 0:
            continue

        if answer_continue.lower() == 'y':
            we_will_not_repeat = True
        else:
            continue

        # print('Проверка доступной памяти...')
        # print()
        # normir = 1024 # для перевода в килобайты
        # print('Статистика по памяти')
        # print('Название_пойки\tСвободно_памяти (кб)\tТребуется памяти(кб)\tОстанется памяти(кб)')
        # for name_rekv in list_of_rekv:
        #     req_mem = computing_occuped_memory_size(choose_out_dir)
        #     free_mem = computing_free_memory_size(os.path.join(mount_point,name_rekv))
        #     remain_mem = free_mem -req_mem
        #     message = ''
        #     if remain_mem <= 0:
        #         message = 'Памяти не хватит!'
        #         we_will_not_repeat = False
        #     print('{}\t{}\t{}\t{}\t{}'.format(name_rekv, round(free_mem/normir,1),
        #                                       round(req_mem/normir,1), round(remain_mem/normir,1), message))
        # print()
        # if we_will_not_repeat == False:
        #     print('Недостаточно памяти на пойках (пойке). Освободите место')
        #     print('Затем нажмите Enter. После этого процедура поиска поек и проверки памяти')
        #     print('запустится заново')
        #     answer_not_important = input()
        #     continue
        print()
        if we_will_not_repeat == True:
            for name_rekv in list_of_rekv:
                path_rekv = os.path.join(mount_point,name_rekv)
                print('Идет копирование... Не прерывайте программу')
                name_out_dir = os.path.split(choose_out_dir)[1]
                dst_out_path = os.path.join(path_rekv, name_out_dir)
                if (dst_out_path == path_rekv) or (dst_out_path == mount_point):
                    print('#'*20)
                    print()
                    print('Критическая ошибка с путями!')
                    print('папка для перезаписи {}'.format(dst_out_path))
                    print('Обратитесь в техподдержку коллектива ignis')
                    print()
                    print('#' * 20)

                if os.path.exists(dst_out_path):
                    shutil.rmtree(dst_out_path)
                shutil.copytree(choose_out_dir, dst_out_path)
                print('Папка \n {} \n скопирована в \n {}'.format(choose_out_dir, dst_out_path))
                print()
                save_statistic(path_rekv, ASK_ABOUT_SAVE_STRUCTURE)

        print()
        print('Все успешно. Если хотите загрузить другие папки,')
        print('вставьте в usb компьютера другой реквизит, затем нажмите Enter.')
        print('Если нет, то введите что-нибудь и нажмите Enter')
        answer_about_continue = input()
        if len(answer_about_continue) == 0:
            we_will_not_repeat = False
        else:
            we_will_not_repeat = True

def check_order_time(time_metka):
    for i in range(len(time_metka)-1):
        try:
            t1 = float(time_metka[i])
        except ValueError:
            print('Неправильное время {} в файле меток'.format(time_metka[i]))
            sys.exit()
        try:
            t2 = float(time_metka[i+1])
        except ValueError:
            print('Неправильное время {} в файле меток'.format(time_metka[i+1]))
            sys.exit()
        if t1 >= t2:
            print('Ошибка в таймингах в файле меток! Строчки {}, {}'.format(i,i+1))
            print('Тайминги должны идти по порядку')
            print()
            print('Тайминги \n {}\n {}'.format(t1, t2))
            sys.exit()










name_file, path_pic, name_file_out = use_data_from_previous_sessions()
if (name_file == False):
    name_file, path_pic = seacrh_of_picdir_and_metok()
    print("\nФайл меток: {name_file}".format(name_file=name_file))
    print("Папка с картинками: {path_pic}".format(path_pic=path_pic))
    print("Если все правильно, введите Enter. Если что-то неверно, напечатайте что-нибудь и нажмите Enter.")

    answer = input()
    if len(answer) == 0:
        pass
    else:
        name_file, path_pic = seacrh_of_picdir_and_metok(prohod = 2)
    
    name_file_out = input_and_checking_name_of_output_dir()
    input_of_participants() # если нет названий поек и высоты реквизита, добавляем


print('Проверка картинок в папке с картинками...')
print()
checking_of_pictures(path_pic, name_file)


write_data_for_future_sessions(name_file, path_pic, name_file_out) # запись введенных имен для будущих запусков

if not(os.path.exists(NAME_FILE_POI_NAMES)):
    input_of_participants()



# ОСНОВНЫЕ МАССИВЫ ##############################################
###### Чтобы понять, проще посмотреть на их содержимое. (раскомментировать вывод в конце файла)

time_metka=[] # для абс времени каждой метки в формате файла меток audacity
metka=[] # для имен картинок для каждой метки: запись нескольких через ; Картинки могут повторяться
person=[] # для имен поек для каждой метки: запись нескольких через ;. Имена могут повторяться
full_metki=[] # массив из полного текста (без изменений, как файле) каждой метки
list_out_dirs = [] # здесь будут храниться названия созданных программой папок
ignor_metok = [] # Для многопользовательского режима. В массиве определяется что делать, если имя
#                  пойки не встретилось в метке. False - погасить пойку, True - ничего не делать
# rekv=[] -  высота реквизита
# person_rekv -  # имя пойки
# flag_rekv - количество поек (точнее программ для поек) в шоу
#########################################################################



with open(name_file, 'r') as mfile:
    full_text_of_file_metok = mfile.read()

is_right_format(full_text_of_file_metok)

####Обработка файла с заголовком
person_rekv, rekv, flag_rekv = obrab_of_file_with_participants()

# ОБРАБОТКА ФАЙЛА ОТМЕТОК ############################################################
with open(name_file, 'r') as mfile:
    prev_persons = 'all'
    flag_ignor_metok = False
    num_row = 0
    for st in mfile: # построчная обработка
        if not(len(st.split('\t'))==3) and not('#' in st): # проверка, нет ли какой фигни в виде опечаток.
            print('В файле опечатка! Все строки кроме строк с # должны состоять из 3 колонок, '+
                  'разделенных табуляциями. Ошибочная строка:')
            print(st)
            print('Исправьте и перезапустите программу.' +
                  ' Пример правильного оформления:')
            print('# enot - 64')
            sys.exit()
        else:
            # обработка строк с #
            # ...
            # обработка обычных строк с таймингом
            if not('#' in st):
                num_row += 1
                t1 = st.split('\t')[0].replace(',','.')
                t2 = st.split('\t')[1].replace(',','.')
                if not(t1 == t2):
                    print('WARNING: Тайминги в строке \n {} не равны между собой\n'.format(st))
                
                time_metka.append(t1) # абс время
                s=st.split('\t')[2]

                # обработка режима игнора меток
                if flag_ignor_metok == True and '^' in s:
                    flag_ignor_metok = False
                    s = s.replace('^', '')

                ignor_metok.append(flag_ignor_metok)

                if flag_ignor_metok == False and '^' in s:
                    flag_ignor_metok = True

                # if '^' in s:
                #     flag_ignor_metok = not(flag_ignor_metok)
                s = s.replace('^','')
                full_metki.append(s) # полный текст метки
                # обработка текста метки s
                if '>' in s: # если сразу несколько картинок для 1 тайминга
                    if '/' in s:
                        chasti=s.split('/')
                        person_sbor=''
                        metka_sbor=''
                        for ch in chasti:
                            person_sbor += rems(ch.split('>')[0]) + ';'
                            metka_sbor += rems(ch.split('>')[1]) + ';'
                        person.append(person_sbor[:-1]) # запись всех имен поек для танного тайминга через ;
                        metka.append(metka_sbor[:-1]) # запись всех картинок поек для данного тайминга через ;
                        prev_persons = person_sbor[:-1]
                    else:
                        person.append(rems(s.split('>')[0]))
                        metka.append(rems(s.split('>')[1]))
                        prev_persons = rems(s.split('>')[0])
                else: # если одна картинка для 1 тайминга
                    if num_row == 1 or rems(s).lower() == 'end':
                        person.append('all')
                        metka.append(rems(s))
                    else:
                        curr_metka = ''
                        for i in range(len(prev_persons.split(';'))):
                            curr_metka += rems(s) + ';'
                        person.append(prev_persons)
                        metka.append(curr_metka[:-1])
##################################################################################################
check_order_time(time_metka)

for per_rekv in person_rekv:
    if is_letters_latin(per_rekv) == False:
        print('Поменяйте название пойки {} в файле {}'.format(per_rekv,NAME_FILE_POI_NAMES))
        sys.exit()

is_names_in_one_time_unique(person, len(person_rekv), full_text_of_file_metok)


name_file_out = checking_of_itog_name_of_output_dir(name_file_out, person_rekv)

### Проверка, все ли картинки из файла меток есть в папке
list_pictures = [] # список картинок из файла меток
for el in metka:
    for pc in el.split(';'):
        list_pictures.append(pc)
list_pictures = set(list_pictures)
list_pictures = list(list_pictures)

    # получение названия всех картинок
pictures_in_dir = os.listdir(path_pic)
for i in range(len(pictures_in_dir)):
    pictures_in_dir[i] = pictures_in_dir[i].split('.')[0] # избавляемся от .bmp

fl_picmetka = 0
fl_picend = 0
for pic_metka in list_pictures:
    if '$' in pic_metka:
        number_row_with_element = 0
        for me in metka:
            if pic_metka in me:
                number_row_with_element += 1 # важно, в скольких строках встретили елемент
        if number_row_with_element > 1:
            print('Название картинки с $ не может встречаться в нескольких строках')
            print('Ведь одна и та же картинка не может иметь сразу две ширины в пикселях')
            print('Переименуйте метки с $ и картинки так,')
            print('чтобы все названия картинок в разных строках различались')
            print('Строки с неправильными метками:')
            print(row_with_error(pic_metka, full_text_of_file_metok))
            fl_picmetka = 1

for pic_metka in list_pictures:
    if '$' in pic_metka:
        if pic_metka.replace('$','*') in list_pictures:
            print('Картинка с * не может использоваться с $ Для * нужна картинка')
            print('шириной {} пикселей, а для $ картинка с другой шириной'.format(SYSTEM_SIZE))
            print('Сделайте картинку {} шириной {} пикселей, '.format(pic_metka.replace('$',''), 
                                                                      SYSTEM_SIZE))
            print('а картинку {} переименуйте (в метках тоже)'.format(pic_metka))
            print('Строки с названием картинки:')
            print(row_with_error(pic_metka, full_text_of_file_metok))
            print(row_with_error(pic_metka.replace('$','*'), full_text_of_file_metok))
            fl_picmetka = 1
    pic_metka = pic_metka.replace('*','')
    pic_metka = pic_metka.replace('$','')
    if not(pic_metka in pictures_in_dir) and not(pic_metka.lower() == 'end'):
        fl_picmetka = 1
        print('НЕТ ФАЙЛА {}'.format(pic_metka))
        print('Строчки с названием файла:')
        print(row_with_error(pic_metka, full_text_of_file_metok))
    if pic_metka.lower() == 'end':
        fl_picend = 1

if fl_picend == 0:
    print('В файле меток отсутствует метка выключения end!')

if fl_picmetka==1 or fl_picend==0:
    sys.exit()



# получение списка из НЕПОВТОРЯЮЩИХСЯ имен поек
all_persons=[]
for elem in person:
    pers=elem.split(';')
    for p in pers:
        all_persons.append(p)

persons_uniq=list(collections.Counter(all_persons).keys()) # список из НЕПОВТОРЯЮЩИХСЯ имен поек persons_uniq
rekv2=[int(32)]*len(persons_uniq) # Пока у всех высота реквизита 32.

# соответствие поек в заголовке пойкам в метках
flag_good_header = True
for per in persons_uniq:
    if not(per in person_rekv) and not('all' == per):
        print('Названия пойки {} нет в заголовке!'.format(per))
        print('Пойки, перечисленные в заголовке:')
        for per_rekv in person_rekv:
            print(per_rekv)
        print('Возможно, ошибка в следующих строках:')
        print(row_with_error(per, full_text_of_file_metok))
        flag_good_header = False

if flag_good_header == False:
    print('Ошибка также может быть в самом заголовке.')
    sys.exit()

# Добавка программ, которые есть в файле заголовка (SHOW_PARTICIPANTS)
# но нет в файле меток
for name_prog in person_rekv:
    if not(name_prog in persons_uniq):
        persons_uniq.append(name_prog)
        rekv2.append(int(32))

## Получение реальной высоты реквизита для каждой пойки. Будет храниться в rekv2
if flag_rekv>1:
    for j in range(len(persons_uniq)):
        for i in range(len(person_rekv)):
            if person_rekv[i]==persons_uniq[j]:
                rekv2[j]=rekv[i]
if flag_rekv==1:
    for j in range(len(persons_uniq)):
        rekv2[j]=rekv[0]



        



people=0 # флаг для количества поек

# Если только одна прога people = 1, если их сразу несколько, people = 0
if len(persons_uniq)==1 and persons_uniq[0]=='all':
    people=1 # одна прога на всех
    if flag_rekv==0:
        print("Ошибка: вы не указали длину реквизита в пикселях в файле {}".format(NAME_FILE_POI_NAMES))
        sys.exit()

# Вычисляем абсолютное время относительно точки включения ###############################
dtime=[] # абсолютное время относительно точки включения
stime=[] # абсолютное время относительно точки включения в нужном для e-poi формате
pictures=[]
intervals=[] # относительное время для метки. Вычисляется для настройки скорости при использовании *
pop=0 # для учета секундной задержки
for j in range(len(time_metka)):
    dtime.append((float(time_metka[j]) - float(time_metka[0])))

for j in range(len(time_metka)):
    minn=int(floor(dtime[j]//60))
    sec=int(floor(dtime[j]%60)) - pop # минус секунда! Учет секундной задержки. Но не для первого тайминга
    if (sec == -1):
        sec=59
        minn-=1
    msec = int(floor((dtime[j] - floor(dtime[j] % 60) - floor(dtime[j]//60) * 60) * 100))
    if msec > 999:
        print(dtime[j])
        print(floor(dtime[j]//60))
        print(dtime[j]%60)
        print((dtime[j] - floor(dtime[j] % 60) - floor(dtime[j]//60) * 60) * 100)
    stime.append('{:0>2}:{:0>2}:{:0>2}'.format(minn,sec,msec))
    pop=1



for j in range(1,len(time_metka)):
    intervals.append( ( float(time_metka[j]) - float(time_metka[j-1]) ) )
intervals.append(0)

# ^func
intervals_per = {}
for per in persons_uniq:
    intervals_per[per] = [-1]*len(intervals)
    index_intervals_per = 0

    for index_intervals in range(len(intervals)):
        if (ignor_metok[index_intervals] == False) or \
                (per in person[index_intervals].split(';')) or \
                (person[index_intervals] == 'all'):

            index_intervals_per = index_intervals
            intervals_per[per][index_intervals_per] = intervals[index_intervals]
        else:
            intervals_per[per][index_intervals_per] += intervals[index_intervals]


######## Наполнение папок и создания файла программы: Если одна программа в файле меток
if people==1:
    if flag_rekv==0:
        print("Ошибка: вы не указали длину реквизита в пикселях в начале файла меток")
        sys.exit()
    
    #создание дирректории для пойки. В name_path она будет храниться
    name_path=direct(name_file_out) #d
    list_out_dirs.append(name_path) # добавляем в список созданных папок
    file_out=open(os.path.join(name_path, 'program.txt'),'w') # создание program.txt в папке для пойки


    numer=0
    n_out_rows = 0
    for j in range(len(time_metka)):
        n_out_rows += 1
        star=0 # наличие * в строке
        dol = 0 # наличие $ в строке
        if '*' in metka[j]:
            metka[j] = metka[j].replace('*','')
            star=1
        if '$' in metka[j]:
            metka[j] = metka[j].replace('$','')
            dol=1

        if metka[j].lower() == 'end': # точка выключения
            dop='Finish - {}\nRepeat after finish - no\nLock buttons - yes'.format(stime[j])
            file_out.write(dop)
        else:
            if not metka[j] in pictures: # если картинка еще не была сохранена в нужной папка (нет в pictures)
                numer+=1
                # Нужно ли менять скорость показа картинки (в () указывается задержка)
                pic_metadata = changing_and_writing_of_speed(numer, metka[j], stime[j], intervals[j], 
                                                             star, dol, file_out)
                name_s_pic = resizing_and_saving_image(path_pic, name_path, pic_metadata, rekv[0])
                pictures.append(name_s_pic) # добавление в список сохраненных картинок
            else:
                for p in range(len(pictures)): # если картинка уже была сохранена находим ее индекс в массиве
                    if metka[j]==pictures[p]:
                        break
                # нужно ли менять скорость?
                changing_and_writing_of_speed(p+1, metka[j], stime[j], intervals[j], star, dol, file_out)

    #file_out.write(dop)
    file_out.close()
    n_out_rows += 1
    if n_out_rows > 99:
        print('Количество строк в файле program.txt больше 99. Сократите размер файла меток, чтобы уменьшить программу.')
        sys.exit()
    print()
    print('Картинки и световая программа записаны в '+ name_file_out)
    print()

######## Наполнение папок и создания файла программы: Если несколько программ в файле меток
if people==0:
    person1=[] # промежуточные массивы
    rekv3=[]
    for t in range(len(persons_uniq)):
        if not persons_uniq[t]=='all':
            person1.append(persons_uniq[t])
            rekv3.append(rekv2[t])
    persons_uniq=person1 # здесь названия програм
    rekv=rekv3 # здесь высота реквизита для них 
    per_n=-1
    for per in persons_uniq: # Делаем отдельно для каждой пойки (программы пойки)
        n_out_rows = 0 # проверка на кол-во строк
        prev_pic = {'name_pic':'ABSOLUTELU_NOT_EXIST_NAME_OF_PIC', 'star':1, 'dol':1}
        kombo_pictures=[] # массив для хранения картинок без повторения
        per_n+=1
        numer=0
        name_path=direct(name_file_out+'_'+per) # создание папки под конкретного человека (пойку)
        list_out_dirs.append(name_path)
        file_out=open(os.path.join(name_path, 'program.txt'),'w') # помещение туда program.txt
        for j in range(len(time_metka)): # пробегаемся по всем таймингам
            time_of_pic_show = intervals_per[per][j]
            if metka[j].lower() == 'end':
                dop='Finish - {}\nRepeat after finish - no\nLock buttons - yes'.format(stime[j])
                file_out.write(dop)
            else:
                flag_m=0 # после блока кода скажет, есть ли пойка в данном тайминге
                flag_ignor_metok = ignor_metok[j] # игнорируем метку или нет, если пойки нет в тайминге
                kombo_metka=metka[j].split(';') # массив для картинок одного тайминга
                kombo_person=person[j].split(';') # массив для названий поек одного тайминга
                for m in range(len(kombo_metka)): # аналогично коду выше. Есть ли * и $
                    star = 0
                    dol = 0
                    if '*' in kombo_metka[m]:
                        kombo_metka[m] = kombo_metka[m].replace('*','')
                        star=1
                    if '$' in kombo_metka[m]:
                        kombo_metka[m] = kombo_metka[m].replace('$','')
                        dol=1

                    if per==kombo_person[m] or person[j]=='all': # если в данной метке есть название пойки или all
                        if time_of_pic_show == -1:
                            print('Неверный интервал воспроизведения картинки -1. Обратитесь к разработчику')
                            print('Ошибка связана с использованием ^')
                            print('Если не использовать ^, то все отработает нормально.')
                            print(time_metka[j])
                            sys.exit()

                        if same_with_prev_pic(prev_pic,rems(kombo_metka[m]),star,dol) == True:
                            flag_m = 1
                            continue
                        else:
                            n_out_rows += 1
                        if not kombo_metka[m] in kombo_pictures: # если эта картинка еще не сохранялась в нужной папке
                            # то сохраняем. Аналогично коду для people=1
                            numer+=1
                            pic_metadata = changing_and_writing_of_speed(numer, rems(kombo_metka[m]), 
                                                                         stime[j], time_of_pic_show,
                                                                         star, dol, file_out)
                            name_s_pic = resizing_and_saving_image(path_pic, name_path,
                                                                  pic_metadata, rekv[per_n])
                            kombo_pictures.append(name_s_pic)
                        else: # если уже сохраняли - просто записываем в program.txt. Аналогично коду для people=1
                            for p in range(len(kombo_pictures)):
                                if kombo_metka[m]==kombo_pictures[p]:
                                    break
                            # нужна ли задержка? Аналогично коду для people=1
                            changing_and_writing_of_speed(p+1, rems(kombo_metka[m]), 
                                                         stime[j], time_of_pic_show, star, dol, file_out)
                        flag_m=1
                        prev_pic['name_pic'] = rems(kombo_metka[m])
                        prev_pic['star'] = star
                        prev_pic['dol'] = dol
                if flag_m==0 and flag_ignor_metok == False: # если ни all, ни имя пойки не встретились - значит пойка не должна гореть,
                    # начиная с этого тайминга. Сохраняем картинку blackout (черный цвет) и записываем ее
                    # в program.txt соответствующей пойки. Или не сохраняем, если blackout уже есть в папке
                    if same_with_prev_pic(prev_pic, 'blackout', 0, 0) == True:
                        continue
                    else:
                        n_out_rows += 1
                    if not 'blackout' in kombo_pictures: # сохраняем blackout
                        numer+=1
                        pic_metadata = changing_and_writing_of_speed(numer, 'blackout', 
                                                                         stime[j], intervals[j],
                                                                         0, 0, file_out)
                        resizing_and_saving_image(path_pic, name_path,
                                                  pic_metadata, rekv[per_n])
                        kombo_pictures.append('blackout')
                    else: # blackout уже есть
                        for p in range(len(kombo_pictures)):
                                if 'blackout' == kombo_pictures[p]:
                                    break
                        file_out.write('{:0>2}_{} - {}\n'.format(p+1,'blackout',stime[j]))
                    prev_pic['name_pic'] = 'blackout'
                    prev_pic['star'] = 0
                    prev_pic['dol'] = 0

        file_out.close()
        n_out_rows += 1
        if n_out_rows > 99:
            print('Количество строк в program.txt в '+name_file_out+'_'+per+' больше 99! ')
            print('Сократите файл меток, чтобы уменьшить файл программы')
            sys.exit()
        print()
        print('Картинки и световая программа записаны в '+name_file_out+'_'+per)
        print()

if ASK_ABOUT_WRITE_TO_POI == True:
    write_dirs_to_poi(list_out_dirs)


# На MacOS не будет работать из-за .split('\n'), там функция работает некорректно из-за отличий в разделителе строк ОС

#print()
#print('Техническая информация для программистов')
# print('metka')
# print(metka)
# print('time_metka')
# print(time_metka)
# print('stime')
# print(stime)
# print('dtime')
# print(dtime)
# for m,t,st,dt in zip(metka,time_metka,stime,dtime):
#     print('{} {} {} {}'.format(m,t,st,dt))
# print('persons_uniq')
# print(persons_uniq)
# print('person_rekv')
# print(person_rekv)
# print('rekv')
# print(rekv)
# print(intervals)
# print(intervals_per['a'])
# for t, st, per, fl_ig_met, inter, int_per in zip(time_metka, stime, person, ignor_metok, intervals, intervals_per['a']):
#     print('{} {} {} {} {:0>1} {:0>1}'.format(t, st, per, fl_ig_met, round(inter,2), round(int_per,2)))
