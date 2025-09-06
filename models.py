import torch
import torch.nn as nn

class GRU(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(GRU, self).__init__()
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: (batch_size, seq_length, input_size)
        out, _ = self.gru(x)
        # out shape: (batch_size, seq_length, hidden_size)
        out = self.fc(out[:, -1, :]) # Use the last hidden state
        return out

class BiGRU(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(BiGRU, self).__init__()
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, output_size) # *2 for bidirectional

    def forward(self, x):
        out, _ = self.gru(x)
        out = self.fc(out[:, -1, :])
        return out

class CNN_GRU(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, cnn_out_channels=64, kernel_size=3):
        super(CNN_GRU, self).__init__()
        # Conv1d expects (batch, channels, seq_len)
        self.conv1d = nn.Conv1d(in_channels=input_size, out_channels=cnn_out_channels, kernel_size=kernel_size)
        self.relu = nn.ReLU()
        self.gru = nn.GRU(cnn_out_channels, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: (batch_size, seq_length, input_size)
        x = x.permute(0, 2, 1) # -> (batch_size, input_size, seq_length)
        x = self.relu(self.conv1d(x))
        x = x.permute(0, 2, 1) # -> (batch_size, new_seq_length, cnn_out_channels)
        out, _ = self.gru(x)
        out = self.fc(out[:, -1, :])
        return out

class CNN_BiGRU(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, cnn_out_channels=64, kernel_size=3):
        super(CNN_BiGRU, self).__init__()
        self.conv1d = nn.Conv1d(in_channels=input_size, out_channels=cnn_out_channels, kernel_size=kernel_size)
        self.relu = nn.ReLU()
        self.gru = nn.GRU(cnn_out_channels, hidden_size, num_layers, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, output_size)

    def forward(self, x):
        x = x.permute(0, 2, 1)
        x = self.relu(self.conv1d(x))
        x = x.permute(0, 2, 1)
        out, _ = self.gru(x)
        out = self.fc(out[:, -1, :])
        return out