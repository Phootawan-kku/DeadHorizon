/* Dead Horizon shared gameplay data.
 * Source of truth for the playable game and the public website.
 * Keep this file dependency-free so it can be loaded directly by the browser.
 */
window.DEAD_HORIZON_DATA = Object.freeze({
  version: 2,
  weapons: {
    knife:{image:'assets/weapons/knife.png',n:'Combat Knife',cat:'melee',rarity:0,melee:1,dmg:24,rate:.32,range:52,reload:.1,weight:1,passive:'fast melee',desc:'Fast close-range starter weapon.'},
    bat:{image:'assets/weapons/bat.png',n:'Baseball Bat',cat:'melee',rarity:0,melee:1,dmg:38,rate:.58,range:62,reload:.1,weight:2,knock:360,passive:'heavy knockback',desc:'Heavy melee weapon with strong knockback.'},
    axe:{image:'assets/weapons/axe.png',n:'Fire Axe',cat:'melee',rarity:1,melee:1,dmg:68,rate:.9,range:58,reload:.1,weight:3,knock:480,passive:'armor breaker',desc:'Slow but powerful melee weapon.'},
    machete:{image:'assets/weapons/machete.png',n:'Machete',cat:'melee',rarity:1,melee:1,dmg:45,rate:.48,range:58,reload:.1,weight:2,knock:300,desc:'Fast slashing melee weapon.'},
    pistol:{image:'assets/weapons/pistol.png',icon:'assets/weapons/pistol_icon.png',n:'Pistol',cat:'pistol',rarity:0,dmg:16,rate:.28,mag:12,reload:1.1,spd:900,spread:.03,pel:1,life:.9,ammo:'ammo',desc:'Reliable starting sidearm.'},
    revolver:{image:'assets/weapons/revolver.png',n:'Revolver',cat:'pistol',rarity:1,dmg:38,rate:.65,mag:6,reload:1.45,spd:980,spread:.018,pel:1,life:1,ammo:'ammo',crit:.18,desc:'Slow, accurate and hard hitting.'},
    burst:{image:'assets/weapons/burst.png',n:'Burst Pistol',cat:'pistol',rarity:1,dmg:12,rate:.42,mag:15,reload:1.2,spd:920,spread:.05,pel:3,life:.9,ammo:'ammo',desc:'Three-round burst sidearm.'},
    heavy:{image:'assets/weapons/heavy.png',n:'Heavy Pistol',cat:'pistol',rarity:2,dmg:29,rate:.4,mag:8,reload:1.35,spd:960,spread:.025,pel:1,life:1,ammo:'ammo',knock:170,desc:'High-impact pistol with extra knockback.'},
    smg:{image:'assets/weapons/smg.png',n:'SMG',cat:'smg',rarity:0,dmg:9,rate:.09,mag:30,reload:1.5,spd:950,spread:.08,pel:1,life:.8,auto:1,ammo:'ammo',desc:'Fast automatic weapon.'},
    tactical:{image:'assets/weapons/tactical.png',n:'Tactical SMG',cat:'smg',rarity:1,dmg:11,rate:.075,mag:36,reload:1.35,spd:1000,spread:.055,pel:1,life:.85,auto:1,ammo:'ammo',desc:'More accurate automatic SMG.'},
    machine:{image:'assets/weapons/machine.png',n:'Machine Pistol',cat:'smg',rarity:2,dmg:7,rate:.055,mag:42,reload:1.55,spd:930,spread:.12,pel:1,life:.7,auto:1,ammo:'ammo',desc:'Extremely fast but inaccurate automatic sidearm.'},
    shotgun:{image:'assets/weapons/shotgun.png',icon:'assets/weapons/shotgun_icon.png',n:'Pump Shotgun',cat:'shotgun',rarity:0,dmg:9,rate:.8,mag:6,reload:1.8,spd:800,spread:.18,pel:6,life:.35,ammo:'ammo',desc:'Six-pellet close-range shotgun.'},
    double:{image:'assets/weapons/double.png',icon:'assets/weapons/double_icon.png',n:'Double Barrel',cat:'shotgun',rarity:1,dmg:13,rate:1.0,mag:2,reload:1.4,spd:830,spread:.2,pel:10,life:.3,ammo:'ammo',knock:160,desc:'Two-shell high-damage burst shotgun.'},
    autoShot:{image:'assets/weapons/autoShot.png',n:'Auto Shotgun',cat:'shotgun',rarity:2,dmg:7,rate:.42,mag:10,reload:2.0,spd:780,spread:.2,pel:7,life:.3,ammo:'ammo',auto:1,desc:'Automatic shotgun for sustained close-range fire.'},
    rifle:{image:'assets/weapons/rifle.png',icon:'assets/weapons/rifle_icon.png',n:'Assault Rifle',cat:'rifle',rarity:1,dmg:18,rate:.14,mag:30,reload:1.65,spd:1150,spread:.035,pel:1,life:1.1,auto:1,ammo:'ammo',desc:'Balanced automatic rifle.'},
    tacticalRifle:{image:'assets/weapons/tacticalRifle.png',n:'Tactical Rifle',cat:'rifle',rarity:2,dmg:25,rate:.2,mag:24,reload:1.5,spd:1250,spread:.018,pel:1,life:1.2,ammo:'ammo',crit:.12,desc:'Accurate semi-automatic rifle.'},
    sniper:{image:'assets/weapons/sniper.png',n:'Sniper Rifle',cat:'rifle',rarity:3,dmg:105,rate:1.2,mag:5,reload:2.1,spd:1800,spread:.006,pel:1,life:1.8,ammo:'ammo',crit:.25,knock:300,desc:'Very high single-shot damage.'},
    launcher:{image:'assets/weapons/launcher.png',n:'Grenade Launcher',cat:'heavy',rarity:3,dmg:85,rate:1.1,mag:4,reload:2.2,spd:620,spread:.025,pel:1,life:2,ammo:'grenade',explosive:1,desc:'Fires explosive projectiles.'},
    flamethrower:{image:'assets/weapons/flamethrower.png',n:'Flamethrower',cat:'special',rarity:3,dmg:7,rate:.055,mag:60,reload:2.3,spd:500,spread:.12,pel:1,life:.45,auto:1,ammo:'fuel',burn:1,desc:'Short-range continuous fire weapon.'},
    crossbow:{image:'assets/weapons/crossbow.png',n:'Crossbow',cat:'special',rarity:2,dmg:72,rate:1.0,mag:1,reload:1.3,spd:1050,spread:.008,pel:1,life:1.5,ammo:'part',crit:.2,desc:'Slow silent-style projectile weapon.'}
  },
  enemies: {
    /* Restored from the project's original V3 enemy loot tables. These use the
     * existing item IDs below; no second item/material system is introduced. */
    normal:{image:'assets/enemies/normal.png',n:'Walker',hp:40,sp:55,dmg:8,w:20,h:38,col:'#5e8a4e',drops:[['scrap',.5,1,2],['cloth',.35,1,2],['bone',.3,1,1],['ammo',.45,3,8],['meat',.15,1,1],['metal',.1,1,2],['chemicals',.04,1,1]],desc:'Standard undead with balanced health and movement.'},
    fast:{image:'assets/enemies/fast.png',n:'Runner',hp:28,sp:125,dmg:6,w:18,h:34,col:'#b0a640',jump:1,drops:[['scrap',.6,1,3],['ammo',.5,4,10],['part',.1,1,1],['electronics',.12,1,1]],desc:'Fast, aggressive and able to jump.'},
    tank:{image:'assets/enemies/tank.png',n:'Tank',hp:220,sp:34,dmg:22,w:32,h:54,col:'#7a4a6a',drops:[['scrap',1,3,6],['bone',.6,1,3],['part',.4,1,2],['ammo',.7,8,16],['metal',.8,3,6],['fuel',.2,1,2]],desc:'High health and heavy damage.'},
    spitter:{image:'assets/enemies/spitter.png',n:'Spitter',hp:62,sp:48,dmg:12,w:21,h:40,col:'#4b9b65',ranged:1,drops:[['ammo',.8,5,14],['cloth',.4,1,2],['part',.25,1,2],['chemicals',.4,1,2]],desc:'Keeps distance and launches corrosive projectiles.'},
    screamer:{image:'assets/enemies/screamer.png',n:'Screamer',hp:50,sp:62,dmg:5,w:20,h:42,col:'#d3a34d',scream:1,drops:[['electronics',.3,1,2]],desc:'Calls for additional pressure when nearby.'},
    exploder:{image:'assets/enemies/exploder.png',n:'Exploder',hp:48,sp:105,dmg:45,w:22,h:36,col:'#b34b3d',explode:1,drops:[['scrap',.7,1,4],['ammo',.5,3,10],['part',.25,1,2],['fuel',.5,1,3],['chemicals',.15,1,1]],desc:'Rushes the player and detonates at close range.'},
    armored:{image:'assets/enemies/armored.png',n:'Armored',hp:95,sp:42,dmg:15,w:24,h:42,col:'#5e6673',armor:45,drops:[['metal',.6,2,4]],desc:'Armor absorbs incoming damage first.'},
    crawler:{image:'assets/enemies/crawler.png',n:'Crawler',hp:32,sp:90,dmg:9,w:25,h:22,col:'#718d55',low:1,drops:[['metal',.2,1,2]],desc:'Low-profile enemy that moves quickly.'},
    leaper:{image:'assets/enemies/leaper.png',n:'Leaper',hp:70,sp:76,dmg:16,w:22,h:40,col:'#8f5a91',jump:1,leap:1,drops:[['electronics',.18,1,1]],desc:'Uses long jumps to close distance.'},
    brute:{image:'assets/enemies/brute.png',n:'Brute',hp:300,sp:30,dmg:35,w:38,h:58,col:'#88483d',knock:1,drops:[['metal',.5,2,4]],desc:'Slow heavy enemy with punishing attacks.'},
    swarm:{image:'assets/enemies/swarm.png',n:'Swarm',hp:18,sp:145,dmg:3,w:14,h:26,col:'#77704a',swarm:1,drops:[['chemicals',.06,1,1]],desc:'Small, fast late-wave attacker.'},
    mutant:{image:'assets/enemies/mutant.png',n:'Mutant',hp:180,sp:58,dmg:25,w:30,h:50,col:'#6e4d8c',mutant:1,drops:[['chemicals',.55,1,3]],desc:'High-health mutated threat.'},
    hunter:{image:'assets/enemies/hunter.png',n:'Hunter',hp:85,sp:150,dmg:13,w:20,h:38,col:'#3d826e',hunter:1,drops:[['electronics',.35,1,2]],desc:'Extremely fast tracker.'},
    boss:{image:'assets/enemies/boss.png',n:'Abomination',hp:1400,sp:28,dmg:42,w:62,h:82,col:'#8d2831',boss:1,drops:[['scrap',1,15,30],['part',1,4,8],['ammo',1,20,40],['medkit',1,1,2],['metal',1,8,14],['electronics',1,3,6],['chemicals',1,3,5],['fuel',1,3,6]],desc:'Boss encountered on every 10th wave.'}
  },
  recipes: [
    {out:'bandage',n:1,cost:{cloth:2},kind:'item'},
    {out:'medkit',n:1,cost:{cloth:4,chemicals:1,part:1},kind:'item'},
    {out:'ammo',n:12,cost:{scrap:3,bone:1},kind:'item'},
    {out:'grenade',n:1,cost:{scrap:5,chemicals:2,part:1},kind:'item'},
    {out:'shotgun',n:1,cost:{wood:5,stone:5,scrap:8},kind:'weapon'},
    {out:'smg',n:1,cost:{scrap:25,part:2,wood:4},kind:'weapon'},
    {out:'rifle',n:1,cost:{metal:10,part:4,electronics:2},kind:'weapon'},
    {out:'sniper',n:1,cost:{metal:16,part:6,electronics:4},kind:'weapon'},
    {out:'bat',n:1,cost:{wood:12,scrap:5},kind:'weapon'},
    {out:'axe',n:1,cost:{wood:8,metal:12,scrap:6},kind:'weapon'},
    {out:'machete',n:1,cost:{metal:10,part:2},kind:'weapon'},
    {out:'revolver',n:1,cost:{metal:12,part:3},kind:'weapon'},
    {out:'burst',n:1,cost:{metal:10,electronics:2,part:3},kind:'weapon'},
    {out:'heavy',n:1,cost:{metal:14,part:4},kind:'weapon'},
    {out:'tactical',n:1,cost:{metal:18,electronics:4,part:4},kind:'weapon'},
    {out:'machine',n:1,cost:{metal:20,electronics:5,part:5},kind:'weapon'},
    {out:'double',n:1,cost:{wood:8,metal:16,part:4},kind:'weapon'},
    {out:'autoShot',n:1,cost:{wood:12,metal:22,electronics:3,part:6},kind:'weapon'},
    {out:'tacticalRifle',n:1,cost:{metal:24,electronics:7,part:6},kind:'weapon'},
    {out:'launcher',n:1,cost:{metal:28,electronics:8,part:8,chemicals:4},kind:'weapon'},
    {out:'flamethrower',n:1,cost:{metal:26,electronics:10,part:7,fuel:6},kind:'weapon'},
    {out:'crossbow',n:1,cost:{wood:18,metal:8,part:6},kind:'weapon'}
  ],
  /* ===== Progression: levels, skills, talent trees and run perks =====
   * Everything a player can earn is expressed as "mods" (small numeric deltas keyed by modKeys).
   * game.html sums talents + skills + run perks into one table, so adding content here needs no code changes.
   * Mod meaning (all additive, 0 = no effect):
   *   dmg/ranged/melee +fraction damage · crit +chance · critMul +multiplier on crits (base x2) · reload/rate/meleeRate -fraction time
   *   spread -fraction · mag +fraction · ammoSave/pierce/freeHeal chance · speed +fraction · maxHp +flat · dr -fraction damage taken
   *   regen HP/s · invuln +seconds · heal +fraction · loot +fraction drop chance · lootQty +fraction quantity · gather +flat
   *   xp/coin +fraction · execute +fraction vs <30% HP · killHeal flat HP per kill · killSpeed +speed 2s after a kill
   *   berserk +fraction damage below 35% HP · blast +fraction explosion radius · waveHeal +fraction max HP on wave clear · undying lethal-hit saves per run */
  progression: {
    maxLevel: 40,
    xp: { base: 60, exp: 1.5 },            /* XP to leave level L = round(base * L^exp) */
    skillMax: 10,
    skillXp: { base: 80, exp: 1.5 },
    legacyXpPerKill: 10,                    /* old saves with no progression data are credited this much per past kill */
    talentTierStep: 4,                      /* tier N unlocks after (N-1)*step points are spent in that tree */
    perkWaves: { first: 2, every: 3, boss: 10 },
    modKeys: ['dmg','ranged','melee','crit','critMul','reload','rate','meleeRate','spread','mag','ammoSave','pierce','speed','maxHp','dr','regen','invuln','heal','freeHeal','loot','lootQty','gather','xp','coin','execute','killHeal','killSpeed','berserk','blast','waveHeal','undying'],
    skills: {
      marksman:{n:'MARKSMANSHIP',col:'#e0533d',train:'Kill with ranged weapons',per:{ranged:.02,crit:.005},perDesc:'+2% ranged damage, +0.5% crit chance',
        milestones:[{lv:5,mods:{mag:.10},desc:'+10% magazine size'},{lv:10,mods:{critMul:.25},desc:'+0.25x critical damage'}]},
      closeCombat:{n:'CLOSE COMBAT',col:'#e08a3d',train:'Kill with melee weapons',per:{melee:.03},perDesc:'+3% melee damage',
        milestones:[{lv:5,mods:{execute:.15},desc:'+15% damage to enemies below 30% HP'},{lv:10,mods:{meleeRate:.12},desc:'Melee attacks 12% faster'}]},
      scavenging:{n:'SCAVENGING',col:'#7fa36a',train:'Gather resources and collect loot',per:{loot:.02},perDesc:'+2% loot drop chance',
        milestones:[{lv:5,mods:{lootQty:.15},desc:'+15% loot quantity'},{lv:10,mods:{gather:1},desc:'+1 resource per gather'}]},
      medicine:{n:'FIELD MEDICINE',col:'#4cd9a0',train:'Use bandages and meat',per:{heal:.04},perDesc:'+4% healing',
        milestones:[{lv:5,mods:{freeHeal:.10},desc:'10% chance a heal is not consumed'},{lv:10,mods:{waveHeal:.10},desc:'+10% max HP restored on wave clear'}]},
      resilience:{n:'RESILIENCE',col:'#6fb7e8',train:'Take hits and survive waves',per:{maxHp:3},perDesc:'+3 max HP',
        milestones:[{lv:5,mods:{dr:.05},desc:'-5% damage taken'},{lv:10,mods:{invuln:.15},desc:'+0.15s invulnerability after a hit'}]}
    },
    trees: {
      gun:{n:'GUNSLINGER',col:'#e0533d',desc:'Accuracy, firepower and ammo economy.',nodes:[
        {id:'g_spread',tier:1,max:3,n:'Steady Hands',desc:'-6% spread per rank',mods:{spread:.06}},
        {id:'g_dmg',tier:1,max:3,n:'Trigger Discipline',desc:'+4% ranged damage per rank',mods:{ranged:.04}},
        {id:'g_reload',tier:2,max:3,n:'Fast Fingers',desc:'-7% reload time per rank',mods:{reload:.07}},
        {id:'g_mag',tier:2,max:3,n:'Deep Magazines',desc:'+8% magazine size per rank',mods:{mag:.08}},
        {id:'g_crit',tier:3,max:3,n:'Deadeye',desc:'+3% crit chance per rank',mods:{crit:.03}},
        {id:'g_save',tier:3,max:3,n:'Conservation',desc:'5% chance per rank a shot uses no ammo',mods:{ammoSave:.05}},
        {id:'g_pierce',tier:4,max:2,n:'Hot Lead',desc:'15% chance per rank bullets pierce an enemy',mods:{pierce:.15}},
        {id:'g_critdmg',tier:4,max:2,n:'Brutal Crits',desc:'+0.25x critical damage per rank',mods:{critMul:.25}},
        {id:'g_cap',tier:5,max:1,n:'Bullet Storm',desc:'Capstone: +15% fire rate, +10% damage',mods:{rate:.15,dmg:.10}}]},
      brawl:{n:'BRAWLER',col:'#e08a3d',desc:'Melee power, toughness and staying alive.',nodes:[
        {id:'b_hp',tier:1,max:3,n:'Conditioning',desc:'+10 max HP per rank',mods:{maxHp:10}},
        {id:'b_melee',tier:1,max:3,n:'Heavy Swings',desc:'+6% melee damage per rank',mods:{melee:.06}},
        {id:'b_dr',tier:2,max:3,n:'Thick Hide',desc:'-4% damage taken per rank',mods:{dr:.04}},
        {id:'b_inv',tier:2,max:3,n:'Quick Recovery',desc:'+0.08s invulnerability after a hit per rank',mods:{invuln:.08}},
        {id:'b_kh',tier:3,max:3,n:'Blood Rush',desc:'Heal 1 HP per kill per rank',mods:{killHeal:1}},
        {id:'b_rate',tier:3,max:3,n:'Relentless',desc:'Melee attacks 6% faster per rank',mods:{meleeRate:.06}},
        {id:'b_regen',tier:4,max:2,n:'Second Wind',desc:'+0.4 HP/s regeneration per rank',mods:{regen:.4}},
        {id:'b_exec',tier:4,max:2,n:'Executioner',desc:'+20% damage to enemies below 30% HP per rank',mods:{execute:.20}},
        {id:'b_cap',tier:5,max:1,n:'Undying',desc:'Capstone: once per run, survive a lethal hit at 35% HP',mods:{undying:1}}]},
      surv:{n:'SURVIVALIST',col:'#7fa36a',desc:'Loot, healing, speed and faster growth.',nodes:[
        {id:'s_loot',tier:1,max:3,n:'Forager',desc:'+8% loot drop chance per rank',mods:{loot:.08}},
        {id:'s_speed',tier:1,max:3,n:'Swift',desc:'+3% move speed per rank',mods:{speed:.03}},
        {id:'s_heal',tier:2,max:3,n:'Field Medic',desc:'+10% healing per rank',mods:{heal:.10}},
        {id:'s_gather',tier:2,max:3,n:'Efficient Gatherer',desc:'+1 resource per gather per rank',mods:{gather:1}},
        {id:'s_xp',tier:3,max:3,n:'Quick Study',desc:'+6% XP gained per rank',mods:{xp:.06}},
        {id:'s_qty',tier:3,max:3,n:'Scavenger',desc:'+10% loot quantity per rank',mods:{lootQty:.10}},
        {id:'s_free',tier:4,max:2,n:'Paramedic',desc:'12% chance per rank a heal is not consumed',mods:{freeHeal:.12}},
        {id:'s_coin',tier:4,max:2,n:'Cash Flow',desc:'+10% Horizon Coins per rank',mods:{coin:.10}},
        {id:'s_cap',tier:5,max:1,n:'Wasteland Legend',desc:'Capstone: +8% damage, +8% speed, +10% loot, XP and coins',mods:{dmg:.08,speed:.08,loot:.10,xp:.10,coin:.10}}]}
    },
    perks: [
      {id:'hollow',n:'Hollow Points',rarity:0,max:5,desc:'+8% damage',mods:{dmg:.08}},
      {id:'quickhands',n:'Quick Hands',rarity:0,max:3,desc:'-10% reload time',mods:{reload:.10}},
      {id:'thickskin',n:'Thick Skin',rarity:0,max:5,desc:'+15 max HP (and heals that much)',mods:{maxHp:15}},
      {id:'lightfeet',n:'Light Feet',rarity:0,max:3,desc:'+6% move speed',mods:{speed:.06}},
      {id:'stickyfingers',n:'Sticky Fingers',rarity:0,max:3,desc:'+12% loot drop chance',mods:{loot:.12}},
      {id:'deeppockets',n:'Deep Pockets',rarity:0,max:3,desc:'+10% magazine size',mods:{mag:.10}},
      {id:'steadyaim',n:'Steady Aim',rarity:0,max:3,desc:'-12% spread',mods:{spread:.12}},
      {id:'adrenaline',n:'Adrenaline',rarity:1,max:2,desc:'+25% move speed for 2s after a kill',mods:{killSpeed:.25}},
      {id:'scrounger',n:'Scrounger',rarity:1,max:2,desc:'+30% loot quantity',mods:{lootQty:.30}},
      {id:'fielddress',n:'Field Dressing',rarity:1,max:2,desc:'+30% healing, 15% chance a heal is free',mods:{heal:.30,freeHeal:.15}},
      {id:'executioner',n:'Executioner',rarity:1,max:2,desc:'+30% damage to enemies below 30% HP',mods:{execute:.30}},
      {id:'secondwind',n:'Second Wind',rarity:1,max:3,desc:'+0.5 HP/s regeneration',mods:{regen:.5}},
      {id:'bounty',n:'Bounty Hunter',rarity:1,max:2,desc:'+20% coins, +10% XP',mods:{coin:.20,xp:.10}},
      {id:'ghost',n:'Ghost Rounds',rarity:2,max:3,desc:'20% chance bullets pierce an enemy',mods:{pierce:.20}},
      {id:'ironwill',n:'Iron Will',rarity:2,max:3,desc:'-10% damage taken',mods:{dr:.10}},
      {id:'overclock',n:'Overclock',rarity:2,max:3,desc:'+10% fire rate',mods:{rate:.10}},
      {id:'bloodthirst',n:'Bloodthirst',rarity:2,max:2,desc:'Heal 2 HP per kill',mods:{killHeal:2}},
      {id:'demolition',n:'Demolitionist',rarity:2,max:2,desc:'+30% explosion radius and damage',mods:{blast:.30}},
      {id:'berserker',n:'Berserker',rarity:3,max:1,desc:'+40% damage while below 35% HP',mods:{berserk:.40}},
      {id:'luckyseven',n:'Lucky Seven',rarity:3,max:1,desc:'+15% crit chance, +0.5x critical damage',mods:{crit:.15,critMul:.5}},
      {id:'adaptive',n:'Adaptive Armor',rarity:3,max:1,desc:'+25 max HP, -8% damage taken',mods:{maxHp:25,dr:.08}},
      {id:'glasscannon',n:'Glass Cannon',rarity:3,max:1,desc:'+35% damage, but +15% damage taken',mods:{dmg:.35,dr:-.15}}
    ]
  },
  controls: [
    ['A / D','MOVE','Move the survivor left or right.'],
    ['W / SPACE','JUMP','Jump over threats and terrain.'],
    ['MOUSE','AIM / FIRE','Aim with the cursor and fire with the mouse button.'],
    ['1–6','WEAPONS','Equip the unlocked weapons currently shown in the hotbar.'],
    ['R','RELOAD','Reload the equipped ranged weapon.'],
    ['E','GATHER','Harvest nearby trees and rocks.'],
    ['H','HEAL','Use a bandage or meat when available.'],
    ['TAB','INVENTORY','Open inventory and crafting.'],
    ['O','META','Open profile, armory, cosmetics, collection and progression. The game pauses while it is open.'],
    ['K','TALENTS','Open the talent trees, skills and perks. Spend one talent point per level. The game pauses while it is open.'],
    ['P','POINTER LOCK (OPTIONAL)','Toggle relative pointer aiming. Normal trackpad/mouse aiming does not require it.'],
    ['ESC','PAUSE','Pause the run while in the game.'],
    ['F','EFFECTS','Toggle screen effects.'],
    ['M','MUTE','Toggle all sound on / off.']
  ],
  hotbarLimit: 6,
  startingWeapons: ['knife','pistol']
});
