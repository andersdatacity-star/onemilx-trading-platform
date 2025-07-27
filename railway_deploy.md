# 🚂 Railway.app Deployment Guide

## 🚀 **Sådan deployer du OneMilX Trading Platform på Railway:**

### **Step 1: Gå til Railway**
1. Åbn [railway.app](https://railway.app)
2. Klik **"Login with GitHub"**
3. Login med din GitHub konto (`andersdatacity-star`)

### **Step 2: Opret nyt projekt**
1. Klik **"New Project"**
2. Vælg **"Deploy from GitHub repo"**
3. Find dit repository: `andersdatacity-star/onemilx-trading-platform`
4. Klik **"Deploy Now"**

### **Step 3: Sæt Environment Variables**
1. I dit projekt, gå til **"Variables"** tab
2. Tilføj disse variabler:
```
JWT_SECRET_KEY = onemilx-super-secret-jwt-key-2024
FLASK_SECRET_KEY = onemilx-super-secret-flask-key-2024
```

### **Step 4: Deploy**
- Railway vil automatisk deploye din app
- Du får en URL som: `https://onemilx-trading-platform-production.up.railway.app`

## ✅ **Fordele ved Railway:**
- **Ingen authentication problemer**
- **Automatisk deployment** fra GitHub
- **Bedre gratis tier** ($5 kredit/måned)
- **Ingen konfiguration** nødvendig
- **Automatisk HTTPS**

## 🎯 **Efter deployment:**
- **URL:** Din Railway URL
- **Admin login:** `admin` / `admin123`
- **Alt virker automatisk**

---

**🚂 Railway er meget nemmere end Heroku!** 🎯 