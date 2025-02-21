import discord

def build_match_embed(game_name, tag, match_id, player_stats):
    embed = discord.Embed(title=f"📊 {game_name} ({tag}) - {player_stats.champion}", color=0x00ff00)
    embed.add_field(name="🏅 Esito", value="✅ Vittoria" if player_stats.win else "❌ Sconfitta", inline=True)
    embed.add_field(name="⚔️ KDA", value=f"{player_stats.kills}/{player_stats.deaths}/{player_stats.assists}", inline=True)
    embed.add_field(name="🎮 Ruolo", value=player_stats.role, inline=True)
    
    if hasattr(player_stats, 'cspm'):
        embed.add_field(name="📈 CSPM", value=f"{player_stats.cspm:.2f}", inline=True)
    if hasattr(player_stats, 'dpm'):
        embed.add_field(name="🔥 DPM", value=f"{player_stats.dpm:.2f}", inline=True)
    if hasattr(player_stats, 'solo_kills'):
        embed.add_field(name="🛡️ Solo Kills", value=player_stats.solo_kills, inline=True)
    if hasattr(player_stats, 'gold_diff_10'):
        embed.add_field(name="💰 Gold Diff @10min", value=player_stats.gold_diff_10, inline=True)
    if hasattr(player_stats, 'jungle_proximity'):
        embed.add_field(name="🌲 Jungle Proximity", value=f"{player_stats.jungle_proximity:.2f}%", inline=True)
    if hasattr(player_stats, 'first_blood'):
        embed.add_field(name="🔪 First Blood", value="✅" if player_stats.first_blood else "❌", inline=True)
    if hasattr(player_stats, 'counter_jungle'):
        embed.add_field(name="👹 Counter Jungling", value=f"{player_stats.counter_jungle:.2f}%", inline=True)
    if hasattr(player_stats, 'roaming'):
        embed.add_field(name="🚶 Roaming %", value=f"{player_stats.roaming:.2f}%", inline=True)
    if hasattr(player_stats, 'kill_conversion'):
        embed.add_field(name="⚡ Kill Conversion Rate", value=f"{player_stats.kill_conversion:.2f}", inline=True)
    if hasattr(player_stats, 'vision_score'):
        embed.add_field(name="👀 Vision Score", value=player_stats.vision_score, inline=True)
    if hasattr(player_stats, 'kill_participation'):
        embed.add_field(name="🔗 Kill Participation", value=f"{player_stats.kill_participation:.2f}%", inline=True)
    if hasattr(player_stats, 'objective_assist'):
        embed.add_field(name="🎯 Objective Assist", value=player_stats.objective_assist, inline=True)
    
    embed.set_footer(text=f"Match ID: {match_id}")
    return embed
