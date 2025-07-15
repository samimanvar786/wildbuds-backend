from django.contrib import admin
from django.utils.html import mark_safe  # To safely render HTML in the admin
from django.forms import ModelForm
from django.conf import settings
from .models import Category,Product, ProductImage

class ProductImageForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(ProductImageForm, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.image:
            self.fields['image'].widget.attrs['readonly'] = 'readonly'  # Make the field readonly if it already has an image
            # Optionally, you could add a preview of the current image here
            
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Allows one extra form for adding images
    form = ProductImageForm  # Use the custom form to control how the image is displayed
    
    def image_preview(self, obj):
        default_image_url = f"{settings.SITE_URL}/media/defaults/default-product.png" 
        
        # Display image preview as thumbnail
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" />')
        return mark_safe(f'<img src="{default_image_url}" width="50" height="50" />')

    image_preview.short_description = 'Image Preview'  # Column name for the preview
    readonly_fields = ('image_preview',)  # Make image preview read-only
class ProductAdmin(admin.ModelAdmin):
    list_display = ( 'get_featured_image' ,'name', 'category', 'price', 'created_at')  # Show the featured image in list
    inlines = [ProductImageInline]

    # Custom method to show only the featured image in the admin table
    def get_featured_image(self, obj):
        # Fetch the first image or the image marked as featured for the product
        featured_image = obj.images.filter(is_featured=True).first()  # Assuming 'is_featured' is a field on ProductImage model

        if featured_image:
            # Return the image as a thumbnail
            return mark_safe(f'<img src="{featured_image.image.url}" width="80" height="80" />')
        
        return 'No featured image'

    get_featured_image.short_description = 'Image'  # Set the column name for the featured image
    get_featured_image.allow_tags = True  # Allow HTML tags for rendering the image
    
    
admin.site.register(Category)    
admin.site.register(Product,ProductAdmin)
        

