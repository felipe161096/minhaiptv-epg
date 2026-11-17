#!/usr/bin/env python3
"""Monta o custom.channels.xml do grabber do iptv-org.

Pra cada canal do Brasil e da Itália que tem stream no iptv-org (os mesmos que
aparecem no app Minha IPTV), escolhe a 1ª fonte de guia que conhece o canal,
na ordem de preferência de FONTES. Uso: montar_canais.py <grabber/sites> <saida.xml>
"""
import re
import sys
import urllib.request

STREAMS = {
    "br": "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
    "it": "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/it.m3u",
}
FONTES = {
    "br": ["mi.tv/mi.tv_br.channels.xml", "meuguia.tv/meuguia.tv.channels.xml"],
    # Itália: fontes oficiais primeiro. A SuperGuidaTV não devolveu nada na 1ª
    # execução (2026-11-17) — fica por último, só pros canais que nenhuma outra tem.
    "it": [
        "raiplay.it/raiplay.it.channels.xml",
        "mediasetinfinity.mediaset.it/mediasetinfinity.mediaset.it.channels.xml",
        "guidatv.sky.it/guidatv.sky.it.channels.xml",
        "superguidatv.it/superguidatv.it.channels.xml",
    ],
}
CANAL = re.compile(r"<channel\b([^>]*)>([^<]*)</channel>")
ATTR = re.compile(r'(\w+)="([^"]*)"')


def ids_com_stream(url):
    texto = urllib.request.urlopen(url, timeout=60).read().decode("utf-8")
    return {m.split("@")[0] for m in re.findall(r'tvg-id="([^"]+)"', texto) if m}


def main(sites_dir, saida):
    linhas = []
    for pais, url in STREAMS.items():
        faltam = ids_com_stream(url)
        total = len(faltam)
        for fonte in FONTES[pais]:
            try:
                xml = open(f"{sites_dir}/{fonte}", encoding="utf-8").read()
            except FileNotFoundError:
                print(f"aviso: fonte {fonte} não existe mais no grabber, pulando")
                continue
            achados = 0
            for attrs, nome in CANAL.findall(xml):
                a = dict(ATTR.findall(attrs))
                base = a.get("xmltv_id", "").split("@")[0]
                if base in faltam:
                    faltam.discard(base)
                    achados += 1
                    # valores já vêm escapados do XML de origem: copia como estão
                    linhas.append(
                        f'  <channel site="{a["site"]}" site_id="{a["site_id"]}" '
                        f'lang="{a.get("lang", "")}" xmltv_id="{a["xmltv_id"]}">{nome}</channel>'
                    )
            print(f"{pais}: {fonte}: {achados} canais")
        print(f"{pais}: {total - len(faltam)} de {total} canais com guia")
    if not linhas:
        sys.exit("nenhum canal encontrado — estrutura do grabber mudou?")
    with open(saida, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<channels>\n' + "\n".join(linhas) + "\n</channels>\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
