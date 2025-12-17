### Корреляционный анализ данных "100 лучших фильмов 21 века"

Выбрать из каталога любой интересующий dataset и провести его анализ в вольном стиле

**Датасет:** https://www.kaggle.com/datasets/betlbaak/best-100-movies

```bash
curl -L -o best-100-movies.zip "https://www.kaggle.com/api/v1/datasets/download/betlbaak/best-100-movies"
```

Датасет представляет собой коллекцию 100 лучших фильмов 21 века с полными метаданными для анализа и исследования.  
(100 must-watch films with full metadata for analysis and exploration)

Этот набор данных содержит подробную информацию о 100 самых знаковых, получивших признание критиков и оказавших значительное культурное влияние фильмах, отобранных газетой New York Times.

## Запуск анализа

### Jupyter Notebook
```bash
jupyter notebook hw12_best_100_movies.ipynb
```
Интерактивный анализ с визуализациями в notebook.  
Датасет скачивается автоматически с Kaggle через `kagglehub`.

### Python скрипт
```bash
python best_100_movies_pandas.py
```
Создаст интерактивный dashboard: `interactive_dashboard.html`

## Результаты работы

Интерактивный dashboard включает:

1. **Bar chart**: Распределение фильмов по жанрам (топ-15)  
   - Градиент цвета по частоте
   - Интерактивные подсказки

2. **Bar chart**: Топ-10 режиссёров и актёров  
   - Частота появления в топ-100
   - Интерактивные подсказки

3. **Word Cloud**: Облако слов из названий фильмов  
   - Визуализация частоты слов в названиях

## Ключевые выводы

- **Жанры**: Драма — доминирующий жанр (40 фильмов), за ней Comedy (24) и Thriller (23)
- **Режиссёры**: Christopher Nolan лидирует с 5 фильмами, Paul Thomas Anderson и Alfonso Cuarón — по 4
- **Актёры**: Brad Pitt — 6 фильмов, Michael Caine и Leonardo DiCaprio — по 4

## Технологии

- **Pandas** — обработка и анализ данных
- **Plotly** — интерактивные визуализации
- **WordCloud** — облако слов
- **Matplotlib** — дополнительные визуализации
- **kagglehub** — автоматическое скачивание датасета

---

**Интерактивный dashboard:** [interactive_dashboard.html](interactive_dashboard.html)  
**Jupyter Notebook:** [hw12_best_100_movies.ipynb](hw12_best_100_movies.ipynb)
