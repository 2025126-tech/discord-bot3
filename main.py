import discord
from discord.ext import commands
import json
import os
import asyncio
from flask import Flask
from threading import Thread

# ======================
# Flask (Render用)
# ======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# ======================
# config
# ======================

CONFIG_FILE = "guild_config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return {}
            return json.loads(data)
    except:
        return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

# ======================
# Discord Bot
# ======================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# 起動
# ======================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"起動成功: {bot.user}")

# ======================
# スラッシュコマンド
# ======================

@bot.tree.command(name="set_notify", description="通知チャンネルを設定")
async def set_notify(interaction: discord.Interaction, channel: discord.TextChannel):

    cfg = load_config()
    cfg[str(interaction.guild.id)] = channel.id
    save_config(cfg)

    await interaction.response.send_message(
        f"通知チャンネルを {channel.mention} に設定しました"
    )

@bot.tree.command(name="show_notify", description="通知チャンネル確認")
async def show_notify(interaction: discord.Interaction):

    cfg = load_config()
    ch_id = cfg.get(str(interaction.guild.id))

    if ch_id:

        channel = bot.get_channel(ch_id)

        await interaction.response.send_message(
            f"現在の通知チャンネル: {channel.mention}"
        )

    else:

        await interaction.response.send_message(
            "通知チャンネルは設定されていません"
        )

# ======================
# VC通知
# ======================

@bot.event
async def on_voice_state_update(member, before, after):

    cfg = load_config()
    ch_id = cfg.get(str(member.guild.id))

    if not ch_id:
        return

    channel = bot.get_channel(ch_id)

    if not channel:
        return

    if before.channel is None and after.channel is not None:

        await channel.send(
            f"🎤 {member.display_name} が **{after.channel.name}** に参加しました"
        )

    elif before.channel is not None and after.channel is None:

        await channel.send(
            f"👋 {member.display_name} がボイスチャットから退出しました"
        )

# ======================
# 自動復帰
# ======================

async def run_bot():

    token = os.getenv("DISCORD_TOKEN")

    while True:

        try:
            await bot.start(token)

        except Exception as e:

            print("エラー:", e)

            await asyncio.sleep(60)

# ======================
# start
# ======================

if __name__ == "__main__":

    Thread(target=run_web).start()

    asyncio.run(run_bot())
