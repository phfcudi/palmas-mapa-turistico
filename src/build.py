import base64, io, json, math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import SRC as SRC_DIR, TILES_DIR, RAW, PROC, DIST
from PIL import Image, ImageEnhance

UP = str(TILES_DIR / 'tile_%d.png')
# x, y, largura, altura de cada captura no SVG original (unidades do viewBox)
TILES = {1:(62921.26,1751.24,28314.36,66181.52), 2:(60145.16,67406.01,28446.66,66155.06),
         3:(82466.11,67534.97,28526.06,66207.98), 4:(106155.16,57161.66,28499.6,66049.2),
         5:(37300.07,3600.09,28473.14,66366.76), 6:(20603.62,2965.35,28552.52,66234.44),
         7:(-911.76,0.06,28473.14,66234.44)}
REF = 1110.0  # largura de referência (px) usada ao traçar as coordenadas

imgs = []
for i, (x, y, w, h) in TILES.items():
    im = Image.open(UP % i).convert('RGB'); buf = io.BytesIO()
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.34)).enhance(1.05)  # cores mais vivas, estilo mapa turístico
    im.save(buf, 'WEBP', quality=84, method=5)
    uri = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    imgs.append(f'<clipPath id="c{i}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
                f'<g clip-path="url(#c{i})"><image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/></g>')

def u(t, px, py):
    x, y, w, h = TILES[t]; k = w / REF
    return [round(x + px * k), round(y + py * k)]
def A(t, pts): return ('a', t, pts)
def L(t, pts): return ('l', t, pts)

CATS = {'t': 'Pontos turísticos', 'b': 'Bairros e localidades', 'p': 'Pontos de interesse', 'i': 'Infraestrutura', 'n': 'Natureza e água', 'v': 'Vias e ferrovia', 'q': 'Quadras do Plano Diretor', 'l': 'Lazer e esportes'}
R = []
def add(id, n, c, d, parts, s=None, f=None): R.append(dict(id=id, n=n, c=c, d=d, parts=parts, s=s, f=f, o=None))

# ---------- natureza e água ----------
add('lago-palmas', 'Lago de Palmas (Rio Tocantins)', 'n',
    'Reservatório formado no Rio Tocantins pela usina hidrelétrica Luís Eduardo Magalhães (Lajeado). Banha toda a orla oeste de Palmas, separa a capital de Luzimangues e Porto Nacional e é atravessado pela TO-080.',
    [A(5, [(510,0),(1111,0),(1111,2576),(262,2576),(330,2300),(365,2050),(330,1750),(290,1450),(290,1100),(285,880),(275,700),(300,620),(420,330),(455,240),(415,165)]),
     A(1, [(0,0),(130,0),(165,120),(180,270),(182,600),(210,730),(178,850),(165,960),(150,1060),(120,1200),(95,1450),(75,1650),(60,1900),(40,2000),(0,2040)])],
    s='Lago de Palmas', f=7)
add('mata-aeroporto', 'Mata e áreas verdes ao sul do Plano Diretor', 'n',
    'Grande mancha de vegetação entre o fim do Plano Diretor e a região do aeroporto, junto à margem do lago.',
    [A(1, [(15,2060),(100,2040),(250,2080),(400,2150),(560,2200),(625,2260),(625,2576),(10,2576)]),
     A(2, [(275,0),(725,0),(725,250),(300,250)])], s='Mata e áreas verdes', f=9)
add('parque-pds', 'Parque do lago (Plano Diretor Sul)', 'p',
    'Grande área verde com lago no Plano Diretor Sul, a leste do eixo da Av. Teotônio Segurado, usada para lazer, caminhadas e esportes. Nome e limites aproximados: provavelmente corresponde ao Parque Cesamar, confira o nome oficial.',
    [A(1, [(560,1175),(690,1170),(800,1190),(805,1360),(720,1360),(640,1350),(570,1280)])], s='Parque do lago')

# ---------- Palmas: Plano Diretor ----------
add('pdn-oeste', 'Plano Diretor Norte — ARNO', 'b',
    'Setor residencial a noroeste da Praça dos Girassóis, a oeste da Av. Teotônio Segurado. As quadras usam a sigla ARNO (Área Residencial Norte Oeste), e a malha segue o desenho de avenidas LO (leste-oeste) e NS (norte-sul).',
    [A(1, [(205,745),(250,700),(310,650),(430,572),(520,552),(520,975),(215,975),(210,880),(205,800)])], s='ARNO')
add('pdn-leste', 'Plano Diretor Norte — ARNE', 'b',
    'Setor residencial a nordeste da Praça dos Girassóis, a leste do eixo da Av. Teotônio Segurado e junto à BR-010. As quadras usam a sigla ARNE (Área Residencial Norte Leste).',
    [A(1, [(520,552),(560,548),(660,585),(720,655),(780,668),(930,668),(930,975),(520,975)])], s='ARNE')
add('pds-oeste', 'Plano Diretor Sul — ARSO', 'b',
    'Setor residencial ao sul da Praça dos Girassóis, a oeste da Av. Teotônio Segurado, voltado para a orla do lago. Sigla ARSO (Área Residencial Sul Oeste).',
    [A(1, [(210,990),(520,990),(520,2110),(345,2110),(345,1700),(290,1700),(290,1540),(150,1540),(150,1300),(210,1150)])], s='ARSO')
add('pds-leste', 'Plano Diretor Sul — ARSE', 'b',
    'Setor residencial ao sul da Praça dos Girassóis, a leste da Av. Teotônio Segurado, até a BR-010. Sigla ARSE (Área Residencial Sul Leste).',
    [A(1, [(527,1040),(870,1040),(880,1100),(830,1200),(790,1330),(780,1700),(790,1860),(800,1960),(650,2120),(527,2120)])], s='ARSE')
add('praca-girassois', 'Praça dos Girassóis', 'p',
    'Centro cívico de Palmas e uma das maiores praças do país. Abriga o Palácio Araguaia, sede do governo estadual, e fica no cruzamento do eixo da Av. Teotônio Segurado com a TO-080.',
    [A(1, [(478,932),(563,932),(563,1035),(478,1035)])])
add('uft', 'Universidade Federal do Tocantins (campus Palmas)', 'p',
    'Campus de Palmas da UFT, na orla do lago, junto à Av. NS-15, no extremo oeste do Plano Diretor Norte.',
    [A(1, [(172,862),(258,862),(258,945),(172,945)])], s='UFT')
add('teotonio', 'Avenida Teotônio Segurado', 'v',
    'Eixo central de Palmas, corre de norte a sul e divide o Plano Diretor em lados leste e oeste. Concentra o trânsito principal, o comércio e os serviços da capital.',
    [L(1, [(518,835),(520,975),(522,1400),(525,1900),(528,2100),(540,2200),(580,2290),(612,2400),(615,2576)])])

# ---------- infraestrutura ----------
add('aeroporto', 'Aeroporto de Palmas — Brigadeiro Lysias Rodrigues', 'i',
    'Principal aeroporto do Tocantins, ao sul do Plano Diretor, na margem do lago e a poucos quilômetros do centro.',
    [A(1, [(100,2185),(235,2180),(390,2340),(385,2400),(225,2400),(95,2235)])], s='Aeroporto')
add('flyer', 'Aeródromo Sítio Flyer', 'i', 'Pequeno aeródromo indicado no mapa-base, ao norte do Plano Diretor.',
    [A(1, [(572,30),(585,28),(672,70),(660,82)])], s='Sítio Flyer')
add('ete-norte', 'ETE Norte (BRK)', 'i', 'Estação de tratamento de esgoto na orla norte, indicada no mapa-base como ETE Norte, operada pela BRK.',
    [A(1, [(190,480),(270,480),(265,570),(190,575)])])
add('ata', 'Aeródromo da Associação Tocantinense de Aviação', 'i', 'Pista da ATA, ao norte da TO-080, entre a ferrovia e Luzimangues.',
    [A(7, [(412,1018),(522,1017),(522,1037),(412,1037)])], s='ATA')
add('terminal', 'Terminal Multimodal Palmas / Porto Nacional', 'i',
    'Terminais ao longo da Ferrovia Norte-Sul (Terminal Multimodal e Terminal VLI Porto Nacional, conforme os rótulos do mapa-base), usados para integrar ferrovia e rodovias no escoamento da produção regional.',
    [A(7, [(345,1335),(385,1360),(392,1425),(350,1432)]), A(7, [(248,1552),(328,1520),(332,1672),(268,1676)])], s='Terminal Multimodal')
add('aterro', 'Aterro Sanitário de Palmas', 'i', 'Destino final dos resíduos da capital, afastado da área urbana, a sudeste de Taquaralto.',
    [A(3, [(840,505),(910,500),(945,640),(855,645)])], s='Aterro')
add('prata', 'Área “Prata”', 'i', 'Grande área de uso rural ou logístico rotulada como “Prata” no mapa-base, a oeste da BR-010.',
    [A(2, [(330,1470),(560,1455),(570,1610),(335,1650)])], s='Prata')
add('frigovale', 'Aeródromo Fazenda Frigovale I', 'i', 'Aeródromo agrícola indicado no mapa-base, ao sul, perto da BR-010 e da TO-050.',
    [A(2, [(530,2150),(648,2148),(648,2178),(530,2180)])], s='Frigovale')
add('agrotins', 'Agrotins', 'p', 'Parque onde ocorre a Agrotins, feira agrotecnológica do Tocantins, na margem do lago, ao sul de Palmas.',
    [A(2, [(145,985),(230,985),(232,1065),(148,1065)])])

# ---------- sul e leste ----------
add('aureny', 'Aureny e região sul', 'b', 'Região residencial ao sul do Plano Diretor, a oeste da BR-010, com avenidas largas como a do Comércio e a Brasil. Limites aproximados.',
    [A(1, [(610,2300),(960,2300),(960,2576),(610,2576)]), A(2, [(718,0),(1045,0),(1045,260),(718,260)])], s='Aureny')
add('jardim-taquari', 'Jardim Taquari', 'b', 'Bairro da região sul, entre a orla do lago e a BR-010, com vias de prefixo TLO e TNS (Av. TLO-5, TNS-2 e outras).',
    [A(2, [(335,310),(725,310),(725,480),(335,480)])])
add('taquaralto', 'Taquaralto', 'b',
    'Região sul de Palmas, às margens da BR-010. É uma das áreas mais populosas da capital, com bairros, comércio próprio e avenidas como Taquaruçu e Ipanema.',
    [A(3, [(190,140),(340,165),(440,215),(545,175),(558,300),(525,335),(470,400),(430,500),(340,560),(290,610),(190,585)]),
     A(3, [(30,430),(130,430),(130,700),(30,720)])])
add('taquarussu', 'Taquarussu do Porto', 'b',
    'Distrito de Palmas conhecido pelas cachoeiras e trilhas da Serra do Lajeado, ligado ao resto da cidade pela TO-030.',
    [A(4, [(885,345),(950,320),(1020,350),(1080,410),(1075,490),(1000,505),(930,490),(890,440)])])
add('capivara', 'Capivara', 'b', 'Povoado rural indicado no mapa-base, ao norte da TO-080, a oeste de Luzimangues.',
    [A(7, [(700,585),(840,570),(910,700),(900,800),(780,830),(700,760)])])

# ---------- Luzimangues ----------
add('luzimangues', 'Luzimangues', 'b',
    'Distrito de Porto Nacional do outro lado do lago, conurbado a Palmas e ligado a ela pela TO-080 e pela ponte. Reúne vários loteamentos (Laguna, Jardim Europa, Barcelona, Águas Lindas e outros).',
    [A(6, [(330,690),(930,690),(950,1000),(905,1120),(960,1330),(1010,1500),(865,1565),(600,1565),(430,1340),(400,1000),(330,880)])], f=8)
for id_, n, txt, q in [
    ('laguna-1', 'Laguna I', 'ao norte da TO-080', [(335,870),(490,855),(495,1020),(400,1022)]),
    ('jardim-madri', 'Jardim Madri', 'ao norte da TO-080', [(495,855),(615,855),(625,1030),(500,1025)]),
    ('jardim-europa', 'Jardim Europa', 'ao norte da TO-080', [(615,850),(765,850),(765,1035),(640,1030)]),
    ('barcelona', 'Barcelona Residencial', 'junto à cabeceira da ponte', [(765,820),(935,815),(940,1075),(765,1050)]),
    ('laguna-2', 'Laguna II', 'ao sul da TO-080', [(380,1040),(460,1040),(490,1130),(480,1230),(400,1200)]),
    ('park-buritis', 'Park dos Buritis', 'ao sul da TO-080', [(480,1130),(620,1130),(620,1200),(480,1200)]),
    ('jardim-porto', 'Jardim do Porto', 'ao sul da TO-080', [(600,1085),(760,1085),(780,1160),(660,1170)]),
    ('laguna-3', 'Laguna III', 'ao sul da TO-080', [(470,1230),(640,1230),(640,1340),(490,1330)]),
    ('aguas-lindas', 'Águas Lindas', 'ao sul da TO-080', [(640,1305),(860,1285),(885,1390),(690,1410)]),
    ('bela-vista', 'Jardim Bela Vista', 'no extremo sul do distrito', [(700,1420),(880,1385),(900,1500),(760,1550),(690,1500)]),
    ('pocao', 'Poção', 'ao norte, na região da TO-348', [(330,355),(365,355),(365,385),(330,385)])]:
    add(id_, n, 'b', f'Bairro ou localidade de Luzimangues, {txt}. Limites aproximados.', [A(6, q)])

# ---------- vias ----------
add('to080', 'TO-080', 'v', 'Rodovia estadual que cruza Palmas pela Praça dos Girassóis, atravessa o lago pela ponte e chega a Luzimangues e Porto Nacional.',
    [L(7, [(0,1115),(300,1124),(570,1128),(1108,1142)]), L(6, [(270,1025),(450,1027),(840,1037),(940,945),(1108,940)]),
     L(5, [(463,914),(700,912),(1108,908)]), L(1, [(111,985),(520,983),(915,975)])])
add('br010', 'BR-010', 'v', 'Rodovia federal que margeia Palmas a leste e segue para o sul passando por Taquaralto. Principal eixo de ligação regional.',
    [L(1, [(803,0),(815,120),(850,300),(890,480),(930,665),(930,850),(920,980),(890,1090),(820,1210),(790,1330),(780,1700),(790,1860),(870,1990),(930,2130),(955,2300),(960,2576)]),
     L(3, [(200,0),(185,260),(165,500),(140,580),(120,700),(110,850),(112,980),(125,1030),(120,1080),(60,1150),(29,1190)]),
     L(2, [(900,1190),(870,1300),(865,1600),(840,1800),(760,1920),(590,2085),(520,2150),(430,2190),(180,2576)])])
add('to030', 'TO-030', 'v', 'Rodovia estadual que liga a região de Taquaralto a Taquarussu do Porto.',
    [L(3, [(190,245),(370,245),(430,215),(545,175),(655,108),(800,140),(860,150),(915,125)]),
     L(4, [(0,520),(150,490),(300,450),(380,375),(480,325),(540,305),(570,335),(640,340),(720,330),(780,295),(850,350),(930,405),(1030,415),(1060,340),(1108,300)])])
add('to348', 'TO-348', 'v', 'Rodovia estadual que sai da TO-080, em Luzimangues, rumo ao norte.',
    [L(6, [(672,0),(668,330),(640,400),(470,500),(380,560),(310,640),(260,780),(250,1020)])])
add('to455', 'TO-455', 'v', 'Rodovia estadual que parte da TO-080 rumo ao sul, passando pelo Terminal Multimodal.',
    [L(7, [(570,1128),(480,1400),(435,1550),(440,1640),(500,1720),(540,1790),(700,1850),(750,1950),(740,2000),(665,2060),(690,2200),(730,2260),(700,2330),(690,2430),(640,2480),(625,2576)])])
add('ferrovia', 'Ferrovia Norte-Sul', 'v', 'Corredor ferroviário que passa a oeste de Luzimangues e abastece o Terminal Multimodal.',
    [L(7, [(0,470),(100,505),(135,600),(120,680),(85,860),(80,1000),(95,1115),(220,1200),(330,1300),(355,1380),(335,1520),(310,1650),(240,1690),(130,1740),(60,1900),(45,1990),(50,2050),(0,2075)])])



# ---------- geometrias reais do OpenStreetMap (export recebido) ----------
OSM = json.load(open(PROC / 'osm_regs.json', encoding='utf-8')) + json.load(open(PROC / 'osm_regs2.json', encoding='utf-8'))
QF = json.load(open(PROC / 'quadra_fix.json', encoding='utf-8'))
_idx = {r['id']: r for r in R}
for o in OSM:
    parts = [(p['k'], None, [tuple(x) for x in p['q']]) for p in o['parts']]
    if o.get('patch'): continue
    if o.get('replace') and o['id'] in _idx:
        r = _idx[o['id']]; r['parts'] = parts; r['d'] = o['d']; r['ln'] = o.get('ln', False)
        if o.get('f'): r['f'] = o['f']
    else:
        add(o['id'], o['n'], o['c'], o['d'], parts, s=o.get('s'), f=o.get('f')); R[-1]['ln'] = o.get('ln', False)
_idx['parque-pds']['n'] = 'Parque Cesamar'
_idx['parque-pds']['d'] = 'Grande área verde com lago no Plano Diretor Sul, a leste do eixo da Av. Teotônio Segurado, usada para lazer, caminhadas e esportes. O nome é confirmado pela “Lagoa do Parque Cesamar”, mapeada no OpenStreetMap neste mesmo local. Limites aproximados.'
_idx['parque-pds']['s'] = 'Parque Cesamar'

# ---------- quadras do Plano Diretor ----------
import re as _re
QR=json.load(open(PROC / 'quadras_final.json', encoding='utf-8'))
for _q in QR:
    _q['o']={'301 N':'ACSU-NO 40','302 N':'ARNE 40'}.get(_q['n'],_q['o'])
CODE={'ARSO':'Área Residencial Sul Oeste','ARSE':'Área Residencial Sul Leste','ARNO':'Área Residencial Norte Oeste','ARNE':'Área Residencial Norte Leste'}
def tipo(o):
    if not o: return 'Quadra do Plano Diretor.'
    k=o.split()[0]
    if k in CODE: return f'Quadra residencial ({o}, {CODE[k]}).'
    if k.startswith('ASR'): return f'Faixa de serviços ASR ({o}), junto à BR-010.'
    if k.startswith('ACSU'): return f'Faixa de comércio e serviços ao longo da Av. Teotônio Segurado ({o}).'
    if k.startswith('AC'): return f'Área central de comércio e serviços ({o}).'
    if k.startswith('AV'): return f'Área verde ({o}).'
    return f'Código antigo: {o}.'
seen=set()
for q in QR:
    num,side=q['n'].rsplit(' ',1); lado='Norte' if side=='N' else 'Sul'
    nome=f"Quadra {num} {lado}" if not num.startswith('AV') and not num.startswith('AA') else f"Área verde {num} {lado}"
    full=nome+(f" ({q['o']})" if q['o'] else '')
    id_=_re.sub(r'[^a-z0-9]+','-',(num+'-'+lado+'-'+(q['o'] or '')).lower()).strip('-')
    if id_ in seen: continue
    seen.add(id_)
    d=tipo(q['o'])
    if q.get('t')=='osm': d+=' Contorno vindo do OpenStreetMap.'
    elif q.get('t')=='h': d+=' Contorno estimado a partir das alamedas da quadra mapeadas no OpenStreetMap.'
    else: d+=' Contorno e posição aproximados, derivados do mapa esquemático de quadras de Palmas e ajustados pelas alamedas do OpenStreetMap.'
    if num=='109 N': d+=' No mapa de origem este rótulo aparece como “109 S (ARSO 14)”, provável erro de grafia: por estar ao norte da Av. JK, foi tratada como 109 Norte.'
    if q['n'].endswith('N') and False: pass
    add('q-'+id_, full, 'q', d, [('a',1,[tuple(p) for p in QF.get(q['n']+'|'+str(q['o']),q['poly'])])], s=num+' '+side, f=14)
    R[-1]['o']=q['o']

# ---------- lazer e esportes (OpenStreetMap) ----------
LZ=json.load(open(PROC / 'lazer.json', encoding='utf-8'))
SP={'soccer':'futebol','basketball':'basquete','volleyball':'vôlei','futsal':'futsal','multi':'esportes variados','skateboard':'skate'}
for i,l in enumerate(LZ):
    nome=l['n'].replace('Quada','Quadra')
    kind={'pitch':'Quadra esportiva','park':'Praça ou parque','playground':'Playground','garden':'Jardim'}.get(l['leisure'],'Área de lazer')
    sp=(' Modalidade: '+SP.get(l['sport'],l['sport'])+'.') if l.get('sport') else ''
    id_='l-'+_re.sub(r'[^a-z0-9]+','-',nome.lower()).strip('-')+f'-{i}'
    add(id_, nome, 'l', f'{kind} mapeada no OpenStreetMap.{sp}', [('a',1,[tuple(p) for p in l['poly']])], s=nome.replace('Quadra Poliesportiva','Poliesp.').replace('Praça da Quadra','Praça').replace('Praça da','Praça'), f=30)

# ---------- pontos turísticos (mapa turístico em PDF + OSM) ----------
import numpy as _np, cv2 as _cv
_idx2={r['id']:r for r in R}
def _circle(c,r=300,n=12): return [(c[0]+r*math.cos(2*math.pi*i/n),c[1]+r*math.sin(2*math.pi*i/n)) for i in range(n)]
_lake=[o for o in OSM if o['id']=='lago-palmas'][0]; _lq=_np.array(_lake['parts'][0]['q'],_np.float32).reshape(-1,1,2)
_br=[a for o in OSM if o['id']=='to080' for p in o['parts'] for a in p['q'] if _cv.pointPolygonTest(_lq,(float(a[0]),float(a[1])),False)>0]
_bc=(float(_np.median([a[0] for a in _br])),float(_np.median([a[1] for a in _br]))) if _br else tuple(u(5,700,908))
_praca=u(1,520.5,983.5)
SRC=' (Fonte: mapa turístico de Palmas fornecido.)'
NEW=[('tur-ponte','Ponte da Amizade (TO-080)','bridge','lago',_bc,'Liga Palmas a Luzimangues pela TO-080, atravessando o Lago de Palmas. O mapa turístico a destaca como Ponte da Amizade e cita 8 km de comprimento; a Praia da Graciosa tem vista para ela.'+SRC,'Ponte da Amizade'),
('tur-palacio','Palácio Araguaia','palace','cult',_praca,'Sede do governo do Tocantins, no centro da Praça dos Girassóis, entre as quatro áreas administrativas (AA) do Plano Diretor.','Palácio Araguaia'),
('tur-graciosa','Praia da Graciosa','umbrella','lago',tuple(u(1,145,1085)),'Orla de 520 m com bares e restaurantes, quadra de esporte, marina com atracadouro, píer e vista para a Ponte da Amizade. Recebe eventos culturais, esportivos e de lazer, e o pôr do sol no lago é imperdível. Posição aproximada.'+SRC,'Praia da Graciosa'),
('tur-arnos','Praia das Arnos','umbrella','lago',tuple(u(1,202,715)),'Praia da orla norte do Plano Diretor, citada no mapa turístico junto às praias da Graciosa e do Prata. Posição aproximada.'+SRC,'Praia das Arnos'),
('tur-canela','Ilha Canela','island','lago',tuple(u(5,664,1782)),'Ilha no Lago de Palmas, a sudoeste da Praia do Prata, destacada no mapa turístico. Posição aproximada.'+SRC,'Ilha Canela'),
('tur-serra','Serra do Lajeado e Mirante da Serra','mountain','nat',(152000.0,66000.0),'O Mirante da Serra, a 450 m de altitude, permite ver quase toda a extensão da capital, entre o grande lago e a serra, e tem rampas para salto de parapente (informações: www.voepalmas.com.br). Posição ilustrativa: a serra fica a leste de Taquaruçu, fora das imagens do mapa-base.'+SRC,'Serra do Lajeado')]

SIGNS=[('sinal-miracema','Sinalização — Miracema','sign','sign',(84300.0,9600.0),'Direção de Miracema do Tocantins, ao norte, pela BR-010/TO-010 (indicação do mapa turístico).','MIRACEMA ↑'),
('sinal-lajeado','Sinalização — Lajeado','sign','sign',(88600.0,12600.0),'Direção de Lajeado, ao norte (indicação do mapa turístico).','LAJEADO ↑'),
('sinal-paraiso','Sinalização — Paraíso','sign','sign',(900.0,28600.0),'Direção de Paraíso do Tocantins, a oeste, atravessando a Ponte da Amizade pela TO-080 (indicação do mapa turístico).','← PARAÍSO'),
('sinal-porto-nacional','Sinalização — Porto Nacional','sign','sign',(64700.0,132400.0),'Direção de Porto Nacional, ao sul, pela BR-010 (TO-050 e TO-020 no mapa turístico).','PORTO NACIONAL ↓'),
('sinal-taquaralto','Sinalização — Taquaralto','sign','sign',(87300.0,71500.0),'Região de Taquaralto, ao sul do Plano Diretor, pela BR-010.','TAQUARALTO ↓'),
('sinal-taquarucu','Sinalização — Taquaruçu','sign','sign',(133600.0,64700.0),'Distrito de Taquaruçu, a 32 km de Palmas, pela TO-030 (indicação do mapa turístico).','TAQUARUÇU →')]

# ---------- cinco pontos adicionais (OSM + mapa turístico) ----------
from calib import g_units as _gu
def _qp(n): return _np.array([q for q in QR if q['n']==n][0]['poly'],float)
def _edge(n,side,k=3,dx=0):
    P=_qp(n); idx=_np.argsort(P[:,0])[:k] if side=='w' else _np.argsort(-P[:,0])[:k]; c=P[idx].mean(axis=0); return tuple(u(1,c[0]+dx,c[1]))
_feira=[f for f in json.load(open(RAW / 'osm_export_1.geojson', encoding='utf-8'))['features'] if f['properties'].get('name')=='Feira da 304 Sul'][0]
_fp=[tuple(p) for p in _gu(_np.array(_feira['geometry']['coordinates'][0]))]
add('feira-304-sul','Feira da 304 Sul','p','Feira da quadra 304 Sul (marcada como mercado no OpenStreetMap), destacada no mapa turístico. Contorno do OpenStreetMap.',[('a',None,_fp)],s='Feira 304 Sul',f=30)
_rid={r['id']:r for r in R}
_est=_np.array([a for p in _rid['estadio-nilton-santos']['parts'] for a in p[2]],float).mean(axis=0)
NEW+=[('tur-sesc','SESC','building','cult',_edge('504 N','w',3,-4),'Unidade do SESC destacada no mapa turístico, na região norte do Plano Diretor, junto à Av. Joaquim Teotônio Segurado e às quadras 504 N e 602 N. Posição aproximada, estimada a partir da ilustração do mapa turístico.','SESC'),
('tur-palacinho','Palácio da Cultura (Palacinho)','palace','cult',_edge('112 N','e',3,10),'Aparece no mapa turístico como “Palacinho da Cultura”, no extremo nordeste do Plano Diretor, junto à quadra 112 N e à rodovia. Posição aproximada, estimada a partir da ilustração do mapa turístico.','Palacinho da Cultura'),
('tur-caju','Praia do Caju','umbrella','lago',tuple(u(1,161,1980)),'Praia citada no mapa turístico, junto à foz do Ribeirão Taquaruçu Grande, ao sul do Plano Diretor, ao lado das quadras 1307 S e 1311 S e perto do aeroporto. Posição estimada pela mancha de areia do mapa-base.'+SRC,'Praia do Caju')]
SIGNS+=[('sinal-buritis','Sinalização — Praia dos Buritis','sign','sign',tuple(u(1,948,2170)),'No mapa turístico, uma placa indica a Praia dos Buritis seguindo para o leste, pela BR-010, depois do estádio e da região do Aureny’s. A praia fica fora da área coberta pelo mapa-base; a posição da placa é aproximada.'+SRC,'PRAIA DOS BURITIS →')]


# ---------- mais seis pontos do mapa turístico ----------
def _qc(n,o=None):
    q=[q for q in QR if q['n']==n and (o is None or q['o']==o)][0]; c=_np.array(q['poly'],float).mean(axis=0); return tuple(u(1,c[0],c[1]))
NEW+=[('tur-sebrae','SEBRAE-TO','building','serv',_qc('102 N'),'Sede do SEBRAE no Tocantins (apoio a micro e pequenas empresas), destacada no mapa turístico junto à quadra 102 N, perto do Córrego Sussuapara e da Praça dos Girassóis. Posição aproximada, estimada pela quadra citada na ilustração.','SEBRAE-TO'),
('tur-catur','CATUR — Centro de Atendimento ao Turista','info','serv',_qc('103 N','ACNO 1'),'Centro de Atendimento ao Turista (CATUR), da Agência Municipal de Turismo (Agtur) da Prefeitura de Palmas: acolhe, orienta e informa sobre os atrativos da capital, e distribui mapas, folders e roteiros. Endereço conforme o Google Maps: Quadra 103 Norte, Rua NO 1, Plano Diretor Norte, Palmas (CEP 77001-096), ao lado da Praça dos Girassóis, ao norte da Av. JK. Telefone (63) 3215-2380; site visitepalmas.com.br. Dados do Google Maps (captura fornecida): confira os horários antes da visita.','CATUR'),
('tur-shopping','Palmas Shopping','bag','serv',_qc('101 S'),'Shopping center do Plano Diretor, destacado no mapa turístico junto à quadra 101 S, perto da Praça dos Girassóis. Posição aproximada, estimada pela quadra citada na ilustração.','Palmas Shopping'),
('tur-espaco-cultural','Espaço Cultural','theater','cult',_qc('202 S'),'Equipamento cultural destacado no mapa turístico junto às quadras 202 S e 204 S, perto da Feira da 304 Sul. Posição aproximada, estimada pela quadra citada na ilustração.','Espaço Cultural'),
('tur-ulbra','ULBRA Palmas','cap','cult',tuple(u(1,531,2205)),'Campus da ULBRA em Palmas, no extremo sul da Av. Teotônio Segurado, perto do estádio e do aeroporto. O OpenStreetMap traz vias identificadas como “Ulbra — Entrada Aeroporto” neste local.','ULBRA'),
('tur-catolica','Católica do Tocantins','cap','cult',_qc('1402 S'),'Centro universitário Católica do Tocantins, destacado no mapa turístico junto à quadra 1402 S, no sul do Plano Diretor. Posição aproximada, estimada pela quadra citada na ilustração.','Católica do Tocantins')]


def _rc(id_):
    r=[x for x in R if x['id']==id_][0]; k,t,pts=r['parts'][0]; P=_np.array([u(t,*p) if t is not None else p for p in pts],float); return tuple(P.mean(axis=0))
_ap=_rc('eq-terminal-de-passageiros') if any(x['id']=='eq-terminal-de-passageiros' for x in R) else _rc('aeroporto')
NEW+=[('tur-catur-aeroporto','CATUR — Aeroporto','info','serv',_ap,'Unidade do CATUR no Aeroporto de Palmas, inaugurada pela Prefeitura (Agtur) em 10 de abril de 2025, com estande temático inspirado nas belezas naturais da cidade, totens interativos e adesivação nas áreas de embarque, desembarque e no saguão. Fonte: Jornal Opção Tocantins, 11/04/2025. Posição aproximada dentro do terminal.','CATUR (Aeroporto)'),
('tur-catur-taquarucu','CATUR — Taquaruçu','info','serv',(_rc('taquarussu')[0]+700,_rc('taquarussu')[1]+420),'Unidade do CATUR no distrito de Taquaruçu, voltada ao ecoturismo (trilhas e cachoeiras) e ao Festival Gastronômico de Taquaruçu, segundo informação fornecida. Posição aproximada no distrito; confirme endereço e horários no portal da Prefeitura de Palmas.','CATUR (Taquaruçu)')]


_a=_qc('201 S'); _b=_qc('202 S')
NEW+=[('tur-hgp','Hospital Geral de Palmas (HGP)','health','serv',((_a[0]+_b[0])/2,(_a[1]+_b[1])/2),'Hospital Geral de Palmas (HGP), destacado no mapa turístico com a cruz vermelha, junto às quadras 201 S e 202 S, perto do Espaço Cultural. Em emergências, o SAMU atende pelo 192. Posição aproximada, estimada pela ilustração do mapa turístico; confirme o endereço antes de usar como referência.','HGP')]
SIGNS+=[('sinal-aureny','Sinalização — Aureny’s','sign','sign',(float(_est[0]+2900),float(_est[1]+700)),'No mapa turístico, uma placa indica o Aureny’s, região residencial ao sul do Plano Diretor, seguindo para o leste pela via que passa junto ao estádio. Posição da placa aproximada.'+SRC,'AURENY’S →')]

for id_,n,ic,g,c,d_,s_ in NEW+SIGNS:
    add(id_,n,'t',d_,[('a',None,_circle(c))],s=s_)
_idx2={r['id']:r for r in R}
def _upd(id_,d_=None,n=None):
    if id_ in _idx2:
        if d_: _idx2[id_]['d']=d_
        if n: _idx2[id_]['n']=n
_upd('lago-palmas','Reservatório formado no Rio Tocantins pela usina hidrelétrica Luís Eduardo Magalhães (Lajeado). Tem cerca de 630 km² e, só na capital, 54 km de comprimento. É propício a esportes náuticos e à pesca esportiva, banha a orla oeste de Palmas, separa a capital de Luzimangues e Porto Nacional e é atravessado pela TO-080. Contorno do OpenStreetMap; dados de área do mapa turístico.')
_upd('parque-pds','Área verde com lago no Plano Diretor Sul, a leste da Av. Teotônio Segurado. Tem pista de cooper de 2.820 m circundando o lago, pista de skate, bicicross, aparelhos de ginástica, trilha ecológica, playground e bar e restaurante. O nome é confirmado pela “Lagoa do Parque Cesamar” no OpenStreetMap. Limites aproximados.')
_upd('praia-do-prata','Praia na orla do Lago de Palmas, ao sul do Plano Diretor, citada no mapa turístico junto às praias da Graciosa, das Arnos, do Caju e dos Buritis. Contorno do OpenStreetMap.')
_upd('taquarussu','Distrito de Palmas a 32 km da capital, refúgio dos ecoturistas, com mais de 80 cachoeiras, trilhas, paredões, grutas, córregos e mirantes: Roncadeira (70 m, trilha de 40 min sombreada), Cachoeira do Evilson e Vale do Vai-Quem-Quer. Há artesanato de palha de babaçu e buriti, rapel e tirolesa (a Voo do Pontal é apontada como a maior em operação no Brasil) e de simples pousadas a hotéis fazenda. Clima ameno, de 10° a 34°. Ligado a Palmas pela TO-030.'+SRC)
_upd('kartodromo','Kartódromo de Palmas, junto ao Estádio Nilton Santos (chamado Kartódromo Rubens Barrichello no mapa turístico).')
_upd('praca-girassois','Centro cívico de Palmas e uma das maiores praças do país. Abriga o Palácio Araguaia, sede do governo estadual, e fica no cruzamento do eixo da Av. Teotônio Segurado com a TO-080 e a Av. JK.')
MKDEF=[('tur-ponte','bridge','lago'),('tur-palacio','palace','cult'),('praca-girassois','sunflower','cult'),('parque-pds','tree','nat'),('uft','cap','cult'),
('tur-graciosa','umbrella','lago'),('tur-arnos','umbrella','lago'),('praia-do-prata','umbrella','lago'),('tur-canela','island','lago'),('lago-palmas','wave','lago'),
('estadio-nilton-santos','stadium','esp'),('kartodromo','flag','esp'),('aeroporto','plane','trans'),('rodoviaria-palmas','bus','trans'),('agrotins','wheat','cult'),
('taquarussu','waterfall','nat'),('tur-serra','mountain','nat')]+[(s[0],'sign','sign') for s in SIGNS]+[('feira-304-sul','market','cult'),('tur-sesc','building','cult'),('tur-palacinho','palace','cult'),('tur-caju','umbrella','lago'),('tur-sebrae','building','serv'),('tur-catur','info','serv'),('tur-shopping','bag','serv'),('tur-espaco-cultural','theater','cult'),('tur-ulbra','cap','cult'),('tur-catolica','cap','cult'),('tur-catur-aeroporto','info','serv'),('tur-catur-taquarucu','info','serv'),('tur-hgp','health','serv')]

# ---------- serialização ----------
out = []
for r in R:
    parts, allp = [], []
    for k, t, pts in r['parts']:
        q = [u(t, *p) for p in pts] if t is not None else [[int(round(x)), int(round(y))] for x, y in pts]; parts.append(dict(k=k, q=q)); allp.append((k, q))
    xs = [p[0] for _, q in allp for p in q]; ys = [p[1] for _, q in allp for p in q]
    big = max(allp, key=lambda a: len(a[1]) if a[0] == 'l' else (max(p[0] for p in a[1]) - min(p[0] for p in a[1])) * (max(p[1] for p in a[1]) - min(p[1] for p in a[1])))
    bq = big[1]
    if big[0] == 'l': lab = bq[len(bq) // 2]
    else: lab = [round((min(p[0] for p in bq) + max(p[0] for p in bq)) / 2), round((min(p[1] for p in bq) + max(p[1] for p in bq)) / 2)]
    d = dict(id=r['id'], n=r['n'], c=r['c'], d=r['d'], p=parts, bb=[min(xs), min(ys), max(xs), max(ys)], lab=lab)
    if r['s']: d['s'] = r['s']
    if r['f']: d['f'] = r['f']
    if r.get('o'): d['o'] = r['o']
    if r.get('ln'): d['ln'] = 1
    out.append(d)


byid={d['id']:d for d in out}
MK=[]
for id_,ic,g in MKDEF:
    if id_ in byid:
        x,y=byid[id_]['lab']; MK.append(dict(id=id_,ic=ic,g=g,x=int(x),y=int(y),s=byid[id_].get('s') or byid[id_]['n']))

html = open(SRC_DIR / 'template.html', encoding='utf-8').read()
html = html.replace('__IMAGES__', ''.join(imgs)).replace('__DATA__', json.dumps(dict(cats=CATS, regs=out, mk=MK), ensure_ascii=False, separators=(',', ':')))
DIST.mkdir(exist_ok=True)
open(DIST / 'index.html', 'w', encoding='utf-8').write(html)
print(len(R), 'áreas;', round(len(html) / 1e6, 2), 'MB')
