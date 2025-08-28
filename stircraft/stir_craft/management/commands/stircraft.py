"""
StirCraft Master Data Management Command

This is the primary command for managing all data operations in StirCraft.
It provides a unified interface for running maintenance, import, and analysis
operations either individually or in automated sequences.

Usage Examples:
    # Run complete data maintenance sequence
    python manage.py stircraft --maintain-all --dry-run
    
    # Import fresh data from CocktailDB
    python manage.py stircraft --import-cocktails --limit 100
    
    # Run health check and generate report
    python manage.py stircraft --health-check --report
    
    # Complete workflow: import → maintain → analyze
    python manage.py stircraft --workflow=complete --verbose

Author: StirCraft Development Team
Date: August 2025
Version: 1.0
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction
from io import StringIO
import sys
from ..utils.command_base import StirCraftBaseCommand


class Command(StirCraftBaseCommand):
    """
    Master command for orchestrating all StirCraft data operations.
    
    This command serves as the primary interface for data management,
    providing both individual operation control and automated workflows
    for complex multi-step processes.
    
    Workflow Capabilities:
    1. Data Import: Fresh data from external sources
    2. Data Maintenance: Cleanup, normalization, integrity checks
    3. Data Analysis: Reporting and health monitoring
    4. Automated Sequences: Chained operations with dependency management
    
    Command Orchestration:
    The master command coordinates sub-commands while managing:
    - Shared transaction contexts
    - Progress aggregation across operations  
    - Error handling and recovery
    - Comprehensive reporting
    """
    
    help = 'Master command for all StirCraft data operations: import, maintain, analyze'

    def add_arguments(self, parser):
        super().add_common_arguments(parser)
        
        # Individual Operations
        import_group = parser.add_argument_group('Import Operations')
        import_group.add_argument(
            '--import-cocktails',
            action='store_true',
            help='Import cocktails from TheCocktailDB',
        )
        import_group.add_argument(
            '--import-limit',
            type=int,
            help='Limit number of cocktails to import',
        )
        
        # Maintenance Operations
        maintenance_group = parser.add_argument_group('Maintenance Operations')
        maintenance_group.add_argument(
            '--maintain-ingredients',
            action='store_true',
            help='Run ingredient maintenance (duplicates, categories, alcohol)',
        )
        maintenance_group.add_argument(
            '--maintain-units',
            action='store_true', 
            help='Standardize measurement units',
        )
        maintenance_group.add_argument(
            '--maintain-images',
            action='store_true',
            help='Check and fix image consistency',
        )
        maintenance_group.add_argument(
            '--maintain-tags',
            action='store_true',
            help='Clean and normalize tags',
        )
        maintenance_group.add_argument(
            '--maintain-all',
            action='store_true',
            help='Run all maintenance operations',
        )
        
        # Analysis Operations
        analysis_group = parser.add_argument_group('Analysis Operations')
        analysis_group.add_argument(
            '--analyze-cocktails',
            action='store_true',
            help='Analyze cocktail database and generate insights',
        )
        analysis_group.add_argument(
            '--health-check',
            action='store_true',
            help='Perform database health check',
        )
        analysis_group.add_argument(
            '--report',
            action='store_true',
            help='Generate comprehensive report',
        )
        
        # Automated Workflows
        workflow_group = parser.add_argument_group('Automated Workflows')
        workflow_group.add_argument(
            '--workflow',
            choices=['import', 'maintain', 'analyze', 'complete', 'daily'],
            help='Run predefined workflow sequence',
        )
        workflow_group.add_argument(
            '--force-workflow',
            action='store_true',
            help='Force workflow execution even if previous steps failed',
        )

    def handle(self, *args, **options):
        """Execute the master data management workflow."""
        self.setup_command(options)
        
        try:
            # Execute based on options
            if options.get('workflow'):
                self._run_workflow(options['workflow'], options)
            else:
                self._run_individual_operations(options)
            
            self.print_summary()
            
        except Exception as e:
            self.log_error(f"Master command failed: {str(e)}")
            raise CommandError(f"StirCraft data management failed: {str(e)}")

    def _run_workflow(self, workflow_name: str, options: dict):
        """
        Execute predefined workflow sequences.
        
        Workflows provide automated sequences of operations with proper
        dependency management and error handling between steps.
        """
        self.log_info(f"🚀 Starting '{workflow_name}' workflow")
        
        workflows = {
            'import': self._workflow_import,
            'maintain': self._workflow_maintain,  
            'analyze': self._workflow_analyze,
            'complete': self._workflow_complete,
            'daily': self._workflow_daily,
        }
        
        if workflow_name in workflows:
            workflows[workflow_name](options)
        else:
            raise CommandError(f"Unknown workflow: {workflow_name}")

    def _workflow_import(self, options: dict):
        """Import workflow: Fresh data from external sources."""
        self.log_info("📥 IMPORT WORKFLOW")
        self.log_info("=" * 40)
        
        steps = [
            ('Import Cocktails', 'data_import.import_cocktaildb', {
                'limit': options.get('import_limit'),
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            }),
        ]
        
        self._execute_workflow_steps(steps, options)

    def _workflow_maintain(self, options: dict):
        """Maintenance workflow: Cleanup and normalization.""" 
        self.log_info("🔧 MAINTENANCE WORKFLOW")
        self.log_info("=" * 40)
        
        steps = [
            ('Ingredient Maintenance', 'data_maintenance.maintain_ingredients', {
                'all': True,
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            }),
            ('Unit Standardization', 'data_maintenance.maintain_units', {
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            }),
            ('Image Consistency', 'data_maintenance.maintain_images', {
                'check_all': True,
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            }),
            ('Tag Cleanup', 'data_maintenance.maintain_tags', {
                'all': True,
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            }),
        ]
        
        self._execute_workflow_steps(steps, options)

    def _workflow_analyze(self, options: dict):
        """Analysis workflow: Generate insights and reports."""
        self.log_info("📊 ANALYSIS WORKFLOW") 
        self.log_info("=" * 40)
        
        steps = [
            ('Cocktail Analysis', 'data_analysis.analyze_cocktails', {
                'comprehensive': True,
                'verbose': self.verbose,
            }),
            ('Health Check', 'data_analysis.analyze_cocktails', {
                'health_check': True,
                'verbose': self.verbose,
            }),
        ]
        
        self._execute_workflow_steps(steps, options)

    def _workflow_complete(self, options: dict):
        """Complete workflow: Import → Maintain → Analyze."""
        self.log_info("🎯 COMPLETE WORKFLOW")
        self.log_info("=" * 40)
        
        # Run all workflows in sequence
        self._workflow_import(options)
        if not self.dry_run:  # Only proceed if not dry run
            self._workflow_maintain(options)
            self._workflow_analyze(options)

    def _workflow_daily(self, options: dict):
        """Daily workflow: Light maintenance and health checks."""
        self.log_info("📅 DAILY WORKFLOW")
        self.log_info("=" * 40)
        
        steps = [
            ('Quick Health Check', 'data_analysis.analyze_cocktails', {
                'health_check': True,
                'quick': True,
                'verbose': self.verbose,
            }),
            ('Image Check', 'data_maintenance.maintain_images', {
                'check_only': True,
                'verbose': self.verbose,
            }),
        ]
        
        self._execute_workflow_steps(steps, options)

    def _run_individual_operations(self, options: dict):
        """Execute individual operations based on command options."""
        operations_run = False
        
        # Import Operations
        if options.get('import_cocktails'):
            self._call_subcommand('data_import.import_cocktaildb', {
                'limit': options.get('import_limit'),
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            })
            operations_run = True
        
        # Maintenance Operations
        if options.get('maintain_all'):
            self._call_subcommand('data_maintenance.maintain_ingredients', {
                'all': True,
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            })
            self._call_subcommand('data_maintenance.maintain_units', {
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            })
            self._call_subcommand('data_maintenance.maintain_images', {
                'check_all': True,
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            })
            self._call_subcommand('data_maintenance.maintain_tags', {
                'all': True,
                'dry_run': self.dry_run,
                'verbose': self.verbose,
            })
            operations_run = True
        else:
            if options.get('maintain_ingredients'):
                self._call_subcommand('data_maintenance.maintain_ingredients', {
                    'all': True,
                    'dry_run': self.dry_run,
                    'verbose': self.verbose,
                })
                operations_run = True
            
            if options.get('maintain_units'):
                self._call_subcommand('data_maintenance.maintain_units', {
                    'dry_run': self.dry_run,
                    'verbose': self.verbose,
                })
                operations_run = True
            
            if options.get('maintain_images'):
                self._call_subcommand('data_maintenance.maintain_images', {
                    'check_all': True,
                    'dry_run': self.dry_run,
                    'verbose': self.verbose,
                })
                operations_run = True
            
            if options.get('maintain_tags'):
                self._call_subcommand('data_maintenance.maintain_tags', {
                    'all': True,
                    'dry_run': self.dry_run,
                    'verbose': self.verbose,
                })
                operations_run = True
        
        # Analysis Operations
        if options.get('analyze_cocktails'):
            self._call_subcommand('data_analysis.analyze_cocktails', {
                'comprehensive': True,
                'verbose': self.verbose,
            })
            operations_run = True
        
        if options.get('health_check'):
            self._call_subcommand('data_analysis.analyze_cocktails', {
                'health_check': True,
                'verbose': self.verbose,
            })
            operations_run = True
        
        if not operations_run:
            self.log_warning("No operations specified. Use --help to see available options.")
            self.log_info("Quick start: python manage.py stircraft --workflow=daily")

    def _execute_workflow_steps(self, steps: list, options: dict):
        """Execute a sequence of workflow steps with error handling."""
        total_steps = len(steps)
        force = options.get('force_workflow', False)
        
        for i, (step_name, command, step_options) in enumerate(steps, 1):
            self.log_info(f"🔄 Step {i}/{total_steps}: {step_name}")
            
            try:
                success = self._call_subcommand(command, step_options)
                if success:
                    self.log_success(f"✅ Completed: {step_name}")
                else:
                    self.log_warning(f"⚠️ Issues detected in: {step_name}")
                    if not force:
                        self.log_warning("Use --force-workflow to continue despite issues")
                        
            except Exception as e:
                self.log_error(f"❌ Failed: {step_name} - {str(e)}")
                if not force:
                    raise CommandError(f"Workflow stopped at step: {step_name}")

    def _call_subcommand(self, command_name: str, command_options: dict) -> bool:
        """
        Call a subcommand with error handling and output capture.
        
        Args:
            command_name: Django command name to execute
            command_options: Options dictionary for the command
            
        Returns:
            bool: True if command succeeded, False otherwise
        """
        try:
            # Capture output if not in verbose mode
            if not self.verbose:
                old_stdout = sys.stdout
                sys.stdout = captured_output = StringIO()
            
            # Execute the subcommand
            call_command(command_name, **command_options)
            
            # Restore output
            if not self.verbose:
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                # Only show errors and important messages
                for line in output.split('\n'):
                    if any(marker in line.lower() for marker in ['error', 'failed', 'warning', 'summary']):
                        self.stdout.write(line)
            
            self.changes_made += 1
            return True
            
        except Exception as e:
            if not self.verbose:
                sys.stdout = old_stdout
            self.log_error(f"Subcommand '{command_name}' failed: {str(e)}")
            return False
