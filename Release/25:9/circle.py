#!/usr/bin/env python
import PySimpleGUI as sg

# Usage of Graph element.

layout = [[sg.Graph(canvas_size=(12, 12), graph_bottom_left=(0, 0), graph_top_right=(12, 10), enable_events=True, key='graph')],
          [sg.Text('Change circle color to:'), sg.Button('Red'), sg.Button('Blue'), sg.Button('Move')]]

window = sg.Window('Graph test', layout, finalize=True)

graph = window['graph']         # type: sg.Graph
circle = graph.draw_circle((6, 5), 5, fill_color='green', line_color='green')
while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED:
        break

window.close()