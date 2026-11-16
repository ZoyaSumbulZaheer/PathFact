
from types import SimpleNamespace

from modules.tokenizers.report_tokenizers import Tokenizer
from modules.datamodules.wsi_caption.base import WSICaptionDataset


# Configuration
args = SimpleNamespace(
    data_path_patch="tcga_subset/features",
    manifest_path="tcga_subset/tcga_manifest.csv",
    reports_json_path="reports/tcga_reports_splits.json",
    max_fea_length=10000,
    max_seq_length=600,
    dataset_type="tcga"
)

# Initialize tokenizer
print("Initializing tokenizer...")
tokenizer = Tokenizer(
    args.reports_json_path,
    args.dataset_type
)

print("Vocabulary size:", tokenizer.get_vocab_size())

# Test all three splits
for split in ["train", "val", "test"]:

    print("\n" + "=" * 50)
    print("Testing split:", split)
    print("=" * 50)

    dataset = WSICaptionDataset(args, tokenizer, split)

    print("Number of slides:", len(dataset))

    # Load one actual sample
    slide_id, features, report_ids, report_masks = dataset[0]

    print("\nSample loaded successfully!")
    print("Slide ID:", slide_id)
    print("Feature shape:", tuple(features.shape))
    print("Feature dtype:", features.dtype)
    print("Report token count:", sum(report_masks))
    print("Report IDs shape:", len(report_ids))
    print("Report masks shape:", len(report_masks))

    assert features.ndim == 2
    assert features.shape[1] == 1536
    assert len(report_ids) == 600
    assert len(report_masks) == 600

    print("Split test: PASSED")

print("\nALL DATASET TESTS PASSED!")
