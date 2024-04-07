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
from itertools import groupby


@frappe.whitelist()
def get_payments():
    payments = frappe.db.sql(
        """ Select pe.name, pe.posting_date, pe.paid_amount, pe.party, pe.party_name, ba.iban,
            pe.paid_from, pe.paid_to_account_currency, per.reference_doctype, per.reference_name
            From `tabPayment Entry` as pe
            Left Join `tabPayment Entry Reference` as per ON per.parent = pe.name
            left join `tabBank Account` as ba ON ba.party_type = pe.party_type and ba.party = pe.party
            Where pe.docstatus = 0 and pe.payment_type = "Pay" and pe.party_type = "Supplier" and pe.xml_file_generated = 0 and ba.iban is not null
            order by posting_date
        """,
        as_dict=1,
    )

    payments_ = []

    def key_func(k):
        return k["name"]

    INFO = sorted(payments, key=key_func)

    for key, value in groupby(INFO, key_func):
        ref_name_list = []
        for d in list(value):
            ref_name_list.append(d.get("reference_name"))
        d.update({"reference_name": ref_name_list})
        payments_.append(d)

    return {"payments": payments_}


# adds Windows-compatible line endings (to make the xml look nice)
def make_line(line):
    return line + "\r\n"


@frappe.whitelist()
def genrate_file_for_sepa(payments, posting_date):
    payments = eval(payments)
    payments = list(filter(None, payments))

    message_root = get_message_root()

    group_header = get_group_header_content(payments, message_root)

    payment_information_element = get_payment_info(payments, group_header, posting_date)

    return payment_information_element


def get_message_root():
    # create xml header
    content = make_line('<?xml version="1.0" encoding="UTF-8"?>')
    # define xml template reference
    content += make_line(
        '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03 pain.001.001.03.xsd">'
    )
    # transaction holder
    content += make_line("<CstmrCdtTrfInitn>")
    return content


def get_group_header_content(payments, message_root):
    content = "\r\n" + message_root
    content += make_line("      <GrpHdr>")
    content += make_line(
        "          <MsgId>{0}</MsgId>".format(time.strftime("%Y%m%d%H%M%S"))
    )
    content += make_line(
        "          <CreDtTm>{0}</CreDtTm>".format(time.strftime("%Y-%m-%dT%H:%M:%S"))
    )
    transaction_count = 0
    transaction_count_identifier = "<!-- $COUNT -->"
    content += make_line(
        "          <NbOfTxs>{0}</NbOfTxs>".format(transaction_count_identifier)
    )
    control_sum = 0.0
    control_sum_identifier = "<!-- $CONTROL_SUM -->"
    content += make_line(
        "          <CtrlSum>{0}</CtrlSum>".format(control_sum_identifier)
    )
    content += make_line("          <InitgPty>")
    content += make_line(
        "              <Nm>{0}</Nm>".format(get_company_name(payments[0]))
    )
    content += make_line("              <Id>")
    content += make_line("                  <OrgId>")
    content += make_line("                      <Othr>")
    content += make_line("                          <Id>556036867100</Id>")
    content += make_line("                          <SchmeNm>")
    content += make_line("                              <Cd>BANK</Cd>")
    content += make_line("                          </SchmeNm>")
    content += make_line("                      </Othr>")
    content += make_line("                  </OrgId>")
    content += make_line("              </Id>")
    content += make_line("          </InitgPty>")
    content += make_line("      </GrpHdr>")

    return content


def get_payment_info(payments, group_header, posting_date):
    content = "\r\n" + group_header
    content += make_line("      <PmtInf>")
    content += make_line("          <PmtInfId>{0}</PmtInfId>".format(payments[0]))
    content += make_line("          <PmtMtd>TRF</PmtMtd>")
    content += make_line("          <BtchBookg>false</BtchBookg>")
    transaction_count = 0
    transaction_count_identifier = "<!-- $COUNT -->"
    content += make_line(
        "          <NbOfTxs>{0}</NbOfTxs>".format(transaction_count_identifier)
    )
    control_sum = 0.0
    control_sum_identifier = "<!-- $CONTROL_SUM -->"
    content += make_line(
        "          <CtrlSum>{0}</CtrlSum>".format(control_sum_identifier)
    )

    content += make_line("          <PmtTpInf>")
    content += make_line("              <SvcLvl>")
    content += make_line("                  <Cd>SEPA</Cd>")
    content += make_line("              </SvcLvl>")
    content += make_line("          </PmtTpInf>")

    required_execution_date = posting_date
    content += make_line(
        "          <ReqdExctnDt>{0}</ReqdExctnDt>".format(required_execution_date)
    )

    content += make_line("          <Dbtr>")
    company_name = get_company_name(payments[0])
    content += make_line("              <Nm>{0}</Nm>".format(company_name))
    content += make_line("              <Id>")
    content += make_line("                  <OrgId>")
    content += make_line("                      <Othr>")
    content += make_line("                          <Id>55667755110004</Id>")
    content += make_line("                          <SchmeNm>")
    content += make_line("                              <Cd>BANK</Cd>")
    content += make_line("                          </SchmeNm>")
    content += make_line("                      </Othr>")
    content += make_line("                  </OrgId>")
    content += make_line("              </Id>")
    content += make_line("              <CtryOfRes>SE</CtryOfRes>")
    content += make_line("          </Dbtr>")

    content += make_line("          <DbtrAcct>")
    content += make_line("              <Id>")
    iban = get_company_iban(company_name)
    content += make_line("                  <IBAN>{0}</IBAN>".format(iban))
    content += make_line("              </Id>")
    content += make_line("              <Ccy>EUR</Ccy>")
    content += make_line("          </DbtrAcct>")

    content += make_line("          <DbtrAgt>")
    content += make_line(
        "          <!-- Note: For IBAN only on Debtor side use Othr/Id: NOTPROVIDED - see below -->"
    )
    content += make_line("              <FinInstnId>")
    content += make_line("                  <Othr>")
    content += make_line("                      <Id>NOTPROVIDED</Id>")
    content += make_line("                  </Othr>")
    content += make_line("              </FinInstnId>")
    content += make_line("          </DbtrAgt>")

    content += make_line("          <ChrgBr>SLEV</ChrgBr>")
    for payment in payments:
        frappe.db.set_value("Payment Entry", payment, "xml_file_generated", 1)
        payment_record = frappe.get_doc("Payment Entry", payment)

        content += make_line("          <CdtTrfTxInf>")
        content += make_line("              <PmtId>")
        content += make_line("                  <InstrId>{}</InstrId>".format(payment))
        content += make_line(
            "                  <EndToEndId>{}</EndToEndId>".format(
                payment.replace("-", "")
            )
        )
        content += make_line("              </PmtId>")
        content += make_line("              <Amt>")
        content += make_line(
            '                  <InstdAmt Ccy="{0}">{1:.2f}</InstdAmt>'.format(
                payment_record.paid_from_account_currency, payment_record.paid_amount
            )
        )
        content += make_line("              </Amt>")
        content += make_line(
            "              <!-- Note: Creditor Agent should not be used at all for IBAN only on Creditor side -->"
        )
        content += make_line("              <Cdtr>")
        # if payment_record.party_type == "Employee":
        #     name = frappe.get_value("Employee", payment_record.party, "employee_name")
        # if payment_record.party_type == "Supplier":
        name = frappe.db.get_value("Supplier", payment_record.party, "supplier_name")
        if "&" in name:
            new_name = name.replace("& ", "")
            if new_name == name:
                new_name = name.replace("&", " ")
            name = new_name
        content += make_line("                  <Nm>{0}</Nm>".format(name))
        content += make_line("              </Cdtr>")
        content += make_line("              <CdtrAcct>")
        content += make_line("                  <Id>")
        iban_code = get_supplier_iban_no(payment_record.party)
        content += make_line(
            "                      <IBAN>{0}</IBAN>".format(iban_code.strip() or "")
        )
        content += make_line("                  </Id>")
        content += make_line("              </CdtrAcct>")
        content += make_line("              <RmtInf>")
        sup_invoice_no = ""
        if payment_record.references[0].reference_doctype == "Purchase Invoice":
            sup_invoice_no = frappe.db.get_value(
                "Purchase Invoice",
                payment_record.references[0].reference_name,
                "bill_no",
            )
        content += make_line(
            "                  <Ustrd>{0}</Ustrd>".format(
                sup_invoice_no if sup_invoice_no else ""
            )
        )
        content += make_line("              </RmtInf>")
        content += make_line("          </CdtTrfTxInf>")
        transaction_count += 1
        control_sum += payment_record.paid_amount
    content += make_line("      </PmtInf>")
    content += make_line("  </CstmrCdtTrfInitn>")
    content += make_line("</Document>")
    content = content.replace(
        transaction_count_identifier, "{0}".format(transaction_count)
    )
    content = content.replace(control_sum_identifier, "{:.2f}".format(control_sum))

    return content


def get_supplier_iban_no(party):
    iban = frappe.db.sql(
        f"""
        Select iban From `tabBank Account` where party_type = 'Supplier' and party = '{party}' and iban is not null
    """,
        as_dict=1,
    )
    if iban:
        return iban[0].iban
    return ""


def get_company_name(payment_entry):
    return frappe.get_value("Payment Entry", payment_entry, "company")


def get_company_iban(company_name):
    iban = frappe.db.sql(
        f"""
        Select iban From `tabBank Account` where is_company_account = 1 and company = '{company_name}'
     """,
        as_dict=1,
    )
