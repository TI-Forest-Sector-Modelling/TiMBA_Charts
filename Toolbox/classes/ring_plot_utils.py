from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go

RING_PALETTE = [
    "#9C5D0FB9",
    "#E8D7B5", #"#9C5D0FB9",
    "#DDB77D",
    "#CD9655",
    "#B97932",
    #"#9C5D0F",
    "#7A481D",
    "#5C3718",
]
RING_ROW_COLOR = "#4D2D0763"  # grey, used for "rest of world"
_RING_EPS = 1e-9


@dataclass
class _RingGeometry:
    """All numbers needed to draw the ring plot (no Plotly objects yet)."""

    years: list            # sorted years, one per segment
    centers: list          # centre angle (degrees) of each segment
    cells: dict            # partner -> dict of lists for Barpolar
    sep_theta: list        # separator lines: angles (None = line break)
    sep_r: list            # separator lines: radii  (None = line break)
    total_r: list          # radius where the total label of each year is placed
    total_text: list       # text of the total labels
    max_ring: int          # number of rings of the largest year


class RingPlotsUtils:
    """
    Helper functions for the ring plot (Radial Unit Chart).

    Input is a pivot table: index = year, columns = partners (incl. one
    "rest of world" column), values = trade value. See Plots.create_trade_ring_plot.
    """

    def __init__(self, template="plotly_white", pad_down=150, margin_top=60, title_x=0.5, title_y=0.96):
        self.template = template
        self.pad_down = pad_down
        self.margin_top = margin_top
        self.title_x = title_x
        self.title_y = title_y

    # ------------------------------------------------------------------ #
    # Data preparation
    # ------------------------------------------------------------------ #
    @staticmethod
    def _ring_nice_unit(max_total: float, target_rings: int = 15) -> float:
        """Round value per ring (1, 2, 5, 10, ... x 10^n) so that the largest year has about `target_rings` rings."""
        if not max_total or max_total <= 0 or np.isnan(max_total):
            return 1.0
        raw = max_total / target_rings
        mag = 10 ** math.floor(math.log10(raw))
        for m in (1, 2, 5, 10):
            if m * mag >= raw:
                return m * mag
        return 10 * mag

    @staticmethod
    def _ring_prepare_pivot(pivot, top, row_label):
        """
        Clean the pivot table and make `top` and the columns consistent.

        - NaN -> 0, years sorted.
        - top=None: all columns except `row_label` are top partners.
        - Columns that are neither in `top` nor `row_label` are summed into
          `row_label`.
        - `top` is always sorted by the total over all years, largest first,
          whatever order was passed in. The colours (see _ring_assign_colors)
          and the legend follow this order: the partner with the largest trade
          gets the first colour, the smallest top partner the last one.

        Returns
        -------
        pivot : DataFrame, index = year, columns = top partners (+ row_label)
        top   : list of top partners, largest total first
        """
        pivot = pivot.copy().fillna(0.0).sort_index()

        if top is None:
            top = [c for c in pivot.columns if c != row_label]
        else:
            top = [p for p in top if p in pivot.columns and p != row_label]

        # rank by total over all years: largest first (stable for ties)
        top = sorted(top, key=lambda p: -pivot[p].sum())

        others = [c for c in pivot.columns if c not in top and c != row_label]
        if others:
            pivot[row_label] = pivot.get(row_label, 0.0) + pivot[others].sum(axis=1)
            pivot = pivot.drop(columns=others)

        return pivot, top

    @staticmethod
    def _ring_assign_colors(top, row_label, partner_colors=None):
        """One fixed colour per partner; grey for rest of world. `partner_colors` overrides single partners."""
        cmap = {p: RING_PALETTE[i % len(RING_PALETTE)] for i, p in enumerate(top)}
        cmap[row_label] = RING_ROW_COLOR
        if partner_colors:
            cmap.update(partner_colors)
        return cmap

    # ------------------------------------------------------------------ #
    # Geometry
    # ------------------------------------------------------------------ #
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
    def _ring_layout_year(pivot, year, order, a0, span, unit, cells, sep_theta, sep_r):
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

            for ring, f0, f1 in RingPlotsUtils._ring_pieces(cum, cum + v, unit):
                c = cells[p]
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
    def _ring_compute_geometry(pivot, top, unit, gap_deg, row_label, row_outermost):
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

            order = RingPlotsUtils._ring_fill_order(pivot, year, top, row_label, row_outermost)
            by_ring, total = RingPlotsUtils._ring_layout_year(
                pivot, year, order, a0, span, unit, cells, sep_theta, sep_r
            )

            arc_t, arc_r = RingPlotsUtils._ring_arc_separators(by_ring, a0, span, unit)
            sep_theta += arc_t
            sep_r += arc_r

            top_ring = math.ceil(total / unit - 1e-12)
            max_ring = max(max_ring, top_ring)
            total_r.append(top_ring * unit + unit * 0.7)  # label sits just above the last ring
            total_text.append(f"{total:,.0f}" if total >= 100 else f"{total:,.1f}")

        return _RingGeometry(years, centers, cells, sep_theta, sep_r, total_r, total_text, max_ring)

    # ------------------------------------------------------------------ #
    # Plotly traces
    # ------------------------------------------------------------------ #
    @staticmethod
    def _ring_area_traces(geo, top, row_label, cmap, unit_label):
        """One Barpolar trace per partner (one colour, one legend entry)."""
        traces = []
        for p in [*top, row_label]:
            c = geo.cells.get(p)
            if not c:
                continue

            color = cmap[p]
            traces.append(
                go.Barpolar(
                    theta=c["theta"], width=c["width"], base=c["base"], r=c["r"],
                    name=p, legendgroup=p, showlegend=True,
                    # outline in the fill colour closes hairline gaps between cells
                    marker=dict(color=color, line=dict(color=color, width=0.6)),
                    customdata=c["cd"],
                    hovertemplate=(
                        "%{customdata[0]}<br>%{customdata[1]}: "
                        "%{customdata[2]:,.2f} " + unit_label + "<extra></extra>"
                    ),
                )
            )
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

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _ring_apply_layout(self, fig, geo, unit, unit_label, hole, center_label, center_font_size, title_text,
                           year_offset=1.5):
        """
        Title, axes, legend and the optional label in the centre hole.

        year_offset: distance of the year labels from the outermost ring, in
        rings. Larger values move the years further out (and the rings get
        smaller, because the plot area then covers a larger radius).
        """
        r_rings = (geo.max_ring + 1.6) * unit       # head room for the total labels
        r_max = r_rings + year_offset * unit        # plus space for the year labels
        grid_step = unit * 5                        # one grid line every 5 rings

        # Year labels as text (the built-in tick labels cannot be moved)
        fig.add_trace(go.Scatterpolar(
            theta=geo.centers,
            r=[r_max - 0.5 * unit] * len(geo.years),
            mode="text",
            text=[str(y) for y in geo.years],
            textfont=dict(size=12),
            hoverinfo="skip", showlegend=False,
        ))

        fig.update_layout(
            title={
                "text": title_text,
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            autosize = True,
            template=self.template,
            margin=dict(l=2, r=0, t=self.margin_top, b=25),
            legend=dict(orientation="v", y=0.5, x=-0.05, xanchor="center"),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                hole=hole,
                barmode="overlay",
                radialaxis=dict(
                    range=[0, r_max],
                    tickvals=list(np.arange(grid_step, r_rings, grid_step)),
                    title=dict(text=unit_label, font=dict(size=10)),
                    tickfont=dict(size=10),
                    showline=False,
                    gridcolor="rgba(128,128,128,0.3)",
                    angle=90,
                    showticklabels=False
                ),
                angularaxis=dict(
                    rotation=90,            # first segment starts at 12 o'clock
                    direction="clockwise",
                    tickmode="array",
                    tickvals=geo.centers,
                    showticklabels=False,   # years are drawn as text above
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
            margin=dict(l=20, r=10, t=self.margin_top, b=80),
        )
        return fig