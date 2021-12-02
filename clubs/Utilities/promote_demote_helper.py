from ..Constants import consts
from django.shortcuts import render
promote_user = {consts.APPLICANT:consts.MEMBER, 
                consts.MEMBER:consts.OFFICER, 
                consts.OFFICER:consts.CLUB_OWNER,
                consts.CLUB_OWNER:consts.CLUB_OWNER}

demote_user = {consts.APPLICANT:consts.APPLICANT,
               consts.MEMBER:consts.MEMBER,
               consts.OFFICER:consts.MEMBER,
               consts.CLUB_OWNER:consts.OFFICER}