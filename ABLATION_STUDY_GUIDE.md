# Ablation Study Guide
## LLM as Judge - IEEE A* Conference Submission

This guide provides systematic approaches for conducting ablation studies on the evaluation system.

## Overview

Ablation studies help answer:
- Which components contribute most to final scores?
- How sensitive is the system to weight changes?
- What is the impact of review confidence scaling?
- How do different LLM models affect extraction accuracy?

## Study 1: Component Weight Ablation

### Objective
Determine the influence of each component on the final score.

### Methodology

```python
from llm_judge_pipeline import evaluate_product
from llm_judge_config import FINAL_WEIGHTS

# Baseline evaluation
baseline = evaluate_product(...)

# Ablate each component by setting its weight to 0
ablation_results = {}

for component in ['price', 'specs', 'brand', 'reviews', 'marketplace']:
    # Modify weights (normalize remaining)
    modified_weights = FINAL_WEIGHTS.copy()
    ablated_weight = modified_weights.pop(component)
    total = sum(modified_weights.values())
    modified_weights = {k: v/total for k, v in modified_weights.items()}
    
    # Re-run with modified weights
    # (Requires temporary modification of FINAL_WEIGHTS in config)
    result = evaluate_product(...)
    
    ablation_results[component] = {
        'original_weight': ablated_weight,
        'score_change': result['final_score'] - baseline['final_score']
    }
```

### Analysis
- Calculate relative importance: `|score_change| / original_weight`
- Rank components by impact
- Visualize with bar chart

---

## Study 2: Specification Subcomponent Ablation

### Objective
Determine which hardware specs matter most.

### Methodology

```python
from llm_judge_config import SPEC_WEIGHTS

# Test with each spec component at min/max
components = ['cpu', 'gpu', 'ram', 'storage', 'display']
ranges = {
    'cpu': ['D', 'S'],
    'gpu': ['Integrated', 'S'],
    'ram': [4, 64],
    'storage': [128, 2048],
    'display': ['C', 'A']
}

results = []
for component in components:
    for value in [ranges[component][0], ranges[component][1]]:
        signals = baseline_signals.copy()
        signals[component + '_tier' if component in ['cpu','gpu','display'] else component + '_gb'] = value
        
        score = compute_component_scores(signals)
        results.append({
            'component': component,
            'value': value,
            'spec_score': score['specs']
        })
```

### Analysis
- Calculate score range per component: `max - min`
- Multiply by spec weight to get absolute impact
- Compare against spec weight allocation

---

## Study 3: Review Confidence Scaling Impact

### Objective
Evaluate the effect of confidence scaling on review scores.

### Methodology

```python
test_cases = [
    {'review_count': 5, 'positive': 0.8},
    {'review_count': 50, 'positive': 0.8},
    {'review_count': 500, 'positive': 0.8},
    {'review_count': 5000, 'positive': 0.8},
]

comparison = []
for case in test_cases:
    sentiment = {'positive': case['positive'], 'neutral': 0.1, 'negative': 0.1}
    
    score_no_scaling = compute_review_score(sentiment, use_confidence_scaling=False)
    score_with_scaling = compute_review_score(
        sentiment, 
        review_count=case['review_count'],
        use_confidence_scaling=True
    )
    
    comparison.append({
        'review_count': case['review_count'],
        'without_scaling': score_no_scaling,
        'with_scaling': score_with_scaling,
        'difference': score_with_scaling - score_no_scaling
    })
```

### Analysis
- Plot scaling factor vs. review count
- Determine threshold where confidence reaches 1.0
- Assess impact on final scores

---

## Study 4: Price Sensitivity Analysis

### Objective
Understand how price deviations affect final scores.

### Methodology

```python
market_price = 1000.0
deviations = [-0.30, -0.25, -0.10, -0.05, 0.0, 0.05, 0.10, 0.25, 0.30]

price_sensitivity = []
for dev in deviations:
    actual_price = market_price * (1 + dev)
    price_score = compute_price_score(actual_price, market_price)
    
    # Insert into full evaluation
    result = evaluate_product(..., actual_price=actual_price, market_price=market_price)
    
    price_sensitivity.append({
        'deviation_pct': dev * 100,
        'price_score': price_score,
        'final_score': result['final_score']
    })
```

### Analysis
- Plot price deviation vs. final score
- Identify optimal price range
- Calculate elasticity: `% change in final score / % change in price`

---

## Study 5: LLM Model Comparison

### Objective
Compare extraction accuracy across different LLM models.

### Methodology

```python
models = ['llama3.2', 'llama2', 'mistral', 'phi']  # Available Ollama models

extraction_comparison = []
for model in models:
    try:
        result = evaluate_product(
            ...,
            ollama_model=model
        )
        
        extraction_comparison.append({
            'model': model,
            'signals': result['signals'],
            'final_score': result['final_score']
        })
    except Exception as e:
        print(f"Model {model} failed: {e}")
```

### Analysis
- Compare extracted tiers across models
- Check for consensus on categorical values
- Measure variance in final scores (due to extraction differences)
- **Important**: Scoring layer remains unchanged!

---

## Study 6: Tier Granularity Impact

### Objective
Assess whether 5-tier (S/A/B/C/D) vs. 3-tier (High/Mid/Low) affects discrimination.

### Methodology

```python
# Collapse S/A → High, B → Mid, C/D → Low
def collapse_tiers(tier_5):
    mapping = {'S': 'High', 'A': 'High', 'B': 'Mid', 'C': 'Low', 'D': 'Low'}
    return mapping.get(tier_5, tier_5)

# Define 3-tier scoring matrix
TIER_3_SCORES = {'High': 1.0, 'Mid': 0.6, 'Low': 0.2}

# Compare results
products = [...]  # Multiple test products
comparison = []

for product in products:
    # 5-tier evaluation
    result_5tier = evaluate_product(...)
    
    # 3-tier evaluation (modify scoring in config temporarily)
    # ... (collapse tiers and re-score)
    
    comparison.append({
        'product': product,
        'score_5tier': result_5tier['final_score'],
        'score_3tier': result_3tier['final_score'],
        'difference': abs(result_5tier['final_score'] - result_3tier['final_score'])
    })
```

### Analysis
- Calculate correlation between 5-tier and 3-tier scores
- Measure loss of discrimination (variance reduction)
- Check if rankings change

---

## Study 7: Sentiment Distribution Simplification

### Objective
Test if binary (positive/negative) is sufficient vs. ternary (positive/neutral/negative).

### Methodology

```python
# Original: positive/neutral/negative
# Simplified: merge neutral → split 50/50 into positive and negative

sentiment_original = {'positive': 0.6, 'neutral': 0.3, 'negative': 0.1}
sentiment_binary = {
    'positive': 0.6 + 0.15,  # 0.75
    'neutral': 0.0,
    'negative': 0.1 + 0.15   # 0.25
}

score_original = compute_review_score(sentiment_original)
score_binary = compute_review_score(sentiment_binary)
```

### Analysis
- Compare across multiple products
- Calculate score differences
- Assess if simplification is justified

---

## Study 8: Weight Optimization (Sensitivity)

### Objective
Find optimal weight configuration through grid search.

### Methodology

```python
import itertools
import numpy as np

# Define weight ranges (must sum to 1.0)
# Example: price weight from 0.15 to 0.35 (step 0.05)
weight_ranges = {
    'price': np.arange(0.15, 0.40, 0.05),
    'specs': [1.0]  # Fixed, others adjust
}

# Generate all valid combinations
# (Skip invalid combinations that don't sum to 1.0)

# Evaluate on ground truth dataset
best_config = None
best_f1 = 0

for weight_combo in valid_combinations:
    # Apply weights temporarily
    # Evaluate on test set
    # Calculate precision, recall, F1
    
    if f1 > best_f1:
        best_f1 = f1
        best_config = weight_combo
```

### Analysis
- Heatmap of weight configurations vs. F1 score
- Test statistical significance of improvements
- Report optimal configuration

---

## Statistical Testing

For all ablation studies, include:

1. **Baseline Comparison**
   ```python
   from scipy.stats import ttest_rel
   t_stat, p_value = ttest_rel(baseline_scores, ablated_scores)
   ```

2. **Effect Size**
   ```python
   cohen_d = (mean(ablated) - mean(baseline)) / pooled_std
   ```

3. **Confidence Intervals**
   ```python
   from scipy.stats import bootstrap
   ci = bootstrap((scores,), np.mean, confidence_level=0.95)
   ```

---

## Reporting Template

```markdown
### Ablation Study: [Component Name]

**Hypothesis**: Removing/modifying [component] will [expected effect].

**Setup**:
- Dataset: [N products]
- Baseline: [configuration]
- Variation: [what was changed]

**Results**:
| Metric | Baseline | Ablated | Δ | p-value |
|--------|----------|---------|---|---------|
| F1     | X.XX     | X.XX    | ±X.XX | 0.XXX |

**Conclusion**: [Component] contributes [X%] to final score. [Accept/Reject hypothesis].
```

---

## Validation Datasets

For meaningful ablation studies, prepare:

1. **Ground Truth Dataset** (100+ products with human labels)
2. **Diverse Price Ranges** (budget, mid-range, premium)
3. **Varied Spec Configurations** (balanced, GPU-heavy, CPU-heavy)
4. **Review Distributions** (positive, negative, mixed, few/many reviews)

---

## Reproducibility

All ablation scripts should:
- [ ] Use fixed random seeds (if any randomness)
- [ ] Log all parameter changes
- [ ] Save results to JSON/CSV
- [ ] Include visualization code
- [ ] Be runnable with single command

---

**Remember**: The goal is to demonstrate that:
1. Each component contributes meaningfully
2. The system is robust to reasonable variations
3. Design choices are justified by data

Good luck with your IEEE A* submission!
