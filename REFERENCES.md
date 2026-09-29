# Dataset & references

## Dataset used in the talk

**XAI4HEAT SCADA Dataset 2024** — real-world SCADA data from a district
heating system at the Faculty of Mechanical Engineering, Niš, Serbia.
Five residential substations (L4, L8, L12, L17, L22), five heating seasons
(2019–2024). Includes supply/return temperatures (primary + secondary),
transmitted energy, delivered power, and outdoor temperature.

- Repository (Mendeley Data, CC BY 4.0):
  https://data.mendeley.com/datasets/2mwc6x6kwb/1
  DOI: 10.17632/2mwc6x6kwb.1
- GitHub mirror with raw CSVs (what `get_data.py` downloads):
  https://github.com/xai4heat/xai4heat
  Raw file used: `datasets/raw/TPS Lamela L4.csv`

### Cite the dataset

> Cvetković, S., Zdravković, M., Ignjatović, M. (2024).
> *XAI4HEAT SCADA Dataset 2024.* Mendeley Data, V1.
> https://doi.org/10.17632/2mwc6x6kwb.1

### Cite the companion data paper

> Cvetković, S., Zdravković, M., Ignjatović, M. (2025).
> *Exploring district heating systems: A SCADA dataset for enhanced
> explainability.* Data in Brief, 59, 111320.
> https://doi.org/10.1016/j.dib.2025.111320

Note: this is a peer-reviewed *Data in Brief* article, not an arXiv preprint.
If you specifically need an arXiv item on data-driven DH heat-load modelling,
the closest open preprint is the Tartu (Estonia) smart-heat-meter study:

> *Data-Driven Model for Heat Load Prediction in Buildings Connected to
> District Heating Networks.* arXiv:2309.11504.
> https://arxiv.org/abs/2309.11504

(That is a different dataset — 42 substations in Tartu, hourly — not the one
plotted in the talk. Listed only because you asked for an arXiv reference.)

## Raw data caveats (worth knowing before you quote it on stage)

The raw file is deliberately unprocessed. In substation L4 you will find:

- **Mixed sampling intervals.** Mostly hourly, with a 15-minute stretch and a
  genuine 3-minute stretch (early April 2024 — the window used in the
  real-time figure). The meter's logging resolution changed over time.
- **Cumulative energy counter** (`energy`, MWh) with ~350 negative steps
  (resets/glitches) and long flat runs when little heat is delivered.
- **Missing `power` values** (~10k NaNs across the file).
- **A multi-day gap** (~18 days) and many shorter gaps.
- **Sensor dropouts** — supply temperature occasionally reads 0 °C.

The figures show this as-is; nothing is smoothed or gap-filled. That mess is
the point of the two hook slides.

## Column reference (raw file)

| column      | meaning                                   |
|-------------|-------------------------------------------|
| datetime    | timestamp                                 |
| t_out       | outdoor temperature [°C]                  |
| t_ref       | reference/target temperature [°C]         |
| t1_supply   | primary supply temperature [°C]           |
| t1_return   | primary return temperature [°C]           |
| t2_supply   | secondary supply temperature [°C]         |
| t2_return   | secondary return temperature [°C]         |
| energy      | cumulative transmitted energy [MWh]       |
| power       | delivered heat power [kW]                 |
