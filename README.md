# WACCM6 Gravity-Wave Research Data

Processed data supporting a study of convective gravity-wave parameter sensitivity, equatorial stratospheric winds, and the Pacific Walker circulation in SC-WACCM6.

The CSV files contain results from five one-year simulations, the ERA5 Walker-index comparison (1991–2020), and nine exploratory five-day simulations. `plots_from_csv.py` generates figures from these CSVs. Full model output and the original analysis notebooks are not included.

## Plotting

```bash
pip install numpy pandas matplotlib
python plots_from_csv.py --annual-dir . --era5-dir . --five-day-dir . --out figures
```

## Repository contents
| File | Contents |
| --- | --- |
| `annual_diagnostics.csv` | Annual summary of GW tendency, equatorial wind, Walker index, precipitation, and trade-wind metrics for the five one-year cases; includes anomalies relative to control. |
| `monthly_diagnostics.csv` | Twelve monthly diagnostic records per annual case, including control-relative anomalies. |
| `annual_gw_lat_lev.csv` | Latitude–pressure structure of annual convective GW zonal-wind tendency. |
| `annual_u_lat_lev.csv` | Latitude–pressure structure of annual zonal wind. |
| `annual_equatorial_u_profile.csv` | Annual equatorial zonal-wind vertical profiles. |
| `annual_walker_lon_lev.csv` | Equatorial longitude–pressure circulation fields used to examine the Walker response. |
| `annual_precip_lat_lon.csv` | Annual precipitation fields and anomalies over the plotted domain. |
| `annual_u850_lat_lon.csv` | Annual 850-hPa zonal-wind fields and anomalies over the plotted domain. |
| `era5_annual_walker.csv` | Annual ERA5 Walker-index components and values for 1991–2020 (30 records). |
| `era5_monsthly_walker.csv` | Monthly ERA5 Walker-index components and values for 1991–2020 (360 records); filename retains its spelling as uploaded. |
| `five_day_daily_diagnostics.csv` | Daily diagnostics for the nine matched exploratory configurations. |
| `five_day_anomalies.csv` | Daily five-day diagnostics and anomalies relative to the matching control. |
| `five_day_signed_gw_interactions.csv` | Four combined-parameter signed GW tendency interactions and approximate multiplicative-scaling comparisons. |
| `plots_from_csv.py` | Standalone Python script for recreating diagnostic plots from the CSVs. |
| `LICENSE` | Repository license. |

## Definitions and units

- **GW tendency:** `BUTGWSPEC`, the parameterized convective GW *zonal-wind tendency*, reported in `m s^-1 day^-1`. It is not itself a momentum flux. `gw_rms_m_s_day` describes the magnitude of the diagnosed tendency; `gw_signed_m_s_day` preserves its sign.
- **Equatorial stratospheric wind:** `u30_m_s`, zonal wind near nominal 30 hPa, reported in `m s^-1`.
- **Walker index:** the difference between eastern and western equatorial-Pacific pressure vertical velocity at approximately 500 hPa:

  `Walker = mean(OMEGA_500, east) - mean(OMEGA_500, west)`

  The western region is **5°S–5°N, 120°–160°E**, and the eastern region is **5°S–5°N, 240°–280°E**. Values are in `hPa day^-1`. Under the pressure-velocity convention, negative `OMEGA` indicates ascent and positive `OMEGA` indicates descent. This is a **regional vertical-motion contrast**, not a direct measurement of the entire Walker mass circulation.
- **Precipitation:** model total precipitation is calculated as `PRECC + PRECL` where `PRECT` is not stored separately; reported in `mm day^-1`.
- **850-hPa winds:** `u850_trade_m_s`, zonal wind in `m s^-1`. Positive anomalies indicate an eastward shift relative to control.
- **Anomalies:** columns prefixed `delta_`, or named `delta_vs_ctrl`, mean **experiment minus the matching control**. Coordinates in the gridded CSVs are given by `lat`, `lon` (degrees east), and `lev` (nominal pressure, hPa), as applicable.
- **Annual aggregation:** the model's monthly means are combined using model-month durations. The 1991–2020 ERA5 annual values were formed from monthly data with calendar-month-duration weighting.

## Citation and archiving
ERA5 monthly pressure-level data: https://doi.org/10.24381/cds.6860a573

Cite a versioned repository release or archive DOI when available if reusing this data or script.

The repository includes an MIT `LICENSE` file. Any distinct license for the numerical datasets should be explicitly documented in the archival release metadata.
