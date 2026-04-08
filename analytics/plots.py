from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.graph_objects as go


def _stock_color(stock: float) -> str:
    if stock <= 0:
        return "#d62728"  # red
    if stock < 0.25:  # not used for scaled values but kept for future
        return "#ff9800"  # orange
    return "#2ca02c"  # green


def plot_inventory_level_over_time(forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Closing Stock"],
            mode="lines+markers",
            name="Closing Stock",
            marker=dict(size=6),
        )
    )
    fig.update_layout(
        title="Inventory Level Over Time",
        xaxis_title="Date",
        yaxis_title="Units",
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_daily_demand(forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=forecast_df["Date"],
            y=forecast_df["Demand"],
            name="Daily Demand (Consumption)",
        )
    )
    fig.update_layout(
        title="Daily Demand (Consumption)",
        xaxis_title="Date",
        yaxis_title="Units",
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_stock_depletion_curve(forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Closing Stock"],
            mode="lines",
            name="Stock Depletion Curve",
        )
    )

    shortage = forecast_df[forecast_df["Closing Stock"] < 0]
    if not shortage.empty:
        fig.add_trace(
            go.Scatter(
                x=shortage["Date"],
                y=shortage["Closing Stock"],
                mode="markers",
                name="Shortage",
                marker=dict(color="#d62728", size=10),
            )
        )

    fig.update_layout(
        title="Stock Depletion Curve",
        xaxis_title="Date",
        yaxis_title="Closing Stock (units)",
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_shortage_highlight(forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Closing Stock"],
            mode="lines+markers",
            name="Closing Stock",
        )
    )

    shortage = forecast_df[forecast_df["Closing Stock"] < 0]
    if not shortage.empty:
        fig.add_trace(
            go.Scatter(
                x=shortage["Date"],
                y=shortage["Closing Stock"],
                mode="markers",
                name="Shortage Highlight",
                marker=dict(color="#d62728", size=12),
            )
        )

    fig.update_layout(
        title="Shortage Highlight",
        xaxis_title="Date",
        yaxis_title="Closing Stock (units)",
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_feature_importance(model, *, top_n: int = 12) -> Optional[go.Figure]:
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return None

    names = list(getattr(model, "feature_names_in_", []))
    if not names:
        return None

    imp_df = pd.DataFrame({"feature": names, "importance": importances})
    imp_df = imp_df.sort_values("importance", ascending=False).head(top_n)

    fig = go.Figure(
        go.Bar(
            x=imp_df["importance"],
            y=imp_df["feature"],
            orientation="h",
        )
    )
    fig.update_layout(
        title="Feature Importance (Model-driven)",
        template="plotly_white",
        height=420,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig

