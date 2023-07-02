from style.variables import variables

processed_stylesheet = "style_processed.qss"
def process_style(stylesheet):
    preprocessed = open(stylesheet,"r").read()

    done = False
    while not done:
        done = True
        for key in variables:
            if preprocessed.find(key) > 0:
                done = False
            preprocessed = preprocessed.replace(key,variables[key])

    with open(processed_stylesheet,"w") as f:
        f.write(preprocessed)
    return processed_stylesheet