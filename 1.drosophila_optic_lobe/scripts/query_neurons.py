# NeuPrint Query

import os
import pandas as pd
from neuprint import Client, fetch_neurons

""" Insert your neuPrint authentication token:
from https://neuprint.janelia.org/account """

auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InJlbm95b2xpdmVyYUBnbWFpbC5jb20iLCJsZXZlbCI6Im5vYXV0aCIsImltYWdlLXVybCI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0ppdFV1cWFRcHNHTWJ6TklLaXNsNzJwaXp1YlFVN29IMXZDbHh2Nk9mTGVfVWhOTGJ3PXM5Ni1jP3N6PTUwP3N6PTUwIiwiZXhwIjoxOTM2NzQ1MzAxfQ.7rBAvyXKDId2r3u0ZO8clEJbTIIWDwZoF2_wPHMZ9-g"
dataset = "optic-lobe:v1.1"


script_dir = os.path.dirname(os.path.abspath(__file__)) 
output_dir = os.path.abspath(os.path.join(script_dir, "..", "data"))
output_file = os.path.join(output_dir, "neurons_list.csv")
os.makedirs(output_dir, exist_ok=True) 
print("Saving to:", output_file)


client = Client('https://neuprint.janelia.org', token=auth_token, dataset=dataset)


nt_list = [
    "acetylcholine", "gaba", "glutamate", "octopamine",
    "dopamine", "serotonin", "histamine", "unclear", "unknown"
]
neuromodulator_nts = ["serotonin", "dopamine", "octopamine"]


print("Fetching neurons from neuPrint...")
neuron_df, _ = fetch_neurons(client=client)
neuron_df = neuron_df[["bodyId", "instance", "consensusNt"]].fillna("unknown")
neuron_df["consensusNt"] = neuron_df["consensusNt"].str.lower()
print(f" Total neurons: {len(neuron_df)}") # Total neurons in the specific database (line:10)


neuron_meta_lookup = (
    neuron_df.fillna("unknown")
    .set_index("bodyId")[["instance", "consensusNt"]]
    .to_dict(orient="index")
)

results = []
done_ids = set()

if os.path.exists(output_file):
    print(f"Resuming from previous output: {output_file}")
    partial_df = pd.read_csv(output_file)
    results = partial_df.to_dict(orient="records")
    done_ids = set(partial_df["Neuron ID"])

def get_weight_by_nt(neuron_id, direction):
    if direction not in ("inputs", "outputs"):
        raise ValueError("direction must be 'inputs' or 'outputs'")

    source, target = ("m", "n") if direction == "inputs" else ("n", "m")

    query = f"""
    MATCH ({source}:Neuron)-[x:ConnectsTo]->({target}:Neuron)
    WHERE {target}.bodyId = {neuron_id}
    RETURN {source}.bodyId AS neuron, x.weight AS weight
    """
    df = pd.DataFrame(client.fetch_custom(query))
    if df.empty:
        return {}, {}

    df["consensusNt"] = df["neuron"].map(
        lambda pid: neuron_meta_lookup.get(pid, {}).get("consensusNt", "unknown")
    )
    df["instance"] = df["neuron"].map(
        lambda pid: neuron_meta_lookup.get(pid, {}).get("instance", "unknown")
    )
    nt_sums = df.groupby("consensusNt")["weight"].sum().to_dict()

    neuromodulator_neurons = {
        nt: df[df["consensusNt"] == nt]["instance"].dropna().unique().tolist()
        for nt in neuromodulator_nts

        # NOTE: Neuromodulators (serotonin, dopamine, octopamine) are not used in OBM.
        #       However, they are still reported for interpretability. If future research
        #       helps convert the neuromodulatory effect on neurotransmitters into numerical values,
        #       they may be included in future versions of the OBM.

    }

    return nt_sums, neuromodulator_neurons


print("Calculating synaptic weight breakdown...")
for _, row in neuron_df.iterrows():
    body_id = row["bodyId"]
    if body_id in done_ids:
        continue

    name = row["instance"]
    neuron_nt = row["consensusNt"]

    in_nts, in_neuromodulator = get_weight_by_nt(body_id, "inputs")
    out_nts, out_neuromodulator = get_weight_by_nt(body_id, "outputs")

    def get_weight(nt, d):
        return round(d.get(nt, 0), 2)

    result = {
        "Neuron ID": body_id,
        "Neuron Name": name,
        "Neuron NT": neuron_nt,
        "ACh_in": get_weight("acetylcholine", in_nts),
        "GABA_in": get_weight("gaba", in_nts),
        "Glu_in": get_weight("glutamate", in_nts),
        "I_in": get_weight("gaba", in_nts) + get_weight("glutamate", in_nts),
        "ACh_out": get_weight("acetylcholine", out_nts),
        "GABA_out": get_weight("gaba", out_nts),
        "Glu_out": get_weight("glutamate", out_nts),
        "I_out": get_weight("gaba", out_nts) + get_weight("glutamate", out_nts),
        "Histamine_in": get_weight("histamine", in_nts),
        "Histamine_out": get_weight("histamine", out_nts),
        # NOTE: Histamine inputs and outputs are not used for OBM calculation.
        #       They are included in the output for completeness but do not contribute to OBM metrics.

    }

    for nt in neuromodulator_nts:
        result[f"{nt.capitalize()}_in"] = get_weight(nt, in_nts)
        result[f"{nt.capitalize()}_out"] = get_weight(nt, out_nts)
        result[f"{nt.capitalize()}_in_neurons"] = "; ".join(in_neuromodulator.get(nt, []))
        result[f"{nt.capitalize()}_out_neurons"] = "; ".join(out_neuromodulator.get(nt, []))

    results.append(result)

    # Saves every 50 neurons
    if len(results) % 50 == 0:
        print(f"Progress: {len(results)} / {len(neuron_df)}")
        pd.DataFrame(results).to_csv(output_file, index=False)


results_df = pd.DataFrame(results)
results_df.to_csv(output_file, index=False)
print(f"\n Final output saved to: {output_file}")