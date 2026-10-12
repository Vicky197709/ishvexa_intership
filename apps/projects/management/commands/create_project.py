import secrets
from django.core.management.base import BaseCommand
from apps.projects.models import Project


class Command(BaseCommand):
    help = 'Create a new project with a generated API key'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Project name')

    def handle(self, *args, **options):
        name = options['name']
        
        # Generate secure API key
        api_key = secrets.token_urlsafe(32)
        
        # Create project
        project = Project.objects.create(
            name=name,
            api_key=api_key
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Project "{name}" created successfully!\n'
                f'API Key: {api_key}\n'
                f'Project ID: {project.id}'
            )
        )
