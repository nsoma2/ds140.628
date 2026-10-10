import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Brain Volume Sankey Diagram")

# Load data
url = "https://raw.githubusercontent.com/bcaffo/MRIcloudT1volumetrics/master/inst/extdata/multilevel_lookup_table.txt"
multilevel_lookup = pd.read_csv(url, sep="\t").drop(['Level5'], axis=1)
multilevel_lookup = multilevel_lookup.rename(columns={
    "modify": "roi",
    "modify.1": "level4",
    "modify.2": "level3",
    "modify.3": "level2",
    "modify.4": "level1"
})
multilevel_lookup = multilevel_lookup[['roi', 'level4', 'level3', 'level2', 'level1']]

id = 127
subjectData = pd.read_csv("https://raw.githubusercontent.com/smart-stats/ds4bio_book/main/book/assetts/kirby21AllLevels.csv")
subjectData = subjectData.loc[(subjectData.type == 1) & (subjectData.level == 5) & (subjectData.id == id)]
subjectData = subjectData[['roi', 'volume']]
subjectData = pd.merge(subjectData, multilevel_lookup, on="roi")
subjectData = subjectData.assign(icv="ICV")
subjectData = subjectData.assign(comp=subjectData.volume / np.sum(subjectData.volume))

# Get unique labels for 3 levels
level1_labels = subjectData['level1'].unique().tolist()
level2_labels = subjectData['level2'].unique().tolist()
level3_labels = subjectData['level3'].unique().tolist()

# Combine all labels: ICV -> Level 1 -> Level 2 -> Level 3
all_labels = ['ICV'] + level1_labels + level2_labels + level3_labels

# Create label to index mapping
label_to_idx = {label: idx for idx, label in enumerate(all_labels)}

# Prepare source, target, and value lists
sources = []
targets = []
values = []

# ICV -> Level 1
for _, row in subjectData.groupby('level1')['volume'].sum().reset_index().iterrows():
    sources.append(label_to_idx['ICV'])
    targets.append(label_to_idx[row['level1']])
    values.append(row['volume'])

# Level 1 -> Level 2
for _, row in subjectData.groupby(['level1', 'level2'])['volume'].sum().reset_index().iterrows():
    sources.append(label_to_idx[row['level1']])
    targets.append(label_to_idx[row['level2']])
    values.append(row['volume'])

# Level 2 -> Level 3
for _, row in subjectData.groupby(['level2', 'level3'])['volume'].sum().reset_index().iterrows():
    sources.append(label_to_idx[row['level2']])
    targets.append(label_to_idx[row['level3']])
    values.append(row['volume'])

# Create Sankey Diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=all_labels,
        color="steelblue"
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values
    )
)])

fig.update_layout(
    title_text=f"Brain Volume Hierarchy - Subject 127",
    font_size=10,
    height=700,
    width=1100
)

st.plotly_chart(fig, use_container_width=True)
