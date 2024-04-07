import cv2
import dlib
import os
import base64
import numpy as np
from dash import html, dcc, Dash, Output, Input, State
import urllib.parse as urlparse
import dash_mantine_components as dmc

# Load the pre-trained face detector (SVM model) and landmark predictor
detector = dlib.simple_object_detector("models/dlib_face_detector.svm")
predictor = dlib.shape_predictor("models/dlib_landmark_predictor.dat")

# Initialize Dash app
app = Dash(__name__)

# Update the layout to accept image input and display output
app.layout = html.Div([
    html.Div(
        style={
            "margin": "0",
            "padding": "0",
            "background-color": "#111b2b",
            "font-family": "changa",
            "color": "white",
            "height": "100vh",
            "overflow-x": "hidden",
        },
        children=[
            dmc.Container([
                dmc.Center([
                    dmc.Grid([
                        dmc.Col([
                            dmc.Text(
                                "Thermal Image Analysis App",
                                color='white',
                                align="center",
                                weight=500,
                                style={"fontSize": 36}
                            )
                        ], span=12)
                    ]),
                ]),
            ]),
            html.Hr(),
            dmc.Space(h=30),
            dmc.Grid([
                dmc.Col([
                    html.Div([
                        dcc.Upload(
                            id='upload-image',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Image')
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
                            multiple=False  # Allow only one file to be uploaded
                        ),
                        # html.Button('Run Model', id='run-model-button', n_clicks=0),
                        html.Div(id='uploaded-image-output', style={'display': 'flex', 'justify-content':'center', 'align-item':'center'})  # Set fixed height
                    ])
                ])
            ]),
            dmc.Space(h=30),
            dmc.Center(
                dmc.Button("Run Model", id="run-model-button", n_clicks=0, variant='filled', size='lg',
                           style={"font-family": 'changa'})
            ),
            dmc.Space(h=30),
            dmc.LoadingOverlay(
                dmc.Grid([
                    html.Div(id='output-image')
                ],style={'display': 'flex', 'justify-content':'center', 'align-item':'center'}),
                loaderProps={"variant": "bars", "size": "xl"}
            )
        ]
    )
])


def predict_bounding_boxes_and_landmarks(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    dets = detector(gray)

    for det in dets:
        # Get the bounding box of the face
        (x, y, w, h) = (det.left(), det.top(), det.width(), det.height())

        # Draw bounding box around the face
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Predict landmarks for the current face
        landmarks = predictor(gray, det)

        # Draw landmarks on the image
        for i in range(0, landmarks.num_parts):
            x_lm = landmarks.part(i).x
            y_lm = landmarks.part(i).y
            cv2.circle(image, (x_lm, y_lm), 2, (0, 0, 255), -1)

    # Convert the processed image to base64
    _, img_encoded = cv2.imencode('.png', image)
    img_base64 = base64.b64encode(img_encoded).decode('ascii')
    return img_base64


def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    img_array = np.frombuffer(decoded, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img


@app.callback(Output('uploaded-image-output', 'children'),
              Input('upload-image', 'contents'))
def display_uploaded_image(contents):
    if contents is not None:
        return html.Img(src=contents, style={'max-width': '100%', 'margin': 'auto'})


@app.callback(Output('output-image', 'children'),
              Input('run-model-button', 'n_clicks'),
              State('upload-image', 'contents'))
def update_output(n_clicks, contents):
    if n_clicks > 0 and contents is not None:
        img = parse_contents(contents)
        img_base64 = predict_bounding_boxes_and_landmarks(img)
        return html.Img(src='data:image/png;base64,{}'.format(img_base64))


if __name__ == '__main__':
    app.run_server(debug=True)
