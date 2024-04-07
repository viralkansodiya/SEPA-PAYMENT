# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore (https://www.libracore.com) and contributors
# License: AGPL v3. See LICENCE

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from collections import defaultdict
import time
import html
from frappe.utils import flt, get_link_to_form, getdate, nowdate, now
from datetime import datetime


@frappe.whitelist()
def get_payments():
    payments = frappe.db.sql(
        """ Select pe.name, pe.posting_date, pe.paid_amount, pe.party, pe.party_name, pe.paid_from, pe.paid_to_account_currency, per.reference_doctype,
                                per.reference_name
                                From `tabPayment Entry` as pe
                                Left Join `tabPayment Entry Reference` as per ON per.parent = pe.name
                                left join `tabBank Account` as ba ON ba.party_type = per.reference_doctype and ba.party = per.reference_name
                                Where pe.docstatus = 0 and pe.payment_type = "Pay" and xml_file_generated = 0
                                order by posting_date
                                """,
        as_dict=1,
    )

    return {"payments": payments}


def generate_payment_file(payments):
    pass
