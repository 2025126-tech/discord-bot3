import discord
from discord.ext import commands
from discord import app_commands
import os
import threading
from flask import Flask

# ===== Flask (UptimeRobot用) =====
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

# ===== Discord Bot =====
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 起動時
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot起動: {bot.user}")

# ===== スラッシュコマンド =====

@bot.tree.command(name="ping", description="botの応答速度を確認")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="hello", description="挨拶します")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"こんにちは {interaction.user.mention}!")

# ===== 起動 =====
def start_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKENが設定されていません")
        return
    bot.run(token)

# ===== 実行 =====
if __name__ == "__main__":
    keep_alive()
    start_bot()
