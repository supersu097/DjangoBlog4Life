#!/usr/bin/env python3
# coding = 'utf-8'
"""
@Time    : 2021/1/27-22:39
@Author  : sharp
@FileName: forms.py
@Software: PyCharm
@Blog    ：https://www.sharpgan.com/
"""
from django import forms
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from validate_email import validate_email


class CommentsFormForLoggedIn(forms.Form):
    comment_content = forms.CharField(label='评论', label_suffix='*',
                                      min_length=6, max_length=5000,
                                      widget=CKEditorWidget(config_name='comment_ckeditor'),
                                      error_messages={'min_length': '评论不能少于6个字',
                                                      'max_length': '昵称不能超过5000个字',
                                                      'required': '评论不能为空'})
    comment_parent = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'comment_parent', 'value': 0}))


class CommentsFormForNotLoggedIn(forms.Form):
    comment_content = forms.CharField(label='评论', label_suffix='*',
                                      min_length=6, max_length=5000,
                                      widget=CKEditorWidget(config_name='comment_ckeditor'),
                                      error_messages={'min_length': '评论不能少于6个字',
                                                      'max_length': '昵称不能超过5000个字',
                                                      'required': '评论不能为空'},
                                      )
    comment_parent = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'comment_parent', 'value': 0}))
    captcha = CaptchaField()

    user_name = forms.CharField(min_length=3, max_length=10,
                                label_suffix='*', label='昵称',
                                error_messages={'min_length': '昵称不能少于3位',
                                                'max_length': '昵称不能超过10位',
                                                'required': '昵称不能为空'})
    user_email = forms.EmailField(min_length=5, max_length=50,
                                  label_suffix='*', label='邮箱',
                                  error_messages={'min_length': '邮箱不能少于5位',
                                                  'max_length': '邮箱不能超过50位',
                                                  'required': '邮箱不能为空'})

    def clean_user_name(self):
        user_name = self.cleaned_data["user_name"]
        if "sharp" == user_name.strip().lower() or "admin" == user_name.strip().lower():
            raise ValidationError(
                "昵称不能为站长的用户名sharp或者admin")
        return user_name

    def clean_user_email(self):
        user_email = self.cleaned_data['user_email']
        is_valid = validate_email(email_address=user_email,
                                  smtp_from_address='hello@hello.com',
                                  smtp_helo_host='myhost', smtp_timeout=10, dns_timeout=10,
                                  check_blacklist=True, smtp_debug=True)
	if not is_valid:
            raise ValidationError(
                "你的邮箱好像不是有效的邮箱呢，检查一下哪里写错了哦~"
            )
        return user_email
