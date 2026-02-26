# ☀️ Energy Smart PV Climate
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blueviolet.svg)

**Energy Smart PV Climate** è un'integrazione per Home Assistant progettata per orchestrare il tuo impianto fotovoltaico, la batteria domestica e il sistema di climatizzazione (AC/Pompe di calore) in un unico ecosistema intelligente.

L'obiettivo è massimizzare l'autoconsumo, proteggere la batteria e garantire il comfort termico e igrometrico senza interventi manuali.

---

## 🚀 Funzionalità Principali

* **⚡ Gestione Surplus PV:** Attivazione automatica dei climatizzatori basata sull'eccesso di energia immessa in rete.
* **🔋 Protezione Batteria:** Evita cicli di scarica inutili bloccando il boost se la batteria è sotto una soglia configurabile.
* **💧 Deumidificazione Smart:** Controllo dell'umidità con isteresi e gestione intelligente per sistemi multi-split.
* **🌡️ Offset Adattivo:** Regolazione della temperatura target in estate basata sulla temperatura esterna.
* **🤖 Multi-Split Sync:** Algoritmo di "voto" per evitare conflitti tra unità interne che condividono la stessa unità esterna (modalità condivisa).
* **📊 UI Dedicata:** Due card Lovelace personalizzate per il controllo granulare o centralizzato.

---

## 🏗️ Architettura del Sistema

L'integrazione crea diverse entità per ogni **Zona** (es. Soggiorno, Camera):

| Entità | Descrizione |
| :--- | :--- |
| `switch.<zone>_auto_mode` | Attiva/Disattiva l'automazione della zona. |
| `select.<zone>_mode` | Selettore stagionale: `Summer`, `Winter` o `Auto`. |
| `sensor.<zone>_status` | Stato operativo (Boosting, Charging Battery, Idle, ecc.). |
| `sensor.<zone>_surplus_power` | Calcolo in tempo reale del surplus disponibile per la zona. |

---

## 🛠️ Installazione

### 1. Copia dei file
Copia la cartella `custom_components/energy_smart_pv_climate` nella cartella `custom_components` del tuo Home Assistant.

Copia i file delle card JS (`energy-smart-pv-card.js` e `energy-smart-pv-unified-card.js`) nella cartella `www` (es. `/config/www/energy_smart_pv/`).

### 2. Configurazione Frontend
Aggiungi le risorse in **Impostazioni > Dashboard > Risorse**:
* `/local/energy_smart_pv/energy-smart-pv-card.js` (Modulo JavaScript)
* `/local/energy_smart_pv/energy-smart-pv-unified-card.js` (Modulo JavaScript)

### 3. Setup Integrazione
Vai su **Impostazioni > Dispositivi e Servizi > Aggiungi Integrazione** e cerca `Energy Smart PV Climate`.
* **Prima zona:** Configura i sensori globali (Grid, Batteria, Meteo).
* **Zone successive:** I sensori globali verranno ereditati automaticamente.

---

## 🧠 Logica di Controllo

### Gestione Energia
* **Boost:** Si attiva se il surplus > `export_threshold`.
* **Stop:** Si disattiva se il surplus scende sotto i 100W (con protezione anti-ciclo di 5 min).
* **Priorità Batteria:** Se la batteria < `min_battery_level`, l'AC si spegne immediatamente per favorire la carica.

### Logica Multi-Split (Smart Voting)
Per le unità esterne condivise, il sistema gestisce i conflitti:
1.  **Votazione:** Le zone votano tra `HEAT` e `DRY/COOL` in base all'umidità.
2.  **Veto Invernale:** Se anche solo una zona ha il flag "Winter Dehumidification" disattivato, l'intero gruppo non entrerà in modalità deumidificazione per evitare raffreddamenti indesiderati.

---

## 🖼️ Interfaccia Grafica (Lovelace)

### Single-Zone Card
Dedicata al controllo di precisione di una singola stanza. Permette di regolare soglie di umidità, batteria e attivare i flag di condivisione.

### Unified Card
Una dashboard compatta per vedere lo stato di tutta la casa, con un "Eco Score" globale e accesso rapido ai parametri di ogni zona.

---

## 🤝 Contribuire
Le pull request sono benvenute! Per modifiche importanti, apri prima un'issue per discutere cosa vorresti cambiare.

---

*Developed with ❤️ to optimize your self-consumption.*
