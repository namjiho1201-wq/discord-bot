import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- 24시간 유지를 위한 웹 서버 코드 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
# ---------------------------------------

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'--- {bot.user}로 로그인 성공! ---')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)}개의 명령어가 동기화되었습니다.')
    except Exception as e:
        print(f'동기화 에러: {e}')

@bot.tree.command(name="수업추가", description="수업명과 교수명을 입력받아 역할을 생성하고 할당합니다")
async def add_class(interaction: discord.Interaction, 수업명: str, 교수명: str):
    # 10062 에러(Unknown interaction) 방지용 응답 예약
    await interaction.response.defer(ephemeral=True)
    
    try:
        guild = interaction.guild
        역할이름 = f"{수업명}-{교수명}"
        
        existing_role = discord.utils.get(guild.roles, name=역할이름)
        
        if existing_role:
            await interaction.user.add_roles(existing_role)
            await interaction.followup.send(f"✅ 기존 역할 `{역할이름}`을 할당했습니다!", ephemeral=True)
        else:
            new_role = await guild.create_role(name=역할이름)
            await interaction.user.add_roles(new_role)
            await interaction.followup.send(f"✅ 새로운 역할 `{역할이름}`을 생성하고 할당했습니다!", ephemeral=True)
            
    except discord.Forbidden:
        await interaction.followup.send("❌ 봇의 권한이 부족합니다. 서버 설정에서 봇 역할을 위로 올려주세요.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ 오류 발생: {str(e)}", ephemeral=True)

@bot.tree.command(name="내역할", description="내가 가진 모든 역할을 확인합니다")
async def my_roles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    try:
        user_roles = interaction.user.roles
        roles_list = [role.mention for role in user_roles if role.name != "@everyone"]
        if roles_list:
            embed = discord.Embed(title="📋 내 역할", color=discord.Color.blue())
            embed.add_field(name="할당된 역할", value="\n".join(roles_list), inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ 할당된 역할이 없습니다.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ 오류 발생: {str(e)}", ephemeral=True)

# 봇 실행 및 24시간 유지 서버 시작
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    bot.run(TOKEN)
