import os
 
folders_needing_init = [
    'ml', 'ml/data', 'ml/training', 'ml/evaluation', 'ml/api',
    'ml/agents', 'ml/agents/workers',
]
 
for folder in folders_needing_init:
    init = os.path.join(folder, '__init__.py')
    if not os.path.exists(init):
        open(init, 'w').close()
        print(f'  Created: {init}')
    else:
        print(f'  Already exists: {init}')
 
# Also create processed/ folder if missing
os.makedirs('ml/data/processed', exist_ok=True)
print('\nDone! Python imports will now work correctly.')