#!/usr/bin/python

from app import Application
from models import week_user
import autoAccount
print "Creating app"
applc = Application({})
print "Creating test"
week_user.test()
print autoAccount.check_valid_date()

