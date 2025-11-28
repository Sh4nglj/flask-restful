# -*- coding: utf-8 -*-
"""
Version migration documentation generator for Flask-RESTful API versioning system.
"""

import json
import difflib
from collections import defaultdict


class MigrationDocGenerator:
    """
    Generates migration documentation between API versions.
    """
    
    def __init__(self, api):
        """
        Initialize the migration document generator.
        
        :param api: The Flask-RESTful API instance
        :type api: flask_restful.Api
        """
        self.api = api
        self.versioned_resources = api.versioned_resources
        self.version_inheritance = api.version_inheritance
        self.conversion_rules = api.conversion_rules
        self.deprecated_versions = api.deprecated_versions
    
    def generate_migration_guide(self, from_version, to_version):
        """
        Generate a migration guide between two versions.
        
        :param from_version: Source version
        :type from_version: str
        
        :param to_version: Target version
        :type to_version: str
        
        :return: Migration guide as a dictionary
        :rtype: dict
        """
        guide = {
            'from_version': from_version,
            'to_version': to_version,
            'changes': [],
            'deprecations': [],
            'conversion_rules': [],
            'migration_steps': []
        }
        
        # Check if versions exist
        if from_version not in self.versioned_resources:
            guide['errors'] = ["Source version '{}' not found".format(from_version)]
            return guide
        
        if to_version not in self.versioned_resources:
            guide['errors'] = ["Target version '{}' not found".format(to_version)]
            return guide
        
        # Get resources for both versions
        from_resources = self.versioned_resources[from_version]
        to_resources = self.versioned_resources[to_version]
        
        # Find added resources
        added_resources = set(to_resources.keys()) - set(from_resources.keys())
        if added_resources:
            guide['changes'].append({
                'type': 'added',
                'resources': list(added_resources),
                'description': 'New resources added in version {}'.format(to_version)
            })
        
        # Find removed resources
        removed_resources = set(from_resources.keys()) - set(to_resources.keys())
        if removed_resources:
            guide['changes'].append({
                'type': 'removed',
                'resources': list(removed_resources),
                'description': 'Resources removed in version {}'.format(to_version)
            })
        
        # Find modified resources
        common_resources = set(from_resources.keys()) & set(to_resources.keys())
        modified_resources = []
        for resource_name in common_resources:
            from_resource = from_resources[resource_name]
            to_resource = to_resources[resource_name]
            
            if from_resource != to_resource:
                modified_resources.append(resource_name)
        
        if modified_resources:
            guide['changes'].append({
                'type': 'modified',
                'resources': modified_resources,
                'description': 'Resources modified in version {}'.format(to_version)
            })
        
        # Check deprecations
        if from_version in self.deprecated_versions:
            deprecation_date, sunset_date = self.deprecated_versions[from_version]
            guide['deprecations'].append({
                'version': from_version,
                'deprecation_date': deprecation_date,
                'sunset_date': sunset_date,
                'description': 'Version {} is deprecated'.format(from_version)
            })
        
        # Check conversion rules
        if from_version in self.conversion_rules and to_version in self.conversion_rules[from_version]:
            request_converter, response_converter = self.conversion_rules[from_version][to_version]
            guide['conversion_rules'].append({
                'from_version': from_version,
                'to_version': to_version,
                'has_request_converter': request_converter is not None,
                'has_response_converter': response_converter is not None,
                'description': 'Automatic conversion available between versions'
            })
        
        # Generate migration steps
        migration_steps = []
        
        if added_resources:
            migration_steps.append("Review and implement new resources: {}".format(', '.join(added_resources)))
        
        if removed_resources:
            migration_steps.append("Remove usage of deprecated resources: {}".format(', '.join(removed_resources)))
        
        if modified_resources:
            migration_steps.append("Update usage of modified resources: {}".format(', '.join(modified_resources)))
        
        if from_version in self.deprecated_versions:
            migration_steps.append("Migrate away from deprecated version {} before {}".format(from_version, sunset_date or 'unknown'))
        
        if migration_steps:
            guide['migration_steps'] = migration_steps
        
        return guide
    
    def generate_full_migration_guide(self):
        """
        Generate a full migration guide for all versions.
        
        :return: Full migration guide as a dictionary
        :rtype: dict
        """
        guide = {
            'versions': sorted(self.versioned_resources.keys()),
            'version_inheritance': self.version_inheritance,
            'deprecated_versions': self.deprecated_versions,
            'migration_paths': []
        }
        
        # Generate migration guides for all consecutive versions
        versions = sorted(self.versioned_resources.keys())
        for i in range(len(versions) - 1):
            from_version = versions[i]
            to_version = versions[i + 1]
            
            migration_guide = self.generate_migration_guide(from_version, to_version)
            guide['migration_paths'].append(migration_guide)
        
        return guide
    
    def generate_migration_guide_markdown(self, from_version, to_version):
        """
        Generate migration guide in Markdown format.
        
        :param from_version: Source version
        :type from_version: str
        
        :param to_version: Target version
        :type to_version: str
        
        :return: Markdown formatted migration guide
        :rtype: str
        """
        guide = self.generate_migration_guide(from_version, to_version)
        
        if 'errors' in guide:
            return "# Migration Guide Error\n\n" + "\n".join(guide['errors'])
        
        markdown = "# API Migration Guide: {} → {}\n\n".format(from_version, to_version)
        
        # Changes section
        if guide['changes']:
            markdown += "## Changes\n\n"
            for change in guide['changes']:
                markdown += "### {} Resources\n\n".format(change['type'].capitalize())
                markdown += "- {}\n\n".format(change['description'])
                for resource in change['resources']:
                    markdown += "  - {}\n".format(resource)
                markdown += "\n"
        
        # Deprecations section
        if guide['deprecations']:
            markdown += "## Deprecations\n\n"
            for deprecation in guide['deprecations']:
                markdown += "### Version {}\n\n".format(deprecation['version'])
                if deprecation['deprecation_date']:
                    markdown += "- Deprecation Date: {}\n".format(deprecation['deprecation_date'])
                if deprecation['sunset_date']:
                    markdown += "- Sunset Date: {}\n".format(deprecation['sunset_date'])
                markdown += "- Description: {}\n\n".format(deprecation['description'])
        
        # Conversion rules section
        if guide['conversion_rules']:
            markdown += "## Automatic Conversion\n\n"
            for rule in guide['conversion_rules']:
                markdown += "- From: {}\n".format(rule['from_version'])
                markdown += "- To: {}\n".format(rule['to_version'])
                markdown += "- Request Conversion: {}\n".format("Available" if rule['has_request_converter'] else "Not Available")
                markdown += "- Response Conversion: {}\n\n".format("Available" if rule['has_response_converter'] else "Not Available")
        
        # Migration steps section
        if guide['migration_steps']:
            markdown += "## Migration Steps\n\n"
            for i, step in enumerate(guide['migration_steps'], 1):
                markdown += "{}. {}\n\n".format(i, step)
        
        return markdown
    
    def generate_full_migration_guide_markdown(self):
        """
        Generate full migration guide in Markdown format.
        
        :return: Markdown formatted full migration guide
        :rtype: str
        """
        guide = self.generate_full_migration_guide()
        
        markdown = "# Full API Migration Guide\n\n"
        markdown += "## Versions\n\n"
        for version in guide['versions']:
            markdown += "- {}\n".format(version)
        
        markdown += "\n## Version Inheritance\n\n"
        for version, parent in guide['version_inheritance'].items():
            markdown += "- {} → {}\n".format(version, parent)
        
        markdown += "\n## Deprecated Versions\n\n"
        for version, (deprecation_date, sunset_date) in guide['deprecated_versions'].items():
            markdown += "- {}: Deprecated {}{}\n".format(
                version, 
                "since " + deprecation_date if deprecation_date else "",
                ", sunset " + sunset_date if sunset_date else ""
            )
        
        markdown += "\n## Migration Paths\n\n"
        for path in guide['migration_paths']:
            from_version = path['from_version']
            to_version = path['to_version']
            markdown += "---\n\n"
            markdown += "### {} → {}\n\n".format(from_version, to_version)
            
            if 'errors' in path:
                markdown += "**Error**: {}\n\n".format("\n".join(path['errors']))
                continue
            
            for change in path['changes']:
                markdown += "#### {} Resources\n\n".format(change['type'].capitalize())
                for resource in change['resources']:
                    markdown += "- {}\n".format(resource)
                markdown += "\n"
        
        return markdown


def generate_migration_diff(old_schema, new_schema):
    """
    Generate a diff between two API schemas.
    
    :param old_schema: Old API schema
    :type old_schema: dict
    
    :param new_schema: New API schema
    :type new_schema: dict
    
    :return: Diff between the two schemas
    :rtype: str
    """
    old_json = json.dumps(old_schema, indent=2, sort_keys=True)
    new_json = json.dumps(new_schema, indent=2, sort_keys=True)
    
    diff = difflib.unified_diff(
        old_json.splitlines(),
        new_json.splitlines(),
        lineterm='',
        fromfile='old_schema.json',
        tofile='new_schema.json'
    )
    
    return '\n'.join(diff)