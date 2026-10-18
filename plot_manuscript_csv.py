#!/usr/bin/env python3
"""Reproduce manuscript diagnostic visualizations from exported CSVs.

Usage:
  python plot_manuscript_csv.py --annual-dir agu_data/annual \
      --era5-dir agu_data/era5 --five-day-dir agu_data/five_day \
      --out plots
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CASES = ("EFF_LOW", "EFF_HIGH", "DEPTH_LOW", "DEPTH_HIGH")
CASE_NAMES = {"CTRL": "Control", "EFF_LOW": "Efficiency LOW",
              "EFF_HIGH": "Efficiency HIGH", "DEPTH_LOW": "Heating depth LOW",
              "DEPTH_HIGH": "Heating depth HIGH"}
METRICS = (
    ("delta_gw_rms_m_s_day", "GW tendency RMS anomaly", "m s$^{-1}$ day$^{-1}$"),
    ("delta_u30_m_s", "Equatorial U near 30 hPa anomaly", "m s$^{-1}$"),
    ("delta_walker_hpa_day", "Walker index anomaly", "hPa day$^{-1}$"),
    ("delta_u850_trade_m_s", "Pacific 850-hPa trade-wind anomaly", "m s$^{-1}$"),
)


def read_csv(folder: Path | None, filename: str) -> pd.DataFrame | None:
    if folder is None:
        return None
    path = folder / filename
    if not path.exists():
        warnings.warn(f"Skipping absent file: {path}")
        return None
    return pd.read_csv(path)


def check_fields(df: pd.DataFrame, fields: tuple[str, ...] | list[str], name: str):
    missing = set(fields) - set(df.columns)
    if missing:
        raise ValueError(f"{name}: missing columns {sorted(missing)}")


def save(fig, out: Path, name: str):
    fig.savefig(out / (name + '.png'), dpi=175, bbox_inches='tight')
    fig.savefig(out / (name + '.pdf'), bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {name}.png and .pdf")


def four_panels(df: pd.DataFrame, out: Path, name: str, x: str, y: str,
                title: str, cbar: str, x_label: str, y_label: str,
                pressure_x: bool = False, pressure_y: bool = False,
                outlines: bool = False):
    check_fields(df, ('case', x, y, 'delta_vs_ctrl'), name)
    subset = df[df['case'].isin(CASES)]
    if subset.empty:
        raise ValueError(f"{name}: no sensitivity cases found")
    zlim = float(np.nanmax(np.abs(subset['delta_vs_ctrl'].to_numpy(dtype=float))))
    zlim = zlim if np.isfinite(zlim) and zlim > 0 else 1.0
    fig, axs = plt.subplots(2, 2, figsize=(11.3, 7.5), layout='constrained',
                            sharex=True, sharey=True)
    last = None
    for ax, case in zip(axs.flat, CASES):
        part = subset[subset['case'] == case]
        if part.empty:
            ax.text(.5, .5, 'Case unavailable', transform=ax.transAxes,
                    ha='center', va='center')
            continue
        grid = part.pivot_table(index=y, columns=x, values='delta_vs_ctrl', aggfunc='mean')
        grid = grid.sort_index().sort_index(axis=1)
        xx = grid.columns.to_numpy(dtype=float)
        yy = grid.index.to_numpy(dtype=float)
        XX, YY = np.meshgrid(xx, yy)
        Z = grid.to_numpy(dtype=float)
        if len(xx) >= 2 and len(yy) >= 2:
            last = ax.pcolormesh(XX, YY, Z, shading='auto', cmap='RdBu_r',
                                 vmin=-zlim, vmax=zlim)
        else:
            last = ax.scatter(XX.flatten(), YY.flatten(), c=Z.flatten(),
                              cmap='RdBu_r', vmin=-zlim, vmax=zlim)
        ax.set_title(CASE_NAMES[case] + ' − CTRL')
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if pressure_x:
            ax.set_xscale('log')
            ax.invert_xaxis() 
        if pressure_y:
            ax.set_yscale('log')
            ax.invert_yaxis()  
    if last is not None:
        fig.colorbar(last, ax=axs, shrink=.80, label=cbar)
    fig.suptitle(title, size=12)
    save(fig, out, name)


def plot_monthly(df: pd.DataFrame, out: Path):
    check_fields(df, ('case', 'sample') + tuple(m[0] for m in METRICS), 'monthly_diagnostics.csv')
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.0), layout='constrained', sharex=True)
    for ax, (key, label, unit) in zip(axes.flat, METRICS):
        for case in CASES:
            d = df.loc[df.case == case].sort_values('sample')
            if not d.empty:
                ax.plot(d['sample'].to_numpy(), d[key].to_numpy(), marker='o',
                        markersize=3, label=CASE_NAMES[case])
        ax.axhline(0, lw=.8, color='0.4')
        ax.set_title(label)
        ax.set_ylabel(unit)
        ax.set_xlabel('Model month')
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside lower center', ncol=4)
    fig.suptitle('Monthly sensitivity experiments: anomaly relative to control')
    save(fig, out, 'fig06_monthly_diagnostic_anomalies')


def plot_annual(d: Path, out: Path):
    specs = (
        ('annual_gw_lat_lev.csv', 'fig01_gw_tendency_lat_pressure', 'lev', 'lat',
         'Annual GW zonal tendency anomaly', 'Δ GW tendency (m s$^{-1}$ day$^{-1}$)',
         'Pressure (hPa)', 'Latitude (°)', True, False),
        ('annual_u_lat_lev.csv', 'fig02_zonal_wind_lat_pressure', 'lev', 'lat',
         'Annual zonal wind anomaly', 'Δ zonal wind (m s$^{-1}$)',
         'Pressure (hPa)', 'Latitude (°)', True, False),
        ('annual_walker_lon_lev.csv', 'fig03_walker_omega_lon_pressure', 'lon', 'lev',
         'Annual equatorial vertical motion anomaly', 'Δ omega (hPa day$^{-1}$)',
         'Longitude (°E)', 'Pressure (hPa)', False, True),
        ('annual_precip_lat_lon.csv', 'fig04_precipitation_lat_lon', 'lon', 'lat',
         'Annual Pacific precipitation anomaly', 'Δ precipitation (mm day$^{-1}$)',
         'Longitude (°E)', 'Latitude (°)', False, False),
        ('annual_u850_lat_lon.csv', 'fig05_pacific_u850_lat_lon', 'lon', 'lat',
         'Annual Pacific 850-hPa zonal wind anomaly', 'Δ U850 (m s$^{-1}$)',
         'Longitude (°E)', 'Latitude (°)', False, False),
    )
    for src, name, x, y, title, bar, xlabel, ylabel, px, py in specs:
        df = read_csv(d, src)
        if df is not None:
            if src == 'annual_walker_lon_lev.csv':
                check_fields(df, ('variable',), src)
                df = df.loc[df['variable'] == 'OMEGA'].copy()
            four_panels(df, out, name, x, y, title, bar, xlabel, ylabel,
                        pressure_x=px, pressure_y=py)
    monthly = read_csv(d, 'monthly_diagnostics.csv')
    if monthly is not None:
        plot_monthly(monthly, out)
    annual = read_csv(d, 'annual_diagnostics.csv')
    if annual is not None:
        annual.to_csv(out / 'annual_diagnostics_copy.csv', index=False)
        print('Annual diagnostic values read from the CSV archive:')
        for _, row in annual.iterrows():
            print(f" {row['case']:13s}  GW RMS={row['gw_rms_m_s_day']:.3f}; "
                  f"U30={row['u30_m_s']:.3f}; Walker={row['walker_hpa_day']:.3f}")


def plot_era5(d: Path, out: Path, annual_folder: Path | None):
    annual = read_csv(d, 'era5_annual_walker.csv')
    if annual is None:
        return
    check_fields(annual, ('year','walker_hpa_day'), 'era5_annual_walker.csv')
    fig, ax = plt.subplots(figsize=(10, 4.3), layout='constrained')
    ax.plot(annual['year'], annual['walker_hpa_day'], marker='o', markersize=3,
            label='ERA5 annual Walker index')
    mean = float(annual['walker_hpa_day'].mean())
    sd = float(annual['walker_hpa_day'].std(ddof=1))
    ax.axhline(mean, ls='--', label=f'ERA5 1991–2020 mean: {mean:.2f}')
    ax.fill_between(annual['year'], mean-sd, mean+sd, alpha=.15,
                    label=f'±1 interannual SD: {sd:.2f}')
    if annual_folder is not None:
        exp = read_csv(annual_folder, 'annual_diagnostics.csv')
        if exp is not None and 'case' in exp.columns:
            ctrl = exp[exp.case == 'CTRL']
            if not ctrl.empty:
                ax.axhline(float(ctrl.iloc[0]['walker_hpa_day']), ls=':',
                           label='SC-WACCM6 control (single model year)')
    ax.set(xlabel='Year', ylabel='Walker index (hPa day$^{-1}$)',
           title='ERA5 Walker index: historical variability')
    ax.legend(fontsize=8)
    save(fig, out, 'era5_walker_annual_context')


def plot_five_day(d: Path, out: Path):
    daily = read_csv(d, 'five_day_anomalies.csv')
    if daily is not None:
        check_fields(daily, ('case','sample','delta_gw_signed_m_s_day',
                             'delta_walker_hpa_day'), 'five_day_anomalies.csv')
        fig, axes = plt.subplots(2, 1, figsize=(10.2, 6.5), layout='constrained', sharex=True)
        for case in sorted(daily['case'].unique()):
            if case == 'CTRL':
                continue
            part = daily[daily.case == case].sort_values('sample')
            for ax, field in zip(axes, ('delta_gw_signed_m_s_day', 'delta_walker_hpa_day')):
                ax.plot(part['sample'], part[field], marker='.', label=case)
        axes[0].set_ylabel('Signed GW tendency anomaly\n(m s$^{-1}$ day$^{-1}$)')
        axes[1].set_ylabel('Walker index anomaly\n(hPa day$^{-1}$)')
        axes[1].set_xlabel('Model-day sample')
        for ax in axes:
            ax.axhline(0, color='0.4', linewidth=.8)
        axes[0].legend(fontsize=7, ncol=3)
        fig.suptitle('Exploratory five-day simulations (not annual findings)')
        save(fig, out, 'five_day_daily_exploration')
    interactions = read_csv(d, 'five_day_signed_gw_interactions.csv')
    if interactions is not None:
        check_fields(interactions, ('case', 'measured_signed_interaction_m_s_day',
                 'multiplicative_prediction_m_s_day'), 'five_day_signed_gw_interactions.csv')
        x = np.arange(len(interactions))
        fig, ax = plt.subplots(figsize=(9, 4.5), layout='constrained')
        ax.bar(x - .18, interactions.measured_signed_interaction_m_s_day,
               width=.36, label='Diagnosed signed interaction')
        ax.bar(x + .18, interactions.multiplicative_prediction_m_s_day,
               width=.36, label='Approximate forcing scaling')
        ax.set_xticks(x, interactions.case, rotation=20, ha='right')
        ax.set_ylabel('Signed GW tendency interaction (m s$^{-1}$ day$^{-1}$)')
        ax.set_title('Exploratory five-day comparison (not a Walker prediction)')
        ax.axhline(0, color='0.4', linewidth=.8)
        ax.legend()
        save(fig, out, 'five_day_signed_gw_interactions')


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--annual-dir', type=Path, help='Directory with annual exported CSVs')
    p.add_argument('--era5-dir', type=Path, help='Directory with ERA5 exported CSVs')
    p.add_argument('--five-day-dir', type=Path, help='Directory with exploratory exported CSVs')
    p.add_argument('--out', type=Path, default=Path('csv_reconstructed_figures'))
    args = p.parse_args()
    if not any((args.annual_dir, args.era5_dir, args.five_day_dir)):
        p.error('Supply at least one of --annual-dir, --era5-dir or --five-day-dir')
    args.out.mkdir(parents=True, exist_ok=True)
    if args.annual_dir:
        plot_annual(args.annual_dir, args.out)
    if args.era5_dir:
        plot_era5(args.era5_dir, args.out, args.annual_dir)
    if args.five_day_dir:
        plot_five_day(args.five_day_dir, args.out)
    print(f'Outputs: {args.out.resolve()}')


if __name__ == '__main__':
    main()
