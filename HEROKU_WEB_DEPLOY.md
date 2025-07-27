# 🌐 OneMilX Trading Platform - Heroku Web Deployment

## 🚀 **Sådan deployer du via Heroku Web Interface:**

### **1. Gå til Heroku Dashboard**
- Åbn [dashboard.heroku.com](https://dashboard.heroku.com)
- Login med din konto

### **2. Opret ny app**
- Klik "New" → "Create new app"
- **App name:** `onemilx-trading-platform`
- **Region:** Europe (hvis tilgængelig)
- Klik "Create app"

### **3. Connect til GitHub (valgfrit)**
- I din nye app, gå til "Deploy" tab
- Under "Deployment method" vælg "GitHub"
- Connect din GitHub konto
- Find og vælg dit repository

### **4. Manual Deploy (hvis ikke GitHub)**
- Upload alle filer som ZIP
- Eller brug Heroku CLI senere

### **5. Sæt Environment Variables**
Gå til "Settings" tab → "Config Vars" → "Reveal Config Vars"

Tilføj disse variabler:
```
JWT_SECRET_KEY = your-super-secret-jwt-key-here
FLASK_SECRET_KEY = your-super-secret-flask-key-here
```

### **6. Deploy**
- Klik "Deploy Branch" (hvis GitHub)
- Eller "Deploy" (hvis manual)

## 📋 **Alternative: Installer Git og Heroku CLI**

### **Installer Git:**
```bash
winget install --id=Git.Git
```

### **Installer Heroku CLI (hvis ikke virker):**
```bash
# Download fra: https://devcenter.heroku.com/articles/heroku-cli
# Eller prøv:
winget install --id=Heroku.HerokuCLI
```

### **Efter installation:**
```bash
# Genstart PowerShell
# Login til Heroku
heroku login --api-key HRKU-AAznIygkrnPThvvYLnbI6EFWV0xrL9T2GfjF_LjLY4fA_____wnJnx-JPsF2

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create onemilx-trading-platform
heroku config:set JWT_SECRET_KEY="your-secret-key"
heroku config:set FLASK_SECRET_KEY="your-flask-key"
git push heroku main
```

## 🔧 **Hvis du vil deploye nu:**

### **Option 1: Web Interface (Anbefalet)**
1. Gå til [dashboard.heroku.com](https://dashboard.heroku.com)
2. Opret ny app: `onemilx-trading-platform`
3. Upload filer via "Deploy" tab
4. Sæt environment variables

### **Option 2: Vent på CLI installation**
- Genstart computeren
- Prøv Heroku CLI igen

### **Option 3: Brug GitHub**
1. Upload projekt til GitHub
2. Connect GitHub til Heroku
3. Auto-deploy ved ændringer

## 🎯 **Efter deployment:**
- **URL:** `https://onemilx-trading-platform.herokuapp.com`
- **Admin:** `admin` / `admin123`
- **Invite system** aktiv

## 📞 **Hjælp:**
- Heroku Support: [help.heroku.com](https://help.heroku.com)
- Dokumentation: [devcenter.heroku.com](https://devcenter.heroku.com)

---

**🚀 Din OneMilX Trading Platform er klar til deployment!** 🎯 