import os
 
files = [
    ('ml/data/training_data.csv',                      'Step 5'),
    ('ml/data/anomaly_data.csv',                       'Step 6'),
    ('ml/data/demand_data.csv',                        'Step 7'),
    ('ml/data/processed/features_engineered.csv',      'Step 8'),
    ('ml/models/brake_failure_model.pkl',              'Step 9'),
    ('ml/models/label_encoder.pkl',                    'Step 9'),
    ('ml/models/anomaly_detector.pkl',                 'Step 10'),
    ('ml/models/demand_forecaster.pkl',                'Step 11'),
    ('ml/visualizations/feature_importance.png',       'Step 12'),
    ('ml/visualizations/model_accuracy.png',           'Step 12'),
    ('ml/visualizations/sensor_trends.png',            'Step 12'),
    ('ml/evaluation/accuracy_report.json',             'Step 9'),
    ('ml/api/predictions_api.py',                      'Step 14'),
    ('agents/workers/data_analysis_agent.py',          'Step 15'),
    ('agents/workers/diagnosis_agent.py',              'Step 16'),
]
 
done, missing = 0, []
for path, step in files:
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f'  ✓  {path}')
        done += 1
    else:
        print(f'  ✗  {path}  ← run {step}')
        missing.append((path, step))
 
print(f'\nProgress: {done}/{len(files)} files complete')
if not missing:
    print('✓ ALL FILES DONE — ready to run final test!')
else:
    print(f'Next step: {missing[0][1]} — create {missing[0][0]}')