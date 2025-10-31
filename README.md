# Systém pro správu faktur a API pro správu položek

Tento projekt obsahuje dvě samostatné aplikace:

1. **Systém pro správu faktur** - Kompletní systém pro správu faktur s autentizací a reporty
2. **API pro správu položek** - REST API s dokumentací Swagger pro správu položek (úkoly/produkty)

## GitHub repozitář

Repozitář je dostupný na GitHubu a obsahuje kompletní README.md s popisem API.

## Požadavky

- Python 3.8 nebo vyšší
- pip (správce balíčků pro Python)
- Windows, macOS nebo Linux

## Instalace

1. Nainstalujte požadované závislosti:
```bash
pip install -r requirements.txt
```

## Spuštění aplikací

### 1. Systém pro správu faktur

Pro spuštění systému pro správu faktur:
```bash
python main.py
```

Aplikace se spustí na adrese `http://localhost:80`

Funkce:
- Autentizace s rolí (majitel, účetní)
- CRUD operace pro faktury
- Reporty pro nezaplacené faktury, největší dlužníky, průměrnou dobu úhrady a faktury po splatnosti
- Automatický výpočet data splatnosti (14 dní po datu vystavení)

Výchozí přihlašovací údaje:
- Majitel: uživatelské jméno 'owner', heslo 'owner123'
- Účetní: uživatelské jméno 'accountant', heslo 'accountant123'

### 2. API pro správu položek se Swaggerem

Pro spuštění REST API pro správu položek s dokumentací Swagger:
```bash
python app_api.py
```

Aplikace se spustí na adrese `http://localhost:5000`

Funkce:
- RESTful API pro správu položek (úkoly/produkty)
- Dokumentace Swagger/OpenAPI dostupná na adrese `http://localhost:5000/api/`
- Webové rozhraní pro ukázku funkčnosti API
- Endpoint `/api` s Swagger dokumentací

## Testování

### Systém pro správu faktur
```bash
python test_invoices.py
```

### API pro správu položek
```bash
python run_tests.py
```

Nebo spusťte testy přímo:
```bash
python -m pytest test_items_api.py -v
```

## API endpointy

### Systém pro správu faktur
- `POST /api/login` - Přihlášení
- `POST /api/logout` - Odhlášení
- `GET /api/me` - Získání informací o aktuálním uživateli
- `GET /api/invoices` - Získání všech faktur
- `POST /api/invoices` - Vytvoření nové faktury
- `GET /api/invoices/{id}` - Získání konkrétní faktury
- `PUT /api/invoices/{id}` - Aktualizace faktury
- `DELETE /api/invoices/{id}` - Smazání faktury (pouze pro majitele)
- `GET /api/reports/unpaid` - Získání nezaplacených faktur
- `GET /api/reports/largest-debtors` - Získání největších dlužníků
- `GET /api/reports/average-payment-time` - Získání průměrné doby úhrady
- `GET /api/reports/overdue` - Získání faktur po splatnosti

### API pro správu položek
- `GET /api/items` - Získání seznamu položek
- `POST /api/items` - Vytvoření nové položky
- `GET /api/items/{id}` - Získání konkrétní položky
- `PUT /api/items/{id}` - Aktualizace položky
- `DELETE /api/items/{id}` - Smazání položky

## Použité technologie

- Python
- Flask
- Flask-SQLAlchemy
- Flask-RestX (pro dokumentaci Swagger)
- SQLite
