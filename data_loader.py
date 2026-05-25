import pandas as pd
from pathlib import Path
import streamlit as st


@st.cache_data
def load_data():

    BASE_DIR = Path(__file__).resolve().parent
    input_file = BASE_DIR / "Players" / "all_divisions.xlsx"

    df = pd.read_excel(input_file)

    # PASTE EVERYTHING FROM INSIDE YOUR FUNCTION HERE

    def assign_role(position):
        if pd.isna(position):
            return 'Unknown'
        if 'G' in position:
            return 'Goalkeeper'
        elif 'B' in position:
            return 'Defender'
        elif 'M' in position or 'W' in position:
            return 'Midfielder'
        elif 'F' in position:
            return 'Forward'
        else:
            return 'Unknown'

    df['Role'] = df['Position'].apply(assign_role)

    df = df.drop(columns=[
        'Team',
        'Market value',
        'Passport country',
        'Weight',
        'Foot',
        'On loan',
        'Contract expires'
    ])

    df = df.rename(columns={'Team within selected timeframe': 'Team'})

    defender_cols = [
        'Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played',
        'Goals', 'xG', 'Assists', 'xA',
        'Duels per 90', 'Duels won, %',
        'Defensive duels per 90', 'Defensive duels won, %',
        'Aerial duels per 90', 'Aerial duels won, %',
        'Sliding tackles per 90', 'PAdj Sliding tackles',
        'Shots blocked per 90', 'Interceptions per 90', 'PAdj Interceptions',
        'Fouls per 90', 'Yellow cards per 90', 'Red cards per 90',
        'Passes per 90', 'Accurate passes, %',
        'Long passes per 90', 'Accurate long passes, %',
        'Progressive passes per 90', 'Accurate progressive passes, %',
        'Passes to final third per 90', 'Accurate passes to final third, %',
        'Average pass length, m', 'Role', 'Division', 'Due For Release'
    ]

    midfielder_cols = [
        'Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played',
        'Goals', 'xG', 'Assists', 'xA',
        'Duels per 90', 'Duels won, %',
        'Defensive duels per 90', 'Defensive duels won, %',
        'Interceptions per 90', 'PAdj Interceptions',
        'Fouls per 90', 'Yellow cards per 90', 'Red cards per 90',
        'Goals per 90', 'xG per 90', 'Assists per 90', 'xA per 90',
        'Shots per 90', 'Shots on target, %',
        'Dribbles per 90', 'Successful dribbles, %',
        'Progressive runs per 90', 'Accelerations per 90',
        'Passes per 90', 'Accurate passes, %',
        'Forward passes per 90', 'Accurate forward passes, %',
        'Progressive passes per 90', 'Accurate progressive passes, %',
        'Key passes per 90', 'Smart passes per 90', 'Accurate smart passes, %',
        'Passes to final third per 90', 'Accurate passes to final third, %',
        'Through passes per 90', 'Accurate through passes, %',
        'Shot assists per 90', 'Second assists per 90', 'Deep completions per 90',
        'Touches in box per 90', 'Offensive duels per 90', 'Offensive duels won, %',
        'Role', 'Role', 'Division', 'Due For Release'
    ]

    forward_cols = [
        'Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played',
        'Goals', 'xG', 'Assists', 'xA',
        'Goals per 90', 'Non-penalty goals per 90', 'xG per 90',
        'Head goals per 90', 'Shots per 90', 'Shots on target, %', 'Goal conversion, %',
        'Assists per 90', 'xA per 90', 'Shot assists per 90',
        'Crosses per 90', 'Accurate crosses, %',
        'Crosses to goalie box per 90', 'Deep completed crosses per 90',
        'Dribbles per 90', 'Successful dribbles, %',
        'Offensive duels per 90', 'Offensive duels won, %',
        'Touches in box per 90', 'Progressive runs per 90', 'Accelerations per 90',
        'Fouls suffered per 90', 'Received passes per 90',
        'Key passes per 90', 'Passes to penalty area per 90', 'Accurate passes to penalty area, %',
        'Role', 'Role', 'Division', 'Due For Release'
    ]

    goalkeeper_cols = [
        'Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played',
        'Conceded goals', 'Conceded goals per 90',
        'Shots against', 'Shots against per 90',
        'Clean sheets', 'Save rate, %',
        'xG against', 'xG against per 90',
        'Prevented goals', 'Prevented goals per 90',
        'Back passes received as GK per 90',
        'Exits per 90', 'Aerial duels per 90.1',
        'Free kicks per 90', 'Direct free kicks per 90', 'Direct free kicks on target, %',
        'Passes per 90', 'Accurate passes, %',
        'Long passes per 90', 'Accurate long passes, %',
        'Average pass length, m', 'Average long pass length, m',
        'Role', 'Role', 'Division', 'Due For Release'
    ]

    exclude_cols = [
        'Player', 'Team', 'Position', 'Age', 'Role',
        'Matches played', 'Minutes played',
        'Yellow cards', 'Red cards',
        'Non-penalty goals', 'Head goals',
        'Shots', 'Conceded goals', 'Shots against',
        'Clean sheets', 'Prevented goals', 'xG against'
    ]

    lower_is_better = [
        'Fouls per 90',
        'Yellow cards per 90',
        'Red cards per 90',
        'Conceded goals per 90',
        'xG against per 90'
    ]

    def add_percentile_ranks(data, exclude_cols, lower_is_better=[]):
        data = data.copy()

        metric_cols = [col for col in data.columns if col not in exclude_cols]

        for col in metric_cols:

            if col in lower_is_better:
                data[f'{col} percentile'] = (
                    data[col]
                    .rank(pct=True, ascending=False)
                    .mul(100)
                    .round(1)
                )
            else:
                data[f'{col} percentile'] = (
                    data[col]
                    .rank(pct=True)
                    .mul(100)
                    .round(1)
                )

        return data

    df_defenders = add_percentile_ranks(
        df[df['Role'] == 'Defender'][defender_cols],
        exclude_cols,
        lower_is_better
    )

    df_midfielders = add_percentile_ranks(
        df[df['Role'] == 'Midfielder'][midfielder_cols],
        exclude_cols,
        lower_is_better
    )

    df_forwards = add_percentile_ranks(
        df[df['Role'] == 'Forward'][forward_cols],
        exclude_cols,
        lower_is_better
    )

    df_goalkeepers = add_percentile_ranks(
        df[df['Role'] == 'Goalkeeper'][goalkeeper_cols],
        exclude_cols,
        lower_is_better
    )

    return df_defenders, df_midfielders, df_forwards, df_goalkeepers
