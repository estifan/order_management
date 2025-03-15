# Copyright (c) 2025, Tilet Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

def jump_workflow(docname, action):
    doc = frappe.get_doc("Single Orders", docname)
    apply_workflow(doc, action)
    print(f"Applied workflow action: {action}")

class SingleOrders(Document):
	def validate(self):
		# self.handle_workflow_jump()
		self.handle_status_change()

	# def after_save(self):
	# 	doc = frappe.get_doc("Single Orders", self.name)
	# 	status_changed = False
	# 	if doc.status == "Workshop Pending":
	# 		if not doc.workshoped:
	# 			if doc.designed:
	# 				print("Designing only")
	# 				# jump_workflow(self.name, "Completed")
	# 				doc.workflow_state = "Completed"
	# 				doc.status = "Completed"
	# 				status_changed = True
	# 	elif doc.status == "Pending":
	# 		if not doc.designed:
	# 			if doc.workshoped:
	# 				print("Workshop only")
	# 				# jump_workflow(self.name, "Workshop Pending")
	# 				doc.workflow_state = "Workshop Pending"
	# 				doc.status = "Workshop Pending"
	# 				status_changed = True
	# 	if status_changed:
	# 		doc.save()
	# 		frappe.db.commit()
	# 		print("Order and service status updated successfully.")

	def handle_status_change(self):
		doc = frappe.get_doc("Order", self.order_number)
		doc.flags.ignore_permissions = True

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



		
