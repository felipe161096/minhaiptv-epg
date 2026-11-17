# minhaiptv-epg

Gera todo dia o guia de programação (EPG) dos canais do Brasil e da Itália
usados pelo app **Minha IPTV**, e publica um `epg.json` pequeno (~100–300 KB)
no branch `dados`, que o app baixa no máximo a cada 12h.

- Fontes: grabber do [iptv-org/epg](https://github.com/iptv-org/epg) —
  mi.tv e meuguia.tv (BR); SuperGuidaTV, RaiPlay, Mediaset e Sky (IT).
- `scripts/montar_canais.py`: escolhe uma fonte por canal.
- `scripts/converter.py`: XMLTV → JSON curto (só de 1h atrás até 30h à frente).
- `.github/workflows/epg.yml`: roda 1x por dia (e pelo botão "Run workflow").

O branch `dados` tem sempre um commit só (sobrescrito), então o repositório
não cresce. Se o GitHub pausar o agendamento por inatividade (acontece em
repositórios públicos sem commits por 60 dias), reative em Actions.
