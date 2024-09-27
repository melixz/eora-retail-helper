import random

# Список ссылок
URLS_TO_PARSE = [
    "https://eora.ru/cases/promyshlennaya-bezopasnost",
    "https://eora.ru/cases/lamoda-systema-segmentacii-i-poiska-po-pohozhey-odezhde",
    "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/karas-golosovoy-assistent",
    "https://eora.ru/cases/assistenty-dlya-gorodov",
    "https://eora.ru/cases/avtomatizaciya-v-promyshlennosti/chemrar-raspoznovanie-molekul",
    "https://eora.ru/cases/zeptolab-skazki-pro-amnyama-dlya-sberbox",
    "https://eora.ru/cases/goosegaming-algoritm-dlya-ocenki-igrokov",
    "https://eora.ru/cases/dodo-pizza-robot-analitik-otzyvov",
    "https://eora.ru/cases/ifarm-nejroset-dlya-ferm",
    "https://eora.ru/cases/zhivibezstraha-navyk-dlya-proverki-rodinok",
    "https://eora.ru/cases/sportrecs-nejroset-operator-sportivnyh-translyacij",
    "https://eora.ru/cases/avon-chat-bot-dlya-zhenshchin",
    "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/navyk-dlya-proverki-loterejnyh-biletov",
    "https://eora.ru/cases/computer-vision/iss-analiz-foto-avtomobilej",
    "https://eora.ru/cases/purina-master-bot",
    "https://eora.ru/cases/skinclub-algoritm-dlya-ocenki-veroyatnostej",
    "https://eora.ru/cases/skolkovo-chat-bot-dlya-startapov-i-investorov",
    "https://eora.ru/cases/purina-podbor-korma-dlya-sobaki",
    "https://eora.ru/cases/purina-navyk-viktorina",
    "https://eora.ru/cases/dodo-pizza-pilot-po-avtomatizacii-kontakt-centra",
    "https://eora.ru/cases/dodo-pizza-avtomatizaciya-kontakt-centra",
    "https://eora.ru/cases/icl-bot-sufler-dlya-kontakt-centra",
    "https://eora.ru/cases/s7-navyk-dlya-podbora-aviabiletov",
    "https://eora.ru/cases/workeat-whatsapp-bot",
    "https://eora.ru/cases/absolyut-strahovanie-navyk-dlya-raschyota-strahovki",
    "https://eora.ru/cases/kazanexpress-poisk-tovarov-po-foto",
    "https://eora.ru/cases/kazanexpress-sistema-rekomendacij-na-sajte",
    "https://eora.ru/cases/intels-proverka-logotipa-na-plagiat",
    "https://eora.ru/cases/karcher-viktorina-s-voprosami-pro-uborku",
    "https://eora.ru/cases/chat-boty/purina-friskies-chat-bot-na-sajte",
    "https://eora.ru/cases/nejroset-segmentaciya-video",
    "https://eora.ru/cases/chat-boty/essa-nejroset-dlya-generacii-rolikov",
    "https://eora.ru/cases/qiwi-poisk-anomalij",
    "https://eora.ru/cases/frisbi-nejroset-dlya-raspoznavaniya-pokazanij-schetchikov",
    "https://eora.ru/cases/skazki-dlya-gugl-assistenta",
    "https://eora.ru/cases/chat-boty/hr-bot-dlya-magnit-kotoriy-priglashaet-na-sobesedovanie"
]

# Категории ссылок
CATEGORIES = {
    "чат-боты": {
        "urls": [
            "https://eora.ru/cases/avon-chat-bot-dlya-zhenshchin",
            "https://eora.ru/cases/chat-boty/hr-bot-dlya-magnit-kotoriy-priglashaet-na-sobesedovanie",
            "https://eora.ru/cases/chat-boty/purina-friskies-chat-bot-na-sajte",
            "https://eora.ru/cases/workeat-whatsapp-bot",
            "https://eora.ru/cases/skolkovo-chat-bot-dlya-startapov-i-investorov"
        ],
        "keywords": ["чат-бот", "бот", "общение", "клиенты", "покупатели", "запрос"],
        "description": "разработку чат-ботов для различных целей"
    },
    "анализ данных": {
        "urls": [
            "https://eora.ru/cases/qiwi-poisk-anomalij",
            "https://eora.ru/cases/skinclub-algoritm-dlya-ocenki-veroyatnostej",
            "https://eora.ru/cases/dodo-pizza-robot-analitik-otzyvov",
            "https://eora.ru/cases/purina-master-bot"
        ],
        "keywords": ["анализ", "данные", "прогнозирование", "статистика", "метрика"],
        "description": "анализ данных и прогнозирование"
    },
    "управление запасами": {
        "urls": [
            "https://eora.ru/cases/ifarm-nejroset-dlya-ferm",
            "https://eora.ru/cases/assistenty-dlya-gorodov",
            "https://eora.ru/cases/lamoda-systema-segmentacii-i-poiska-po-pohozhey-odezhde",
            "https://eora.ru/cases/promyshlennaya-bezopasnost",
            "https://eora.ru/cases/kazanexpress-poisk-tovarov-po-foto"
        ],
        "keywords": ["управление", "запасы", "товары", "склад", "логистика", "цепочки"],
        "description": "управление запасами и логистикой"
    },
    "компьютерное зрение/нейросети": {
        "urls": [
            "https://eora.ru/cases/computer-vision/iss-analiz-foto-avtomobilej",
            "https://eora.ru/cases/nejroset-segmentaciya-video",
            "https://eora.ru/cases/frisbi-nejroset-dlya-raspoznavaniya-pokazanij-schetchikov",
            "https://eora.ru/cases/zeptolab-skazki-pro-amnyama-dlya-sberbox"
        ],
        "keywords": ["компьютерное зрение", "нейросеть", "распознавание", "фото", "анализ изображений"],
        "description": "компьютерное зрение и нейросети для распознавания изображений"
    }
}


def get_random_services():
    """
    Возвращает случайное описание услуги и URL из списка категорий.
    """
    category, data = random.choice(list(CATEGORIES.items()))
    random_url = random.choice(data['urls'])
    return data['description'], random_url
