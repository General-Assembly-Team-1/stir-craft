"""
StirCraft Management Command Utilities

This module provides shared utilities and base classes for Django management commands
in the StirCraft application. It consolidates common functionality to reduce code
duplication and ensure consistent behavior across all data processing commands.

Shared Functionality:
- Dry-run mode implementation
- Progress reporting and logging
- Database transaction handling
- Error handling and recovery
- Common validation patterns

Author: StirCraft Development Team
Date: August 2025
Version: 1.0
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from typing import Any, Dict, List, Optional
import sys


class StirCraftBaseCommand(BaseCommand):
    """
    Enhanced base class for StirCraft management commands.
    
    This class provides common functionality used across multiple commands:
    - Standardized dry-run implementation
    - Progress reporting utilities
    - Transaction management
    - Error handling patterns
    - Consistent logging format
    
    All StirCraft commands should inherit from this class to ensure
    consistent behavior and reduce code duplication.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dry_run = False
        self.verbose = False
        self.changes_made = 0
        self.errors_encountered = 0
    
    def add_common_arguments(self, parser):
        """
        Add common command line arguments used across multiple commands.
        
        Args:
            parser: Django argument parser object
        """
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without making actual modifications to the database',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress information and debug output',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each database transaction (default: 100)',
        )
    
    def setup_command(self, options: Dict[str, Any]) -> None:
        """
        Initialize command state from options.
        
        Args:
            options: Dictionary of command line options
        """
        self.dry_run = options.get('dry_run', False)
        self.verbose = options.get('verbose', False)
        self.batch_size = options.get('batch_size', 100)
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))
            self.stdout.write('=' * 60)
    
    def log_info(self, message: str, prefix: str = "ℹ️") -> None:
        """Log informational message with consistent formatting."""
        self.stdout.write(f"{prefix} {message}")
    
    def log_success(self, message: str, prefix: str = "✅") -> None:
        """Log success message with green styling."""
        self.stdout.write(self.style.SUCCESS(f"{prefix} {message}"))
    
    def log_warning(self, message: str, prefix: str = "⚠️") -> None:
        """Log warning message with yellow styling."""
        self.stdout.write(self.style.WARNING(f"{prefix} {message}"))
    
    def log_error(self, message: str, prefix: str = "❌") -> None:
        """Log error message with red styling."""
        self.stdout.write(self.style.ERROR(f"{prefix} {message}"))
        self.errors_encountered += 1
    
    def log_verbose(self, message: str, prefix: str = "🔧") -> None:
        """Log verbose message only if verbose mode is enabled."""
        if self.verbose:
            self.stdout.write(f"{prefix} {message}")
    
    def update_progress(self, current: int, total: int, item_name: str = "items") -> None:
        """
        Display progress information with percentage.
        
        Args:
            current: Current item number
            total: Total number of items
            item_name: Description of items being processed
        """
        if total > 0:
            percentage = (current / total) * 100
            self.stdout.write(f"📊 Progress: {current}/{total} {item_name} ({percentage:.1f}%)")
    
    def safe_execute(self, operation, description: str, **kwargs) -> bool:
        """
        Execute an operation safely with error handling and dry-run support.
        
        Args:
            operation: Function to execute
            description: Description of the operation for logging
            **kwargs: Arguments to pass to the operation
            
        Returns:
            bool: True if operation succeeded, False if it failed or was skipped (dry-run)
        """
        try:
            if self.dry_run:
                self.log_info(f"Would {description}")
                return False
            else:
                result = operation(**kwargs)
                self.changes_made += 1
                self.log_verbose(f"Completed: {description}")
                return True
        except Exception as e:
            self.log_error(f"Failed to {description}: {str(e)}")
            return False
    
    def batch_process(self, queryset, process_function, description: str = "items"):
        """
        Process a queryset in batches with transaction safety.
        
        Args:
            queryset: Django queryset to process
            process_function: Function to call for each item
            description: Description for progress reporting
        """
        total_items = queryset.count()
        processed = 0
        
        self.log_info(f"Processing {total_items} {description} in batches of {self.batch_size}")
        
        # Process in batches to avoid memory issues and enable transaction rollback
        for i in range(0, total_items, self.batch_size):
            batch = queryset[i:i + self.batch_size]
            
            try:
                with transaction.atomic():
                    for item in batch:
                        process_function(item)
                        processed += 1
                        
                        if processed % 10 == 0:  # Update progress every 10 items
                            self.update_progress(processed, total_items, description)
                
            except Exception as e:
                self.log_error(f"Error processing batch {i//self.batch_size + 1}: {str(e)}")
                continue
        
        self.update_progress(processed, total_items, description)
    
    def print_summary(self) -> None:
        """Print a summary of command execution results."""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📋 COMMAND SUMMARY")
        self.stdout.write("=" * 60)
        
        if self.dry_run:
            self.log_info("Mode: DRY RUN (no changes made)")
        else:
            self.log_success(f"Changes made: {self.changes_made}")
        
        if self.errors_encountered > 0:
            self.log_error(f"Errors encountered: {self.errors_encountered}")
        else:
            self.log_success("No errors encountered")


class DataMaintenanceCommand(StirCraftBaseCommand):
    """
    Base class for data maintenance commands.
    
    This class extends StirCraftBaseCommand with specific functionality
    for data cleanup, normalization, and integrity checks.
    """
    
    def add_arguments(self, parser):
        super().add_common_arguments(parser)
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix detected issues (use with caution)',
        )
    
    def setup_command(self, options: Dict[str, Any]) -> None:
        super().setup_command(options)
        self.auto_fix = options.get('fix', False)
        
        if self.auto_fix and not self.dry_run:
            self.log_warning("Auto-fix mode enabled - changes will be made automatically")


class DataImportCommand(StirCraftBaseCommand):
    """
    Base class for data import commands.
    
    This class provides functionality specific to importing data
    from external sources like APIs or files.
    """
    
    def add_arguments(self, parser):
        super().add_common_arguments(parser)
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of items to import',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force import even if data already exists',
        )
    
    def setup_command(self, options: Dict[str, Any]) -> None:
        super().setup_command(options)
        self.import_limit = options.get('limit')
        self.force_import = options.get('force', False)


class DataAnalysisCommand(StirCraftBaseCommand):
    """
    Base class for data analysis commands.
    
    This class provides functionality for analyzing existing data
    and generating reports or insights.
    """
    
    def add_arguments(self, parser):
        super().add_common_arguments(parser)
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for analysis results',
        )
        parser.add_argument(
            '--format',
            choices=['text', 'json', 'csv'],
            default='text',
            help='Output format for analysis results',
        )
