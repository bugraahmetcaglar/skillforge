from django.contrib import admin

# Customize admin site headers and titles
admin.site.site_header = "SkillForge Admin"
admin.site.site_title = "SkillForge Admin Portal" 
admin.site.index_title = "Welcome to SkillForge Administration"


# Set custom login form

# Set custom templates
admin.site.login_template = "admin/login.html"
admin.site.index_template = "admin/index.html"
