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
# Funções para MONSTROS
# =========================
def get_creatures_from_tibiadata():
    url = "https://api.tibiadata.com/v4/creatures"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return [c["name"] for c in data["creatures"]["creature_list"]]

def get_creature_details_from_tibiawiki(name):
    page_name = name.replace(" ", "_")
    url = f"https://tibia.fandom.com/wiki/{page_name}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    infobox = soup.find("table", {"class": "infobox"})
    details = {}
    if infobox:
        for row in infobox.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].get_text(strip=True).lower()
                val = cols[1].get_text(strip=True)
                details[key] = val
    return details

async def insert_monster(conn, name, level, health, attack_type, weaknesses, attributes, loots, comment):
    query = """
        INSERT INTO monsters (name, level, health, attack_type, weaknesses, attributes, loots, comment)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (name) DO UPDATE
        SET level = EXCLUDED.level,
            health = EXCLUDED.health,
            attack_type = EXCLUDED.attack_type,
            weaknesses = EXCLUDED.weaknesses,
            attributes = EXCLUDED.attributes,
            loots = EXCLUDED.loots,
            comment = EXCLUDED.comment;
    """
    await conn.execute("SET my.api_token = $1", API_TOKEN)
    await conn.execute(query, name, level, health, attack_type, weaknesses, attributes, loots, comment)

# =========================
# Funções para ITENS
# =========================
def get_items_list():
    url = "https://tibia.fandom.com/wiki/Category:Items"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for link in soup.select(".category-page__member-link"):
        items.append(link.get_text(strip=True))
    return items

def get_item_details(item_name):
    page_name = item_name.replace(" ", "_")
    url = f"https://tibia.fandom.com/wiki/{page_name}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    infobox = soup.find("table", {"class": "infobox"})
    details = {}
    if infobox:
        for row in infobox.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].get_text(strip=True).lower()
                val = cols[1].get_text(strip=True)
                details[key] = val
    return details

async def insert_item(conn, name, slot, vocation, level_required, attack, defense, magic, description, classification, tier):
    query = """
        INSERT INTO items (name, slot, vocation, level_required, attack, defense, magic, descrition, classification, tier)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (name) DO UPDATE
        SET slot = EXCLUDED.slot,
            vocation = EXCLUDED.vocation,
            level_required = EXCLUDED.level_required,
            attack = EXCLUDED.attack,
            defense = EXCLUDED.defense,
            magic = EXCLUDED.magic,
            descrition = EXCLUDED.descrition,
            classification = EXCLUDED.classification,
            tier = EXCLUDED.tier;
    """
    await conn.execute("SET my.api_token = $1", API_TOKEN)
    await conn.execute(query, name, slot, vocation, level_required, attack, defense, magic, description, classification, tier)

# =========================
# Função principal
# =========================
async def main():
    ssl_context = ssl.create_default_context()
    conn = await asyncpg.connect(DATABASE_URL, ssl=ssl_context)

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
            tier = 0  # Podemos mapear depois

            await insert_item(conn, item, slot, vocation, level_required, attack, defense, magic, description, classification, tier)
            print(f"✅ [ITEM] {item} atualizado.")

    await conn.close()
    print("🎯 Atualização concluída com sucesso!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
