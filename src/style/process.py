from style.variables import variables
from resources import resource_path
import re

processed_stylesheet = "style_processed.qss"
def process_style(stylesheet,variables):
    preprocessed = open(stylesheet,"r").read()

    done = False
    while not done:
        done = True
        for key in sorted(variables,key=len,reverse=True):
            if preprocessed.find(key) > 0:
                done = False
            preprocessed = preprocessed.replace(key,variables[key])

    paths = re.findall("resource_path\(.*\)",preprocessed)
    for path in paths:
        file = path.replace("resource_path(","").replace(")","").replace("\"","").replace("\'","")
        preprocessed = preprocessed.replace(path,"url("+file+")")
    with open(processed_stylesheet,"w") as f:
        f.write(preprocessed)
    return preprocessed