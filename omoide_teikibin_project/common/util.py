from friend.models import Friendship as FS
from accounts.models import CustomUser as User
from typing import Literal,Optional
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

from typing import Literal

Status = Literal["friend", "incoming", "outgoing", "me", "none"]



def fs_to_status(fs:FS,me:User)->Status:
    match fs.status:
        case FS.Status.A2B:
            return "outgoing" if fs.user_a_id == me.id else "incoming"
        case FS.Status.B2A:
            return "outgoing" if fs.user_b_id == me.id else "incoming"
        case FS.Status.ACPT:
            return "friend"
        case _:
            return "none"

def post_query(before:str|None,after:str | None,raw_limit:str | None,qs):
        try:
            limit  = int(raw_limit)
        except (ValueError,TypeError):
            limit = 10
        
        if (limit is None) or (limit <= 0):
            limit = 10
        
        if before and after:
            raise ValidationError()
        
        if after:
            dt = parse_datetime(after)
            if not dt:
                raise ValidationError()
            qs = qs.filter(created_at__gt = dt)
        elif before:
            dt = parse_datetime(before)
            if not dt:
                raise ValidationError()
            qs = qs.filter(created_at__lt = dt)
            
        
        qs = qs.order_by("-created_at","-post_id")[:limit]
        
    
        return qs