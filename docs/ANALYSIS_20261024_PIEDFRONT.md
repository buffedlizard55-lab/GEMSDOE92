# GEMSDOE32 (`0.2778`) Forensic Analysis & `PIEDFRONT` Evaluation Report (2026-10-24)

**Branch:** `arena/8bf37367-gemsdoe92`  
**Primary artefact:** `docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`  
**Audit receipt:** `docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-audit.json`  
**Run card:** `evidence/piedfront_run_card.json` / `docs/downloads/piedfront_run_card.json`  
**Proxy audit:** `evidence/piedfront_proxy_audit.json`  
**Public witness receipt:** `evidence/piedfront_public_registry_witness17.json`

---

## 1. Why `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (`GEMSDOE32`, `0.2778`) Scored Highest Among Listed GEMSDOE Sites

In the DrivenData Geothermal Exploration Machine-learning (GEMS) Fault Detection challenge, submissions are scored by the organizer's Distance-Tolerant IoU (`DTI`, `alpha=0.2`, `beta=0.8`, 300 m / 3 px triangular distance kernel $K$, pixel-exact masking of the visible `existing_faults.tif` catalogue $M$):

$$\mathrm{DTI}(S, G_{\text{hid}}) = \frac{\mathrm{tp}_w}{\mathrm{tp}_w + 0.2\,\mathrm{fp}_w + 0.8\,\mathrm{fn}_w}$$

where $S' = S \odot (1 - M)$ and $G' = G_{\text{hid}} \odot (1 - M)$.

Line-by-line byte and geometric verification of the lineage chain stored in `.cache/gems_inputs/lineage/` (`registry/data_manifest.json`) establishes why `R0` (`h33-h33-2-b2`, `GEMSDOE32`) beat every earlier GEMSDOE submission in its lineage:

| Step | Lineage File | Dots ($S$) | Verified Operation & Metric Consequence |
|---|---|---:|---|
| 1 | `h19_5.tif` | `59,666` | Multi-band hydrothermal/structural skeleton inside the `5,167,373`-px valid footprint (`10.02%` of footprint within its 3-px kernel halo). |
| 2 | `d28.tif` | `39,710` | Euclidean $2.8\text{ px}$ minimum-spacing thinning of `h19_5.tif`. Two unit dots closer than $2.8\text{ px}$ clip at $1.0$ inside $\min(1, K * S')$ where their 300 m kernels overlap, paying double false-positive penalty ($0.2\,\mathrm{fp}_w$) for sub-linear $\mathrm{tp}_w$ gain. `d28` eliminates self-clipping while preserving $94.7\%$ of `h19_5`'s 3-px halo area (`509,759` vs `517,770` px). |
| 3 | `parent_R0_zeros.tif` (`h33-h33-2-b2`) | `37,654` | Prunes the `2,056` dots of `d28.tif` at $d_{\text{cat}} \le 2.0\text{ px}$ (`111` directly on `existing_faults.tif`, muted to zero by $1-M$, plus `1,945` at $0 < d_{\text{cat}} \le 2.0\text{ px}$ whose kernels overlap the already-mapped traces), while **retaining `2,027` collar dots at $2.0 < d_{\text{cat}} \le 3.0\text{ px}$** whose 300 m halos reach across catalogue trace gaps, tip terminations, and unmapped splays. |

### Why Surpassing `0.2778` / `0.3195` / `0.4413` Requires Both Skeleton Hole Repair and Piedmont Range-Front Discovery

Our diagnostic audit uncovered two structural defects in prior attempts to improve on `R0`:

1. **Unrepaired post-`b2` holes on `H19-5` (NEXT_STEPS #3):** Because `R0` deleted `2,056` dots at $d_{\text{cat}} \le 2.0\text{ px}$ *after* `d28` thinning without re-running $2.8\text{ px}$ greedy selection on the surviving $d_{\text{cat}} > 2.0\text{ px}$ skeleton, `R0` left **`794` spacing-legal `H19-5` pixels** ($d_{\text{R0}} > 2.8\text{ px}$, $d_{\text{cat}} > 2.0\text{ px}$), including **`593` pixels in the high-leverage $2.0 < d_{\text{cat}} \le 3.0\text{ px}$ band**, completely uncovered.
2. **Mountain-core topographic bias in prior off-skeleton lanes:** Prior locally-unique off-skeleton lanes (`BREAKLINE f45` `0.004861`, `SCARPPOL f45` `0.005315`, `STRAINBREAK f60` `0.005487`, `ANASIG f45` `0.004967`, `SPRINGALIGN f33` `0.004865`) replaced $33\text{--}60\%$ of `R0` with off-skeleton dots ($d_{\text{H19}} > 3.0\text{ px}$) to satisfy the local $\le 70\%$ 3-px overlap rule, but every single one dropped `HOLDOUT-DTI` below `RELIEF p10` (`0.006045`). Why? In `BREAKLINE f45`, $L_{\text{raw}} = \text{pct\_rank}(\|\nabla(\text{det\_elev\_slope})\|) \times \text{coh}(\text{det\_elev})$ is unnormalized by background slope, so **`74.8%` (`12,673 / 16,944`) of its off-skeleton dots landed in the highest-elevation range-interior tercile** (`det_elev >= 38.76 m`) on steep mountain crags and ridge crests, and only `23.1%` landed in the piedmont (`-29.40 <= det_elev < 38.76 m`). By contrast, `RELIEF p10` (`0.006045`) succeeded on holdout because it moved dots *into* the piedmont transition (`41.4%` piedmont vs `R0` `33.1%`), where active Basin-and-Range range-front normal faults and concealed geothermal step-overs sit at the bedrock–basin contact.

---

## 2. The `PIEDFRONT` Mechanism (`gems/piedfront.py`, `scripts/build_piedfront_variants.py`)

`PIEDFRONT` (pre-registered Rank-1 hypothesis in `docs/HYPOTHESES_20261024_PIEDFRONT.md`) resolves both defects simultaneously using four manifest-pinned bands (`Band 5 iso_grav_anom_slope`, `Band 12 det_elev`, `Band 15 depth_to_base_surf`, `Band 19 det_elev_slope`):

$$R_{\text{scarp}}(x) = \operatorname{pct\_rank}\!\left(\frac{\|\nabla\,\text{det\_elev\_slope}(x)\|}{\max(\text{det\_elev\_slope}(x), 0) + 2.0^\circ}\right) \times \operatorname{coh}_{\sigma_g=1.5,\sigma_t=4.0}(\text{det\_elev})(x)$$

$$W_{\text{pied}}(x) = \exp\!\left(-\frac{1}{2}\left(\frac{\operatorname{pct\_rank}(\text{det\_elev})(x) - 0.45}{0.28}\right)^2\right) \exp\!\left(-\frac{1}{2}\left(\frac{\operatorname{pct\_rank}(\text{depth\_to\_base})(x) - 0.50}{0.35}\right)^2\right) \left(0.50 + 0.50\,\operatorname{pct\_rank}(\text{iso\_grav\_anom\_slope})(x)\right)$$

$$S_{\text{raw}}(x) = R_{\text{scarp}}(x)\,W_{\text{pied}}(x), \qquad S_{\text{pct}}(x) = \operatorname{pct\_rank}(S_{\text{raw}}(x))$$

At fixed $S = 37,654$ unit-mass dots ($d_{\text{cat}} > 2.0\text{ px}$):
1. **On-skeleton piedmont hole repair ($N_{\text{skel}} = 37,654 - N_{\text{far}}$ dots on `H19-5`):** Keep the top $N_{\text{skel}} - 4,000$ dots of `R0` ranked by $w_{\text{pf}} = (0.30 + 0.70\,S_{\text{pct}})\,W_{\text{pied}}$ and refill $4,000$ piedmont `H19-5` holes (`h19 & is_piedmont & d_cat > 2.0 & ~R0`) via exact marginal expected-DTI greedy (`select_exact_marginal_dti_add`).
2. **Off-skeleton piedmont range-front discovery ($N_{\text{far}} \in \{13,179,\,15,062,\,16,944\}$ dots, $f_{\text{far}} \in \{0.35, 0.40, 0.45\}$):** Place $N_{\text{far}}$ spaced-top dots ($2.8\text{ px}$ strict floor) on $S_{\text{raw}}$ strictly $>3.0\text{ px}$ from `H19-5`, $>2.0\text{ px}$ from `existing_faults.tif`, and $>3.0\text{ px}$ from the off-skeleton dot sets of all five prior off-skeleton lanes (`BREAKLINE f45`, `SCARPPOL f45`, `STRAINBREAK f60`, `ANASIG f45`, `SPRINGALIGN f33`).

---

## 3. Evaluation Results (`evidence/piedfront_proxy_audit.json`)

### 3.1 Pooled `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 Withheld Positives, 8 Folds, 1,000 Paired Cluster Draws)

| Arm / Variant | Dots | Piedmont Dots (%) | Far Piedmont (%) | `HOLDOUT-DTI` `[95% CI]` | Paired $\Delta$ vs `R0` `[95% CI]` | Paired $\Delta$ vs `RELIEF p10` `[95% CI]` | `SGMC` Bedrock `PROXY` | Fixed-Cat `DIAGNOSTIC` | Worst Local 3-px Overlap | Worst Local `|φ|` |
|---|---:|---:|---:|---|---|---|---|---|---:|---:|
| **`PIEDFRONT f35Ptop` (primary)** | `37,654` | **`73.9%`** | **`78.7%`** | **`0.006425 [0.005375, 0.007479]`** | **`+0.002418 [+0.001538, +0.003255]`** | **`+0.000379 [-0.000257, +0.001066]`** | `0.059993` | `0.009569` | **`0.649997` (`h19_5.tif`)** | **`0.585871`** |
| `PIEDFRONT f40Ptop` | `37,654` | `75.7%` | `78.0%` | `0.006402 [0.005341, 0.007461]` | `+0.002396 [+0.001493, +0.003254]` | `+0.000357 [-0.000297, +0.001060]` | `0.058179` | `0.009382` | `0.599989` (`h19_5.tif`) | `0.528941` |
| `PIEDFRONT f45Ptop` | `37,654` | `77.0%` | `77.2%` | `0.006137 [0.005092, 0.007200]` | `+0.002131 [+0.001207, +0.003009]` | `+0.000092 [-0.000592, +0.000834]` | `0.055900` | `0.009052` | `0.550008` (`h19_5.tif`) | `0.469979` |
| `RELIEF p10` (prior holdout best, local-dup) | `37,654` | `41.4%` | — | `0.006045 [0.005187, 0.006927]` | `+0.002039 [+0.001614, +0.002446]` | `0.000000` | `0.087245` | `0.009791` | `0.994290` (`R0`, DUP) | `0.899895` |
| `STRAINBREAK f60s2i` (prior unique best) | `37,654` | — | — | `0.005487 [0.004522, 0.006430]` | `+0.001481 [+0.000399, +0.002530]` | `-0.000558 [-0.001577, +0.000431]` | `0.105162` | `0.008561` | `0.400011` (`R0`) | `0.400710` |
| `SCARPPOL f45Stop` | `37,654` | — | — | `0.005315 [0.004352, 0.006262]` | `+0.001309 [+0.000180, +0.002421]` | `-0.000730 [-0.001789, +0.000280]` | `0.106694` | `0.008657` | `0.550008` (`h19_5.tif`) | `0.506779` |
| `ANASIG f45Atop` | `37,654` | — | — | `0.004967 [0.004127, 0.005882]` | `+0.000961 [-0.000008, +0.001859]` | `-0.001078 [-0.001993, -0.000232]` | `0.072578` | `0.008090` | `0.550008` (`h19_5.tif`) | `0.506667` |
| `SPRINGALIGN f33Ctop` | `37,654` | — | — | `0.004865 [0.004114, 0.005638]` | `+0.000859 [+0.000192, +0.001465]` | `-0.001180 [-0.001922, -0.000440]` | `0.077160` | `0.008620` | `0.669995` (`h19_5.tif`) | `0.629032` |
| `BREAKLINE f45Ltop` | `37,654` | `23.1%` (far) | `23.1%` | `0.004861 [0.004032, 0.005822]` | `+0.000854 [-0.000109, +0.001776]` | `-0.001185 [-0.002109, -0.000264]` | `0.126105` | `0.007746` | `0.550008` (`h19_5.tif`) | `0.506521` |
| `R0` (`h33-h33-2-b2`, parent) | `37,654` | `33.1%` | — | `0.004006 [0.003424, 0.004690]` | `0.000000` | `-0.002039 [-0.002446, -0.001614]` | `0.096060` | `0.006709` | — | — |

**Key findings:**
- **All three `PIEDFRONT` doses (`0.006425`, `0.006402`, `0.006137`) exceed both `R0` (`0.004006`) and the prior non-collar holdout best `RELIEF p10` (`0.006045`) in point estimate on `gems57-pooled-hide-v2`**, while satisfying every local registry uniqueness threshold ($\le 0.6500$ 3-px forward overlap vs $\le 0.70$ limit; $\le 0.5859$ $|\phi|$ vs $\le 0.90$ limit across all 29 unique local registry rasters).
- **`PIEDFRONT f35Ptop` (`0.006425`) beats `R0` by `+0.002418` (`+60.4%`, paired 95% CI `[+0.001538, +0.003255]`, strictly $>0$) and beats `BREAKLINE f45` (`0.004861`) by `+0.001564` (`+32.2%`, paired 95% CI `[+0.000471, +0.002607]`, strictly $>0$).**
- **Complementarity of the two local instruments (`HOLDOUT-DTI` vs `SGMC` bedrock `PROXY`):** Moving off-skeleton dots out of mountain-core pre-Quaternary bedrock (`det_elev >= 38.76 m`, where `BREAKLINE f45` placed `74.8%` of its far dots and scored `0.126105` on `SGMC`) into the piedmont range-front transition (`78.7%` of `f35Ptop` far dots, `73.9%` overall) raises `HOLDOUT-DTI` from `0.004861` (`BREAKLINE f45`) to `0.006425` (`PIEDFRONT f35Ptop`), while lowering `SGMC` bedrock fault recovery from `0.096060` (`R0`) to `0.059993` (`f35Ptop`).

### 3.2 Single-Feature Leakage Canaries (`gems57-pooled-hide-v2`)

| Feature | Raw AUC | Symmetric AUC ($\max(\text{AUC}, 1-\text{AUC})$) | Gate ($\le 0.90$) |
|---|---:|---:|---|
| `training_band_5_iso_grav_anom_slope` | `0.551113` | `0.551113` | PASS |
| `training_band_12_det_elev` | `0.497553` | `0.502447` | PASS |
| `training_band_15_depth_to_base_surf` | `0.485138` | `0.514862` | PASS |
| `training_band_19_det_elev_slope` | `0.446860` | `0.553140` | PASS |
| `piedfront_rel_break_pct` | `0.579356` | `0.579356` | PASS |
| `piedfront_R_scarp` | `0.620797` | `0.620797` | PASS |
| `piedfront_W_pied` | `0.582369` | `0.582369` | PASS |
| `piedfront_S_pct_main` | `0.639112` | **`0.639112`** | PASS |

### 3.3 Local & Public Registry Uniqueness (`REGISTRY-MEASUREMENT`)

- **Local registry (29 unique local rasters in `data/`, `releases/`, `docs/downloads/`):**
  - Pre-placement surface (`.cache/piedfront_surface.tif`): worst `|Spearman ρ|` = `0.127084` (`h19_5.tif`, $\le 0.90$ PASS); worst spaced-top-37,654 3-px forward overlap = `0.434907` (`h19_5.tif`, $\le 0.70$ PASS).
  - Final dots `f35Ptop`: worst 3-px forward overlap = `0.649997` (`h19_5.tif`, $\le 0.70$ PASS; vs `R0` `0.641047`; vs `SPRINGALIGN f33` `0.551575`; vs `BREAKLINE f45` `0.471212`; vs `ANASIG f45` `0.470441`; vs `STRAINBREAK f60` `0.369470`); worst `|φ|` = `0.585871` (`RELIEFp10`, $\le 0.90$ PASS).
- **Public witness (`17GEMSDOE`, `evidence/piedfront_public_registry_witness17.json`):**
  - Pre-placement surface worst `|Spearman ρ|` vs `17GEMSDOE_E-proba-multiscale` = `0.411790` ($\le 0.90$), final dots worst `|Spearman ρ|` = `0.052160` ($\le 0.90$), but forward 3-px overlap = `1.0` (`100%`) because `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` has `5,167,373` positive pixels (every pixel in the competition footprint).

### 3.4 Verdict: `negative` (`OK TO DOWNLOAD` for research; `NOT CLEARED` for a live weekly submission slot)

Per our pre-registered decision rule (`docs/HYPOTHESES_20261024_PIEDFRONT.md`):
1. Although `PIEDFRONT f35Ptop` (`0.006425`) is the **highest-scoring locally-unique candidate on `HOLDOUT-DTI` in the repository** and exceeds `RELIEF p10` (`0.006045`) in point estimate, its paired 95% bootstrap CI against `RELIEF p10` (`[-0.000257, +0.001066]`) includes zero and its `SGMC` bedrock fault proxy (`0.059993`) is below `R0` (`0.096060`).
2. Independently, the public dense-surface witness (`17GEMSDOE E-proba`) triggers the literal $>70\%$ forward-overlap rule (`submission_eligible: false`) until an operator policy decision distinguishes dense continuous probability surfaces from sparse dot clouds.
