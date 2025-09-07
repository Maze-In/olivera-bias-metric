import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import importlib.util

script_dir = os.path.dirname(os.path.abspath(__file__)) 
constants_path = os.path.join(script_dir, "..", "utils", "constants.py")

spec = importlib.util.spec_from_file_location("constants", constants_path)
constants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(constants)

nt_label_map = constants.nt_label_map
nt_color_map = constants.nt_color_map


data_dir = os.path.abspath(os.path.join(script_dir, "..", "data"))
df = pd.read_csv(os.path.join(data_dir, "neurons_bias_coordinates.csv"))
df["Color"] = df["Neuron NT"].map(nt_color_map).fillna("black")


OUTPUT_DIR = os.path.abspath(os.path.join(script_dir, "..", "outputs", "OBM_plot_per_nt"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

#Plot
def plot_simple_scatter(df_nt, nt):
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.axhline(0, color="black", linewidth=2)
    ax.axvline(0, color="black", linewidth=2)
    ax.scatter(df_nt["x"], df_nt["y"], c=df_nt["Color"], edgecolors="k", alpha=0.75)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.set_xlabel("OBM Input Bias (x) = (E_in - I_in) / (E_in + I_in)")
    ax.set_ylabel("OBM Output Bias (y) = (I_out - E_out) / (E_out + I_out)")
    ax.set_title(f"{nt_label_map.get(nt, nt.capitalize())} Neurons (n={len(df_nt)})")
    ax.grid(True)

    # Legend
    legend_patches = [
        mpatches.Patch(color=nt_color_map[nt], label=nt_label_map[nt])
        for nt in nt_color_map
    ]
    ax.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc="upper left")

    filename = f"{nt_label_map.get(nt, nt).capitalize()}_OBM_plot.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()
    print(f"Saved {nt_label_map.get(nt, nt)} plot to {filepath}")


for nt in df["Neuron NT"].unique():
    df_nt = df[df["Neuron NT"] == nt].copy()
    plot_simple_scatter(df_nt, nt)
