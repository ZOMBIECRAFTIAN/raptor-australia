# Dataset Leakage Audit

Images audited: **1992**
Exact duplicate cross-split groups: **0**
Source-ID cross-split groups: **0**
Near-duplicate cross-split pairs: **13**

## Interpretation

Potential leakage was detected. Inspect the JSON report before using the split for final claims.

## Split Counts

| Split | Images |
|---|---:|
| train | 1590 |
| val | 196 |
| test | 206 |

## First Near-Duplicate Pairs

| Hamming | A | B |
|---:|---|---|
| 0 | `dataset/processed/train/circus_assimilis/circus_assimilis_320320273_579131684.jpg` | `dataset/processed/test/circus_assimilis/ala_860404ea-477a-42fc-a572-2bfd4d39fa0b.jpg` |
| 0 | `dataset/processed/train/hieraaetus_morphnoides/ala_685a613e-2331-4184-8231-3fa938d949d9.jpg` | `dataset/processed/val/hieraaetus_morphnoides/hieraaetus_morphnoides_340404286_619458540.jpg` |
| 2 | `dataset/processed/test/circus_assimilis/ala_8bd3a263-8f9d-46e3-98f4-2e9c09ac531d.jpg` | `dataset/processed/train/circus_assimilis/circus_assimilis_313943044_566986707.jpg` |
| 2 | `dataset/processed/val/circus_assimilis/ala_46992cb4-faa9-4462-961a-96e6ef1db49a.jpg` | `dataset/processed/train/circus_assimilis/circus_assimilis_326952915_592245393.jpg` |
| 2 | `dataset/processed/val/circus_assimilis/ala_883a5995-e471-43d9-a403-93e5508899e2.jpg` | `dataset/processed/train/circus_assimilis/circus_assimilis_325644281_589637638.jpg` |
| 3 | `dataset/processed/test/circus_assimilis/circus_assimilis_294763186_530586862.jpg` | `dataset/processed/val/circus_assimilis/ala_192ea4f3-16ea-49fe-a845-00b8f19ec26e.jpg` |
| 3 | `dataset/processed/test/elanus_axillaris/ala_dfef4d28-e2d4-449a-9293-e637b0878be8.jpg` | `dataset/processed/val/elanus_axillaris/elanus_axillaris_337260635_613053120.jpg` |
| 3 | `dataset/processed/test/hieraaetus_morphnoides/hieraaetus_morphnoides_324404854_587147170.jpg` | `dataset/processed/train/hieraaetus_morphnoides/hieraaetus_morphnoides_339805982_618232770.jpg` |
| 4 | `dataset/processed/test/circus_assimilis/ala_7238f997-58d7-44de-8713-a39465b3d21b.jpg` | `dataset/processed/train/circus_assimilis/circus_assimilis_281401042_505489285.jpg` |
| 4 | `dataset/processed/test/falco_peregrinus/falco_peregrinus_330327982_598967662.jpg` | `dataset/processed/train/falco_peregrinus/ala_752ff81a-8f46-4796-b6c6-785f55cbc4ee.jpg` |
| 4 | `dataset/processed/val/falco_peregrinus/ala_6fb1737a-3bf8-46d8-9bbe-05f78b768116.jpg` | `dataset/processed/train/falco_peregrinus/ala_b2c5af69-5cbf-498f-8444-91265c0e8017.jpg` |
| 4 | `dataset/processed/val/falco_peregrinus/falco_peregrinus_323606526_585572323.jpg` | `dataset/processed/train/falco_peregrinus/ala_269a9438-2540-4e9b-8487-2f6600b59363.jpg` |
| 4 | `dataset/processed/val/lophoictinia_isura/lophoictinia_isura_338531257_615671199.jpg` | `dataset/processed/train/lophoictinia_isura/ala_58ad803c-6cb6-409b-8496-d8d09d19d64c.jpg` |
