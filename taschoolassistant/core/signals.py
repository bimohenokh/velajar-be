# from django.db import transaction
# from django.db.models import FileField
# from django.db.models.signals import post_delete
# from django.dispatch import receiver


# @receiver(post_delete)
# def delete_file_on_delete(sender, instance, **kwargs):
#     """
#     Delete the image file only after the database transaction is committed.
#     Not working in bulk delete
#     """
#     print("Signal delete_image_on_delete")
#     def cleanup():
#         for field in sender._meta.fields:
#             if isinstance(field, FileField):
#                 image = getattr(instance, field.name)
#                 if image:
#                     image.delete(save=False)
#
#     transaction.on_commit(cleanup)  # Ensures deletion happens only after commit

# TODO nyoba pake signal untuk update image
# @receiver(pre_save)
# def store_old_image(sender, instance, **kwargs):
#     """
#     Store old image before updating, using instance data (no extra DB queries).
#     Not working in bulk update
#     """
#     # Not working in bulk update
#     print("Signal store_old_image")
#     if instance.pk:  # Only for existing instances (not new ones)
#         instance._old_images = {
#             field.name: getattr(instance, field.name)
#             for field in sender._meta.fields if isinstance(field, models.FileField)
#         }
#
#
# @receiver(post_save)
# def delete_old_image_on_update(sender, instance, **kwargs):
#     """
#     Delete the old image file only after a successful update.
#     Not working in bulk update
#     """
#     print("Signal delete_old_image_on_update")
#     if not hasattr(instance, "_old_images"):  # Ensure attribute exists
#         return
#
#     old_images = instance._old_images  # Store reference before deleting
#
#     def cleanup():
#         for field_name, old_image in old_images.items():
#             new_image = getattr(instance, field_name)
#             if old_image and old_image != new_image:
#                 old_image.delete(save=False)
#
#         del instance._old_images  # Now safe to delete
#
#     transaction.on_commit(cleanup)  # Run cleanup only after transaction commits
