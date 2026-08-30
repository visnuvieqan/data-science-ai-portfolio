# Extracted from the original DataCamp/DataLab project workbook.
# Raw course-provided datasets are not redistributed in this public portfolio.

import pandas as pd
import matplotlib.pyplot as plt

netflix_df = pd.read_csv("netflix_data.csv")
movies_90s = netflix_df[
    (netflix_df['type'] == 'Movie')
    & (netflix_df['release_year'] >= 1990)
    & (netflix_df['release_year'] < 2000)
]

plt.hist(movies_90s['duration'])
plt.title('Distribution of Movie Durations in the 1990s')
plt.xlabel('Duration (minutes)')
plt.ylabel('Number of Movies')
plt.show()

duration = 90
short_movies_90s = movies_90s[
    (movies_90s['duration'] < 90) & (movies_90s['genre'] == 'Action')
]
short_movie_count = len(short_movies_90s)
print(duration)
print(short_movie_count)
