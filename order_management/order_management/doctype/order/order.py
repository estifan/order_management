# Copyright (c) 2025, Tilet Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Order(Document):
    def validate(self):
        self.calculate_totals()
        self.set_recieved_by()
        
    def calculate_totals(self):
        full_payment = 0

        for item in self.get('services'):
            full_payment += item.total_price

        self.full_payment= full_payment
    def set_recieved_by(self):
        self.recieved_by = frappe.session.user

        
