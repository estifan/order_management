import frappe
from frappe.model.document import Document

class Order(Document):
    def validate(self):
        self.calculate_totals()
        self.set_recieved_by()
        self.validate_services_table()

    def validate_services_table(self):
        if self.services and isinstance(self.services, list):
            for item in self.services:
                if not item.designed and not item.workshoped:
                    frappe.throw(
                        f"Row {item.idx}: At least either 'Designed' or 'Workshopped' must be filled in the Services table."
                    )

    def calculate_totals(self):
        full_payment = 0
        for item in self.get('services'):
            full_payment += item.total_price
        self.full_payment = full_payment

    def set_recieved_by(self):
        self.recieved_by = frappe.session.user

    def on_update(self):
        self.create_or_update_single_orders()

    def create_or_update_single_orders(self):
        assigned_users = []

        if self.services and isinstance(self.services, list):
            for item in self.services:
                if item.designed or item.workshoped:
                    assigned_users.append({
                        "designed": item.designed,
                        "workshoped": item.workshoped,
                        "service": item.service,
                        "qty": item.quantity,
                        "name": item.name,
                    })

            for user in assigned_users:
                filters = {
                    "source_docname": user["name"]
                }

                existing_orders = frappe.get_list("Single Orders", filters=filters, fields=["name"])
                print("user: ",user)
                print("existing_orders: ",existing_orders)
                if existing_orders:
                    for existing in existing_orders:
                        order_doc = frappe.get_doc("Single Orders", existing["name"])

                        previous_designed = order_doc.designed
                        previous_workshoped = order_doc.workshoped

                        if previous_designed:
                            frappe.share.remove("Single Orders", order_doc.name, previous_designed)
                        if previous_workshoped:
                            frappe.share.remove("Single Orders", order_doc.name, previous_workshoped)

                        updated_fields = []
                        if order_doc.qty != user["qty"]:
                            order_doc.qty = user["qty"]
                            updated_fields.append("qty")

                        if order_doc.designed != user["designed"]:
                            order_doc.designed = user["designed"]
                            updated_fields.append("designed")

                        if order_doc.workshoped != user["workshoped"]:
                            order_doc.workshoped = user["workshoped"]
                            updated_fields.append("workshoped")

                        if updated_fields:
                            order_doc.save(ignore_permissions=True)
                            frappe.msgprint(f"Updated Single Order {existing['name']} with fields: {', '.join(updated_fields)}", alert=True, indicator="blue")

                            for assigned_user in [user["designed"], user["workshoped"]]:
                                if assigned_user:
                                    frappe.share.add(
                                        doctype="Single Orders",
                                        name=order_doc.name,
                                        user=assigned_user,
                                        read=1,
                                        write=1,
                                        share=0,
                                        everyone=0,
                                        notify=1
                                    )
                                    frappe.logger().info(f"Updated and shared Single Orders with user: {assigned_user}")

                else:
                    status = "Pending"
                    workflow_state = "Pending"

                    # Create the new order with initial state
                    new_order = frappe.get_doc({
                        "doctype": "Single Orders",
                        "service": user["service"],
                        "customer_name": self.customer_name,
                        "recieved_by": self.recieved_by,
                        "contact_person": self.contact_person,
                        "qty": user["qty"],
                        "designed": user["designed"],
                        "workshoped": user["workshoped"],
                        "status": status,
                        "workflow_state": workflow_state,
                        "source_docname": user["name"],
                        "order_number": self.name,
                    })
                    new_order.insert(ignore_permissions=True)

                    # If only workshop is assigned, transition the workflow state properly
                    if user["workshoped"] and not user["designed"]:
                        # Get the workflow document
                        workflow = frappe.get_doc("Workflow", {"document_type": "Single Orders"})
                        # Find the transition from Pending to Workshop Pending
                        for transition in workflow.transitions:
                            if (transition.state == "Pending" and 
                                transition.next_state == "Workshop Pending" and 
                                transition.allowed == "Administrator"):
                                # Apply the transition
                                new_order.workflow_state = "Workshop Pending"
                                new_order.status = "Workshop Pending"
                                new_order.save(ignore_permissions=True)
                                break

                    frappe.msgprint(f"Single Order created for {user['service']} with quantity {user['qty']}", alert=True, indicator="green")

                    for assigned_user in [user["designed"], user["workshoped"]]:
                        if assigned_user:
                            frappe.share.add(
                                doctype="Single Orders",
                                name=new_order.name,
                                user=assigned_user,
                                read=1,
                                write=1,
                                share=0,
                                everyone=0,
                                notify=1
                            )
                            frappe.logger().info(f"Shared Single Orders with user: {assigned_user}")