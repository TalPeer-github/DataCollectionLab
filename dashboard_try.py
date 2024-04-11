import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Data Collection Lab - AI Requirments Analyzer",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

df_reshaped = pd.read_csv('data/final_EM.csv')
with st.sidebar:
    st.title('🏂 Data Collection Lab')

    year_list = list(df_reshaped.position.unique())[::-1]

    selected_year = st.selectbox('Select a position', year_list, index=len(year_list) - 1)
    position_data = df_reshaped[df_reshaped.year == selected_year]
    position_data_sorted = position_data.sort_values(by="population", ascending=False)

    education_counts = position_data['education'].iloc[0]
    sorted_education_counts = dict(sorted(education_counts.items(), key=lambda x: x[1], reverse=True))
    top_5_education = dict(list(sorted_education_counts.items())[:5])
    all_other_count = sum(sorted_education_counts.values()) - sum(top_5_education.values())
    combined_education_counts = {**top_5_education, 'All Other': all_other_count}
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo',
                        'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


    def make_donut(input_response, input_text, input_color):
        if input_color == 'blue':
            chart_color = ['#29b5e8', '#155F7A']
        if input_color == 'green':
            chart_color = ['#27AE60', '#12783D']
        if input_color == 'orange':
            chart_color = ['#F39C12', '#875A12']
        if input_color == 'red':
            chart_color = ['#E74C3C', '#781F16']

        source = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100 - input_response, input_response]
        })
        source_bg = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100, 0]
        })

        plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
            theta="% value",
            color=alt.Color("Topic:N",
                            scale=alt.Scale(
                                # domain=['A', 'B'],
                                domain=[input_text, ''],
                                # range=['#29b5e8', '#155F7A']),  # 31333F
                                range=chart_color),
                            legend=None),
        ).properties(width=130, height=130)

        text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700,
                              fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
        plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
            theta="% value",
            color=alt.Color("Topic:N",
                            scale=alt.Scale(
                                # domain=['A', 'B'],
                                domain=[input_text, ''],
                                range=chart_color),  # 31333F
                            legend=None),
        ).properties(width=130, height=130)
        return plot_bg + plot + text

def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import textwrap
from wordcloud import WordCloud, STOPWORDS
import re
from collections import Counter

st.set_page_config(
    page_title="Data Collection Lab - AI Requirements Analyzer",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

df_reshaped = pd.read_csv('data/final_EM.csv')


@st.cache
def plot_position_data2(df, position_title):
    def generate_summary_text(skills_counts, education_counts):
        if position_title == 'Data Scientist':
            return ds_text_start + ds_text_skills + ds_text_experience + ds_text_summary  # ds_text_start,ds_text_skills,ds_text_experience,ds_text_summary
        top_skills_text = "\n".join([
                                        f"- {skill}, with {(count / len(skills_counts.items())) * 100} % of the {position_title}s skills we've collected"
                                        for skill, count in skills_counts.items()][:5])
        top_education_text = "\n".join(
            [f"- {education}: {(count / len(education_counts.items())) * 100} % of the education mentions" for
             education, count in education_counts.items()][:5])

        summary_text = f"For the position of {position_title}, the top skills are:\n{top_skills_text}\n\n"
        summary_text += f"Also, the top education levels are:\n{top_education_text}"

        return summary_text

    def create_word_cloud(bag_of_words):
        custom_stopwords = set(STOPWORDS)
        custom_stopwords.update({"job", "title", "position", "at", "end", "of", "skills", "0", "1"})
        wordcloud = WordCloud(width=800, height=400, background_color='white',
                              stopwords={"job", "title", "position", "at", "end", "of", "skills", "0", "1"},
                              colormap='Blues', collocation_threshold=20).generate_from_frequencies(bag_of_words)
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(f"Bag of Words - {position_title} Required Skills")
        plt.axis('off')
        st.pyplot(plt)  # Display word cloud using st.pyplot()

    def create_bag_of_words(df):
        all_skills = ' '.join(df['skills'].values.astype(str))
        words = re.findall(r'\b[a-zA-Z]+\b', all_skills.lower())
        word_counts = Counter(words)
        return word_counts

    position_data = df[df['position'] == position_title]

    if 'education' in position_data.columns:
        education_counts = position_data['education'].iloc[0]
        sorted_education_counts = dict(sorted(education_counts.items(), key=lambda x: x[1], reverse=True))
        top_5_education = dict(list(sorted_education_counts.items())[:5])
        all_other_count = sum(sorted_education_counts.values()) - sum(top_5_education.values())
        combined_education_counts = {**top_5_education, 'All Other': all_other_count}

        # Create pie chart for educational levels
        st.title(f"Educational Levels for {position_title}")
        st.write(pd.Series(combined_education_counts).plot.pie(autopct='%1.1f%%'))

    if 'skills' in position_data.columns:
        skills_counts = position_data['skills'].iloc[0]
        total_skills = sum(skills_counts.values())
        skills_percentages = {skill: (count / total_skills) * 100 for skill, count in
                              position_data['skills'].iloc[0].items()}
        skills_df = pd.DataFrame(list(skills_percentages.items()), columns=['skill', 'p'])
        skills_df = skills_df.sort_values(by='p', ascending=True)

        num_skills_to_display = min(15, len(skills_df))
        skills_df = skills_df.iloc[-num_skills_to_display:]

        # Create horizontal bar chart for top skills
        st.title(f"Top Skills for {position_title}")
        st.bar_chart(skills_df.set_index('skill'))  # Display bar chart using st.bar_chart()

        summary_text = generate_summary_text(skills_counts, education_counts)
        max_text_width = 50
        wrapped_text = textwrap.fill(summary_text, width=max_text_width)

        # Display summary text
        st.title("Summary")
        st.write(wrapped_text)

    if 'years_of_experience' in position_data.columns:
        years_of_experience = position_data['years_of_experience']

        # Create histogram for years of experience
        st.title(f"Years of Experience for {position_title}")
        st.hist_chart(years_of_experience, bins=15)

        # Create boxplot for years of experience
        st.title(f"Years of Experience for {position_title}")
        st.box_chart(years_of_experience)


# Sidebar components
st.sidebar.title('🏂 Data Collection Lab')

positions_list = list(df_reshaped.position.unique())[::-1]
selected_position = st.sidebar.selectbox('Select a position', selected_year, index=len(positions_list) - 1)
position_data = df_reshaped[df_reshaped.year == selected_year]
selected_color_theme = st.sidebar.selectbox('Select a color theme',
                                            ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds',
                                             'rainbow', 'turbo', 'viridis'])
plot_position_data2(position_data, selected_position)