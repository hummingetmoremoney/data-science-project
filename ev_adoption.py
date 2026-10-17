"""How fast do car markets switch to electric? Analysis of IEA data via Our World in Data."""

import pandas as pd
import matplotlib.pyplot as plt

V = "Share of new cars that are electric"
AGGREGATES = ["World", "Europe", "European Union (27)", "Rest of World"]

df = pd.read_csv("data/ev_share.csv").rename(columns={V: "share"})
world = df[df.Entity == "World"].set_index("Year")["share"]
df = df[~df.Entity.isin(AGGREGATES)]
wide = df.pivot_table(index="Year", columns="Entity", values="share")

rows = []
for c in wide.columns:
    s = wide[c].dropna()
    if s.max() < 1:
        continue
    y1 = s[s >= 1].index.min()
    rows.append({"market": c, "y_1pct": y1,
                 "years_to_10pct": (s[s >= 10].index.min() - y1) if s.max() >= 10 else None,
                 "share_2025": s.get(2025)})
gaps = pd.DataFrame(rows).set_index("market")

t10 = gaps["years_to_10pct"].dropna()
s25 = gaps["share_2025"].dropna().sort_values(ascending=False)

# Figure 1: put every market on the same clock, starting at its first year above 1%.
fig, ax = plt.subplots(figsize=(9, 5.6))
for m in t10.index:
    s = wide[m].dropna()
    y1 = gaps.loc[m, "y_1pct"]
    ax.plot(s.index - y1, s.values, color="#C9CFD6", lw=1.1, zorder=1)

for m, col in [("Luxembourg", "#E69F00"), ("Germany", "#009E73"),
               ("United States", "#D55E00"), ("Norway", "#0072B2")]:
    s = wide[m].dropna()
    y1 = gaps.loc[m, "y_1pct"]
    ax.plot(s.index - y1, s.values, color=col, lw=2.4, zorder=3,
            label=f"{m} ({int(gaps.loc[m, 'years_to_10pct'])} yr)")

ax.axhline(10, color="#8894A0", lw=1, ls=(0, (4, 3)), zorder=2)
ax.text(9.55, 11.3, "10% of new sales", fontsize=9, color="#5A6672")
ax.set_xlim(0, 11.2)
ax.set_ylim(0, 100)
ax.set_xlabel("Years since the market first passed 1% of new car sales")
ax.set_ylabel("Electric share of new car sales (%)")
ax.legend(frameon=False, loc="upper left", fontsize=9.5)
ax.grid(axis="y", color="#E6EAEE", lw=0.8)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

fig.text(0.055, 0.965, "Once a market passes 1%, reaching 10% takes one to seven years",
         fontsize=15, weight="bold", color="#1A1A1A")
fig.text(0.055, 0.925,
         f"Each line is one market, shifted so that year 0 is its first year above 1%; "
         f"lines end in 2025. Median gap: {t10.median():.0f} years.",
         fontsize=10, color="#5A6672")
fig.subplots_adjust(left=0.085, right=0.93, top=0.855, bottom=0.115)
fig.savefig("figures/fig1_time_to_10pct.png", dpi=200)
plt.close(fig)

# Figure 2: where every market stands in 2025.
fig, ax = plt.subplots(figsize=(8.4, 10))
colors = ["#0072B2" if v >= 50 else "#D55E00" if v < 10 else "#B8C4CE" for v in s25.values]
ax.barh(range(len(s25)), s25.values, color=colors, height=0.72)
ax.set_yticks(range(len(s25)))
ax.set_yticklabels(s25.index, fontsize=8)
ax.invert_yaxis()
ax.axvline(world.loc[2025], color="#1A1A1A", lw=1.2, ls=(0, (5, 3)))
ax.text(world.loc[2025] + 1.5, len(s25) - 1.5,
        f"World average {world.loc[2025]:.0f}%", fontsize=9.5, color="#1A1A1A")
for i, v in enumerate(s25.values):
    ax.text(v + 1.2, i, f"{v:g}", va="center", fontsize=7.5, color="#333333")
ax.set_xlim(0, 108)
ax.set_xlabel("Electric share of new car sales in 2025 (%)")
ax.grid(axis="x", color="#E6EAEE", lw=0.8)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

fig.text(0.055, 0.975, "In 2025 electric cars passed half of new sales in eight markets",
         fontsize=15, weight="bold", color="#1A1A1A")
fig.text(0.055, 0.955,
         f"Blue: 50% or more. Orange: below 10%. Grey: in between. {len(s25)} markets with 2025 data.",
         fontsize=9.5, color="#5A6672")
fig.subplots_adjust(left=0.215, right=0.95, top=0.935, bottom=0.055)
fig.savefig("figures/fig2_share_2025.png", dpi=200)
plt.close(fig)

print("markets:", wide.shape[1], "| rows:", len(df), "| years:",
      int(wide.index.min()), "-", int(wide.index.max()))
print("reached 10%:", len(t10), "| still below 10%:",
      len(gaps) - len(t10), "| never passed 1%:", wide.shape[1] - len(gaps))
print("years 1%%->10%%  min %d  median %.0f  max %d" % (t10.min(), t10.median(), t10.max()))
print("distribution:", t10.value_counts().sort_index().to_dict())
print("2025 n=%d | >=50%%: %d | <10%%: %d | <5%%: %d" %
      (len(s25), (s25 >= 50).sum(), (s25 < 10).sum(), (s25 < 5).sum()))
print("unweighted mean of markets: %.1f | world (all sales): %.1f" %
      (s25.mean(), world.loc[2025]))
print("fastest:", list(t10[t10 == t10.min()].index))
print("slowest:", list(t10[t10 == t10.max()].index))
print(gaps.sort_values("years_to_10pct").to_string())
