"""
Here we Calculate the coordinates for my Olivera Bias Metric (OBM) 
for each neuron based on its excitatory (E) and inhibitory (I) input/output weights.
"""

import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.abspath(os.path.join(script_dir, "..", "data"))


input_path = os.path.join(data_dir, "neurons_list.csv")
output_path = os.path.join(data_dir, "neurons_bias_coordinates.csv")


df = pd.read_csv(input_path).fillna(0)

# NOTE: Define excitatory and inhibitory components (changes depending on species)
df["E_in"] = df["ACh_in"]
df["I_in"] = df["GABA_in"] + df["Glu_in"]
df["E_out"] = df["ACh_out"]
df["I_out"] = df["GABA_out"] + df["Glu_out"]

# filter invalid E/I inputs and outputs
valid_mask = (df["E_in"] + df["I_in"] > 0) & (df["E_out"] + df["I_out"] > 0)
df = df[valid_mask].copy()
print(f"Neurons kept: {len(df)}")


df["x"] = (df["E_in"] - df["I_in"]) / (df["E_in"] + df["I_in"])
df["y"] = (df["I_out"] - df["E_out"]) / (df["E_out"] + df["I_out"])


df.to_csv(output_path, index=False)
print(f"Saved to {output_path}")
