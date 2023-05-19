from keras.models import model_from_json
import numpy as np
import os





# load json and create model
json_file = open('/logs/04_extra_nodes_layers_200_epochs/model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights('/logs/04_extra_nodes_layers_200_epochs/model_weights.h5')
print("Loaded model from disk")