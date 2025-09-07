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


DATA_DIR = os.path.abspath(os.path.join(script_dir, "..", "data"))
df = pd.read_csv(os.path.join(DATA_DIR, "neurons_bias_coordinates.csv"))
df["Color"] = df["Neuron NT"].map(nt_color_map).fillna("black")


output_dir = os.path.abspath(os.path.join(script_dir, "..", "outputs"))
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "OBM_plot_all.png")

# Plot
def plot_obm_all_neurons(df, output_path):
    plt.figure(figsize=(10, 8))
    plt.axhline(0, color='black', linewidth=2)
    plt.axvline(0, color='black', linewidth=2)
    plt.scatter(df["x"], df["y"], c=df["Color"], edgecolors="k", alpha=0.75)

    plt.xlabel("OBM Input Bias (x) = (E_in - I_in) / (E_in + I_in)")
    plt.ylabel("OBM Output Bias (y) = (I_out - E_out) / (E_out + I_out)")
    plt.title("All Neurons of Drosophila's Optic-Lobe E/I Bias Map")
    plt.grid(True)

    # Legend
    legend_patches = [
        mpatches.Patch(color=nt_color_map[nt], label=nt_label_map[nt])
        for nt in nt_color_map
    ]
    plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved plot to {output_path}")

    plt.show()
    plt.close()
