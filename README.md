# olivera-bias-metric
A project to compute and visualize neurons using the Olivera Bias Metric (OBM) Version 1.0 – for Drosophila optic lobe:v1.1 using data from neuPrint


How to Run
1. Query neuron data:
python scripts/query_neurons.py
2. Compute OBM coordinates:
python scripts/compute_bias_coordinates.py
3. Generate OBM plots:
All neurons in one plot:
python scripts/plot_bias_coordinates_all.py
4. One plot per neurotransmitter:
python scripts/plot_bias_coordinates_per_nt.py

---

## About the OBM Design and Data Compatibility

This implementation of the **Olivera Bias Metric (OBM)** is specifically designed for the `optic-lobe:v1.1` dataset from the [neuPrint](https://neuprint.janelia.org) database. It queries neuron-level data including:

- `consensusNt` — the neurotransmitter assigned by expert consensus
- Synaptic weight — for upstream and downstream partners

These values are grouped and computed into OBM coordinates per neuron.

### Compatibility with Other neuPrint Datasets

Other neuPrint datasets such as:

- `hemibrain:v1.2.1`
- `manc:v1.2.3` (Male Adult Nerve Cord)
- `mushroombody`

may **not include the `consensusNt` field**. Instead, manc:v1.2.3 uses `predictedNt` , while others do not include neurotransmitter annotations at all. Therefore:

- The current OBM (v1.0) **will not work directly** with these datasets without modification.
- Future versions (e.g., OBM v1.1) will include support for `manc` and other datasets, even if neurotransmitter annotations are less reliable.

---

## Using OBM with Custom Datasets

If you have your own dataset, you can still compute OBM **as long as** you have:

1. Synaptic weight information
2. The neurotransmitter of the neuron at hand
3. The distribution of neurotransmitters in upstream and downstream connections

Only the `query_neurons.py` script is tied to neuPrint. The other three scripts can be adapted to your data with minimal changes.

---
### 1. Excitatory vs Inhibitory Neurotransmitters

#### File: compute_bias_coordinates.py  
#### Lines: 19–23
```python
# NOTE: Define excitatory and inhibitory components (changes depending on species)
df["E_in"] = df["ACh_in"]
df["I_in"] = df["GABA_in"] + df["Glu_in"]
df["E_out"] = df["ACh_out"]
df["I_out"] = df["GABA_out"] + df["Glu_out"]


Note:
This reflects that in Drosophila Melanogaster, glutamate is inhibitory, acting through GluCl (glutamate-gated chloride channels), which produce inhibitory postsynaptic potentials. In contrast, vertebrate glutamate is typically excitatory via AMPA/NMDA receptors.

For other species, this logic should be modified.

Example for vertebrates:

df["E_in"] = df["ACh_in"] + df["Glu_in"]
df["I_in"] = df["GABA_in"]
```

### 2. Neuromodulators

#### File: query_neurons.py  
#### Lines: 76-83
```python
# Get neuron names for neuromodulators
    neuromodulator_neurons = {
        nt: df[df["consensusNt"] == nt]["instance"].dropna().unique().tolist()
        for nt in neuromodulator_nts
# NOTE: Neuromodulators (serotonin, dopamine, octopamine) are not used in OBM.
#       However, they are still reported for interpretability. If future research
#       helps convert the neuromodulatory effect on neurotransmitters into numerical values,
#       they may be included in future versions of the OBM.


Note:
Neuromodulators do not currently influence OBM scoring but are included in the output for potential interpretability and future use.
```


### 3. Histamine Inputs/Outputs

#### File: query_neurons.py  
#### Lines: 117-120
```python
"Histamine_in": get_weight("histamine", in_nts),
"Histamine_out": get_weight("histamine", out_nts),
# NOTE: Histamine inputs and outputs are not used for OBM calculation.
#       They are included in the output for completeness but do not contribute to OBM metrics.

```
  ---
    
## OBM Calculation and Interpretation
The OBM coordinate system is defined by:

```python
OBM_input  = (E_in  - I_in)  / (E_in  + I_in)   # x-axis
OBM_output = (I_out - E_out) / (E_out + I_out)  # y-axis
```
This results in a 2D scatter plot, classifying neurons into four quadrants:
```python
Quadrant	
(+x, +y)	Excitatory Input / Inhibitory Output - Quadrant 1
(-x, +y)	Inhibitory Input / Inhibitory Output - Quadrant 2
(-x, -y)	Inhibitory Input / Excitatory Output - Quadrant 3
(+x, -y)	Excitatory Input / Excitatory Output - Quadrant 4
```
---

## Future Plans
  
1. ``v1.1 will support OBM calculation for manc:v1.2.3 despite lower transmitter annotation reliability.``  

2. ``Neuromodulators may be incorporated via parameterized weighting, depending on research advances.``   

3. ``compatible with more datasets like that of Caenorhabditis elegans``

4. ``` 
   Spatial Weighting of Synaptic Strength:
   A future extension may involve integrating 3D spatial data, such as soma and synapse coordinates from connectomics datasets
   Rationale: Synaptic inputs located closer to the soma may exert a stronger physiological effect.
   Incorporating this spatial distance into synaptic weighting could improve OBM precision.
   
   - The feasibility of this depends on:
   1.Availability of soma coordinates
   2.Access to synapse-level 3D coordinates
   3.Methodology to compute Euclidean distance
