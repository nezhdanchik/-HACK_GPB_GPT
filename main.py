import asyncio
import logging

# ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11 ВЕРСИЯ PYTHON 3.11
from collections import Counter


from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from Course import SalesGPT, llm, my_variants

bot_token = '7002087061:AAErik31z_euzihvi1ewfCZsfK8rDIuQN50'

sales_agent = None

count_messages = 0

courses_names = ['Финансовый анализ', 'МСФО для банковских аналитиков', 'Кредитный анализ',
                 'Машинное обучение – продвинутый курс', 'Python-программирование – продвинутый курс',
                 'Frontend-разработка для продвинутых',
                 'Инвестиционный анализ', 'Финансовое моделирование инвестиционных проектов',
                 'Построение финансовых моделей', 'Продакт-менеджмент', 'Копирайтинг от А до Я',
                 'Интернет-маркетолог с нуля', 'Введение в SQL', 'Современные технологии фронтенд-разработки',
                 'Python для начинающих', 'Машинное обучение', 'Python-программирование', 'Frontend-разработка',
                 ]

courses_names = list(map(lambda x: x.lower(), courses_names))

def find_most_common(lst: list, r: int) -> str:
    r = min(r, len(set(lst)))
    return ', '.join(['"'+i[0]+'"' for i in Counter(lst).most_common(r)])

async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    bot = Bot(bot_token, parse_mode=None)
    logging.basicConfig(level=logging.INFO)

    @dp.channel_post(Command(commands=["start"]))
    async def repl(message):
        global sales_agent
        global count_messages
        count_messages = 0
        sales_agent = SalesGPT.from_llm(llm, verbose=False)
        sales_agent.seed_agent()
        ai_message = sales_agent.ai_step()
        await message.answer(ai_message)

    @dp.channel_post(F.text)
    async def repl(message):
        global count_messages
        global sales_agent
        if sales_agent is None:
            await message.answer('Используйте команду /start')
        else:
            human_message = message.text
            if human_message:
                for course in courses_names:
                    if course in human_message.lower():
                        await message.answer((f'[{course}]'))
                        sales_agent = None
                        break
                count_messages += 1
                if count_messages >= 5 and len(my_variants) > 0:
                    r = min(2, len(my_variants))
                    print(Counter(my_variants))
                    s = 'Предлагаю вам несколько курсов на выбор. Какой вы предпочитаете? Укажите его название.'
                    s += find_most_common(my_variants, r)
                    await message.answer(s)
                if count_messages >= 7 and len(my_variants) > 0 and sales_agent is not None:
                    print(f'[{Counter(my_variants).most_common(1)[0][0]}]')
                    await message.answer(f'[{Counter(my_variants).most_common(1)[0][0]}]')
                    sales_agent = None
                human_message = human_message.replace('курс', 'курс Газпрома')
                sales_agent.human_step(human_message)
            if sales_agent is not None:
                ai_message = sales_agent.ai_step()
                sales_agent.analyse_stage()

                sales_agent.analyse()

                await message.answer(ai_message)

    @dp.message(~F.text)
    async def empty(message):
        await message.answer('Бот принимает только текст')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=['channel_post'])


if __name__ == "__main__":
    asyncio.run(main())
