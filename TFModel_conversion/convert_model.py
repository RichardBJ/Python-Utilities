#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:56:06 2024

@author: rbj
"""
from tensorflow import keras
import tensorflowjs as tfjs
import h5py

#Take a look at what we've got
with h5py.File("model.h5", "r") as f:
    print(list(f.keys()))

model = keras.models.load_model("model.h5")

# Convert the Keras model to TensorFlow.js format
tfjs_target_dir = "json_model/tfjs_model"
tfjs.converters.save_keras_model(model, tfjs_target_dir)

print(f"Model converted and saved for TensorFlow.js at: {tfjs_target_dir}")