
import csv
from pathlib import Path

import h5py
import torch
from torch.nn.utils.rnn import pad_sequence

from modules.datamodules.base import BaseReportDataModule, BaseReportDataset


class WSICaptionDataset(BaseReportDataset):

    def __init__(self, args, tokenizer, split):
        self.data_path_patch = Path(args.data_path_patch)
        self.manifest_path = Path(args.manifest_path)
        self.max_fea_length = args.max_fea_length
        self.slide_file_paths = {}

        super().__init__(args, tokenizer, split)

    def build_slides(self):
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"Manifest not found: {self.manifest_path.resolve()}"
            )

        matched_slides = []

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            records = csv.DictReader(f)

            for record in records:
                if record["split"] != self.split:
                    continue

                slide_id = record["id"]

                # Only include slides that have reports in this split.
                if slide_id not in self.reports:
                    continue

                feature_path = self.data_path_patch / record["repo_path"]

                if not feature_path.exists():
                    raise FileNotFoundError(
                        f"Feature file missing for {slide_id}: "
                        f"{feature_path}"
                    )

                if slide_id in self.slide_file_paths:
                    raise ValueError(
                        f"Duplicate slide ID in manifest: {slide_id}"
                    )

                self.slide_file_paths[slide_id] = feature_path
                matched_slides.append(slide_id)

        print(
            f"Split: {self.split} | "
            f"Reports: {len(self.reports)} | "
            f"Matched feature files: {len(matched_slides)}"
        )

        if not matched_slides:
            raise RuntimeError(
                f"No matching slides found for split: {self.split}"
            )

        return matched_slides

    def __getitem__(self, idx):
        slide_id = self.slides[idx]

        report_ids, report_masks = self.encode_report(slide_id)

        feature_path = self.slide_file_paths[slide_id]

        with h5py.File(feature_path, "r") as h5_file:
            patch_embedding = torch.tensor(
                h5_file["features"][:]
            )[:self.max_fea_length]

        return slide_id, patch_embedding, report_ids, report_masks


class WSICaptionDataModule(BaseReportDataModule):

    def build_dataset(self, split):
        return WSICaptionDataset(self.args, self.tokenizer, split)

    @staticmethod
    def collate_fn(batch):
        slide_ids, patch_embeddings, report_ids, report_masks = zip(*batch)

        report_ids = WSICaptionDataModule.to_long_tensor(report_ids)

        features = {
            "patch": pad_sequence(
                patch_embeddings,
                batch_first=True
            ),
        }

        return (
            slide_ids,
            features,
            report_ids,
            WSICaptionDataModule.to_float_tensor(report_masks)
        )
