from __future__ import annotations

import io
from typing import Optional

import pandas as pd


def _try_plotly_to_png_bytes(fig) -> Optional[bytes]:
    try:
        # Requires plotly+kaleido.
        return fig.to_image(format="png")
    except Exception:
        return None


def build_inventory_report_pdf(
    *,
    forecast_df: pd.DataFrame,
    stock_recommendation_text: list[str],
    input_summary: dict,
    charts: dict,
) -> bytes:
    """
    Create a simple PDF report (best-effort).

    If optional deps are missing, the PDF will still include text-only content.
    """
    buffer = io.BytesIO()

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader

        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        y = height - 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "AI-Powered Inventory Management System (US-Based)")

        y -= 22
        c.setFont("Helvetica", 10)
        c.drawString(40, y, "Report generated from the current planning view.")

        y -= 24
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Input Summary")
        y -= 14
        c.setFont("Helvetica", 9)
        for k, v in input_summary.items():
            line = f"{k}: {v}"
            c.drawString(40, y, line[:120])
            y -= 12
            if y < 120:
                c.showPage()
                y = height - 40
                c.setFont("Helvetica", 9)

        c.showPage()
        y = height - 40
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Recommendations")
        y -= 14
        c.setFont("Helvetica", 10)
        for msg in stock_recommendation_text:
            for wrapped in [msg]:
                c.drawString(40, y, wrapped[:120])
                y -= 14
                if y < 90:
                    c.showPage()
                    y = height - 40
                    c.setFont("Helvetica", 10)

        # Charts: one per page (best-effort)
        for chart_title, fig in charts.items():
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, chart_title)
            y -= 18

            png_bytes = _try_plotly_to_png_bytes(fig)
            if png_bytes:
                img = ImageReader(io.BytesIO(png_bytes))
                # Fit roughly within page
                c.drawImage(img, 40, 90, width=width - 80, height=height - 160, preserveAspectRatio=True)
            else:
                c.setFont("Helvetica", 9)
                c.drawString(40, 100, "Chart image not available (install kaleido for better PDF charts).")

        # Final page: brief table snippet
        c.showPage()
        y = height - 40
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Inventory Status (Tail)")
        y -= 14
        c.setFont("Helvetica", 9)
        tail = forecast_df.tail(7).copy()
        for _, r in tail.iterrows():
            line = f"{r['Date']}: Closing={r['Closing Stock']:.0f}, Demand={r['Demand']:.0f}, Status={r['Stock Status']}"
            c.drawString(40, y, line[:140])
            y -= 12
            if y < 90:
                c.showPage()
                y = height - 40
                c.setFont("Helvetica", 9)

        c.save()
        return buffer.getvalue()

    except Exception:
        # Text-only fallback: return empty bytes so the UI can still proceed.
        return b""

