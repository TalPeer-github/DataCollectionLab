import datetime
import pandas as pd
from thefuzz import process
from thefuzz import fuzz
import ast


def read_df(file_name, dir_path='data/'):
    file_path = dir_path + file_name
    return pd.read_csv(file_path)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename({"Title": "title", "Alternate Title": "alternative_titles"}, axis=1)
    df['alternative_titles'] = df['alternative_titles'].apply(lambda x: ast.literal_eval(x))
    map_df = df.explode('alternative_titles').reset_index(drop=True)
    duplicated_alternatives = map_df[map_df.duplicated('alternative_titles', keep=False)]
    replacement_values = duplicated_alternatives['title'] + ' - ' + duplicated_alternatives['alternative_titles']
    map_df.loc[duplicated_alternatives.index, 'alternative_titles'] = replacement_values
    titles_df = map_df.drop_duplicates(subset=['alternative_titles'], keep='first')
    titles_df.to_csv("data/alternative_titles_map.csv", index=False)
    return titles_df


def get_match(title):
    matches = process.extractOne(title, choices, scorer=fuzz.token_set_ratio)
    if matches[1] < 90:
        return None
    return matches[0]


def save_chunk(i: int, n: int, df: pd.DataFrame):
    dir_path = 'data/chunks'
    file_path = f"{dir_path}/processed{n}_{i}"
    df.to_csv(file_path, index=False)


if __name__ == "__main__":
    """
    :param need_process: Don't change it 
    :param to_csv: For saving the results in 'data/chunks/'
    :param n: Number of records in 1 chunk
    :param num_chunks: Number of chunks you want to create
    :param last_chunk: Last processed chunk (check in data/chunks dir)
    """
    dir_path = 'data/'
    need_process = False
    to_csv = True
    n = 5000
    num_chunks = 3
    last_chunk = 0
    start_chunk = last_chunk + 1

    if need_process:
        titles_benchmark = read_df(file_name='alternate_titles.csv')
        titles_df = preprocess(titles_benchmark)
    else:
        titles_df = read_df(file_name='alternative_titles_map.csv', dir_path=dir_path)

    raw_titles_df = read_df(file_name='job_postings.csv', dir_path=dir_path)

    choices = titles_df.alternative_titles.values.tolist()
    choices_map = titles_df[['alternative_titles', 'title']].set_index('alternative_titles')

    for i in range(start_chunk, start_chunk + num_chunks):
        print("===================================")
        print(f"Starting chunk {i}...")
        start_time = datetime.datetime.now()
        titles_sample = raw_titles_df.iloc[n * i: n * (i + 1), :].copy()

        titles_sample['match_title'] = titles_sample['job_title'].apply(lambda x: get_match(x))
        titles_sample = titles_sample[['job_title', 'match_title']].dropna(subset='match_title')
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        print(f"Processed chunk {i} ({n} records) in {round(elapsed_time / 60, 2)} minutes")
        if to_csv:
            save_chunk(i, n, titles_sample)
