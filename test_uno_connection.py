#!/usr/bin/env python3
"""
Simple UNO connection test to debug LibreOffice connectivity
"""

import sys
import time

def test_uno_imports():
    """Test if UNO imports are working"""
    print("🔍 Testing UNO imports...")
    try:
        import uno
        print("✅ uno module imported successfully")
        
        from com.sun.star.beans import PropertyValue
        print("✅ PropertyValue imported successfully")
        
        from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK, LINE_BREAK
        print("✅ ControlCharacter imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ UNO import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def test_uno_connection():
    """Test UNO connection to LibreOffice"""
    print("\n🔍 Testing UNO connection...")
    try:
        import uno
        
        # Get local context
        local_context = uno.getComponentContext()
        print("✅ Local UNO context created")
        
        # Get resolver
        resolver = local_context.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_context
        )
        print("✅ UNO resolver created")
        
        # Try to connect to LibreOffice
        context = resolver.resolve(
            "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
        )
        print("✅ Connected to LibreOffice UNO bridge")
        
        # Get desktop
        desktop = context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", context
        )
        print("✅ Desktop service acquired")
        
        return desktop, context
        
    except Exception as e:
        print(f"❌ UNO connection failed: {e}")
        return None, None

def test_document_creation(desktop):
    """Test creating a simple document"""
    print("\n🔍 Testing document creation...")
    try:
        # Create new Writer document
        document = desktop.loadComponentFromURL(
            "private:factory/swriter", "_blank", 0, ()
        )
        print("✅ Writer document created")
        
        # Add some text
        text = document.Text
        cursor = text.createTextCursor()
        text.insertString(cursor, "Hello from UNO API!", False)
        print("✅ Text inserted successfully")
        
        # Save document
        temp_path = "/tmp/uno_test_document.odt"
        from com.sun.star.beans import PropertyValue
        save_props = (
            PropertyValue("FilterName", 0, "writer8", 0),
            PropertyValue("Overwrite", 0, True, 0)
        )
        
        document.storeAsURL(f"file://{temp_path}", save_props)
        print(f"✅ Document saved to: {temp_path}")
        
        # Close document
        document.close(True)
        print("✅ Document closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Document creation failed: {e}")
        return False

def main():
    """Run UNO connection diagnostics"""
    print("🧪 SQUIRT UNO CONNECTION DIAGNOSTICS")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_uno_imports():
        print("\n❌ UNO imports failed - check LibreOffice Python packages")
        return False
    
    # Test 2: Connection
    desktop, context = test_uno_connection()
    if not desktop:
        print("\n❌ UNO connection failed")
        print("💡 Try: killall soffice.bin && python3 test_uno_connection.py")
        return False
    
    # Test 3: Document creation
    if not test_document_creation(desktop):
        print("\n❌ Document creation failed")
        return False
    
    print("\n✅ ALL UNO TESTS PASSED!")
    print("🎉 LibreOffice UNO API is working correctly")
    print("📝 Ready to proceed with invoice generation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)