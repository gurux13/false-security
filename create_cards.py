from db_models.cardtype import CardType
from db_models.card import Card
from db_models.defence import Defence
from flask_script import Manager

from app import app, db

manager = Manager(app)


def create_offence_type():
    cardTypeOffence = CardType(name='Нападение', color='Red', isAccident=False)

    cardTypeOffence.cards = [Card(
        name='Шифровальщик', 
        text='', 
        damage=7),
    Card(
        name='Кейлогер', 
        text='', 
        damage=5),
    Card(
        name='MS 17-010', 
        text='', 
        damage=7),
    Card(
        name='Посредственный фишинг', 
        text='', 
        damage=3),
    Card(
        name='Подготовленный фишинг', 
        text='', 
        damage=5),
    Card(
        name='Целенаправленный фишинг', 
        text='', 
        damage=7),
    Card(
        name='Прослушка', 
        text='', 
        damage=4),
    Card(
        name='Перехват пакетов Wi-Fi', 
        text='', 
        damage=4),
    Card(
        name='Выполнение макросов', 
        text='', 
        damage=4),
    Card(
        name='Ваш пароль взломали перебором', 
        text='', 
        damage=4),
    Card(
        name='Устаревшее ПО', 
        text='', 
        damage=4),
    Card(
        name='Вы попали в ботнет', 
        text='', 
        damage=5),
    ]

    db.session.add(cardTypeOffence)
    return cardTypeOffence


def сreate_accident_type():
    cardTypeAccident = CardType(name='Случайность', color='Blue', isAccident=True)

    cardTypeAccident.cards = [Card(
        name='Уязвимости нулевого дня', 
        text='Хакеры уже знают об этой ошибке в ПО, а вот его производители о ней еще не догадываются...', 
        damage=6),
    Card(
        name='Взлом серверов и утечка паролей', 
        text='Увы, не бывает абсолютно надежных сайтов и приложений', 
        damage=5),
    Card(
        name='Железные бэкдоры', 
        text='Никто не может защитить Вас от недобросовестных производителей железа', 
        damage=3),
    Card(
        name='Катаклизмы', 
        text='Пожары, наводнения, короткие замыкания. Чего только не случается в этом мире.', 
        damage=4),
    Card(
        name='Кража ноутбука', 
        text='21 век на дворе. А от краж никуда не деться. Да и кражи бывают разные.', 
        damage=5),
    Card(
        name='Блокировка доступа к ресурсам', 
        text='', 
        damage=3),
    Card(
        name='COVID-19', 
        text='От коронавируса защитить не может ничто. Отдайте половину своих денег соседу', 
        isCovid=True, 
        damage=0),
    ]

    db.session.add(cardTypeAccident)
    return cardTypeAccident


def create_defence_type():
    cardTypeDefence = CardType(name='Защита', color='Green', isAccident=False)

    cardTypeDefence.cards = [Card(
        name='Антивирус', 
        text='', 
        damage=None),
    Card(
        name='Двухфакторная аутентификация', 
        text='', 
        damage=None),
    Card(
        name='Сложные пароли', 
        text='', 
        damage=None),
    Card(
        name='Полнодисковое шифрование', 
        text='', 
        damage=None),
    Card(
        name='Использование VPN', 
        text='', 
        damage=None),
    Card(
        name='Регулярные обновления', 
        text='', 
        damage=None),
    Card(
        name='Лицензионное ПО', 
        text='', 
        damage=None),
    Card(
        name='Надежные мессенджеры', 
        text='', 
        damage=None),
    Card(
        name='Пользовательская осторожность', 
        text='', 
        damage=None),
    Card(
        name='Использование HTTPS', 
        text='', 
        damage=None),
    Card(
        name='Регулярные бэкапы', 
        text='', 
        damage=None),
    Card(
        name='Цифровая подпись и шифрование писем', 
        text='', 
        damage=None),]

    db.session.add(cardTypeDefence)
    return cardTypeDefence

 
def defence(cardTypeDefence, cardTypeOffence, cardTypeAccident):
    defences = {card.name: card for card in cardTypeDefence.cards}
    offences = {card.name: card for card in cardTypeOffence.cards}
    accidents = {card.name: card for card in cardTypeAccident.cards}
    defences['Антивирус'].defensiveFrom = [
        Defence(offence=offences['Шифровальщик'], value=3),
        Defence(offence=offences['Кейлогер'], value=3),
        Defence(offence=offences['MS 17-010'], value=2),
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
        Defence(offence=offences['MS 17-010'], value=2),
        Defence(offence=offences['Шифровальщик'], value=1),
        Defence(offence=accidents['Уязвимости нулевого дня'], value=2),
    ]
    defences['Лицензионное ПО'].defensiveFrom = [
        Defence(offence=offences['Шифровальщик'], value=2),
        Defence(offence=offences['MS 17-010'], value=2),
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
        Defence(offence=offences['Кейлогер'], value=2),
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
    print("I will try to write to db")
    defenceCards = create_defence_type()
    offenceCards = create_offence_type()
    accidentCards = сreate_accident_type()
    defence(defenceCards, offenceCards, accidentCards)
    db.session.commit()


if __name__ == '__main__':
    manager.run()

