# Wisteria JSON Testing Directory

This directory is for testing Biomni integration with your Wisteria JSON files.

## How to Use

1. **Copy your JSON files** to this directory
2. **Run the test script**: `python test_wisteria_json_biomni.py`
3. **Review results** in the generated `wisteria_biomni_test_results.json`

## Supported JSON Formats

The tester supports various JSON structures commonly used in research:

### Format 1: Hypothesis Array
```json
{
  "hypotheses": [
    {
      "title": "CRISPR-Cas9 Gene Editing for Sickle Cell Disease",
      "content": "CRISPR-Cas9 can correct HBB gene mutations to treat sickle cell disease",
      "research_area": "gene_therapy"
    }
  ]
}
```

### Format 2: Single Hypothesis
```json
{
  "hypothesis": {
    "title": "Tau Protein Aggregation in Alzheimer's",
    "description": "Targeting tau protein aggregation can slow AD progression",
    "domain": "neuroscience"
  }
}
```

### Format 3: Research Results
```json
{
  "results": [
    {
      "research_question": "Can immunotherapy treat cancer?",
      "hypothesis_text": "CAR-T cells can eliminate B-cell lymphomas",
      "confidence": 0.8
    }
  ]
}
```

### Format 4: Simple Text
```json
{
  "content": "Mitochondrial dysfunction contributes to aging through oxidative stress",
  "title": "Mitochondrial Aging Hypothesis",
  "source": "research_paper"
}
```

## What the Tester Does

1. **Discovers** all JSON files in this directory
2. **Extracts** hypotheses using intelligent parsing
3. **Verifies** each hypothesis with Modern Biomni
4. **Analyzes** biological plausibility and confidence
5. **Suggests** experiments and evidence
6. **Generates** comprehensive reports

## Output

The tester creates:
- **Console output**: Real-time progress and summary
- **JSON results file**: Complete verification data
- **Biomni analysis**: Evidence, experiments, confidence scores

## Example Files

See the example files in this directory to understand the expected formats.
