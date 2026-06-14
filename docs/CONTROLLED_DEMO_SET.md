# Controlled Demo Set

Use this set for presentations so the demo is honest and repeatable.

| Category | Image | Expected use | y_true | y_pred | confidence |
|---|---|---|---|---|---:|
| easy_correct | `dataset/processed/test/aquila_audax/ala_11a1ff86-c08b-41bb-a300-2a0fe5d3f5e6.jpg` | Show normal successful classification. | `aquila_audax` | `aquila_audax` | 99.7 |
| easy_correct | `dataset/processed/test/aquila_audax/ala_2c4aa6d3-c927-45ec-9081-30928c519970.jpg` | Show normal successful classification. | `aquila_audax` | `aquila_audax` | 91.6 |
| easy_correct | `dataset/processed/test/aquila_audax/ala_303fb88d-6ca1-4751-866a-b5ff54db08aa.jpg` | Show normal successful classification. | `aquila_audax` | `aquila_audax` | 99.8 |
| easy_correct | `dataset/processed/test/aquila_audax/ala_361edc73-4ff4-4a5d-8aea-1f86e5347867.jpg` | Show normal successful classification. | `aquila_audax` | `aquila_audax` | 95.9 |
| easy_correct | `dataset/processed/test/aquila_audax/ala_5ae4195f-2f5d-4db0-827d-fb6381eb94a5.jpg` | Show normal successful classification. | `aquila_audax` | `aquila_audax` | 94.0 |
| difficult | `dataset/processed/test/circus_assimilis/ala_0d542178-f851-4bed-a9e6-ff6c0cbf8e85.jpg` | Show uncertainty, top-3 alternatives, and error discussion. | `circus_assimilis` | `falco_cenchroides` | 43.8 |
| difficult | `dataset/processed/test/circus_assimilis/ala_ba8c3d83-02a6-4a28-9c59-0d79daae3897.jpg` | Show uncertainty, top-3 alternatives, and error discussion. | `circus_assimilis` | `lophoictinia_isura` | 79.8 |
| difficult | `dataset/processed/test/circus_assimilis/ala_bb5f2ca3-7f8a-4ac2-b116-d69dcad0307c.jpg` | Show uncertainty, top-3 alternatives, and error discussion. | `circus_assimilis` | `hieraaetus_morphnoides` | 30.1 |
| out_of_domain | `demo/controlled/ood_gray.png` | Demonstrate closed-set weakness and out-of-domain feedback. | `not_a_bird` | `` |  |
| out_of_domain | `demo/controlled/ood_sky_like.png` | Demonstrate that non-raptor scenes still require user caution. | `not_a_raptor` | `` |  |

## Presentation Rule

Show easy, difficult and out-of-domain cases. Do not present only successful examples.
