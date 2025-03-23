import frappe

@frappe.whitelist()
def get_users_by_role(doctype, txt, searchfield, start, page_len, filters):
    """Return a list of users with the specified role."""
    role = filters.get("role")  # Get the role from the filters

    # Query users with the specified role
    users = frappe.db.sql("""
        SELECT DISTINCT parent
        FROM `tabHas Role`
        WHERE role = %s AND parenttype = 'User'
    """, (role), as_dict=False)  # Use as_dict=False to return a list of lists

    # Format the results for search_link
    results = [[user[0]] for user in users]  # Wrap each user in a list
    return results