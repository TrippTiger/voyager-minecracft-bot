async function mineBlock(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        throw new Error(`name for mineBlock must be a string`);
    }
    if (typeof count !== "number") {
        throw new Error(`count for mineBlock must be a number`);
    }
    const blockByName = mcData.blocksByName[name];
    if (!blockByName) {
        throw new Error(`No block named ${name}`);
    }
    const oreTypes = [
        "coal_ore","iron_ore","gold_ore","diamond_ore","emerald_ore",
        "lapis_ore","redstone_ore","copper_ore","nether_gold_ore",
        "nether_quartz_ore","ancient_debris","deepslate_coal_ore",
        "deepslate_iron_ore","deepslate_gold_ore","deepslate_diamond_ore",
        "deepslate_emerald_ore","deepslate_lapis_ore","deepslate_redstone_ore",
        "deepslate_copper_ore",
    ];
    const isOre = oreTypes.includes(name);

    function isExposed(pos) {
        const offsets = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
        return offsets.some(([dx,dy,dz]) => {
            const b = bot.blockAt(pos.offset(dx,dy,dz));
            return !b || b.name === "air" || b.name === "cave_air" || b.boundingBox === "empty";
        });
    }

    let rawBlocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 32,
        count: 1024,
    });
    const blocks = isOre ? rawBlocks.filter(isExposed) : rawBlocks;
    if (blocks.length === 0) {
        bot.chat(`No ${name} nearby, please explore first`);
        _mineBlockFailCount++;
        if (_mineBlockFailCount > 10) {
            throw new Error(
                "mineBlock failed too many times, make sure you explore before calling mineBlock"
            );
        }
        return;
    }
    const targets = [];
    for (let i = 0; i < blocks.length; i++) {
        targets.push(bot.blockAt(blocks[i]));
    }
    await bot.collectBlock.collect(targets, {
        ignoreNoPath: true,
        count: count,
    });
    bot.save(`${name}_mined`);
}
