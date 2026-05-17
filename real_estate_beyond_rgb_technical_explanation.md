# Real Estate Beyond RGB — Technical Explanation

## 1. Σκοπός του project

Το project **Real Estate Beyond RGB** είναι ένα decision-support tool για αξιολόγηση αγροτικών εκτάσεων με χρήση υπερφασματικών δορυφορικών δεδομένων EnMap.

Ο βασικός στόχος είναι:

> Για κάθε διαθέσιμη έκταση γης και κάθε πιθανή καλλιέργεια/επενδυτικό σενάριο, να υπολογιστεί ένας δείκτης καταλληλότητας ώστε ο επενδυτής να μπορεί να συγκρίνει επιλογές.

Η βασική ροή είναι:

```text
Land plots
+ Crop assumptions
+ EnMap hyperspectral data
+ Investor risk profile
= Ranked crop/plot recommendations
```

---

## 2. Τι έχουμε υλοποιήσει μέχρι τώρα

Μέχρι στιγμής έχουμε φτιάξει τα εξής layers:

```text
data layer
↓
EnMap loading layer
↓
spectral analysis layer
↓
scoring layer
↓
recommendation layer
```

Τρέχουσα δομή:

```text
makeathon-2026-MOTION-i-sense/
│
├── data/
│   ├── plots.json
│   ├── crop_knowledge_base.json
│   └── enmap/
│       ├── arkadia_20241024_mosaic/
│       ├── magnisia_20241024_mosaic/
│       ├── arkadia2_20240531_mosaic/
│       └── Veroia-Veroia_20250821_mosaic/
│
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── enmap_loader.py
│   ├── spectral_indices.py
│   ├── scoring.py
│   └── recommendation.py
│
├── test_load_plots.py
├── test_load_crops.py
├── test_read_enmap.py
├── test_spectral_indices.py
├── test_scoring.py
└── test_recommendation.py
```

---

## 3. Τι κάνει κάθε βασικό αρχείο

### `data/plots.json`

Περιέχει τα 4 land plots.

Κάθε plot έχει:

```text
plot_id
name
latitude
longitude
area_m2
assumed_price_eur
enmap_folder
```

Το `enmap_folder` συνδέει το plot με τον αντίστοιχο φάκελο EnMap.

---

### `data/crop_knowledge_base.json`

Περιέχει τις καλλιέργειες ή επενδυτικές επιλογές.

Για κάθε crop/scenario κρατάμε στοιχεία όπως:

```text
suitable_ph_min
suitable_ph_max
water_need_level
water_risk_sensitivity
expected_revenue_eur_per_ha_per_year
expected_opex_eur_per_ha_per_year
initial_capex_eur_per_ha
regulatory_risk_score
market_risk_score
climate_risk_score
capex_risk_score
notes
```

Αυτό το αρχείο είναι η βάση πάνω στην οποία συγκρίνουμε κάθε καλλιέργεια με κάθε έκταση.

---

### `src/config.py`

Το `config.py` κρατάει τα βασικά paths του project.

Παράδειγμα:

```python
PLOTS_FILE = DATA_DIR / "plots.json"
CROP_KNOWLEDGE_BASE_FILE = DATA_DIR / "crop_knowledge_base.json"
ENMAP_DIR = DATA_DIR / "enmap"
```

Με απλά λόγια:

> Το `config.py` λέει στον κώδικα πού βρίσκονται τα δεδομένα.

---

### `src/data_loader.py`

Το `data_loader.py` διαβάζει τα JSON αρχεία.

Περιέχει functions όπως:

```python
load_plots()
load_crop_knowledge_base()
```

Με απλά λόγια:

> Το `data_loader.py` μετατρέπει τα JSON αρχεία σε Python data που μπορεί να χρησιμοποιήσει ο κώδικας.

---

### `src/enmap_loader.py`

Το `enmap_loader.py` συνδέει κάθε plot με τα αντίστοιχα EnMap αρχεία.

Για κάθε plot βρίσκει:

```text
SPECTRAL_IMAGE.TIF
METADATA.XML
```

Η βασική function είναι:

```python
read_spectral_image_info(plot)
```

Αυτή ελέγχει ότι η Python μπορεί να ανοίξει το δορυφορικό αρχείο και επιστρέφει:

```text
number of bands
image width
image height
CRS
bounds
NoData value
```

---

## 4. Τι είναι τα EnMap δεδομένα

Τα EnMap δεδομένα είναι hyperspectral satellite imagery.

Μια απλή RGB εικόνα έχει 3 κανάλια:

```text
Red
Green
Blue
```

Η EnMap εικόνα έχει πολλά περισσότερα κανάλια, στο δικό μας αρχείο 224 spectral bands.

Κάθε band αντιστοιχεί σε διαφορετικό μήκος κύματος.

Αυτό είναι σημαντικό γιατί διαφορετικά υλικά και καταστάσεις του εδάφους αντανακλούν διαφορετικά το φως.

Παράδειγμα:

```text
Red band      → χρήσιμο για NDVI
NIR band      → χρήσιμο για vegetation health
SWIR bands    → χρήσιμα για moisture, minerals, soil surface proxies
```

---

## 5. Τι είναι το `SPECTRAL_IMAGE.TIF`

Το `SPECTRAL_IMAGE.TIF` είναι το αρχείο με τις πραγματικές τιμές των pixels.

Δεν είναι απλή φωτογραφία. Είναι ένας πολυδιάστατος raster πίνακας.

Για κάθε pixel υπάρχει τιμή σε κάθε spectral band.

Παράδειγμα:

```text
Pixel (row 5, col 10):
Band 1   = value
Band 2   = value
...
Band 224 = value
```

Από αυτές τις τιμές υπολογίζουμε spectral indices.

---

## 6. Τι είναι το `METADATA.XML`

Το `METADATA.XML` είναι η ταυτότητα/περιγραφή της εικόνας.

Περιέχει πληροφορίες όπως:

```text
processing level
ημερομηνία λήψης
pixel size
αριθμό VNIR και SWIR bands
μήκος κύματος κάθε band
gain και offset κάθε band
quality information
```

Το πιο χρήσιμο κομμάτι για εμάς είναι το `bandCharacterisation`.

Εκεί βρίσκουμε για κάθε band το κεντρικό μήκος κύματος.

Έτσι ο κώδικας δεν χρειάζεται να ξέρει εκ των προτέρων ποιο band είναι το Red ή το NIR. Το βρίσκει αυτόματα από το XML.

---

## 7. Τι είναι τα quality files

Τα αρχεία τύπου:

```text
QL_QUALITY_CLOUD.TIF
QL_QUALITY_CLOUDSHADOW.TIF
QL_QUALITY_HAZE.TIF
QL_PIXELMASK.TIF
```

είναι βοηθητικά quality layers.

Μας λένε αν κάποια pixels έχουν προβλήματα όπως:

```text
clouds
cloud shadows
haze
snow
invalid pixels
```

Στο σημερινό MVP δεν τα χρησιμοποιούμε ακόμα ενεργά στο scoring. Μπορούν όμως να προστεθούν αργότερα για masking, ώστε να αγνοούμε προβληματικά pixels.

---

## 8. `src/spectral_indices.py`

Αυτό είναι ένα από τα σημαντικότερα αρχεία.

Εκεί υπολογίζουμε τους δορυφορικούς δείκτες.

Η βασική function είναι:

```python
compute_spectral_indices_for_plot(plot)
```

Αυτή κάνει:

```text
1. Βρίσκει τα EnMap paths για το plot.
2. Διαβάζει το METADATA.XML.
3. Βρίσκει τα bands κοντά σε Red, Green, Blue, NIR, SWIR1, SWIR2.
4. Διαβάζει αυτά τα bands από το SPECTRAL_IMAGE.TIF.
5. Υπολογίζει NDVI, NDMI, brightness, redness proxy, SWIR ratio proxy.
6. Υπολογίζει ένα rule-based pH proxy.
```

---

## 9. Τι είναι NDVI

Ο NDVI σημαίνει:

```text
Normalized Difference Vegetation Index
```

Υπολογίζεται ως:

```text
NDVI = (NIR - Red) / (NIR + Red)
```

Όπου:

```text
NIR = Near Infrared reflectance
Red = Red reflectance
```

Ο NDVI είναι δείκτης βλάστησης.

Χοντρικά:

```text
NDVI κοντά στο 0     → γυμνό έδαφος ή πολύ λίγη βλάστηση
NDVI 0.2–0.4         → αραιή/μέτρια βλάστηση
NDVI 0.4–0.7         → καλή βλάστηση
NDVI > 0.7           → πολύ πυκνή/υγιής βλάστηση
```

Στο project μας ο NDVI χρησιμοποιείται ως proxy για:

```text
vegetation health
general productivity
land surface condition
```

Δεν σημαίνει απευθείας ότι μια καλλιέργεια θα έχει κέρδος. Είναι όμως χρήσιμη ένδειξη για την κατάσταση της γης.

---

## 10. Τι είναι NDMI

Ο NDMI σημαίνει:

```text
Normalized Difference Moisture Index
```

Υπολογίζεται ως:

```text
NDMI = (NIR - SWIR1) / (NIR + SWIR1)
```

Ο NDMI χρησιμοποιείται ως proxy για υγρασία/ξηρασία.

Χοντρικά:

```text
υψηλότερος NDMI → περισσότερη υγρασία / λιγότερο water stress
χαμηλότερος NDMI → ξηρότερη κατάσταση / πιθανό water stress
```

Στο project μας ο NDMI χρησιμοποιείται για να εκτιμήσουμε αν μια περιοχή είναι πιο κατάλληλη για καλλιέργειες με υψηλές ή χαμηλές ανάγκες σε νερό.

---

## 11. Τι είναι Brightness Proxy

Το brightness proxy είναι απλός δείκτης φωτεινότητας της επιφάνειας.

Υπολογίζεται περίπου ως μέσος όρος από visible bands:

```text
Brightness = mean(Red, Green, Blue)
```

Χρησιμοποιείται ως proxy για:

```text
bare soil
dry surface
bright/calcareous soil tendency
```

Υψηλό brightness μπορεί να δείχνει πιο γυμνή, ξηρή ή φωτεινή επιφάνεια. Δεν είναι από μόνο του πλήρης εδαφολογική ανάλυση.

---

## 12. Τι είναι Redness Proxy

Το redness proxy συγκρίνει το red reflectance με το green/blue.

Στο project το υπολογίζουμε ως:

```text
Redness proxy = Red / average(Green, Blue)
```

Χρησιμοποιείται ως χοντρική ένδειξη για:

```text
iron oxides
soil mineral surface effects
reddish bare soil tendency
```

Δεν είναι εργαστηριακή μέτρηση. Είναι μόνο proxy.

---

## 13. Τι είναι SWIR Ratio Proxy

Το SWIR ratio proxy χρησιμοποιεί τα SWIR bands.

Στο project το υπολογίζουμε περίπου ως:

```text
SWIR ratio = SWIR1 / SWIR2
```

Τα SWIR bands είναι χρήσιμα γιατί σχετίζονται με:

```text
moisture
clay/mineral properties
soil surface condition
carbonates or dry mineral signatures
```

Στο MVP το χρησιμοποιούμε ως γενικό mineral/soil surface proxy.

---

## 14. Πώς εκτιμούμε pH

Το pH δεν μετριέται άμεσα από το EnMap.

Στο project όμως θέλουμε functionality, οπότε κάνουμε ένα **educated pH assumption**.

Το ονομάζουμε:

```text
pH proxy
```

και όχι laboratory pH.

Η λογική είναι:

```text
NDVI
+ NDMI
+ brightness
+ redness
+ SWIR ratio
= rough pH tendency
```

Η αρχική βάση είναι ένα neutral-to-slightly alkaline Mediterranean assumption, περίπου:

```text
pH ≈ 7.2
```

Μετά ο κώδικας το προσαρμόζει:

```text
υψηλότερο brightness → πιθανή τάση προς πιο alkaline
χαμηλότερο NDMI → πιθανή ξηρότερη/calcareous επιφάνεια
redness/SWIR proxies → πιθανή mineral influence
πολύ υψηλό NDVI → μεγαλύτερη αβεβαιότητα για γυμνό soil signal
```

Το output είναι:

```text
estimated_ph
ph_class
ph_confidence
ph_method
```

Παράδειγμα:

```json
{
  "estimated_ph": 7.6,
  "ph_class": "slightly_alkaline",
  "ph_confidence": "low_to_medium",
  "ph_method": "rule_based_hyperspectral_proxy_not_lab_measurement"
}
```

Στην παρουσίαση πρέπει να ξεκαθαριστεί:

> Το pH proxy δεν αντικαθιστά εργαστηριακή εδαφολογική ανάλυση. Χρησιμοποιείται μόνο για preliminary screening και functionality στο MVP.

---

## 15. Γιατί χρησιμοποιούμε μέσο όρο

Για κάθε plot, το EnMap crop είναι μικρή εικόνα πολλών pixels.

Ο κώδικας υπολογίζει τον δείκτη σε κάθε pixel και μετά βγάζει:

```text
mean
min
max
```

Παράδειγμα:

```text
NDVI mean
NDVI min
NDVI max
```

Ο μέσος όρος χρησιμοποιείται ως συνοπτική τιμή για όλη την έκταση.

Αργότερα μπορούμε να προσθέσουμε spatial variability, δηλαδή να δούμε αν η έκταση έχει εσωτερικές διαφοροποιήσεις.

---

## 16. `src/scoring.py`

Το `scoring.py` μετατρέπει τους δείκτες σε scores.

Τα scores είναι αριθμοί από:

```text
0 έως 1
```

Όπου:

```text
0 = κακό / ακατάλληλο
1 = πολύ καλό / κατάλληλο
```

Η βασική function είναι:

```python
calculate_crop_plot_suitability(plot_indices, crop, investor_risk_level)
```

Αυτή συνδυάζει:

```text
pH suitability
water suitability
vegetation suitability
risk fit
```

και βγάζει:

```text
overall_suitability_score
```

---

## 17. pH Score

Το pH score συγκρίνει:

```text
estimated pH του plot
```

με:

```text
ιδανικό pH range του crop
```

Αν το pH είναι μέσα στο range:

```text
ph_score = 1.0
```

Αν είναι εκτός range, πέφτει ανάλογα με την απόσταση.

---

## 18. Water Score

Το water score βασίζεται στο NDMI και στο πόσο ευαίσθητο είναι το crop στην έλλειψη νερού.

Από το crop JSON έχουμε:

```text
water_risk_sensitivity
```

Παράδειγμα:

```text
Avocado: high water sensitivity
Saffron: low water sensitivity
```

Αν το NDMI είναι χαμηλό:

```text
το avocado τιμωρείται περισσότερο
το saffron λιγότερο
```

Άρα το ίδιο plot μπορεί να είναι κακό για avocado αλλά αποδεκτό για saffron.

---

## 19. Vegetation Score

Το vegetation score βασίζεται στον NDVI.

Υψηλότερος NDVI δίνει υψηλότερο score.

Χρησιμοποιείται ως γενικός δείκτης για:

```text
current vegetation condition
land productivity proxy
surface vitality
```

---

## 20. Risk Score

Το risk score συγκρίνει το crop risk με το risk tolerance του επενδυτή.

Το crop έχει risk inputs:

```text
regulatory_risk_score
market_risk_score
climate_risk_score
capex_risk_score
```

Αν ο επενδυτής είναι low risk:

```text
high-risk crops πέφτουν πολύ
```

Αν είναι high risk:

```text
high-risk/high-upside crops γίνονται πιο αποδεκτά
```

Άρα το ίδιο crop μπορεί να έχει διαφορετική κατάταξη ανάλογα με το risk profile.

---

## 21. Overall Suitability Score

Το συνολικό score είναι weighted average:

```text
overall =
0.25 * pH score
+ 0.30 * water score
+ 0.25 * vegetation score
+ 0.20 * risk score
```

Τα βάρη είναι MVP assumptions.

Ερμηνεία:

```text
water score έχει ελαφρώς μεγαλύτερο βάρος
pH και vegetation είναι επίσης σημαντικά
risk fit επηρεάζει το αποτέλεσμα αλλά δεν κυριαρχεί
```

Αυτά τα βάρη μπορούν να γίνουν adjustable στο UI.

---

## 22. `src/recommendation.py`

Το `recommendation.py` δημιουργεί τον τελικό ranked πίνακα.

Η βασική function είναι:

```python
build_recommendation_table(plots, crops, investor_risk_level)
```

Αυτή κάνει:

```text
Για κάθε plot:
    υπολόγισε EnMap indices

    Για κάθε crop:
        υπολόγισε suitability scores
        φτιάξε ένα row με όλα τα αποτελέσματα

Ταξινόμησε όλα τα rows από το μεγαλύτερο overall score στο μικρότερο.
```

Αν έχουμε:

```text
4 plots
6 crops
```

τότε έχουμε:

```text
4 × 6 = 24 combinations
```

Ο πίνακας ταξινομείται και παίρνει rank.

---

## 23. Τι σημαίνει το τελικό ranking

Το ranking δεν λέει:

```text
αυτό είναι σίγουρα το πιο κερδοφόρο crop
```

Λέει:

```text
με βάση τα διαθέσιμα EnMap proxies, crop assumptions και risk profile,
αυτός ο συνδυασμός φαίνεται πιο κατάλληλος.
```

Άρα είναι preliminary decision-support ranking.

Τα οικονομικά στοιχεία θα προστεθούν αργότερα για να δούμε expected revenue, CAPEX, OPEX, ROI και payback.

---

## 24. Τι δεν κάνει ακόμα το project

Το project μέχρι τώρα δεν κάνει ακόμα:

```text
πλήρες οικονομικό μοντέλο
year-by-year cashflow
CAPEX/OPEX ROI calculation
Streamlit UI
automatic allocation optimization
quality mask filtering
laboratory-grade soil analysis
```

Αυτά είναι τα επόμενα βήματα.

---

## 25. Πώς θα ενσωματωθούν τα οικονομικά

Το οικονομικό μοντέλο θα μπει μετά το suitability scoring.

Η ιδέα είναι:

```text
suitability factor
+ crop revenue assumptions
+ crop cost assumptions
+ yield ramp-up
= expected cashflow
```

Για κάθε crop θα έχουμε:

```text
expected full revenue per hectare
expected OPEX per hectare
initial CAPEX per hectare
yield ramp-up curve
years to maturity
```

Έτσι θα υπολογίζουμε:

```text
annual revenue
annual expenses
net yearly cashflow
cumulative cashflow
payback year
ROI
```

---

## 26. Πώς θα εμφανιστεί στο UI

Το UI θα γίνει αργότερα σε Streamlit.

Ο χρήστης θα μπορεί:

```text
1. Να επιλέξει ένα από τα 4 plots.
2. Να δει λίστα καλλιεργειών.
3. Να πατήσει κάθε crop και να δει:
   - suitability score
   - estimated pH
   - NDVI/NDMI indicators
   - risk level
   - expected revenue/economics όταν προστεθούν
4. Να φιλτράρει με:
   - available capital
   - risk tolerance
```

---

## 27. Πώς εξηγείται απλά σε μη τεχνικό κοινό

Μια απλή περιγραφή για παρουσίαση:

> Αντί να βλέπουμε τη γη μόνο σαν κανονική εικόνα RGB, χρησιμοποιούμε υπερφασματικά δεδομένα EnMap. Αυτά καταγράφουν πληροφορία σε πολλά μήκη κύματος, πέρα από αυτό που βλέπει το ανθρώπινο μάτι. Από αυτά υπολογίζουμε δείκτες όπως NDVI για τη βλάστηση, NDMI για την υγρασία και άλλα soil surface proxies. Μετά συγκρίνουμε αυτούς τους δείκτες με τις ανάγκες κάθε καλλιέργειας και με το risk profile του επενδυτή. Έτσι δημιουργούμε ένα ranked recommendation table για το ποια καλλιέργεια ταιριάζει καλύτερα σε κάθε έκταση.

---

## 28. Περιορισμοί και σωστή διατύπωση

Στην παρουσίαση είναι σημαντικό να αναφερθεί:

```text
1. Τα EnMap indices είναι proxies, όχι εργαστηριακές μετρήσεις.
2. Το pH είναι educated assumption και όχι measured pH.
3. Τα crop assumptions πρέπει να βελτιωθούν με γεωπονικά και οικονομικά sources.
4. Τα οικονομικά θα είναι scenario-based, όχι εγγυημένη απόδοση.
5. Το tool είναι για preliminary screening και όχι για τελική επενδυτική απόφαση χωρίς field validation.
```

Αυτό κάνει το project πιο αξιόπιστο.

---

## 29. Τρέχον τεχνικό αποτέλεσμα

Μέχρι τώρα έχουμε λειτουργικό pipeline:

```text
JSON plots
↓
JSON crop assumptions
↓
EnMap TIF + XML loading
↓
NDVI / NDMI / brightness / pH proxy
↓
crop-plot suitability scoring
↓
ranked recommendations
```

Αυτό είναι ο πυρήνας του decision engine.

---

## 30. Επόμενα βήματα

Τα βασικά επόμενα βήματα είναι:

```text
1. Προσθήκη economics module.
2. Προσθήκη year-by-year crop cashflow.
3. Προσθήκη capital filter.
4. Προσθήκη risk filter στο UI.
5. Δημιουργία Streamlit interface.
6. Προαιρετικά: portfolio/allocation mode.
7. Προαιρετικά: quality mask filtering.
```

---

# Summary

Το project έχει ήδη περάσει από απλό data loading σε πραγματική αξιοποίηση υπερφασματικών δεδομένων.

Η βασική αξία είναι ότι μετατρέπει δορυφορικά spectral data σε πρακτικά investment-support metrics.

Με απλά λόγια:

```text
Δεν κοιτάμε μόνο πού είναι η γη.
Κοιτάμε πώς φαίνεται φασματικά η γη.
Μετατρέπουμε αυτό σε scores.
Και μετά συνδέουμε τα scores με crop suitability και investment risk.
```
