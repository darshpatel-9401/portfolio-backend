"""What each content type looks like. These match what the React portfolio shows.
To add a field: add a line here, then add it to the admin form (portfolio-admin/src/admin/resources.js)."""
from app.utils.validation import Bool, Email, Int, Str, StrList, Url

ABOUT = {
    "name": Str(True, 150), "title": Str(True, 150), "hero_text": Str(max=600), "profile_image": Url(),
    "journey_title": Str(max=100, default="My Journey"), "journey_text": Str(max=6000),
    "email": Str(max=255), "phone": Str(max=50), "location": Str(max=200),
    "github_url": Url(), "linkedin_url": Url(), "twitter_url": Url(), "dribbble_url": Url(), "resume_url": Url(),
    "cta_primary_text": Str(max=60, default="View Work"), "cta_secondary_text": Str(max=60, default="Contact Me"),
}

HIGHLIGHT = {  # the small cards in the About section
    "title": Str(True, 100), "icon": Str(max=50), "description": Str(max=300),
    "display_order": Int(default=0), "is_active": Bool(True),
}

SKILL = {  # one card per skill group, e.g. "Backend Development" with tags
    "title": Str(True, 100), "icon": Str(max=50), "description": Str(max=300), "tags": StrList(),
    "display_order": Int(default=0), "is_active": Bool(True),
}

PROJECT = {
    "title": Str(True, 200), "slug": Str(max=220), "description": Str(max=500), "full_description": Str(max=20000),
    "image": Url(), "tech": StrList(), "demo_url": Url(), "github_url": Url(),
    "featured": Bool(False), "published": Bool(True), "display_order": Int(default=0),
}

EXPERIENCE = {
    "role": Str(True, 200), "company": Str(True, 200), "duration": Str(max=100), "description": Str(max=3000),
    "display_order": Int(default=0), "is_active": Bool(True),
}

SERVICE = {
    "title": Str(True, 150), "description": Str(max=500), "icon": Str(max=50),
    "display_order": Int(default=0), "is_active": Bool(True),
}

TESTIMONIAL = {
    "name": Str(True, 150), "role": Str(max=150), "content": Str(True, 2000), "avatar": Url(),
    "display_order": Int(default=0), "is_active": Bool(True),
}

BLOG = {
    "title": Str(True, 250), "slug": Str(max=270), "description": Str(max=500),
    "content": Str(max=100000), "featured_image": Url(), "author": Str(max=150),
    "tags": StrList(15, 40), "seo_title": Str(max=250), "seo_description": Str(max=320),
    "is_published": Bool(False),
}

CONTACT = {
    "name": Str(True, 150), "email": Email(), "subject": Str(max=200), "message": Str(True, 5000),
}
