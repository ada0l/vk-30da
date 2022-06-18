import dash
import pandas as pd
from dash import dcc, html
from dateutil import parser


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


# posts
posts_df = pd.read_csv("data/posts.csv")

# profiles
profiles_df = pd.read_csv("data/profiles.csv").groupby('id').first().reset_index()

# groups
groups_df = pd.read_csv("data/groups.csv").groupby('id').first().reset_index()

# comments
comments_df = pd.read_csv("data/comments.csv")

# scalars_values_by_date
scalars_values_by_date = posts_df.copy()
scalars_values_by_date['date'] = scalars_values_by_date['date'].map(lambda x: parser.parse(x).date())
scalars_values_by_date = scalars_values_by_date.groupby('date').agg({
    'likes_count': ['sum'],
    'comments_count': ['sum'],
    'views_count': ['sum']
}).reset_index()
scalars_values_by_date.columns = ["date", "likes_count", "comment_count", "views_count"]

# top posts
posts_top_10 = posts_df.sort_values(by=['likes_count', 'views_count'], ascending=[False, False]).head(10)
posts_top_10['text'] = posts_top_10['text'][:50]

# top comments
comments_df_merged = pd.merge(
    comments_df, profiles_df, left_on="from_id", right_on="id", how="left"
).sort_values(by=['likes'], ascending=[False])

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="FEFU IMCT", ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": scalars_values_by_date["date"],
                        "y": scalars_values_by_date["views_count"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Views"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": scalars_values_by_date["date"],
                        "y": scalars_values_by_date["comment_count"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Comments"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": scalars_values_by_date["date"],
                        "y": scalars_values_by_date["likes_count"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Likes"},
            },
        ),
        html.H2(children='top posts'),
        generate_table(posts_top_10[['date', 'text', 'likes_count', 'views_count', 'comments_count']]),
        html.H2(children='top comments'),
        generate_table(comments_df_merged[['text', 'likes', 'last_name', 'first_name']])
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')
