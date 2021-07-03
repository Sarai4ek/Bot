import asyncio
import sqlite3
import config
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import re

bot = Bot( command_prefix = '.')
base = sqlite3.connect('ЧС.db')  #Создание базы данных
cur = base.cursor()
base.execute('CREATE TABLE IF NOT EXISTS data(name TEXT PRIMARY KEY, id INT)') #Создание таблицы базы данных, если ее нет
base.commit()
i = 0 

#ЧС команда
@bot.command()
@commands.has_permissions(manage_messages=True) #Права доступа
async def чс(ctx, arg=None, arg2=None, arg3=None):
    author = ctx.message.author
    if arg == None:     #Вывод дступных команд
        embed = discord.Embed(color = 0x000000, description =f'Доступные команды:\n .чс добавить *NICK* *ID*\n .чс убрать *NICK*\n .чс поиск *NICK*')
        await ctx.send(embed=embed)
    elif arg == 'добавить': #Команда для добавления в ЧС
        try:
            cur.execute('INSERT INTO data VALUES(?,?)', (arg2, arg3))
            base.commit()
            await ctx.send(f'{author.mention} Данный ник успешно добавлен в черный список')

        except:
            await ctx.send(f'{author.mention} Данный ник или ID уже есть в черном списке')

    elif arg == 'убрать': #Команда удаления из ЧС
        cur.execute('DELETE FROM data WHERE name == ?', (arg2,))
        base.commit()
        await ctx.send(f'{author.mention} Данный ник был удален из черного списока')

    elif arg == 'поиск': #Проверка наличия игрока в ЧС
        c = base.cursor()
        BL = c.execute('SELECT * FROM data').fetchall()
        Flag = True
        for s in BL:
            if re.search('{}'.format(arg2), str(s)):
                embed = discord.Embed(title = 'Черный список: ',color = 0x000000, description ='Найдено совпадение')
                embed.add_field(name='Имя:', value=s[0])
                embed.add_field(name='ID', value=s[1])
                await ctx.send(embed=embed)
                Flag = False
        if Flag == True:
            await ctx.send(f'{author.mention} Совпадений не было найдено')

    elif arg == 'список': #Вывод списка игроков в ЧС
        global embedBLACK
        embedBLACK = discord.Embed(color = 0x000000, description ='Черный список:')
        c1 = base.cursor()   #Создание новой переменной для обращения к базе данных чтобы при повторном написании обновлялся список, если был ранее обновлен
        BL = c1.execute('SELECT * FROM data').fetchall()
        number = 0
        for r in s:
            number += 1
            embedBLACK.add_field(name='№', value=f'{number}')
            embedBLACK.add_field(name='Имя:', value=r[0])
            embedBLACK.add_field(name='ID', value=r[1])

        #Передача из локатьной переменной в глобальную для работы add_reaction
        #Публикация embed
        #Добавление эмодзи к embed black list
        global blackLIST
        blackLIST = await ctx.send(embed=embedBLACK)
        left = await blackLIST.add_reaction('⬅️')
        right = await blackLIST.add_reaction('➡️')


#Проверка наличия кликов на эмодзи
@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    mess = blackLIST.id           #Передача переменной c id сообщения о embed ЧС из другой функции
    print('start')

    if not payload.member.bot:        #Проверка что эмодзи добавил не бот
        if payload.message_id == mess:     #Проверка что эмодзи было нажато на сообщении с embed ЧС списком
            print('Тот id')

            if payload.emoji.name == '⬅️':              #Если нажато левая стрелка
                print('Нажатие левой стрелки', i)

                lft = i - 8
                print(lft)
                row = cur.execute('SELECT * FROM data LIMIT {}, 8'.format(lft)).fetchall()
                edition = discord.Embed(color = 0x000000, description ='Черный список: \n')

                #Удаление строк embed для редакции сообщения с ЧС списком
                edition.clear_fields()
                embedBLACK.clear_fields()

                number = 0
                for r in row:
                    number += 1
                    edition.add_field(name='№', value=f'{number}')
                    edition.add_field(name='Имя:', value=r[0])
                    edition.add_field(name='ID', value=r[1])

                await blackLIST.edit(embed=edition)
                await message.remove_reaction(str(payload.emoji), payload.member) #Не проверял работоспособность

            if payload.emoji.name == '➡️':       #Если нажато правая стрелка
                print('Нажатие правой стрелки', i)

                rgt = i + 8
                print(rgt)
                row = cur.execute('SELECT * FROM data LIMIT {}, 8'.format(rgt)).fetchall()
                edition = discord.Embed(color = 0x000000, description ='Черный список: \n')

                #Удаление строк embed для редакции сообщения с ЧС списком
                edition.clear_fields()
                embedBLACK.clear_fields()

                number = 0
                for r in row:
                    number += 1
                    edition.add_field(name='№', value=f'{number}')
                    edition.add_field(name='Имя:', value=r[0])
                    edition.add_field(name='ID', value=r[1])

                await blackLIST.edit(embed=edition)

                await message.remove_reaction(str(payload.emoji), payload.member) #Не проверял работоспособность



bot.run(config.TOKEN)