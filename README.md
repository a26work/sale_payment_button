# Sale Order Payment Button

## Overview
This module enhances Odoo 16 by adding payment smart buttons to both sales orders and invoices, similar to the functionality available in Odoo 18. The module allows users to easily track and access payments directly from sales orders and invoices without navigating to separate menus.

## Features
- **Sales Order Payment Button**: Adds a payment smart button on sales order forms showing the count of related payments
- **Invoice Payment Button**: Adds a payment smart button on invoice forms showing the count of related payments
- **Quick Access**: Clicking the button opens a list view of all payments related to the document
- **Integration**: Seamlessly integrates with Odoo's existing sales and accounting workflows

## Installation
1. Download the module folder (`sale_payment_button`) to your Odoo 16 addons directory
2. Update the apps list in Odoo (Settings > Apps > Update Apps List)
3. Install the "Sale Order Payment Button" module from the apps list


## Technical Information
This module extends the following models:
- `sale.order`: Adds payment count computation and action to view payments
- `account.move`: Adds payment count computation and action to view payments

- You most add the user to (Show Accounting Features - Readonly) Group

## Requirements
- Odoo 16.0
- `sale_management` module
- `account` module

