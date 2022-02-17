from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse


class User(AbstractUser):
    pass


class Category(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('index')


class Listing(models.Model):
    item_name= models.CharField(max_length=64)
    item_description= models.TextField()
    image = models.ImageField(upload_to='images', blank=True, null=True)
    start_time = models.DateTimeField(default= datetime.now())
    end_time = models.DateTimeField()
    start_bid= models.IntegerField()
    close_listing= models.BooleanField(default=False)
    watchlist= models.ManyToManyField(User, blank=True, related_name="watchlist")
    category= models.ForeignKey(Category,blank=True,null=True,on_delete=models.SET_NULL,related_name="auctions")
    user= models.ForeignKey(User,on_delete=models.CASCADE,related_name="profile")

    class Meta:
        ordering = ('-end_time',)
        
    def __str__(self):
        return f"Auction #{self.id}: {self.item_name} ({self.user.username})"

    def save(self, *args, **kwargs):
        self.start_time = datetime.now()
        super().save(*args, **kwargs)

    def is_finshed(self):
        if self.close_listing or self.end_time < timezone.now():
            self.close_listing = True
            return True
        else:
            return False


class Bid(models.Model):
    amount  = models.IntegerField()
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    class Meta:
        ordering = ('-amount',)

    def __str__(self):
        return f"${self.amount}"


class Comment(models.Model):
    message = models.TextField()
    time    = models.DateTimeField(default=datetime.now())
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    class Meta:
        ordering = ('-time',)

    def __str__(self):
        return f'{self.message}'