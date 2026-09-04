from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.goto((root / 'index.html').as_uri())
    page.wait_for_selector('#startBtn')

    contract = page.evaluate("""async () => {
      const ok = (value, message) => { if (!value) throw new Error(message); };

      const cav = U({name:'骑',cls:'骑兵',kind:'cav',mounted:true,x:0,y:0,atk:30,def:10,hp:100});
      const inf = U({name:'步',cls:'先锋',kind:'vanguard',x:1,y:0,atk:30,def:10,hp:100});
      const archer = U({name:'弓',cls:'弓手',kind:'archer',x:2,y:0,atk:30,def:10,hp:100,rngMin:2,rngMax:2});
      const spear = U({name:'枪',cls:'枪兵',kind:'spear',x:3,y:0,atk:30,def:10,hp:100});
      ok(advInfo(cav,inf).mult === 1.15, 'cavalry must counter infantry');
      ok(advInfo(inf,archer).mult === 1.15, 'infantry must counter archers');
      ok(advInfo(archer,cav).mult === 1.15, 'archers must counter cavalry');
      ok(advInfo(spear,cav).mult === 1.2, 'spears must keep anti-cavalry specialty');

      const raw = JSON.stringify({name:'赵云', chapter:'长坂坡', emoji:'⚔️', nested:{n:7}});
      const code = portEncode(raw);
      ok(code.startsWith('SGL2'), 'new save codes must use SGL2');
      ok(portDecode(code) === raw, 'SGL2 Unicode round trip failed');

      const snap = {units:[{name:'赵云'}], bag:{}, forgeBag:{}, forge:{}, bondExp:{}, chains:{}, cargo:{}, fort:{}, dao:0, gold:0};
      const normalized = normalizeCampaignSave({ver:3,camp:'zhaoyun',chap:0,snap});
      ok(normalized && normalized.ver === SAVE_VER, 'compatible older save was rejected');
      ok(normalized.snap.gold === 0 && normalized.snap.dao === 0, 'zero values were overwritten');
      ok(normalized.snap.goodTrend && typeof normalized.snap.goodTrend === 'object', 'missing trend was not normalized');

      const battle = normalizeBattleSave({ver:3,chap:0,units:[{name:'赵云',x:1,y:1}],snap:{goodTrend:{silk:1.5}}});
      ok(battle && battle.goodTrend.silk === 1.5, 'battle trend fallback failed');
      ok(battle.commandPts === 2, 'older battle command default failed');

      ok(sceneThemeFor({godArc:true,map:['...']}).name==='时裂神域', 'god arc theme routing failed');
      ok(sceneThemeFor({weather:'snow',map:['...']}).name==='霜天冻土', 'snow theme routing failed');
      ok(sceneThemeFor({barrels:[[1,1],[2,2]],map:['...'],title:'战场'}).name==='赤焰焦土', 'ember theme routing failed');
      ok(sceneThemeFor({map:['ccc'],title:'普通营寨'}).name==='苍岚原野', 'ordinary chapters must preserve the original bright battlefield');
      ok(sceneThemeFor({theme:'siege',map:['...']}).name==='百垒攻城', 'explicit chapter theme routing failed');
      const model=U({name:'模型测试',side:'P',kind:'cav',x:0,y:0,hp:100});
      const basePalette=pal(model).armor;
      model.promoted='龙骧骑';const promotedPalette=pal(model).armor;
      model.awakened='武神';const awakenedPalette=pal(model).armor;
      model.rb=1;const rebornPalette=pal(model).armor;
      ok(new Set([basePalette,promotedPalette,awakenedPalette,rebornPalette]).size===1, 'career stages must preserve the original detailed model palette');
      const drawSource=drawUnitSprite.toString();
      ok(drawSource.includes('SPRITES[u.kind]')&&drawSource.includes('drawEvolutionFx'), 'career FX must wrap, not replace, the detailed class model');
      ok(visualStage(model)===3&&stageLabel(model).includes('转生'), 'rebirth visual stage failed');
      const oldSpeed=fastMode;fastMode='blitz';
      ok(spd()===6&&fxCount(22)<10, 'blitz speed or FX density failed');
      renderFastBtn();
      ok(document.getElementById('fastBtn').textContent==='极 速', 'speed label must not claim an unverified numeric multiplier');
      banner('极速测试');
      await new Promise(r=>setTimeout(r,300));
      ok(document.getElementById('banner').style.display==='none', 'banner lifecycle did not follow blitz speed');
      fastMode=oldSpeed;
      renderFastBtn();

      const savedUnits=units,savedCommand=commandPts,savedSelected=selected,savedState=state;
      const menuHero=U({name:'菜单测试',side:'P',x:0,y:0,hp:100,atk:30,def:10});
      const menuEnemy=U({name:'菜单靶',side:'E',x:1,y:0,hp:100,atk:20,def:10});
      units=[menuHero,menuEnemy];selected=menuHero;commandPts=0;showMenu(menuHero);
      ok(!document.querySelector('#menu [data-act="commandbreak"]'), 'unavailable command break must not clutter every action menu');
      commandPts=3;showMenu(menuHero);
      ok(!!document.querySelector('#menu [data-act="commandbreak"]'), 'available command break entry was hidden');
      hideMenu();units=savedUnits;commandPts=savedCommand;selected=savedSelected;state=savedState;

      const statusUnit = U({name:'状态测试',x:0,y:0,hp:100});
      statusUnit.status=[{k:'burn',t:2},{k:'poison',t:2},{k:'slow',t:2},{k:'rally',t:2},{k:'stun',t:1}];
      cleanseCurable(statusUnit);
      ok(!hasStatus(statusUnit,'burn') && !hasStatus(statusUnit,'poison'), 'curable DOT was not removed');
      ok(hasStatus(statusUnit,'slow') && hasStatus(statusUnit,'rally') && hasStatus(statusUnit,'stun'), 'cleanse removed tactical statuses');
      addStatus(statusUnit,'seal',2);
      ok(!canHeal(statusUnit), 'seal must block healing');

      const duelA=U({name:'甲',x:0,y:0,hp:10000,atk:20,def:20,side:'P'});
      const duelD=U({name:'乙',x:1,y:0,hp:10000,atk:20,def:20,side:'E'});
      units=[duelA,duelD]; selected=duelA; ended=false;
      const duelPromise=startDuel(duelA,duelD);
      duelPick('atk');
      duelPick('def');
      await new Promise(r=>setTimeout(r,30));
      ok(duelState && duelState.round===1, 'duel double input advanced multiple rounds');
      await new Promise(r=>setTimeout(r,180));
      await duelPick('def');
      await duelPick('brk');
      await duelPromise;
      ok(duelState===null && duelResolver===null, 'duel promise did not resolve cleanly');

      return {codeLength: code.length, saveVersion: SAVE_VER};
    }""")

    page.evaluate("""() => {
      selectCampaign(CAMP_ZHAOYUN);
      roster=[];bag={...activeCamp.bag};gold=500;ensureRoster();
      openPrep(0);
      const slots=[...document.querySelectorAll('#deployBoard [data-dslot]')];
      if(slots.length<2)throw new Error('deployment board did not render real spawn slots');
      if(document.querySelectorAll('#deployBoard .deployTerrain').length!==CHAPTERS[0].map.length*CHAPTERS[0].map[0].length)throw new Error('deployment board did not render the real chapter map');
      if(document.querySelectorAll('#deployBoard canvas[data-deploy-unit]').length!==slots.length)throw new Error('deployment board did not preserve detailed officer models');
      if(!document.querySelector('#deployBoard .deployEnemy'))throw new Error('deployment board omitted enemy direction preview');
      const before=syncDeploymentOrder(0).slice();
      slots[0].click();document.querySelectorAll('#deployBoard [data-dslot]')[1].click();
      const swapped=syncDeploymentOrder(0).slice();
      if(swapped[0]!==before[1]||swapped[1]!==before[0])throw new Error('click-to-swap deployment failed');
      const snapshot=snapshotRoster();
      if(!snapshot.deployments||!snapshot.deployments[deploymentKey(0)])throw new Error('deployment was not persisted in roster snapshot');
      window.__expectedDeployment=swapped;
      document.getElementById('overlay').classList.add('hidden');
      document.getElementById('prep').classList.add('hidden');
      startChapter(0);
    }""")
    page.wait_for_function("document.getElementById('commandTxt').textContent === '2/5'")
    chapter = page.evaluate("""async () => {
      const ok=(v,m)=>{if(!v)throw new Error(m);};
      ok(window.__expectedDeployment.every((name,i)=>{
        const u=units.find(x=>x.name===name), sp=CHAPTERS[0].spawns[i];
        return u&&u.x===sp[0]&&u.y===sp[1];
      }), 'battle did not honor deployment order');
      ok(battleTheme&&battleTheme===sceneThemeFor(CHAPTERS[0],0), 'chapter theme was not activated');
      const attacker=alive('P')[0], target=alive('E').find(e=>!e.boss);
      const base=dmgRange(attacker,target);
      attacker.commandBreak=true;
      const broken=dmgRange(attacker,target);
      attacker.commandBreak=false;
      ok(broken[0]>=base[0]&&broken[1]>=base[1], 'command break did not improve damage');

      const caster=U({name:'军师测试',cls:'军师',kind:'adv',side:'P',leader:true,x:target.x-1,y:target.y,int:40,mp:99,hp:200});
      const spellTarget=U({name:'策略靶',cls:'贼兵',kind:'brig',side:'E',x:target.x,y:target.y,hp:999,def:18});
      const oldUnits=units;units=[caster,spellTarget];
      const preview=strategyPreview(caster,spellTarget,'poison');
      const before=spellTarget.hp;
      await doStrategy(caster,'poison',spellTarget);
      ok(before-spellTarget.hp===preview.dmg, 'strategy preview and settlement diverged');
      ok(hasStatus(spellTarget,'poison'), 'strategy status was not applied');
      units=oldUnits;

      const stunned=alive('E')[0];stunned.status=[{k:'stun',t:1}];
      await tickStatus('E');
      ok(hasStatus(stunned,'stun')&&stunned.status.find(s=>s.k==='stun').t===1, 'stun expired before action gate');
      stunned.status=[];

      attacker.stunTurns=1;attacker.moleTurns=2;attacker._legendKills=2;
      const payload=battlePayload();
      const saved=payload.units.find(u=>u.name===attacker.name);
      ok(saved.stunTurns===1&&saved.moleTurns===2&&saved._legendKills===2, 'runtime battle fields missing');
      ok(payload.commandPts===commandPts&&payload.goodTrend, 'battle-wide fields missing');

      return {
        command: commandPts,
        playerCount: alive('P').filter(u=>!u.npc).length,
        enemyCount: alive('E').length,
        threats: buildThreatMap().size,
        baseDamage: base,
        breakDamage: broken,
        strategyDamage: preview.dmg,
        deployment: window.__expectedDeployment,
        theme: battleTheme.name,
        endText: document.getElementById('endTurn').textContent
      };
    }""")
    assert chapter['command'] == 2
    assert chapter['playerCount'] > 0 and chapter['enemyCount'] > 0 and chapter['threats'] > 0

    page.click('#endTurn')
    page.wait_for_timeout(80)
    confirmed = page.evaluate("() => ({phase,state,text:document.getElementById('endTurn').textContent})")
    assert confirmed['phase'] == 'P'
    assert confirmed['state'] == 'idle'
    assert confirmed['text'] == '再按结束'

    if errors:
        raise AssertionError('Browser errors:\n' + '\n'.join(errors))
    print('[SMOKE_PASS]', {'contract': contract, 'chapter': chapter, 'endTurnGuard': confirmed})
    browser.close()
