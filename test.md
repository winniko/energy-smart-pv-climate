# ☀️ Energy Smart PV Climate per Home Assistant

Questo Custom Component per Home Assistant ottimizza in modo intelligente l'uso dei tuoi climatizzatori (e termostati) basandosi sulla reale produzione del tuo impianto fotovoltaico e sullo stato della batteria di accumulo.

Il sistema massimizza l'autoconsumo gestendo automaticamente:
* **Riscaldamento (Inverno):** Attiva i climatizzatori quando c'è esubero solare o la batteria è sufficientemente carica, supportando anche il termostato della caldaia.
* **Raffrescamento (Estate):** Mantiene la casa fresca sfruttando l'energia solare gratuita, con offset adattivi basati sulla temperatura esterna.
* **Deumidificazione Intelligente:** Gestisce l'umidità in eccesso con logiche avanzate, proteggendo i sistemi multisplit da conflitti di modalità.

---

## ⚠️ ATTENZIONE: Card Lovelace (Frontend)
Per mantenere il codice pulito e performante, **le interfacce grafiche personalizzate sono state separate da questa integrazione**. 

Per visualizzare le card (`energy-smart-pv-card` e `energy-smart-pv-unified-card`) nella tua dashboard, devi installare il componente frontend dedicato:
👉 **[INSERISCI QUI IL LINK AL REPO DELLE TUE CARD JS]**

*Se usi HACS, troverai il frontend aggiungendo il link sopra come repository personalizzato di tipo "Lovelace / Interfaccia".*

---

## 🚀 Funzionalità Principali

### 1. Gestione Automatica Fotovoltaico e Batteria
* **Attivazione su Surplus:** Se esporti energia in rete oltre la soglia impostata (es. 2000W), il clima si accende.
* **Protezione Batteria:** Spegne *immediatamente* i dispositivi se la batteria scende sotto la soglia minima impostata (priorità alla ricarica della casa).
* **Spegnimento Intelligente & Eco Mode (🍃):** Se il sole viene coperto da una nuvola, il sistema NON spegne subito il clima (evitando dannosi on/off). Attende 5 minuti e poi entra in modalità **Eco** per un massimo di 60 minuti, modulando la temperatura target in base a quella ambiente per ridurre i consumi al minimo. Spegne definitivamente solo dopo 1 ora di assenza di sole.

### 2. Logica di Gruppo e Sincronizzazione (Multisplit)
Se hai più climatizzatori configurati con la **"Deumidificazione Condivisa"**, il sistema previene conflitti tecnici (es. una macchina in Caldo e l'altra in Deumidificazione, che bloccherebbero l'unità esterna):
* **Voto Intelligente:** Il sistema decide la modalità (HEAT, COOL o DRY) contando le reali necessità di ogni stanza in base all'umidità. Vince la maggioranza e tutto il gruppo si allinea.
* **Veto Invernale:** Se anche *una sola* stanza ha la spunta "Deumidificazione in Inverno" disattivata, l'intero gruppo non andrà mai in deumidificazione, garantendo il riscaldamento prioritario.

### 3. Offset Adattivi
* **Inverno:** Se usi il clima in supporto ai termosifoni, il setpoint del clima diventa dinamicamente `Temperatura Termostato + Offset Boost`.
* **Estate:** Usa un sensore di temperatura esterna per calcolare un setpoint adattivo, evitando di raffreddare troppo quando fuori non fa caldissimo.

---

## 🛠 Installazione

### Tramite HACS (Consigliato)
1. Apri **HACS** in Home Assistant.
2. Vai su **Integrazioni** > clicca sui tre puntini in alto a destra > **Repository personalizzati**.
3. Incolla l'URL di questo repository e scegli la categoria **Integrazione**.
4. Clicca su **Scarica**.
5. Riavvia Home Assistant.

### Manuale
1. Scarica il repository.
2. Copia l'intera cartella `custom_components/energy_smart_pv` all'interno della cartella `custom_components` della tua installazione di Home Assistant.
3. Riavvia Home Assistant.

---

## ⚙️ Configurazione

L'integrazione si configura interamente da interfaccia grafica (UI). Nessun file YAML da modificare!

1. Vai su **Impostazioni** > **Dispositivi e Servizi** > **Aggiungi Integrazione**.
2. Cerca **Energy Smart PV Climate**.
3. Compila i campi richiesti:
   * **Sensore Immissione (Grid):** Il sensore che legge l'esubero (in negativo o positivo a seconda dell'inverter).
   * **Sensore Batteria (%):** Opzionale, per la protezione scarica.
   * **Climatizzatore / Split:** L'entità `climate` da comandare.
   * **Termostato Caldaia:** Opzionale, se vuoi creare logiche combinate in inverno.
   * **Soglie & Temperature:** Definisci a quanti Watt far partire il sistema e le temperature base per estate/inverno.

*Nota: Puoi configurare questa integrazione più volte (creando più istanze), una per ogni stanza/split della tua casa.*

---

## ❓ Domande Frequenti (FAQ)

**Q: Cos'è l'Eco Mode (Foglia Verde 🍃)?**
Quando l'esubero solare scende sotto i 100W (es. nuvola, tramonto), il sistema non spegne subito per preservare il compressore. 
1. Attende 5 minuti per confermare il calo di produzione.
2. Attiva la modalità Eco: regola la temperatura target di ±2°C rispetto all'ambiente per ridurre drasticamente l'assorbimento elettrico.
3. Se il sole torna, ripristina la potenza piena. Se non torna entro 60 minuti, spegne il clima.

**Q: Quando si spegne esattamente il condizionatore?**
In due casi principali: se la batteria di accumulo scende sotto la percentuale minima da te impostata (es. 50%), o se la modalità Eco dura per più di 60 minuti consecutivi.

**Q: Come funziona la deumidificazione condivisa?**
Utile per chi ha sistemi multisplit con un singolo motore esterno. Se attivata su più zone, le macchine "votano". Se la maggioranza delle stanze supera la soglia di umidità, tutte passano in DRY (Deumidificazione). Altrimenti, restano in HEAT/COOL. Evita blocchi dell'unità esterna per richieste discordanti.

**Q: Cosa fa l'opzione "Deumidificazione in Inverno"?**
Spesso deumidificare in inverno abbassa troppo la temperatura della stanza. Se disattivi questa spunta, quella stanza non entrerà mai in DRY. Se fa parte di un gruppo condiviso, la sua assenza funge da "Veto", bloccando la deumidificazione anche per le altre stanze del gruppo per garantire il riscaldamento.
