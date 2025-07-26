import os
from flask import send_file
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
from prophet import Prophet
from github_live_fetch import get_github_trending_languages  
from datetime import datetime

app = Flask(__name__)

# Full language list (30+ modern languages)
ALL_LANGUAGES = [
    "python", "javascript", "java", "c", "c++", "c#", "go", "typescript", "ruby", "php",
    "swift", "kotlin", "rust", "dart", "scala", "perl", "lua", "haskell", "elixir", "clojure",
    "shell", "powershell", "r", "matlab", "julia", "groovy", "objective-c", "visual-basic", "assembly", "f#"
]

def forecast_language(data, lang):
    try:
        df = data[['Year', lang]].dropna()
        df = df.rename(columns={'Year': 'ds', lang: 'y'})
        df['ds'] = pd.to_datetime(df['ds'], format='%Y')
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=12, freq='YE')
        forecast = model.predict(future)
        forecast['Year'] = forecast['ds'].dt.year
        return forecast[['Year', 'yhat']].groupby('Year').mean().reset_index()
    except Exception as e:
        return pd.DataFrame(columns=['Year', 'yhat'])


@app.route('/', methods=['GET', 'POST'])
def index():
    data = pd.read_csv('language_trends.csv')
    available_langs = [col for col in data.columns if col != "Year"]

    selected_langs = request.form.getlist('languages')
    if not selected_langs:
        selected_langs = ["Python", "Java", "JavaScript", "C"]

    df_melted = data[['Year'] + selected_langs].melt(id_vars='Year',
        var_name='Language', value_name='Popularity')

    fig = px.line(df_melted, x='Year', y='Popularity', color='Language',
        title="📊 Programming Language Popularity (2004–2022)", markers=True)
    trend_graph = pio.to_html(fig, full_html=False)

    future_values = {}
    for lang in available_langs:
        forecast_df = forecast_language(data, lang)
        row = forecast_df[forecast_df['Year'] == 2025]
        if not row.empty:
            future_values[lang] = round(row.iloc[0]['yhat'], 2)

    top10_df = pd.DataFrame(list(future_values.items()),
        columns=["Language", "Popularity"]).sort_values(by='Popularity', ascending=False).head(10)

    top10_fig = px.bar(top10_df, x='Language', y='Popularity',
        title="🚀 Top 10 Programming Languages in 2025 (Predicted)", text_auto=True)
    top10_graph = pio.to_html(top10_fig, full_html=False)

    return render_template("index.html",
        languages=available_langs,
        selected_langs=selected_langs,
        plot=trend_graph,
        top10=top10_graph)

@app.route('/analytics')
def analytics():
    data = pd.read_csv('language_trends.csv')
    corr = data.drop(columns=['Year']).corr()
    heatmap_fig = px.imshow(corr, title="🔍 Correlation Between Language Trends")
    heatmap_graph = pio.to_html(heatmap_fig, full_html=False)

    latest_year = data['Year'].max()
    latest_data = data[data['Year'] == latest_year].melt(id_vars='Year',
        var_name='Language', value_name='Popularity')
    pie_fig = px.pie(latest_data, names='Language', values='Popularity',
        title=f"📌 Popularity Distribution in {latest_year}")
    pie_graph = pio.to_html(pie_fig, full_html=False)

    return render_template("analytics.html",
        heatmap=heatmap_graph,
        pie=pie_graph)

@app.route('/github-live')
def github_live():
    from github_live_fetch import get_github_trending_languages
    data = get_github_trending_languages()
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("github_live.html", data=data, updated_at=updated_at)

@app.route('/download-github-csv')
def download_github_csv():
    csv_path = "github_live_trending.csv"
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True)
    else:
        return "❌ File not found. Please fetch GitHub data first.", 404



if __name__ == '__main__':
    app.run(debug=True)
