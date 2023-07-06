import threading
from threading import Thread
import atexit
import os
import discord
import requests
import base64
import urllib.request
from PIL import Image
import openai
import asyncio
from discord import ui

from pymongo import MongoClient
from discord import DMChannel, TextChannel
from time import sleep

openai.api_key = "OPEN_AI_KEY"

#start_sequence = "\nAnamika:"
#restart_sequence = "\n\nFriend:"
status = 0

#logs = {'Farziverse#829 + 8394030202': ['hello there', 1, 'a']}

client2 = MongoClient(
  "YOUR MONGO_DB"
)

db = client2['Botdata_v1']
data = db.data
logs = db.logs

#changes add server
#client = discord.Client(intents=intents)
#async def send_welcome_message_to_all_servers():
#for guild in client.guilds:
# Send the welcome message to the default channel of the server
#default_channel = guild.system_channel
#await default_channel.send("Thank you for adding me to your server! I am here to help.")


def search_images(query):

  API_KEY = os.environ['API_KEY']
  CSE_ID = os.environ['CSE_ID']

  query = query.replace(' ', '+')
  search_url = "https://www.googleapis.com/customsearch/v1?key=" + API_KEY + "&cx=" + CSE_ID + "&q=" + query + "&searchType=image&fileType=jpg%7Cjpeg%7Cpng&excludeTerms=site:prnewswire.com"
  response = requests.get(search_url)
  results = response.json()
  #print(results)
  if 'items' in results:
    #print("Hey")
    first_image = results['items'][0]
    image_url = first_image['link']
    #print(image_url)
    return image_url


def run_bot(bot_id, session_prompt, bot_token):

  client = discord.Client(intents=discord.Intents.all())
  #print(bot_id)

  # Register an event handler for the message event
  @client.event
  async def on_message(message):
    #async with message.channel.typing():
    #await asyncio.sleep(0.5)
    #jhanda = 0

    start_sequence = "\nAnamika"
    restart_sequence = f'\n\n{str(message.author)[:-5]}'
    global status
    #global logs

    if message.author == client.user:
      return

    if message.author.bot and message.content != "bracad1":
      return

    if message.content == "I am resetted. Lets goo!": return

    jassie = data.find_one({'bot_unique': str(bot_id + 1)})
    #print(jassie)
    #jassie['Flag'] = [12, 1]
    #print(jassie)
    #print(jassie['name'])

    if jassie['Flag'][0] == 1:
      lin2 = jassie['url']
      nam2 = jassie['Name']

      urllib.request.urlretrieve(lin2, nam2)

      img = Image.open(nam2, 'r')
      with open(nam2, 'rb') as f:
        picture = f.read()
      data.update_one({'bot_unique': str(bot_id + 1)}, {"$set": jassie})

      #print("Image change")
      jassie['Flag'][0] = 0
      #await client.user.edit(username=jassie['Name'], avatar=picture)
      try:
        await client.user.edit(username=jassie['Name'], avatar=picture)
      except discord.errors.HTTPException:
        await client.user.edit(username="ChangeMyName", avatar=picture)
      #print("name change")
      jassie['Flag'][0] = 0
      data.update_one({'bot_unique': str(bot_id + 1)}, {"$set": jassie})

    if jassie['Flag'][1] == 1:
      try:
        await client.user.edit(username=jassie['Name'], avatar=picture)
      except discord.errors.HTTPException:
        await client.user.edit(username="ChangeMyName", avatar=picture)
      #print("name change")
      #await client.user.edit(username=jassie['Name'])
      jassie['Flag'][1] = 0
      data.update_one({'bot_unique': str(bot_id + 1)}, {"$set": jassie})

    if isinstance(message.channel, DMChannel):
      #await message.channel.typing()
      unique_id = str(message.author) + ' + ' + jassie['Bot_Tokens']

    elif isinstance(message.channel, TextChannel):
      # Get the name of the channel
      channel_name = message.channel.name
      unique_id = str(channel_name) + ' + ' + jassie['Bot_Tokens']
      user_id = str(message.author) + ' + ' + jassie['Bot_Tokens']

    if isinstance(message.channel, TextChannel):
      if logs.find_one({'unique_id': user_id}) == None:
        logs.insert_one({'unique_id': user_id, 'logs': [' ', 0, '', 0, 0]})

    #if unique_id not in logs.keys():
    if logs.find_one({'unique_id': unique_id}) == None:
      lin = jassie['url']
      nam = jassie['Name']
      #jassie['flag'] = [0, 0]
      #lin = search_images(jassie['name'])
      #print(jassie['Name'])
      if 'amazon' in jassie['url']: lin = jassie['url']
      #else: lin = search_images(nam)
      if lin == None:
        lin = "https://i.postimg.cc/Jzs0mRKr/naruto.jpg"
        nam = nam + ".jpg"
      #print(lin)
      if lin[-4:] == ".jpg": nam = nam + ".jpg"
      elif lin[-4:] == ".png": nam = nam + ".png"
      elif lin[-5:] == ".jpeg": nam = nam + ".jpeg"

      try:
        urllib.request.urlretrieve(lin, nam)
      except:
        #print("check")
        img = Image.open(nam, 'r')
      img = Image.open(nam, 'r')
      #img = img.save(nam)

      with open(nam, 'rb') as f:
        picture = f.read()
      if len(jassie['Name']) > 32:
        await client.user.edit(username=jassie['Name'][:30], avatar=picture)
      else:
        try:
          await client.user.edit(username=jassie['Name'], avatar=picture)
        except discord.errors.HTTPException:
          await client.user.edit(username="ChangeMyName", avatar=picture)
      #logs[unique_id] = [' ', 0, ' ']
      if isinstance(message.channel, TextChannel):
        logs.insert_one({
          'unique_id': unique_id,
          'logs': ['', 0, '', 0, 0],
          'flag': 0
        })
      else:
        logs.insert_one({'unique_id': unique_id, 'logs': ['', 0, '', 0, 0]})
#logs.insert_one({'unique_id': unique_id,'final_prompt': promper,'story':story,'secondaries':secondaries, })
    if message.content == "bracad1": return

    prompt = jassie['Prompt']
    creep = logs.find_one({'unique_id': unique_id})

    if isinstance(message.channel, TextChannel):
      if message.content == "activate" or message.content == "Activate":
        await message.channel.send("Activatantodo hoomans!")
        creep['flag'] = 1
        logs.update_one({'unique_id': unique_id}, {"$set": creep})
      if message.content == "deactivate" or message.content == "Deactivate":
        await message.channel.send("bieee me gng Deactive")
        creep['flag'] = 0
        logs.update_one({'unique_id': unique_id}, {"$set": creep})
      if creep['flag'] == 0:
        return

    try:
      await message.channel.typing()
    except discord.errors.Forbidden:
      #print("baba re baba")
      return

    if isinstance(message.channel, TextChannel):
      user = logs.find_one({'unique_id': user_id})
      user['logs'][1] += 1
      #user['logs'][3] += 1

    if message.content == "iWack" or message.content == "iwack":
      creep['logs'] = ['', 0, '', 0, 0]
      logs.update_one({'unique_id': unique_id}, {"$set": creep})
      if isinstance(message.channel, TextChannel):
        user['logs'] = ['', 0, '', 0, 0]
        logs.update_one({'unique_id': user_id}, {"$set": user})
      await message.channel.send("I am Reset!, who are you?")
      return

    if creep['logs'][3] >= 2 or creep['logs'][4] == 1:
      #user['logs'][3] = 0
      #print("message overload")
      creep['logs'][3] = 0
      logs.update_one({'unique_id': unique_id}, {"$set": creep})
      if isinstance(message.channel, TextChannel):
        logs.update_one({'unique_id': user_id}, {"$set": user})
      return

    #logs[unique_id][1] += 1
    creep['logs'][1] += 1
    creep['logs'][3] += 1
    if creep['logs'][3] == 2:
      #print("Blocking other messages")
      creep['logs'][4] = 1
      logs.update_one({'unique_id': unique_id}, {"$set": creep})

    response = openai.Completion.create(
      engine="text-davinci-003",
      #prompt=f'{chat_log}{restart_sequence}{message.content}',
      prompt=f"{prompt}{creep['logs'][0]}{restart_sequence}{message.content}\n",
      max_tokens=1000,
      n=1,
      top_p=1,
      temperature=0.75,
      frequency_penalty=2,
      presence_penalty=2)

    win = jassie['Name']
    if str(jassie["Name"]) in str(response["choices"][0]["text"]):
      creep['logs'][
        0] += f'\n{str(message.author)[:-5]}:{message.content}\n{response["choices"][0]["text"]}'
    else:
      creep['logs'][
        0] += f'\n{str(message.author)[:-5]}:{message.content}\n{str(jassie["Name"])}:{response["choices"][0]["text"]}'

    if creep['logs'][1] <= 30 and creep['logs'][1] >= 5:
      creep['logs'][2] = creep['logs'][0]
    if creep['logs'][1] > 30:
      #print(f'updating creep log: {creep["logs"][1]}')
      creep['logs'][0] = creep['logs'][2]
      creep['logs'][1] = 1

    if isinstance(message.channel, TextChannel):
      user['logs'][
        0] += f'\n{str(message.author)[:-5]}:{message.content}\n{response["choices"][0]["text"]}'

      if user['logs'][1] <= 30 and user['logs'][1] >= 5:
        user['logs'][2] = user['logs'][0]
      if creep['logs'][1] > 30:
        print(f'updating user log: {user["logs"][1]}')
        user['logs'][0] = user['logs'][2]
        user['logs'][1] = 1

      logs.update_one({'unique_id': user_id}, {"$set": user})

    logs.update_one({'unique_id': unique_id}, {"$set": creep})

    bing = str(response["choices"][0]["text"])

    try:
      if ':' in bing:
        final_response = bing.rsplit(":", 1)[1]

      elif bing == "":
        final_response = "Just say it once more, ek aur baar bolna"
      else:
        final_response = bing
    except IndexError:
      final_response = "ok"
    if chr(34) in final_response or '"' in final_response:
      if final_response[0] == chr(34): final_response = final_response[1:-1]
      if final_response[1] == chr(34): final_response = final_response[2:-1]

    if isinstance(message.channel, TextChannel):
      #final_response = f'{message.author.mention} {final_response}'
      #if there is a name in final_response I will first replace it with 7 and then cut it into 2 pieces, and attach mention at the start of 2nd one, then merge em again
      if str(message.author)[:-5] in final_response:
        final_response = final_response.replace(str(message.author)[:-5], "7")
        #print(final_response)
        cut1 = final_response.rsplit("7", 1)[0]
        cut2 = final_response.rsplit("7", 1)[1]
        cut2 = f' {message.author.mention} {cut2}'
        final_response = cut1 + cut2
      else:
        final_response = f'{message.author.mention} {final_response}'

    #print(creep['logs'][3])
    #print(f'Logs number: {creep["logs"][1]}')
    if isinstance(message.channel, TextChannel):
      #if creep['logs'][3] >= 3: return
      if creep['logs'][3] >= 2:
        #print("Entering the sending 2nd mess")

        try:
          await message.channel.typing()
        except discord.errors.Forbidden:
          #print("baba re baba")
          return

        try:
          await message.channel.send(final_response)
        except discord.errors.Forbidden:
          #print("baba re baba")
          return

        creep['logs'][3] = 0
        creep['logs'][4] = 0
        #print("2nd message post complete")
        logs.update_one({'unique_id': unique_id}, {"$set": creep})
      else:
        #print("Entering the sending 1st mess")
        #await message.channel.send(final_response)
        try:
          await message.channel.send(final_response)
        except discord.errors.Forbidden:
          #print("baba re baba")
          return

        #sleep(1)
        #print(f'1st mess sent')

    else:
      if creep['logs'][3] >= 2:
        creep['logs'][3] = 0
        creep['logs'][4] = 0
        logs.update_one({'unique_id': unique_id}, {"$set": creep})
      #await message.channel.send(final_response)
      try:
        await message.channel.send(final_response)
      except discord.errors.Forbidden:
        #print("baba re baba")
        return
    """
    elif isinstance(message.channel, TextChannel):
      user['logs'][3] = 0
      creep['logs'][3] = 0
      logs.update_one({'unique_id': user_id}, {"$set": user})
      logs.update_one({'unique_id': unique_id}, {"$set": creep})
      return
    else:
      creep['logs'][3] = 0
      logs.update_one({'unique_id': unique_id}, {"$set": creep})
      return
    """
# client.run(
#   requests.get(
#     'https://api.sheety.co/2886a651e9ccce8cf7c08c476ae384c2/botbaba/sheet1').
#   json()['sheet1'][bot_id]['botTokens'])

  client.run(data.find_one({'bot_unique': str(bot_id + 1)})['Bot_Tokens'])


# Create a list of threads, one for each Discord bot

bot_tokens = []
prompts = []

for i in range(70):
  bot_tokens.append(f'{i}')
  prompts.append(f'{i}')

threads = []
for i in range(70):
  # Create a new thread and add it to the list
  thread = threading.Thread(target=run_bot,
                            args=(i, prompts[i], bot_tokens[i]))
  #thread = threading.Thread(target=run_bot, args=(i))
  threads.append(thread)

# Start all of the threads
for thread in threads:
  thread.start()

for thread in threads:
  thread.join()


async def cleanup_and_exit():
  await cleanup()


cleanup_and_exit()

#hey baby, wanna go to the movies?
