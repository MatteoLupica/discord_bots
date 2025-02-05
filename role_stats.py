class PlayerStats:
    """Classe base per le statistiche di un giocatore."""
    def __init__(self, participant, team, game_duration):
        self.champion = participant.get("championName", "Unknown")
        self.role = participant.get("teamPosition", "UNKNOWN")
        self.kills = participant.get("kills", 0)
        self.deaths = participant.get("deaths", 0)
        self.assists = participant.get("assists", 0)
        self.vision_score = participant.get("visionScore", 0)
        self.win = participant.get("win", False)
        self.game_duration = game_duration / 60  # Converti in minuti

        # Calcola statistiche comuni
        self.cspm = (participant.get("totalMinionsKilled", 0) + participant.get("neutralMinionsKilled", 0)) / self.game_duration
        self.dpm = participant.get("totalDamageDealtToChampions", 0) / self.game_duration
        self.kill_participation = (self.kills + self.assists) / max(sum(p.get("kills", 0) for p in team), 1) * 100

    def print_stats(self):
        """Metodo che verrà sovrascritto dalle sottoclassi."""
        raise NotImplementedError


class TopStats(PlayerStats):
    """Statistiche specifiche per la Top Lane."""
    def __init__(self, participant, team, game_duration):
        super().__init__(participant, team, game_duration)
        self.solo_kills = participant.get("soloKills", 0)
        self.gold_diff_10 = participant.get("goldDiffAt10", 0)
        self.xp_diff_10 = participant.get("xpDiffAt10", 0)

    def print_stats(self):
        print(f"🏆 {self.champion} (Top Lane) - {'✅ Vittoria' if self.win else '❌ Sconfitta'}")
        print(f"⚔️ KDA: {self.kills}/{self.deaths}/{self.assists}")
        print(f"📈 CSPM: {self.cspm:.2f}")
        print(f"🔥 DPM: {self.dpm:.2f}")
        print(f"🔗 Kill Participation: {self.kill_participation:.2f}%")
        print(f"🛡️ Solo Kills: {self.solo_kills}")
        print(f"💰 Gold Diff @10min: {self.gold_diff_10}")
        print(f"📊 XP Diff @10min: {self.xp_diff_10}")
        print("-" * 50)


class JungleStats(PlayerStats):
    """Statistiche specifiche per la Jungle."""
    def __init__(self, participant, team, game_duration):
        super().__init__(participant, team, game_duration)

        # Calcolo del farm nei primi 10 minuti
        self.jungle_cs_10min = participant.get("neutralMinionsKilled", 0)
        
        # Calcolo della Jungle Proximity (quanto tempo passa vicino alle lane)
        self.jungle_proximity = (15 - min(self.jungle_cs_10min / 5, 15)) + (self.kill_participation / 5)

        # Partecipazione alla prima uccisione
        self.first_blood = participant.get("firstBloodKill", False) or participant.get("firstBloodAssist", False)

        # Controllo degli obiettivi
        self.scuttles = participant.get("firstScuttleCrab", 0)  # Scuttle Crab
        self.herald = participant.get("firstRiftHerald", 0)  # Herald
        self.dragon = participant.get("firstDragon", 0)  # Dragon
        self.objectives_taken = self.scuttles + self.herald + self.dragon

        # Controllo della Counter Jungling (% di mostri rubati nella giungla nemica)
        self.enemy_jungle_cs = participant.get("enemyJungleMinionsKilled", 0)
        self.total_jungle_cs = self.jungle_cs_10min + self.enemy_jungle_cs
        self.counter_jungle = (self.enemy_jungle_cs / max(self.total_jungle_cs, 1)) * 100  # % farm rubato

    def print_stats(self):
        print(f"🏆 {self.champion} (Jungle) - {'✅ Vittoria' if self.win else '❌ Sconfitta'}")
        print(f"⚔️ KDA: {self.kills}/{self.deaths}/{self.assists}")
        print(f"📈 CSPM: {self.cspm:.2f}")
        print(f"🔥 DPM: {self.dpm:.2f}")
        print(f"🔗 Kill Participation: {self.kill_participation:.2f}%")
        print(f"🌲 Jungle Proximity: {self.jungle_proximity:.2f}%")
        print(f"🔪 First Blood: {'✅' if self.first_blood else '❌'}")
        print(f"👹 Counter Jungling: {self.counter_jungle:.2f}%")
        print(f"🐲 Obiettivi presi: {self.objectives_taken} (Scuttles: {self.scuttles}, Herald: {self.herald}, Dragon: {self.dragon})")
        print("-" * 50)



class MidStats(PlayerStats):
    """Statistiche specifiche per la Mid Lane."""
    def __init__(self, participant, team, game_duration):
        super().__init__(participant, team, game_duration)
        self.roaming = (participant.get("timeCCingOthers", 0) / self.game_duration) * 100

    def print_stats(self):
        print(f"🏆 {self.champion} (Mid Lane) - {'✅ Vittoria' if self.win else '❌ Sconfitta'}")
        print(f"⚔️ KDA: {self.kills}/{self.deaths}/{self.assists}")
        print(f"📈 CSPM: {self.cspm:.2f}")
        print(f"🔥 DPM: {self.dpm:.2f}")
        print(f"🔗 Kill Participation: {self.kill_participation:.2f}%")
        print(f"🚶 Roaming: {self.roaming:.2f}%")
        print("-" * 50)


class ADCStats(PlayerStats):
    """Statistiche specifiche per ADC (Bot Lane)."""
    def __init__(self, participant, team, game_duration):
        super().__init__(participant, team, game_duration)
        self.kill_conversion = self.kills / max(participant.get("totalDamageDealtToChampions", 1), 1)

    def print_stats(self):
        print(f"🏆 {self.champion} (ADC) - {'✅ Vittoria' if self.win else '❌ Sconfitta'}")
        print(f"⚔️ KDA: {self.kills}/{self.deaths}/{self.assists}")
        print(f"📈 CSPM: {self.cspm:.2f}")
        print(f"🔥 DPM: {self.dpm:.2f}")
        print(f"🔗 Kill Participation: {self.kill_participation:.2f}%")
        print(f"⚡ Kill Conversion Rate: {self.kill_conversion:.2f}")
        print("-" * 50)


class SupportStats(PlayerStats):
    """Statistiche specifiche per il Support."""
    def __init__(self, participant, team, game_duration):
        super().__init__(participant, team, game_duration)
        self.roaming = (participant.get("timeCCingOthers", 0) / self.game_duration) * 100
        self.objective_assist = participant.get("totalDamageShieldedOnTeammates", 0)

    def print_stats(self):
        print(f"🏆 {self.champion} (Support) - {'✅ Vittoria' if self.win else '❌ Sconfitta'}")
        print(f"⚔️ KDA: {self.kills}/{self.deaths}/{self.assists}")
        print(f"👀 Vision Score: {self.vision_score}")
        print(f"🔗 Kill Participation: {self.kill_participation:.2f}%")
        print(f"🎯 Objective Assist: {self.objective_assist}")
        print(f"🚶 Roaming: {self.roaming:.2f}%")
        print("-" * 50)


def get_role_class(participant, team, game_duration):
    role = participant.get("teamPosition", "UNKNOWN")
    if role == "TOP":
        return TopStats(participant, team, game_duration)
    elif role == "JUNGLE":
        return JungleStats(participant, team, game_duration)
    elif role == "MIDDLE":
        return MidStats(participant, team, game_duration)
    elif role == "BOTTOM":
        return ADCStats(participant, team, game_duration)
    elif role == "UTILITY":
        return SupportStats(participant, team, game_duration)
    else:
        return PlayerStats(participant, team, game_duration)
