#!/bin/bash
# ============================================================
# ChronoColor 4K AI — Model Weight Downloader
# ============================================================
# Downloads all required AI model weights.
# Run: bash scripts/download_models.sh
# ============================================================

set -e

MODELS_DIR="${MODELS_DIR:-./models}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ChronoColor 4K AI — Model Weight Downloader       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Download directory: $MODELS_DIR"
echo ""

# Create directories
mkdir -p "$MODELS_DIR"/{realesrgan,gfpgan,codeformer,nafnet,ddcolor,yolo,sam2,scene}

# --- Real-ESRGAN ---
echo "📦 [1/8] Downloading Real-ESRGAN x4plus..."
if [ ! -f "$MODELS_DIR/realesrgan/RealESRGAN_x4plus.pth" ]; then
    wget -q --show-progress -O "$MODELS_DIR/realesrgan/RealESRGAN_x4plus.pth" \
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
    echo "   ✅ Real-ESRGAN downloaded"
else
    echo "   ⏭️  Already exists, skipping"
fi

# --- GFPGAN ---
echo "📦 [2/8] Downloading GFPGAN v1.4..."
if [ ! -f "$MODELS_DIR/gfpgan/GFPGANv1.4.pth" ]; then
    wget -q --show-progress -O "$MODELS_DIR/gfpgan/GFPGANv1.4.pth" \
        "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"
    echo "   ✅ GFPGAN downloaded"
else
    echo "   ⏭️  Already exists, skipping"
fi

# --- CodeFormer ---
echo "📦 [3/8] Downloading CodeFormer..."
if [ ! -f "$MODELS_DIR/codeformer/codeformer.pth" ]; then
    wget -q --show-progress -O "$MODELS_DIR/codeformer/codeformer.pth" \
        "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth"
    echo "   ✅ CodeFormer downloaded"
else
    echo "   ⏭️  Already exists, skipping"
fi

# --- NAFNet ---
echo "📦 [4/8] Downloading NAFNet..."
if [ ! -f "$MODELS_DIR/nafnet/NAFNet-width64.pth" ]; then
    wget -q --show-progress -O "$MODELS_DIR/nafnet/NAFNet-width64.pth" \
        "https://github.com/megvii-research/NAFNet/releases/download/v0.1.0/NAFNet-SIDD-width64.pth"
    echo "   ✅ NAFNet downloaded"
else
    echo "   ⏭️  Already exists, skipping"
fi

# --- DDColor ---
echo "📦 [5/8] Downloading DDColor..."
if [ ! -f "$MODELS_DIR/ddcolor/ddcolor_artistic.pth" ]; then
    echo "   ⚠️  DDColor must be downloaded from Hugging Face."
    echo "   Visit: https://huggingface.co/piddnad/DDColor"
    echo "   Place the model at: $MODELS_DIR/ddcolor/ddcolor_artistic.pth"
else
    echo "   ⏭️  Already exists, skipping"
fi

# --- YOLOv11 ---
echo "📦 [6/8] Downloading YOLOv11..."
if [ ! -f "$MODELS_DIR/yolo/yolo11n.pt" ]; then
    pip install -q ultralytics 2>/dev/null
    python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')" 2>/dev/null
    mv yolo11n.pt "$MODELS_DIR/yolo/" 2>/dev/null || true
    echo "   ✅ YOLOv11 downloaded"
else
    echo "   ⏭️  Already exists, skipping"
fi

# --- SAM 2 ---
echo "📦 [7/8] Downloading SAM 2..."
if [ ! -f "$MODELS_DIR/sam2/sam2_hiera_large.pt" ]; then
    echo "   ⚠️  SAM 2 must be downloaded from Meta."
    echo "   Visit: https://github.com/facebookresearch/sam2#download-checkpoints"
    echo "   Place the model at: $MODELS_DIR/sam2/sam2_hiera_large.pt"
else
    echo "   ⏭️  Already exists, skipping"
fi

# --- RAFT ---
echo "📦 [8/8] RAFT optical flow..."
echo "   ℹ️  RAFT is included in torchvision, no separate download needed."

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ Model download complete!"
echo ""
echo "Models directory: $MODELS_DIR"
du -sh "$MODELS_DIR" 2>/dev/null || true
echo "═══════════════════════════════════════════════════════"
