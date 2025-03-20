# Copyright (c) 2025, Tilet Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

def jump_workflow(docname, action):
    doc = frappe.get_doc("Single Orders", docname)
    apply_workflow(doc, action)
    print(f"Applied workflow action: {action}")
def allow_all(*args, **kwargs):
    return True

class SingleOrders(Document):
	def validate(self):
		self.handle_workflow_jump()
		self.handle_status_change()
	def after_save(self):
		print('after save')

	def handle_workflow_jump(self):
		if self.workflow_state == "Workshop Pending":
			print('if self.workflow_state == "Workshop Pending":')
			if not self.workshoped:
				print('if self.workflow_state == "Workshop Pending": 1')
				if self.designed:
					print('if self.workflow_state == "Workshop Pending": 2')
					self.workflow_state = "Completed"
					self.status = "Completed"

	def handle_status_change(self):
		# Get the meta object for the Order doctype
		meta = frappe.get_meta("Order")
		# Store the original has_permission method
		original_has_permission = meta.has_permission
		
		# Override the has_permission method to always return True
		meta.has_permission = allow_all
		try:
			doc = frappe.get_doc("Order", self.order_number)
			status_changed = False  # Flag to track changes

			for child in doc.get("services"):
				if child.name == self.source_docname and child.status != self.status:
					child.status = self.status
					status_changed = True  # Track that a change happened

			# Determine new status based on child services
			service_statuses = [child.status for child in doc.get("services")]

			if any(status != "Pending" for status in service_statuses):
				if doc.status != "In progress":
					doc.status = "In progress"
					doc.workflow_state = "In progress"
					status_changed = True

			if all(status == "Completed" for status in service_statuses):
				if doc.status != "Completed":
					doc.status = "Completed"
					doc.workflow_state = "Completed"
					status_changed = True

			# Save only if there's a change
			if status_changed:
				doc.save(ignore_permissions=True)
				frappe.db.commit()
				frappe.logger().info(f"Order {self.order_number} and service status updated successfully.")
		finally:
			# Restore the original permission check
			meta.has_permission = original_has_permission


		
