# Release Manifest - v1.5 Academic Baseline

Generated UTC: `2026-06-14T19:42:23+00:00`

- Classifier: EfficientNetB4
- Detector/cropper: YOLO
- Active species: 8
- Test predictions: `results/test_predictions.csv`

## Verification Commands

```powershell
python notebooks\run_tests.py
python notebooks\healthcheck.py --verbose
python notebooks\audit_thesis_docx.py
python notebooks\audit_thesis_pdf.py
python notebooks\build_release_manifest.py
```

## Files

| Path | Size bytes | SHA-256 |
|---|---:|---|
| `README.md` | 27048 | `57a1131604931ba2d8c2b5db070bb209e46bb2d48ec71d4b5c828afbedba1036` |
| `LICENSE` | 2223 | `1e6c72ad106d3b6d03bdf6ad87f993c17cfd8b4bc57cf7da45cfed57e81031e8` |
| `CHANGELOG.md` | 15307 | `9be81c80eea8532da8eb65b9af2ca81325e016223b8b54c56af1ca1d2386aa59` |
| `CITATION.cff` | 1959 | `06daf61e91ca4573bc2588175d770895b1f5c34e26186d425c23587edc15e0ab` |
| `CONTRIBUTING.md` | 3250 | `bb8dc1c2f95dc0a24348011a1eb38478a92264c64bd1cad84a3a7ebbae4a1155` |
| `.gitignore` | 2563 | `3dae35d3c8c59fc7f15cca0ad737d69d227159f9de9970509c642b6f9a47a6e2` |
| `requirements.txt` | 968 | `d27bb1080954f7b7956fba8a853f3d3516dbad3b00519d4ae8c66cbcb8f60058` |
| `requirements-lock.txt` | 2753 | `b53d39893fcb1a7e055cbc16404dbb6a549e8076e79a0435c2654c5c4c3d0450` |
| `environment.yml` | 1185 | `89f3b170ac09e4334a970e46d52e7f22fcf10f9d7d9091a5a8949e0c2daa13aa` |
| `Dockerfile` | 2264 | `9ba9dfd41a177e2a95ef494ee291e49ba238cbee435a98354b61fbec2e00843a` |
| `.github/workflows/ci.yml` | 705 | `f17d8d6ff19d1d094478eed7580507c0ade3985033d68bd696cfa972864c9c27` |
| `gui/app.py` | 50326 | `d3f0d8e5a1606fb2734dabae2727b5f92fef5a3ab391abbb13532654c103fee4` |
| `gui/yolo_detector.py` | 2214 | `7dc5715798f15c8b7a22b697ff5b0521cdd4a364ffbaf85e8af03ed0b6a49b6c` |
| `gui/species_data_i18n.py` | 130779 | `39adaf0a5f739b93d4e0e4ed04b9ca4b6f0373c6947740e384ef35d084ad34ee` |
| `tests/test_project_integrity.py` | 6275 | `6971f7da0d38bb5e0f3d879e7800af0220d7e5427fd8cfb2dba7c814d2fbb7fe` |
| `notebooks/healthcheck.py` | 15281 | `614f6072f28bdb810080a85e513f94b6a711b3de5409fbfa8bb6c11d6867bc5d` |
| `notebooks/run_tests.py` | 1186 | `5914dfec9dda01c116a5db6e8d2c91d990551fc05664f98b8244966d9fecac5e` |
| `notebooks/retrain.py` | 23060 | `e4cf12ca41250fe199c8a2c71c01a62e423fd531805788615b977260e7ede865` |
| `notebooks/export_test_predictions.py` | 2619 | `1d5d9f95ab367714de5ffd5856406fb87a0a9a20add754f48cbdb2c887a59a4c` |
| `notebooks/update_final_report.py` | 4370 | `89c5a15d33ddb97426ae61b276b61596cf0835fae67de148c818cca1644f1091` |
| `notebooks/bootstrap_metrics.py` | 7899 | `d47d57e92da46bb24bf34d0d54bc6b28c839c7a969c591e7f545a616a58ba23f` |
| `notebooks/error_analysis.py` | 7909 | `7f65c655187ddc2977bd2705f1fa3b2cd79320cbfb9a3196e20c90cce76e5572` |
| `notebooks/calibration_ece.py` | 4912 | `9de56979b8488d8465e7d511df5520613d907bea298ea1a25aa5be2281841dae` |
| `notebooks/build_thesis_docx.py` | 29889 | `4768cfc935152215c07cb1a6e924447edd1658752e9222b910f1be4f7320fc64` |
| `notebooks/audit_thesis_docx.py` | 3484 | `468d22dea27c98fcca646cbe51e74b49fd32fbd8ce9af17c8ad3cb580f720f1d` |
| `notebooks/export_thesis_pdf.ps1` | 1381 | `5242a179a18f8f2167aaa53a9a31dffab587caa400b9a7bf0bccc8b245a972cd` |
| `notebooks/audit_thesis_pdf.py` | 2483 | `23a66c815ef5e15002d14e4a63eea011cfac5fa4b01e44cc43cdf84b0495d800` |
| `notebooks/audit_dataset_leakage.py` | 9909 | `840b3e6744687e0443885cf65321c7beb1db2521190b2529420d1e0da47e21e9` |
| `notebooks/build_leakage_review_plan.py` | 3979 | `7548294b856c3c035fa9f4f56e45e421909bcde1f8bb576c3d07f1e763728bca` |
| `notebooks/yolo_crop_ablation.py` | 6422 | `b01b9186fa935572b40b7cc32aa5a075871d7eca05ad264b6e9b860f9860822b` |
| `notebooks/top3_utility.py` | 3705 | `31fe1a9e06ef5488f81eac181037e6fb540f148cca172e3961601d5c738bc284` |
| `notebooks/build_model_registry.py` | 4171 | `496d03f770e82496e306c721a7a9c88322522ba6b727e12611f6d3e80af78614` |
| `notebooks/build_controlled_demo_set.py` | 4392 | `173fe3ce6f8ccfa21e85b7e97f61c1d153634d2bb0b7d32f5ba9409a5d314523` |
| `docs/THESIS.md` | 7332 | `e46f738f0e6c11891a331651873e706613f8c830355fadf791ecba144a521325` |
| `docs/SETUP.md` | 7775 | `0aa17a81fc5817b84c0d241e669306577df602459b72a25260dd45ae65144899` |
| `docs/Australian_Raptor_Thesis_v1_5.docx` | 2246395 | `55d89b40bb1b391b98af01e9f4037a1f3d449d69b49462a5d7fb8364239f9665` |
| `docs/Australian_Raptor_Thesis_v1_5.pdf` | 528946 | `872c358e8b2cc6c140dbaaff07bfe03deb1f8599f425ac186537e9f4572e1682` |
| `docs/DATASHEET.md` | 4418 | `32f89f2482e1397098455cfba690d55adffe625f568d620b12fb9114dfb2a8c8` |
| `docs/MODEL_CARD.md` | 3594 | `cfe773aeb64fe812047fbd399b6ef581b07a92dd30192e641dd17cb1d75372ad` |
| `docs/METHODOLOGY.md` | 5007 | `1117f3650d6b279f5cbcdd702d91fbf3eb3ead9c878a527c7f5fda67ddd9a8c2` |
| `docs/MASTERS_RESEARCH_PROPOSAL.md` | 4872 | `edc547409f01fef0136057ef831166629c356c19bd8903a53682d5c7e9737515` |
| `docs/SCIENTIFIC_DEFENSIBILITY.md` | 4530 | `eef97b5d02e8a8be64ed29e39f749be27cbb304a27abd81563e12301e690858e` |
| `docs/MASTERS_PRESENTATION_OUTLINE.md` | 2204 | `178cbab484ac7486b1ee8f9e643e0c0d468e04e0541ac93a933c3f59882070e0` |
| `docs/ETHICS_DATA_GOVERNANCE.md` | 1531 | `bdcc439c201f2d630aa986a49395a2134cefe2b96dd5103fb0399d41ffc9a509` |
| `docs/CLAIMS_MATRIX.md` | 1388 | `c3760f9fd2ef0ca37d67b2a56700f428b67b6f26556c0420dc808dc8ef1607f1` |
| `docs/SPLIT_GOVERNANCE.md` | 1937 | `a2d8c658cf16998f89a7faaf8b61bf9cdfe8e0b66605abf27036680760f2a598` |
| `docs/LEAKAGE_REVIEW_PROTOCOL.md` | 543 | `f01b93e0cc355fae335bad290e8d0a3f61ab93302efc937587b7674594a4d20c` |
| `docs/MODEL_REGISTRY.md` | 1176 | `36ddb1f5d342fc6b29eb0a74266264ad00a7bc0da0f6d49551e1ec0dc0c39870` |
| `docs/LIMITATIONS.md` | 2506 | `7eb2b55537a07800dff145f2b3b0317ffa2c821e5f8dc94bc1eb3b75769138b3` |
| `docs/CONTROLLED_DEMO_SET.md` | 2169 | `81651a71db6a91e5dc00bad55ebbda1088e568f48a7a39e89eea39f495e80fea` |
| `docs/DEFENSE_CHECKLIST.md` | 3346 | `bb6301e846b99a3459fdd7ad35ef67930376e664517e16ef949f70563c616e8d` |
| `docs/DEMO_SCRIPT.md` | 2200 | `7a2ee06662c21f724ffe88facb7b636b052d8a3c412a434a999db17c8b096bc6` |
| `docs/TAXONOMY_VERSIONING.md` | 6557 | `9e80a457fa66fb2ef116296a75267148932828912184766a6071c51d87b6131b` |
| `docs/SPECIES_ROADMAP.md` | 8374 | `ac9cf47a184ac81354143452bc3136372def9caa1be095faead914b1a079abe6` |
| `results/reporte_final.json` | 1995 | `4c4df6bdb58a49416156ee85e5e5f1036e45f8f88df08613bdd5db09e15b07ad` |
| `results/test_report.csv` | 825 | `0c6cae579ccf769178c0e1c4bbd75761b1d427d388e2319b366e967f00fa8d38` |
| `results/test_predictions.csv` | 65678 | `2946a9e2e6148d122b53c5f3f5d6d7c9038d800a08bb29bcb50948be6fde4a50` |
| `results/bootstrap_ci_efficientnet_b4.json` | 1344 | `c05f52af7c045b2e5e8a3e6cbb74a94774e06219e183fc2c7e2e9ea1f642fdd3` |
| `results/bootstrap_ci_efficientnet_b4.md` | 730 | `ae1c70d05ef4350d57e96c752071582c06cf892f83be418cd94f62b5a7e5176c` |
| `results/error_analysis_efficientnet_b4.json` | 1225 | `5631626e668f648fe506bd7001034564eff6d9a6ed431931a87cbd56e7ef33b5` |
| `results/error_analysis_efficientnet_b4.md` | 1079 | `0296e8190202a7a66d0432b931a59290f37ee71f1252acd02bcd76c89c6e7e5a` |
| `results/calibration_efficientnet_b4.json` | 1594 | `9671162cf444e76fab2fd4c04aa076105eb35d4c8344fc211fa814155b5e0573` |
| `results/temperature_scaling_efficientnet_b4.json` | 499 | `098dc2e1979c93112e0f6d081a0f2e209b1c5aa12cb691da8fb66aa84c9df969` |
| `results/top3_utility.json` | 13080 | `02204695e3b04e898f474d4f959e588bf73ab46b2e68fbef8e0089f653a235f7` |
| `results/top3_utility.md` | 620 | `7a27a74d6c4766ffaffa0044f95ea96f091d3358726f14f362f9824ad5e67a39` |
| `results/leakage_audit.json` | 6389 | `828a5d976f3d461adbd650810cd547626a9436528a5e33e3efcf591a6b39e7bd` |
| `results/leakage_audit.md` | 2874 | `805020aa5fdb9c9e97d2b4dedae461bfbfefb3ade1ab8d917ae92a5aea47ecd1` |
| `results/leakage_near_duplicate_pairs.jpg` | 237135 | `45bd4379809969bf9c3450ef15bb44b9a4db1ac9f9e121e76520cd8c240139a6` |
| `results/leakage_review_decisions.csv` | 4054 | `d2d4bab8d3a7d7377d04bce7070ad14dbed558317a958e02a32da3e47a8ee07b` |
| `dataset/metadata/deleak_split_plan_v1_6.csv` | 4128 | `8ec5ff538519b086cfc4d4c651f9739f875be748e1707ebaaa9e99f5f9e8c523` |
| `results/yolo_crop_ablation.json` | 675 | `451b686af199e008ec331fabece1ab4912268ded82b52b16221eb71e06610cd0` |
| `results/yolo_crop_ablation.md` | 383 | `ee7197bbb4d40a6d6b31d9b9633e58bf69778d5227cb26ebd47a453bdfe8a468` |
| `results/model_registry_v1_5.json` | 1533 | `0b02c3403555cc993ca32931259e96a0b2416d96c7492b1bdcb1cff1d93d2f1c` |
| `results/controlled_demo_set.csv` | 1727 | `46b308fb8bb39fe1595cd9aae48db382b1bd5b539dd66eea928bd29922a45607` |
| `demo/controlled/ood_gray.png` | 1275 | `87b45c546391650096bfcbaec1fef0de6014abd83fb9ff3d5f1d92121e501739` |
| `demo/controlled/ood_sky_like.png` | 1727 | `a84bbf1623e3908f73d933a424cbed5ebfc178863082d7532ee5d5b724ac2960` |
| `results/reliability_diagram_efficientnet_b4.png` | 45509 | `3a7400f3a78c64bfc40f98998290bae6ebd9835e5070da3947f84c5ac4357131` |
| `results/confusion_family_efficientnet_b4.png` | 31844 | `7c0b40c414640e36a88b5718e1eeae3e8ec1d5a123795a6db53721fb3c9b3c51` |
| `results/gradcam_mosaic.png` | 2128480 | `df9391b27cef8b5cb029c64115da03ad53ec3a24ba40852ef9672ec75cc6b689` |
| `results/thesis_docx_audit.json` | 1477 | `5a636650b74091cc3af1de5d40b8e5231a155ad0c2b5edd50cd4f52877a3f834` |
| `results/thesis_pdf_audit.json` | 780 | `f8eb6213ef6c8130c62728960487d7877635fe2e57a25eaa28edc91e21e1febd` |
| `models/best_model.pth (optional large artefact)` | 74654485 | `b8cdef9986913f77b5f234c535182bc130b202280c590fd130f148f053bb9f31` |
| `models/yolov8n.pt (optional large artefact)` | 6549796 | `f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36` |
