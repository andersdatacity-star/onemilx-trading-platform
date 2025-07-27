# 🚀 OneMilX Trading Platform - Heroku Deployment Guide

## 📋 Forudsætninger

1. **Heroku Account** - Opret en gratis konto på [heroku.com](https://heroku.com)
2. **Heroku CLI** - Download og installer fra [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git** - Sørg for at Git er installeret

## 🔧 Deployment Steps

### 1. Installer Heroku CLI
```bash
# Windows (med winget)
winget install --id=Heroku.HerokuCLI

# Eller download fra heroku.com
```

### 2. Login til Heroku
```bash
heroku login
```

### 3. Initialiser Git Repository (hvis ikke allerede gjort)
```bash
git init
git add .
git commit -m "Initial commit for OneMilX Trading Platform"
```

### 4. Opret Heroku App
```bash
heroku create onemilx-trading-platform
```

### 5. Sæt Environment Variables
```bash
heroku config:set JWT_SECRET_KEY="your-super-secret-jwt-key-here"
heroku config:set FLASK_SECRET_KEY="your-super-secret-flask-key-here"
```

### 6. Deploy til Heroku
```bash
git push heroku main
```

### 7. Åbn Appen
```bash
heroku open
```

## 🌐 App URL

Efter deployment vil din app være tilgængelig på:
```
https://onemilx-trading-platform.herokuapp.com
```

## 🔑 Admin Login

- **Brugernavn:** `admin`
- **Password:** `admin123`

## 📊 Platform Features

### ✅ Fungerer på Heroku:
- **Bruger registrering** med invite codes
- **Login/logout system**
- **Admin panel** til at styre brugere
- **Invite management**
- **Dashboard** med mock data
- **Strategy control** (simuleret)

### ❌ Kræver ekstra setup:
- **Real Binance API** - Skal konfigureres med dine API keys
- **Database** - Heroku Postgres tilføjes senere
- **Real trading** - Kræver live API integration

## 🔧 Konfiguration

### Tilføj Binance API (valgfrit):
```bash
heroku config:set BINANCE_API_KEY="din_api_key"
heroku config:set BINANCE_SECRET_KEY="din_secret_key"
```

### Tilføj Heroku Postgres (for production):
```bash
heroku addons:create heroku-postgresql:mini
```

## 📈 Skalering

### Free Tier (Hobby):
- 550-1000 dyno hours/måned
- Perfekt til testing og små projekter

### Paid Plans:
- **Basic:** $7/måned - 24/7 uptime
- **Standard:** $25/måned - Bedre performance
- **Performance:** $250/måned - Dedicated resources

## 🛠️ Troubleshooting

### App crasher:
```bash
heroku logs --tail
```

### Database problemer:
```bash
heroku run python
>>> from user_auth import UserAuth
>>> auth = UserAuth()
```

### Restart app:
```bash
heroku restart
```

## 🔒 Sikkerhed

### Production Best Practices:
1. **Ændr admin password** efter første login
2. **Brug stærke JWT secrets**
3. **Aktiver Heroku SSL**
4. **Sæt up monitoring**

### SSL Certificate:
```bash
heroku certs:auto:enable
```

## 📞 Support

Hvis du har problemer:
1. Tjek logs: `heroku logs --tail`
2. Verificer environment variables: `heroku config`
3. Test lokalt først
4. Kontakt support hvis nødvendigt

---

**🎯 Din OneMilX Trading Platform er nu live på Heroku!** 🚀 