#!/usr/bin/env python3
"""
Click Position Recorder for macOS
Records mouse click positions and saves them for later use
"""

import pyautogui as pg
from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller as KeyboardController
import json
import time
from datetime import datetime
from pathlib import Path
import threading
import signal
import sys

class ClickRecorder:
    def __init__(self, save_file="click_positions.json"):
        self.save_file = Path(save_file)
        self.positions = []
        self.is_recording = False
        self.current_session = []
        self.keyboard = KeyboardController()
        self.listener = None
        self.key_listener = None
        
        # Load existing positions if file exists
        if self.save_file.exists():
            with open(self.save_file, 'r') as f:
                self.positions = json.load(f)
        else:
            self.positions = []
    
    def start_recording(self):
        """Start recording mouse clicks"""
        if self.is_recording:
            print("Already recording!")
            return
        
        print("=" * 50)
        print("CLICK POSITION RECORDER")
        print("=" * 50)
        print("Click anywhere to record positions")
        print("Hotkeys:")
        print("  [SPACE] - Add name to last recorded position")
        print("  [ESC]   - Stop recording and save")
        print("  [S]     - Save current session")
        print("  [D]     - Delete last recorded position")
        print("  [C]     - Clear current session")
        print("=" * 50)
        
        self.is_recording = True
        self.current_session = []
        
        # Start mouse listener
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        
        # Start keyboard listener
        self.key_listener = keyboard.Listener(on_release=self.on_key_release)
        self.key_listener.start()
        
        print("Recording started. Click to record positions...")
    
    def stop_recording(self):
        """Stop recording and save positions"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.listener:
            self.listener.stop()
        if self.key_listener:
            self.key_listener.stop()
        
        # Save to file
        self.save_positions()
        
        print(f"\nRecording stopped.")
        print(f"Recorded {len(self.current_session)} positions in this session.")
        print(f"Total positions in file: {len(self.positions)}")
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if pressed and self.is_recording:
            # Record position
            pos_data = {
                "x": x,
                "y": y,
                "button": str(button),
                "timestamp": datetime.now().isoformat(),
                "session": len(self.current_session) + 1,
                "name": f"Position {len(self.current_session) + 1}"
            }
            
            self.current_session.append(pos_data)
            
            print(f"📌 Recorded position {len(self.current_session)}: ({x}, {y})")
    
    def on_key_release(self, key):
        """Handle keyboard hotkeys"""
        if not self.is_recording:
            return
        
        try:
            # Space: Add name to last position
            if key == Key.space:
                self.add_name_to_last()
            
            # Escape: Stop recording
            elif key == Key.esc:
                self.stop_recording()
                return False  # Stop listener
            
            # S: Save current session
            elif hasattr(key, 'char') and key.char == 's':
                self.save_session()
            
            # D: Delete last position
            elif hasattr(key, 'char') and key.char == 'd':
                self.delete_last_position()
            
            # C: Clear current session
            elif hasattr(key, 'char') and key.char == 'c':
                self.clear_session()
            
            # R: Print all positions
            elif hasattr(key, 'char') and key.char == 'r':
                self.print_all_positions()
            
            # P: Preview last position
            elif hasattr(key, 'char') and key.char == 'p':
                self.preview_last_position()
        
        except AttributeError:
            pass
    
    def add_name_to_last(self):
        """Add a custom name to the last recorded position"""
        if not self.current_session:
            print("No positions to name!")
            return
        
        try:
            name = input("\nEnter name for last position: ").strip()
            if name:
                self.current_session[-1]["name"] = name
                print(f"✓ Position renamed to: {name}")
        except EOFError:
            print("Name input cancelled.")
    
    def save_session(self):
        """Save current session to main positions list"""
        if not self.current_session:
            print("No positions to save!")
            return
        
        self.positions.extend(self.current_session)
        self.save_positions()
        
        print(f"✓ Session saved! Total positions: {len(self.positions)}")
    
    def save_positions(self):
        """Save all positions to JSON file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.positions, f, indent=2)
            print(f"✓ Positions saved to {self.save_file}")
        except Exception as e:
            print(f"Error saving positions: {e}")
    
    def delete_last_position(self):
        """Delete the last recorded position"""
        if not self.current_session:
            print("No positions to delete!")
            return
        
        removed = self.current_session.pop()
        print(f"✗ Deleted position: ({removed['x']}, {removed['y']})")
        print(f"Remaining in session: {len(self.current_session)}")
    
    def clear_session(self):
        """Clear current session"""
        if not self.current_session:
            print("Session is already empty!")
            return
        
        count = len(self.current_session)
        self.current_session.clear()
        print(f"✗ Cleared {count} positions from current session")
    
    def print_all_positions(self):
        """Print all recorded positions"""
        print("\n" + "=" * 50)
        print("ALL RECORDED POSITIONS")
        print("=" * 50)
        
        if not self.positions:
            print("No positions recorded yet.")
            return
        
        for i, pos in enumerate(self.positions, 1):
            print(f"{i:3}. {pos['name']:20} - ({pos['x']:4}, {pos['y']:4}) - {pos['timestamp'][:19]}")
    
    def preview_last_position(self):
        """Preview the last recorded position by moving mouse there"""
        if not self.current_session:
            print("No positions to preview!")
            return
        
        last_pos = self.current_session[-1]
        current_x, current_y = pg.position()
        
        print(f"Moving to: ({last_pos['x']}, {last_pos['y']}) - {last_pos['name']}")
        
        # Move mouse to the position
        pg.moveTo(last_pos['x'], last_pos['y'], duration=0.5)
        
        # Wait 2 seconds, then move back
        time.sleep(2)
        pg.moveTo(current_x, current_y, duration=0.5)
    
    def export_as_python(self, output_file="click_positions.py"):
        """Export positions as Python code"""
        with open(output_file, 'w') as f:
            f.write("# Auto-generated click positions\n")
            f.write("# Generated on: " + datetime.now().isoformat() + "\n\n")
            f.write("CLICK_POSITIONS = [\n")
            
            for pos in self.positions:
                f.write(f"    {{'name': '{pos['name']}', 'x': {pos['x']}, 'y': {pos['y']}}},\n")
            
            f.write("]\n\n")
            
            # Add helper functions
            f.write("def get_position(name):\n")
            f.write("    for pos in CLICK_POSITIONS:\n")
            f.write("        if pos['name'] == name:\n")
            f.write("            return (pos['x'], pos['y'])\n")
            f.write("    return None\n\n")
            
            f.write("def click_position(name, button='left'):\n")
            f.write("    pos = get_position(name)\n")
            f.write("    if pos:\n")
            f.write("        import pyautogui as pg\n")
            f.write("        pg.click(pos[0], pos[1], button=button)\n")
            f.write("        return True\n")
            f.write("    return False\n")
        
        print(f"✓ Positions exported to {output_file}")

# Standalone click position functions
def get_current_position(name=""):
    """Get current mouse position"""
    x, y = pg.position()
    print(f"Current position: ({x}, {y})")
    
    if name:
        return {"name": name, "x": x, "y": y, "timestamp": datetime.now().isoformat()}
    return x, y

def quick_record_clicks(num_clicks=5, delay=1):
    """Quickly record a specified number of clicks"""
    print(f"Quick recording {num_clicks} clicks...")
    print("Click on the target positions.")
    print(f"You have {delay} seconds between clicks.")
    
    positions = []
    
    for i in range(num_clicks):
        print(f"\nClick #{i+1}/{num_clicks} in {delay} seconds...")
        time.sleep(delay)
        
        print("CLICK NOW!")
        
        # Wait for click
        start_time = time.time()
        clicked = False
        
        def on_click(x, y, button, pressed):
            nonlocal clicked
            if pressed:
                positions.append({
                    "x": x,
                    "y": y,
                    "button": str(button),
                    "timestamp": datetime.now().isoformat(),
                    "name": f"Quick_{i+1}"
                })
                print(f"✓ Recorded: ({x}, {y})")
                clicked = True
        
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        
        # Wait for click or timeout
        while time.time() - start_time < 5 and not clicked:
            time.sleep(0.1)
        
        listener.stop()
    
    # Save the quick recording
    if positions:
        save_file = f"quick_clicks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(save_file, 'w') as f:
            json.dump(positions, f, indent=2)
        print(f"\n✓ Saved {len(positions)} positions to {save_file}")
    
    return positions

def main_menu():
    """Main menu for the click recorder"""
    recorder = ClickRecorder()
    
    while True:
        print("\n" + "=" * 50)
        print("CLICK POSITION RECORDER MENU")
        print("=" * 50)
        print("1. Start recording clicks")
        print("2. View all recorded positions")
        print("3. Quick record (fixed number of clicks)")
        print("4. Get current mouse position")
        print("5. Export positions as Python code")
        print("6. Test click at position")
        print("7. Clear all positions")
        print("0. Exit")
        print("=" * 50)
        
        choice = input("\nSelect option (0-7): ").strip()
        
        try:
            if choice == '1':
                recorder.start_recording()
                input("\nPress Enter to return to menu...")
            
            elif choice == '2':
                recorder.print_all_positions()
                input("\nPress Enter to return to menu...")
            
            elif choice == '3':
                try:
                    num = int(input("Number of clicks to record: "))
                    delay = float(input("Delay between clicks (seconds): "))
                    quick_record_clicks(num, delay)
                except ValueError:
                    print("Invalid input!")
                input("\nPress Enter to return to menu...")
            
            elif choice == '4':
                name = input("Name for this position (optional): ").strip()
                get_current_position(name)
                input("\nPress Enter to return to menu...")
            
            elif choice == '5':
                output_file = input("Output filename (default: click_positions.py): ").strip()
                if not output_file:
                    output_file = "click_positions.py"
                recorder.export_as_python(output_file)
                input("\nPress Enter to return to menu...")
            
            elif choice == '6':
                if not recorder.positions:
                    print("No positions to test!")
                else:
                    recorder.print_all_positions()
                    try:
                        index = int(input("\nEnter position number to test: ")) - 1
                        if 0 <= index < len(recorder.positions):
                            pos = recorder.positions[index]
                            print(f"Testing: {pos['name']} at ({pos['x']}, {pos['y']})")
                            pg.moveTo(pos['x'], pos['y'], duration=1)
                            time.sleep(1)
                            pg.click()
                            print("Clicked!")
                        else:
                            print("Invalid position number!")
                    except ValueError:
                        print("Invalid input!")
                input("\nPress Enter to return to menu...")
            
            elif choice == '7':
                confirm = input("Are you sure you want to clear ALL positions? (y/N): ").lower()
                if confirm == 'y':
                    recorder.positions = []
                    recorder.save_positions()
                    print("All positions cleared!")
                input("\nPress Enter to return to menu...")
            
            elif choice == '0':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice!")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            continue
        except Exception as e:
            print(f"Error: {e}")
            input("\nPress Enter to continue...")

def interactive_recorder():
    """Simple interactive recorder for quick use"""
    print("Interactive Click Recorder")
    print("Click anywhere to record positions.")
    print("Press Ctrl+C to stop.\n")
    
    positions = []
    
    def on_click(x, y, button, pressed):
        if pressed:
            pos = {
                "x": x,
                "y": y,
                "button": str(button),
                "timestamp": datetime.now().isoformat(),
                "name": f"Click_{len(positions)+1}"
            }
            positions.append(pos)
            print(f"#{len(positions)}: ({x}, {y})")
    
    with mouse.Listener(on_click=on_click) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            pass
    
    # Save positions
    if positions:
        filename = f"clicks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(positions, f, indent=2)
        print(f"\nSaved {len(positions)} positions to {filename}")

if __name__ == "__main__":
    print("Click Position Recorder for macOS")
    print("Use Ctrl+C to exit at any time\n")
    
    try:
        # Quick mode or menu mode
        mode = input("Quick mode? (y/N): ").lower()
        
        if mode == 'y':
            interactive_recorder()
        else:
            main_menu()
    
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
