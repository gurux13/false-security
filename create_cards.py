from db_models.cardtype import CardType, CardTypeEnum
from db_models.card import Card
from db_models.defence import Defence
from flask_script import Manager
import json

from globals import app, db

manager = Manager(app)


def get_popup_from_json(data: list, name: str) -> str:
    return [next((i for i in data if i.get("name") == name), None)][0]["popUpText"]


def create_offence_type(data: list):
    cardTypeOffence = CardType(name='Нападение', color='Red', enumType=CardTypeEnum.OFFENCE)

    cardTypeOffence.cards = [Card(
        name='Шифровальщик',
        popUpText=get_popup_from_json(data, "Шифровальщик"),
        countInDeck=3,
        damage=7),
        Card(
            name='Кейлоггер',
            popUpText=get_popup_from_json(data, "Кейлоггер"),
            countInDeck=3,
            damage=5),
        Card(
            name='Удаленное выполнение кода',
            popUpText=get_popup_from_json(data, "Удаленное выполнение кода"),
            countInDeck=3,
            damage=7),
        Card(
            name='Посредственный фишинг',
            popUpText=get_popup_from_json(data, "Фишинг"),
            countInDeck=3,
            damage=3),
        Card(
            name='Подготовленный фишинг',
            popUpText=get_popup_from_json(data, "Фишинг"),
            countInDeck=3,
            damage=5),
        Card(
            name='Целенаправленный фишинг',
            popUpText=get_popup_from_json(data, "Фишинг"),
            countInDeck=3,
            damage=7),
        Card(
            name='Прослушка',
            popUpText=get_popup_from_json(data, "Прослушка"),
            countInDeck=3,
            damage=4),
        Card(
            name='Перехват пакетов Wi-Fi',
            popUpText=get_popup_from_json(data, "Перехват пакетов Wi-Fi"),
            countInDeck=3,
            damage=4),
        Card(
            name='Выполнение макросов',
            popUpText=get_popup_from_json(data, "Выполнение макросов"),
            countInDeck=3,
            damage=4),
        Card(
            name='Ваш пароль взломали перебором',
            popUpText=get_popup_from_json(data, "Ваш пароль взломали перебором"),
            countInDeck=3,
            damage=4),
        Card(
            name='Устаревшее ПО',
            popUpText=get_popup_from_json(data, "Устаревшее ПО"),
            countInDeck=3,
            damage=4),
        Card(
            name='Вы попали в ботнет',
            popUpText=get_popup_from_json(data, "Вы попали в ботнет"),
            countInDeck=3,
            damage=5),
    ]

    db.session.add(cardTypeOffence)
    return cardTypeOffence


def create_accident_type():
    cardTypeAccident = CardType(name='Случайность', color='Blue', enumType=CardTypeEnum.ACCIDENT)

    cardTypeAccident.cards = [Card(
        name='Уязвимости нулевого дня',
        text='Хакеры уже знают об этой ошибке в ПО, а вот его производители о ней еще не догадываются...',
        countInDeck=3,
        damage=6),
        Card(
            name='Взлом серверов и утечка паролей',
            text='Увы, не бывает абсолютно надежных сайтов и приложений',
            countInDeck=3,
            damage=5),
        Card(
            name='Железные бэкдоры',
            text='Никто не может защитить Вас от недобросовестных производителей железа',
            countInDeck=3,
            damage=3),
        Card(
            name='Катаклизмы',
            text='Пожары, наводнения, короткие замыкания. Чего только не случается в этом мире',
            countInDeck=3,
            damage=4),
        Card(
            name='Кража ноутбука',
            text='21 век на дворе. А от краж никуда не деться. Да и кражи бывают разные',
            countInDeck=3,
            damage=5),
        Card(
            name='Блокировка доступа к ресурсам',
            text='',
            countInDeck=3,
            damage=3),
        Card(
            name='COVID-19',
            text='От коронавируса защитить не может ничто. Отдайте половину своих денег соседу',
            isCovid=True,
            countInDeck=3,
            damage=0),
    ]

    db.session.add(cardTypeAccident)
    return cardTypeAccident


def create_defence_type():
    cardTypeDefence = CardType(name='Защита', color='Green', enumType=CardTypeEnum.DEFENCE)

    cardTypeDefence.cards = [
        Card(
            name='Антивирус',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Двухфакторная аутентификация',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Сложные пароли',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Полнодисковое шифрование',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Использование VPN',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Регулярные обновления',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Лицензионное ПО',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Надежные мессенджеры',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Пользовательская осторожность',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Использование HTTPS',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Регулярные бэкапы',
            text='',
            countInDeck=3,
            damage=None),
        Card(
            name='Цифровая подпись и шифрование писем',
            text='',
            countInDeck=3,
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
    defenceCards = create_defence_type()
    offenceCards = create_offence_type(data)
    accidentCards = create_accident_type()
    defence(defenceCards, offenceCards, accidentCards)
    db.session.commit()
    print("DB data initialized")


if __name__ == '__main__':
    manager.run()
