from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from Toolbox.classes.utils import PlotUtils
from Toolbox.parameters.default_parameters import under_to_over_bark

# Ring plot: colour pair per partner (dark tone, light tone).
# Which tone is used for historic vs. forecast years is set by `forecast_is_dark`.
RING_PALETTE = [
    ("#3283D3", "#7FBCF8FF"),  # blue
    ("#C94E25", "#F59A7B"),  # coral
    ("#1CB657", "#5FE4B8"),  # teal
    ("#9C5D0FB9", "#E9A63A"),  # amber
    ("#D33B6E", "#F3759F"),  # pink
    ("#695FDA", "#8982F5"),  # violet
    ("#4A8F12", "#A5DB5A"),  # green
    ("#C73636", "#FA6A6A"),  # red
]
RING_ROW_COLORS = ("#6E6D68", "#D3D1C7")  # grey, used for "rest of world"
_RING_EPS = 1e-9


@dataclass
class _RingGeometry:
    """All numbers needed to draw the ring plot (no Plotly objects yet)."""

    years: list            # sorted years, one per segment
    centers: list          # centre angle (degrees) of each segment
    cells: dict            # (partner, is_forecast) -> dict of lists for Barpolar
    sep_theta: list        # separator lines: angles (None = line break)
    sep_r: list            # separator lines: radii  (None = line break)
    total_r: list          # radius where the total label of each year is placed
    total_text: list       # text of the total labels
    max_ring: int          # number of rings of the largest year


class RingPlotsUtils:

    def __init__(self, template="plotly_white"):
        self.template = template
        self.pad_down = 150
        self.margin_top = 60
        self.title_x = 0.5
        self.title_y = 0.925   

    @staticmethod
    def _ring_nice_unit(max_total: float, target_rings: int = 15) -> float:
        """Round value per ring (1, 2, 5, 10, ... x 10^n) so that the largest year has about `target_rings` rings."""
        if max_total <= 0:
            return 1.0
        raw = max_total / target_rings
        mag = 10 ** math.floor(math.log10(raw))
        for m in (1, 2, 5, 10):
            if m * mag >= raw:
                return m * mag
        return 10 * mag

    @staticmethod
    def _ring_aggregate_partners(df, year_col, partner_col, value_col, top_n, row_label):
        """
        Keep the `top_n` partners (by total value over all years) and sum all
        other partners into one `row_label` ("rest of world") entry.

        Returns
        -------
        pivot : DataFrame, index = year, columns = partner, values = value
        top   : list of the top-N partner names, largest first
        """
        d = df[[year_col, partner_col, value_col]].copy()
        d.columns = ["y", "p", "v"]

        totals = d.groupby("p").v.sum().sort_values(ascending=False)
        top = list(totals.index[:top_n])

        d["p"] = d.p.where(d.p.isin(top), row_label)
        d = d.groupby(["y", "p"], as_index=False).v.sum()
        pivot = d.pivot(index="y", columns="p", values="v").fillna(0.0).sort_index()
        return pivot, top

    @staticmethod
    def _ring_assign_colors(top, row_label, partner_colors=None):
        """Fixed colour pair (dark, light) per partner; grey for rest of world."""
        cmap = {p: RING_PALETTE[i % len(RING_PALETTE)] for i, p in enumerate(top)}
        cmap[row_label] = RING_ROW_COLORS
        if partner_colors:
            cmap.update(partner_colors)
        return cmap

    @staticmethod
    def _ring_fill_order(pivot, year, top, row_label, row_outermost):
        """
        Order in which the partners of one year are filled into the rings,
        from the centre outwards: LARGEST value first, smallest value last.

        If `row_outermost` is True, "rest of world" always comes last
        (outermost), regardless of its size. Otherwise it is sorted like any
        other partner.
        """
        present = [p for p in top if p in pivot.columns]
        has_row = row_label in pivot.columns

        if has_row and not row_outermost:
            return sorted(present + [row_label], key=lambda p: -pivot.at[year, p])

        order = sorted(present, key=lambda p: -pivot.at[year, p])
        if has_row:
            order.append(row_label)
        return order

    @staticmethod
    def _ring_pieces(start, end, unit):
        """
        Split the value range [start, end) into pieces that each lie inside one ring.

        Yields (ring, f0, f1): the ring index and the start / end of the piece
        as a fraction (0..1) of the ring's angular width.
        """
        ring = int(start // unit)
        while ring * unit < end - 1e-12:
            f0 = (max(start, ring * unit) - ring * unit) / unit
            f1 = (min(end, (ring + 1) * unit) - ring * unit) / unit
            if f1 > f0 + 1e-12:
                yield ring, f0, f1
            ring += 1

    @staticmethod
    def _ring_layout_year(pivot, year, order, a0, span, unit, is_forecast, cells, sep_theta, sep_r):
        """
        Create all ring cells of one year and the radial separators between
        different partners within a ring. Appends to `cells`, `sep_theta`
        and `sep_r` in place.

        Returns
        -------
        by_ring : dict ring -> list of (partner, f0, f1), needed for the arc separators
        total   : total value of the year
        """
        by_ring = defaultdict(list)
        cum = 0.0

        for p in order:
            v = float(pivot.at[year, p])
            if v <= 0:
                continue

            for ring, f0, f1 in Plots._ring_pieces(cum, cum + v, unit):
                c = cells[(p, is_forecast)]
                c["theta"].append(a0 + span * (f0 + f1) / 2)  # centre angle of the cell
                c["width"].append(span * (f1 - f0))           # angular width of the cell
                c["base"].append(ring * unit)                 # inner radius
                c["r"].append(unit)                           # ring thickness
                c["cd"].append((p, year, v))                  # hover data (full value)
                by_ring[ring].append((p, f0, f1))

                # A piece that does not start at the ring's start borders another partner.
                if f0 > _RING_EPS:
                    t = a0 + span * f0
                    sep_theta += [t, t, None]
                    sep_r += [ring * unit, (ring + 1) * unit, None]

            cum += v

        return by_ring, cum

    @staticmethod
    def _ring_arc_separators(by_ring, a0, span, unit):
        """
        Arc-shaped separators between ring k and ring k+1, drawn only where
        the partner below differs from the partner above.

        Returns two lists (theta, r) with None as line breaks.
        """
        theta, radius = [], []
        for ring, lower in by_ring.items():
            upper = by_ring.get(ring + 1)
            if not upper:
                continue
            r = (ring + 1) * unit
            for pa, a_f0, a_f1 in lower:
                for pb, b_f0, b_f1 in upper:
                    lo, hi = max(a_f0, b_f0), min(a_f1, b_f1)  # overlapping angular range
                    if hi > lo + _RING_EPS and pa != pb:
                        npts = max(2, int((hi - lo) * span / 2) + 2)  # enough points for a smooth arc
                        theta += list(a0 + span * np.linspace(lo, hi, npts)) + [None]
                        radius += [r] * npts + [None]
        return theta, radius

    @staticmethod
    def _ring_compute_geometry(pivot, top, last_actual, unit, gap_deg, row_label, row_outermost):
        """Run the geometry steps for all years and collect the results."""
        years = list(pivot.index)
        w = 360.0 / len(years)   # angle per year
        span = w - gap_deg       # drawn width (the rest is the gap between years)

        cells = defaultdict(lambda: {"theta": [], "width": [], "base": [], "r": [], "cd": []})
        sep_theta, sep_r = [], []
        centers, total_r, total_text = [], [], []
        max_ring = 0

        for i, year in enumerate(years):
            a0 = i * w + gap_deg / 2
            centers.append(a0 + span / 2)

            order = Plots._ring_fill_order(pivot, year, top, row_label, row_outermost)
            by_ring, total = Plots._ring_layout_year(
                pivot, year, order, a0, span, unit, year > last_actual, cells, sep_theta, sep_r
            )

            arc_t, arc_r = Plots._ring_arc_separators(by_ring, a0, span, unit)
            sep_theta += arc_t
            sep_r += arc_r

            top_ring = math.ceil(total / unit - 1e-12)
            max_ring = max(max_ring, top_ring)
            total_r.append(top_ring * unit + unit * 0.7)  # label sits just above the last ring
            total_text.append(f"{total:,.0f}" if total >= 100 else f"{total:,.1f}")

        return _RingGeometry(years, centers, cells, sep_theta, sep_r, total_r, total_text, max_ring)

    @staticmethod
    def _ring_area_traces(geo, top, row_label, cmap, unit_label, forecast_is_dark):
        """One Barpolar trace per partner and period (historic / forecast)."""
        traces = []
        legend_done = set()

        for p in [*top, row_label]:
            for is_forecast in (False, True):
                c = geo.cells.get((p, is_forecast))
                if not c:
                    continue

                dark, light = cmap[p]
                use_dark = is_forecast if forecast_is_dark else not is_forecast
                color = dark if use_dark else light

                traces.append(
                    go.Barpolar(
                        theta=c["theta"], width=c["width"], base=c["base"], r=c["r"],
                        name=p, legendgroup=p,
                        # one legend entry per partner (the historic trace)
                        showlegend=p not in legend_done and not is_forecast,
                        # outline in the fill colour closes hairline gaps between cells
                        marker=dict(color=color, line=dict(color=color, width=0.6)),
                        customdata=c["cd"],
                        hovertemplate=(
                            "%{customdata[0]}<br>%{customdata[1]}: "
                            "%{customdata[2]:,.2f} " + unit_label + "<extra></extra>"
                        ),
                    )
                )
                if not is_forecast:
                    legend_done.add(p)
        return traces

    @staticmethod
    def _ring_separator_trace(geo, line_color):
        """All separator lines as one Scatterpolar trace (None values break the line)."""
        return go.Scatterpolar(
            theta=geo.sep_theta, r=geo.sep_r, mode="lines",
            line=dict(color=line_color, width=1.3),
            hoverinfo="skip", showlegend=False,
        )

    @staticmethod
    def _ring_total_trace(geo):
        """Total value as text at the end of each segment."""
        return go.Scatterpolar(
            theta=geo.centers, r=geo.total_r, mode="text", text=geo.total_text,
            textfont=dict(size=11), hoverinfo="skip", showlegend=False,
        )

    def _ring_apply_layout(self, fig, geo, unit, unit_label, hole, center_label, center_font_size, title_text):
        """Title, axes, legend and the optional label in the centre hole."""
        r_max = (geo.max_ring + 1.6) * unit  # head room for the total labels
        grid_step = unit * 5                 # one grid line every 5 rings

        fig.update_layout(
            title={
                "text": title_text,
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            template=self.template,
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                hole=hole,
                barmode="overlay",
                radialaxis=dict(
                    range=[0, r_max],
                    tickvals=list(np.arange(grid_step, r_max, grid_step)),
                    title=dict(text=unit_label, font=dict(size=10)),
                    tickfont=dict(size=10),
                    showline=False,
                    gridcolor="rgba(128,128,128,0.3)",
                    angle=90,
                ),
                angularaxis=dict(
                    rotation=90,            # first segment starts at 12 o'clock
                    direction="clockwise",
                    tickmode="array",
                    tickvals=geo.centers,
                    ticktext=[str(y) for y in geo.years],
                    showgrid=False,
                    showline=False,
                    ticks="",
                ),
            ),
        )

        if center_label:
            # (0.5, 0.5) in paper coordinates is the centre of the polar plot
            fig.add_annotation(
                x=0.5, y=0.5, xref="paper", yref="paper",
                text=f"<b>{center_label}</b>", showarrow=False,
                font=dict(size=center_font_size),
            )

    def _ring_empty_figure(self, message: str) -> go.Figure:
        """Empty figure with a message, so that a callback never fails on empty data."""
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5, xref="paper", yref="paper",
            text=message, showarrow=False, font=dict(size=14),
        )
        fig.update_layout(
            template=self.template,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
        )
        return fig