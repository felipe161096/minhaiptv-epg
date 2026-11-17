#!/usr/bin/env python3
"""guide.xml (XMLTV gerado pelo grabber) -> epg.json pequeno pro app Minha IPTV.

Formato: {"gerado": <seg unix>, "canais": {"RedeGlobo.br": [{"i": ini, "f": fim, "t": "título"}, ...]}}
Mantém só o que importa pro "Agora / A seguir": de 1h atrás até 30h à frente.
Uso: converter.py guide.xml epg.json
"""
import json
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime


def seg(valor):
    return int(datetime.strptime(valor.strip(), "%Y%m%d%H%M%S %z").timestamp())


def converter(entrada, agora=None):
    agora = int(agora if agora is not None else time.time())
    ini, fim = agora - 3600, agora + 30 * 3600
    canais = {}
    for _, el in ET.iterparse(entrada, events=("end",)):
        if el.tag != "programme":
            continue
        try:
            i, f = seg(el.get("start", "")), seg(el.get("stop", ""))
        except ValueError:
            el.clear()
            continue
        canal = el.get("channel", "").split("@")[0]
        titulo = (el.findtext("title") or "").strip()
        if canal and titulo and f > ini and i < fim and f > i:
            canais.setdefault(canal, {})[i] = {"i": i, "f": f, "t": titulo}  # dedup por horário de início
        el.clear()
    return {"gerado": agora, "canais": {c: [p[k] for k in sorted(p)] for c, p in sorted(canais.items())}}


def main(entrada, saida):
    epg = converter(entrada)
    total = sum(len(v) for v in epg["canais"].values())
    if not epg["canais"]:
        sys.exit("guide.xml sem nenhum programa — não publica (o app continua com o de ontem)")
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(epg, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(epg['canais'])} canais, {total} programas")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
