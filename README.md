## SEPA Payment XML FILE Generation Feature

This app will help you to execute bulk payments with XML file

Welcome to our SEPA payments generation feature! With this tool, you can easily generate SEPA payment instructions to facilitate euro-denominated transactions within the SEPA zone.

With This version of the app, you can generate XML file for creditors.
### Pre Setup
  1. Create EUR Bank Account (Chart of Accounts)
  2. Company EUR Bank Account (Bank Account)
  3. Company Address
  4. Initiating Party Org Id (This id is assigned by Bank)
  5. Debtor Org Id (Tax number - VAT number or Corporate Id)

![Capture](https://github.com/viralkansodiya/SEPA-PAYMENT/assets/141210323/0acf2afd-4a42-45c8-bd81-70b46f215669)

### Supplier Details
  1. Create a supplier bank account in EUR currency (Iban Code, Branch Code or Swift Code)
  2. Address

# Process to generate XML file
  1. Create a `Purchase Invoice` in EUR currency.
  2. Create a `Payment Entry` against the purchase invoice and keep the payment entry in `Draft`.
  3. Go to the payment export page
  4. Select a payment Entry
  5. Click on Create Button
