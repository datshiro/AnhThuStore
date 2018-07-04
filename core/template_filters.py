# -*- coding: utf-8 -*-


class TemplateFilter(object):
    @staticmethod
    def price(s):
        return "{:,.0f}".format(s)