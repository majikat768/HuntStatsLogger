variables = {
    "main_window_background": "#212121",
    "main_text_color": "#e8e8e8",

    "header_background": "#20282c",
    "header_border_color": "#44ffffff",
    "widget_background": "#20282c",
    "widget_border_color": "#44ffffff",

    "widget_background_gradient": "qlineargradient(\
        x1:0,y1:0,x2:1,y2:0,\
        stop:0.0 transparent,\
        stop:0.02 widget_background,\
        stop:0.98 widget_background,\
        stop:1.0 transparent)",

    "header_background_gradient": "qlineargradient(\
        x1:0,y1:0,x2:1,y2:0,\
        stop:0.0 transparent,\
        stop:0.02 header_background,\
        stop:0.98 header_background,\
        stop:1.0 transparent)",

    "widget_border_gradient": "qlineargradient(\
        x1:0,y1:0,x2:1,y2:0,\
        stop:0.0 transparent,\
        stop:0.02 widget_border_color,\
        stop:0.98 widget_border_color,\
        stop:1.0 transparent)",

    "tab_color": "#1188ccff",
    "tab_border_color": "#44ffffff",

    "tab_gradient": "qlineargradient(\
        x1:0,y1:0,x2:1,y2:0,\
        stop:0.0 transparent,\
        stop:0.02 tab_color,\
        stop:0.98 tab_color,\
        stop:1.0 transparent)",

    "selected_tab_color": "#4f171a",

    "selected_tab_gradient": "qlineargradient(\
        x1:0,y1:0,x2:1,y2:0,\
        stop:0.0 tab_color,\
        stop:0.1 selected_tab_color,\
        stop:0.9 selected_tab_color,\
        stop:1.0 tab_color)"
}

new_variables = {}
for k in sorted(variables,key=len,reverse=True):
    new_variables[k] = variables[k]
variables = new_variables