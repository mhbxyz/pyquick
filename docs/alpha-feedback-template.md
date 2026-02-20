# Alpha Feedback Template

Use this template when reporting internal alpha feedback.

## Title format

`[alpha][<severity>] <short symptom>`

Examples:

- `[alpha][blocker] pyignite run fails on fresh scaffold`
- `[alpha][medium] dev loop runs full checks too often`

## Severity

- `blocker`: cannot continue primary workflow
- `high`: core workflow degraded significantly
- `medium`: usable but problematic
- `low`: polish/documentation issue

## Report body

```text
### Context
- OS:
- Python version:
- uv version:
- Commit/version under test:

### Command(s) run
<exact commands>

### Expected behavior
<what you expected>

### Actual behavior
<what happened>

### Key output
<paste ERROR/Hint and relevant lines>

### Reproduction
- Reproducible: always / sometimes / once
- Minimal steps:
  1.
  2.
  3.

### Impact
<what this blocks or slows down>

### Suggested improvement (optional)
<if you have one>
```

## Checklist before submitting

- [ ] I included exact command(s)
- [ ] I included error output lines
- [ ] I stated expected vs actual behavior
- [ ] I provided reproducibility details
- [ ] I assigned severity
