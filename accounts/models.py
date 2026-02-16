from django.db import models
from django.contrib.auth.models import User
from PIL import Image
 
# Patient Models
class Patient(models.Model):
    pid = models.AutoField(primary_key=True)  
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    bloodgroup = models.CharField(max_length=3)
    casepaper = models.CharField(max_length=10, blank=True)
    otp = models.CharField(max_length=6, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='med_report')
    

    
    def __str__(self):
        return self.user.username
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        img=Image.open(self.image.path)
        if img.height > 400 or img.width > 400:
            output_size=(400,400)
            img.thumbnail(output_size)
            img.save(self.image.path)

            

    