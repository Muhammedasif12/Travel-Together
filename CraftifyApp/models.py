from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Login(AbstractUser):
    userType = models.CharField(max_length=100)
    viewPass = models.CharField(max_length=100, null=True)
    regDate = models.DateField(null=True)

    def __str__(self):
        return self.username


class Artist(models.Model):
    name = models.CharField(max_length=100,null=True)
    email = models.EmailField(max_length=100,null=True)
    phone = models.IntegerField(null=True)
    skills = models.CharField(max_length=200,null=True)
    image1 = models.ImageField(upload_to="image",null=True)
    image2 = models.ImageField(upload_to="image",null=True)
    image3 = models.ImageField(upload_to="image",null=True)
    address = models.CharField(max_length=300,null=True)
    status = models.CharField(max_length=100, default="Not Paid",null=True)
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE, default=1,null=True)

    def __str__(self):
        return self.name


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.IntegerField()
    address = models.CharField(max_length=300)
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.IntegerField()
    color = models.CharField(max_length=100)
    qty = models.IntegerField()
    image = models.ImageField(upload_to="image")
    desc = models.CharField(max_length=300)
    status = models.CharField(max_length=100, default="Pending")
    artistId = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)
    tripday = models.DateField(null = True)
    uploaded = models.DateField(auto_now_add=True,null = True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    pid = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    status = models.CharField(max_length=100, default="InCart")
    date = models.DateField(auto_now=True, null=True)
    name=models.CharField(max_length=100,null=True)
    email=models.EmailField(max_length=100,null=True)
    state=models.CharField(max_length=100,null=True)
    pincode=models.IntegerField(null=True)
    address=models.CharField(max_length=300,null=True)
    completedpay=models.IntegerField(null=True)
    proof = models.ImageField(upload_to='image/', null=True, blank=True)
    cancellation_reason = models.CharField(max_length=500, null=True, blank=True)
    cancelled_by = models.CharField(max_length=100, null=True, blank=True)


class Wishlist(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    pid = models.ForeignKey(Products, on_delete=models.CASCADE)


class Feedback(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    oid = models.ForeignKey(Cart, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.CharField(max_length=300)
    date = models.DateField(auto_now=True)


class Chat(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    artistid = models.ForeignKey(Artist, on_delete=models.CASCADE)
    message = models.CharField(max_length=300)
    date = models.DateField(auto_now=True)
    time = models.CharField(max_length=100)
    utype = models.CharField(max_length=100)



class GChat(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE,null = True)
    artistid = models.ForeignKey(Artist, on_delete=models.CASCADE,null = True)
    message = models.CharField(max_length=300,null = True)
    date = models.DateField(auto_now=True,null = True)
    time = models.TimeField(null = True, auto_now_add=True)
    utype = models.CharField(max_length=100,null = True)
    status = models.CharField(max_length=100,null = True)
    packages = models.ForeignKey(Products, on_delete=models.CASCADE,null = True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notif_type = models.CharField(max_length=100, default="general")

    def __str__(self):
        return self.message