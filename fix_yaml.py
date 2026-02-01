import os
import yaml

folder = 'agents'
print("🔧 Starting YAML Fixer (UTF-8 Mode)...")

for filename in os.listdir(folder):
    if filename.endswith('.yaml'):
        path = os.path.join(folder, filename)
        
        try:
            # FIX: Force UTF-8 encoding to handle emojis/special chars
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 1. Fix spec_version
            data['spec_version'] = 'v1'

            # 2. Fix tools list (convert objects to simple strings)
            if 'tools' in data and isinstance(data['tools'], list):
                new_tools = []
                for t in data['tools']:
                    if isinstance(t, dict) and 'name' in t:
                        new_tools.append(t['name'])
                    elif isinstance(t, str):
                        new_tools.append(t)
                data['tools'] = new_tools

            # Save with UTF-8
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ Fixed: {filename}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

print("✨ All files updated!")