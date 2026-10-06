from app.routes.crud import ORDER, blog_hook, blog_search, make_crud, project_hook
from app.utils import schemas

blueprints = [
    make_crud("highlights", schemas.HIGHLIGHT, public_filter={"is_active": True}),
    make_crud("skills", schemas.SKILL, public_filter={"is_active": True}),
    make_crud(
        "projects", schemas.PROJECT, public_filter={"published": True},
        public_sort=[("featured", -1)] + ORDER, hook=project_hook, by_slug=True,
    ),
    make_crud("experience", schemas.EXPERIENCE, public_filter={"is_active": True}),
    make_crud("services", schemas.SERVICE, public_filter={"is_active": True}),
    make_crud("testimonials", schemas.TESTIMONIAL, public_filter={"is_active": True}),
    make_crud(
        "blogs", schemas.BLOG, public_filter={"is_published": True},
        public_sort=[("published_at", -1)], admin_sort=[("created_at", -1)],
        hook=blog_hook, by_slug=True, hide_in_list=["content"], extra_query=blog_search,
    ),
]
