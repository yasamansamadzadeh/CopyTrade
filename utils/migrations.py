from django.db import migrations


class AddPeriodicTask(migrations.RunPython):
    def __init__(self, name, task, scheduler, **kwargs):
        def insert_task(apps, schema_editor):
            PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
            Scheduler = apps.get_model('django_celery_beat', scheduler)
            scheduler_arg_name = scheduler.removesuffix('Schedule').lower()

            try:
                scheduler_obj, _ = Scheduler.objects.get_or_create(**kwargs)
                PeriodicTask.objects.create(**{
                    scheduler_arg_name: scheduler_obj,
                    'name': name,
                    'task': task,
                })
            except Exception as e:
                raise RuntimeError('Cannot create periodic task with name %s' % name) from e

        def remove_task(apps, schema_editor):
            PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
            PeriodicTask.objects.filter(name=name).delete()

        super().__init__(insert_task, remove_task)
