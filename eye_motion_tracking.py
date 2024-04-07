import cv2
import numpy as np
import os
import subprocess
import base64
from dash import Dash, html, dcc, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from dash.long_callback import DiskcacheLongCallbackManager
import dash_mantine_components as dmc
import plotly.graph_objs as go

CARD_STYLE = "https://fonts.googleapis.com/css?family=Saira+Semi+Condensed:300,400,700"

## Diskcache
import diskcache

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = Dash(
    __name__,
    external_stylesheets=[CARD_STYLE],
    long_callback_manager=long_callback_manager,
    suppress_callback_exceptions=True,
)

app.title = 'Eye Analyzer'

model_input = html.Div([
    dmc.Col(
        dmc.Text("Model Settings", color='white', style={"fontSize": 20, "font-family": 'changa'})
    ),
    dmc.Center([
        dmc.Col([
            dmc.Text('Start Time (s): ', color='white', style={"font-family": 'changa'}),
            dmc.NumberInput(
                id='starttime-input',
                label="",
                value=0,
                min=0,
                style={"color": 'white', "font-family": 'changa'},
                className='mantine-1w07r5r'
            )
        ], span=10)
    ]),
    dmc.Center([
        dmc.Col([
            dmc.Text('Duration (s): ', color='white', style={"font-family": 'changa'}),
            dmc.NumberInput(
                id='duration-input',
                label="",
                value=5,
                min=1,
                max=10,
                style={"color": 'white', "font-family": 'changa'},
                className='mantine-1w07r5r'
            )
        ], span=10)
    ]),
    dmc.Center([
        dmc.Col([
            dmc.Text('Detection Confidence: ', color='white', style={"font-family": 'changa'}),
            dmc.Slider(
                id="detection-slider",
                value=5,
                min=0, max=10, step=0.5,
                style={"width": 250},
            )
        ], span=10)
    ]),
    dmc.Center([
        dmc.Col([
            dmc.Text('Tracking Confidence: ', color='white', style={"font-family": 'changa'}),
            dmc.Slider(
                id="tracking-slider",
                value=5,
                min=0, max=10, step=0.5,
                style={"width": 250},
            )
        ], span=10)
    ]),
    dmc.Space(h=20),
], style={})

output_body = html.Div([
    dmc.Grid([
        dmc.Col([
            dmc.LoadingOverlay(
                html.Div([
                    html.Img(id='frame-output', style={'height': '380px', 'width': '380px'}),
                    html.Img(id='grayscale-output', style={'height': '380px', 'width': '380px'}),
                    html.Img(id='threshold-output', style={'height': '380px', 'width': '380px'}),
                ], style={'display': 'flex', 'justify-content': 'space-evenly', 'align-item': 'center'}),
                loaderProps={"variant": "bars", "size": "xl"}
            )
        ]),
    ])
], id='output-div', style={"visibility": "hidden", 'overflowX': 'hidden'})



app.layout = dmc.Container([
    dmc.Center([
        dmc.Grid([
            dmc.Col([
                dmc.Text(
                    "Eye Motion Analysis App",
                    color='white',
                    align="center",
                    weight=500,
                    style={"fontSize": 36, "font-family": 'changa'}
                )
            ], span=12)
        ]),
    ]),
    html.Hr(),
    dmc.Space(h=30),
    dmc.Grid([
        dmc.Col([
            html.Div([
                dcc.Upload(
                    id='upload-video',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Video')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px',
                        "font-family": 'changa',
                        'color': 'white'
                    },
                    multiple=False  # Changed to False to allow only one file upload
                ),
                html.Div(id='output-video',style={'display': 'flex', 'justify-content':'center', 'align-item':'center'})
            ])
        ], span=12)
    ]),
    dmc.Space(h=30),
    dmc.Center(
        dmc.Button("Run Model", id="run-model-button", variant='filled', size='lg', style={"font-family": 'changa'})
    ),
    dmc.Space(h=30),
    dcc.Store(id='output-path'),
    model_input,
    dmc.LoadingOverlay(output_body, loaderProps={"variant": "bars", "size": "xl"}),
    dmc.Space(h=30)
], fluid=True, style={'backgroundColor': '#111b2b', 'overflow-y': 'hidden', 'overflowX': 'hidden'})


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    with open(filename, 'wb') as f:
        f.write(decoded)
    return html.Video(src=contents, controls=True)


@app.callback(Output('output-video', 'children'),
              Input('upload-video', 'contents'),
              State('upload-video', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        children = parse_contents(contents, filename)
        return children


last_processed_filename = None

@app.callback(
    Output("starttime-input", "value"),
    Output("duration-input", "value"),
    Input("upload-video", "contents"),
    State("upload-video", "filename"),
    prevent_initial_call=True
)
def update_time(contents, filename):
    global last_processed_filename

    if filename != last_processed_filename:
        last_processed_filename = filename

        if contents is not None:
            content_type, content_string = contents.split(',')[0], contents.split(',')[1]
            decoded = base64.b64decode(content_string)
            video_path = 'temp_video.mp4'
            with open(video_path, 'wb') as f:
                f.write(decoded)

            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps

            cap.release()
            os.remove(video_path)

            return 0, duration

    if contents is None:
        raise PreventUpdate
    else:
        return dash.no_update, dash.no_update

def convert_webm_to_mp4(input_file, output_file):
    ffmpeg_path = 'C:\Path_program'  # Replace this with the actual path to ffmpeg
    subprocess.run([ffmpeg_path, '-i', input_file, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_file])

@app.long_callback(
    Output("frame-output", "src"),
    Output("grayscale-output", "src"),
    Output("threshold-output", "src"),
    Input("run-model-button", "n_clicks"),
    State("upload-video", "contents"),
    State("upload-video", "filename"),
    State("starttime-input", "value"),
    State("duration-input", "value"),
    State("detection-slider", "value"),
    State("tracking-slider", "value"),
    running=[
            (Output("run-model-button", "disabled"), True, False),
            (Output("run-model-button", "children"), "Running Model", "Run Model"),
            (Output("output-div", "style"), {"visibility": "hidden"}, {"visibility": "visible"})
        ],
    manager=long_callback_manager,
    prevent_initial_call=True
)
def show_output(n_clicks, contents, filename, start, duration, detectionCon, trackingCon, save_directory="./uploaded_videos"):
    if n_clicks and contents is not None:
        video_data = contents.split(',')[1]
        video_data = base64.b64decode(video_data)
        video_path = filename

        if video_path.lower().endswith('.webm'):
            mp4_path = video_path[:-5] + '.mp4'
            convert_webm_to_mp4(video_path, mp4_path)
            video_path = mp4_path

        with open(video_path, "wb") as f:
            f.write(video_data)

        cap = cv2.VideoCapture(video_path)

        while True:
            ret, frame = cap.read()
            if ret is False:
                break

            # Eye tracking logic
            # Left Eye
            yl1 = 295
            yl2 = 350
            xl1 = 575
            xl2 = 725
            roi_left = frame[yl1: yl2, xl1: xl2]
            rows_left, cols_left, _ = roi_left.shape
            gray_roi_left = cv2.cvtColor(roi_left, cv2.COLOR_BGR2GRAY)
            gray_roi_left = cv2.GaussianBlur(gray_roi_left, (7, 7), 0)

            _, threshold_left = cv2.threshold(gray_roi_left, 50, 255, cv2.THRESH_BINARY_INV)

            contours_left, _ = cv2.findContours(threshold_left, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours_left = sorted(contours_left, key=lambda x: cv2.contourArea(x), reverse=True)

            for cnt in contours_left:
                x_left, y_left, w_left, h_left = cv2.boundingRect(cnt)

                cv2.rectangle(frame, (x_left + xl1, y_left + yl1), (x_left + w_left + xl1, y_left + h_left + yl1), (255, 0, 0), 2)
                cv2.line(frame, (x_left + int(w_left/2) + xl1, 0 + yl1), (x_left + int(w_left/2) + xl1, rows_left + yl1), (0, 255, 0), 2)
                cv2.line(frame, (0 + xl1, y_left + int(h_left/2) + yl1), (cols_left + xl1, y_left + int(h_left/2) + yl1), (0, 255, 0), 2)

                break  # Only process the largest contour

            # Right Eye
            yr1 = 295
            yr2 = 350
            xr1 = 725
            xr2 = 825
            roi_right = frame[yr1: yr2, xr1: xr2]
            rows_right, cols_right, _ = roi_right.shape
            gray_roi_right = cv2.cvtColor(roi_right, cv2.COLOR_BGR2GRAY)
            gray_roi_right = cv2.GaussianBlur(gray_roi_right, (7, 7), 0)

            _, threshold_right = cv2.threshold(gray_roi_right, 50, 255, cv2.THRESH_BINARY_INV)

            contours_right, _ = cv2.findContours(threshold_right, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours_right = sorted(contours_right, key=lambda x: cv2.contourArea(x), reverse=True)

            for cnt in contours_right:
                x_right, y_right, w_right, h_right = cv2.boundingRect(cnt)

                cv2.rectangle(frame, (x_right + xr1, y_right + yr1), (x_right + w_right + xr1, y_right + h_right + yr1), (255, 0, 0), 2)
                cv2.line(frame, (x_right + int(w_right/2) + xr1, 0 + yr1), (x_right + int(w_right/2) + xr1, rows_right + yr1), (0, 255, 0), 2)
                cv2.line(frame, (0 + xr1, y_right + int(h_right/2) + yr1), (cols_right + xr1, y_right + int(h_right/2) + yr1), (0, 255, 0), 2)

                break  # Only process the largest contour

            grayscale_frame = np.hstack((cv2.cvtColor(gray_roi_left, cv2.COLOR_GRAY2BGR), cv2.cvtColor(gray_roi_right, cv2.COLOR_GRAY2BGR)))
            threshold_frame = np.hstack((cv2.cvtColor(threshold_left, cv2.COLOR_GRAY2BGR), cv2.cvtColor(threshold_right, cv2.COLOR_GRAY2BGR)))

            ret, buffer1 = cv2.imencode('.jpg', frame)
            ret, buffer2 = cv2.imencode('.jpg', grayscale_frame)
            ret, buffer3 = cv2.imencode('.jpg', threshold_frame)

            frame_output = base64.b64encode(buffer1)
            grayscale_output = base64.b64encode(buffer2)
            threshold_output = base64.b64encode(buffer3)

            return 'data:image/jpg;base64,' + frame_output.decode(), 'data:image/jpg;base64,' + grayscale_output.decode(), 'data:image/jpg;base64,' + threshold_output.decode()

        cap.release()
        cv2.destroyAllWindows()
    else:
        print("ERROR HERE")

if __name__ == "__main__":
    app.run_server()
