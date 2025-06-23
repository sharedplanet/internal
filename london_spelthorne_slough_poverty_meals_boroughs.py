import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

pink_cmap = LinearSegmentedColormap.from_list("custom_pink", [
    "#ffe6f0",
    "#ffb3d9",
    "#ff66b3",
    "#cc0066"
])

gdf_london = gpd.read_file("statistical-gis-boundaries-london/ESRI/London_Borough_Excluding_MHW.shp")
gdf_london = gdf_london.rename(columns={"NAME": "London Borough"})
gdf_london = gdf_london[["London Borough", "geometry"]]

gdf_uk = gpd.read_file("Local_Authority_Districts_December_2023_Boundaries_UK_BGC_-6607102865052560878/LAD_DEC_2023_UK_BGC.shp")
extra_boroughs = gdf_uk[gdf_uk["LAD23NM"].isin(["Slough", "Spelthorne", "Greenwich", "Bromley", "Sutton", "Bexley", "Havering"])]
extra_boroughs = extra_boroughs.rename(columns={"LAD23NM": "London Borough"})
extra_boroughs = extra_boroughs[["London Borough", "geometry"]]

gdf_london = gdf_london.to_crs(epsg=27700)
extra_boroughs = extra_boroughs.to_crs(epsg=27700)

gdf = pd.concat([gdf_london, extra_boroughs], ignore_index=True)

data = {
    "London Borough": [
        "Barking and Dagenham", "Barnet", "Brent", "Camden", "City of London",
        "Westminster", "Croydon", "Ealing", "Enfield", "Hackney",
        "Hammersmith and Fulham", "Haringey", "Harrow", "Hillingdon", "Hounslow",
        "Islington", "Kensington and Chelsea", "Kingston upon Thames", "Lambeth",
        "Lewisham", "Merton", "Newham", "Redbridge", "Richmond upon Thames",
        "Southwark", "Tower Hamlets", "Waltham Forest", "Wandsworth", "Slough", "Spelthorne",
        "Greenwich", "Bromley", "Sutton", "Bexley", "Havering"
    ],
    "Weekly Recipients": [
        "REDACTED"] * 35,
    "Poverty Rate": [
        30, 26, 31, 43, None, 42, 22, 31, 31, 28,
        19, 23, 22, 25, 29, 20, 28, 21, 25,
        29, 15, 38, 30, 12,
        21, 41, 23, 30, 30.6, 33.6, 26, 16, 22, 20, 19
    ]
}
df = pd.DataFrame(data)

merged = gdf.merge(df, on="London Borough", how="left")
merged = merged.to_crs(epsg=27700)

centroids = merged.copy()
centroids["geometry"] = centroids.representative_point()
centroids["BubbleSize"] = pd.to_numeric(centroids["Weekly Recipients"], errors="coerce") / 4
centroids["BubbleSize"] = centroids["BubbleSize"].clip(lower=10)
centroids_sorted = centroids.dropna(subset=["BubbleSize"]).sort_values("BubbleSize", ascending=False)

fig, ax = plt.subplots(1, 1, figsize=(13, 13))

merged.plot(
    column="Poverty Rate",
    cmap="Greens",
    linewidth=0.8,
    ax=ax,
    edgecolor="0.8",
    legend=True
)

centroids_sorted.plot(
    ax=ax,
    markersize=centroids_sorted["BubbleSize"],
    color="grey",
    alpha=0.6,
    edgecolor="black",
    linewidth=0.5
)

label_subs = {
    "City of London": "1",
    "Westminster": "2",
    "Kensington and Chelsea": "3",
    "Hammersmith and Fulham": "4"
}

for idx, row in merged.iterrows():
    point = row.geometry.representative_point()
    label = label_subs.get(row["London Borough"], row["London Borough"])
    ax.text(point.x, point.y, label, fontsize=8, ha='center', va='center')

for idx, row in merged.dropna(subset=["Poverty Rate"]).iterrows():
    pt = row.geometry.representative_point()
    ax.text(
        pt.x, pt.y - 550,
        f'{int(row["Poverty Rate"])}%',
        fontsize=7,
        ha='center',
        va='top',
        color='black',
        alpha=0.8
    )

label_legend_handles = [
    mpatches.Patch(color="none", label="1: City of London"),
    mpatches.Patch(color="none", label="2: Westminster"),
    mpatches.Patch(color="none", label="3: Kensington and Chelsea"),
    mpatches.Patch(color="none", label="4: Hammersmith and Fulham")
]
legend1 = ax.legend(handles=label_legend_handles, loc="lower left", bbox_to_anchor=(0.03, 0), title="Central Borough Labels", frameon=True)

for handle in [legend1]:
    ax.add_artist(handle)

bubble_sizes = [1000, 5000, 10000]
bubble_handles = [
    plt.scatter([], [], s=size/4, color="gray", alpha=0.6, edgecolor='black') for size in bubble_sizes
]
bubble_labels = [
    "1,000 recipients          ",
    "5,000 recipients          ",
    "10,000 recipients         ",
]

legend2 = ax.legend(
    bubble_handles,
    bubble_labels,
    loc="lower left",
    bbox_to_anchor=(0.03, -0.4),
    title="Weekly Recipients",
    scatterpoints=1,
    labelspacing=4,
    handlelength=5,
    frameon=True
)
legend2._legend_box.sep = 20
legend2._legend_box.height = 225

ax.add_artist(legend2)

plt.title("London Boroughs: Poverty Rates and Weekly Recipients", fontsize=16)
plt.axis("off")
plt.tight_layout()

fig.text(
    0.01, -0.02,
    "*Poverty rates for Spelthorne and Slough were sourced from their respective borough-level data, "
    "as they are not London boroughs. Additionally, the geographic shapes for both boroughs were merged "
    "with those of London's boroughs for consistency in mapping.",
    ha='left',
    va='top',
    fontsize=9,
    color='gray',
    wrap=True
)
plt.show()