# ChronoColor 4K AI — Model Weights

This directory stores AI model weights. **These files are gitignored** due to their large size (~25-40 GB total).

## Download Instructions

Run the download script to fetch all required model weights:

```bash
bash scripts/download_models.sh
```

Or download individual models:

### Required Models

| Model | Size | Source |
|-------|------|--------|
| Real-ESRGAN x4 | ~64MB | [GitHub](https://github.com/xinntao/Real-ESRGAN) |
| GFPGAN v1.4 | ~332MB | [GitHub](https://github.com/TencentARC/GFPGAN) |
| CodeFormer | ~370MB | [GitHub](https://github.com/sczhou/CodeFormer) |
| NAFNet-width64 | ~65MB | [GitHub](https://github.com/megvii-research/NAFNet) |
| DDColor artistic | ~2.4GB | [GitHub](https://github.com/piddnad/DDColor) |
| YOLOv11n | ~6MB | [Ultralytics](https://docs.ultralytics.com) |
| SAM 2 hiera_large | ~900MB | [GitHub](https://github.com/facebookresearch/sam2) |
| RAFT (sintel) | ~20MB | [torchvision](https://pytorch.org/vision) |

### Directory Structure

```
models/
├── realesrgan/
│   └── RealESRGAN_x4plus.pth
├── gfpgan/
│   └── GFPGANv1.4.pth
├── codeformer/
│   └── codeformer.pth
├── nafnet/
│   └── NAFNet-width64.pth
├── ddcolor/
│   └── ddcolor_artistic.pth
├── yolo/
│   └── yolo11n.pt
├── sam2/
│   └── sam2_hiera_large.pt
└── scene/
    └── scene_classifier.pth
```
