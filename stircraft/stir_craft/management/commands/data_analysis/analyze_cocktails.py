"""
Comprehensive Cocktail Database Analysis Command

This command provides detailed analysis and reporting capabilities for the
cocktail database, generating insights about usage patterns, data quality,
and content statistics.

Usage:
    python manage.py analyze_cocktails --output report.json
    python manage.py analyze_cocktails --health-check --verbose
    python manage.py analyze_cocktails --full-report --format csv
"""

import json
import csv
from pathlib import Path
from django.core.management.base import CommandError
from django.db.models import Count, Avg, Q
from collections import defaultdict, Counter
from ...utils.command_base import DataAnalysisCommand
from ...models import Cocktail, Ingredient, RecipeComponent, Vessel
from taggit.models import TaggedItem


class Command(DataAnalysisCommand):
    help = 'Comprehensive analysis and reporting for cocktail database'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Perform database health and integrity checks',
        )
        parser.add_argument(
            '--usage-stats',
            action='store_true',
            help='Generate usage statistics and popularity metrics',
        )
        parser.add_argument(
            '--ingredient-analysis',
            action='store_true',
            help='Analyze ingredient usage patterns and classification',
        )
        parser.add_argument(
            '--full-report',
            action='store_true',
            help='Generate comprehensive report with all analysis types',
        )

    def handle(self, *args, **options):
        """Execute the cocktail database analysis."""
        self.setup_command(options)
        
        self.output_file = options.get('output')
        self.output_format = options.get('format', 'text')
        
        # Determine which analyses to run
        analyses = []
        if options['full_report']:
            analyses = ['health', 'usage', 'ingredients', 'quality']
        else:
            if options['health_check']:
                analyses.append('health')
            if options['usage_stats']:
                analyses.append('usage')
            if options['ingredient_analysis']:
                analyses.append('ingredients')
        
        if not analyses:
            raise CommandError("Please specify at least one analysis type or use --full-report")
        
        self.log_info(f"Starting cocktail database analysis: {', '.join(analyses)}")
        
        try:
            results = {}
            
            if 'health' in analyses:
                results['health'] = self._health_check_analysis()
            
            if 'usage' in analyses:
                results['usage'] = self._usage_statistics_analysis()
            
            if 'ingredients' in analyses:
                results['ingredients'] = self._ingredient_analysis()
            
            if 'quality' in analyses:
                results['quality'] = self._data_quality_analysis()
            
            # Output results
            self._output_results(results)
            
            self.print_summary()
            
        except Exception as e:
            self.log_error(f"Analysis failed: {str(e)}")
            raise CommandError(f"Database analysis failed: {str(e)}")

    def _health_check_analysis(self):
        """
        Perform comprehensive database health checks.
        
        Returns:
            dict: Health check results and recommendations
        """
        self.log_info("🏥 Performing database health check...")
        
        health_results = {
            'overview': {},
            'integrity': {},
            'recommendations': []
        }
        
        # Basic counts
        total_cocktails = Cocktail.objects.count()
        total_ingredients = Ingredient.objects.count()
        total_components = RecipeComponent.objects.count()
        total_vessels = Vessel.objects.count()
        
        health_results['overview'] = {
            'total_cocktails': total_cocktails,
            'total_ingredients': total_ingredients,
            'total_recipe_components': total_components,
            'total_vessels': total_vessels,
            'avg_ingredients_per_cocktail': round(total_components / max(total_cocktails, 1), 2)
        }
        
        # Integrity checks
        cocktails_without_ingredients = Cocktail.objects.filter(components__isnull=True).count()
        cocktails_without_instructions = Cocktail.objects.filter(
            Q(instructions__isnull=True) | Q(instructions='')
        ).count()
        cocktails_without_images = Cocktail.objects.filter(
            Q(image__isnull=True) | Q(image='')
        ).count()
        
        ingredients_without_type = Ingredient.objects.filter(ingredient_type='other').count()
        ingredients_without_alcohol = Ingredient.objects.filter(
            alcohol_content__isnull=True
        ).count()
        
        components_without_units = RecipeComponent.objects.filter(
            Q(unit__isnull=True) | Q(unit='')
        ).count()
        
        health_results['integrity'] = {
            'cocktails_without_ingredients': cocktails_without_ingredients,
            'cocktails_without_instructions': cocktails_without_instructions,
            'cocktails_without_images': cocktails_without_images,
            'ingredients_without_classification': ingredients_without_type,
            'ingredients_without_alcohol_data': ingredients_without_alcohol,
            'components_without_units': components_without_units
        }
        
        # Generate recommendations
        recommendations = []
        
        if cocktails_without_ingredients > 0:
            recommendations.append(f"Fix {cocktails_without_ingredients} cocktails without ingredients")
        
        if cocktails_without_instructions > total_cocktails * 0.1:
            recommendations.append(f"Add instructions to {cocktails_without_instructions} cocktails")
        
        if ingredients_without_type > total_ingredients * 0.2:
            recommendations.append(f"Classify {ingredients_without_type} ingredients currently marked as 'other'")
        
        if components_without_units > 0:
            recommendations.append(f"Fix {components_without_units} recipe components missing units")
        
        health_results['recommendations'] = recommendations
        
        # Log health summary
        if recommendations:
            self.log_warning(f"Health check found {len(recommendations)} issues to address")
            for rec in recommendations:
                self.log_warning(f"  - {rec}")
        else:
            self.log_success("Database health check passed - no critical issues found")
        
        return health_results

    def _usage_statistics_analysis(self):
        """
        Analyze usage patterns and popularity metrics.
        
        Returns:
            dict: Usage statistics and trends
        """
        self.log_info("📊 Analyzing usage statistics...")
        
        usage_results = {
            'popular_ingredients': [],
            'popular_vessels': [],
            'cocktail_complexity': {},
            'alcoholic_distribution': {}
        }
        
        # Most popular ingredients
        ingredient_usage = RecipeComponent.objects.values(
            'ingredient__name'
        ).annotate(
            usage_count=Count('id')
        ).order_by('-usage_count')[:20]
        
        usage_results['popular_ingredients'] = [
            {
                'name': item['ingredient__name'],
                'usage_count': item['usage_count']
            }
            for item in ingredient_usage
        ]
        
        # Most popular vessels
        vessel_usage = Cocktail.objects.values(
            'vessel__name'
        ).annotate(
            usage_count=Count('id')
        ).order_by('-usage_count')[:10]
        
        usage_results['popular_vessels'] = [
            {
                'name': item['vessel__name'],
                'usage_count': item['usage_count']
            }
            for item in vessel_usage
        ]
        
        # Cocktail complexity analysis
        complexity_data = Cocktail.objects.annotate(
            ingredient_count=Count('components')
        ).aggregate(
            avg_ingredients=Avg('ingredient_count'),
            max_ingredients=Count('components')
        )
        
        # Complexity distribution
        complexity_distribution = defaultdict(int)
        for cocktail in Cocktail.objects.annotate(ingredient_count=Count('components')):
            if cocktail.ingredient_count <= 3:
                complexity_distribution['simple'] += 1
            elif cocktail.ingredient_count <= 6:
                complexity_distribution['moderate'] += 1
            else:
                complexity_distribution['complex'] += 1
        
        usage_results['cocktail_complexity'] = {
            'average_ingredients': round(complexity_data['avg_ingredients'] or 0, 2),
            'distribution': dict(complexity_distribution)
        }
        
        # Alcoholic vs non-alcoholic distribution
        alcoholic_stats = Cocktail.objects.aggregate(
            total=Count('id'),
            alcoholic=Count('id', filter=Q(is_alcoholic=True)),
            non_alcoholic=Count('id', filter=Q(is_alcoholic=False))
        )
        
        usage_results['alcoholic_distribution'] = {
            'total_cocktails': alcoholic_stats['total'],
            'alcoholic': alcoholic_stats['alcoholic'],
            'non_alcoholic': alcoholic_stats['non_alcoholic'],
            'alcoholic_percentage': round(
                (alcoholic_stats['alcoholic'] / max(alcoholic_stats['total'], 1)) * 100, 1
            )
        }
        
        self.log_success("Usage statistics analysis completed")
        return usage_results

    def _ingredient_analysis(self):
        """
        Analyze ingredient patterns and classification accuracy.
        
        Returns:
            dict: Ingredient analysis results
        """
        self.log_info("🧪 Analyzing ingredient patterns...")
        
        ingredient_results = {
            'type_distribution': {},
            'alcohol_content_stats': {},
            'orphaned_ingredients': [],
            'classification_accuracy': {}
        }
        
        # Ingredient type distribution
        type_distribution = Ingredient.objects.values('ingredient_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        ingredient_results['type_distribution'] = {
            item['ingredient_type']: item['count']
            for item in type_distribution
        }
        
        # Alcohol content statistics
        alcohol_stats = Ingredient.objects.filter(
            alcohol_content__isnull=False
        ).aggregate(
            avg_alcohol=Avg('alcohol_content'),
            max_alcohol=Count('alcohol_content'),
            min_alcohol=Count('alcohol_content')
        )
        
        ingredient_results['alcohol_content_stats'] = {
            'average_alcohol_content': round(alcohol_stats['avg_alcohol'] or 0, 2),
            'ingredients_with_alcohol_data': Ingredient.objects.filter(
                alcohol_content__isnull=False
            ).count(),
            'ingredients_missing_alcohol_data': Ingredient.objects.filter(
                alcohol_content__isnull=True
            ).count()
        }
        
        # Find orphaned ingredients (not used in any recipes)
        used_ingredient_ids = RecipeComponent.objects.values_list(
            'ingredient_id', flat=True
        ).distinct()
        
        orphaned_ingredients = Ingredient.objects.exclude(
            id__in=used_ingredient_ids
        ).values_list('name', flat=True)
        
        ingredient_results['orphaned_ingredients'] = list(orphaned_ingredients)
        
        # Classification accuracy assessment
        misclassified_count = 0
        total_checked = 0
        
        # Simple heuristic: check if 'other' category ingredients have obvious classifications
        other_ingredients = Ingredient.objects.filter(ingredient_type='other')
        
        for ingredient in other_ingredients:
            name_lower = ingredient.name.lower()
            total_checked += 1
            
            # Check for obvious spirit names
            spirits = ['vodka', 'gin', 'rum', 'whiskey', 'tequila', 'brandy']
            if any(spirit in name_lower for spirit in spirits):
                misclassified_count += 1
                continue
            
            # Check for obvious liqueur names
            liqueurs = ['liqueur', 'amaretto', 'kahlua', 'baileys']
            if any(liqueur in name_lower for liqueur in liqueurs):
                misclassified_count += 1
                continue
        
        ingredient_results['classification_accuracy'] = {
            'total_other_category': other_ingredients.count(),
            'potentially_misclassified': misclassified_count,
            'classification_accuracy_estimate': round(
                ((total_checked - misclassified_count) / max(total_checked, 1)) * 100, 1
            )
        }
        
        self.log_success("Ingredient analysis completed")
        return ingredient_results

    def _data_quality_analysis(self):
        """
        Analyze overall data quality and completeness.
        
        Returns:
            dict: Data quality metrics and scores
        """
        self.log_info("🔍 Analyzing data quality...")
        
        quality_results = {
            'completeness_scores': {},
            'consistency_checks': {},
            'overall_quality_score': 0
        }
        
        total_cocktails = Cocktail.objects.count()
        
        # Completeness scores
        cocktails_with_descriptions = Cocktail.objects.exclude(
            Q(description__isnull=True) | Q(description='')
        ).count()
        
        cocktails_with_instructions = Cocktail.objects.exclude(
            Q(instructions__isnull=True) | Q(instructions='')
        ).count()
        
        cocktails_with_images = Cocktail.objects.exclude(
            Q(image__isnull=True) | Q(image='')
        ).count()
        
        cocktails_with_tags = Cocktail.objects.filter(
            vibe_tags__isnull=False
        ).distinct().count()
        
        completeness_scores = {
            'descriptions': round((cocktails_with_descriptions / max(total_cocktails, 1)) * 100, 1),
            'instructions': round((cocktails_with_instructions / max(total_cocktails, 1)) * 100, 1),
            'images': round((cocktails_with_images / max(total_cocktails, 1)) * 100, 1),
            'tags': round((cocktails_with_tags / max(total_cocktails, 1)) * 100, 1)
        }
        
        quality_results['completeness_scores'] = completeness_scores
        
        # Consistency checks
        total_components = RecipeComponent.objects.count()
        components_with_units = RecipeComponent.objects.exclude(
            Q(unit__isnull=True) | Q(unit='')
        ).count()
        
        components_with_amounts = RecipeComponent.objects.exclude(
            Q(amount__isnull=True)
        ).count()
        
        consistency_scores = {
            'units_consistency': round((components_with_units / max(total_components, 1)) * 100, 1),
            'amounts_consistency': round((components_with_amounts / max(total_components, 1)) * 100, 1)
        }
        
        quality_results['consistency_checks'] = consistency_scores
        
        # Calculate overall quality score
        all_scores = list(completeness_scores.values()) + list(consistency_scores.values())
        overall_quality = round(sum(all_scores) / len(all_scores), 1)
        quality_results['overall_quality_score'] = overall_quality
        
        # Quality assessment
        if overall_quality >= 90:
            self.log_success(f"Excellent data quality: {overall_quality}%")
        elif overall_quality >= 75:
            self.log_info(f"Good data quality: {overall_quality}%")
        elif overall_quality >= 60:
            self.log_warning(f"Fair data quality: {overall_quality}%")
        else:
            self.log_error(f"Poor data quality: {overall_quality}%")
        
        return quality_results

    def _output_results(self, results):
        """Output analysis results in specified format."""
        if self.output_file:
            output_path = Path(self.output_file)
            
            try:
                if self.output_format == 'json':
                    with open(output_path, 'w') as f:
                        json.dump(results, f, indent=2, default=str)
                    self.log_success(f"Results saved to {output_path}")
                
                elif self.output_format == 'csv':
                    # Flatten results for CSV output
                    flattened = self._flatten_results(results)
                    with open(output_path, 'w', newline='') as f:
                        if flattened:
                            writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
                            writer.writeheader()
                            writer.writerows(flattened)
                    self.log_success(f"Results saved to {output_path}")
                
                else:  # text format
                    with open(output_path, 'w') as f:
                        self._write_text_report(f, results)
                    self.log_success(f"Results saved to {output_path}")
                    
            except Exception as e:
                self.log_error(f"Error saving results: {str(e)}")
        else:
            # Output to console
            self._write_text_report(None, results)

    def _flatten_results(self, results):
        """Flatten nested results for CSV output."""
        flattened = []
        
        for category, data in results.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (list, dict)):
                        continue  # Skip complex nested structures for CSV
                    flattened.append({
                        'category': category,
                        'metric': key,
                        'value': value
                    })
        
        return flattened

    def _write_text_report(self, file_handle, results):
        """Write results in human-readable text format."""
        def write_line(line=""):
            if file_handle:
                file_handle.write(line + "\n")
            else:
                self.stdout.write(line)
        
        write_line("=" * 60)
        write_line("STIRCRAFT DATABASE ANALYSIS REPORT")
        write_line("=" * 60)
        
        for category, data in results.items():
            write_line(f"\n{category.upper()} ANALYSIS")
            write_line("-" * 40)
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        write_line(f"{key}: {len(value)} items")
                        for item in value[:5]:  # Show first 5 items
                            if isinstance(item, dict):
                                write_line(f"  - {item}")
                            else:
                                write_line(f"  - {item}")
                        if len(value) > 5:
                            write_line(f"  ... and {len(value) - 5} more")
                    elif isinstance(value, dict):
                        write_line(f"{key}:")
                        for subkey, subvalue in value.items():
                            write_line(f"  {subkey}: {subvalue}")
                    else:
                        write_line(f"{key}: {value}")
        
        write_line("\n" + "=" * 60)
