from locale import normalize
import os
from dataclasses import dataclass, field
from typing import Optional, List
from transformers import TrainingArguments


@dataclass
class ModelArguments:
    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    config_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained config name or path if not the same as model_name"}
    )
    tokenizer_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained tokenizer name or path if not the same as model_name"}
    )
    cache_dir: Optional[str] = field(
        default=None, metadata={"help": "Where do you want to store the pretrained models downloaded from s3"}
    )

    # out projection
    #add_pooler: bool = field(default=False)
    #projection_in_dim: int = field(default=768)
    #projection_out_dim: int = field(default=768)
    #normalize: bool = field(default=False)
    quantize_4bit: bool = field(default=True)
    use_grad_checkpointing: bool = field(default=True)
    train_batch_size: int = field(default=16)
    train_max_seq_length: int = field(default=512)
    use_flash_attention: bool = field(default=True)
    grad_acc_steps: int = field(default=2)
    seed: int = field(default=42)
    new_model_name: str = field(default="my-qlora-model")
    num_epochs: int = field(default=1)
    lora_alpha: int = field(default=32)
    lora_r: int = field(default=32)

    # for Jax training
    '''
    dtype: Optional[str] = field(
        default="float32",
        metadata={
            "help": "Floating-point format in which the model weights should be initialized and trained. Choose one "
                    "of `[float32, float16, bfloat16]`. "
        },
    )
    '''


@dataclass
class DataArguments:
    train_dir: str = field(
        default=None, metadata={"help": "Path to train directory"}
    )
    dataset_name: str = field(
        default=None, metadata={"help": "huggingface dataset name"}
    )
    passage_field_separator: str = field(default=' ')
    dataset_proc_num: int = field(
        default=96, metadata={"help": "number of proc used in dataset preprocess"}
    )
    train_n_passages: int = field(default=2)

    encode_in_path: List[str] = field(default=None, metadata={"help": "Path to data to encode"})
    encoded_save_path: str = field(default=None, metadata={"help": "where to save the encode"})
    encode_is_qry: bool = field(default=False)
    encode_num_shard: int = field(default=1)
    encode_shard_index: int = field(default=0)

    q_max_len: int = field(
        default=512,
        metadata={
            "help": "The maximum total input sequence length after tokenization for query. Sequences longer "
                    "than this will be truncated, sequences shorter will be padded."
        },
    )
    p_max_len: int = field(
        default=128,
        metadata={
            "help": "The maximum total input sequence length after tokenization for passage. Sequences longer "
                    "than this will be truncated, sequences shorter will be padded."
        },
    )
    data_cache_dir: Optional[str] = field(
        default=None, metadata={"help": "Where do you want to store the data downloaded from huggingface"}
    )
    codemix_ratio: float = field(default=0.0)
    codemix_sentence_ratio: float = field(default=0.0)
    #codemix_set: str = field(default='en-ko')
    codemix_in_runtime: bool = field(default=True)
    cm_loss_weight: float = field(default=0.0)

    def __post_init__(self):
        if self.dataset_name is not None:
            if ':' in self.dataset_name:
                info = self.dataset_name.split(':')
                if len(info) == 3:
                    self.dataset_name, self.dataset_language, self.dataset_split = self.dataset_name.split(':')
                if len(info) == 2:
                    self.dataset_name, self.dataset_language = self.dataset_name.split(':')
                    self.dataset_split = 'train'
            else:
                info = self.dataset_name.split('/')
                self.dataset_split = info[-1] if len(info) == 3 else 'train'
                self.dataset_name = "/".join(info[:-1]) if len(info) == 3 else '/'.join(info)
                self.dataset_language = 'default'
            if ':' in self.dataset_name:
                self.dataset_name, self.dataset_language = self.dataset_name.split(':')
        else:
            self.dataset_name = 'json'
            self.dataset_split = 'train'
            self.dataset_language = 'default'
        if self.train_dir is not None:
            if os.path.isdir(self.train_dir):
                files = os.listdir(self.train_dir)
                # change all train directory paths to absolute
                self.train_dir = os.path.join(os.path.abspath(os.getcwd()), self.train_dir)
                self.train_path = [
                    os.path.join(self.train_dir, f)
                    for f in files
                    if f.endswith('jsonl') or f.endswith('json')
                ]
            else:
                self.train_path = [self.train_dir]
        else:
            self.train_path = None

'''
@dataclass
class TevatronTrainingArguments(TrainingArguments):
    warmup_ratio: float = field(default=0.1)
    negatives_x_device: bool = field(default=False, metadata={"help": "share negatives across devices"})
    do_encode: bool = field(default=False, metadata={"help": "run the encoding loop"})

    grad_cache: bool = field(default=False, metadata={"help": "Use gradient cache update"})
    gc_q_chunk_size: int = field(default=4)
    gc_p_chunk_size: int = field(default=32)
    
    contrastive: bool = field(default=False, metadata={"help": "ContrastiveMix"})
'''