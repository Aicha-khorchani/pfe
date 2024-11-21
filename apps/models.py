from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, full_name, user_type='customuser' , password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name,
            user_type=user_type,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, full_name, password=None):
        user = self.create_user(
            username=username,
            email=email,
            full_name=full_name,
            user_type='admin',
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def create_livreur(self, username, email, full_name, number, company_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        
        livreur = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name,
            user_type='livreur',
        )
        livreur.number = number
        livreur.company_name = company_name
        livreur.set_password(password)
        livreur.save(using=self._db)
        return livreur

class customuser(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = [
        ('customuser', 'CustomUser'), 
        ('admin', 'AdminUser'),
        ('livreur', 'Livreurs'),
    ]
    username = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customuser')  # Default to CustomUser


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return self.username

class UserPermission(models.Model):
    user = models.ForeignKey(customuser, on_delete=models.CASCADE)
    permission = models.ForeignKey('auth.Permission', on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'permission'], name='unique_user_permission')
        ]    
    def __str__(self):
        return f"{self.user} - {self.permission}"
    

class AdminUser(customuser):
    position = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=50, blank=True)
    def __str__(self):
        return f"{self.full_name} - {self.position} in {self.department}"
    
    
class Livreurs(customuser):
    number = models.CharField(max_length=15, blank=True)  
    company_name = models.CharField(max_length=100, blank=True) 

    def __str__(self):
        return f"{self.full_name} ({self.username}) - {self.company_name}"
    class Meta:
        db_table = 'apps_Livreurs'
 

class customer(models.Model):
    customer_TYPE_CHOICES = [
        ('volume', 'Volume customer'),
        ('retail', 'Retail customer'),
    ]
    customer = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=20, null=True, blank=True)
    contact_person = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    customer_type = models.CharField(max_length=10, choices=customer_TYPE_CHOICES, default='retail')
    
    def __str__(self):
        return f"customer {self.customer_name} {self.contact_person} {self.email} {self.phone_number}"
    class Meta:
        db_table = 'apps_customer'
        

class item(models.Model):
    item = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volume_price = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    def __str__(self):
        return f"Item{self.product_name}  - {self.unit_price} - {self.volume_price}"
    class Meta:
        db_table = 'apps_item'
        

class itemvariant(models.Model):
    variant_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(item, on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=50, blank=True, null=True)
    variant_values = models.JSONField(default=list)
    def __str__(self):
        return f"Variant {self.variant_name}: {self.variant_values} - {self.item}"
    class Meta:
        db_table = 'apps_itemvariant'
        

  

class supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=35, blank=True, null=True)
    contact_info = models.CharField(max_length=35, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    categories_supplied = models.CharField(max_length=45, blank=True, null=True)
    payment_terms = models.CharField(max_length=45, blank=True, null=True)
    product_quality = models.IntegerField(blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    interaction_quality = models.IntegerField(blank=True, null=True)
    feedback = models.TextField( blank=True, null=True)

    def __str__(self):
        return (f"supplier {self.supplier_name or 'Unknown'}")
    class Meta:
        db_table = 'apps_supplier'     
      
        

    
class Stock(models.Model):
    item = models.ForeignKey(item, on_delete=models.CASCADE)
    item_variant = models.ForeignKey(itemvariant, on_delete=models.CASCADE)
    variant_combination = models.JSONField(default=dict)  
    quantity_available = models.IntegerField(default=0)  

    def __str__(self):
        return f"{self.item.product_name} - {self.item_variant.variant_name}: {self.quantity_available}"

    class Meta:
        db_table = 'apps_stock'
    
class lead(models.Model):
    lead = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=55, blank=True, null=True)
    contact_person = models.CharField(max_length=55, blank=True, null=True)
    position = models.CharField(max_length=55, blank=True, null=True)
    contact = models.CharField(max_length=55, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.company_name if self.company_name else "Unnamed Lead"
    class Meta:
        db_table = 'apps_lead'
        

class leaddata(models.Model):
    id= models.AutoField(primary_key=True)
    lead = models.ForeignKey('lead', on_delete=models.CASCADE)
    owner = models.CharField(max_length=55, blank=True, null=True)
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)
    nextdate = models.DateField(blank=True, null=True)
    revenue = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    worker = models.CharField(max_length=30, blank=True, null=True) 
    leadsrc = models.CharField(max_length=55, blank=True, null=True)
    sector = models.CharField(max_length=55, blank=True, null=True)
    status = models.CharField(max_length=100, choices=[
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('follow_up', 'Follow Up'),
        ('closed', 'Closed'),
    ] , blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.owner if self.owner else "No data provided"
    
    class Meta:
        db_table = 'apps_leaddata'




class bonreception(models.Model):
    delivery = models.AutoField(primary_key=True)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_address = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.ForeignKey(supplier, on_delete=models.CASCADE)

    class Meta:
        db_table = 'apps_bonreception'
    def __str__(self):
        return f"bonreception {self.delivery} for {self.delivery_address}"

class BonReceptionLine(models.Model):
    bon_reception = models.ForeignKey(bonreception, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(item, on_delete=models.CASCADE)  
    variant_combination = models.JSONField(default=dict)  
    quantity = models.IntegerField()  

    class Meta:
        db_table = 'apps_bonreception_line'

    def __str__(self):
        return f"{self.item.product_name} - {self.variant_combination} pcs"
    
    
class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    delivery_person = models.ForeignKey(Livreurs, on_delete=models.CASCADE, default=16)
    delivery_person_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.company_name} - {self.delivery_person}"
    class Meta:
        db_table = 'apps_Delivery'  
   

class Command(models.Model):
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    order_date = models.DateField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Command {self.id} for {self.customer}"
    class Meta:
        db_table = 'apps_Command'


class CommandLine(models.Model):
    command = models.ForeignKey(Command, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    variant_combination = models.JSONField(default=dict)

    def __str__(self):
        return f"Line {self.id} - {self.product.product_name} (x{self.quantity})"
    
    class Meta:
        db_table = 'apps_CommandLine'




class facture(models.Model):
    facture_id = models.AutoField(primary_key=True)
    datef = models.DateField(blank=True, null=True)
    addressf = models.CharField(max_length=100, blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)  
    discount = models.IntegerField(blank=True, null=True)  
    calculated_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  
    payment_method = models.CharField(max_length=55, blank=True, null=True)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    commands = models.ManyToManyField(Command, related_name='factures')

    def __str__(self):
        return f"Facture {self.facture_id} for {self.customer}"

    class Meta:
        db_table = 'apps_facture'



class retour(models.Model):
    retour = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(supplier, on_delete=models.CASCADE, blank=True, null=True)
    raison_retour = models.TextField(blank=True, null=True)
    date_retour = models.DateField(blank=True, null=True)
    livreur = models.ForeignKey(Livreurs, on_delete=models.CASCADE, default=16)
    informations_supp = models.TextField(blank=True, null=True)
    facture = models.ForeignKey(facture, on_delete=models.CASCADE) 
  
    def __str__(self):
        return f"retour de {self.raison_retour} pour {self.informations_supp}"
    class Meta:
        db_table = 'apps_retour' 
        

class Note(models.Model):
    note_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    command = models.ForeignKey(Command, on_delete=models.CASCADE)
    note =  models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Note for {self.customer.customer_name} -  {self.note}"

    class Meta: 
        db_table = 'apps_note'
        
        

class Notification(models.Model):
    user = models.ForeignKey(customuser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.message}"