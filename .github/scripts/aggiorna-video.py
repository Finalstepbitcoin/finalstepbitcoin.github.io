#!/usr/bin/env python3
"""
Scrive dentro index.html l'elenco degli ultimi video del canale.

Perche' esiste: YouTube vieta ai browser di leggere il suo feed
direttamente, quindi prima la pagina passava per servizi-ponte gratuiti di
terzi. Il 28 luglio 2026 erano giu' o saturi tutti insieme e la sezione
video e' sparita dal sito. Da server quel divieto non esiste: qui il feed
si legge e basta.

Cosa mostra: i 3 video piu' recenti, esclusi gli Short (riconosciuti dal
tag nel titolo) e le rassegne stampa (che stanno tutte in una playlist,
di cui si legge il feed per sapere quali ID scartare).

Non va lanciato a mano: lo esegue da solo il compito in
.github/workflows/video.yml. Se serve provarlo:  python3 questo-file.py
"""

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

CANALE = 'UCQxD8d7zhz9-OMMvvKPxNvA'
PLAYLIST_RASSEGNA = 'PLUbYXa060CgyN2yuT_LEOX2BkE1I4fA4s'
FEED = 'https://www.youtube.com/feeds/videos.xml?'
QUANTI = 3

RX_SHORT = re.compile(r'#\s*shor?ts?\b', re.I)
MESI = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu',
        'lug', 'ago', 'set', 'ott', 'nov', 'dic']

NS = {'a': 'http://www.w3.org/2005/Atom',
      'yt': 'http://www.youtube.com/xml/schemas/2015'}

INIZIO = '<!-- VIDEO:INIZIO'
FINE = '<!-- VIDEO:FINE -->'


def scarica(url):
    richiesta = urllib.request.Request(
        url, headers={'User-Agent': 'finalstepbitcoin-aggiorna-video'})
    with urllib.request.urlopen(richiesta, timeout=30) as r:
        return r.read()


def voci(xml_bytes):
    """Trasforma il feed in una lista di dizionari: id, titolo, data."""
    radice = ET.fromstring(xml_bytes)
    fuori = []
    for e in radice.findall('a:entry', NS):
        vid = e.find('yt:videoId', NS)
        titolo = e.find('a:title', NS)
        pubblicato = e.find('a:published', NS)
        if vid is None or titolo is None:
            continue
        fuori.append({
            'id': vid.text.strip(),
            'titolo': (titolo.text or '').strip(),
            'quando': (pubblicato.text or '').strip() if pubblicato is not None else '',
        })
    return fuori


def data_italiana(iso):
    """2026-07-22T18:00:00+00:00 -> 22 lug 2026"""
    if not iso:
        return ''
    try:
        d = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except ValueError:
        return ''
    return '%02d %s %d' % (d.day, MESI[d.month - 1], d.year)


def scheda(v):
    vid = html.escape(v['id'], quote=True)
    titolo = html.escape(v['titolo'])
    quando = html.escape(data_italiana(v['quando']))
    return (
        '<a href="https://www.youtube.com/watch?v=' + vid + '" target="_blank" '
        'rel="noopener" class="vcard">'
        '<span class="vthumb">'
        '<img src="https://img.youtube.com/vi/' + vid + '/mqdefault.jpg" alt="" '
        'loading="lazy" decoding="async">'
        '<span class="vplay"><svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path d="M8 5v14l11-7z"/></svg></span>'
        '</span>'
        '<span class="vinfo">'
        '<span class="vtitle">' + titolo + '</span>'
        '<span class="vdate">' + quando + '</span>'
        '</span>'
        '</a>'
    )


def main():
    try:
        tutti = voci(scarica(FEED + 'channel_id=' + CANALE))
    except Exception as errore:
        print('ERRORE: il feed del canale non risponde:', errore, file=sys.stderr)
        return 1

    if not tutti:
        print('ERRORE: il feed del canale e\' arrivato vuoto', file=sys.stderr)
        return 1

    # Le rassegne stampa stanno tutte in una playlist: ne leggo il feed per
    # sapere quali ID scartare. Se non risponde uso il ripiego sui titoli.
    esclusi = None
    try:
        esclusi = {v['id'] for v in voci(scarica(FEED + 'playlist_id=' + PLAYLIST_RASSEGNA))}
    except Exception as errore:
        print('avviso: playlist rassegne non raggiungibile, uso il ripiego sui titoli:',
              errore, file=sys.stderr)

    def da_tenere(v):
        if RX_SHORT.search(v['titolo']):
            return False
        if esclusi is not None:
            return v['id'] not in esclusi
        t = v['titolo'].lower()
        return 'rassegna' not in t and 'stampa' not in t

    scelti = [v for v in tutti if da_tenere(v)]
    scelti.sort(key=lambda v: v['quando'], reverse=True)
    scelti = scelti[:QUANTI]

    if not scelti:
        print('ERRORE: nessun video da mostrare dopo i filtri', file=sys.stderr)
        return 1

    pagina = open('index.html', encoding='utf-8').read()
    a = pagina.find(INIZIO)
    b = pagina.find(FINE)
    if a == -1 or b == -1:
        print('ERRORE: i segnaposto VIDEO:INIZIO / VIDEO:FINE non sono in index.html',
              file=sys.stderr)
        return 1

    testa = pagina[a:pagina.index('-->', a) + 3]
    blocco = testa + '\n      ' + '\n      '.join(scheda(v) for v in scelti) + '\n      '
    nuova = pagina[:a] + blocco + pagina[b:]

    if nuova == pagina:
        print('Nessun cambiamento: i video in pagina sono gia\' questi.')
        return 0

    open('index.html', 'w', encoding='utf-8').write(nuova)
    print('Aggiornati %d video:' % len(scelti))
    for v in scelti:
        print('  -', data_italiana(v['quando']), '|', v['titolo'][:70])
    return 0


if __name__ == '__main__':
    sys.exit(main())
