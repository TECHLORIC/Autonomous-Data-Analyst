import json
import os
from pathlib import Path
import pandas as pd

def build_dashboard_html(df: pd.DataFrame, title: str = "Autonomous Data Analyst Dashboard") -> str:
    """Generate a self-contained, interactive HTML dashboard using Plotly.js."""
    cols = [c.lower() for c in df.columns]
    col_map = {c.lower(): c for c in df.columns}

    # Sales / metric column
    sales_col = None
    for candidate in ["sales_amount", "sales", "revenue", "amount", "total"]:
        if candidate in col_map:
            sales_col = col_map[candidate]
            break
    if not sales_col:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        sales_col = numeric_cols[0] if numeric_cols else None

    # Date / time column
    date_col = None
    for candidate in ["date", "timestamp", "time", "order_date", "day"]:
        if candidate in col_map:
            date_col = col_map[candidate]
            break

    # Grouping column (region, category, etc.)
    group_col = None
    for candidate in ["region", "category", "segment", "department", "type"]:
        if candidate in col_map:
            group_col = col_map[candidate]
            break

    # Secondary category
    category_col = None
    for candidate in ["category", "customer_segment", "segment", "product"]:
        if candidate in col_map and col_map[candidate] != group_col:
            category_col = col_map[candidate]
            break

    # Calculate KPIs
    kpi_cards = []
    if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        total_val = df[sales_col].sum()
        kpi_cards.append({
            "label": f"Total {sales_col.replace('_', ' ').title()}",
            "value": f"${total_val:,.2f}" if "sale" in sales_col.lower() or "rev" in sales_col.lower() else f"{total_val:,.0f}"
        })
        avg_val = df[sales_col].mean()
        kpi_cards.append({
            "label": f"Avg {sales_col.replace('_', ' ').title()}",
            "value": f"${avg_val:,.2f}" if "sale" in sales_col.lower() or "rev" in sales_col.lower() else f"{avg_val:,.2f}"
        })

    units_col = col_map.get("units_sold")
    if units_col and pd.api.types.is_numeric_dtype(df[units_col]):
        kpi_cards.append({
            "label": "Total Units Sold",
            "value": f"{df[units_col].sum():,}"
        })

    score_col = col_map.get("satisfaction_score")
    if score_col and pd.api.types.is_numeric_dtype(df[score_col]):
        kpi_cards.append({
            "label": "Avg Satisfaction",
            "value": f"{df[score_col].mean():.2f} / 5.0"
        })

    kpi_cards.append({
        "label": "Total Records",
        "value": f"{len(df):,}"
    })

    # Prepare primary chart data (Time-series / Multi-series line)
    primary_traces = []
    if date_col and sales_col:
        df_sorted = df.sort_values(by=date_col)
        if group_col:
            for group_val, grp in df_sorted.groupby(group_col):
                primary_traces.append({
                    "x": grp[date_col].astype(str).tolist(),
                    "y": grp[sales_col].tolist(),
                    "name": str(group_val),
                    "type": "scatter",
                    "mode": "lines+markers",
                    "line": {"shape": "spline"}
                })
        else:
            primary_traces.append({
                "x": df_sorted[date_col].astype(str).tolist(),
                "y": df_sorted[sales_col].tolist(),
                "name": sales_col,
                "type": "scatter",
                "mode": "lines+markers"
            })
    elif sales_col:
        first_col = df.columns[0]
        primary_traces.append({
            "x": df[first_col].astype(str).tolist(),
            "y": df[sales_col].tolist(),
            "type": "bar",
            "name": sales_col
        })

    # Prepare secondary chart data (Breakdown by Category or Region)
    secondary_traces = []
    sec_col = category_col or group_col
    if sec_col and sales_col:
        breakdown = df.groupby(sec_col)[sales_col].sum().reset_index()
        secondary_traces.append({
            "labels": breakdown[sec_col].astype(str).tolist(),
            "values": breakdown[sales_col].tolist(),
            "type": "pie",
            "hole": 0.4,
            "textinfo": "label+percent"
        })

    # Table preview
    preview_df = df.head(15)
    headers_html = "".join([f"<th class='px-4 py-2 border-b border-gray-700 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider'>{col}</th>" for col in preview_df.columns])
    rows_html = ""
    for _, row in preview_df.iterrows():
        row_tds = "".join([f"<td class='px-4 py-2 border-b border-gray-800 text-sm text-gray-300'>{row[col]}</td>" for col in preview_df.columns])
        rows_html += f"<tr class='hover:bg-gray-800 transition'>{row_tds}</tr>"

    kpi_cards_html = ""
    for card in kpi_cards:
        kpi_cards_html += f"""
        <div class="bg-gray-800/80 border border-gray-700/60 rounded-xl p-5 shadow-lg backdrop-blur">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider">{card['label']}</p>
            <p class="text-2xl font-bold text-white mt-1">{card['value']}</p>
        </div>
        """

    primary_traces_json = json.dumps(primary_traces)
    secondary_traces_json = json.dumps(secondary_traces)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {{ background-color: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }}
    </style>
</head>
<body class="min-h-screen p-6 md:p-8">
    <div class="max-w-7xl mx-auto space-y-6">
        <!-- Header -->
        <header class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-gray-800 gap-4">
            <div>
                <div class="flex items-center gap-3">
                    <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Live Dashboard</span>
                    <h1 class="text-2xl font-bold tracking-tight text-white">{title}</h1>
                </div>
                <p class="text-sm text-gray-400 mt-1">Autonomous analysis & interactive data visualization</p>
            </div>
            <div class="flex items-center gap-3">
                <button onclick="window.location.reload()" class="px-3.5 py-1.5 text-xs font-medium bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg border border-gray-700 transition">Refresh</button>
            </div>
        </header>

        <!-- KPI Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {kpi_cards_html}
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2 bg-gray-800/80 border border-gray-700/60 rounded-xl p-5 shadow-lg">
                <h2 class="text-base font-semibold text-white mb-2">Trend Analysis: {sales_col or 'Data'}</h2>
                <div id="primary-chart" style="height: 380px;"></div>
            </div>
            <div class="bg-gray-800/80 border border-gray-700/60 rounded-xl p-5 shadow-lg">
                <h2 class="text-base font-semibold text-white mb-2">Distribution Breakdown</h2>
                <div id="secondary-chart" style="height: 380px;"></div>
            </div>
        </div>

        <!-- Data Preview Table -->
        <div class="bg-gray-800/80 border border-gray-700/60 rounded-xl p-5 shadow-lg">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-base font-semibold text-white">Dataset Preview (First 15 Rows)</h2>
                <span class="text-xs text-gray-400">Total {len(df)} records</span>
            </div>
            <div class="overflow-x-auto rounded-lg border border-gray-700/80">
                <table class="min-w-full divide-y divide-gray-700 text-left">
                    <thead class="bg-gray-900/80">
                        <tr>{headers_html}</tr>
                    </thead>
                    <tbody class="divide-y divide-gray-800">
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const darkLayout = {{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {{ color: '#94a3b8' }},
            margin: {{ t: 30, r: 20, l: 50, b: 50 }},
            xaxis: {{ gridcolor: '#334155', zerolinecolor: '#475569' }},
            yaxis: {{ gridcolor: '#334155', zerolinecolor: '#475569' }},
            legend: {{ orientation: 'h', y: 1.15 }}
        }};

        const primaryTraces = {primary_traces_json};
        Plotly.newPlot('primary-chart', primaryTraces, darkLayout, {{ responsive: true }});

        const secondaryTraces = {secondary_traces_json};
        if (secondaryTraces.length > 0) {{
            const pieLayout = {{ ...darkLayout, showlegend: true, margin: {{ t: 30, r: 20, l: 20, b: 20 }} }};
            Plotly.newPlot('secondary-chart', secondaryTraces, pieLayout, {{ responsive: true }});
        }} else {{
            document.getElementById('secondary-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-500">No secondary categorical dimension</div>';
        }}
    </script>
</body>
</html>
"""
    return html_template

def build_dashboard(df: pd.DataFrame, port: int = 8050):
    return build_dashboard_html(df)
