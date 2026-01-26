# Identification Strategy

## Research Question

**Estimand:** What is the causal effect of Google's AI Overviews rollout on organic website traffic?

---

## Setting

### Treatment
Introduction of AI Overviews (AI-generated summaries at the top of Google Search results) that may reduce click-through rates to websites.

### Rollout
Staggered across countries and time (May 2024 onwards):

| Country | Treatment Date | Wave | Role |
|---------|---------------|------|------|
| **United States** | May 14, 2024 | Wave 1 | Early-treated cohort |
| **Great Britain** | August 28, 2024 | Wave 2 | Late-treated cohort |
| **Ireland** | Never | — | Pure control group |

### Units
Websites (domains) indexed by Google, focusing on social media platforms and news sites.

### Outcome
Weekly organic traffic visits.

---

## Identification Challenges

### 1. Selection Bias
Sites affected by AI Overviews may differ systematically from unaffected sites (e.g., content type, search ranking, query intent).

**Mitigation:**
- Use within-site variation (site fixed effects)
- Compare treated vs. not-yet-treated cohorts within the same platform category

### 2. Time-Varying Confounders
Seasonal trends, algorithm updates, or competitor behavior could coincide with rollout.

**Mitigation:**
- Include time fixed effects
- Use staggered DiD with heterogeneity-robust estimators (avoid biased two-way FE)
- Compare countries with similar traffic patterns and search behavior

### 3. Anticipation Effects
Sites may change content/SEO strategy in anticipation of AI Overviews (e.g., adapting to be more "AI-friendly").

**Check:** Event study with leads; anticipation would show pre-treatment effects.

---

## Estimation Strategy

### Staggered Difference-in-Differences

We adopt modern staggered DiD approaches that avoid biases from heterogeneous treatment effects:

#### Callaway and Sant'Anna (2021)
- Compute group-time average treatment effects \( ATT(g,t) \) for each cohort \( g \) at time \( t \)
- Use only valid comparisons (not-yet-treated or never-treated as controls)
- Aggregate with appropriate weights
- Doubly-robust estimator robust to misspecification

**Advantages over TWFE:**
- Avoids "forbidden comparisons" (using already-treated units as controls)
- Allows effect heterogeneity across cohorts and time
- Valid inference via bootstrap

### Specification

For site \( i \) in cohort \( g \) at time \( t \):

\[
Y_{it} = \alpha_i + \lambda_t + \sum_{e \neq -1} \beta_e \cdot \mathbb{1}[t - G_i = e] + \epsilon_{it}
\]

where:
- \( \alpha_i \): Site fixed effects
- \( \lambda_t \): Time fixed effects
- \( G_i \): Treatment date for site \( i \)
- \( e \): Event time (periods relative to treatment)
- \( \beta_e \): Dynamic treatment effect at event time \( e \)

---

## Key Assumptions

### 1. Parallel Trends
**Assumption:** Absent treatment, treated and control sites would follow parallel traffic trends.

**Test:**
- Visual inspection of pre-treatment trends
- (Planned) Formal test: leads (\( e < 0 \)) should be statistically zero

**Plausibility:**
- US, GB, IE have similar internet penetration, search behavior, and platform usage
- Social media platforms operate globally with similar content strategies

### 2. No Spillovers
**Assumption:** Treatment of one site does not affect control sites.

**Concern:** If AI Overviews shift traffic between sites (zero-sum), estimates capture relative, not absolute, effects.

**Interpretation:** Estimates identify the *competitive effect* of AI Overviews (treated sites' traffic loss relative to controls).

### 3. Stable Unit Treatment Value Assumption (SUTVA)
**Assumption:** Treatment effect for site \( i \) does not depend on treatment status of other sites.

**Concern:** Relaxed by focusing on within-platform comparisons (YouTube US vs. YouTube GB).

---

## Robustness Checks

### Planned
- [ ] **Alternative control groups:** Never-treated only vs. not-yet-treated
- [ ] **Clustering:** Standard errors clustered at country or platform level
- [ ] **Sample restrictions:** Exclude sites with anomalous traffic spikes/drops
- [ ] **Placebo tests:** Assign fake treatment dates in pre-period; should find null effects
- [ ] **Functional form:** Levels vs. log vs. inverse hyperbolic sine (IHS)
- [ ] **Pre-trend testing:** Formal joint test of lead coefficients

### Sensitivity Analysis
- **Heterogeneity by site category:** News vs. e-commerce vs. social media
- **Heterogeneity by traffic channel:** Search vs. direct vs. referral (may show mechanism)
- **Heterogeneity by treatment intensity:** Sites with high vs. low AI Overview exposure

---

## Expected Findings

If AI Overviews reduce click-through to websites (by answering queries directly), we expect:

1. **Negative ATT:** \( \beta_e < 0 \) for \( e \geq 0 \) (post-treatment periods)
2. **Larger effects for informational queries:** News/reference sites more affected than transactional (e-commerce)
3. **Channel composition shift:** Search traffic declines more than direct/referral
4. **Persistent effects:** No reversion to baseline (structural change in search behavior)

---

## Data Requirements

### Traffic Data
- Weekly/monthly panel
- Columns: `domain`, `country`, `date`, `all_traffic_visits`, `channel` (for heterogeneity)

### Treatment Timing
- AI Overviews rollout dates by country (from Google announcements)
- Validation: Cross-reference with Google blog posts and press releases

### Covariates (for heterogeneity)
- Site category (social media, news, e-commerce)
- Language (for language-specific rollouts)
- Initial traffic rank (to test effect heterogeneity by prominence)

---

## Limitations

1. **External validity:** Effects may differ for long-tail sites not in our sample
2. **Treatment definition:** Binary treatment (AI Overviews on/off) ignores intensity variation (% of queries with overviews)
3. **Mechanism:** Cannot directly observe user click behavior; infer from traffic aggregates

---

## References

**Methodology:**
- Callaway, B., & Sant'Anna, P. H. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.
