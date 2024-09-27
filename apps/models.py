from django.contrib.auth.models import AbstractBaseUser, BaseUserManager , PermissionsMixin
from django.db import models

class customuserManager(BaseUserManager):
    def create_user(self, username, email, full_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, full_name, password):
        user = self.create_user(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class customuser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = customuserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']
    
    def get_user_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has i need to add the list to access my database dont forget this aicha !!!.
        """
        return ['%s.%s' % (app_label, codename) for app_label, codename in self.get_all_permissions(obj)]
    
    def __str__(self):
        return self.username
 

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
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    volume_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Item{self.product_name}  - {self.unit_price} - {self.volume_price}"
    class Meta:
        db_table = 'apps_item'
        

class itemvariant(models.Model):
    variant_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(item, on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=50, blank=True, null=True)
    variant_value = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Variant {self.variant_name}: {self.variant_value} - {self.item}"
    class Meta:
        db_table = 'apps_itemvariant'
    
class lead(models.Model):
    lead = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=55, blank=True, null=True)
    contact_person = models.CharField(max_length=55, blank=True, null=True)
    position = models.CharField(max_length=55, blank=True, null=True)
    contact = models.CharField(max_length=55, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.company_name
    class Meta:
        db_table = 'apps_lead'
        

class leaddata(models.Model):
    id= models.AutoField(primary_key=True)
    lead = models.ForeignKey('lead', on_delete=models.CASCADE)
    owner = models.CharField(max_length=55, blank=True, null=True)
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)
    nextdate = models.DateField()
    revenue = models.DecimalField(max_digits=10, decimal_places=10, blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    number = models.DecimalField(max_digits=10, decimal_places=10, blank=True, null=True)
    score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    worker = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
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
     return f"leaddata {self.status or 'No Status'} - {self.score if self.score is not None else 0}" 
    class Meta:
        db_table = 'apps_leaddata'


class supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=35, blank=True, null=True)
    contact_info = models.CharField(max_length=35, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    categories_supplied = models.CharField(max_length=45, blank=True, null=True)
    payment_terms = models.CharField(max_length=45, blank=True, null=True)
    product_quality = models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    cost = models.FloatField(blank=True, null=True)
    interaction_quality = models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    feedback = models.TextField(max_length=100, blank=True, null=True)

    def __str__(self):
        return (f"supplier {self.supplier_name or 'Unknown'}: "
                f"ID {self.supplier} - "
                f"Contact: {self.contact_info }, "
                f"Address: {self.address }, "
                f"Categories: {self.categories_supplied }, "
                f"Payment Terms: {self.payment_terms }, "
                f"Product Quality: {self.product_quality }, "
                f"Cost: {self.cost}, "
                f"Interaction Quality: {self.interaction_quality}, "
                f"Feedback: {self.feedback }")
    class Meta:
        db_table = 'apps_supplier'


class bonreception(models.Model):
    delivery = models.AutoField(primary_key=True)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_address = models.CharField(max_length=100, blank=True, null=True)
    supplier_id = models.ForeignKey(supplier, on_delete=models.CASCADE)
    item = models.ForeignKey(item, on_delete=models.CASCADE)
    quantity_delivered = models.IntegerField(blank=True, null=True)
    unit_of_measure = models.CharField(max_length=50, blank=True, null=True)
    transportation_type = models.CharField(max_length=100, blank=True, null=True)
    variant_id = models.ForeignKey('itemvariant', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'apps_bonreception'
    def __str__(self):
        return f"bonreception {self.delivery} for {self.supplier}"
    class Meta:
        db_table = 'apps_bonreception'


class facture(models.Model):
    facture = models.AutoField(primary_key=True)
    datef = models.DateField(blank=True, null=True)
    addressf = models.CharField(max_length=100, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=55, blank=True, null=True)
    qte_facture = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ttc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product = models.ForeignKey(item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)                                                          
    variant = models.ForeignKey(itemvariant, on_delete=models.CASCADE) 
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"facture {self.facture} on {self.datef}"
    class Meta:
        db_table = 'apps_facture'    
    
    
class retour(models.Model):
    retour = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(supplier, on_delete=models.CASCADE)
    client = models.ForeignKey(customer, on_delete=models.CASCADE)
    produit = models.ForeignKey(item, on_delete=models.CASCADE)
    quantite_retournee = models.PositiveIntegerField()
    raison_retour = models.TextField(blank=True, null=True)
    date_retour = models.DateField(auto_now_add=True)
    livreur = models.CharField(max_length=55, blank=True, null=True)
    informations_supp = models.TextField(blank=True, null=True)
    numero_c = models.CharField(max_length=55, blank=True, null=True)
    statut_retour = models.CharField(max_length=50, default='en attente')
  
    def __str__(self):
        return f"retour de {self.client} pour {self.produit}"
    class Meta:
        db_table = 'apps_retour' 