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
import pymongo
from discord import DMChannel, TextChannel
from time import sleep

import boto3
import colorama
from discord.ext import commands
from colorama import Back, Fore, Style
import platform
import datetime
from discord import ui
import re
import asyncio

now = datetime.datetime.now()
time = (now.strftime("%Y-%m-%d %H:%M:%S"))
colorama.init(autoreset=True)

openai.api_key = "OPEN_AI_KEY"

client2 = MongoClient(
  'MONGO_DB_DATABASE'
)

db = client2['Botdata_v1']
data = db.data
logger = db.logger


class MyModal(ui.Modal, title="make your FAM!"):
  short_d = ui.TextInput(
    label="what Fam u want huh!",
    placeholder="(example: a cheese which talks, genius sci-fi girl)",
    style=discord.TextStyle.long,
    max_length=45)
  long_d = ui.TextInput(
    label="NOW tell everything about Fam",
    placeholder=
    "funny lives in fridge, miss brinjal is his best friend, sings in poems",
    style=discord.TextStyle.long,
    max_length=1500)
  responded = False

  #function which from input creates story, stores name creates voice, emotion,relationship situations, dialogues
  async def on_submit(self, interaction: discord.Interaction):
    if not self.responded:
      self.responded = True
      user = interaction.user

      #if check for the last instance of username and 0 then make it 1
      if data.find_one({'Username': user.name, "Completion": 0}):
        beep = data.update_one({
          "Username": user.name,
          "Completion": 0
        }, {'$set': {
          'Completion': 1
        }})

      await interaction.response.send_message(
        f"Hold on {user.name}! We are Making your Fam...")

      #prompt = f'Generate a 400-word long detailed GPT3 prompt which gives detailed description in third person mode of {self.short_d}.Describe lengthly and in great detail. Talk and reply like {self.short_d}.{self.long_d}.The first word of description should be the name of character'

      story_prompt = f'Generate a 100-word first-person mode description of {self.short_d}.{self.short_d} is {self.long_d}.Write in third-person mode describing {self.short_d}.Imagine a name for the character as well. Make the description very human-like with flaws,great traits and entire personality defined. The First word of description should always be name of character'

      response_story = openai.Completion.create(engine="text-davinci-003",
                                                prompt=f'{story_prompt}\n',
                                                max_tokens=1212,
                                                n=1,
                                                temperature=0.8,
                                                frequency_penalty=2,
                                                presence_penalty=1.49)
      story = response_story["choices"][0]["text"]
      name = story.split()[0]
      name = ''.join([c for c in name if c.isalpha()])
      if name == 'My':
        name = story.split()[3]
        name = ''.join([c for c in name if c.isalpha()])

      prompt = f"Generate a 250 word long detailed GPT3 prompt in first-person mode of {self.short_d}. Write it in first-person mode of the {self.short_d}. Name is {name}. {name} talks like a GenZ with maximum 6 words in each of his replies.{name} uses a lot of GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap. {name} will misspell words like a GenZ and give each replies in max 6 words.{name} is {self.long_d}. Describe lengthly, in great detail and in first-person mode of {name},{self.short_d}."

      response = openai.Completion.create(engine="text-davinci-003",
                                          prompt=f'{prompt}\n',
                                          max_tokens=1212,
                                          n=1,
                                          temperature=1,
                                          frequency_penalty=2,
                                          presence_penalty=1.49)

      description = response["choices"][0]["text"]
      #story = response["choices"][0]["text"]
      #chimp = story.split("Hi")[1]
      #chimp = "Hi" + chimp
      #name = str(self.namo)

      secondaries = "okjgsgslfs"
      print(secondaries)
      response = openai.Image.create(
        prompt=
        f'digital art colorful anime profile picture,{name} {self.short_d}.',
        n=1,
        size="256x256")

      # Extract the URL of the generated image
      image_url = response['data'][0]['url']
      print(image_url)

      # download the image from the URL
      response = requests.get(image_url)
      image_data = response.content

      # save the image data to a local file
      with open(f'{name}.jpg', 'wb') as f:
        f.write(image_data)

        s3 = boto3.client(
          's3',
          aws_access_key_id='AKIAUNFXI2AGVXDAKF6K',
          aws_secret_access_key='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')
        s3.upload_file(f'{name}.jpg', 'whatthefraand', f'{name}.jpg')
        photo_url = f'http://whatthefraand.s3.ap-south-1.amazonaws.com/{name}.jpg'
        print(photo_url)

      secondary = {
        "Voice": ["", 0],
        "Emotion": ["", 0],
        "Relationship": ["", 0],
        "Situations": ["", 0],
        "Dialogue1": ["", 0],
        "Dialogue2": ["", 0]
      }

      for i in range(len(secondaries)):
        secondary["Voice"][0] = secondaries[0]
        secondary["Emotion"][0] = secondaries[1]
        secondary["Relationship"][0] = secondaries[2]
        secondary["Situations"][0] = secondaries[3]
        secondary["Dialogue1"][0] = f'### {secondaries[4]} ###'
        secondary["Dialogue2"][0] = f'### {secondaries[5]} ###'

      ching = data.find_one({'Username': "None"})
      final_prompt = f"This is a 2-way conversation between me and {name}, {self.short_d}.You have to generate maximum 6-word GenZ like replies of {name},{self.short_d}.Replies should be GenZ like maximum 6-word long,do not use emojis.{name} will be talking a lot about themselves.{name} is {self.long_d}.{name} will be talking like a GenZ.{name} will use GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap.{name} will maximum put 1 emoji but that too very rarely. Initially {name} will introduce themselves and talk about themselves.{name} will know all about the musics and shows, and will share about them while giving context of their own situation.Remember to give maximum 6-word replies only.But make replies conversational. \n {name}, {self.short_d} is described below in first-person mode. \n {description} ### Me:-hi! \n {name}:Sup? How are u? ### ### Me:-hey! \n {name}:Sup? How are u? ### ### Me:-hey there! \n {name}:Sup? How are u? ###"

      beep = data.update_one({'Username': "None"}, {
        '$set': {
          'Username': user.name,
          'Prompt': final_prompt,
          'Name': name,
          'url': photo_url,
          'Story': story,
          'Secondaries': secondary,
          'Completion': 0,
          'Initial_Phrase': [str(self.short_d),
                             str(self.long_d)]
        }
      })

      print(story)

      embed = discord.Embed(title=name, color=discord.Color.green())
      embed.add_field(name="Vibe", value="not set")
      embed.set_image(url=image_url)
      embed.add_field(name="Your Fam is Here!🚀 (add to server & dm)",
                      value=ching['Link'])
      embed.description = story
      await interaction.followup.send(embed=embed)
      await interaction.followup.send(
        f"Congrats! *{user.name}* You just made a new **fam**. Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
      )


class revamp(ui.Modal, title="Generate Fam's story from parts!"):
  world = ui.TextInput(label="Describe the world & era of your fam",
                       placeholder="Atlantis City under the water",
                       style=discord.TextStyle.long,
                       max_length=1800)
  personality = ui.TextInput(label="Describe the personality of your fam",
                             placeholder="Really cranky but very cute",
                             style=discord.TextStyle.long,
                             max_length=1800)
  friends = ui.TextInput(
    label="Who are the friends of your Fam",
    placeholder=
    "She has a friend named Tabby who is a genius at math but really stupid",
    style=discord.TextStyle.long,
    max_length=1800)
  responded = False

  async def on_submit(self, interaction: discord.Interaction):

    if not self.responded:
      self.responded = True
      user = interaction.user
      await interaction.response.send_message(
        f"Hold on {user.name} revamping your Fam's Story...")

      ching = data.find_one({"Username": user.name, "Completion": 0})
      if ching == None:
        await interaction.followup.send(
          "Hey! First Use /make-fam command and begin creating!")
      print(ching["Name"])

      name = ching['Name']
      short_d = ching['Initial_Phrase'][0]
      long_d = ching['Initial_Phrase'][1]

      story_prompt = f'Generate a 100-word first-person mode description of {short_d}.{short_d} is {long_d}.Write in first-person mode as if {short_d} is describing themselves. Make the description very human-like with flaws,great traits and entire personality defined. Start the description from the sentence Hi I am {name}'

      response_story = openai.Completion.create(engine="text-davinci-003",
                                                prompt=f'{story_prompt}\n',
                                                max_tokens=1212,
                                                n=1,
                                                temperature=1,
                                                frequency_penalty=2,
                                                presence_penalty=1.49)

      old_story = response_story["choices"][0]["text"]
      name = old_story.split()[0]
      name = ''.join([c for c in name if c.isalpha()])

      prompt = f"Generate a 250 word long detailed GPT3 prompt in first-person mode of {short_d}. Write it in first-person mode of the {short_d}. Name is {name}. {name} talks like a GenZ with maximum 6 words in each of their replies.{name} uses a lot of GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap.{name} will sometimes use emojis. {name} will misspell words like a GenZ and give each replies in max 6 words.{name} is {long_d}.{name} lives in {self.world}.{name} has these friends {self.friends}.{name} has a personality like {self.personality} Describe lengthly, in great detail and in first-person mode of {name}, {short_d}."

      response2 = openai.Completion.create(engine="text-davinci-003",
                                           prompt=f'{prompt}\n',
                                           max_tokens=1212,
                                           n=1,
                                           temperature=1,
                                           frequency_penalty=2,
                                           presence_penalty=1.49)
      story = response2["choices"][0]["text"]

      final_story = f"This is a 2-way conversation between me and {name}, {short_d}.You have to generate maximum 6-word GenZ like replies of {name},{short_d}.Replies should be GenZ like maximum 6-word long.{name} will be sharing about themselves and ask questions about me.{name} is {long_d}.{name} will be talking like a GenZ.{name} will use GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap. {name} will sometimes use emojis.{name} will maximum put 1 emoji but that too very rarely. Initially {name} will introduce herself and just get to know me, but then later start to subtly ask questions about the topics {name} is interested in and talk about music and tv shows.{name} will know all about the musics and shows. Based on my answers, if {name} agrees {name} will expand on my points, if {name} doesnt then {name} will debate with me and ask me to explain more.Remember to give maximum 6-word replies only.But make replies conversational. \n {name}, {short_d} is described below in first-person mode.' + '\n' + {story} + '### Me:-hi! \n {name}:Sup? How are u? ###' + '### Me:-hey! \n {name}:Sup? How are u? ### + '### Me:-hey there! \n {name}:Sup? How are u? ###'"

      print(final_story)

      beep = data.update_one({
        "Username": user.name,
        "Completion": 0
      }, {
        '$set': {
          'Username': user.name,
          'Prompt': final_story + '\n' + story,
          'Story': old_story,
          'Secondaries': ching['Secondaries'],
          'Completion': 0
        }
      })

      embed2 = discord.Embed(title=ching['Name'],
                             color=discord.Color.blurple())

      if ching["Secondaries"]["Emotion"][1] == 0:
        embed2.add_field(name="Vibe", value="not set")
      else:
        embed2.add_field(name="Vibe", value=ching["Secondaries"]["Emotion"][0])

      embed2.set_image(url=ching['url'])
      embed2.description = old_story
      embed2.add_field(name="Your Fam is Here!🚀 (add to server & dm)",
                       value=ching['Link'])
      await interaction.followup.send(embed=embed2)
      await interaction.followup.send(
        f"Yooo!!*{user.name}* Revamped Done!!!! You just made a new **fam**. Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
      )
      
      
client = commands.Bot(command_prefix="`", intents=discord.Intents.all())


@client.event
async def on_ready():
  print(Fore.LIGHTGREEN_EX + time + Fore.RESET + " " + "Logged in as " +
        Style.BRIGHT + Fore.MAGENTA + client.user.name + Style.RESET_ALL +
        Fore.RESET)
  synced = await client.tree.sync()
  print(Fore.LIGHTGREEN_EX + time + Fore.RESET + " " + "Slash CMDs synced " +
        Style.BRIGHT + Fore.LIGHTBLUE_EX + str(len(synced)) + Style.RESET_ALL +
        Fore.RESET)


@client.event
async def on_message(message):
  # So our bot doesn't reply to itself
  if message.author.id == client.user.id:
    return
  async with message.channel.typing():
    await asyncio.sleep(0.5)
    if message.content == "hello" or "hi" or "Hey" or "Hello":
      # Get a reference to the text channel
      channel = message.channel
      # Send the message
      await channel.send(
        f" Use the following command to make your fam🚀:\n\n `/fam` to Create a Fam From Scratch\n"
      )

      # Allows bot to use @bot.command() commands along with on_message event
      #await client.process_commands(ctx)


#1 MAKE Command
@client.tree.command(name="fam",
                     description="Make a Fam From Scratch")
async def modal(interaction: discord.Interaction, ):
  await interaction.response.send_modal(MyModal())


#2 Revamp Command
@client.tree.command(name="revamp", description="Revamp your fam's story")
async def modal1(interaction: discord.Interaction, ):
  await interaction.response.send_modal(revamp())


#3 Vibe Command
@client.tree.command(name="vibe", description="Set the mood of your FAM")
async def newcommand(
  interaction: discord.Interaction,
  direction: str,
):
  user = interaction.user
  await interaction.response.send_message(f'Hold On! {user.name} Generating...'
                                          )
  ching = data.find_one({"Username": user.name, "Completion": 0})
  if ching == None:
    await interaction.followup.send(f"Hold on! {user.name} Setting Emotion...")
  name = ching['Name']
  story = ching['Story']
  short_d = ching['Initial_Phrase'][0]
  long_d = ching['Initial_Phrase'][1]

  ching["Secondaries"]["Emotion"] = [str(direction), 1]
  keys = list(ching["Secondaries"].keys())
  name = ching['Name']
  story = ching['Story']

  story_prompt = f'Generate a 100-word first-person mode description of {short_d}.{short_d} is {long_d}.Write in first-person mode as if {short_d} is describing themselves. Make the description very human-like with flaws,great traits and entire personality defined. Start the description from the sentence Hi I am {name}'

  response_story = openai.Completion.create(engine="text-davinci-003",
                                            prompt=f'{story_prompt}\n',
                                            max_tokens=1212,
                                            n=1,
                                            temperature=1,
                                            frequency_penalty=2,
                                            presence_penalty=1.49)

  old_story = response_story["choices"][0]["text"]
  name = old_story.split()[0]
  name = ''.join([c for c in name if c.isalpha()])

  prompt = f"Generate a 250 word long detailed GPT3 prompt in first-person mode of {short_d}. Write it in first-person mode of the {short_d}. Name is {name}. {name} talks like a GenZ with maximum 6 words in each of their replies.{name} uses a lot of GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap.{name} will sometimes use emojis. {name} will misspell words like a GenZ and give each replies in max 6 words.{name} is {long_d}.But, {name} has a deep vibe of {direction} Describe lengthly, in great detail and in first-person mode of {name}, {short_d}."

  response2 = openai.Completion.create(engine="text-davinci-003",
                                       prompt=f'{prompt}\n',
                                       max_tokens=1212,
                                       n=1,
                                       temperature=1,
                                       frequency_penalty=2,
                                       presence_penalty=1.49)
  description = response2['choices'][0]['text']
  final_story = f"This is a 2-way conversation between me and {name}, {short_d}.You have to generate maximum 6-word GenZ like replies of {name},{short_d}.Replies should be GenZ like maximum 6-word long.{name} will be sharing about themselves and ask questions about me.{name} is {long_d}.{name} will be talking like a GenZ.{name} will use GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap. {name} will sometimes use emojis.{name} will maximum put 1 emoji but that too very rarely. Initially {name} will introduce herself and just get to know me, but then later start to subtly ask questions about the topics {name} is interested in and talk about music and tv shows.{name} will know all about the musics and shows. Based on my answers, if {name} agrees {name} will expand on my points, if {name} doesnt then {name} will debate with me and ask me to explain more.Remember to give maximum 6-word replies only.But make replies conversational. \n {name}, {short_d} is described below in first-person mode.' + '\n' + {story} + '### Me:-hi! \n {name}:Sup? How are u? ###' + '### Me:-hey! \n {name}:Sup? How are u? ### + '### Me:-hey there! \n {name}:Sup? How are u? ###'"
  print(final_story)
  data.update_one({
    "Username": user.name,
    "Completion": 0
  }, {
    '$set': {
      'Prompt': final_story,
      'Story': old_story,
      'Secondaries': ching['Secondaries']
    }
  })

  embed6 = discord.Embed(title=ching['Name'], color=discord.Color.blurple())

  if ching["Secondaries"]["Emotion"][1] == 0:
    embed6.add_field(name="Vibe", value="not set")
  else:
    embed6.add_field(name="Vibe", value=ching["Secondaries"]["Emotion"][0])
  embed6.description = old_story
  embed6.set_image(url=ching['url'])
  embed6.add_field(name="Your Fam is Here!🚀 (add to server & dm)",
                   value=ching['Link'])

  await interaction.followup.send(embed=embed6)
  await interaction.followup.send(
    f"Vibe Setted! {user.name}. Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
  )


#4 refine Command
@client.tree.command(name="refine",
                     description="refine the character of your fam..")
async def newcommand(
  interaction: discord.Interaction,
  write: str,
):
  user = interaction.user
  await interaction.response.send_message(f'Hold On! {user.name} Generating...'
                                          )
  ching = data.find_one({"Username": user.name, "Completion": 0})
  if ching == None:
    await interaction.followup.send(f"Hold on! {user.name} Setting Emotion...")
  name = ching['Name']
  story = ching['Story']
  short_d = ching['Initial_Phrase'][0]
  long_d = ching['Initial_Phrase'][1]

  ching["Secondaries"]["Voice"] = [str(write), 1]
  keys = list(ching["Secondaries"].keys())
  name = ching['Name']
  story = ching['Story']
  refine = write

  story_prompt = f'Generate a 100-word first-person mode description of {short_d}.{short_d} is {long_d}.Write in first-person mode as if {short_d} is describing themselves. Make the description very human-like with flaws,great traits and entire personality defined. Start the description from the sentence Hi I am name {name}'

  response_story = openai.Completion.create(engine="text-davinci-003",
                                            prompt=f'{story_prompt}\n',
                                            max_tokens=1212,
                                            n=1,
                                            temperature=1,
                                            frequency_penalty=2,
                                            presence_penalty=1.49)

  old_story = response_story["choices"][0]["text"]
  name = old_story.split()[0]
  name = ''.join([c for c in name if c.isalpha()])

  prompt = f'Generate a 250 word long detailed GPT3 prompt in first-person mode of {short_d}. Write it in first-person mode of the {short_d}. Name is {name}. {name} talks like a GenZ with maximum 6 words in each of his replies.{name} uses a lot of GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap.{name} will sometimes use emojis. {name} will misspell words like a GenZ and give each replies in max 6 words.{name} will know all about music,shows,animes and the latest news. {name} is {long_d}.But, make the character of {name} very {write} Describe lengthly, in great detail and in first-person mode of {name}, {short_d}.'

  response2 = openai.Completion.create(engine="text-davinci-003",
                                       prompt=f'{prompt}\n',
                                       max_tokens=1212,
                                       n=1,
                                       temperature=1,
                                       frequency_penalty=2,
                                       presence_penalty=1.49)
  description = response2['choices'][0]['text']
  final_prompt = f"This is a 2-way conversation between me and {name}, {short_d}.You have to generate maximum 6-word GenZ like replies of {name},{short_d}.Replies should be GenZ like maximum 6-word long.{name} will be sharing about themselves and ask questions about me.{name} is {long_d}.{name} will be talking like a GenZ.{name} will use GenZ slangs like lmao,drip,sus,sksksks,ngl,no cap. {name} will sometimes use emojis.{name} will maximum put 1 emoji but that too very rarely. Initially {name} will introduce herself and just get to know me, but then later start to subtly ask questions about the topics {name} is interested in and talk about music and tv shows.{name} will know all about the musics and shows. Based on my answers, if {name} agrees {name} will expand on my points, if {name} doesnt then {name} will debate with me and ask me to explain more.Remember to give maximum 6-word replies only.But make replies conversational. \n {name}, {short_d} is described below in first-person mode.' + '\n' + {story} + '### Me:-hi! \n {name}:Sup? How are u? ###' + '### Me:-hey! \n {name}:Sup? How are u? ### + '### Me:-hey there! \n {name}:Sup? How are u? ### +\n + {description}"
  print(final_prompt)
  data.update_one({
    "Username": user.name,
    "Completion": 0
  }, {
    '$set': {
      'Prompt': final_prompt,
      'Story': old_story,
      'Secondaries': ching['Secondaries']
    }
  })

  embed6 = discord.Embed(title=ching['Name'], color=discord.Color.blurple())
  if ching["Secondaries"]["Emotion"][1] == 0:
    embed6.add_field(name="Vibe", value="not set")
  else:
    embed6.add_field(name="Vibe", value=ching["Secondaries"]["Emotion"][0])
  embed6.description = old_story
  embed6.set_image(url=ching['url'])
  embed6.add_field(name="Your Fam is Here!🚀 (add to server & dm)",
                   value=ching['Link'])

  await interaction.followup.send(embed=embed6)
  await interaction.followup.send(
    f"Refine Done! {user.name}. Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
  )


#5 Name Command
@client.tree.command(name="name", description="Change up Fam's name")
async def namecommand(
  interaction: discord.Interaction,
  direction: str,
):
  user = interaction.user
  await interaction.response.send_message(f'Hold On! {user.name} Generating...'
                                          )
  ching = data.find_one({"Username": user.name, "Completion": 0})
  if ching == None:
    await interaction.response.send_message(f"use /make-fam please!...")

  old_name = ching['Name']
  namo = str(direction)
  name = ching['Name']
  ching['Name'] = namo
  ching['Story'] = ching['Story'].replace(old_name, namo)
  story = ching['Story'].replace(old_name, namo)
  story = ching['Story']
  ching['Prompt'] = ching['Prompt'].replace(old_name, namo)
  ching['Flag'][1] = 1
  for value in ching['Secondaries'].values():
    value[0] = value[0].replace(old_name, namo)
  keys = list(ching["Secondaries"].keys())

  data.update_one({
    "Username": user.name,
    "Completion": 0
  }, {
    '$set': {
      'Prompt': ching['Prompt'],
      'Name': str(direction),
      'Story': ching['Story'],
      'Secondaries': ching['Secondaries'],
      'Flag': ching['Flag']
    }
  })

  embed9 = discord.Embed(title=ching['Name'], color=discord.Color.red())

  if ching["Secondaries"]["Emotion"][1] == 0:
    embed9.add_field(name="Emotion", value="not set")
  else:
    embed9.add_field(name="Emotion", value=ching["Secondaries"]["Emotion"][0])
  embed9.description = story
  embed9.add_field(name="Your Fam is Here!🚀 (add to server & dm)",
                   value=ching['Link'])

  embed9.set_image(url=ching['url'])
  await interaction.followup.send(embed=embed9)
  await interaction.followup.send(
    f"Congrats! You just refined your **fam**. Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
  )


#5 Name Command
@client.tree.command(name="rename", description="Change up Fam's name")
async def namecommand(
  interaction: discord.Interaction,
  direction: str,
):
  user = interaction.user
  await interaction.response.send_message(f'Hold On! {user.name} Generating...'
                                          )
  ching = data.find_one({"Username": user.name, "Completion": 0})
  if ching == None:
    await interaction.response.send_message(f"use /make-fam please!...")

  old_name = ching['Name']
  namo = str(direction)
  name = ching['Name']
  ching['Name'] = namo
  ching['Story'] = ching['Story'].replace(old_name, namo)
  story = ching['Story'].replace(old_name, namo)
  story = ching['Story']
  ching['Prompt'] = ching['Prompt'].replace(old_name, namo)
  ching['Flag'][1] = 1
  for value in ching['Secondaries'].values():
    value[0] = value[0].replace(old_name, namo)
  keys = list(ching["Secondaries"].keys())

  data.update_one({
    "Username": user.name,
    "Completion": 0
  }, {
    '$set': {
      'Prompt': ching['Prompt'],
      'Name': str(direction),
      'Story': ching['Story'],
      'Secondaries': ching['Secondaries'],
      'Flag': ching['Flag']
    }
  })

  embed9 = discord.Embed(title=ching['Name'], color=discord.Color.red())

  if ching["Secondaries"]["Emotion"][1] == 0:
    embed9.add_field(name="Emotion", value="not set")
  else:
    embed9.add_field(name="Emotion", value=ching["Secondaries"]["Emotion"][0])
  embed9.description = story
  embed9.add_field(name="Your Fam is Here!🚀 (add to server & dm)",
                   value=ching['Link'])

  embed9.set_image(url=ching['url'])
  await interaction.followup.send(embed=embed9)
  await interaction.followup.send(
    f"Congrats! You just refined your **fam**. Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
  )




#6 IMAGE GENERATION
@client.tree.command(name="avatar", description="Generate an image")
async def generate_image(
  interaction: discord.Interaction,
  imagine: str,
):
  user = interaction.user
  await interaction.response.send_message("Hold On !Generating...")
  ching = data.find_one({"Username": user.name, "Completion": 0})
  ching['Flag'][0] = 1
  name = ching['Name']
  res = openai.Image.create(
    prompt=f'high quality colorful anime profile picture' + imagine,
    n=1,
    size="256x256",
  )
  image_url = res['data'][0]['url']
  print(image_url)

  res = requests.get(image_url)
  image_data = res.content

  # Split the string into a list of words and join them with an empty separator
  imagine = ''.join(imagine.split())

  with open(f'{imagine}.jpg', 'wb') as f:
    f.write(image_data)

  s3 = boto3.client(
    's3',
    aws_access_key_id='',
    aws_secret_access_key='')
  s3.upload_file(f'{imagine}.jpg', 'whatthefraand', f'{imagine}.jpg')
  photo_url2 = f'http://whatthefraand.s3.ap-south-1.amazonaws.com/{imagine}.jpg'
  print(photo_url2)

  data.update_one({
    "Username": user.name,
    "Completion": 0
  }, {'$set': {
    'Flag': ching['Flag'],
    'url': photo_url2
  }})

  embed10 = discord.Embed(title=ching['Name'], color=discord.Color.blurple())

  if ching["Secondaries"]["Emotion"][1] == 0:
    embed10.add_field(name="Vibe", value="not set")
  else:
    embed10.add_field(name="Vibe", value=ching["Secondaries"]["Emotion"][0])
  embed10.description = ching['Story']
  embed10.set_image(url=photo_url2)
  embed10.add_field(name="Your Fam is Here!🚀 (add to server & dm)",
                    value=ching['Link'])
  await interaction.followup.send(embed=embed10)
  await interaction.followup.send(
    f"Heyyo! {user.name} Profile Picture Changed! . Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
  )


#7 HELP
@client.tree.command(name="help", description="See all the commands")
async def generate_image(interaction: discord.Interaction, ):
  await interaction.response.send_message(
    f" Use the following commands to iterate on your fam:\n\n **main** \n `/fam` to Create a Fam From Scratch\n\n **story** \n`/revamp` to rewrite your fams's life-story \n `/refine` to refine the character of your fam\n `/vibe` set the vibe of ur fam\n\n **Bio** \n `/rename` to change your fam's name \n `/avatar` to change the profile picture of your fam."
  )


#BOT_TOKEN
client.run("BOT_TOKEN")
