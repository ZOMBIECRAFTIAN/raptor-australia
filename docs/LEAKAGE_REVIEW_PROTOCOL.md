# Leakage Review Protocol

Use this protocol before claiming a de-leaked v1.6 split.

1. Open `results/leakage_near_duplicate_pairs.jpg`.
2. Fill `results/leakage_review_decisions.csv`.
3. Mark each pair as `confirmed_duplicate`, `same_observation_likely`, `visually_similar_but_ok`, or `false_positive`.
4. Build a new split only after confirmed/same-observation pairs are grouped.
5. Retrain or re-evaluate before replacing v1.5 metrics.

Do not move files manually without updating `dataset/metadata/deleak_split_plan_v1_6.csv`.
