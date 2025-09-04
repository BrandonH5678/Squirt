#!/usr/bin/env python3
"""
Test LibreOffice document opening methods for human-in-the-loop validation
Verify consistent and reliable opening of documents
"""

import subprocess
import time
import os

def test_opening_methods():
    """Test different methods of opening LibreOffice documents"""
    
    test_file = "/tmp/emily_sorel_invoice_uno.odt"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print("🔍 TESTING LIBREOFFICE OPENING METHODS")
    print("=" * 50)
    
    methods = [
        {
            'name': 'Method 1: Simple libreoffice command',
            'command': ['libreoffice', test_file],
            'background': True
        },
        {
            'name': 'Method 2: LibreOffice Writer specific',
            'command': ['libreoffice', '--writer', test_file],
            'background': True
        },
        {
            'name': 'Method 3: With DISPLAY environment',
            'command': ['libreoffice', test_file],
            'env': {'DISPLAY': ':0'},
            'background': True
        },
        {
            'name': 'Method 4: Using xdg-open (system default)',
            'command': ['xdg-open', test_file],
            'background': True
        }
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n📝 Testing {method['name']}")
        print("-" * 40)
        
        try:
            env = os.environ.copy()
            if 'env' in method:
                env.update(method['env'])
            
            if method.get('background', False):
                # Start in background and check if it worked
                process = subprocess.Popen(
                    method['command'], 
                    env=env,
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
                
                # Give it time to start
                time.sleep(2)
                
                # Check if LibreOffice GUI process is running
                check_result = subprocess.run(
                    ['pgrep', '-f', 'soffice.*gui'],
                    capture_output=True, text=True
                )
                
                if check_result.returncode == 0:
                    print(f"✅ {method['name']} - LibreOffice GUI started")
                    
                    print(f"✅ {method['name']} - LibreOffice GUI process detected")
                    print(f"   📋 Command: {' '.join(method['command'])}")
                    
                    # Check if window manager can see the window
                    window_check = subprocess.run(
                        ['wmctrl', '-l'], capture_output=True, text=True
                    )
                    
                    if 'LibreOffice' in window_check.stdout:
                        print(f"✅ {method['name']} - Window manager detects LibreOffice window")
                        
                        # This method works - close and return it
                        subprocess.run(['pkill', '-f', 'soffice'], capture_output=True)
                        time.sleep(2)
                        return method
                    else:
                        print(f"⚠️ {method['name']} - GUI process running but no window detected")
                        # Close processes and continue testing
                        subprocess.run(['pkill', '-f', 'soffice'], capture_output=True)
                        time.sleep(2)
                else:
                    print(f"❌ {method['name']} - No GUI process detected")
            else:
                # Foreground execution
                result = subprocess.run(method['command'], env=env, timeout=5)
                if result.returncode == 0:
                    print(f"✅ {method['name']} - Command executed successfully")
                else:
                    print(f"❌ {method['name']} - Command failed with code {result.returncode}")
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ {method['name']} - Timeout (may still be working)")
        except Exception as e:
            print(f"❌ {method['name']} - Error: {e}")
    
    print(f"\n❌ No reliable opening method found")
    return None

def recommend_opening_function(working_method):
    """Generate the recommended function based on working method"""
    if not working_method:
        return None
    
    print(f"\n📋 RECOMMENDED OPENING FUNCTION:")
    print("=" * 40)
    
    if 'xdg-open' in working_method['command']:
        function_code = '''def open_document_for_validation(file_path: str) -> bool:
    """Open document for human validation using system default application"""
    try:
        subprocess.Popen(['xdg-open', file_path], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"❌ Failed to open document: {e}")
        return False'''
    else:
        env_part = ""
        if working_method.get('env'):
            env_part = f"""
        env = os.environ.copy()
        env.update({working_method['env']})"""
        
        function_code = f'''def open_document_for_validation(file_path: str) -> bool:
    """Open document for human validation using LibreOffice"""
    try:{env_part}
        subprocess.Popen({working_method['command'][:-1] + ['file_path']}, {
            'env=env, ' if env_part else ''}
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"❌ Failed to open document: {{e}}")
        return False'''
    
    print(function_code)
    return function_code

def main():
    """Test LibreOffice opening methods and recommend best approach"""
    
    print("🧪 LIBREOFFICE OPENING METHOD VERIFICATION")
    print("Testing different ways to open documents for human validation")
    print()
    
    working_method = test_opening_methods()
    
    if working_method:
        print(f"\n✅ RELIABLE METHOD FOUND: {working_method['name']}")
        recommend_opening_function(working_method)
        
        print(f"\n📝 USE THIS METHOD IN UNO GENERATORS:")
        print("Add this function to your generator classes for consistent document opening")
        
    else:
        print(f"\n❌ NO RELIABLE METHOD FOUND")
        print("Manual opening may be required for human validation")
        print("Consider checking display settings and LibreOffice installation")

if __name__ == "__main__":
    main()