"""Disk usage analysis module."""

from pathlib import Path
from core.utils import get_dir_size, format_size


class DiskAnalyzer:
    """Analyzes disk space usage for uv Python packages."""
    
    def __init__(self, base_path=None):
        """Initialize analyzer.
        
        Args:
            base_path: Base path to search for virtual environments.
                      Defaults to ~/code/python
        """
        self.home = Path.home()
        self.cache_dir = self.home / '.cache' / 'uv'
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = self.home / 'code' / 'python'
    
    def analyze_cache(self):
        """Analyze uv cache directory.
        
        Returns:
            tuple: (subdirs_dict, total_size_bytes)
        """
        if not self.cache_dir.exists():
            return None, 0
        
        total_size = get_dir_size(self.cache_dir)
        
        # Analyze subdirectories
        subdirs = {}
        if self.cache_dir.exists():
            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    size = get_dir_size(item)
                    subdirs[item.name] = size
        
        return subdirs, total_size
    
    def analyze_venvs(self):
        """Find all .venv directories in the base path.
        
        Returns:
            list: List of tuples (venv_path, size_bytes) sorted by size (largest first)
        """
        venvs = []
        
        for venv_path in self.base_path.rglob('.venv'):
            if venv_path.is_dir():
                size = get_dir_size(venv_path)
                venvs.append((venv_path, size))
        
        return sorted(venvs, key=lambda x: x[1], reverse=True)
    
    def analyze_packages(self, venv_path):
        """Analyze package sizes within a virtual environment.
        
        Args:
            venv_path: Path to virtual environment
            
        Returns:
            dict: Dictionary mapping package names to sizes (bytes)
        """
        packages = {}
        
        # Find site-packages directory
        site_packages_dirs = list(venv_path.glob('lib/python*/site-packages'))
        if not site_packages_dirs:
            return packages
        
        site_packages = site_packages_dirs[0]
        
        for item in site_packages.iterdir():
            if item.is_dir() and not item.name.endswith('.dist-info'):
                size = get_dir_size(item)
                if size > 0:
                    packages[item.name] = size
        
        return dict(sorted(packages.items(), key=lambda x: x[1], reverse=True))
    
    def get_summary(self):
        """Get summary of disk usage.
        
        Returns:
            dict: Summary with cache_size, venv_size, total_size (all in bytes)
        """
        cache_subdirs, cache_total = self.analyze_cache()
        venvs = self.analyze_venvs()
        venv_total = sum(size for _, size in venvs)
        
        return {
            'cache_size': cache_total,
            'venv_size': venv_total,
            'total_size': cache_total + venv_total,
            'cache_subdirs': cache_subdirs or {},
            'venv_count': len(venvs),
            'venvs': venvs
        }
    
    def format_summary(self, summary=None):
        """Format summary for display.
        
        Args:
            summary: Optional summary dict. If None, will generate one.
            
        Returns:
            str: Formatted summary string
        """
        if summary is None:
            summary = self.get_summary()
        
        lines = []
        lines.append(f"UV cache:        {format_size(summary['cache_size']):>15s}")
        lines.append(f"Virtual envs:    {format_size(summary['venv_size']):>15s}")
        lines.append(f"Total:           {format_size(summary['total_size']):>15s}")
        
        return '\n'.join(lines)

