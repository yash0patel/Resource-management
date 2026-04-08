from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Callable, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics.explanations import demand_explanation_for_peak_day
from analytics.plots import (
    plot_daily_demand,
    plot_feature_importance,
    plot_inventory_level_over_time,
    plot_shortage_highlight,
    plot_stock_depletion_curve,
)
from inventory.inventory_csv import (
    append_inventory_row,
    ensure_inventory_log_exists,
    load_inventory_log,
)
from inventory.planner import forecast_inventory
from recommendations.stock import (
    build_stock_recommendation_text,
    compute_stock_plan,
)
from ui.export import build_inventory_report_pdf
from ui.components import inject_saas_styles
from utils.holidays import holiday_promotion_feature
from utils.model import load_forecast_model
from utils.seasonality import season_from_month
from utils.weather import StoreLocation, WeatherProvider


st.set_page_config(page_title="AI-Powered Inventory (US-Based)", layout="wide")
inject_saas_styles()


@st.cache_data(show_spinner=False)
def _load_forecast_model_cached():
    return load_forecast_model()


def _holiday_info_for_date_factory() -> Callable[[date], Tuple[int, int, Optional[str]]]:
    # The planner uses apply_promotion itself; the second return value is ignored,
    # but we keep the function contract stable.
    return lambda d: holiday_promotion_feature(d, apply_promotion=False)


def _color_from_risk(risk_level: str) -> str:
    if risk_level.startswith("🟢"):
        return "#2ca02c"
    if risk_level.startswith("🟠"):
        return "#ff9800"
    return "#d62728"


def _format_int(n: Optional[float]) -> str:
    if n is None:
        return "—"
    return f"{int(round(n)):,}"


def _effective_bad_weather_override(start_dt: date) -> str:
    # Map to month-based “bad weather” similar to the project requirement.
    if start_dt.month in (12, 1, 2):
        return "Snowy"
    if start_dt.month in (3, 4, 5):
        return "Cloudy"
    return "Rainy"


model, active_model_path, model_notes = _load_forecast_model_cached()

st.title("AI-Powered Inventory Management System (US-Based)")
st.caption("US holidays + US weather patterns + ML demand forecasting → actionable inventory decisions.")
st.info(f"Model in use: `{active_model_path}`")
if model_notes:
    st.caption("Model selection notes: " + " | ".join(model_notes))


with st.sidebar:
    st.header("Planning Inputs")

    location = StoreLocation()

    api_key_default = os.getenv("OPENWEATHERMAP_API_KEY", "")
    api_key = st.text_input(
        "OpenWeatherMap API Key (optional)",
        value=api_key_default,
        type="password",
        help="If not provided or the API fails, the system uses deterministic US fallback weather logic.",
    )

    current_stock = st.number_input("Current Inventory Level", min_value=0, step=1, value=1000)
    category = st.selectbox("Category", ["Clothing", "Electronics", "Furniture", "Groceries", "Toys"])
    region = st.selectbox("Region", ["East", "North", "South", "West"])

    lead_time = st.slider("Lead Time (days)", min_value=1, max_value=21, value=3)
    buffer_days = st.slider("Safety Buffer (days)", min_value=1, max_value=30, value=7)

    apply_promotion = st.toggle(
        "Apply Promotion",
        value=False,
        help="Overrides US holiday detection for the ML feature `Holiday/Promotion` (1 = yes).",
    )

    st.divider()
    st.subheader("Date Range")
    start_date = st.date_input("Start Date", value=date.today() + timedelta(days=1))
    end_date = st.date_input("End Date", value=date.today() + timedelta(days=7))


if end_date < start_date:
    st.error("End Date cannot be before Start Date.")
    st.stop()


# Simulation controls (scenario / what-if)
if "sim_demand_multiplier" not in st.session_state:
    st.session_state.sim_demand_multiplier = 1.0
if "sim_weather_override" not in st.session_state:
    st.session_state.sim_weather_override = None  # "Sunny|Rainy|Cloudy|Snowy"
if "sim_promo_override" not in st.session_state:
    st.session_state.sim_promo_override = None  # bool override for apply_promotion

with st.container(border=True):
    st.markdown("### What-If Simulation (Auto re-run)")
    c1, c2, c3, c4 = st.columns(4)

    run_clicked = False
    if c1.button("Calculate Plan", use_container_width=True):
        run_clicked = True

    if c2.button("Festival Week", use_container_width=True):
        st.session_state.sim_promo_override = True
        st.session_state.sim_weather_override = None
        st.session_state.sim_demand_multiplier = 1.0
        run_clicked = True

    if c3.button("High Demand Surge", use_container_width=True):
        st.session_state.sim_promo_override = None
        st.session_state.sim_weather_override = None
        st.session_state.sim_demand_multiplier = 1.25
        run_clicked = True

    if c4.button("Bad Weather Week", use_container_width=True):
        st.session_state.sim_promo_override = None
        st.session_state.sim_weather_override = _effective_bad_weather_override(start_date)
        st.session_state.sim_demand_multiplier = 1.0
        run_clicked = True

    reset_col, _ = st.columns([2, 3])
    if reset_col.button("Reset Simulation", use_container_width=True):
        st.session_state.sim_demand_multiplier = 1.0
        st.session_state.sim_weather_override = None
        st.session_state.sim_promo_override = None
        run_clicked = True


effective_apply_promotion = (
    st.session_state.sim_promo_override
    if st.session_state.sim_promo_override is not None
    else apply_promotion
)
effective_demand_multiplier = float(st.session_state.sim_demand_multiplier or 1.0)
effective_weather_override = st.session_state.sim_weather_override

weather_provider = WeatherProvider(location=location, api_key=api_key or None)
weather_condition_for_date = weather_provider.condition_for_date
holiday_info_for_date = _holiday_info_for_date_factory()


forecast_df: Optional[pd.DataFrame] = None
stock_plan = None
stock_recommendation_text: list[str] = []
meta = {}

# Make the UI feel “alive”: run once on first page load so cards appear immediately.
if not st.session_state.get("did_initial_calc", False):
    run_clicked = True
    st.session_state.did_initial_calc = True

if run_clicked:
    with st.spinner("Running forecast: predicting demand + simulating stock..."):
        forecast_df, meta = forecast_inventory(
            model,
            start_date,
            end_date,
            inventory_level=float(current_stock),
            category=category,
            region=region,
            apply_promotion=bool(effective_apply_promotion),
            weather_condition_for_date=weather_condition_for_date,
            holiday_info_for_date=holiday_info_for_date,
            weather_override=effective_weather_override,
            demand_multiplier=effective_demand_multiplier,
        )

    stock_plan = compute_stock_plan(
        forecast_df,
        current_stock=float(current_stock),
        lead_time=int(lead_time),
        buffer_days=int(buffer_days),
        days_until_stockout=meta.get("days_until_stockout"),
    )
    stock_recommendation_text = build_stock_recommendation_text(
        stock_plan, promotion_enabled=bool(effective_apply_promotion)
    )


def _render_forecast_dashboard(df: pd.DataFrame) -> None:
    with st.container(border=True):
        st.subheader("📊 Inventory Dashboard")
        fig1 = plot_inventory_level_over_time(df)
        fig2 = plot_daily_demand(df)
        fig3 = plot_stock_depletion_curve(df)
        fig4 = plot_shortage_highlight(df)

        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.plotly_chart(fig1, use_container_width=True)
        with dcol2:
            st.plotly_chart(fig2, use_container_width=True)

        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)


def _render_stock_status(df: pd.DataFrame) -> None:
    with st.container(border=True):
        st.subheader("📦 Stock Status")

        avg_daily = float(df["Demand"].mean()) if not df.empty else 0.0
        safety_stock = avg_daily * float(buffer_days)
        reorder_point = avg_daily * float(lead_time) + safety_stock
        days_until_stockout = meta.get("days_until_stockout")

        # Risk badge
        risk_color = _color_from_risk(stock_plan.risk_level) if stock_plan else "#999"
        st.markdown(
            f"<div style='padding:10px;border-radius:12px;background:{risk_color};color:white;font-weight:700;'>"
            f"Risk Level: {stock_plan.risk_level if stock_plan else '—'}</div>",
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average Daily Demand", _format_int(avg_daily))
        col2.metric("Days Until Stockout", "—" if days_until_stockout is None else f"{int(days_until_stockout)}")
        col3.metric("Safety Stock (units)", _format_int(safety_stock))
        col4.metric("Reorder Point (ROP)", _format_int(reorder_point))

        st.markdown("---")
        st.subheader("Forecast Table")
        display_cols = ["Date", "Weather Condition", "Holiday Name", "Holiday", "Holiday/Promotion", "Demand", "Opening Stock", "Closing Stock", "Stock Status"]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, height=360)


def _render_recommendations(df: pd.DataFrame) -> None:
    with st.container(border=True):
        st.subheader("🧠 Recommendations")

        # Reorder + risk insights
        if stock_plan:
            st.metric("Recommended Reorder Quantity", f"{stock_plan.recommended_reorder_qty:,} units")

        for msg in stock_recommendation_text:
            st.write(f"- {msg}")

        # Demand explanation: why demand is high?
        if not df.empty:
            peak_row = df.loc[df["Demand"].idxmax()]
            peak_day = peak_row["Date"]
            base_weather = str(peak_row["Weather Condition"])
            base_holiday_promo = int(peak_row["Holiday/Promotion"])

            try:
                with st.spinner("Generating demand explanation..."):
                    exp = demand_explanation_for_peak_day(
                        model,
                        peak_day,
                        category=category,
                        region=region,
                        base_weather_condition=base_weather,
                        base_holiday_promotion_flag=base_holiday_promo,
                        inventory_level=float(current_stock),
                        holiday_info_for_date=holiday_info_for_date,
                    )
            except Exception as e:
                st.warning(f"Could not generate demand explanation: {e}")
                return

            st.markdown("---")
            st.subheader("🔍 Why Demand Is High?")
            st.caption(f"Peak day: {peak_day}")
            st.write(
                f"Holiday impact: demand changes by {exp['holiday_impact']['delta']:,} units "
                f"(baseline {exp['holiday_impact']['baseline']:,} vs without holiday {exp['holiday_impact']['without_holiday']:,})."
            )
            st.write(
                f"Weather impact: demand changes by {exp['weather_impact']['delta']:,} units "
                f"(baseline {exp['weather_impact']['baseline']:,} vs Sunny {exp['weather_impact']['weather_as_sunny']:,})."
            )
            st.write(
                f"Seasonal trend: peak potential season is **{exp['seasonality_trend']['best_season']}** "
                f"(baseline vs average delta: {exp['seasonality_trend']['seasonal_delta_vs_avg']:.0f})."
            )


def _render_analytics(df: pd.DataFrame) -> None:
    with st.container(border=True):
        st.subheader("📈 Inventory Analytics")

        avg_daily = float(df["Demand"].mean()) if not df.empty else 0.0
        st.metric("Average Demand", _format_int(avg_daily))

        peak_days = df.sort_values("Demand", ascending=False).head(3)[["Date", "Demand", "Weather Condition", "Holiday/Promotion"]]
        st.write("Peak demand days (top 3):")
        st.dataframe(peak_days, use_container_width=True, height=160)

        lowest_stock_days = df.sort_values("Closing Stock", ascending=True).head(3)[["Date", "Closing Stock", "Demand", "Weather Condition"]]
        st.write("Lowest stock days (bottom 3):")
        st.dataframe(lowest_stock_days, use_container_width=True, height=160)

        fig_imp = plot_feature_importance(model)
        if fig_imp is not None:
            st.markdown("---")
            st.subheader("Feature Importance (Model-driven)")
            st.plotly_chart(fig_imp, use_container_width=True)


def _render_simulation_scenarios() -> None:
    with st.container(border=True):
        try:
            st.subheader("👥 Inventory Simulation (Scenario)")
            st.caption("Compare promotion vs non-promotion, and holiday vs non-holiday demand impact.")

            colL, colR = st.columns(2)
            with colL:
                with st.container(border=True):
                    st.markdown("**Promotion vs No Promotion**")
                    with st.spinner("Scenario: Promo vs No Promo"):
                        promo_df, _ = forecast_inventory(
                            model,
                            start_date,
                            end_date,
                            inventory_level=float(current_stock),
                            category=category,
                            region=region,
                            apply_promotion=True,
                            weather_condition_for_date=weather_condition_for_date,
                            holiday_info_for_date=holiday_info_for_date,
                            weather_override=effective_weather_override,
                            demand_multiplier=effective_demand_multiplier,
                        )
                        no_promo_df, _ = forecast_inventory(
                            model,
                            start_date,
                            end_date,
                            inventory_level=float(current_stock),
                            category=category,
                            region=region,
                            apply_promotion=False,
                            weather_condition_for_date=weather_condition_for_date,
                            holiday_info_for_date=holiday_info_for_date,
                            weather_override=effective_weather_override,
                            demand_multiplier=effective_demand_multiplier,
                        )

                    total_promo = float(promo_df["Demand"].sum())
                    total_no_promo = float(no_promo_df["Demand"].sum())
                    diff = total_promo - total_no_promo
                    stockout_promo = (promo_df["Closing Stock"] < 0).any()
                    stockout_no_promo = (no_promo_df["Closing Stock"] < 0).any()
                    st.metric("Total Demand (Promo)", _format_int(total_promo))
                    st.metric("Total Demand (No Promo)", _format_int(total_no_promo))
                    st.metric("Demand Difference", f"{diff:+.0f} units")
                    st.write(
                        f"Stockout with promo: {stockout_promo}, without promo: {stockout_no_promo}"
                    )

            with colR:
                with st.container(border=True):
                    st.markdown("**Holiday vs Non-Holiday**")
                    with st.spinner("Scenario: Holiday vs Non-Holiday"):
                        holiday_df, _ = forecast_inventory(
                            model,
                            start_date,
                            end_date,
                            inventory_level=float(current_stock),
                            category=category,
                            region=region,
                            apply_promotion=False,
                            weather_condition_for_date=weather_condition_for_date,
                            holiday_info_for_date=holiday_info_for_date,
                            weather_override=effective_weather_override,
                            demand_multiplier=effective_demand_multiplier,
                        )
                        non_holiday_df, _ = forecast_inventory(
                            model,
                            start_date,
                            end_date,
                            inventory_level=float(current_stock),
                            category=category,
                            region=region,
                            apply_promotion=False,
                            weather_condition_for_date=weather_condition_for_date,
                            holiday_info_for_date=holiday_info_for_date,
                            weather_override=effective_weather_override,
                            demand_multiplier=effective_demand_multiplier,
                            holiday_promotion_override=0,
                        )

                    total_holiday = float(holiday_df["Demand"].sum())
                    total_non_holiday = float(non_holiday_df["Demand"].sum())
                    diff = total_holiday - total_non_holiday
                    shortages_h = int((holiday_df["Closing Stock"] < 0).sum())
                    shortages_nh = int((non_holiday_df["Closing Stock"] < 0).sum())
                    st.metric("Total Demand (Holiday)", _format_int(total_holiday))
                    st.metric("Total Demand (Non-Holiday)", _format_int(total_non_holiday))
                    st.metric("Demand Difference", f"{diff:+.0f} units")
                    st.write(
                        f"Shortage days (Holiday): {shortages_h}, (Non-Holiday): {shortages_nh}"
                    )

            # Shared overlay charts (demand + stock impact)
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=promo_df["Date"],
                    y=promo_df["Demand"],
                    mode="lines",
                    name="Promo Demand",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=no_promo_df["Date"],
                    y=no_promo_df["Demand"],
                    mode="lines",
                    name="No Promo Demand",
                )
            )
            fig.update_layout(
                title="Demand Impact: Promo vs No Promo",
                template="plotly_white",
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Scenario simulation failed: {e}")


def _render_update_inventory() -> None:
    ensure_inventory_log_exists()
    with st.container(border=True):
        st.subheader("📝 Update Inventory")
        st.caption("Daily inventory update (CSV append). Weather + US holiday detection are auto-filled.")

        with st.form("inventory_update_form", clear_on_submit=True):
            d_input = st.date_input("Date", value=date.today())
            inv_level = st.number_input("Inventory Level", min_value=0, step=1)
            units_sold = st.number_input("Units Sold (Demand)", min_value=0, step=1)
            cat = st.selectbox("Category", ["Clothing", "Electronics", "Furniture", "Groceries", "Toys"])
            reg = st.selectbox("Region", ["East", "North", "South", "West"])
            promo_toggle = st.toggle("Apply Promotion (overrides holiday)", value=False)

            # Auto-fill
            weather_cond = weather_provider.condition_for_date(d_input)
            holiday_flag, _holiday_promo_flag, holiday_name = holiday_promotion_feature(d_input, apply_promotion=False)
            holiday_promo_flag = 1 if promo_toggle else holiday_flag

            st.markdown(f"📍 Weather (Auto-detected, New York): **{weather_cond}**")
            st.markdown(f"📅 Holiday (Auto-detected, US): **{holiday_name or 'None'}** (flag={holiday_flag})")

            submit = st.form_submit_button("Append to Inventory CSV")

        if submit:
            append_inventory_row(
                d=d_input,
                inventory_level=float(inv_level),
                units_sold=float(units_sold),
                category=cat,
                region=reg,
                weather_condition=weather_cond,
                holiday_flag=int(holiday_flag),
                holiday_promotion_flag=int(holiday_promo_flag),
            )
            st.success("Inventory row appended safely.")

        # Show tail
        df_log = load_inventory_log()
        if not df_log.empty:
            st.markdown("Latest entries:")
            st.dataframe(df_log.tail(10), use_container_width=True, height=260)


def _render_exports(df: pd.DataFrame) -> None:
    with st.container(border=True):
        st.subheader("📤 Export Reports")
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Forecast CSV",
            data=csv_bytes,
            file_name="inventory_forecast.csv",
            mime="text/csv",
            use_container_width=True,
        )

        if stock_plan is not None:
            input_summary = {
                "Store location": f"{weather_provider.location.city}, {weather_provider.location.country}",
                "Planning window": f"{start_date.isoformat()} → {end_date.isoformat()}",
                "Category": category,
                "Region": region,
                "Current inventory": f"{int(current_stock):,}",
                "Lead time (days)": int(lead_time),
                "Safety buffer (days)": int(buffer_days),
                "Effective apply promotion": bool(effective_apply_promotion),
                "Effective demand multiplier": effective_demand_multiplier,
                "Weather override": effective_weather_override or "Auto-detected",
                "Model": active_model_path,
            }

            charts = {
                "Inventory Level Over Time": plot_inventory_level_over_time(df),
                "Daily Demand (Consumption)": plot_daily_demand(df),
                "Stock Depletion Curve": plot_stock_depletion_curve(df),
            }
            pdf_bytes = build_inventory_report_pdf(
                forecast_df=df,
                stock_recommendation_text=stock_recommendation_text,
                input_summary=input_summary,
                charts=charts,
            )

            st.download_button(
                "Download PDF Report",
                data=pdf_bytes,
                file_name="inventory_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


if forecast_df is not None:
    _render_forecast_dashboard(forecast_df)
    _render_stock_status(forecast_df)
    _render_recommendations(forecast_df)
    _render_analytics(forecast_df)
    _render_simulation_scenarios()
    _render_update_inventory()
    _render_exports(forecast_df)
else:
    st.info("Click `Calculate Plan` to generate the inventory dashboard and recommendations.")
    _render_update_inventory()

