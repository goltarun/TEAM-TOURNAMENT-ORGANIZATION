from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models import Player, Tournament, TournamentRegistration, News, ContactMessage

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_type', 'role', 'rank', 'age', 'contact', 'verified', 'created_at')
    list_filter = ('game_type', 'role', 'experience', 'playing_time', 'verified', 'created_at')
    search_fields = ('name', 'id_code', 'contact')
    list_editable = ('verified',)
    readonly_fields = ('created_at', 'updated_at')
    actions = []

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Support quick-verify buttons from custom player_list template:
        # ?verified=1 -> set verified=True
        # ?verified=0 -> set verified=False
        verified_param = request.GET.get('verified')
        if verified_param in ('1', '0'):
            try:
                # object_id is a string from URL; parse safely.
                obj_pk = int(object_id)
                obj = self.get_queryset(request).get(pk=obj_pk)
                obj.verified = (verified_param == '1')
                obj.save(update_fields=['verified'])
            except (Player.DoesNotExist, ValueError, TypeError):
                pass

            # Redirect back to avoid resubmission / keep admin flow clean.
            from django.shortcuts import redirect
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            return redirect(f'/admin/squad/player/{object_id}/change/')

        # IMPORTANT:
        # Django 5.1 template context copy can error in some envs.
        # Just use the built-in ModelAdmin implementation.
        return super(PlayerAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'game_type', 'role', 'rank', 'age', 'verified')
        }),
        ('Contact Details', {
            'fields': ('id_code', 'contact')
        }),
        ('Additional Information', {
            'fields': ('experience', 'playing_time', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'prize', 'entry_fee', 'date', 'time', 'game_mode', 'mode', 'status', 'get_registrations_count', 'get_available_slots')
    list_filter = ('status', 'game_mode', 'mode', 'date', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'get_registrations_count', 'get_available_slots')
    actions = None

    class Media:
        js = ('admin/js/tournament_slots.js',)
    
    fieldsets = (
        ('Tournament Details', {
            'fields': ('title', 'description', 'status')
        }),
        ('Prize Information', {
            'fields': ('prize', 'entry_fee', 'per_kill')
        }),
        ('Schedule', {
            'fields': ('date', 'time')
        }),
        ('Game Settings', {
            'fields': ('game_mode', 'mode', 'map_name', 'max_slots')
        }),
        ('Rules', {
            'fields': ('rules',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_registrations_count(self, obj):
        count = obj.registrations.count()
        color = 'green' if count > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, count
        )
    get_registrations_count.short_description = 'Registrations'

    def get_available_slots(self, obj):
        return format_html(
            '<span style="color: orange; font-weight: bold;">{}</span>',
            obj.available_slots
        )
    get_available_slots.short_description = 'Available Slots'

    def response_add(self, request, obj, post_url_continue=None):
        from django.shortcuts import redirect
        return redirect('tournament_list')

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        return redirect('tournament_list')

@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'tournament', 'team_name', 'slot_number', 'payment_status', 'registered_at')
    list_filter = ('payment_status', 'tournament', 'registered_at')
    search_fields = ('player_name', 'team_name', 'contact_number')
    list_editable = ('payment_status',)
    readonly_fields = ('registered_at',)
    
    fieldsets = (
        ('Registration Details', {
            'fields': ('tournament', 'player_name', 'team_name', 'slot_number')
        }),
        ('Contact Information', {
            'fields': ('contact_number',)
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_amount')
        }),
        ('Admin Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('registered_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tournament')

    def response_add(self, request, obj, post_url_continue=None):
        from django.shortcuts import redirect
        return redirect('registration_list')

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        return redirect('registration_list')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['make_active_yes', 'make_active_no']
    
    @admin.action(description='Active: Set to Yes')
    def make_active_yes(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='Active: Set to No')
    def make_active_no(self, request, queryset):
        queryset.update(is_active=False)
        
    def response_add(self, request, obj, post_url_continue=None):
        from django.shortcuts import redirect
        return redirect('news_list')

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        return redirect('news_list')
    
    fieldsets = (
        ('News Content', {
            'fields': ('title', 'content', 'date_display')
        }),
        ('Publication', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)
    actions = ['make_read_yes', 'make_read_no']
    
    @admin.action(description='Read: Set to Yes')
    def make_read_yes(self, request, queryset):
        queryset.update(is_read=True)
    
    @admin.action(description='Read: Set to No')
    def make_read_no(self, request, queryset):
        queryset.update(is_read=False)
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message Content', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# Custom Admin Site Configuration
admin.site.site_header = 'FF Squad Maker Administration'
admin.site.site_title = 'FF Squad Maker Admin'
admin.site.index_title = 'Welcome to FF Squad Maker Admin Panel'
