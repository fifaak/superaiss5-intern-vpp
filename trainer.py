import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from tqdm import tqdm
import pandas as pd
import time

def create_sequences(data, seq_length):
    """Creates sequences for time series forecasting."""
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def train_and_evaluate(experiment_name, model, train_df, test_df, config, single_station):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # --- Data Preparation ---
    if single_station:
        scaler = MinMaxScaler()
        train_scaled = scaler.fit_transform(train_df[['Electricity(kW)']].values)
        test_scaled = scaler.transform(test_df[['Electricity(kW)']].values)
    else: # All stations (multi-variate)
        stations = train_df['station_name'].unique()
        train_pivot = train_df.pivot(index='Date', columns='station_name', values='Electricity(kW)')[stations]
        test_pivot = test_df.pivot(index='Date', columns='station_name', values='Electricity(kW)')[stations]
        
        scaler = MinMaxScaler()
        train_scaled = scaler.fit_transform(train_pivot)
        test_scaled = scaler.transform(test_pivot)

    X_train, y_train = create_sequences(train_scaled, config['seq_length'])
    X_test, y_test = create_sequences(test_scaled, config['seq_length'])

    X_train, y_train = torch.from_numpy(X_train).float(), torch.from_numpy(y_train).float()
    X_test, y_test = torch.from_numpy(X_test).float(), torch.from_numpy(y_test).float()

    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True, num_workers=2, pin_memory=True)
    
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config['learning_rate'])
    grad_scaler = torch.amp.GradScaler('cuda', enabled=torch.cuda.is_available())

    # --- Training Loop ---
    log_data = []
    for epoch in tqdm(range(config['epochs']), desc=f"Training {experiment_name}", leave=False):
        start_time = time.time()
        model.train()
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device, non_blocking=True), y_batch.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            
            with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
                output = model(X_batch)
                loss = criterion(output, y_batch)
            
            grad_scaler.scale(loss).backward()
            grad_scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            grad_scaler.step(optimizer)
            grad_scaler.update()

        epoch_time = time.time() - start_time
        log_data.append({'epoch': epoch + 1, 'loss': loss.item(), 'time': epoch_time})
    
    # --- Evaluation ---
    model.eval()
    with torch.no_grad():
        test_predictions = []
        test_loader = DataLoader(TensorDataset(X_test), batch_size=config['batch_size'], shuffle=False)
        for X_batch, in test_loader:
            X_batch = X_batch.to(device)
            with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
                preds = model(X_batch)
            test_predictions.append(preds.cpu().numpy())
    predictions = np.concatenate(test_predictions, axis=0)
    
    predictions_inv = scaler.inverse_transform(predictions)
    y_test_inv = scaler.inverse_transform(y_test.cpu().numpy())
    
    mae = mean_absolute_error(y_test_inv, predictions_inv)
    mse = mean_squared_error(y_test_inv, predictions_inv)
    rmse = np.sqrt(mse)
    wape = np.mean(np.abs(y_test_inv - predictions_inv)) / np.mean(y_test_inv) * 100
    
    results = {'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'WAPE': wape}
    return pd.DataFrame([results]), pd.DataFrame(log_data)