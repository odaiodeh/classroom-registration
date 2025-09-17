#!/usr/bin/env python3
"""
School Classes Management System - Configuration Launcher
This script makes it easy to run the app with different configurations.
"""

import sys
import subprocess
import os

def main():
    print("🏫 School Classes Management System - Config Launcher")
    print("=" * 55)
    
    # Available configurations
    configs = {
        '1': {'file': 'classes.json', 'name': 'الصفوف الأولى - الثالثة (الأساسي)'},
        '2': {'file': 'classes-secondary.json', 'name': 'الصفوف الرابعة - السادسة (الثانوي)'},
    }
    
    # Check which config files exist
    available_configs = {}
    for key, config in configs.items():
        if os.path.exists(config['file']):
            available_configs[key] = config
        else:
            print(f"⚠️  Config file '{config['file']}' not found - creating default...")
            
    if not available_configs:
        print("❌ No configuration files found!")
        return
    
    print("\nاختر الإعداد المطلوب:")
    print("Choose configuration:")
    for key, config in available_configs.items():
        print(f"  {key}. {config['name']} ({config['file']})")
    
    print(f"  c. Custom config file")
    print(f"  q. Quit")
    
    while True:
        choice = input("\nاختيارك (Your choice): ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            return
        
        if choice == 'c':
            config_file = input("Enter config file path: ").strip()
            if not os.path.exists(config_file):
                print(f"❌ File '{config_file}' not found!")
                continue
            break
        
        if choice in available_configs:
            config_file = available_configs[choice]['file']
            print(f"✅ Selected: {available_configs[choice]['name']}")
            break
        
        print("❌ Invalid choice. Please try again.")
    
    # Get port
    port = input("Port (default 5000): ").strip()
    if not port:
        port = "5000"
    
    # Get host
    host = input("Host (default 127.0.0.1): ").strip()
    if not host:
        host = "127.0.0.1"
    
    # Debug mode
    debug = input("Debug mode? (y/N): ").strip().lower()
    debug_flag = "--debug" if debug in ['y', 'yes'] else ""
    
    # Build command
    cmd = [
        sys.executable, "app.py",
        "--config", config_file,
        "--port", port,
        "--host", host
    ]
    
    if debug_flag:
        cmd.append(debug_flag)
    
    print(f"\n🚀 Starting server with:")
    print(f"   📁 Config: {config_file}")
    print(f"   🌐 URL: http://{host}:{port}")
    print(f"   🐛 Debug: {bool(debug_flag)}")
    print("=" * 55)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
