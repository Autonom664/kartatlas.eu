# One-step rebuild: prep -> enrich -> inject into the page. usage: python -I build.py (run from pipeline/)
import subprocess, sys, os, shutil
here = os.path.dirname(os.path.abspath(__file__))
CCS = ['DE', 'AT', 'IT', 'CH', 'LI', 'DK', 'SE', 'NL', 'BE', 'FR']
py = sys.executable
subprocess.run([py, '-I', os.path.join(here, 'prep.py'), here, *CCS], check=True)
subprocess.run([py, '-I', os.path.join(here, 'enrich.py'), here], check=True)
h = open(os.path.join(here, 'template.html'), encoding='utf-8').read()
for k, f, e in [('TRACKS', 'tracks.json', '[]'), ('COUNTRIES', 'countries.json', '{}'), ('WORLD', 'geo/world.min.json', '{}'), ('RATES', 'rates_meta.json', '{}')]:
    d = open(os.path.join(here, f), encoding='utf-8').read().replace('</', '<\\/')
    t = '/*' + k + '*/' + e
    assert t in h, t
    h = h.replace(t, d)
out = os.path.join(here, '..', 'kart-atlas.html')
open(out, 'w', encoding='utf-8').write(h)
shutil.copy(os.path.join(here, 'tracks.json'), os.path.join(here, '..', 'kart-atlas.json'))
print('built', os.path.getsize(out), 'bytes')
