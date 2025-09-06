from data_loader import load_and_preprocess_data
from models import GRU, BiGRU, CNN_GRU, CNN_BiGRU
from trainer import train_and_evaluate
from utils import set_seed, get_device, save_results
import pandas as pd
import optuna
import torch

def run_experiment(experiment_name, model_class, train_df, test_df, config, single_station=False):
    """Runs a full experiment for a given model, including 5 seeds."""
    all_results, all_logs = [], []
    num_stations = train_df['station_name'].nunique()

    print(f"\n--- Starting Experiment: {experiment_name} ---")
    
    if single_station:
        config['model_params']['input_size'] = 1
        config['model_params']['output_size'] = 1
        for station in tqdm(train_df['station_name'].unique(), desc=f"Stations for {experiment_name}"):
            station_train_df = train_df[train_df['station_name'] == station]
            station_test_df = test_df[test_df['station_name'] == station]
            
            for seed in range(5):
                set_seed(seed)
                model = model_class(**config['model_params'])
                if hasattr(torch, 'compile'): model = torch.compile(model)
                
                exp_id = f"{experiment_name}_{station.replace('Data_', '')}_seed{seed}"
                results, log = train_and_evaluate(exp_id, model, station_train_df, station_test_df, config, single_station=True)
                results['station'], results['seed'] = station, seed
                all_results.append(results)
                all_logs.append(log)
    else: # All-station models
        config['model_params']['input_size'] = num_stations
        config['model_params']['output_size'] = num_stations
        for seed in range(5):
            set_seed(seed)
            model = model_class(**config['model_params'])
            if hasattr(torch, 'compile'): model = torch.compile(model)
            
            exp_id = f"{experiment_name}_seed{seed}"
            results, log = train_and_evaluate(exp_id, model, train_df, test_df, config, single_station=False)
            results['seed'] = seed
            all_results.append(results)
            all_logs.append(log)
            
    final_results = pd.concat(all_results)
    final_logs = pd.concat(all_logs)
    save_results(experiment_name, final_results, final_logs)

def objective(trial, model_class, train_df, test_df, config, single_station):
    """Optuna objective function."""
    temp_config = config.copy()
    temp_config['learning_rate'] = trial.suggest_loguniform('learning_rate', 1e-4, 1e-2)
    temp_config['batch_size'] = trial.suggest_categorical('batch_size', [32, 64, 128])
    temp_config['model_params'] = config['model_params'].copy()
    temp_config['model_params']['hidden_size'] = trial.suggest_categorical('hidden_size', [50, 100, 150])
    temp_config['model_params']['num_layers'] = trial.suggest_int('num_layers', 1, 3)
    
    # Optuna runs on a single station for speed
    station = train_df['station_name'].unique()[0]
    station_train = train_df[train_df['station_name'] == station]
    station_test = test_df[test_df['station_name'] == station]
    
    model = model_class(**temp_config['model_params'])
    results, _ = train_and_evaluate("optuna_trial", model, station_train, station_test, temp_config, single_station=True)
    return results['MAE'].iloc[0]

def main():
    """Main function to orchestrate all experiments."""
    train_df, test_df = load_and_preprocess_data()
    get_device()

    base_config = {
        'seq_length': 96, 'epochs': 50, 'learning_rate': 0.001, 'batch_size': 64,
        'model_params': {'hidden_size': 100, 'num_layers': 2}
    }

    # --- Experiments without Optuna ---
    experiments = {
        "GRU_all_station": (GRU, False), "BiGRU_all_station": (BiGRU, False),
        "CNN_GRU_all_station": (CNN_GRU, False), "CNN_BiGRU_all_station": (CNN_BiGRU, False),
        # "GRU_single_station": (GRU, True), "BiGRU_single_station": (BiGRU, True),
        # "CNN_GRU_single_station": (CNN_GRU, True), "CNN_BiGRU_single_station": (CNN_BiGRU, True)
    }
    for name, (model_class, is_single) in experiments.items():
        run_experiment(name, model_class, train_df, test_df, base_config, single_station=is_single)

    # --- Experiments with Optuna ---
    # Note: Optuna is run on a single station for faster hyperparameter search
    optuna_experiments = {
        "GRU_tuned": GRU, "BiGRU_tuned": BiGRU, "CNN_GRU_tuned": CNN_GRU, "CNN_BiGRU_tuned": CNN_BiGRU
    }
    for name, model_class in optuna_experiments.items():
        print(f"\n--- Running Optuna for: {name} ---")
        study = optuna.create_study(direction='minimize')
        study.optimize(lambda t: objective(t, model_class, train_df, test_df, base_config, single_station=True), n_trials=10)
        
        print(f"Best params for {name}: {study.best_params}")
        tuned_config = base_config.copy()
        tuned_config.update(study.best_params)
        
        run_experiment(f"{name}_all_station", model_class, train_df, test_df, tuned_config, single_station=False)
        run_experiment(f"{name}_single_station", model_class, train_df, test_df, tuned_config, single_station=True)

if __name__ == '__main__':
    main()