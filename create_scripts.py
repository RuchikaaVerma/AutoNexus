import os
 
scripts = [
    'ml/training/generate_training_data.py',
    'ml/training/generate_anomaly_data.py',
    'ml/training/generate_demand_data.py',
    'ml/training/feature_engineering.py',
    'ml/training/train_failure_model.py',
    'ml/training/train_anomaly_model.py',
    'ml/training/train_demand_model.py',
    'ml/training/create_visualizations.py',
    'ml/training/retrain_model.py',
    'ml/evaluation/evaluate_model.py',
    'ml/api/predictions_api.py',
    'agents/workers/data_analysis_agent.py',
    'agents/workers/diagnosis_agent.py',
]
 
for s in scripts:
    os.makedirs(os.path.dirname(s), exist_ok=True)
    if not os.path.exists(s):
        open(s, 'w').close()
        print(f'  Created: {s}')
    else:
        print(f'  Already exists: {s}')
print('\nAll script files ready. Now fill them in step by step!')