"""
Runs a model on a single node across multiple gpus.
"""
import os
from argparse import ArgumentParser

from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import EarlyStopping

from project.model.deepspeech_main import DeepSpeech

seed_everything(234)


def main(args):
    """ Main training routine specific for this project. """
    # ------------------------
    # 1 INIT LIGHTNING MODEL
    # ------------------------
    model = DeepSpeech(**vars(args))

    # ------------------------
    # 2 INIT TRAINER
    # ------------------------
    trainer = Trainer.from_argparse_args(args)

    # ------------------------
    # 3 START TRAINING
    # ------------------------
    trainer.fit(model)


def run_cli():
    # ------------------------
    # TRAINING ARGUMENTS
    # ------------------------
    # these are project-wide arguments
    root_dir = os.path.dirname(os.path.realpath(__file__))
    parent_parser = ArgumentParser(add_help=False)
    # Each LightningModule defines arguments relevant to it
    parser = DeepSpeech.add_model_specific_args(parent_parser, root_dir)
    # Data
    parser.add_argument("--num_workers", default=4, type=int)
    parser.add_argument("--batch_size", default=8, type=int)
    parser.add_argument("--data_root", default="data/", type=str)
    parser.add_argument("--data_url", default=["train-clean-100", "train-clean-360", "train-other-500"])

    # training params (opt)
    parser.add_argument("--epochs", default=20, type=int)
    parser.add_argument("--learning_rate", default=0.001, type=float)
    parser.add_argument("--accumulate_grad_batches", default=40, type=int)
    parser.add_argument("--gpus", default=1, type=int)
    parser.add_argument("--precission", default=16, type=int)
    parser.add_argument("--gradient_clip", default=0.5, type=float)
    parser.add_argument("--auto_scale_batch_size", default=True, type=bool)
    parser.add_argument("--auto_select_gpus", default=True, type=bool)
    parser.add_argument("--log_gpu_memory", default=True, type=bool)
    parser.add_argument("--use_amp", default=True, type=bool)
    parser.add_argument("--early_stop_metric", default="wer", type=str)
    parser.add_argument("--early_stop_patience", default=3, type=int)

    # callbacks

    # parser = Trainer.add_argparse_args(parser)
    args = parser.parse_args()

    # Early stopper
    early_stop = EarlyStopping(
        monitor=args.early_stop_metric,
        patience=args.early_stop_patience,
        verbose=True,
    )

    args.early_stop_callback = early_stop
    setattr(args, "accumulate_grad_batches", 40)

    # ---------------------
    # RUN TRAINING
    # ---------------------
    main(args)


if __name__ == "__main__":
    run_cli()
