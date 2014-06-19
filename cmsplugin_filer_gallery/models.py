# -*- coding: utf-8 -*-
from django.db.models import SmallIntegerField, BooleanField
from django.utils.translation import ugettext_lazy as _
from django.db import models
from cms.models import CMSPlugin, Page
from positions.fields import PositionField

from datetime import datetime
from filer.fields.image import FilerImageField
ANIMATION_CHOICES = ('fade', 'flash', 'pulse', 'slide', 'fadeslide')
ANIMATION_CHOICES = tuple(enumerate(ANIMATION_CHOICES))

QUALITY_CHOICES = ('low', 'normal', 'high')
QUALITY_CHOICES = tuple(enumerate(QUALITY_CHOICES))

QUALITY_SIZE = ['320x200', '640x480', '800x600']

#INSTALLED_THEMES = ['classic', 'miniml']
#INSTALLED_THEMES = tuple(enumerate(INSTALLED_THEMES))
INSTALLED_THEMES = [
    ('classic', 'classic'),
    ('miniml', 'miniml')
]


class FilerGallery(CMSPlugin):

    animation = SmallIntegerField(_("animation"),
                                  choices=ANIMATION_CHOICES,
                                  default=0)
    first_animation = SmallIntegerField(_("first image animation"),
                                        choices=ANIMATION_CHOICES,
                                        default=0)

    quality = SmallIntegerField(_("Image quality"),
                                choices=QUALITY_CHOICES,
                                default=1)

    height = SmallIntegerField(_("Gallery height"), default=300,
                               null=True, blank=True,
                               help_text=_('Height of gallery'))

    width = SmallIntegerField(_("Gallery width"), default=None,
                              null=True, blank=True,
                              help_text=_('Leave empty for auto width'))

    autoplay_active = BooleanField(_("autoplay"), default=False,
                                   help_text=_('Start playing automatically'))
    
    autoplay_timeout = models.SmallIntegerField(
        _("autoplay timeout"),
        default=3000, help_text=_('Timeout for next picture in ms'))

    lightbox = models.BooleanField(
        _("lightbox"), default=True,
        help_text=_('show fullscreen image in lightbox'))

    imagecrop = models.BooleanField(
        _("ImageCrop"), default=False,
        help_text=_('If selected image will be cropped'))

    theme = models.CharField(choices=INSTALLED_THEMES,
                             help_text=_('Theme for current gallery'),
                             max_length=10,
                             default='classic')
    
    
    
    @property
    def autoplay(self):
        if not self.autoplay_active:
            return False
        return self.autoplay_timeout
    
    class Meta:
        verbose_name = _("django filer gallery")
        verbose_name_plural = _("django filer galleries")
    
    def copy_relations(self,old_plugin):
       for image in old_plugin.images.all():
           image.gallery = self
           image.pk = None
           image.save()
        
        
class GalleryImage(models.Model):
    gallery = models.ForeignKey(FilerGallery, related_name="images")
    image = FilerImageField(related_name="imagesss")
    active = models.BooleanField(_('Active'), default=True)
    pub_date = models.DateTimeField(default=datetime.now)   
    order = models.IntegerField(default=1)
    ordering = PositionField(collection='gallery')
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Gallery Image')
        verbose_name_plural = _('Gallery Images')

    def __unicode__(self):
        """Return the FilerImage name"""
        return u"%s" % self.image

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pub_date = self.image.date_taken
        super(GalleryImage, self).save(*args, **kwargs)