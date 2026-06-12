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

# Nomes alternativos que a API pode usar
ALIASES = {
    "United States":"EUA","USA":"EUA","United States of America":"EUA",
    "Korea Republic":"Coreia do Sul","Republic of Korea":"Coreia do Sul",
    "Czechia":"Tchéquia","Czech Republic":"Tchéquia",
    "Bosnia & Herzegovina":"Bósnia","Bosnia and Herzegovina":"Bósnia",
    "Ivory Coast":"Costa do Marfim","Côte d'Ivoire":"Costa do Marfim",
    "Curaçao":"Curaçao","Curacao":"Curaçao",
    "DR Congo":"Congo DR","Congo DR":"Congo DR","Democratic Republic of Congo":"Congo DR",
    "New Zealand":"Nova Zelândia","Cape Verde":"Cabo Verde",
    "Saudi Arabia":"Arábia Saudita","South Africa":"África do Sul",
}

def normalize(name):
    """Converte nome em inglês para português."""
    if name in EN_TO_PT:
        return EN_TO_PT[name]
    if name in ALIASES:
        alias = ALIASES[name]
        if alias in TEAM_MAP:
            return alias
        return alias
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

def fetch_matches():
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    # Tenta WC primeiro, depois FIFA World Cup 2026 por ID
    for code in ["WC", "FIFA"]:
        try:
            url = f"https://api.football-data.org/v4/competitions/{code}/matches"
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                matches = resp.json().get("matches", [])
                print(f"  Competição '{code}': {len(matches)} jogos")
                if matches:
                    return matches
        except Exception as e:
            print(f"  Erro em '{code}': {e}")
    # Fallback: lista todas as competições disponíveis
    print("\nListando competições disponíveis na API:")
    resp = requests.get("https://api.football-data.org/v4/competitions", headers=headers, timeout=15)
    if resp.status_code == 200:
        for c in resp.json().get("competitions", []):
            print(f"  {c.get('code','?')} | {c.get('name','?')} | {c.get('id','?')}")
    return []

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

def firebase_patch(path, data, token):
    url = f"{FIREBASE_DB_URL}/{path}.json?access_token={token}"
    resp = requests.patch(url, json=data, timeout=15)
    resp.raise_for_status()
    return resp.json()

def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Buscando resultados...")
    matches = fetch_matches()
    print(f"Total de jogos retornados: {len(matches)}")
    if not matches:
        print("Nenhum jogo encontrado. Verifique o código da competição.")
        return
    token = get_firebase_token()
    updates = {}
    unmapped = []
    for m in matches:
        status = m.get("status","")
        if status not in ("FINISHED","AWARDED"):
            continue
        home_en = m.get("homeTeam",{}).get("name","") or m.get("homeTeam",{}).get("shortName","")
        away_en = m.get("awayTeam",{}).get("name","") or m.get("awayTeam",{}).get("shortName","")
        score   = m.get("score",{})
        full    = score.get("fullTime",{})
        home_g  = full.get("home")
        away_g  = full.get("away")
        if home_g is None or away_g is None:
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
        updates[game_id] = {"c":int(home_g),"f":int(away_g)}
        print(f"  ✅ {home_pt} {home_g}–{away_g} {away_pt} → {game_id}")
    if unmapped:
        print(f"\n⚠ Times não mapeados ({len(unmapped)}):")
        for u in unmapped[:10]:
            print(f"  - {u}")
    if updates:
        firebase_patch("bolao2026/resultados", updates, token)
        print(f"\n✅ {len(updates)} resultado(s) salvos no Firebase!")
    else:
        print("\nNenhum resultado novo para salvar.")

if __name__ == "__main__":
    main()
