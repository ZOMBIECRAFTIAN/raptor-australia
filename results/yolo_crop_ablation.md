# YOLO-Crop vs Whole-Image Ablation

Status: **completed**

| Mode | n | Accuracy | Mean confidence |
|---|---:|---:|---:|
| whole_image | 217 | 0.8387 | 75.18 |
| yolo_crop | 217 | 0.8157 | 73.68 |
| adaptive | 217 | 0.8571 | 80.26 |

## Note

This is an inference ablation with the same EfficientNetB4 checkpoint. It does not retrain the classifier on cropped images.
