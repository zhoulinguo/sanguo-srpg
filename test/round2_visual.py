from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
out = root.parent / 'sanguo-srpg-round2-captures'
out.mkdir(parents=True, exist_ok=True)
errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 960}, device_scale_factor=1)
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.goto((root / 'index.html').as_uri())
    page.wait_for_selector('#startBtn')
    page.evaluate("""() => {
      selectCampaign(CAMP_ZHAOYUN);
      roster=[];bag={...activeCamp.bag};gold=500;ensureRoster();
      document.getElementById('overlay').classList.add('hidden');
      openPrep(0);
      document.querySelector('.prepTab[data-tab="deploy"]').click();
    }""")
    page.wait_for_timeout(700)
    page.screenshot(path=str(out / 'deployment_board.png'))

    page.evaluate("""() => {
      const party=deploymentParty(0);
      party[0].promoted='龙骧骑';
      party[1].promoted='仁德主君';party[1].awakened='昭烈天命';
      party[2].promoted='武圣';party[2].awakened='青龙武神';party[2].rb=3;
      document.getElementById('prep').classList.add('hidden');
      document.getElementById('overlay').classList.add('hidden');
      startChapter(0);
      battleTheme=BATTLE_THEMES.rift;renderBase();
      fastMode='blitz';renderFastBtn();
      document.getElementById('banner').style.display='none';
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=str(out / 'rift_career_stages.png'))
    if errors:
        raise AssertionError('Browser errors:\n' + '\n'.join(errors))
    print('[ROUND2_VISUAL_PASS]', out)
    browser.close()
