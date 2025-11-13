import os
import yaml


SETTINGS_FILE = os.path.join(os.getcwd(), 'totoro.yaml')

def load_settings():
    with open(SETTINGS_FILE, 'r') as f:
        return yaml.safe_load(f)

def save_settings(config: dict):
    """
    Save settings back to totoro.yaml file.
    Preserves YAML formatting and comments as much as possible.
    """
    with open(SETTINGS_FILE, 'w') as f:
        yaml.safe_dump(
            config,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=2
        )

def save_deployment_target(tag: str, target_config: dict):
    """
    Add a new deployment target while preserving file formatting.
    Only modifies the deployment_targets section to keep blank lines intact.
    """
    with open(SETTINGS_FILE, 'r') as f:
        lines = f.readlines()
    
    # Find the deployment_targets section and where to insert
    in_deployment_targets = False
    insert_index = None
    base_indent = 0
    
    for i, line in enumerate(lines):
        # Found the deployment_targets section
        if line.strip().startswith('deployment_targets:'):
            in_deployment_targets = True
            base_indent = len(line) - len(line.lstrip())
            continue
        
        if in_deployment_targets:
            stripped = line.strip()
            
            # Empty line - continue looking
            if not stripped:
                continue
            
            # Check if we've moved to the next top-level section
            current_indent = len(line) - len(line.lstrip())
            
            # If we hit a line at the same indent level as deployment_targets (or less), 
            # and it's a key (ends with :), we've left the section
            if current_indent <= base_indent and stripped.endswith(':'):
                insert_index = i
                break
    
    # If we didn't find a next section, insert at the end
    if insert_index is None:
        insert_index = len(lines)
    
    # Build the new deployment target entry with proper indentation
    entry_indent = ' ' * (base_indent + 2)
    value_indent = ' ' * (base_indent + 4)
    
    new_lines = [
        f"{entry_indent}{tag}:\n",
        f"{value_indent}host: {target_config['host']}\n",
        f"{value_indent}engine: {target_config['engine']}\n",
        f"{value_indent}env_file: {target_config['env_file']}\n",
    ]
    
    # Insert the new lines
    for j, new_line in enumerate(new_lines):
        lines.insert(insert_index + j, new_line)
    
    # Write back to file
    with open(SETTINGS_FILE, 'w') as f:
        f.writelines(lines)