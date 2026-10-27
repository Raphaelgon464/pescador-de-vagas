
import requests
import json
import os
from datetime import datetime
from pescador.config import (
    carregar_segredos,
    KEYWORDS_INCLUSAO, KEYWORDS_EXCLUSAO,
    CACHE_FILE, MAX_CACHE_SIZE, MAX_VAGAS_POR_MENSAGEM
)

# Legado até a T6: mantém os nomes antigos, mas lidos do ambiente.
_SEGREDOS = carregar_segredos()
TELEGRAM_TOKEN = _SEGREDOS.telegram_token
CHAT_ID = _SEGREDOS.chat_id
JOOBLE_API_KEY = _SEGREDOS.jooble_api_key

def carregar_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def salvar_cache(cache):
    cache = cache[-MAX_CACHE_SIZE:]
    with open(CACHE_FILE, 'w', encoding='utf-8') as f: json.dump(cache, f, ensure_ascii=False)

def vaga_bate_com_perfil(titulo, descricao=''):
    texto = (str(titulo) + ' ' + str(descricao)).lower()
    tem_inclusao = any(kw in texto for kw in KEYWORDS_INCLUSAO)
    tem_exclusao = any(kw in texto for kw in KEYWORDS_EXCLUSAO)
    return tem_inclusao and not tem_exclusao

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML', 'disable_web_page_preview': False}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200: print("✅ Mensagem enviada para o Telegram!")
        else: print(f"❌ Erro Telegram: {r.text}")
    except Exception as e: print(f"❌ Erro de conexão com Telegram: {e}")

def buscar_jooble(query, location):
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {"keywords": query, "location": location}
    print(f"🔍 Buscando na Jooble: {query} em {location}...")
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code != 200:
            print(f"❌ Erro Jooble ({r.status_code}): {r.text}")
            return []
        return r.json().get('jobs', [])
    except Exception as e:
        print(f"❌ Erro de conexão Jooble: {e}")
        return []

def buscar_remoteok():
    url = "https://remoteok.com/api"
    headers = {'User-Agent': 'Mozilla/5.0'}
    print("🔍 Buscando na RemoteOK (Remoto Global)...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200: return []
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            return data[1:] if data[0].get('id') == 'remoteok' else data
        return []
    except Exception as e:
        print(f"❌ Erro RemoteOK: {e}")
        return []

def processar_jooble(vagas, cache):
    novas = []
    for v in vagas:
        job_id = f"jooble_{v.get('id')}"
        if job_id in cache: continue
        titulo = v.get('title', '')
        if not vaga_bate_com_perfil(titulo, v.get('description', '')): continue
        local = v.get('location', 'Brasil')
        is_remote = 'remoto' in local.lower() or 'remote' in titulo.lower()
        novas.append({
            'id': job_id, 'titulo': titulo, 'empresa': v.get('company', 'N/A'),
            'local': local, 'tipo': ' Remoto' if is_remote else '🏢 Híbrido/Presencial',
            'link': v.get('url', v.get('link', ''))
        })
        cache.append(job_id)
    return novas

def processar_remoteok(vagas, cache):
    novas = []
    for v in vagas:
        job_id = f"rok_{v.get('id')}"
        if job_id in cache: continue
        titulo = v.get('position', '')
        tags = ' '.join([t.get('tag', '') for t in v.get('tags', [])])
        if not vaga_bate_com_perfil(titulo, tags): continue
        novas.append({
            'id': job_id, 'titulo': titulo, 'empresa': v.get('company', 'N/A'),
            'local': v.get('location', 'Global'), 'tipo': '🌍 Remoto (Global)', 'link': v.get('url', '')
        })
        cache.append(job_id)
    return novas

def main():
    print(f" [{datetime.now().strftime('%d/%m %H:%M')}] Iniciando busca de vagas...")
    cache = carregar_cache()
    todas_novas = []
    
    if JOOBLE_API_KEY:
        vagas_rem_br = buscar_jooble('desenvolvedor OR analista OR suporte OR assistente OR python OR c#', 'Brazil')
        todas_novas.extend(processar_jooble(vagas_rem_br, cache))
        vagas_sp = buscar_jooble('desenvolvedor OR analista OR suporte OR assistente OR python OR c#', 'Sao Paulo')
        todas_novas.extend(processar_jooble(vagas_sp, cache))
    
    vagas_rok = buscar_remoteok()
    todas_novas.extend(processar_remoteok(vagas_rok, cache))
    
    if todas_novas:
        msg = f"🚨 <b>ALERTA DE VAGAS</b> 🚨\n\n🎣 <b>{len(todas_novas)} vaga(s) nova(s):</b>\n\n"
        for v in todas_novas[:MAX_VAGAS_POR_MENSAGEM]:
            msg += f"💼 <b>{v['titulo']}</b>\n {v['empresa']}\n {v['local']} | {v['tipo']}\n🔗 <a href='{v['link']}'>Aplicar</a>\n━━━━━━━━━━━━━━━\n"
        enviar_telegram(msg)
    else:
        print("️ Nenhuma vaga nova encontrada.")
    
    salvar_cache(cache)
    print("🏁 Processo finalizado.")

if __name__ == "__main__":
    main()
