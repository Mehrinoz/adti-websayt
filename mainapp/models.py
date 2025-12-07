from django.db import models
from django.contrib.auth.models import User
class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)  # 📷 cover image
    file = models.FileField(upload_to='books/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='images/',blank=True,null=True)
    date_of_birth = models.DateField(blank=True,null=True)

    # class Meta:
    #     verbose_name ="Profil"

    def __str__(self):
        return f"{self.user.username} profili "


class TeamMember(models.Model):
    name = models.CharField(max_length=200, verbose_name='Ism')
    position = models.CharField(max_length=200, verbose_name='Lavozim')
    photo = models.ImageField(upload_to='team/', verbose_name='Rasm', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name='Biografiya')
    telegram = models.URLField(blank=True, verbose_name='Telegram link')
    instagram = models.URLField(blank=True, verbose_name='Instagram link')
    gmail = models.EmailField(blank=True, verbose_name='Gmail')
    order = models.PositiveIntegerField(default=0, verbose_name='Tartib raqami')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Jamoa a\'zosi'
        verbose_name_plural = 'Jamoa a\'zolari'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.position}"