import datetime
import glob
import re

import numpy as np
import pandas as pd
import thefuzz.utils
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
    matches = process.extractOne(title, choices, scorer=fuzz.token_set_ratio,
                                 processor=thefuzz.process.default_processor)
    if matches[1] < 90:
        return None
    return matches[0]


def merged_value_counts():
    dfs = []
    csv_files = glob.glob('data/job_links/*.csv')
    for chunk_id, file_name in enumerate(csv_files):
        df = pd.read_csv(file_name)
        df['chunk'] = [chunk_id] * df.shape[0]
        dfs.append(pd.read_csv(file_name))
    merged_df = pd.concat(dfs, axis=0)


def save_chunk(chunk_id: int,sample_size: int, df: pd.DataFrame, file_path: str):
    file_path = f"{file_path}/sample{sample_size}_{chunk_id}.csv"
    df.to_csv(file_path, index=False)


def create_chunks(start_chunk: int, n: 5000, num_chunks=3, to_csv=True, save_to_path="data/chunks"):
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
            save_chunk(i, n, titles_sample, save_to_path)


if __name__ == "__main__":
    """
    :param need_process: Don't change it 
    :param to_csv: For saving the results in 'data/chunks/'
    :param n: Number of records in 1 chunk
    :param num_chunks: Number of chunks you want to create
    :param last_chunk: Last processed chunk (check in data/chunks dir)
    """


    def process_profiles(to_csv=True):
        csv_files = glob.glob('data/profiles/*.csv')
        save_to_path = 'data/profiles/processed'
        for i, f in enumerate(csv_files):
            print("===================================")
            print(f"Starting chunk {i}...")
            df = pd.read_csv(f)
            clean_df = df[df.position.str.contains(r'[a-zA-Z]', na=False)].reset_index().rename(
                {'index': "position_idx"}, axis=1).drop_duplicates(subset=['position'], keep='first')
            n = clean_df.shape[0]
            print(f"DataFrame (no duplicates): {n} items")
            start_time = datetime.datetime.now()
            try:
                clean_df['match_title'] = clean_df['position'].apply(lambda x: get_match(x))
                titles_sample = clean_df[['position_idx', 'position', 'match_title']].dropna(subset='match_title')
            except Exception as e:
                print(f"An error occurred: {e}")
                continue
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            print(f"Processed chunk {i} ({n} records) in {round(elapsed_time / 60, 2)} minutes")
            if to_csv:
                save_chunk(chunk_id=i, sample_size=n, df=titles_sample, file_path=save_to_path)


    def process_moti(start_chunk: int, n: 5000, num_chunks=3, to_csv=True, save_to_path="data/job_links/processed"):
        finish_flag = False
        for i in range(start_chunk, start_chunk + num_chunks):
            print("===================================")
            print(f"Starting chunk {i}...")
            start_time = datetime.datetime.now()
            limit = n * (i + 2)
            if not limit <= raw_titles_df.shape[0] - 1:
                limit = raw_titles_df.shape[0] - 1
                finish_flag = True
            n = min(n, limit - n * i)
            titles_sample = raw_titles_df.iloc[n * i: limit, :].sample(n)

            titles_sample['match_title'] = titles_sample['job_title'].apply(lambda x: get_match(x))
            titles_sample = titles_sample[['job_title', 'match_title']].dropna(subset='match_title')
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            print(f"Processed chunk {i} ({n} records) in {round(elapsed_time / 60, 2)} minutes")
            if to_csv:
                save_chunk(chunk_id=i, sample_size = n, df=titles_sample, file_path=save_to_path)
            if finish_flag:
                break


    dir_path = 'data/'
    need_process = False
    to_csv = True
    n = 5000
    num_chunks = 2
    last_chunk = 3
    start_chunk = last_chunk + 1

    if need_process:
        titles_benchmark = read_df(file_name='alternate_titles.csv')
        titles_df = preprocess(titles_benchmark)
    else:
        titles_df = read_df(file_name='alternative_titles_map.csv', dir_path=dir_path)

    raw_titles_df = read_df(file_name='job_postings.csv', dir_path=dir_path).drop_duplicates(subset=['job_title'],
                                                                                             keep='first').iloc[30000:,
                    :].sample(4000)
    choices = titles_df.alternative_titles.values.tolist()
    choices_map = titles_df[['alternative_titles', 'title']].set_index('alternative_titles')
    process_moti(start_chunk=0, n=5000, num_chunks=50, to_csv=True)
    process_profiles()

