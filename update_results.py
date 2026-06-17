import os
import json
import requests
from datetime import datetime, timezone

FOOTBALL_API_KEY = os.environ["FOOTBALL_API_KEY"]
FIREBASE_DB_URL  = "https://copa-2026-album-79fb4-default-rtdb.firebaseio.com"

TEAM_MAP = {
    "México":"Mexico","África do Sul":"South Africa","Coreia do Sul":"South Korea",
    "Tchéquia":"Czech Republic","Canadá":"Canada","Bósnia":"Bosnia and Herzegovina",
    "Catar":"Qatar","Suíça":"Switzerland","Brasil":"Brazil","Marrocos":"Morocco",
    "Haiti":"Haiti","Escócia":"Scotland","EUA":"USA","Paraguai":"Paraguay",
    "Austrália":"Australia","Turquia":"Turkey","Alemanha":"Germany","Curaçao":"Curacao",
    "Costa do Marfim":"Ivory Coast","Equador":"Ecuador","Holanda":"Netherlands",
    "Japão":"Japan","Suécia":"Sweden","Tunísia":"Tunisia","Bélgica":"Belgium",
    "Egito":"Egypt","Irã":"Iran","Nova Zelândia":"New Zealand","Espanha":"Spain",
    "Cabo Verde":"Cape Verde","Arábia Saudita":"Saudi Arabia","Uruguai":"Uruguay",
    "França":"France","Senegal":"Senegal","Iraque":"Iraq","Noruega":"Norway",
    "Argentina":"Argentina","Argélia":"Algeria","Áustria":"Austria","Jordânia":"Jordan",
    "Portugal":"Portugal","Congo DR":"DR Congo","Uzbequistão":"Uzbekistan",
    "Colômbia":"Colombia","Inglaterra":"England","Croácia":"Croatia",
    "Gana":"Ghana","Panamá":"Panama",
}
EN_TO_PT = {v: k for k, v in TEAM_MAP.items()}

ALIASES = {
    "United States":"EUA","USA":"EUA","United States of America":"EUA",
    "Korea Republic":"Coreia do Sul","Republic of Korea":"Coreia do Sul",
    "Czechia":"Tchéquia","Czech Republic":"Tchéquia",
    "Bosnia & Herzegovina":"Bósnia","Bosnia and Herzegovina":"Bósnia","Bosnia-Herzegovina":"Bósnia","Bosnia & Herz":"Bósnia",
    "Canada":"Canadá",
    "Ivory Coast":"Costa do Marfim","Côte d'Ivoire":"Costa do Marfim",
    "Curaçao":"Curaçao","Curacao":"Curaçao",
    "DR Congo":"Congo DR","Democratic Republic of Congo":"Congo DR","Congo DR":"Congo DR","Congo, DR":"Congo DR",
    "New Zealand":"Nova Zelândia","Cape Verde":"Cabo Verde","Cape Verde Islands":"Cabo Verde","Spain":"Espanha",
    "Saudi Arabia":"Arábia Saudita","South Africa":"África do Sul",
}

def normalize(name):
    if name in EN_TO_PT: return EN_TO_PT[name]
    if name in ALIASES:
        a = ALIASES[name]
        return a
    return None

GAME_IDS = {
    ("México","África do Sul"):"ga1",("Coreia do Sul","Tchéquia"):"ga2",
    ("Canadá","Bósnia"):"ga3",("EUA","Paraguai"):"ga4",
    ("Catar","Suíça"):"ga5",("Brasil","Marrocos"):"ga6",
    ("Haiti","Escócia"):"ga7",("Austrália","Turquia"):"ga8",
    ("Alemanha","Curaçao"):"ga9",("Holanda","Japão"):"ga10",
    ("Costa do Marfim","Equador"):"ga11",("Suécia","Tunísia"):"ga12",
    ("Espanha","Cabo Verde"):"ga13",("Bélgica","Egito"):"ga14",
    ("Arábia Saudita","Uruguai"):"ga15",("Irã","Nova Zelândia"):"ga16",
    ("França","Senegal"):"ga17",("Iraque","Noruega"):"ga18",
    ("Argentina","Argélia"):"ga19",("Áustria","Jordânia"):"ga20",
    ("Portugal","Congo DR"):"ga21",("Inglaterra","Croácia"):"ga22",
    ("Gana","Panamá"):"ga23",("Uzbequistão","Colômbia"):"ga24",
    ("Tchéquia","África do Sul"):"ga25",("Suíça","Bósnia"):"ga26",
    ("Canadá","Catar"):"ga27",("México","Coreia do Sul"):"ga28",
    ("EUA","Austrália"):"ga29",("Escócia","Marrocos"):"ga30",
    ("Brasil","Haiti"):"ga31",("Turquia","Paraguai"):"ga32",
    ("Holanda","Suécia"):"ga33",("Alemanha","Costa do Marfim"):"ga34",
    ("Equador","Curaçao"):"ga35",("Tunísia","Japão"):"ga36",
    ("Espanha","Arábia Saudita"):"ga37",("Bélgica","Irã"):"ga38",
    ("Uruguai","Cabo Verde"):"ga39",("Nova Zelândia","Egito"):"ga40",
    ("Argentina","Áustria"):"ga41",("França","Iraque"):"ga42",
    ("Noruega","Senegal"):"ga43",("Jordânia","Argélia"):"ga44",
    ("Portugal","Uzbequistão"):"ga45",("Inglaterra","Gana"):"ga46",
    ("Panamá","Croácia"):"ga47",("Colômbia","Congo DR"):"ga48",
    ("Suíça","Canadá"):"ga49",("Bósnia","Catar"):"ga50",
    ("Escócia","Brasil"):"ga51",("Marrocos","Haiti"):"ga52",
    ("Tchéquia","México"):"ga53",("África do Sul","Coreia do Sul"):"ga54",
    ("Equador","Alemanha"):"ga55",("Curaçao","Costa do Marfim"):"ga56",
    ("Japão","Suécia"):"ga57",("Tunísia","Holanda"):"ga58",
    ("Turquia","EUA"):"ga59",("Paraguai","Austrália"):"ga60",
    ("Noruega","França"):"ga61",("Senegal","Iraque"):"ga62",
    ("Cabo Verde","Arábia Saudita"):"ga63",("Uruguai","Espanha"):"ga64",
    ("Egito","Irã"):"ga65",("Nova Zelândia","Bélgica"):"ga66",
    ("Panamá","Inglaterra"):"ga67",("Croácia","Gana"):"ga68",
    ("Colômbia","Portugal"):"ga69",("Congo DR","Uzbequistão"):"ga70",
    ("Argélia","Áustria"):"ga71",("Jordânia","Argentina"):"ga72",
}

# Status que indicam jogo finalizado ou em andamento com placar disponível
FINISHED_STATUS = {"FINISHED", "AWARDED", "FULL_TIME"}
# Status em andamento — salva placar parcial mas não sobrescreve FINISHED
LIVE_STATUS = {"IN_PLAY", "PAUSED", "HALF_TIME", "EXTRA_TIME", "PENALTY"}

def fetch_matches():
    headers = {
        "X-Auth-Token": FOOTBALL_API_KEY,
        "X-Unfold-Goals": "true",
    }
    resp = requests.get(
        "https://api.football-data.org/v4/competitions/WC/matches",
        headers=headers, timeout=15
    )
    # Log rate limit info
    remaining = resp.headers.get("X-Requests-Available-Minute","?")
    print(f"  API rate limit restante: {remaining}/min")
    resp.raise_for_status()
    return resp.json().get("matches", [])

def get_firebase_token():
    import time, base64
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
    sa = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
    now = int(time.time())
    header  = base64.urlsafe_b64encode(json.dumps({"alg":"RS256","typ":"JWT"}).encode()).rstrip(b"=")
    payload = base64.urlsafe_b64encode(json.dumps({
        "iss":sa["client_email"],"sub":sa["client_email"],
        "aud":"https://oauth2.googleapis.com/token",
        "iat":now,"exp":now+3600,
        "scope":"https://www.googleapis.com/auth/firebase.database https://www.googleapis.com/auth/userinfo.email"
    }).encode()).rstrip(b"=")
    msg = header + b"." + payload
    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None, backend=default_backend())
    sig = base64.urlsafe_b64encode(key.sign(msg, padding.PKCS1v15(), hashes.SHA256())).rstrip(b"=")
    jwt = (msg + b"." + sig).decode()
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type":"urn:ietf:params:oauth:grant-type:jwt-bearer","assertion":jwt
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

def firebase_get(path, token):
    url = f"{FIREBASE_DB_URL}/{path}.json?access_token={token}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json() or {}

def firebase_patch(path, data, token):
    url = f"{FIREBASE_DB_URL}/{path}.json?access_token={token}"
    resp = requests.patch(url, json=data, timeout=15)
    resp.raise_for_status()
    return resp.json()

def main():
    now_utc = datetime.now(timezone.utc)
    # BRT = UTC-3
    now_brt = now_utc.strftime("%Y-%m-%d %H:%M") + " BRT"
    print(f"[{now_utc.isoformat()}] Buscando resultados... (agora: {now_brt[:-4]} UTC-3)")

    matches = fetch_matches()
    print(f"Total de jogos retornados: {len(matches)}")

    # Log dos status existentes
    from collections import Counter
    status_count = Counter(m.get("status","") for m in matches)
    print(f"  Status encontrados: {dict(status_count)}")

    token = get_firebase_token()
    # Busca resultados já salvos no Firebase para não sobrescrever FINISHED com LIVE
    saved = firebase_get("bolao2026/resultados", token)

    updates = {}
    unmapped = []

    for m in matches:
        status = m.get("status","")
        is_finished = status in FINISHED_STATUS
        is_live = status in LIVE_STATUS

        if not is_finished and not is_live:
            continue

        home_en = m.get("homeTeam",{}).get("name","") or m.get("homeTeam",{}).get("shortName","")
        away_en = m.get("awayTeam",{}).get("name","") or m.get("awayTeam",{}).get("shortName","")

        # Pega placar — tenta fullTime, depois regularTime, depois score
        score = m.get("score",{})
        ft = score.get("fullTime",{})
        home_g = ft.get("home")
        away_g = ft.get("away")

        # Fallback para regularTime se fullTime for null
        if home_g is None or away_g is None:
            rt = score.get("regularTime",{})
            home_g = rt.get("home")
            away_g = rt.get("away")

        if home_g is None or away_g is None:
            print(f"  ⚠ Placar nulo [{status}]: {home_en} vs {away_en} | score={score}")
            continue

        home_pt = normalize(home_en)
        away_pt = normalize(away_en)
        if not home_pt or not away_pt:
            unmapped.append(f"{home_en} vs {away_en}")
            continue

        game_id = GAME_IDS.get((home_pt, away_pt))
        if not game_id:
            print(f"  ℹ Sem mapeamento: {home_pt} vs {away_pt}")
            continue

        # Se já temos FINISHED salvo, não sobrescrever com placar parcial

        updates[game_id] = {"c":int(home_g),"f":int(away_g)}
        tag = "✅ FINAL" if is_finished else "🔴 LIVE"
        print(f"  {tag} {home_pt} {home_g}–{away_g} {away_pt} → {game_id}")

    if unmapped:
        print(f"\n⚠ Times não mapeados ({len(unmapped)}):")
        for u in set(unmapped):
            print(f"  - {u}")

    if updates:
        firebase_patch("bolao2026/resultados", updates, token)
        print(f"\n✅ {len(updates)} resultado(s) salvos no Firebase!")
    else:
        print("\nNenhum resultado novo para salvar.")

if __name__ == "__main__":
    main()
