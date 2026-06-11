import os
import json
import requests
from datetime import datetime, timezone

# ─── CONFIGURAÇÃO ────────────────────────────────────────────────────────────
FOOTBALL_API_KEY = os.environ["FOOTBALL_API_KEY"]
FIREBASE_DB_URL  = "https://copa-2026-album-79fb4-default-rtdb.firebaseio.com"

# Mapa: fixture id da API → id interno do bolão
# football-data.org: competição FIFA World Cup 2026 = WC (code)
# Vamos buscar todos os jogos da competição e mapear pelo nome dos times

# Nomes em português (bolão) → nomes em inglês (API)
TEAM_MAP = {
    "México":           "Mexico",
    "África do Sul":    "South Africa",
    "Coreia do Sul":    "South Korea",
    "Tchéquia":         "Czech Republic",
    "Canadá":           "Canada",
    "Bósnia":           "Bosnia and Herzegovina",
    "Catar":            "Qatar",
    "Suíça":            "Switzerland",
    "Brasil":           "Brazil",
    "Marrocos":         "Morocco",
    "Haiti":            "Haiti",
    "Escócia":          "Scotland",
    "EUA":              "USA",
    "Paraguai":         "Paraguay",
    "Austrália":        "Australia",
    "Turquia":          "Turkey",
    "Alemanha":         "Germany",
    "Curaçao":          "Curacao",
    "Costa do Marfim":  "Ivory Coast",
    "Equador":          "Ecuador",
    "Holanda":          "Netherlands",
    "Japão":            "Japan",
    "Suécia":           "Sweden",
    "Tunísia":          "Tunisia",
    "Bélgica":          "Belgium",
    "Egito":            "Egypt",
    "Irã":              "Iran",
    "Nova Zelândia":    "New Zealand",
    "Espanha":          "Spain",
    "Cabo Verde":       "Cape Verde",
    "Arábia Saudita":   "Saudi Arabia",
    "Uruguai":          "Uruguay",
    "França":           "France",
    "Senegal":          "Senegal",
    "Iraque":           "Iraq",
    "Noruega":          "Norway",
    "Argentina":        "Argentina",
    "Argélia":          "Algeria",
    "Áustria":          "Austria",
    "Jordânia":         "Jordan",
    "Portugal":         "Portugal",
    "Congo DR":         "DR Congo",
    "Uzbequistão":      "Uzbekistan",
    "Colômbia":         "Colombia",
    "Inglaterra":       "England",
    "Croácia":          "Croatia",
    "Gana":             "Ghana",
    "Panamá":           "Panama",
}

# Inverte: inglês → português
EN_TO_PT = {v: k for k, v in TEAM_MAP.items()}

# IDs internos do bolão: (casa_pt, fora_pt) → game_id
GAME_IDS = {
    ("México","África do Sul"):     "ga1",
    ("Coreia do Sul","Tchéquia"):   "ga2",
    ("Canadá","Bósnia"):            "ga3",
    ("EUA","Paraguai"):             "ga4",
    ("Catar","Suíça"):              "ga5",
    ("Brasil","Marrocos"):          "ga6",
    ("Haiti","Escócia"):            "ga7",
    ("Austrália","Turquia"):        "ga8",
    ("Alemanha","Curaçao"):         "ga9",
    ("Holanda","Japão"):            "ga10",
    ("Costa do Marfim","Equador"):  "ga11",
    ("Suécia","Tunísia"):           "ga12",
    ("Espanha","Cabo Verde"):       "ga13",
    ("Bélgica","Egito"):            "ga14",
    ("Arábia Saudita","Uruguai"):   "ga15",
    ("Irã","Nova Zelândia"):        "ga16",
    ("França","Senegal"):           "ga17",
    ("Iraque","Noruega"):           "ga18",
    ("Argentina","Argélia"):        "ga19",
    ("Áustria","Jordânia"):         "ga20",
    ("Portugal","Congo DR"):        "ga21",
    ("Inglaterra","Croácia"):       "ga22",
    ("Gana","Panamá"):              "ga23",
    ("Uzbequistão","Colômbia"):     "ga24",
    ("Tchéquia","África do Sul"):   "ga25",
    ("Suíça","Bósnia"):             "ga26",
    ("Canadá","Catar"):             "ga27",
    ("México","Coreia do Sul"):     "ga28",
    ("EUA","Austrália"):            "ga29",
    ("Escócia","Marrocos"):         "ga30",
    ("Brasil","Haiti"):             "ga31",
    ("Turquia","Paraguai"):         "ga32",
    ("Holanda","Suécia"):           "ga33",
    ("Alemanha","Costa do Marfim"): "ga34",
    ("Equador","Curaçao"):          "ga35",
    ("Tunísia","Japão"):            "ga36",
    ("Espanha","Arábia Saudita"):   "ga37",
    ("Bélgica","Irã"):              "ga38",
    ("Uruguai","Cabo Verde"):       "ga39",
    ("Nova Zelândia","Egito"):      "ga40",
    ("Argentina","Áustria"):        "ga41",
    ("França","Iraque"):            "ga42",
    ("Noruega","Senegal"):          "ga43",
    ("Jordânia","Argélia"):         "ga44",
    ("Portugal","Uzbequistão"):     "ga45",
    ("Inglaterra","Gana"):          "ga46",
    ("Panamá","Croácia"):           "ga47",
    ("Colômbia","Congo DR"):        "ga48",
    ("Suíça","Canadá"):             "ga49",
    ("Bósnia","Catar"):             "ga50",
    ("Escócia","Brasil"):           "ga51",
    ("Marrocos","Haiti"):           "ga52",
    ("Tchéquia","México"):          "ga53",
    ("África do Sul","Coreia do Sul"): "ga54",
    ("Equador","Alemanha"):         "ga55",
    ("Curaçao","Costa do Marfim"):  "ga56",
    ("Japão","Suécia"):             "ga57",
    ("Tunísia","Holanda"):          "ga58",
    ("Turquia","EUA"):              "ga59",
    ("Paraguai","Austrália"):       "ga60",
    ("Noruega","França"):           "ga61",
    ("Senegal","Iraque"):           "ga62",
    ("Cabo Verde","Arábia Saudita"): "ga63",
    ("Uruguai","Espanha"):          "ga64",
    ("Egito","Irã"):                "ga65",
    ("Nova Zelândia","Bélgica"):    "ga66",
    ("Panamá","Inglaterra"):        "ga67",
    ("Croácia","Gana"):             "ga68",
    ("Colômbia","Portugal"):        "ga69",
    ("Congo DR","Uzbequistão"):     "ga70",
    ("Argélia","Áustria"):          "ga71",
    ("Jordânia","Argentina"):       "ga72",
}

# ─── BUSCAR JOGOS DA API ──────────────────────────────────────────────────────
def fetch_matches():
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    # Código da Copa do Mundo 2026 na football-data.org
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json().get("matches", [])

# ─── FIREBASE REST API (sem SDK, só HTTP) ─────────────────────────────────────
def get_firebase_token():
    """Gera um access token via Google OAuth2 usando a service account."""
    import time
    import base64
    import hashlib
    import hmac
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend

    sa = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
    
    now = int(time.time())
    header = base64.urlsafe_b64encode(json.dumps({"alg":"RS256","typ":"JWT"}).encode()).rstrip(b"=")
    payload = base64.urlsafe_b64encode(json.dumps({
        "iss": sa["client_email"],
        "sub": sa["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
        "scope": "https://www.googleapis.com/auth/firebase.database https://www.googleapis.com/auth/userinfo.email"
    }).encode()).rstrip(b"=")
    
    msg = header + b"." + payload
    
    key = serialization.load_pem_private_key(
        sa["private_key"].encode(),
        password=None,
        backend=default_backend()
    )
    sig = key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=")
    
    jwt = (msg + b"." + sig_b64).decode()
    
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

def firebase_patch(path, data, token):
    url = f"{FIREBASE_DB_URL}/{path}.json?access_token={token}"
    resp = requests.patch(url, json=data, timeout=15)
    resp.raise_for_status()
    return resp.json()

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Buscando resultados...")
    
    matches = fetch_matches()
    print(f"Total de jogos retornados pela API: {len(matches)}")
    
    token = get_firebase_token()
    
    updates = {}
    updated_count = 0
    
    for m in matches:
        status = m.get("status", "")
        # Só processa jogos finalizados
        if status not in ("FINISHED", "AWARDED"):
            continue
        
        home_en = m.get("homeTeam", {}).get("name", "")
        away_en = m.get("awayTeam", {}).get("name", "")
        score   = m.get("score", {})
        full    = score.get("fullTime", {})
        home_g  = full.get("home")
        away_g  = full.get("away")
        
        if home_g is None or away_g is None:
            continue
        
        # Converte nomes para português
        home_pt = EN_TO_PT.get(home_en)
        away_pt = EN_TO_PT.get(away_en)
        
        if not home_pt or not away_pt:
            print(f"  ⚠ Time não mapeado: {home_en} vs {away_en}")
            continue
        
        game_id = GAME_IDS.get((home_pt, away_pt))
        if not game_id:
            # Tenta knockout sem times fixos (TBD)
            print(f"  ℹ Jogo não mapeado nos grupos: {home_pt} vs {away_pt}")
            continue
        
        updates[game_id] = {"c": int(home_g), "f": int(away_g)}
        print(f"  ✅ {home_pt} {home_g}–{away_g} {away_pt} → {game_id}")
        updated_count += 1
    
    if updates:
        firebase_patch("bolao2026/resultados", updates, token)
        print(f"\n✅ {updated_count} resultado(s) salvos no Firebase!")
    else:
        print("\nNenhum resultado novo para salvar.")

if __name__ == "__main__":
    main()
