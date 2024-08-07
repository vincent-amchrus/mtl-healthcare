import argparse
import numpy as np
import torch

from dataset import get_data_mtl
from dataset import RegressionDataset
from trainer.regression_trainer import RegressionTrainer
from net import (
    RegressionLSTM,
    reg_loss_fn,
    reg_metric
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Hyper parameters for training")
    # Hyper parameter for training
    parser.add_argument('--batch_size', type=int, help='Batch size for training')
    parser.add_argument('--epochs', type=int, help='Number of training epochs')
    parser.add_argument('--input_dim', type=int, help='Input dimension')
    parser.add_argument('--n_hidden_1', type=int, help='Number of hidden units in the LSTM layer')
    parser.add_argument('--n_hidden_2', type=int, help='Number of hidden units in the LSTM layer')
    parser.add_argument('--p_dropout', type=float, help='Dropout probability')
    parser.add_argument('--learning_rate', type=float, help='Learning rate')
    parser.add_argument('--seed', type=int, help='Set the random seed')
    parser.add_argument('--log_steps', type=int, help='Logging steps during training')
    
    # Location of data and checkpoint 
    parser.add_argument('--data_path', type=str, help='Path to the data training')
    parser.add_argument('--output_dir', type=str, help='Output directory for saving models')

    # WandB logging
    parser.add_argument('--log_console', action='store_true', help='Enable console logging')
    parser.add_argument('--log_wandb', action='store_true', help='Enable WandB logging')
    parser.add_argument('--project_name', type=str, default='Project demo', help='WandB project name')
    parser.add_argument('--experiment_name', type=str, default='Experiment demo', help='WandB experiment name')
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()

    # Load data
    data = np.load(args.data_path)
    print("Loading data from {}...".format(args.data_path))
    tensor_data = get_data_mtl(data=data)
    train_dataset = RegressionDataset(
        features=tensor_data["x_train"],
        reg_target=tensor_data["y_train_reg"]
    )
    dev_dataset = RegressionDataset(
        features=tensor_data["x_dev"],
        reg_target=tensor_data["y_dev_reg"]
    )
    test_dataset = RegressionDataset(
        features=tensor_data["x_test"],
        reg_target=tensor_data["y_test_reg"]
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Initialize the PyTorch model
    model = RegressionLSTM(
        input_size=args.input_dim,
        hidden_size_1=args.n_hidden_1,
        hidden_size_2=args.n_hidden_2,
        dropout=args.p_dropout
    )
    model = model.to(device)

    optimizer = torch.optim.Adam(
        params=model.parameters(),
        lr=args.learning_rate
    )

    print("Training info:\n")
    print("- Train data: {} samples".format(len(train_dataset)))
    print("- Dev data: {} samples".format(len(dev_dataset)))
    print("- Batch size: {}".format(args.batch_size))
    print("- Number of epochs: {}".format(args.epochs))
    print("- Learning rate: {}".format(args.learning_rate))
    print("Model config:\n", model)
    trainer = RegressionTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        test_dataset=test_dataset,
        reg_loss_fn=reg_loss_fn,
        reg_metric=reg_metric,
        optimizer=optimizer,
        batch_size=args.batch_size,
        epochs=args.epochs,
        output_dir=args.output_dir,
        log_console=args.log_console,
        log_steps=args.log_steps,
        log_wandb=args.log_wandb,
        project_name=args.project_name,
        experiment_name=args.experiment_name
    )
    trainer.train()