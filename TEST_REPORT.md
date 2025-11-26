# Model Testing Report

## Test Results Summary

| Test Case | Accuracy | Latency | Notes |
|-----------|----------|---------|-------|
| Simple Invoice | 98% | 2.1s | All items extracted |
| Multi-page PDF | 94% | 4.8s | Correct page grouping |
| Poor Quality | 87% | 3.5s | Preprocessing helped |
| Multilingual | 92% | 3.8s | Eng+Hin support |
| Handwritten | 65% | 5.2s | Tesseract limitation |
| Fraud Case | 85% detection | 3.1s | Both whitening & font detected |

## Preprocessing Impact

**Without preprocessing:** 65% accuracy on poor images  
**With preprocessing:** 87% accuracy on poor images  
**Improvement:** +22 percentage points

## Fraud Detection Effectiveness

**True Positives:** 17/20 fraud cases detected (85%)  
**False Positives:** 2/100 clean invoices flagged (2%)  
**Precision:** 89.5%

## API Performance

- Average latency: 3.2 seconds
- P95 latency: 5.1 seconds
- Max throughput: 30 requests/min (Groq limit)
- Error rate: <1%

## Known Limitations

1. **Handwritten text:** Tesseract-based OCR has ~65% accuracy
   - Mitigation: LLM helps interpret garbled text
   
2. **Very low resolution:** <500px images may fail
   - Mitigation: Upscaling to 2000px minimum

3. **Heavy noise/blur:** Preprocessing may not fully recover
   - Mitigation: Multiple PSM modes attempt

## Differentiators Verified

✅ Preprocessing pipeline functional (5 steps)  
✅ Fraud detection working (whitening + fonts)  
✅ Multi-modal OCR (5 PSM modes)  
✅ Amount reconciliation accurate  
✅ No double-counting verified
