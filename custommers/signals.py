# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import *
from cores.xl_gan_nhan import *
from cores.xl_tach_tu import *


@receiver(post_save, sender=Target)
def target(sender, instance, created, **kwargs):   
    if created:
        print('tao moi')
    else:
        print('khac')