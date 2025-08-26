# Public Lists & Hierarchical Cards Technical Guide

## Overview

This guide covers the implementation of the public list browsing system and hierarchical cocktail card display system introduced in the StirCraft application.

## Public Lists System

### URL Structure
- `/public/` - Public lists index (browse all public lists)
- `/public/{id}/` - Public list detail with medium-detail cocktail cards
- `/lists/{id}/copy/` - Copy/fork a public list to your account

### Components

#### 1. Public Lists Index (`/public/`)
**Template**: `lists/list_feed.html`
**View**: `list_feed(request)`

Features:
- Search functionality across list names and descriptions
- Pagination support for large datasets
- Card-based grid layout with list metadata
- Direct links to public detail pages

```python
# View logic for public lists feed
def list_feed(request):
    lists = List.objects.filter(list_type='custom').select_related('creator')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        lists = lists.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(lists, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
```

#### 2. Public List Detail (`/public/{id}/`)
**Template**: `lists/public_detail.html`
**View**: `public_list_detail(request, list_id)`

Features:
- Medium-detail cocktail cards (shows more info than index cards)
- Copy list functionality for authenticated users
- Add to list dropdown for each cocktail
- Favorite button for each cocktail
- Professional layout with list metadata

```python
def public_list_detail(request, list_id):
    list_obj = get_object_or_404(List, id=list_id, list_type='custom')
    cocktails = list_obj.cocktails.all().order_by('name')
    
    # Get user's lists for dropdown (if authenticated)
    user_lists = None
    if request.user.is_authenticated:
        user_lists = List.objects.filter(creator=request.user)
```

#### 3. List Copying System
**Template**: `lists/copy_confirm.html`
**View**: `list_copy(request, list_id)`

Features:
- Fork-like functionality similar to cocktail forking
- Confirmation page explaining copy process
- Proper attribution with original creator information
- Full cocktail preservation from original list

```python
@login_required
def list_copy(request, list_id):
    original_list = get_object_or_404(List, id=list_id, list_type='custom')
    
    if request.method == 'POST':
        new_list = List.objects.create(
            name=f"{original_list.name} (Copy)",
            description=f"Copied from {original_list.creator.username}'s list: {original_list.description}",
            creator=request.user,
            list_type='custom',
            forked_from=original_list
        )
        new_list.cocktails.set(original_list.cocktails.all())
```

### Database Schema

#### List Model Enhancements
Added `forked_from` field to track list copying relationships:

```python
class List(models.Model):
    # ... existing fields ...
    
    forked_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forks',
        help_text="Original list this was copied from (if it's a fork)"
    )
```

## Hierarchical Cocktail Cards System

### Card Detail Levels

#### 1. Low-Detail Cards (`_cocktail_card_low.html`)
**Usage**: Index pages, search results, browse pages
**Content**: 
- Cocktail name and image
- Non-alcoholic badge (if applicable)
- Up to 2 flavor tags (excluding basic type tags)
- Color tag (pill-shaped with actual colors)
- Base spirit (fallback if no flavor tags)

```django
<!-- Priority: Non-alcoholic > Flavor Tags > Base Spirit -->
{% if not cocktail.is_alcoholic %}
    <span class="badge badge-nonalcoholic bg-success">Non-alcoholic</span>
{% endif %}

{% for tag in cocktail.get_flavor_tags %}
    <span class="badge badge-vibe tag-{{ tag.name|lower|slugify }}">{{ tag.name }}</span>
{% endfor %}
```

#### 2. Medium-Detail Cards (`_cocktail_card_medium.html`)
**Usage**: List detail pages, collection views
**Content**:
- Everything from low-detail cards
- Highest volume mixer information
- Vessel/glassware type
- Extended description or notes

#### 3. Full-Detail Cards (existing detail pages)
**Usage**: Individual cocktail pages
**Content**: Complete cocktail information

### Enhanced Model Methods

#### Cocktail Model Enhancements

```python
class Cocktail(models.Model):
    def get_base_spirit(self):
        """Get the highest volume alcoholic component."""
        alcoholic_components = self.components.filter(
            ingredient__alcohol_content__gt=0
        ).order_by('-amount')
        
        if alcoholic_components.exists():
            return alcoholic_components.first().ingredient.name
        return 'Non-alcoholic'
    
    def get_highest_volume_mixer(self):
        """Get the highest volume non-alcoholic component."""
        mixer_components = self.components.filter(
            ingredient__alcohol_content=0,
            ingredient__ingredient_type__in=['juice', 'soda', 'mixer', 'syrup', 'dairy']
        ).order_by('-amount')
        
        if mixer_components.exists():
            return mixer_components.first().ingredient.name
        return None
    
    def get_flavor_tags(self, limit=2):
        """Get flavor tags excluding basic drink type tags."""
        excluded_tags = ['cocktail', 'shot', 'alcoholic', 'drink', 'non-alcoholic', 'nonalcoholic']
        flavor_tags = []
        
        for tag in self.vibe_tags.all():
            if tag.name.lower() not in excluded_tags and len(flavor_tags) < limit:
                flavor_tags.append(tag)
        
        return flavor_tags
```

### CSS Enhancements

#### Dynamic Tag Coloring
50+ color classes for flavor tags with consistent theming:

```css
.tag-citrus { background-color: #ffd700; color: #495057; }
.tag-sweet { background-color: #e83e8c; color: white; }
.tag-bitter { background-color: #8b4513; color: white; }
/* ... additional flavor-specific colors ... */
```

#### Pill-Shaped Color Tags
Special styling for cocktail color indicators:

```css
.badge-color-pill {
    border-radius: 50px;
    padding: 0.35em 0.8em;
    border: 2px solid transparent;
    text-transform: capitalize;
}

.badge-color-pill[data-color="red"] { 
    background-color: #dc3545; 
    color: white; 
    border-color: #dc3545; 
}
```

## Integration Points

### Template Architecture
- **Modular Partials**: Separate templates for each detail level
- **Easy Maintenance**: Changes isolated to specific card types
- **Scalable Design**: Ready for future detail level additions

### AJAX Interactions
- **Real-time Feedback**: Visual indicators during form submissions
- **Progressive Enhancement**: Works without JavaScript
- **Error Handling**: Graceful degradation for failed requests

### Search Integration
- **Unified Search**: Consistent search patterns across lists and cocktails
- **Query Preservation**: Search terms maintained across pagination
- **Performance**: Optimized queries with proper indexing

## Best Practices

### Performance Considerations
- Use `select_related()` and `prefetch_related()` for related objects
- Implement pagination for large datasets
- Cache frequently accessed data where appropriate

### Security
- Proper authentication checks for copy operations
- CSRF protection on all forms
- Input validation and sanitization

### User Experience
- Clear visual hierarchy between detail levels
- Consistent interaction patterns
- Informative feedback messages
- Responsive design for all screen sizes

## Testing Strategy

### Unit Tests
- Model method testing for cocktail analysis
- View logic testing for all new endpoints
- Form validation testing for copy operations

### Integration Tests
- End-to-end list copying workflow
- Public list browsing and interaction
- Card display consistency across detail levels

### Frontend Tests
- JavaScript interaction testing
- AJAX operation validation
- Responsive design verification

## Future Enhancements

### Potential Improvements
- Advanced search with filters
- List categories and tagging
- User following and notifications
- Advanced analytics for popular lists
- Export functionality for lists
- Social sharing integration

---

*This technical guide covers the major architectural decisions and implementation details for the public lists and hierarchical card systems. For specific implementation questions, refer to the codebase or reach out to the development team.*
