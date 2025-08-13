import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime
import json
import os

# Токен бота
BOT_TOKEN = "MTQwNTE3NjMwNTI2MzA1MDgzNA.GS_FeX.XU-H8sP7sU8GPkYfpIG3HstcHUv4t-XVj8n2ng"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Система уровней (простая)
user_data = {}

def load_user_data():
    global user_data
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r', encoding='utf-8') as f:
            user_data = json.load(f)

def save_user_data():
    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def add_experience(user_id, exp=1):
    user_id = str(user_id)
    if user_id not in user_data:
        user_data[user_id] = {'level': 1, 'exp': 0}
    
    user_data[user_id]['exp'] += exp
    
    # Проверка на повышение уровня (каждый уровень требует больше опыта)
    required_exp = user_data[user_id]['level'] * 50  # 50, 100, 150, 200...
    if user_data[user_id]['exp'] >= required_exp:
        user_data[user_id]['level'] += 1
        user_data[user_id]['exp'] = 0
        save_user_data()
        return True
    save_user_data()
    return False

@bot.event
async def on_ready():
    print(f'🤖 Tenna Knight запущен и готов к работе!')
    print(f'🆔 ID бота: {bot.user.id}')
    load_user_data()
    
    # Устанавливаем статус бота
    await bot.change_presence(
        activity=discord.Game(name="!помощь для команд"),
        status=discord.Status.online
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Добавляем опыт за сообщения
    level_up = add_experience(message.author.id)
    if level_up:
        level = user_data[str(message.author.id)]['level']
        
        # Красивое embed-сообщение о повышении уровня
        embed = discord.Embed(
            title='🎉 Поздравляю!',
            description=f'**{message.author.display_name}** достиг **{level} уровня**!',
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
        embed.add_field(name='Новый уровень', value=f'`{level}`', inline=True)
        embed.add_field(name='Следующий уровень', value=f'Нужно `{level * 100}` опыта', inline=True)
        embed.set_footer(text='Продолжай общаться, чтобы получать больше опыта!')
        
        await message.channel.send(embed=embed)
    
    await bot.process_commands(message)

# Основные команды
@bot.command(name='привет', aliases=['hello', 'hi'])
async def greet(ctx):
    greetings = [
        f'Привет, {ctx.author.mention}! 👋',
        f'Здравствуй, {ctx.author.name}! 😊',
        f'Хей, {ctx.author.mention}! Как дела? 🤗',
        f'Салют, {ctx.author.name}! ✨'
    ]
    await ctx.send(random.choice(greetings))

@bot.command(name='профиль', aliases=['profile', 'уровень'])
async def profile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in user_data:
        user_data[user_id] = {'level': 1, 'exp': 0}
        save_user_data()
    
    current_level = user_data[user_id]['level']
    current_exp = user_data[user_id]['exp']
    required_exp = current_level * 50
    
    embed = discord.Embed(
        title=f'📊 Профиль {member.display_name}',
        color=discord.Color.blue()
    )
    embed.add_field(name='Уровень', value=current_level, inline=True)
    embed.add_field(name='Опыт', value=f"{current_exp}/{required_exp}", inline=True)
    embed.add_field(name='Прогресс', value=f'{round((current_exp/required_exp)*100, 1)}%', inline=True)
    embed.add_field(name='Дата регистрации', value=member.created_at.strftime('%d.%m.%Y'), inline=False)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='кубик', aliases=['dice', 'roll'])
async def roll_dice(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send('❌ Кубик должен иметь минимум 2 стороны!')
        return
    if sides > 100:
        await ctx.send('❌ Максимум 100 сторон!')
        return
    
    result = random.randint(1, sides)
    await ctx.send(f'🎲 {ctx.author.mention} бросил кубик D{sides} и выпало: **{result}**')

@bot.command(name='монетка', aliases=['coin', 'flip'])
async def flip_coin(ctx):
    result = random.choice(['Орёл', 'Решка'])
    emoji = '🦅' if result == 'Орёл' else '🪙'
    await ctx.send(f'{emoji} Выпало: **{result}**')

@bot.command(name='выбор', aliases=['choose'])
async def choose(ctx, *, options):
    choices = [choice.strip() for choice in options.split(',')]
    if len(choices) < 2:
        await ctx.send('❌ Нужно минимум 2 варианта, разделённых запятыми!')
        return
    
    chosen = random.choice(choices)
    await ctx.send(f'🤔 Я выбираю: **{chosen}**')

@bot.command(name='инфо', aliases=['info', 'about'])
async def bot_info(ctx):
    embed = discord.Embed(
        title='ℹ️ Информация о Tenna Knight',
        description='Многофункциональный бот для Discord сервера!',
        color=discord.Color.green()
    )
    embed.add_field(name='Версия Python', value='3.8+', inline=True)
    embed.add_field(name='Библиотека', value='discord.py', inline=True)
    embed.add_field(name='Серверов', value=len(bot.guilds), inline=True)
    embed.add_field(name='Пользователей', value=len(bot.users), inline=True)
    embed.set_footer(text=f'Запрошено {ctx.author.name}', icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='сервер', aliases=['server'])
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f'📋 Информация о сервере: {guild.name}',
        color=discord.Color.purple()
    )
    embed.add_field(name='Участников', value=guild.member_count, inline=True)
    embed.add_field(name='Каналов', value=len(guild.channels), inline=True)
    embed.add_field(name='Ролей', value=len(guild.roles), inline=True)
    embed.add_field(name='Создан', value=guild.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name='Владелец', value=guild.owner.mention if guild.owner else 'Неизвестно', inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    await ctx.send(embed=embed)

@bot.command(name='время', aliases=['time'])
async def current_time(ctx):
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S %d.%m.%Y')
    await ctx.send(f'🕒 Текущее время: **{time_str}**')

@bot.command(name='очистить', aliases=['clear', 'purge'])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 5):
    if amount > 100:
        await ctx.send('❌ Максимум 100 сообщений за раз!')
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f'🗑️ Удалено {len(deleted) - 1} сообщений')
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name='помощь', aliases=['help', 'commands'])
async def help_command(ctx):
    embed = discord.Embed(
        title='📚 Команды Tenna Knight',
        description='Все доступные команды бота:',
        color=discord.Color.gold()
    )
    
    commands_list = {
        '**Основные:**': [
            '`!привет` - Поприветствовать бота',
            '`!профиль` - Показать свой профиль',
            '`!инфо` - Информация о боте',
            '`!сервер` - Информация о сервере',
            '`!время` - Текущее время'
        ],
        '**Развлечения:**': [
            '`!кубик [стороны]` - Бросить кубик',
            '`!монетка` - Подбросить монетку',
            '`!выбор вариант1, вариант2, ...` - Случайный выбор'
        ],
        '**Модерация:**': [
            '`!очистить [количество]` - Очистить сообщения (нужны права)'
        ]
    }
    
    for category, cmds in commands_list.items():
        embed.add_field(
            name=category,
            value='\n'.join(cmds),
            inline=False
        )
    
    embed.set_footer(text='Используй !команда для выполнения')
    await ctx.send(embed=embed)

# Обработка ошибок
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('❌ Команда не найдена! Используй `!помощь` для списка команд.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('❌ У тебя нет прав для использования этой команды!')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('❌ Неверный аргумент! Проверь правильность команды.')
    else:
        await ctx.send(f'❌ Произошла ошибка: {str(error)}')
        print(f'Ошибка: {error}')

if __name__ == '__main__':
    bot.run(BOT_TOKEN)
