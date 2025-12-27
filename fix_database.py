"""
Fix for database.py - PyMongo boolean comparison issue
This script will fix the collection properties to use 'is not None' instead of truth testing
"""

import os

database_file = r'c:\Users\liuda\Documents\nutrigenomics\app\database.py'

# Read the file
with open(database_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the problematic patterns
old_patterns = [
    'return self.db.sessions if self.db else None',
    'return self.db.genetic_results if self.db else None',
    'return self.db.questionnaires if self.db else None',
    'return self.db.recommendations if self.db else None'
]

new_patterns = [
    'return self.db.sessions if self.db is not None else None',
    'return self.db.genetic_results if self.db is not None else None',
    'return self.db.questionnaires if self.db is not None else None',
    'return self.db.recommendations if self.db is not None else None'
]

# Apply replacements
for old, new in zip(old_patterns, new_patterns):
    if old in content:
        content = content.replace(old, new)
        print(f'✓ Fixed: {old[:30]}...')
    else:
        print(f'✗ Not found: {old[:30]}...')

# Write back
with open(database_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('\n[OK] database.py has been fixed!')
print('You can now run: python test_api.py genome_Joshua_Yoakem_v5_Full_20250129211749.txt')
