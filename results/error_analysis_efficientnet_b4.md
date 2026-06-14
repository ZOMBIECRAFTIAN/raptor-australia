# Error analysis — efficientnet_b4

- Test set size: **217** images
- Fine-grained (8-class) accuracy: **0.8571**
- Family-level (2-class) accuracy:  **0.9401**
- Cross-family errors: **13** (6.0% of test set)

## Family-level confusion

| true \ pred | Accipitridae | Falconidae |
|---|---|---|
| Accipitridae | 169 | 3 |
| Falconidae | 10 | 35 |

## Top 10 confusions (off-diagonal)

| Rank | True species | Predicted species | n | Family-crossing? |
|---|---|---|---|---|
| 1 | falco_cenchroides | elanus_axillaris | 3 | yes |
| 2 | hieraaetus_morphnoides | lophoictinia_isura | 3 | same |
| 3 | tachyspiza_fasciata | elanus_axillaris | 3 | same |
| 4 | circus_assimilis | lophoictinia_isura | 2 | same |
| 5 | elanus_axillaris | falco_peregrinus | 2 | yes |
| 6 | falco_cenchroides | lophoictinia_isura | 2 | yes |
| 7 | falco_peregrinus | circus_assimilis | 2 | yes |
| 8 | falco_peregrinus | elanus_axillaris | 2 | yes |
| 9 | hieraaetus_morphnoides | aquila_audax | 2 | same |
| 10 | tachyspiza_fasciata | hieraaetus_morphnoides | 2 | same |
