"""User role classes - business logic by role."""

from .base import User
from .applicant import Applicant
from .dean import DeanOffice
from .oidb import Oidb
from .ydyo import Ydyo
from .ygk import YGK

__all__ = ["User", "Applicant", "DeanOffice", "Oidb", "Ydyo", "YGK"]
