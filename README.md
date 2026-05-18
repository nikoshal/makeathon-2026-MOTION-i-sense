# Minotauros Agricultural Intelligence

**Team Motion — Makeathon 2026**

Minotauros Agricultural Intelligence is a web app for agricultural land-investment decision support.

The app compares different land plots and crop investment options using:

* EnMap hyperspectral satellite imagery
* crop suitability scoring
* financial modelling
* NPV / IRR / payback calculations
* an AI chatbot assistant called **Minotauro**

The project was developed for the challenge:

> \*\*Real Estate Beyond RGB\*\*

\---

## Project idea

Traditional land investment decisions usually rely on visible inspection, location, price, and basic market assumptions.

This project goes beyond RGB imagery by using hyperspectral satellite data to extract land-related indicators that are not directly visible to the human eye.

The goal is to help an investor answer:

> Which land plot and crop combination appears most attractive, and why?

\---

## Main features

The app allows the user to:

* select one of four land plots
* compare crop investment options
* view ranked recommendations
* inspect crop suitability scores
* see EnMap-derived indicators
* review financial metrics
* inspect year-by-year cashflows
* ask the Minotauro AI assistant questions about the results

\---

## Crops and plots

The current version compares four crop / investment options:

* Olives
* Pistachio
* Kiwis
* Medicinal cannabis

The app evaluates four land plots in Greece:

* Arkadia
* Magnisia
* Arkadia 2
* Veroia

Each plot is linked to local EnMap hyperspectral data.

\---

## Methodology

The app follows this pipeline:

```text
Land plots
↓
EnMap hyperspectral data
↓
Spectral indicators
↓
Crop suitability scoring
↓
Yield adjustment
↓
Financial model
↓
Ranked recommendation
```

\---

## EnMap indicators

The app reads EnMap `SPECTRAL\_IMAGE.TIF` and `METADATA.XML` files.

It calculates several indicators:

|Indicator|Meaning|
|-|-|
|NDVI|Vegetation health proxy|
|NDMI|Moisture / water stress proxy|
|Brightness proxy|Soil surface / dryness tendency|
|Redness proxy|Rough mineral / iron oxide tendency|
|SWIR ratio proxy|Soil / mineral / moisture-related proxy|
|pH proxy|Rule-based educated assumption, not a lab measurement|

Important note:

The pH value is not a laboratory measurement. It is a preliminary rule-based proxy derived from hyperspectral indicators and should be validated with soil sampling before real investment decisions.

\---

## Suitability scoring

For every plot and crop, the app calculates:

* pH score
* water score
* vegetation score
* risk fit score
* overall suitability score

The suitability score does not directly change profit.

Instead, it adjusts expected production/yield.

```text
suitability score
→ yield factor
→ adjusted production
→ adjusted revenue
→ cashflow / NPV / IRR / payback
```

This is more realistic because land suitability affects production volume first, while profit is a downstream result.

\---

## Financial model

For each crop, the app loads financial CSV files from:

```text
data/financial\_data/<crop\_name>/
```

Each crop folder contains:

```text
crop\_economics\_inputs.csv
yield\_ramp\_up.csv
price\_scenarios.csv
cost\_breakdown.csv
```

The model calculates:

* yearly production
* yearly revenue
* yearly OPEX
* yearly cashflow
* cumulative cashflow
* NPV
* IRR
* payback year

The model currently uses before-tax financial analysis.

VAT is not treated as income tax.

\---

## AI assistant

The app includes an AI chatbot assistant called **Minotauro**.

It is designed to help non-technical users understand:

* what each indicator means
* why a crop is recommended
* what NPV, IRR and payback mean
* how EnMap suitability affects production
* the limitations of the model

If Gemini API is enabled, the assistant can answer questions using the current app context.

\---

## Installation

Clone the repository:

```bash
git clone https://github.com/nikoshal/makeathon-2026-MOTION-i-sense.git
cd makeathon-2026-MOTION-i-sense
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

\---

## Environment variables

If using the Gemini chatbot, create a `.env` file.

Example `.env`:

```env
GEMINI\_API\_KEY=your\_api\_key\_here
```

Do not commit `.env` or API keys to GitHub.

Use `.env.example` as a template.

\---

## Run the app

Run:

```bash
python app.py
```

Then open:

```text
http://localhost:8501
```

\---

## Project structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── assets/
│   └── logo / branding assets
├── data/
│   ├── plots.json
│   ├── crop\_knowledge\_base.json
│   ├── enmap/
│   └── financial\_data/
├── src/
│   ├── config.py
│   ├── data\_loader.py
│   ├── enmap\_loader.py
│   ├── spectral\_indices.py
│   ├── scoring.py
│   ├── recommendation.py
│   ├── financial\_loader.py
│   ├── economics.py
│   └── investment\_analysis.py
└── test\_\*.py
```

\---

## Useful test commands

Run individual checks:

```bash
python test\_load\_plots.py
python test\_load\_crops.py
python test\_read\_enmap.py
python test\_spectral\_indices.py
python test\_scoring.py
python test\_financial\_loader.py
python test\_economics.py
python test\_investment\_analysis.py
```

\---

## Limitations

This tool is a preliminary decision-support prototype.

It does not replace:

* professional agronomic evaluation
* laboratory soil testing
* legal/regulatory review
* detailed investment due diligence

Main limitations:

* pH is estimated through a rule-based proxy
* satellite indicators are proxies, not direct measurements
* financial outputs are scenario-based
* final investment decisions require field validation

\---

## Future improvements

Possible next steps:

* calibrated pH model using soil samples
* better cloud / quality masking
* more crop scenarios
* portfolio allocation mode
* automatic PDF report export
* improved Gemini chatbot integration
* financing / loan module
* after-tax financial model

\---

## Final message

Minotauros turns invisible land signals into understandable investment decisions.

It combines satellite intelligence, crop suitability, and financial modelling to support smarter agricultural land investment.

