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


class salesorder(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_date} - {self.total_amount} - {self.customer}"
    class Meta:
        db_table = 'apps_salesorder'

class orderitem(models.Model):
    #product
    item = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(salesorder, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Item {self.order_id} {self.product_name} - {self.quantity} - {self.unit_price} - {self.total_price}"
    class Meta:
        db_table = 'apps_orderitem'
        

class itemvariant(models.Model):
    variant_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(orderitem, on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=50, blank=True, null=True)
    variant_value = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Variant {self.variant_name}: {self.variant_value} - {self.item}"
    class Meta:
        db_table = 'apps_itemvariant'
    
class centreddata(models.Model):
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
        db_table = 'apps_centreddata'
        

class adddata(models.Model):
    lead = models.ForeignKey('centreddata', on_delete=models.CASCADE)
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
        return self.lead
    class Meta:
        db_table = 'apps_adddata'


class supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=35, blank=True, null=True)
    contact_info = models.CharField(max_length=35, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    categories_supplied = models.CharField(max_length=45, blank=True, null=True)
    payment_terms = models.CharField(max_length=45, blank=True, null=True)
    product_quality = models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    cost = models.DecimalField(blank=True, decimal_places=10, max_digits=10, null=True)
    interaction_quality = models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    feedback = models.TextField(max_length=100, blank=True, null=True)

    def __str__(self):
        return (f"supplier {self.supplier_name or 'Unknown'}: "
                f"ID {self.supplier_id} - "
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


class deliverynote(models.Model):
    delivery = models.AutoField(primary_key=True)
    delivery_date = models.DateField(blank=True, null=True)
    customer_name = models.CharField(max_length=50, blank=True, null=True)
    delivery_address = models.CharField(max_length=100, blank=True, null=True)
    order = models.ForeignKey(salesorder, on_delete=models.CASCADE)
    item = models.ForeignKey(orderitem, on_delete=models.CASCADE)
    quantity_delivered = models.IntegerField(blank=True, null=True)
    unit_of_measure = models.CharField(max_length=50, blank=True, null=True)
    transportation_type = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Delivery Note {self.delivery} for {self.customer_name}"
    class Meta:
        db_table = 'apps_deliverynote'    


class invoicenote(models.Model):
    invoice = models.AutoField(primary_key=True)
    datef = models.DateField(blank=True, null=True)
    customer_name = models.CharField(max_length=50, blank=True, null=True)
    addressf = models.CharField(max_length=100, blank=True, null=True)
    item = models.ForeignKey(orderitem, on_delete=models.CASCADE)
    order = models.ForeignKey(salesorder, on_delete=models.CASCADE)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=55, blank=True, null=True)
    qte_facture = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    qte_delivred = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pc = models.CharField(max_length=55, blank=True, null=True)
    ttc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Invoice Note for {self.invoice} on {self.datef}"
    class Meta:
        db_table = 'apps_invoicenote'    
    
    
class retour(models.Model):
    RAISON_CHOICES = [
        ('defaut', 'Défaut de fabrication'),
        ('non_conforme', 'Produit non conforme'),
        ('autre', 'Autre'),
    ]

    client = models.ForeignKey(customer, on_delete=models.CASCADE)
    produit = models.ForeignKey(orderitem, on_delete=models.CASCADE)
    quantite_retournee = models.PositiveIntegerField()
    raison_retour = models.CharField(max_length=50, choices=RAISON_CHOICES)
    date_retour = models.DateField(auto_now_add=True)
    livreur = models.CharField(max_length=55, blank=True, null=True)
    informations_supp = models.TextField(blank=True, null=True)
    numero_c = models.CharField(max_length=55, blank=True, null=True)
    statut_retour = models.CharField(max_length=50, default='en attente')
  
    def __str__(self):
        return f"retour de {self.client} pour {self.produit}"
    class Meta:
        db_table = 'apps_retour' 