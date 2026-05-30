"""
Management command: python manage.py clear_submissions [--test-only | --all] --confirm

Deletes OperatorReturn records and their cascaded children:
  LicenceReturn, VehicleEmission, VehicleRouteUsage,
  VehicleAccessibility, Declaration.

OperatorAccess records (tokens, emails) and seed data are NOT touched.

Flags:
  --test-only   Delete only submissions belonging to test operators (is_test=True).
  --all         Delete ALL submissions regardless of test flag.
  --confirm     Required — prevents accidental runs.
"""

from django.core.management.base import BaseCommand, CommandError
from returns.models import OperatorReturn, OperatorAccess


class Command(BaseCommand):
    help = 'Delete operator return submissions. Use --test-only or --all.'

    def add_arguments(self, parser):
        scope = parser.add_mutually_exclusive_group(required=True)
        scope.add_argument('--test-only', action='store_true',
                           help='Delete only submissions from test operators.')
        scope.add_argument('--all', action='store_true',
                           help='Delete ALL submissions (real and test).')
        parser.add_argument('--confirm', action='store_true',
                            help='Required flag — confirms you intend to delete.')

    def handle(self, *args, **options):
        test_only = options['test_only']
        delete_all = options['all']

        if test_only:
            test_pks = OperatorAccess.objects.filter(is_test=True).values_list('operator_return_id', flat=True)
            qs = OperatorReturn.objects.filter(pk__in=test_pks)
            scope_label = 'TEST submissions only'
        else:
            qs = OperatorReturn.objects.all()
            scope_label = 'ALL submissions'

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f'No submissions found for scope: {scope_label}.'))
            return

        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                f'This will permanently delete {count} return(s) ({scope_label}).\n'
                f'Re-run with --confirm to proceed:\n\n'
                f'  python manage.py clear_submissions '
                f'{"--test-only" if test_only else "--all"} --confirm\n'
            ))
            return

        deleted_total, breakdown = qs.delete()
        self.stdout.write(self.style.SUCCESS(
            f'Done. Deleted {scope_label}:\n'
            + '\n'.join(f'  {v} {k}' for k, v in breakdown.items() if v)
            + '\nOperator access tokens and seed data are unchanged.'
        ))
