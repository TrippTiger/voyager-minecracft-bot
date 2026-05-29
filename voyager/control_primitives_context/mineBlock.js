// Mine 3 cobblestone: mineBlock(bot, "stone", 3);
// Note: ore blocks are filtered to only exposed faces — bot cannot x-ray detect buried ores.
async function mineBlock(bot, name, count = 1) {
    const oreTypes = [
        "coal_ore","iron_ore","gold_ore","diamond_ore","emerald_ore",
        "lapis_ore","redstone_ore","copper_ore","deepslate_coal_ore",
        "deepslate_iron_ore","deepslate_gold_ore","deepslate_diamond_ore",
        "deepslate_emerald_ore","deepslate_lapis_ore","deepslate_redstone_ore",
        "deepslate_copper_ore","nether_gold_ore","nether_quartz_ore","ancient_debris",
    ];
    function isExposed(pos) {
        const offsets = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
        return offsets.some(([dx,dy,dz]) => {
            const b = bot.blockAt(pos.offset(dx,dy,dz));
            return !b || b.name === "air" || b.name === "cave_air" || b.boundingBox === "empty";
        });
    }
    let rawBlocks = bot.findBlocks({
        matching: (block) => block.name === name,
        maxDistance: 32,
        count: count * 4,
    });
    const blocks = oreTypes.includes(name) ? rawBlocks.filter(isExposed) : rawBlocks;
    const targets = [];
    for (let i = 0; i < Math.min(blocks.length, count); i++) {
        targets.push(bot.blockAt(blocks[i]));
    }
    await bot.collectBlock.collect(targets, { ignoreNoPath: true });
}
