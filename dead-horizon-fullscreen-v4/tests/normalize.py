import re, json, sys
T = dict(shot_sniper=.75,shot_shotgun=.7,shot_launcher=.6,shot_rifle=.55,shot_pistol=.5,shot_crossbow=.45,shot_smg=.42,shot_flame=.25,
 melee_hit=.4,melee_swing=.25,mag_out=.25,mag_in=.3,rack=.3,shell_in=.2,pump=.35,empty=.25,switch=.2,
 step_dirt=.18,step_grass=.14,step_concrete=.2,step_metal=.2,jump=.2,land=.4,hurt=.5,heal=.3,pickup=.25,coin=.2,chop=.4,mine=.3,
 ui_hover=.08,ui_click=.2,ui_ok=.25,ui_fail=.22,ui_open=.2,ui_close=.2,craft=.35,
 z_groan=.3,z_rasp=.25,z_attack=.35,z_hit=.3,z_death=.35,screech=.35,boss_roar=.6,explosion=.8,spit=.3,armor_hit=.3,wave=.3,
 amb_creak=.1,amb_gust=.12,amb_far=.15)
res = {r['name']:r for r in json.load(open('/home/claude/res_audio_levels.json'))}
P='/home/claude/work/dead-horizon-fullscreen-v4/audio.js'
s=open(P,encoding='utf-8').read()
for n,t in T.items():
    pk=res[n]['peak']; k=t/max(pk,1e-4)
    m=re.search(r'(\n    %s: \{ vol: )([\d.]+)'%n, s); assert m,n
    s=s[:m.start(2)]+('%.3f'%(float(m.group(2))*k))+s[m.end(2):]
open(P,'w',encoding='utf-8').write(s); print('normalized',len(T))
