import os
import zipfile
import base64
from io import BytesIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats


def extract_dataset(zip_path='best-100-movies.zip', extract_to='.'):
    """Автоматическая распаковка датасета из ZIP архива"""
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Архив {zip_path} не найден!")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.txt') or f.endswith('.csv')]
        if csv_files:
            print(f"Датасет распакован: {csv_files[0]}")
            return os.path.join(extract_to, csv_files[0])
    return None


def load_and_clean_dataset(file_path):
    """Загрузка и очистка датасета"""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден. Попытка распаковки архива...")
        file_path = extract_dataset()

    df = pd.read_csv(file_path)
    print(f"Записей найдено: {len(df)}")

    # Очистка данных
    df_cleaned = df.copy()

    # Преобразование числовых колонок
    numeric_cols = ['Rating', 'ReleaseYear', 'Duration(min)', 'Budget(millionUSD)',
                    'BoxOffice(millionUSD)', 'NumAwards', 'Oscar']
    for col in numeric_cols:
        if col in df_cleaned.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')

    print(f"Записей после очистки: {len(df_cleaned)}")
    return df_cleaned


def parse_genres(df):
    """Парсинг жанров из строки в список"""
    genres_list = []
    for genres_str in df['Genre'].dropna():
        genres = [g.strip() for g in str(genres_str).split(',')]
        genres_list.extend(genres)
    return Counter(genres_list)


def parse_names(df, column):
    """Парсинг имён (режиссёров/актёров) из строки"""
    names_list = []
    for names_str in df[column].dropna():
        # Для режиссёров: может быть несколько, разделены запятыми
        # Для актёров: всегда несколько, разделены запятыми
        names = [n.strip() for n in str(names_str).split(',')]
        names_list.extend(names)
    return Counter(names_list)


def create_genre_distribution(df):
    """Интерактивный bar chart распределения жанров"""
    genres_count = parse_genres(df)
    genres_df = pd.DataFrame(genres_count.most_common(15), columns=['Genre', 'Count'])

    # Используем go.Bar для явного контроля данных
    fig = go.Figure(data=[
        go.Bar(
            x=genres_df['Genre'].tolist(),
            y=genres_df['Count'].tolist(),
            marker_color=genres_df['Count'].tolist(),
            marker_colorscale='Viridis',
            hovertemplate='%{x}: %{y} фильмов<extra></extra>'
        )
    ])

    fig.update_layout(
        title='Распределение фильмов по жанрам (топ-15)',
        xaxis_title='Жанр',
        yaxis_title='Количество фильмов',
        height=500,
        xaxis_tickangle=-45
    )
    return fig


def create_runtime_boxplot(df):
    """Интерактивный box plot продолжительности по жанрам"""
    # Разбиваем жанры для анализа
    genre_runtime_data = []
    for idx, row in df.iterrows():
        if pd.notna(row['Genre']) and pd.notna(row['Duration(min)']):
            genres = [g.strip() for g in str(row['Genre']).split(',')]
            for genre in genres:
                genre_runtime_data.append({
                    'Genre': genre,
                    'Duration': row['Duration(min)'],
                    'Title': row['Title']
                })

    genre_runtime_df = pd.DataFrame(genre_runtime_data)

    # Оставляем только популярные жанры (топ-10)
    top_genres = genre_runtime_df['Genre'].value_counts().head(10).index
    genre_runtime_df = genre_runtime_df[genre_runtime_df['Genre'].isin(top_genres)]

    fig = px.box(
        genre_runtime_df,
        x='Genre',
        y='Duration',
        title='Распределение продолжительности фильмов по жанрам',
        labels={'Genre': 'Жанр', 'Duration': 'Продолжительность (мин)'},
        color='Genre',
        hover_data=['Title']
    )

    fig.update_layout(height=500, xaxis_tickangle=-45, showlegend=False)
    return fig


def create_directors_actors_chart(df):
    """Интерактивный bar chart топ режиссёров и актёров"""
    # Для режиссёров используем value_counts напрямую (может быть несколько через запятую)
    directors_list = []
    for director_str in df['Director'].dropna():
        # Режиссёры могут быть разделены запятыми, например "Ethan Coen, Joel Coen"
        directors = [d.strip() for d in str(director_str).split(',')]
        directors_list.extend(directors)
    directors_count = Counter(directors_list)

    # Для актёров разбиваем по запятым
    actors_list = []
    for actors_str in df['Starring'].dropna():
        actors = [a.strip() for a in str(actors_str).split(',')]
        actors_list.extend(actors)
    actors_count = Counter(actors_list)

    top_directors = pd.DataFrame(directors_count.most_common(10), columns=['Name', 'Count'])
    top_actors = pd.DataFrame(actors_count.most_common(10), columns=['Name', 'Count'])
    
    # Переворачиваем порядок, чтобы топ был вверху графика
    top_directors = top_directors.iloc[::-1].reset_index(drop=True)
    top_actors = top_actors.iloc[::-1].reset_index(drop=True)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Топ-10 режиссёров', 'Топ-10 актёров')
    )

    fig.add_trace(
        go.Bar(x=top_directors['Count'].tolist(), y=top_directors['Name'].tolist(), orientation='h',
               name='Режиссёры', marker_color='indianred',
               hovertemplate='%{y}: %{x} фильмов<extra></extra>'),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=top_actors['Count'].tolist(), y=top_actors['Name'].tolist(), orientation='h',
               name='Актёры', marker_color='lightsalmon',
               hovertemplate='%{y}: %{x} фильмов<extra></extra>'),
        row=1, col=2
    )
    fig.update_layout(height=500, title_text="Топ режиссёры и актёры в лучших фильмах")
    return fig


def create_wordcloud_static(df):
    """Статичное облако слов из названий фильмов"""
    titles_text = ' '.join(df['Title'].dropna().astype(str))

    stop_words = set(STOPWORDS)
    stop_words.update(['the', 'a', 'an', 'and', 'or', 'of', 'in', 'to'])

    wordcloud = WordCloud(
        background_color="white",
        width=1600, height=800,
        max_words=100,
        stopwords=stop_words,
        colormap='viridis'
    ).generate(titles_text)

    # Сохраняем в base64 для встраивания в HTML
    img_buffer = BytesIO()
    plt.figure(figsize=(16, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode()

    return img_base64


def create_interactive_dashboard(df, output_file='interactive_dashboard.html'):
    """Создание единого HTML dashboard с всеми интерактивными графиками"""
    print("\nСоздание интерактивного dashboard...")

    # Создаём нужные графики
    fig3 = create_genre_distribution(df)
    fig5 = create_directors_actors_chart(df)
    wordcloud_img = create_wordcloud_static(df)

    # Создаём HTML с встроенными графиками
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Анализ 100 лучших фильмов 21 века</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                text-align: center;
                color: #333;
            }}
            h2 {{
                color: #555;
                margin-top: 40px;
            }}
            .chart-container {{
                background-color: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .description {{
                color: #666;
                margin: 10px 0;
                line-height: 1.6;
            }}
            .wordcloud {{
                text-align: center;
                margin: 20px 0;
            }}
            .wordcloud img {{
                max-width: 100%;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>🎬 Корреляционный анализ 100 лучших фильмов 21 века</h1>
        
        <div class="chart-container">
            <h2>1. Распределение фильмов по жанрам</h2>
            <p class="description">
                Топ-15 жанров среди 100 лучших фильмов. Многие фильмы относятся к нескольким жанрам одновременно.
            </p>
            <div id="chart3"></div>
        </div>
        
        <div class="chart-container">
            <h2>2. Топ режиссёры и актёры</h2>
            <p class="description">
                Режиссёры и актёры, чьи работы чаще всего попадают в список 100 лучших фильмов 21 века.
            </p>
            <div id="chart5"></div>
        </div>
        
        <div class="chart-container">
            <h2>3. Облако слов из названий фильмов</h2>
            <p class="description">
                Визуализация наиболее часто встречающихся слов в названиях лучших фильмов 21 века.
            </p>
            <div class="wordcloud">
                <img src="data:image/png;base64,{wordcloud_img}" alt="Word Cloud">
            </div>
        </div>
        
        <script>
            var chart3 = {fig3.to_json()};
            var chart5 = {fig5.to_json()};
            
            Plotly.newPlot('chart3', chart3.data, chart3.layout);
            Plotly.newPlot('chart5', chart5.data, chart5.layout);
        </script>
    </body>
    </html>
    """

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Dashboard сохранён в файл: {output_file}")
    return output_file


def print_correlation_analysis(df):
    """Вывод статистического анализа корреляций"""
    print("\n" + "="*80)
    print("АНАЛИЗ ДАТАСЕТА '100 ЛУЧШИХ ФИЛЬМОВ 21 ВЕКА'")
    print("="*80)

    # Основная статистика
    print(f"\nВсего фильмов: {len(df)}")
    print(f"Период: {df['ReleaseYear'].min():.0f} - {df['ReleaseYear'].max():.0f}")
    print(f"Средний рейтинг: {df['Rating'].mean():.2f} (σ = {df['Rating'].std():.2f})")
    print(f"Средняя продолжительность: {df['Duration(min)'].mean():.1f} минут")

    # Топ жанры
    print("\n--- Топ-5 жанров ---")
    genres_count = parse_genres(df)
    for genre, count in genres_count.most_common(5):
        print(f"{genre}: {count} фильмов")

    # Топ режиссёры
    print("\n--- Топ-5 режиссёров ---")
    directors_count = parse_names(df, 'Director')
    for director, count in directors_count.most_common(5):
        print(f"{director}: {count} фильмов")

    print("\n" + "="*80)


if __name__ == "__main__":
    print("🎬 Начало анализа датасета '100 лучших фильмов 21 века'")

    # Загрузка данных
    df = load_and_clean_dataset('best_100_movies.txt')

    # Вывод корреляционного анализа в консоль
    print_correlation_analysis(df)

    # Создание интерактивного dashboard
    dashboard_file = create_interactive_dashboard(df)

    print(f"\n✅ Анализ завершён! Откройте файл {dashboard_file} в браузере для просмотра интерактивных графиков.")

