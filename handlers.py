import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import config

bot = Bot(token=config. BOT_TOKEN)
dp = Dispatcher()

class CreditForm(StatesGroup):
    summa = State()
    time = State()
    percent = State()

class Deposit(StatesGroup):
    summa = State()
    time = State()
    percent = State()

class Game(StatesGroup):
    summa = State()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(text=f'Привет, {message.from_user.first_name}, вот что я умею:\n /credit - помогу рассчитать твой кредит\n /deposit - рассчитаю твою банковский вклад\n /game - сыграем в игру "52 недели богатства"')

@dp.message(Command('credit'))
async def credit(message: types.Message, state: FSMContext):
    await message.answer(text='На какую сумму планируешь кредит?')
    await state.set_state(CreditForm.summa)

@dp.message(Command('deposit'))
async def deposit(message: types.Message, state: FSMContext):
    await message.answer(text='Какая у тебя сумма вклада?')
    await state.set_state(Deposit.summa)

@dp.message(Command('game'))
async def game(message: types.Message, state: FSMContext):
    await message.answer(text='Какую сумму желаешь накопить за год?')
    await state.set_state(Game.summa)

@dp.message(CreditForm.summa)
async def credit_summa(message: types.Message, state: FSMContext):
    await state.update_data(summa=message.text)
    await message.answer(text = 'На какой срок(в месяцах) планируешь кредит?')
    await state.set_state(CreditForm.time)

@dp.message(CreditForm.time)
async def credit_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer(text = 'Какая будет процентная ставка?')
    await state.set_state(CreditForm.percent)

@dp.message(CreditForm.percent)
async def credit_percent(message: types.Message, state: FSMContext):
    await state.update_data(percent=message.text)
    data_first = await state.get_data()
    summ = float(data_first['summa'])
    srok = float(data_first['time'])
    procent = float(data_first['percent'])/1200.0
    payment = round(summ*((procent*(1.0+procent)**srok)/(((1.0+procent)**srok)-1.0)), 2)
    overpayment = round(payment * srok - summ, 2)
    await message.answer(text = f'Я рассчитал твой кредит.\nСумма ежемесячного платежа: {payment} ₽\nПереплата по процентам за кредит: {overpayment} ₽')
    await state.clear()

@dp.message(Deposit.summa)
async def deposit_summa(message: types.Message, state: FSMContext):
    await state.update_data(summa=message.text)
    await message.answer(text = 'На какой период(в месяцах) планируешь вклад?')
    await state.set_state(Deposit.time)

@dp.message(Deposit.time)
async def deposit_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer(text = 'Какая будет процентная ставка?')
    await state.set_state(Deposit.percent)

@dp.message(Deposit.percent)
async def deposit_percent(message: types.Message, state: FSMContext):
    await state.update_data(percent=message.text)
    data_second = await state.get_data()
    summ = int(data_second['summa'])
    srok = int(data_second['time'])
    procent = float(data_second['percent'])/1200.0
    vklad = summ
    for i in range (0, srok):
        vklad = vklad * (1+procent)
    payment = round(vklad - summ, 2)
    payment_procent = round((payment/summ)*100, 2)
    await message.answer(text = f'Я рассчитал твой вклад с ежемесячной капитализацией.\nНачисленные проценты: {payment} ₽\nПрирост капитала: {payment_procent} %')
    await state.clear()

@dp.message(Game.summa)
async def game_summa(message: types.Message, state: FSMContext):
    await state.update_data(summa=message.text)
    data_third = await state.get_data()
    summ = int(data_third['summa'])
    x = int(summ/1378)
    await message.answer(text = 'Давай сыграем! Каждую неделю ты должен будешь откладывать определенную сумму. Эта сумма будет увеличиваться каждую неделю на ту, которую ты отложил в первую неделю. Денежные средства лучше класть на банковский вклад.')
    await message.answer(text = f'И так, в первую неделю отложи {x} ₽, а в каждую последущую на эту же сумму больше.\nВ четвертую {x*4} ₽\nВ двадцатую {x*20} ₽\nВ последнюю пятдесят вторую неделю {x*52} ₽')
    await message.answer(text = f'Не забывай откладывать и через 52 недели ты сможешь накопить {summ} ₽ !')
    await state.clear()

@dp.message()
async def echo_massage(message: types.Message):
    await  message.reply(text='Лучше воспользуйся одной из команд')
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)