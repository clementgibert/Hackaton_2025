# 🛡️ AntiTriche - Système de Surveillance d'Examen

> **Un système de surveillance automatique pour examens en ligne avec interface graphique moderne**


---

## 🎯 Aperçu

**AntiTriche** est un logiciel de surveillance conçu pour maintenir l'intégrité des examens en ligne. Il surveille en temps réel les activités suspectes et génère des rapports détaillés pour les superviseurs.

### 🎪 Démonstration

```bash
# Installation simple
git clone ........
cd antitriche
python antitriche.py
```

---

## ✨ Fonctionnalités

### 🔍 Surveillance en Temps Réel

| Fonctionnalité | Description | Status |
|---|---|---|
| **🚫 Processus Interdits** | Détection des applications non autorisées | ✅ |
| **🌐 Surveillance Web** | Monitoring des sites visités dans les navigateurs | ✅ |
| **📋 Presse-papiers** | Surveillance des opérations copier/coller | ✅ |
| **💾 Périphériques USB** | Détection des nouvelles connexions | ✅ |
| **📸 Captures d'écran** | Screenshots automatiques lors des violations | ✅ |
| **📝 Logs Détaillés** | Journal complet des événements | ✅ |

### 🖥️ Interface Utilisateur

- **Interface Tkinter** moderne et intuitive
- **Configuration personnalisable** des règles de surveillance
- **Statistiques en temps réel** avec timer d'examen
- **Alertes visuelles** lors des violations détectées
- **Gestion centralisée** des rapports et logs

### 📊 Rapports et Analytics

- **Rapports JSON** détaillés avec horodatage
- **Captures d'écran** automatiques des violations
- **Logs rotatifs** avec différents niveaux (INFO, WARNING, ERROR)
- **Statistiques d'examen** complètes
- **Export des données** pour analyse

---

## 📸 Captures d'écran

### Interface principale
```
┌─────────────────────────────────────────────────────────────┐
│  📚 Surveillant d'Examen - Version Étudiant                 │
├─────────────────────────────────────────────────────────────┤
│  Configuration de l'Examen                                  │
│  ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│  │ Nom étudiant:   │ │ Jean Dupont                         │ │
│  │ ID examen:      │ │ EXAM_2025_001                       │ │
│  └─────────────────┘ └─────────────────────────────────────┘ │
│                                                             │
│  [Démarrer l'Examen] [Arrêter l'Examen] [Configuration]    │
│                                                             │
│  Statut: 🟢 Surveillance ACTIVE - Examen en cours          │
│                                                             │
│  Journal de Surveillance                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [14:30:25] INFO: Examen démarré pour Jean Dupont       │ │
│  │ [14:35:12] VIOLATION: Site interdit détecté: google    │ │
│  │ [14:40:08] INFO: Capture d'écran prise                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  Violations détectées: 2    Temps d'examen: 01:23:45       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation Rapide

### Prérequis

- **Windows 10/11** (64-bit)
- **Python 3.8+** 
- **Droits administrateur** (recommandé)

### Option 1: Installation Automatique (Recommandée)

```bash
# 1. Cloner le repository
git clone ........
cd antitriche

# 2. Exécuter le script d'installation
install_and_build.bat
```

### Option 2: Installation Manuelle

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
python antitriche.py
```

### Option 3: Exécutable Standalone

```bash
# 1. Télécharger la release
# 2. Extraire AntiTriche.exe
# 3. Double-cliquer pour lancer
```

#### 📦 Dépendances Python

```bash
psutil>=5.9.0      # Monitoring système
pyautogui>=0.9.54  # Capture d'écran
pywin32>=305       # APIs Windows
Pillow>=10.0.0     # Traitement d'images
```

---

## 💻 Utilisation

### 🎬 Démarrage Rapide

1. **Lancement**
   ```bash
   python antitriche.py
   # ou double-clic sur AntiTriche.exe
   ```

2. **Configuration**
   - Saisir le **nom de l'étudiant**
   - Entrer l'**ID de l'examen**
   - Cliquer **"Démarrer l'Examen"**

3. **Surveillance**
   - La surveillance démarre automatiquement
   - Toutes les activités sont loggées en temps réel
   - Les violations déclenchent des alertes

4. **Fin d'examen**
   - Cliquer **"Arrêter l'Examen"**
   - Un rapport JSON est généré automatiquement

### ⚙️ Configuration Avancée

Cliquez sur **"Configuration"** pour personnaliser :

- **Mots-clés interdits** (sites web)
- **Processus surveillés** (applications)
- **Paramètres de capture** d'écran
- **Intervalles de vérification**
- **Niveaux de logging**

---

## 📊 Rapports et Données

### 📁 Structure des Fichiers

```
antitriche/
├── antitriche.py                    # Application principale
├── config.json                      # Configuration
├── requirements.txt                 # Dépendances
├── 📂 reports/                     # Rapports d'examen
│   ├── rapport_EXAM001_20250702_143025.json
│   └── rapport_EXAM002_20250702_150130.json
├── 📂 screenshots/                 # Captures d'écran
│   ├── EXAM001_20250702_152210_VIOLATION.png
│   └── EXAM001_20250702_153015_SUSPICIOUS.png
├── 📂 logs/                        # Logs système
│   └── exam_monitor.log
└── 📂 dist/                        # Exécutable (après build)
    └── AntiTriche.exe
```

### 📋 Format des Rapports JSON

```json
{
  "student_name": "Jean Dupont",
  "exam_id": "EXAM_2025_001",
  "start_time": "2025-07-02T14:30:25.123456",
  "end_time": "2025-07-02T16:45:30.789012",
  "duration": "2:15:05",
  "total_violations": 3,
  "violations": [
    {
      "timestamp": "2025-07-02T15:22:10.456789",
      "type": "SITE_INTERDIT",
      "description": "Site interdit détecté: google dans 'Google - Recherche'",
      "screenshot": "screenshots/EXAM001_20250702_152210_SITE_INTERDIT.png"
    }
  ],
  "config": { /* Configuration utilisée */ }
}
```

### 🔍 Analyse des Rapports

```bash
# Utiliser l'outil d'analyse inclus
python find_reports.py

# Ou explorer manuellement
cd reports/
ls -la *.json
```

---

## ⚙️ Configuration

### 🎛️ Paramètres par Défaut

| Paramètre | Valeur | Description |
|---|---|---|
| `check_interval` | 5 secondes | Fréquence de surveillance |
| `screenshot_on_violation` | `true` | Capture automatique |
| `monitor_usb` | `true` | Surveillance USB |
| `block_clipboard` | `true` | Monitoring presse-papiers |
| `violation_cooldown` | 30 secondes | Anti-spam des alertes |

### 🚫 Éléments Surveillés

#### Sites Web Interdits (par défaut)
```json
[
  "chatgpt", "claude", "bard", "copilot",
  "google", "stackoverflow", "discord",
  "whatsapp", "facebook", "youtube",
  "gmail", "outlook", "teams", "zoom"
]
```

#### Processus Interdits (par défaut)
```json
[
  "discord.exe", "whatsapp.exe", "telegram.exe",
  "teams.exe", "zoom.exe", "notepad++.exe",
  "code.exe", "pycharm64.exe", "spotify.exe"
]
```

---

## 🛠️ Développement

### 🏗️ Architecture

```
antitriche.py
├── ExamMonitor (classe principale)
│   ├── UI Setup (interface Tkinter)
│   ├── Monitoring Loop (surveillance)
│   ├── Violation Detection (détection)
│   └── Report Generation (rapports)
├── ConfigWindow (configuration)
└── Utilities (utilitaires)
```

### 🧪 Build et Distribution

#### Créer un Exécutable

```bash
# Build automatique
python build.py

# Build manuel
pyinstaller --onefile --windowed --name "AntiTriche" antitriche.py

# Build optimisé
pyinstaller --onefile --windowed --strip --exclude-module unittest antitriche.py
```

#### Tests

```bash
# Tests manuels recommandés
python antitriche.py

# Vérification des dépendances
python -c "import psutil, pyautogui, win32gui; print('✅ OK')"
```

### 🐛 Debugging

#### Logs de Debug

```python
# Activer le mode debug dans config.json
{
  "logging": {
    "level": "DEBUG",
    "console_output": true
  }
}
```

#### Mode Console

```bash
# Build avec console pour debug
pyinstaller --onefile --console antitriche.py
```

---

## 🤝 Contribution

### 🌟 Comment Contribuer

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### 📝 Guidelines

- **Code Style**: PEP 8
- **Comments**: En français
- **Tests**: Manuels requis
- **Documentation**: Mettre à jour le README

### 🚀 Roadmap

- [ ] **Interface Web** moderne (React/Flask)
- [ ] **Support multi-plateforme** (Linux, macOS)
- [ ] **Base de données** centralisée
- [ ] **API REST** pour intégration LMS
- [ ] **Reconnaissance faciale**
- [ ] **Mode kiosque** complet
- [ ] **Surveillance réseau**
- [ ] **Machine Learning** pour détection d'anomalies

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

```
MIT License

Copyright (c) 2025 [Votre Nom]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Remerciements

- **Communauté Python** pour les excellentes bibliothèques
- **Contributeurs** et testeurs du projet
- **Institutions éducatives** pour les retours d'expérience
- **Open Source Community** pour l'inspiration

---

## 📞 Support et Contact

### 🆘 Besoin d'Aide ?

- **🐛 Issues**: [GitHub Issues](https://github.com/votre-username/antitriche/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/votre-username/antitriche/discussions)
- **📧 Email**: votre.email@domain.com
- **📖 Wiki**: [Documentation complète](https://github.com/votre-username/antitriche/wiki)

### 🔗 Liens Utiles

- [📥 Dernière Release](https://github.com/votre-username/antitriche/releases/latest)
- [📊 Project Board](https://github.com/votre-username/antitriche/projects)
- [🏷️ Tags & Versions](https://github.com/votre-username/antitriche/tags)

---

<div align="center">

**⭐ N'oubliez pas de mettre une étoile si ce projet vous a aidé ! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/votre-username/antitriche.svg?style=social&label=Star)](https://github.com/votre-username/antitriche)
[![GitHub forks](https://img.shields.io/github/forks/votre-username/antitriche.svg?style=social&label=Fork)](https://github.com/votre-username/antitriche/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/votre-username/antitriche.svg?style=social&label=Watch)](https://github.com/votre-username/antitriche)

---

**🛡️ Fait avec ❤️ pour l'intégrité académique**

</div>
