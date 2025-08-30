# ... (todo o código igual ao update_data.py até a função main)

async def main():
    ssl_context = ssl.create_default_context()
    conn = await asyncpg.connect(DATABASE_URL, ssl=ssl_context)

    # MONSTROS (apenas 3 para teste)
    print("🔄 [MONSTERS] Iniciando atualização de teste...")
    creatures = get_creatures_from_tibiadata()[:3]
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

    # ITENS (apenas 3 para teste)
    print("🔄 [ITEMS] Iniciando atualização de teste...")
    items = get_items_list()[:3]
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
    print("🎯 Teste concluído com sucesso!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
