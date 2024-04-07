import pandas as pd
import thefuzz
from thefuzz import process, fuzz, utils

narrowed_titles_count = {}


def define_choices(narrow=False):
    """
    :param narrow: choices from narrowed titles' list(~200 position titles) or regular list (54K position titles)
    :return: choices list
    """
    file_path = "data/narrowed_alternative_titles.csv" if narrow else "data/alternate_titles.csv"
    choices = pd.read_csv(file_path)
    return choices


def find_narrowed_match(title: str):
    """
    Convert previous experience titles to one title from the title_choices list
    :param title: title to convert
    :return: best match from title_choices list if match accuracy >= 90%, else return None
    """
    pass


def get_relevant_experience(experience: list, record: pd.DataFrame, choices_map: pd.DataFrame):
    """
    Convert previous experience title to one of the 54K titles in the choices list (alternative_titles dataFrame)
    relevant records : title who didn't receive Null values in find_match_title()
    :param choices_map:
    :param record:
    :param experience: titles of previous experience for records who didn't receive Null values in find_match_title()
    :return: experience list after removing unrelated experience from it
    """
    experience = record['title']
    current_title = record['position']
    for i, prev_exp in enumerate(experience):
        match = get_match(prev_exp)
        if choices_map.loc[match, 'title'] == choices_map.loc[current_title, 'title']:  # TODO - check with Yoav
            choices_map[match, 'count'] += 1
            choices_map[current_title, 'count'] += 1
            if current_title not in narrowed_titles_count.keys():
                narrowed_titles_count[current_title] = 1
            else:
                narrowed_titles_count[current_title] += 1


def get_match(title, choices: list):
    matches = process.extractOne(title, choices, scorer=fuzz.token_set_ratio,
                                 processor=thefuzz.process.default_processor)

    if matches[1] < 90:
        return None
    else:

        return matches[0]


def start_flow(df: pd.DataFrame):
    """

    :return:
    """
    narrowed_choices = define_choices(narrow=True)
    choices = define_choices(narrow=False)
    df['narrow_match'] = df['position'].apply(lambda x: get_match(x)).dropna()
