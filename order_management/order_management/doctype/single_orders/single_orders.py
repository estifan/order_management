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
		self.handle_status_change()
	def after_save(self):
		print('after save')
	def on_update(self):
		self.handle_workflow_jump()
		

	def handle_workflow_jump(self):
		if self.workflow_state == "Workshop Pending":
			print('if self.workflow_state == "Workshop Pending":')
			if not self.workshoped:
				print('if self.workflow_state == "Workshop Pending": 1')
				if self.designed:
					print('if self.workflow_state == "Workshop Pending": 2')
					frappe.db.set_value("Single Orders", self.name, "workflow_state", "Completed")
					frappe.db.set_value("Single Orders", self.name, "status", "Completed")
					try:
						services = frappe.get_all(
							"Service Item",
							fields=["status","name"],
							filters={
							"parent": self.order_number
							},
						)
						
						doc = frappe.db.get_value("Order", self.order_number,
							["workflow_state", "status","name"],as_dict=True)
						status_changed = False  # Flag to track changes
						print("services: ",services)
						for child in services:
							print("child: ",child)
							if child.name == self.source_docname and child.status != self.status:
								print("child.status: ",child.status)
								# child.status = self.status
								frappe.db.set_value("Service Item", child.name, "status", "Completed")
								status_changed = True  # Track that a change happened
						services = frappe.get_all(
							"Service Item",
							fields=["status","name"],
							filters={
							"parent": self.order_number
							},
						)

						# Determine new status based on child services
						service_statuses = [child.status for child in services]
						print("service_statuses: ",service_statuses)

						if all(status == "Completed" for status in service_statuses):
							if doc.status != "Completed":
								print("set Completed")
								frappe.db.set_value("Order", self.order_number, "workflow_state", "Completed")
								frappe.db.set_value("Order", self.order_number, "status", "Completed",)
								# doc.status = "Completed"
								# doc.workflow_state = "Completed"
								status_changed = True

						# Save only if there's a change
						if status_changed:
							# doc.save(ignore_permissions=True)
							# frappe.db.commit()
							frappe.logger().info(f"Order {self.order_number} and service status updated successfully.")
					finally:
						# Restore the original permission check
						pass

	def handle_status_change(self):
	
		try:
			services = frappe.get_all(
				"Service Item",
				fields=["status","name"],
				filters={
    			"parent": self.order_number
  				},
			)
			
			doc = frappe.db.get_value("Order", self.order_number,
                ["workflow_state", "status","name"],as_dict=True)
			status_changed = False  # Flag to track changes
			print("services: ",services)
			for child in services:
				print("child: ",child)
				if child.name == self.source_docname and child.status != self.status:
					print("child.status: ",child.status)
					# child.status = self.status
					frappe.db.set_value("Service Item", child.name, "status", self.status)
					status_changed = True  # Track that a change happened
			services = frappe.get_all(
				"Service Item",
				fields=["status","name"],
				filters={
    			"parent": self.order_number
  				},
			)

			# Determine new status based on child services
			service_statuses = [child.status for child in services]
			print("service_statuses: ",service_statuses)

			if any(status != "Pending" for status in service_statuses):
				if doc.status != "In progress":
					print("set In progress")
					frappe.db.set_value("Order", self.order_number, "workflow_state", "In progress")
					frappe.db.set_value("Order", self.order_number, "status", "In progress",)
					status_changed = True

			if all(status == "Completed" for status in service_statuses):
				if doc.status != "Completed":
					print("set Completed")
					frappe.db.set_value("Order", self.order_number, "workflow_state", "Completed")
					frappe.db.set_value("Order", self.order_number, "status", "Completed",)
					# doc.status = "Completed"
					# doc.workflow_state = "Completed"
					status_changed = True

			# Save only if there's a change
			if status_changed:
				# doc.save(ignore_permissions=True)
				# frappe.db.commit()
				frappe.logger().info(f"Order {self.order_number} and service status updated successfully.")
		finally:
			# Restore the original permission check
			pass


		
