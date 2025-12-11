"""Interactive menu system for the CLI tool."""

import sys
from pathlib import Path
from core.analyzer import DiskAnalyzer
from core.cleaner import Cleaner
from core.monitor import SpaceMonitor
from core.utils import format_size


class Menu:
    """Interactive menu for disk space management."""
    
    def __init__(self, base_path=None):
        """Initialize menu.
        
        Args:
            base_path: Base path for analysis. Defaults to ~/code/python
        """
        self.analyzer = DiskAnalyzer(base_path)
        self.cleaner = Cleaner(base_path)
        self.base_path = base_path
        self.running = True
    
    def display_header(self):
        """Display menu header with current usage."""
        summary = self.analyzer.get_summary()
        
        print("\n" + "=" * 80)
        print("UV Disk Space Manager")
        print("=" * 80)
        print(f"Current Usage: {format_size(summary['total_size']):>15s}")
        print(f"Cache:         {format_size(summary['cache_size']):>15s}")
        print(f"Virtual Envs:   {format_size(summary['venv_size']):>15s} ({summary['venv_count']} environments)")
        print("=" * 80)
    
    def display_menu(self):
        """Display main menu options."""
        print("\nOptions:")
        print("  1. Show detailed analysis")
        print("  2. Clean UV cache")
        print("  3. Remove unused virtual environments")
        print("  4. Remove specific virtual environment")
        print("  5. Show cleanup recommendations")
        print("  6. Monitor space (run uv command)")
        print("  7. Exit")
        print()
    
    def show_detailed_analysis(self):
        """Show detailed disk usage analysis."""
        print("\n" + "=" * 80)
        print("Detailed Analysis")
        print("=" * 80)
        
        # Cache analysis
        print("\nUV Cache Analysis")
        print("-" * 80)
        cache_subdirs, cache_total = self.analyzer.analyze_cache()
        if cache_total > 0:
            print(f"Total cache size: {format_size(cache_total)}")
            print(f"Location: {self.analyzer.cache_dir}")
            print()
            if cache_subdirs:
                print("Cache subdirectories:")
                for name, size in sorted(cache_subdirs.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {name:30s} {format_size(size):>15s}")
        else:
            print("No uv cache found")
        
        # Virtual environment analysis
        print("\nVirtual Environment Analysis")
        print("-" * 80)
        venvs = self.analyzer.analyze_venvs()
        if venvs:
            total_venv_size = sum(size for _, size in venvs)
            print(f"Total .venv size: {format_size(total_venv_size)}")
            print(f"Found {len(venvs)} virtual environment(s)")
            print()
            print("Virtual environments (sorted by size):")
            for venv_path, size in venvs:
                rel_path = venv_path.relative_to(self.analyzer.base_path.parent)
                print(f"  {str(rel_path):60s} {format_size(size):>15s}")
            
            # Show largest packages in largest venv
            if venvs:
                largest_venv_path, _ = venvs[0]
                print(f"\nLargest packages in: {largest_venv_path.relative_to(self.analyzer.base_path.parent)}")
                print("-" * 80)
                packages = self.analyzer.analyze_packages(largest_venv_path)
                if packages:
                    for name, size in list(packages.items())[:20]:
                        print(f"  {name:50s} {format_size(size):>15s}")
        else:
            print("No .venv directories found")
        
        print("\n" + "=" * 80)
        input("\nPress Enter to continue...")
    
    def clean_cache(self):
        """Clean UV cache with confirmation."""
        cache_subdirs, cache_total = self.analyzer.analyze_cache()
        
        if cache_total == 0:
            print("\nNo cache to clean.")
            input("Press Enter to continue...")
            return
        
        print(f"\nUV Cache Cleanup")
        print("-" * 80)
        print(f"Cache size: {format_size(cache_total)}")
        print(f"Location: {self.analyzer.cache_dir}")
        print()
        
        response = input("Do you want to clean the cache? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cache cleanup cancelled.")
            input("Press Enter to continue...")
            return
        
        print("\nCleaning cache...")
        result = self.cleaner.clean_cache()
        
        if result['success']:
            print(f"\nSuccess! Freed {format_size(result['size_freed'])}")
            if result.get('files_removed', 0) > 0:
                print(f"Removed {result['files_removed']} files")
        else:
            print(f"\nError: {result['message']}")
        
        input("\nPress Enter to continue...")
    
    def remove_unused_venvs(self):
        """Remove unused virtual environments with confirmation."""
        print("\nAnalyzing unused virtual environments...")
        candidates = self.cleaner.analyze_unused_venvs()
        
        if not candidates:
            print("\nNo unused virtual environments found.")
            print("All virtual environments appear to be in active use.")
            input("Press Enter to continue...")
            return
        
        print(f"\nFound {len(candidates)} potentially unused virtual environment(s):")
        print("-" * 80)
        
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{i}. {candidate['rel_path']}")
            print(f"   Size: {format_size(candidate['size'])}")
            print(f"   Days since activity: {candidate['days_since_activity']:.0f}")
            print(f"   Reasons: {', '.join(candidate['reasons'])}")
        
        print("\n" + "-" * 80)
        response = input("\nDo you want to remove these virtual environments? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Removal cancelled.")
            input("Press Enter to continue...")
            return
        
        total_freed = 0
        removed = 0
        failed = 0
        
        for candidate in candidates:
            print(f"\nRemoving {candidate['rel_path']}...")
            result = self.cleaner.remove_venv(candidate['venv_path'])
            if result['success']:
                total_freed += result['size_freed']
                removed += 1
                print(f"  Success! Freed {format_size(result['size_freed'])}")
            else:
                failed += 1
                print(f"  Error: {result['message']}")
        
        print(f"\n{'=' * 80}")
        print(f"Removed {removed} virtual environment(s)")
        if failed > 0:
            print(f"Failed to remove {failed} virtual environment(s)")
        print(f"Total space freed: {format_size(total_freed)}")
        print("=" * 80)
        
        input("\nPress Enter to continue...")
    
    def remove_specific_venv(self):
        """Remove a specific virtual environment."""
        venvs = self.analyzer.analyze_venvs()
        
        if not venvs:
            print("\nNo virtual environments found.")
            input("Press Enter to continue...")
            return
        
        print("\nSelect virtual environment to remove:")
        print("-" * 80)
        for i, (venv_path, size) in enumerate(venvs, 1):
            rel_path = venv_path.relative_to(self.analyzer.base_path.parent)
            print(f"  {i}. {str(rel_path):60s} {format_size(size):>15s}")
        
        print(f"  {len(venvs) + 1}. Cancel")
        print()
        
        try:
            choice = int(input("Enter number: ").strip())
            if choice < 1 or choice > len(venvs) + 1:
                print("Invalid choice.")
                input("Press Enter to continue...")
                return
            
            if choice == len(venvs) + 1:
                print("Cancelled.")
                input("Press Enter to continue...")
                return
            
            venv_path, size = venvs[choice - 1]
            rel_path = venv_path.relative_to(self.analyzer.base_path.parent)
            
            print(f"\nSelected: {rel_path}")
            print(f"Size: {format_size(size)}")
            print()
            
            response = input("Are you sure you want to remove this virtual environment? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Removal cancelled.")
                input("Press Enter to continue...")
                return
            
            print("\nRemoving virtual environment...")
            result = self.cleaner.remove_venv(venv_path)
            
            if result['success']:
                print(f"\nSuccess! Freed {format_size(result['size_freed'])}")
            else:
                print(f"\nError: {result['message']}")
            
            input("\nPress Enter to continue...")
        except ValueError:
            print("Invalid input. Please enter a number.")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
    
    def show_recommendations(self):
        """Show cleanup recommendations."""
        print("\n" + "=" * 80)
        print("Cleanup Recommendations")
        print("=" * 80)
        
        summary = self.analyzer.get_summary()
        candidates = self.cleaner.get_cleanup_candidates()
        
        recommendations = []
        
        # Cache recommendation
        if candidates['cache']:
            cache_size = candidates['cache']['size']
            if cache_size > 5 * 1024**3:  # > 5GB
                recommendations.append({
                    'type': 'cache',
                    'action': 'Clean UV cache',
                    'potential_savings': cache_size,
                    'description': f'UV cache is {format_size(cache_size)}. Safe to clean - packages will re-download when needed.'
                })
        
        # Venv recommendations
        if candidates['venvs']:
            total_venv_size = sum(v['size'] for v in candidates['venvs'])
            recommendations.append({
                'type': 'venvs',
                'action': f'Remove {len(candidates["venvs"])} unused virtual environment(s)',
                'potential_savings': total_venv_size,
                'description': f'Found {len(candidates["venvs"])} potentially unused virtual environments totaling {format_size(total_venv_size)}.'
            })
        
        # General recommendations
        if summary['venv_count'] > 10:
            recommendations.append({
                'type': 'general',
                'action': 'Review virtual environments',
                'potential_savings': 0,
                'description': f'You have {summary["venv_count"]} virtual environments. Consider removing unused ones.'
            })
        
        if not recommendations:
            print("\nNo specific recommendations at this time.")
            print("Your disk usage appears to be well-managed.")
        else:
            total_potential = sum(r['potential_savings'] for r in recommendations)
            print(f"\nPotential space savings: {format_size(total_potential)}")
            print()
            
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['action']}")
                print(f"   Potential savings: {format_size(rec['potential_savings'])}")
                print(f"   {rec['description']}")
                print()
        
        print("=" * 80)
        input("\nPress Enter to continue...")
    
    def monitor_command(self):
        """Monitor a uv command."""
        print("\nUV Command Monitor")
        print("-" * 80)
        print("Enter the uv command to monitor (e.g., 'uv add pandas' or 'uv sync')")
        print("Or type 'cancel' to go back")
        print()
        
        command = input("Command: ").strip()
        if command.lower() == 'cancel':
            return
        
        if not command.startswith('uv '):
            command = 'uv ' + command
        
        command_args = command.split()
        
        monitor = SpaceMonitor(self.base_path if self.base_path else None)
        monitor.monitor_command(command_args)
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the interactive menu loop."""
        while self.running:
            try:
                self.display_header()
                self.display_menu()
                
                choice = input("Select option: ").strip()
                
                if choice == '1':
                    self.show_detailed_analysis()
                elif choice == '2':
                    self.clean_cache()
                elif choice == '3':
                    self.remove_unused_venvs()
                elif choice == '4':
                    self.remove_specific_venv()
                elif choice == '5':
                    self.show_recommendations()
                elif choice == '6':
                    self.monitor_command()
                elif choice == '7':
                    print("\nExiting...")
                    self.running = False
                else:
                    print("\nInvalid option. Please select 1-7.")
                    input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                self.running = False
            except Exception as e:
                print(f"\nError: {e}")
                input("Press Enter to continue...")

