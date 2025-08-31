import os
import requests
import asyncpg
import ssl
from bs4 import BeautifulSoup

# Variáveis de ambiente (vêm do GitHub Actions Secrets)
DATABASE_URL = os.getenv("DATABASE_URL")
API_TOKEN = os.getenv("API_TOKEN")

# Mapeamentos para slot e classificação
SLOT_MAP = {
    "head": 1, "armor": 2, "legs": 3, "feet": 4, "shield": 5,
    "weapon": 6, "distance weapon": 7, "two-handed": 8,
    "amulet": 9, "ring": 10, "backpack": 11
}

CLASSIFICATION_MAP = {
    "sword": 1, "club": 2, "axe": 3, "distance": 4, "wand": 5,
    "rod": 6, "helmet": 7, "armor": 8, "legs": 9, "boots": 10,
    "shield": 11, "amulet": 12, "ring": 13, "container": 14, "tool": 15
}

# =========================
# Função principal
# =========================
async def main():
    # Força SSL para Supabase
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Garante que a URL tenha sslmode=require
    db_url = DATABASE_URL
    if db_url and "sslmode" not in db_url:
        if "?" in db_url:
            db_url += "&sslmode=require"
        else:
            db_url += "?sslmode=require"

    print("🔗 Conectando ao banco...")
    conn = await asyncpg.connect(dsn=db_url, ssl=ssl_context)

    # MONSTROS
    print("🔄 [MONSTERS] Iniciando atualização...")
    creatures = get_creatures_from_tibiadata()
    for creature in creatures:
        wiki_data = get_creature_details_from_tibiawiki(creature)
        if wiki_data:
            health = int(wiki_data.get("hit points", "0").replace(",", "") or 0)
            level = int(wiki_data.get("experience", "0").replace(",", "") or 0)
            attack_type = wiki_data.get("strong against", "")
            weaknesses = wiki_data.get("weak against", "")
            attributes = {
                "speed": wiki_data.get("speed", ""),
                "armor": wiki_data.get("armor", "")
            }
            loots = wiki_data.get("loot", "")
            comment = ""
            await insert_monster(conn, creature, level, health, attack_type, weaknesses, attributes, loots, comment)
            print(f"✅ [MONSTER] {creature} atualizado.")

    # ITENS
    print("🔄 [ITEMS] Iniciando atualização...")
    items = get_items_list()
    for item in items:
        details = get_item_details(item)
        if details:
            slot_str = details.get("slot", "").lower()
            classification_str = details.get("classification", "").lower()

            slot = SLOT_MAP.get(slot_str, 0)
            classification = CLASSIFICATION_MAP.get(classification_str, 0)

            vocation = details.get("vocation", "")
            try:
                level_required = int(details.get("required level", "0").replace(",", "") or 0)
            except:
                level_required = 0
            attack = int(details.get("attack", "0").replace(",", "") or 0)
            defense = int(details.get("defense", "0").replace(",", "") or 0)
            magic = int(details.get("magic level", "0").replace(",", "") or 0)
            description = details.get("description", "")
            tier = 0

            await insert_item(conn, item, slot, vocation, level_required, attack, defense, magic, description, classification, tier)
            print(f"✅ [ITEM] {item} atualizado.")

    await conn.close()
    print("🎯 Atualização concluída com sucesso!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
