# Multiple Configuration Support

The School Classes Management System now supports multiple configuration files, allowing you to easily switch between different class setups.

## Quick Start

### Method 1: Easy Launcher (Recommended)
```bash
python run_with_config.py
```
This will show you available configurations and let you choose interactively.

### Method 2: Direct Command Line
```bash
# Use default config (classes.json)
python app.py

# Use specific config file
python app.py --config classes-secondary.json

# Use config with custom port
python app.py --config classes-secondary.json --port 5001

# Use config with debug mode
python app.py --config classes-secondary.json --debug

# Full example
python app.py --config classes-secondary.json --port 8080 --host 0.0.0.0 --debug
```

## Available Options

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--config` | `-c` | `classes.json` | Path to configuration file |
| `--port` | `-p` | `5000` | Port to run server on |
| `--host` | | `127.0.0.1` | Host to bind to |
| `--debug` | | `False` | Enable debug mode |

## Example Configurations

### classes.json (Default)
- الصفوف الأولى - الثالثة
- Primary grades configuration

### classes-secondary.json 
- الصفوف الرابعة - السادسة  
- Secondary grades configuration

## Creating Custom Configurations

1. Copy an existing config file:
   ```bash
   cp classes.json my-custom-config.json
   ```

2. Edit the new file to include your classes and settings

3. Run with your custom config:
   ```bash
   python app.py --config my-custom-config.json
   ```

## Configuration File Structure

```json
{
  "grades": {
    "Grade Name": {
      "name": "Display Name",
      "color": "CSS gradient",
      "classes": [
        {
          "name": "Class Name",
          "code": "class-code",
          "type": "section"
        }
      ]
    }
  },
  "school_info": {
    "school_name": "School Name",
    "event_title": "Event Title"
  },
  "settings": {
    "registration_password": "password",
    "admin_password": "admin_password"
  },
  "texts": {
    "registration_form_instruction": "Text",
    "student_name_placeholder": "Placeholder"
  }
}
```

## Tips

- Keep different configs for different events or grade levels
- Use descriptive filenames for your configurations
- Test configurations before important events
- Backup your configuration files

## Examples

```bash
# Elementary school event
python app.py --config elementary-grades.json --port 5000

# Middle school event  
python app.py --config middle-grades.json --port 5001

# High school event
python app.py --config high-grades.json --port 5002

# Testing configuration
python app.py --config test-config.json --debug --port 8000
```
