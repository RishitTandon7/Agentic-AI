# Reproducibility Checklist
## LLM as Judge - IEEE A* Conference Submission

This checklist ensures the research artifact meets reproducibility standards.

## ✅ Environment Setup

- [ ] **Ollama Installation**
  - Version: `ollama --version`
  - Llama 3.2 model pulled: `ollama list | grep llama3.2`

- [ ] **Python Environment**
  - Python version: `python --version` (≥3.8)
  - Dependencies installed: `pip install -r requirements_llm_judge.txt`

- [ ] **System Resources**
  - Ollama running: `curl http://localhost:11434/api/tags`
  - Sufficient RAM: 8GB minimum recommended

## ✅ Code Verification

- [ ] **Unit Tests Pass**
  ```bash
  python test_llm_judge.py
  ```
  Expected: All 8 tests pass

- [ ] **Determinism Verified**
  ```bash
  python -c "from llm_judge_pipeline import verify_determinism; \
  verify_determinism('Test laptop', 'Good reviews', num_runs=3)"
  ```
  Expected: Variance = 0.0 (after LLM extraction)

- [ ] **Example Scripts Run**
  ```bash
  python example_usage.py
  ```
  Expected: All 3 examples complete without errors

## ✅ Architectural Verification

- [ ] **Layer 1: Extraction**
  - File: `llm_judge_extraction.py`
  - Constraint: NO scoring logic present
  - Verification: Grep for forbidden terms
    ```bash
    grep -i "score\|recommend\|good\|bad\|rating" llm_judge_extraction.py | grep -v "# " | grep -v "review_count"
    ```
  - Expected: No matches (excluding comments)

- [ ] **Layer 2: Scoring**
  - File: `llm_judge_scoring.py`
  - Constraint: NO LLM calls
  - Verification: Check for imports
    ```bash
    grep -i "ollama\|llm\|gpt\|claude" llm_judge_scoring.py
    ```
  - Expected: No matches

- [ ] **Layer 3: Aggregation**
  - File: `llm_judge_pipeline.py`
  - Verification: Correct orchestration of layers
  - Expected: Calls extraction → scoring → aggregation in sequence

## ✅ Methodological Correctness

- [ ] **Fixed Matrices**
  - CPU tiers: S=1.00, A=0.85, B=0.70, C=0.50, D=0.30
  - GPU tiers: S=1.00, A=0.90, B=0.75, C=0.55, D=0.35, Integrated=0.20
  - Display tiers: A=1.00, B=0.75, C=0.50
  - Brand: High=1.00, Medium=0.70, Low=0.40

- [ ] **Fixed Formulas**
  - Spec weights sum to 1.0: 0.30+0.30+0.20+0.10+0.10 = 1.0
  - Final weights sum to 1.0: 0.25+0.30+0.20+0.15+0.10 = 1.0
  - Price deviation thresholds: ≤5%, ≤10%, ≤25%, >25%

- [ ] **JSON Schema Validation**
  - All allowed values explicitly defined
  - Sentiment distribution sums to 1.0
  - Null handling for missing data

## ✅ Reproducibility Testing

### Test 1: Same Input → Same Output (Scoring Layer)
```python
from llm_judge_scoring import compute_component_scores

signals = {
    "cpu_tier": "A", "gpu_tier": "B", "ram_gb": 16,
    "storage_gb": 512, "display_tier": "B", "brand_reliability": "Medium",
    "sentiment_distribution": {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
}

results = [compute_component_scores(signals, 1000.0, 1000.0) for _ in range(100)]
assert len(set(str(r) for r in results)) == 1  # All identical
```
- [ ] Test passes

### Test 2: LLM Swappability
```python
# Modify llm_judge_extraction.py to use different model
# Scoring output should remain identical for same extracted signals
```
- [ ] Scoring unchanged when LLM model swapped

### Test 3: Transparency
```python
from llm_judge_scoring import get_score_breakdown

# Generate breakdown for any evaluation
# Verify all intermediate values are exposed
```
- [ ] Full breakdown available
- [ ] All weights visible
- [ ] All formulas traceable

## ✅ Documentation

- [ ] **README Complete**
  - Architecture diagram present
  - Usage examples included
  - Formulas documented
  - Guarantees stated explicitly

- [ ] **Code Comments**
  - All functions documented
  - Parameters explained
  - Return values specified
  - Constraints highlighted (NO LLM, NO scoring, etc.)

## ✅ Research Artifact Standards

- [ ] **Code Quality**
  - No hardcoded magic numbers (all in config)
  - Pure functions (no side effects in scoring layer)
  - Modular design (clear separation of concerns)
  - Error handling (validation, retries)

- [ ] **Testability**
  - Unit tests for all scoring functions
  - Integration tests for pipeline
  - Determinism verification tools
  - Schema validation

- [ ] **Extensibility**
  - Easy to modify weights (config file)
  - Easy to add new tiers (matrices)
  - Easy to swap LLM (single function)
  - Easy to add metrics (new functions)

## ✅ Submission Artifacts

- [ ] Source code files (6 Python files)
- [ ] README documentation
- [ ] Requirements file
- [ ] Test suite
- [ ] This reproducibility checklist
- [ ] Ablation study guide (separate file)

## ✅ Final Verification

Run complete verification script:
```bash
python test_llm_judge.py && \
python example_usage.py && \
echo "✅ ALL CHECKS PASSED - ARTIFACT READY FOR SUBMISSION"
```

## Notes for Reviewers

### How to Verify Reproducibility

1. Install Ollama and pull llama3.2
2. Run: `pip install -r requirements_llm_judge.txt`
3. Run: `python test_llm_judge.py`
4. Run: `python example_usage.py`

### Expected Behavior

- **Deterministic**: Scoring layer produces identical outputs for identical signals
- **Modular**: LLM can be replaced without affecting scoring
- **Transparent**: All formulas and weights are explicit
- **Testable**: Comprehensive test suite validates all components

### Common Issues

1. **Ollama not running**: Start with `ollama serve`
2. **Model not found**: Pull with `ollama pull llama3.2`
3. **Port conflict**: Change `ollama_url` parameter if needed

---

**Artifact Status**: ✅ READY FOR IEEE A* REVIEW

**Last Updated**: 2026-01-30
