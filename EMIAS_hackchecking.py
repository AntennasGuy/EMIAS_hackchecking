"""
Программа заходит на сайт emias.info (в единую медицинскую информационно-аналитическую систему города Москвы),
запрашивает у пользователя полис и дату и в цикле каждую минуту проверяет изменения в записях к участковому врачу.
Выводится список с врачами и датой, с которой можно записаться к врачу. Если в списке происходят изменения -
выдаёт сообщение и звуковой сигнал.
TODO поставить звуковой сигнал не на все изменения, а только на те, которые становятся ближе к сегодняшнему дню.
TODO на моменте перехода на страницу к врачу сделать выбор из списка врачей, запись к которым нужно мониторить
"""

import time
from re import *
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from colorama import Fore
import winsound


def check(num, reg):
    isvalid = reg.match(num)
    return isvalid


def cook():
    """
    Основная функция, где происходит изначальная магия кулинарии.
    Args:
        browser: основной объект программы (браузер)
        link: ссылка на страницу сервиса
    :return: None
    """
    print('♫♫♫ Эта программа для просмотра свободных записей к участковому врачу на сайте emias.ru ♫♫♫')
    print('=============================================================', end='\n')
    global browser
    link = 'https://emias.info/'

    browser = webdriver.Chrome()
    browser.maximize_window()  # важно максимизировать окно - могут быть проблемы с мобильной версией
    browser.implicitly_wait(10)  # ставим неявное ожидание для загрузки страницы (очень важно)
    browser.get(link)


def get_auth():
    """
    Функция спрашивает данные пользователя для ввода на страницу.
    Args:
        polis_re, year_re: регулярные выражения для проверки ввода полиса и года (день и месяц проверяет условием)
    :return: None
    """
    print("...Спрашиваю данные...")
    print()

    polis_re = compile('(^|)(\d{3})([ ]?)(\d{3})([ ]?)(\d{3})([ ]?)(\d{4})([ ]?)(\d{3})')
    year_re = compile('(^|\s)20[0-2][0-9]')

    global polis, day, month, year

    while True:
        polis = input('Введите номер полиса: ')
        if check(polis, polis_re):
            break
        else:
            print('Указали неверный номер полиса. Попробуйте ещё раз.')

    while True:
        day = input('Введите день: ')
        if int(day) >= 1 and int(day) < 32:
            break
        else:
            print('Укажите правильный день.')

    while True:
        month = input('Введите месяц: ')
        if int(month) >= 1 and int(month) < 13:
            break
        else:
            print('Укажите правильный месяц.')

    while True:
        year = input('Введите год: ')
        if check(year, year_re):
            break
        else:
            print('Указали неверный год. Попробуйте ещё раз.')


def get_page():
    """
    Функция для того чтобы добраться до целевой страницы. Здесь вся работа selenium и ActionChains.
    :return:
    """
    time.sleep(3)
    polis_input = browser.find_element(By.NAME, 'policy')
    day_input = browser.find_element(By.NAME, 'day')
    month_input = browser.find_element(By.NAME, 'month')
    year_input = browser.find_element(By.NAME, 'year')
    time.sleep(2)

    ActionChains(browser).move_to_element(polis_input) \
        .click(polis_input).send_keys(polis) \
        .move_to_element(day_input).click(day_input).send_keys(day) \
        .move_to_element(month_input).click(month_input).send_keys(month) \
        .move_to_element(year_input).click(year_input).send_keys(year).move_to_element_with_offset(year_input, 120, 0) \
        .click().perform()

    time.sleep(1)

    # На случай всплывающего окна (можно будет удалить)
    # cross = login_browser.find_element(By.CSS_SELECTOR, '#modal > div > div > div.eO9X89 > svg')
    # ActionChains(login_browser).move_to_element_with_offset(cross, 60, 0).click().perform()
    # time.sleep(2)
    # ActionChains(login_browser).move_to_element_with_offset(year_input, 120, 0).click().perform()

    doctor = browser.find_element(By.CSS_SELECTOR, '#root > main > div > div.dmQyGi > div.mi1gbc > div > '
                                                   'div.xrpaCl > div:nth-child(2) > ul > '
                                                   'li:nth-child(1) > button')

    ActionChains(browser).move_to_element(doctor).click(doctor).perform()

    time.sleep(2)
    sign_button = browser.find_element(By.CSS_SELECTOR, '#modal > div > div > div.scrollbar.VgcxYO > div > '
                                                        'div.ofe7SI > button')

    ActionChains(browser).move_to_element(sign_button).click().perform()


def check_data():
    """
    Функция для цикличной проверки данных с целевой страницы.
    Args:
        second_dict: контрольный словарь для того чтобы отлавливать изменения в цикле
        names: список имён врачей
        access: список с датами для записи
        first_zip: список кортежей из имен врачей и дат на запись - из него выводятся данные в терминал
    :return:
    """
    second_dict = {}

    while True:

        names = [name.text for name in browser.find_elements(By.CLASS_NAME, 'ZEcwA8')]
        access = [acc.text for acc in browser.find_elements(By.CLASS_NAME, 'lOC3rq')]
        first_zip = zip(names, access)

        print()
        print('==============')
        for sign in first_zip:
            print(sign)
            try:
                if second_dict[sign[0]] != sign[1]:
                    print(Fore.GREEN + '◙◙◙◙')
                    print(Fore.GREEN + f"Произошли изменения! У {sign[0]}")
                    print(Fore.GREEN + '◙◙◙◙')
                    print(Fore.RESET)
                    winsound.Beep(400, 1000)
            except Exception:
                'what'

            second_dict[sign[0]] = sign[1]

        time.sleep(60)
        browser.refresh()
        doctor = browser.find_element(By.CSS_SELECTOR, '#root > main > div > div.dmQyGi > div.mi1gbc > div > '
                                                       'div.xrpaCl > div:nth-child(2) > ul > '
                                                       'li:nth-child(1) > button')
        ActionChains(browser).move_to_element(doctor).click(doctor).perform()

        sign_button = browser.find_element(By.CSS_SELECTOR, '#modal > div > div > div.scrollbar.VgcxYO > div > '
                                                            'div.ofe7SI > button')

        ActionChains(browser).move_to_element(sign_button).click().perform()

        print('==============', end='\n')


if __name__ == '__main__':
    cook()
    get_auth()
    get_page()
    check_data()
