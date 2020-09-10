from db_models.cardtype import CardType, CardTypeEnum
from db_models.card import Card
from db_models.defence import Defence
from flask_script import Manager
import json

from globals import app, db

manager = Manager(app)


def get_popup_from_json(data: list, name: str) -> str:
    return [next((i for i in data if i.get("name") == name), None)][0]["popUpText"]

def get_url_from_json(data: list, name: str) -> str:
    return [next((i for i in data if i.get("name") == name), None)][0]["popUpURL"]


def create_offence_type(data: list):
    cardTypeOffence = CardType(name='Нападение', color='Red', enumType=CardTypeEnum.OFFENCE)

    cardTypeOffence.cards = [Card(
        name='Шифровальщик',
        popUpText=get_popup_from_json(data, "Шифровальщик"),
        popUpURL=get_url_from_json(data, "Шифровальщик"),
        countInDeck=5,
        damage=7),
        Card(
            name='Кейлоггер',
            popUpText=get_popup_from_json(data, "Кейлоггер"),
            popUpURL=get_url_from_json(data, "Кейлоггер"),
            countInDeck=4,
            damage=5),
        Card(
            name='Удаленное выполнение кода',
            popUpText=get_popup_from_json(data, "Удаленное выполнение кода"),
            popUpURL=get_url_from_json(data, "Удаленное выполнение кода"),
            countInDeck=4,
            damage=7),
        Card(
            name='Посредственный фишинг',
            popUpText=get_popup_from_json(data, "Фишинг"),
            popUpURL=get_url_from_json(data, "Фишинг"),
            countInDeck=5,
            damage=3),
        Card(
            name='Подготовленный фишинг',
            popUpText=get_popup_from_json(data, "Фишинг"),
            popUpURL=get_url_from_json(data, "Фишинг"),
            countInDeck=5,
            damage=5),
        Card(
            name='Целенаправленный фишинг',
            popUpText=get_popup_from_json(data, "Фишинг"),
            popUpURL=get_url_from_json(data, "Фишинг"),
            countInDeck=5,
            damage=7),
        Card(
            name='Прослушка',
            popUpText=get_popup_from_json(data, "Прослушка"),
            popUpURL=get_url_from_json(data, "Прослушка"),
            countInDeck=4,
            damage=4),
        Card(
            name='Перехват пакетов Wi-Fi',
            popUpText=get_popup_from_json(data, "Перехват пакетов Wi-Fi"),
            popUpURL=get_url_from_json(data, "Перехват пакетов Wi-Fi"),
            countInDeck=4,
            damage=4),
        Card(
            name='Выполнение макросов',
            popUpText=get_popup_from_json(data, "Выполнение макросов"),
            popUpURL=get_url_from_json(data, "Выполнение макросов"),
            countInDeck=4,
            damage=4),
        Card(
            name='Ваш пароль взломали перебором',
            popUpText=get_popup_from_json(data, "Ваш пароль взломали перебором"),
            popUpURL=get_url_from_json(data, "Ваш пароль взломали перебором"),
            countInDeck=5,
            damage=4),
        Card(
            name='Устаревшее ПО',
            popUpText=get_popup_from_json(data, "Устаревшее ПО"),
            popUpURL=get_url_from_json(data, "Устаревшее ПО"),
            countInDeck=4,
            damage=4),
        Card(
            name='Вы попали в ботнет',
            popUpText=get_popup_from_json(data, "Вы попали в ботнет"),
            popUpURL=get_url_from_json(data, "Вы попали в ботнет"),
            countInDeck=4,
            damage=5),
    ]

    db.session.add(cardTypeOffence)
    return cardTypeOffence


def create_accident_type(data: list):
    cardTypeAccident = CardType(name='Случайность', color='Blue', enumType=CardTypeEnum.ACCIDENT)

    cardTypeAccident.cards = [Card(
        name='Уязвимости нулевого дня',
        popUpText=get_popup_from_json(data, "Уязвимости нулевого дня"),
        popUpURL=get_url_from_json(data, "Уязвимости нулевого дня"),
        countInDeck=3,
        damage=6),
        Card(
            name='Взлом серверов и утечка паролей',
            popUpText=get_popup_from_json(data, "Взлом серверов и утечка паролей"),
            popUpURL=get_url_from_json(data, "Взлом серверов и утечка паролей"),
            countInDeck=3,
            damage=5),
        Card(
            name='Железные бэкдоры',
            popUpText=get_popup_from_json(data, "Железные бэкдоры"),
            popUpURL=get_url_from_json(data, "Железные бэкдоры"),
            countInDeck=3,
            damage=3),
        Card(
            name='Катаклизмы',
            popUpText=get_popup_from_json(data, "Катаклизмы"),
            popUpURL=get_url_from_json(data, "Катаклизмы"),
            countInDeck=3,
            damage=4),
        Card(
            name='Кража ноутбука',
            popUpText=get_popup_from_json(data, "Кража ноутбука"),
            popUpURL=get_url_from_json(data, "Кража ноутбука"),
            countInDeck=3,
            damage=5),
        Card(
            name='Блокировка доступа к ресурсам',
            popUpText=get_popup_from_json(data, "Блокировка доступа к ресурсам"),
            popUpURL=get_url_from_json(data, "Блокировка доступа к ресурсам"),
            countInDeck=3,
            damage=3),
        Card(
            name='COVID-19',
            popUpText=get_popup_from_json(data, "COVID-19"),
            popUpURL=get_url_from_json(data, "COVID-19"),
            isCovid=True,
            countInDeck=3,
            damage=0),
    ]

    db.session.add(cardTypeAccident)
    return cardTypeAccident


def create_defence_type(data: list):
    cardTypeDefence = CardType(name='Защита', color='Green', enumType=CardTypeEnum.DEFENCE)

    cardTypeDefence.cards = [
        Card(
            name='Антивирус',
            popUpText=get_popup_from_json(data, "Антивирус"),
            popUpURL=get_url_from_json(data, "Антивирус"),
            countInDeck=9,
            damage=None),
        Card(
            name='Двухфакторная аутентификация',
            popUpText=get_popup_from_json(data, "Двухфакторная аутентификация"),
            popUpURL=get_url_from_json(data, "Двухфакторная аутентификация"),
            countInDeck=8,
            damage=None),
        Card(
            name='Сложные пароли',
            popUpText=get_popup_from_json(data, "Сложные пароли"),
            popUpURL=get_url_from_json(data, "Сложные пароли"),
            countInDeck=8,
            damage=None),
        Card(
            name='Полнодисковое шифрование',
            popUpText=get_popup_from_json(data, "Полнодисковое шифрование"),
            popUpURL=get_url_from_json(data, "Полнодисковое шифрование"),
            countInDeck=8,
            damage=None),
        Card(
            name='Использование VPN',
            popUpText=get_popup_from_json(data, "Использование VPN"),
            popUpURL=get_url_from_json(data, "Использование VPN"),
            countInDeck=8,
            damage=None),
        Card(
            name='Регулярные обновления',
            popUpText=get_popup_from_json(data, "Регулярные обновления"),
            popUpURL=get_url_from_json(data, "Регулярные обновления"),
            countInDeck=8,
            damage=None),
        Card(
            name='Лицензионное ПО',
            popUpText=get_popup_from_json(data, "Лицензионное ПО"),
            popUpURL=get_url_from_json(data, "Лицензионное ПО"),
            countInDeck=8,
            damage=None),
        Card(
            name='Надежные мессенджеры',
            popUpText=get_popup_from_json(data, "Надежные мессенджеры"),
            popUpURL=get_url_from_json(data, "Надежные мессенджеры"),
            countInDeck=8,
            damage=None),
        Card(
            name='Пользовательская осторожность',
            popUpText=get_popup_from_json(data, "Пользовательская осторожность"),
            popUpURL=get_url_from_json(data, "Пользовательская осторожность"),
            countInDeck=9,
            damage=None),
        Card(
            name='Использование HTTPS',
            popUpText=get_popup_from_json(data, "Использование HTTPS"),
            popUpURL=get_url_from_json(data, "Использование HTTPS"),
            countInDeck=8,
            damage=None),
        Card(
            name='Регулярные бэкапы',
            popUpText=get_popup_from_json(data, "Регулярные бэкапы"),
            popUpURL=get_url_from_json(data, "Регулярные бэкапы"),
            countInDeck=8,
            damage=None),
        Card(
            name='Цифровая подпись и шифрование писем',
            popUpText=get_popup_from_json(data, "Цифровая подпись и шифрование писем"),
            popUpURL=get_url_from_json(data, "Цифровая подпись и шифрование писем"),
            countInDeck=8,
            damage=None), ]

    db.session.add(cardTypeDefence)
    return cardTypeDefence


def defence(cardTypeDefence, cardTypeOffence, cardTypeAccident):
    defences = {card.name: card for card in cardTypeDefence.cards}
    offences = {card.name: card for card in cardTypeOffence.cards}
    accidents = {card.name: card for card in cardTypeAccident.cards}
    defences['Антивирус'].defensiveFrom = [
        Defence(offence=offences['Шифровальщик'], value=3),
        Defence(offence=offences['Кейлоггер'], value=3),
        Defence(offence=offences['Удаленное выполнение кода'], value=2),
        Defence(offence=offences['Выполнение макросов'], value=2),
        Defence(offence=offences['Вы попали в ботнет'], value=2),
        Defence(offence=offences['Посредственный фишинг'], value=1),
        Defence(offence=offences['Подготовленный фишинг'], value=1),
        Defence(offence=offences['Целенаправленный фишинг'], value=1),
    ]
    defences['Двухфакторная аутентификация'].defensiveFrom = [
        Defence(offence=offences['Посредственный фишинг'], value=3),
        Defence(offence=offences['Подготовленный фишинг'], value=3),
        Defence(offence=offences['Целенаправленный фишинг'], value=3),
        Defence(offence=offences['Ваш пароль взломали перебором'], value=2),
        Defence(offence=accidents['Взлом серверов и утечка паролей'], value=2),
        Defence(offence=accidents['Кража ноутбука'], value=2),
    ]
    defences['Сложные пароли'].defensiveFrom = [
        Defence(offence=offences['Ваш пароль взломали перебором'], value=3),
    ]
    defences['Полнодисковое шифрование'].defensiveFrom = [
        Defence(offence=accidents['Кража ноутбука'], value=2),
    ]
    defences['Использование VPN'].defensiveFrom = [
        Defence(offence=offences['Перехват пакетов Wi-Fi'], value=3),
        Defence(offence=accidents['Блокировка доступа к ресурсам'], value=2),
    ]
    defences['Регулярные обновления'].defensiveFrom = [
        Defence(offence=offences['Устаревшее ПО'], value=3),
        Defence(offence=offences['Удаленное выполнение кода'], value=2),
        Defence(offence=offences['Шифровальщик'], value=1),
        Defence(offence=accidents['Уязвимости нулевого дня'], value=2),
    ]
    defences['Лицензионное ПО'].defensiveFrom = [
        Defence(offence=offences['Шифровальщик'], value=2),
        Defence(offence=offences['Кейлоггер'], value=2),
        Defence(offence=offences['Удаленное выполнение кода'], value=2),
        Defence(offence=offences['Вы попали в ботнет'], value=2),
        Defence(offence=offences['Устаревшее ПО'], value=1),
    ]
    defences['Надежные мессенджеры'].defensiveFrom = [
        Defence(offence=offences['Прослушка'], value=3),
        Defence(offence=offences['Перехват пакетов Wi-Fi'], value=2),
        Defence(offence=accidents['Блокировка доступа к ресурсам'], value=1),
    ]
    defences['Пользовательская осторожность'].defensiveFrom = [
        Defence(offence=offences['Посредственный фишинг'], value=3),
        Defence(offence=offences['Подготовленный фишинг'], value=3),
        Defence(offence=offences['Целенаправленный фишинг'], value=3),
        Defence(offence=offences['Шифровальщик'], value=2),
        Defence(offence=offences['Кейлоггер'], value=2),
        Defence(offence=offences['Выполнение макросов'], value=2),
        Defence(offence=accidents['Взлом серверов и утечка паролей'], value=1),
    ]
    defences['Использование HTTPS'].defensiveFrom = [
        Defence(offence=offences['Прослушка'], value=2),
        Defence(offence=offences['Перехват пакетов Wi-Fi'], value=3),
    ]
    defences['Регулярные бэкапы'].defensiveFrom = [
        Defence(offence=offences['Устаревшее ПО'], value=2),
        Defence(offence=offences['Шифровальщик'], value=4),
        Defence(offence=accidents['Кража ноутбука'], value=3),
        Defence(offence=accidents['Уязвимости нулевого дня'], value=1),
        Defence(offence=accidents['Катаклизмы'], value=1),
    ]
    defences['Цифровая подпись и шифрование писем'].defensiveFrom = [
        Defence(offence=offences['Посредственный фишинг'], value=2),
        Defence(offence=offences['Подготовленный фишинг'], value=2),
        Defence(offence=offences['Целенаправленный фишинг'], value=2),
        Defence(offence=offences['Прослушка'], value=2),
        Defence(offence=accidents['Кража ноутбука'], value=1),
    ]


@manager.command
def fill():
    with open('descriptions.json') as f:
        data = json.load(f)
    defenceCards = create_defence_type(data)
    offenceCards = create_offence_type(data)
    accidentCards = create_accident_type(data)
    defence(defenceCards, offenceCards, accidentCards)
    db.session.commit()
    print("DB data initialized")


if __name__ == '__main__':
    manager.run()
