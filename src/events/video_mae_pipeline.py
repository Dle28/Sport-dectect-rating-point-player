"""
VideoMAE-based event classifier for soccer clips.

Features:
- Preprocesses videos into 16-frame sequences using Hugging Face processors.
- Extracts embeddings from VideoMAE.
- Trains a classifier for Pass, Shot, Tackle (3-way).
- Runs sliding-window inference to output event timestamps.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoImageProcessor, VideoMAEForVideoClassification


EVENT_LABELS = ["Pass", "Shot", "Tackle"]
LABEL2ID = {label: i for i, label in enumerate(EVENT_LABELS)}
ID2LABEL = {i: label for label, i in LABEL2ID.items()}


def _sample_clip(frames: List, num_frames: int = 16) -> List:
    """Uniformly sample or pad frames to num_frames."""
    if len(frames) >= num_frames:
        idx = torch.linspace(0, len(frames) - 1, steps=num_frames).long()
        return [frames[i] for i in idx]
    # pad with last frame
    return frames + [frames[-1]] * (num_frames - len(frames))


class VideoClipDataset(Dataset):
    """Dataset for labeled clips stored as video files."""

    def __init__(self, samples: List[Tuple[Path, str]], processor: AutoImageProcessor, num_frames: int = 16):
        """
        samples: list of (video_path, label_name)
        """
        self.samples = samples
        self.processor = processor
        self.num_frames = num_frames

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        video_path, label = self.samples[idx]
        frames = self._read_frames(video_path)
        clip = _sample_clip(frames, num_frames=self.num_frames)
        inputs = self.processor(clip, return_tensors="pt")
        pixel_values = inputs["pixel_values"].squeeze(0)  # (num_frames, 3, H, W)
        return {
            "pixel_values": pixel_values,
            "labels": torch.tensor(LABEL2ID[label], dtype=torch.long),
        }

    def _read_frames(self, path: Path) -> List:
        cap = cv2.VideoCapture(str(path))
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
        cap.release()
        if not frames:
            raise RuntimeError(f"No frames read from {path}")
        return frames


@dataclass
class VideoMAEEventClassifier:
    model_name: str = "MCG-NJU/videomae-base"
    num_frames: int = 16
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    learning_rate: float = 3e-4
    weight_decay: float = 0.01

    def __post_init__(self):
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        self.model = VideoMAEForVideoClassification.from_pretrained(
            self.model_name,
            num_labels=len(EVENT_LABELS),
            id2label=ID2LABEL,
            label2id=LABEL2ID,
        ).to(self.device)

    def extract_embeddings(self, pixel_values: torch.Tensor) -> torch.Tensor:
        """
        Return pooled embeddings (batch, hidden_size) without classification head.
        pixel_values: (batch, num_frames, 3, H, W)
        """
        outputs = self.model.videomae(pixel_values.to(self.device))
        hidden = outputs.last_hidden_state  # (batch, tokens, dim)
        pooled = hidden.mean(dim=1)
        return pooled

    def train_epoch(self, dataloader: DataLoader, optimizer: torch.optim.Optimizer) -> float:
        self.model.train()
        total_loss = 0.0
        for batch in dataloader:
            pixel_values = batch["pixel_values"].to(self.device)
            labels = batch["labels"].to(self.device)
            outputs = self.model(pixel_values=pixel_values, labels=labels)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        return total_loss / max(len(dataloader), 1)

    @torch.no_grad()
    def predict_clip(self, frames_rgb: List) -> Dict[str, float]:
        """
        frames_rgb: list of RGB numpy frames.
        Returns class probabilities dict.
        """
        self.model.eval()
        clip = _sample_clip(frames_rgb, num_frames=self.num_frames)
        inputs = self.processor(clip, return_tensors="pt").to(self.device)
        logits = self.model(**inputs).logits
        probs = F.softmax(logits, dim=-1).squeeze(0)
        return {ID2LABEL[i]: probs[i].item() for i in range(len(EVENT_LABELS))}

    @torch.no_grad()
    def predict_events(
        self,
        video_path: Path,
        stride: int = 8,
        threshold: float = 0.6,
    ) -> List[Tuple[str, float, float]]:
        """
        Sliding-window inference over a video.
        Returns: list of (label, timestamp_s, confidence)
        """
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        buffer: List = []
        events: List[Tuple[str, float, float]] = []
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            buffer.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if len(buffer) >= self.num_frames and frame_idx % stride == 0:
                probs = self.predict_clip(buffer[-self.num_frames :])
                label, conf = max(probs.items(), key=lambda x: x[1])
                if conf >= threshold:
                    timestamp = frame_idx / fps
                    events.append((label, timestamp, conf))
            frame_idx += 1
        cap.release()
        return events


def build_dataloader(
    samples: List[Tuple[Path, str]],
    processor: AutoImageProcessor,
    batch_size: int = 4,
    num_frames: int = 16,
    shuffle: bool = True,
) -> DataLoader:
    ds = VideoClipDataset(samples, processor, num_frames=num_frames)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=2, pin_memory=True)
