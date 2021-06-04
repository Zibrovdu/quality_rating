import dash

from quality_rating.callbacks import register_callbacks
from quality_rating.layouts import serve_layout

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                title='Оценка качества')
server = app.server

app.layout = serve_layout
register_callbacks(app)

if __name__ == '__main__':
    app.run_server()
