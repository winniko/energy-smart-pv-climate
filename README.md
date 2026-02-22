# energy-smart-pv-climate
hhh
# Energy Smart PV Climate – Gestione intelligente esubero fotovoltaico e climatizzazione

Energy Smart PV Climate è una integrazione personalizzata per Home Assistant pensata per:

- sfruttare automaticamente l’esubero fotovoltaico per alimentare i climatizzatori (split),
- proteggere e gestire in modo furbo la **batteria di accumulo**,
- migliorare il comfort grazie alla **deumidificazione automatica**, con logiche specifiche per impianti **multi‑split**,
- offrire un’interfaccia grafica completa tramite due card Lovelace:
  - **card singola di zona** (`energy-smart-pv-card.js`),
  - **card unificata** per più zone (`energy-smart-pv-unified-card.js`).

---

## Architettura generale

- **Integrazione Home Assistant** (`custom_components/energy_smart_pv`):
  - una **configurazione per ogni zona** (es. Living, Cameretta, Padronale),
  - per ogni zona vengono create le entità:
    - `sensor.<zona>_status`
    - `sensor.<zona>_surplus_power`
    - `switch.<zona>_auto_mode`
    - `select.<zona>_mode`
- **Card Lovelace**:
  - `energy-smart-pv-card` → vista dettagliata di una singola zona,
  - `energy-smart-pv-unified-card` → riepilogo e controlli rapidi per più zone.

La logica di controllo gira dentro Home Assistant, legge i sensori (rete, batteria, umidità, temperatura, ecc.) e comanda i climatizzatori tramite le entità `climate`.

---

## Installazione

### 1. Copia dei file

Nel server Home Assistant:

- cartella personalizzata:
  - copia la cartella `custom_components/energy_smart_pv` in:
    - `/config/custom_components/energy_smart_pv`
- file delle card:
  - copia i file:
    - `energy-smart-pv-card.js`
    - `energy-smart-pv-unified-card.js`
  - nella cartella frontend usata per le risorse (tipicamente `/config/www/`).

### 2. Aggiunta delle risorse Lovelace

In Home Assistant:

- Impostazioni → Dashboard → Risorse (Resources) → Aggiungi risorsa:
  - `/local/energy-smart-pv-card.js` – tipo: `JavaScript module`
  - `/local/energy-smart-pv-unified-card.js` – tipo: `JavaScript module`

Riavvia Home Assistant se necessario.

---

## Configurazione integrazione

### 1. Prima zona (obbligatoria)

Impostazioni → Dispositivi e servizi → Aggiungi integrazione → cerca **Energy Smart PV Climate**.

Per la **prima zona** devi indicare:

- **Nome zona** (es. “Living”).
- **Sensori principali**:
  - `grid_sensor`: sensore di potenza verso la rete (positivo in immissione / export),
  - `battery_sensor` (opzionale ma consigliato): livello batteria in %,
  - `outdoor_temp_sensor` (opzionale): temperatura esterna,
  - `outdoor_humidity_sensor` (opzionale): umidità esterna,
  - `ac_power_sensor` (opzionale): consumo elettrico del climatizzatore (W).
- **Climatizzatori**:
  - `climate_ac`: split/clima della zona,
  - `climate_heater` (opzionale): termostato caldaia / riscaldamento ambiente.
- **Parametri base**:
  - `export_threshold`: soglia di esubero (W) per attivare il boost,
  - `min_battery_level`: livello minimo batteria (%) per consentire il boost,
  - `summer_temp`: temperatura target base in estate (°C),
  - `winter_temp`: temperatura base in inverno (°C),
  - `humidity_threshold`: soglia umidità interna per attivare la deumidificazione (%).

### 2. Zone successive

Per le zone successive (es. Cameretta, Padronale):

- l’integrazione **riutilizza automaticamente**:
  - sensore rete (`grid_sensor`),
  - batteria (`battery_sensor`),
  - sensori esterni (temperatura/umidità),
  - eventuale sensore potenza AC,
- ti chiede solo:
  - nome zona,
  - climatizzatore della zona,
  - eventuale termostato della zona,
  - parametri specifici della zona (soglie, temperature, umidità, ecc.).

---

## Entità create

Per ogni zona, l’integrazione crea:

- `switch.<zona>_auto_mode`  
  - controlla se l’automazione della zona è **attiva** o **disabilitata**.
- `select.<zona>_mode`  
  - selettore stagione:
    - `Summer (Cooling)`
    - `Winter (Heating)`
    - `Auto`
- `sensor.<zona>_status`  
  - stato del sistema:
    - `Disabled` – automazione disabilitata,
    - `Boosting (Using Excess)` – in uso esubero,
    - `Charging Battery` – priorità alla ricarica,
    - `Idle (Monitoring)` – in attesa.
  - espone molti attributi utilizzati dalle card:
    - `surplus_power`, `battery_level`, `ac_power`,
    - soglie configurate (min_battery_level, export_threshold, ecc.),
    - entità legate (ac_entity, heater_entity, switch_entity, select_entity),
    - parametri umidità (`current_humidity`, `humidity_threshold`, `is_dehumidifying`),
    - flag `shared_dehumidification`.
- `sensor.<zona>_surplus_power`  
  - surplus calcolato (W) associato alla zona.

---

## Logica di controllo: esubero e batteria

### Surplus (esubero) e soglia di attivazione

- L’integrazione legge il **sensore di potenza verso rete** (`grid_sensor`).
- Se il valore supera `export_threshold` per un certo tempo:
  - considera che c’è esubero sufficiente,
  - attiva il **boost** della zona (accensione clima/deumidificazione).
- Quando il surplus scende sotto ~100 W per un po’:
  - attenua il boost o lo spegne, rispettando un **tempo minimo di accensione/spegnimento** per evitare “attacca/stacca” continui.

### Controllo della percentuale di batteria

Il parametro **“Livello Minimo Batteria (%)”** ha due utilizzi principali, molto diversi a seconda del tipo di accumulo:

#### 1. Batterie “su rete AC” (es. Tesla Powerwall)

In questi sistemi (tipici Powerwall, o altre batterie AC‑coupled):

- la batteria è collegata sul lato **AC della casa**, non direttamente all’inverter fotovoltaico,
- la gestione della batteria è spesso indipendente rispetto a quella dell’inverter FV.

Qui il controllo di `min_battery_level` è **molto utile** perché:

- puoi decidere di **non usare l’esubero per il clima** sotto una certa carica, per:
  - riservare energia alla casa nelle ore serali/notturne,
  - proteggere la batteria da scariche troppo profonde,
  - evitare di “rubare” energia che il sistema vorrebbe mantenere per altri carichi.

In pratica:

- se `battery_level < min_battery_level`:
  - la zona non entra in boost, anche se c’è esubero,
  - l’integrazione lascia priorità alla ricarica della batteria / gestione standard dell’accumulo.

#### 2. Batterie gestite dall’inverter (lato DC)

In molti impianti residenziali, la batteria è integrata nell’inverter fotovoltaico e:

- l’inverter decide autonomamente come caricare/scaricare,
- i climatizzatori sono **solo carichi AC**.

In questo scenario il `min_battery_level` è utile anche come strumento di **sequenziamento**:

- puoi impostare **valori diversi** per ogni zona, ad esempio:
  - Zona 1 (Living): min batteria 70%
  - Zona 2 (Cameretta): min batteria 80%
  - Zona 3 (Padronale): min batteria 90%
- Risultato:
  - con batteria “bassa” parte solo la zona con soglia più bassa,
  - man mano che la batteria sale di percentuale, puoi far entrare in gioco altre zone,
  - di fatto ottieni un **ritardo di avvio tra le macchine** senza dover scrivere automazioni manuali.

Questa logica è molto utile quando:

- hai più split potenti,
- non vuoi che partano tutti insieme al primo picco di sole,
- preferisci una strategia “modulare” in base allo stato della batteria.

---

## Modalità clima: Estate, Inverno, Auto

L’integrazione usa il selettore `select.<zona>_mode` per capire come lavorare:

- **Summer (Cooling)**:
  - il clima lavora in raffrescamento,
  - `summer_temp` è la base del target,
  - se configurato, viene applicato un **offset adattivo** in base alla temperatura esterna.

- **Winter (Heating)**:
  - il clima lavora in riscaldamento,
  - `winter_temp` è la base,
  - se hai un **termostato di caldaia** collegato:
    - la temperatura del clima può essere impostata come:
      - `setpoint del termostato + boost_offset`
    - per lavorare in **sinergia**: il clima “aiuta” il riscaldamento tradizionale quando c’è esubero.

- **Auto**:
  - l’integrazione decide **Estate/Inverno** in base:
    - al mese,
    - e (se presente) alla temperatura esterna.

---

## Deumidificazione e isteresi

### Soglia di umidità interna

- La soglia `humidity_threshold` indica sopra quale umidità la zona può richiedere deumidificazione.
- L’integrazione applica una **isteresi di circa ±3%**:
  - se non sta deumidificando:
    - entra in deumidificazione solo se `umidità > soglia + 3%`,
  - se sta già deumidificando:
    - esce solo se `umidità < soglia – 3%`.

Questo evita continui ON/OFF quando l’umidità oscilla vicino alla soglia.

### Comportamento estivo vs invernale

- **Estate / raffrescamento**:
  - se possibile, usa la modalità **`dry`** del clima,
  - altrimenti utilizza `cool` con setpoint adeguato.

- **Inverno**:
  - la “deumidificazione” avviene in pratica come **riscaldamento**:
  - la zona rimane in `heat`,
  - la temperatura target viene aumentata (ad esempio +6 °C) per asciugare l’ambiente.
  - In questo modo tutte le unità restano coerenti lato riscaldamento.

---

## Deumidificazione condivisa (multi‑split)

Molti impianti multi‑split non gradiscono avere:

- una unità in **heat**,
- un’altra in **cool/dry** contemporaneamente.

Per questo esiste il flag:

- **“Deumidificazione condivisa tra le zone (estate)”**

### Come funziona

- Quando il flag è **attivo** e **una zona** entra in deumidificazione in contesto estivo:
  - quella zona imposta il proprio clima in `dry` (se supportato) o `cool`,
  - per ogni altra zona:
    - se l’automazione è attiva,
    - se ha un clima configurato,
    - imposta anche quell’unità in `dry` (se disponibile) o `cool`.
- Risultato:
  - tutte le unità collegate alla stessa macchina esterna lavorano **dalla stessa parte** (raffrescamento/deumidificazione),
  - si evitano combinazioni pericolose tipo due zone che chiedono riscaldamento e una solo deumidificazione in freddo.

### Quando è “obbligatoria” e quando no

- **Impianti multi‑split con unica macchina esterna**  
  In questo caso è fortemente **consigliato (di fatto obbligatorio)** tenere attiva la deumidificazione condivisa:
  - garantisce che tutte le unità interne lavorino in una modalità compatibile,
  - riduce il rischio di errori o protezioni della macchina esterna.

- **Impianti con macchine esterne separate (mono‑split indipendenti)**  
  Se ogni unità interna ha la propria macchina esterna dedicata:
  - puoi tranquillamente **disattivare** la deumidificazione condivisa,
  - ogni zona gestirà la deumidificazione in modo indipendente,
  - è utile se vuoi strategie diverse stanza per stanza.

Le card mostrano chiaramente quando il flag è attivo:

- card singola: scritta “Deumidificazione condivisa attiva” sotto l’header,
- card unificata: piccola dicitura “Deumidificazione condivisa” nella riga della zona.

---

## Automazione: Automatica / Disabilitata

Lo switch `..._auto_mode` controlla se la logica della zona è:

- **Automatica**:
  - l’integrazione:
    - legge surplus, batteria, umidità, stagione, ecc.,
    - decide se accendere/spegnere il clima,
    - gestisce deumidificazione e sincronizzazione condivisa (se attiva).

- **Disabilitata**:
  - l’integrazione **non invia più comandi** al clima / termostato della zona,
  - i sensori e le card continuano a mostrare valori e stati,
  - puoi controllare i climatizzatori manualmente con le normali card di Home Assistant.

Sulle card questo appare come:

- `Automatica` / `Disabilitata` nella riga di stato.

---

## Card Lovelace

### Card singola – `energy-smart-pv-card`

Mostra tutti i dettagli di una **singola zona**:

- Header:
  - nome zona,
  - stato (In Uso / Ricarica / In Attesa / Disabilitata),
  - etichetta `Automatica` / `Disabilitata` (click per attivare/disattivare),
  - efficienza “% Eco”.
- Riquadri dispositivi:
  - climatizzatore: stato, modalità, temperatura target / attuale, potenza (se presente), pillola `DEUM` quando in deumidificazione,
  - termostato: stato e temperature (se configurato).
- Footer:
  - sezione **Modalità** (Estate/Inverno/Auto),
  - **Umidità** con valore attuale e soglia, bottoni `-` / `+` per regolarla,
  - **Batteria minima** con valore e bottoni `-` / `+`,
  - **Soglia esubero W** con valore e bottoni `-` / `+`.

Tutti i `- / +` inviano servizi all’integrazione, che aggiorna le opzioni della zona e ricarica le impostazioni senza bisogno di entrare nelle impostazioni dell’integrazione.

### Card unificata – `energy-smart-pv-unified-card`

È pensata per avere una **vista riassuntiva di più zone**:

- Testata:
  - esubero globale,
  - % batteria media,
  - umidità media,
  - temperatura/umidità esterna,
  - contatore quante zone sono in boost.
- Per ogni zona:
  - header con:
    - nome zona,
    - stato,
    - `Automatica` / `Disabilitata`,
    - eventuale dicitura “Deumidificazione condivisa”.
  - mini‑card AC / Termostato / Modalità.
  - pulsante “tune” per aprire le impostazioni compatte:
    - soglia umidità,
    - batteria minima,
    - soglia W,
    - temperature estate/inverno,
    - offset adattivo,
    - boost offset,
    - spunta “Deumidificazione condivisa” per attivare/disattivare la modalità condivisa per quella zona.

Questa card è comoda per gestire rapidamente tre o più zone da un’unica vista.

---

## Suggerimenti d’uso per scenari tipici

### 1. Impianto con Powerwall / batteria AC‑coupled

- Imposta `min_battery_level` a un valore che protegga la tua autonomia serale (es. 40–60%).
- Permetti al clima di usare l’esubero **solo oltre quella soglia**.
- Se hai più zone:
  - puoi usare lo stesso valore per tutte,
  - oppure graduare leggermente le soglie per avere una priorità (es. Living a 50%, altre a 60–65%).

### 2. Impianto con batteria integrata nell’inverter (lato DC)

- Usa `min_battery_level` come **ritardo di avvio tra zone**:
  - Living a 70%,
  - Cameretta a 80%,
  - Padronale a 90%.
- In questo modo non partono tutti i climatizzatori insieme:
  - prima entra in gioco la zona “prioritaria”,
  - poi, con batteria più carica, si aggiungono le altre.

### 3. Impianto senza batteria

- Puoi lasciare `min_battery_level` al default (80%) oppure a 0:
  - se il sensore batteria non è configurato, viene ignorato,
  - l’attivazione si basa solo su esubero (`export_threshold`).

### 4. Multi‑split vs mono‑split e modalità condivisa

L’opzione **“Modalità condivisa tra le zone (multi‑split caldo/deumidificazione)”** si configura nelle opzioni della singola zona, subito sotto il **Boost Offset**. Serve a dire all’integrazione quali zone appartengono alla **stessa macchina esterna** (multi‑split) e vanno quindi tenute allineate sulla stessa modalità.

- **Multi‑split con unica unità esterna**:
  - attiva la modalità condivisa su **tutte le zone collegate a quella unità esterna** (es. Living + Padronale),
  - ogni zona continua a calcolare in modo indipendente se desidera **caldo** (HEAT) o **freddo/deumidificazione** (COOL/DRY),
  - quando almeno una zona è in boost, l’integrazione fa una **votazione di gruppo**:
    - se la maggioranza delle zone in boost chiede **caldo**, tutte le zone del gruppo vengono impostate in **HEAT**,
    - se la maggioranza chiede **freddo/deumidificazione**, tutte le zone del gruppo vengono impostate in **DRY** (se supportato) oppure **COOL**,
    - in caso di perfetta parità, viene privilegiato:
      - il **caldo** in inverno,
      - il **freddo/deumidificazione** in estate.
  - questo vale **sia in estate che in inverno**: non ci saranno mai, sullo stesso multi‑split, split in HEAT e altri in DRY/COOL contemporaneamente.

- **Mono‑split indipendenti (più macchine esterne separate)**:
  - lascia la modalità condivisa **non spuntata**,
  - ogni zona lavora in autonomia, senza partecipare alla votazione di gruppo,
  - puoi avere logiche diverse stanza per stanza, anche con modalità differenti (es. una in deumidificazione e un’altra in caldo).

---

## Note finali

- Il **termostato di caldaia non viene mai spento automaticamente** dall’integrazione: puoi gestirlo manualmente in ogni momento.
- L’automazione è sempre **disattivabile** a livello di singola zona tramite lo switch/etichetta `Automatica` / `Disabilitata`.
- Le logiche di isteresi e i tempi minimi di accensione/spegnimento riducono il rischio di cicli troppo rapidi che stressano le macchine.

L’obiettivo di Energy Smart PV Climate è farti usare al massimo esubero e accumulo, mantenendo allo stesso tempo comfort, sicurezza per la batteria e rispetto dei limiti degli impianti multi‑split.
