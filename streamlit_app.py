import streamlit as st
import pandas as pd
import altair as alt
import ast 
st.set_page_config(
    page_title="Data Collection Lab - AI Requirments Analyzer",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


df_reshaped = pd.read_csv('data/final_EM.csv')
df_reshaped['education'] =df_reshaped['education'].apply(ast.literal_eval)
df_reshaped['skills'] =df_reshaped['skills'].apply(ast.literal_eval)
df_reshaped['years_of_experience'] =df_reshaped['years_of_experience'].apply(ast.literal_eval)

positions_list = list(df_reshaped['position'].unique())[::-1]

st.title('Position Selection')
st.write('Please select a position from the list below:')
selected_position = st.selectbox('Select Position', positions_list)

st.write(f'You selected: {selected_position}')

def plot_education(position_title):
    position_data = df_reshaped[df_reshaped['position'] == position_title]
    education_counts = position_data['education'].iloc[0]
    sorted_education_counts = dict(sorted(education_counts.items(), key=lambda x: x[1], reverse=True))
    top_5_education = dict(list(sorted_education_counts.items())[:5])
    all_other_count = sum(sorted_education_counts.values()) - sum(top_5_education.values())
    combined_education_counts = {**top_5_education, 'All Other': all_other_count}

    # Plot pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(combined_education_counts.values(), labels=combined_education_counts.keys(), autopct='%1.1f%%',
           startangle=140)
    ax.set_title(f"Educational Levels for {position_title}")
    ax.axis('equal')
    st.pyplot(fig)

def plot_skills(position_title):
    position_data = df_reshaped[df_reshaped['position'] == position_title]
    skills_counts = position_data['skills'].iloc[0]
    total_skills = sum(skills_counts.values())
    skills_percentages = {skill: (count / total_skills) * 100 for skill, count in
                          position_data['skills'].iloc[0].items()}
    skills_df = pd.DataFrame(list(skills_percentages.items()), columns=['skill', 'p'])
    skills_df = skills_df.sort_values(by='p', ascending=True)

    num_skills_to_display = min(15, len(skills_df))
    skills_df = skills_df.iloc[-num_skills_to_display:]

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))

    axes[0].barh(skills_df['skill'], skills_df['p'], color='#A3816A', edgecolor='#0A065D', alpha=0.8)
    axes[0].set_xlabel('Percentage (%)')
    axes[0].set_ylabel('Skill')
    axes[0].set_title(f'Top Skills for {position_title} (%)')

    education_counts = position_data['education'].iloc[0]
    summary_text = generate_summary_text(skills_counts, education_counts)
    max_text_width = 50
    wrapped_text = textwrap.fill(summary_text, width=max_text_width)
    axes[1].axis('off')
    axes[1].text(0.5, 0.5, wrapped_text, fontsize=12, ha='center', va='center', fontfamily='Arial',
                 fontweight='bold', wrap=True)

    st.pyplot(fig)

def plot_experience(position_title):
    position_data = df_reshaped[df_reshaped['position'] == position_title]
    years_of_experience = position_data['years_of_experience']

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))

    axes[0].hist(years_of_experience, bins=15, color='#A3816A', edgecolor='#0A065D')
    axes[0].set_title(f"Years of Experience for {position_title}")
    axes[0].set_xlabel("Years of Experience")
    axes[0].set_ylabel("Frequency")

    axes[1].boxplot(years_of_experience, vert=False)
    axes[1].set_title(f"Years of Experience for {position_title}")
    axes[1].set_xlabel("Years of Experience")

    plt.tight_layout()
    st.pyplot(fig)


plot_education(selected_position)
plot_skills(selected_position)
plot_experience(selected_position)